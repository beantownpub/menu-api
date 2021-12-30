import os
import sqlalchemy

from api.database.models import Products, Category, Flavors, Sides
from api.database.db import db

from .logging import init_logger
from .utils import make_slug

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('Log Level %s', LOG_LEVEL)

TABLES = {
    "flavors": Flavors,
    "items": Products,
    "products": Products,
    "categories": Category,
    "sides": Sides
}


def get_all_items(table_name, query):
    table = TABLES.get(table_name)
    try:
        items = table.query.filter_by(**query).all()
    except sqlalchemy.exc.OperationalError:
        LOG.error('DB OperationalError')
        raise
    return items


def get_item(table_name, query):
    table = TABLES.get(table_name)
    try:
        items = table.query.filter_by(**query).first()
    except sqlalchemy.exc.OperationalError:
        LOG.error('DB OperationalError')
        raise
    return items


def get_item_by_slug(table_name, slug, location=None):
    LOG.debug('Table: %s | Slug: %s | Location: %s', table_name, slug, location)
    table = TABLES.get(table_name)
    item = table.query.filter_by(slug=slug,location=location).first()
    LOG.debug('ITEM: %s', item)
    return item


def get_item_by_sku(table_name, sku):
    table = TABLES.get(table_name)
    LOG.debug('Table: %s | SKU: %s', table_name, sku)
    item = table.query.filter_by(id=sku).first()
    return item


def get_category_uuid(location, category_name):
    LOG.debug('Location: %s | Category: %s', location, category_name)
    query = {"location": location, "name": category_name}
    category = get_item('categories', query)
    if category:
        return category.uuid

def _db_update(item, table_name, body):
    LOG.debug('DB UPDATE %s | Table: %s | Body: %s', item, table_name, body)
    item.name = body['name']
    item.is_active = body['is_active']
    if table_name == 'categories':
        if body.get('order_number'):
            item.order_number = body['order_number']
        item.description = body['description']
        item.slug = body['slug']
        db.session.add(item)
    elif table_name == 'products':
        item.description = body['description']
        item.price = body['price']
        item.category_id = get_category_uuid(body['location'], body['category_id'])
        item.slug = body['slug']
        db.session.add(item)
    else:
        raise MenuDBException(f"DB Table {table_name} not found")


def _db_write(table_name, body):
    LOG.debug('DB WRITE | Table: %s | Body: %s ', table_name, body)
    if table_name == 'products':
        # slug = make_slug(body['category_id'])
        uuid = get_category_uuid(body['location'], body['category_id'])
        #category = get_item_by_slug('categories', slug, location)
        body['category_id'] = uuid
    table = TABLES.get(table_name)
    item = table(**body)
    LOG.debug('DB WRITE | ITEM %s', item)
    db.session.add(item)


def get_item_from_db(table_name, item_name):
    #LOG.debug('Table: %s | Item: %s', table_name, item_name)
    table = TABLES.get(table_name)
    if not table:
        raise MenuDBException(f"DB Table {table_name} not found")
    item = table.query.filter_by(name=item_name).first()
    return item


def run_db_action(action, item=None, body=None, table=None, location=None):
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
