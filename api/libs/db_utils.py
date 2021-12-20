import os
from api.database.models import FoodItem, Category
from api.database.db import db

from .logging import init_logger

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('Log Level %s', LOG_LEVEL)

TABLES = {
    "food_items": FoodItem,
    "categories": Category
}


def get_item_by_slug(table_name, slug):
    table = TABLES.get(table_name)
    #LOG.debug('%s', slug)
    item = table.query.filter_by(slug=slug).first()
    if item:
        return item


def _db_update(item, table_name, body):
    #LOG.debug('Item: %s | Table: %s | Body: %s', item, table_name, body)
    item.name = body['name']
    item.is_active = body['is_active']
    if table_name == 'categories':
        db.session.add(item)
    elif table_name == 'food_items':
        item.description = body['description']
        item.price = body['price']
        item.category_id = body['category_id']
        item.slug = body['slug']
        db.session.add(item)
    else:
        raise MenuDBException(f"DB Table {table_name} not found")


def _db_write(table_name, body):
    #LOG.debug('Table: %s | Body: %s ', table_name, body)
    table = TABLES.get(table_name)
    if not get_item_from_db(table_name, body['name']):
        item = table(**body)
        db.session.add(item)


def get_item_from_db(table_name, item_name):
    #LOG.debug('Table: %s | Item: %s', table_name, item_name)
    table = TABLES.get(table_name)
    if not table:
        raise MenuDBException(f"DB Table {table_name} not found")
    item = table.query.filter_by(name=item_name).first()
    return item


def run_db_action(action, item=None, body=None, table=None):
    #LOG.debug('%s | Table: %s | Item: %s | Body: %s', action, table, item, body)
    if action == "create":
        _db_write(body=body, table_name=table)
    elif action == "update":
        _db_update(item=item, table_name=table, body=body)
    elif action == "delete":
        db.session.delete(item)
    else:
        raise MenuDBException(f"DB action {action} not found")
    db.session.commit()
