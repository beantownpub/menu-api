import json
import os

import sqlalchemy

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Category
from api.libs.db_utils import run_db_action, get_item_from_db, get_item_by_slug
from api.libs.logging import init_logger
from api.resources.food import get_all_food_items_by_category

AUTH = HTTPBasicAuth()
TABLE = 'category'


LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('categories.py logging level %s', LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_password = os.environ.get("API_PASSWORD")
    LOG.debug("CategoryAPI Verifying %s", username)
    if password.strip() == api_password:
        verified = True
    else:
        LOG.info('Access denied for user %s', username)
        verified = False
    return verified


def category_to_dict(category, items=None):
    category_dict = {
        'name': category.name,
        'sku': category.id,
        'is_active': category.is_active,
        'slug': category.slug
    }
    if items:
        category_dict['items'] = items
    return category_dict



def get_all_categories() -> list:
    LOG.info('Getting all categories')
    category_list = []
    try:
        categories = Category.query.filter_by().all()
    except sqlalchemy.exc.OperationalError:
        LOG.error('DB GET ERROR')
        try:
            categories = Category.query.filter_by().all()
        except sqlalchemy.exc.OperationalError:
            raise
    if categories:
        for category in categories:
            category = get_item_from_db(TABLE, category.name)
            if category:
                items = get_all_food_items_by_category(category.name)
                category_list.append(category_to_dict(category, items=items))
        return [x for x in category_list if x]


class CategoriesAPI(Resource):
    @AUTH.login_required
    def post(self):
        body = request.get_json()
        LOG.debug('CategoriesAPI Creating category %s', body['name'])
        if not body.get('slug'):
            body['slug'] = body['name'].lower().replace(' ', '-')
        run_db_action(action='create', body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def get(self):
        categories = get_all_categories()
        if categories:
            categories = json.dumps(categories)
            return Response(categories, mimetype='application/json', status=200)
        else:
            return Response(status=404)


class CategoryAPI(Resource):
    @AUTH.login_required
    def post(self, name):
        LOG.debug('Creating category %s', name)
        body = request.get_json()
        if not body.get('slug'):
            body['slug'] = body['name'].lower().replace(' ', '-')
        run_db_action(action='create', body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def delete(self, name):
        LOG.debug('Deleting category %s', name)
        category = get_item_by_slug(TABLE, name)
        if not category:
            return Response(status=404)
        food_items = get_all_food_items_by_category(category.name)
        if food_items:
            LOG.debug('Deleting all items in %s', category.name)
            for item in food_items:
                item = get_item_by_slug('food_item', item['slug'])
                run_db_action(action='delete', item=item)
                LOG.debug('Deleted item %s', item.name)
        run_db_action(action='delete', item=category)
        return Response(status=204)

    @AUTH.login_required
    def get(self, name):
        LOG.info("GET Category: %s", name)
        category = get_item_from_db(TABLE, name)
        if not category:
            return Response(status=404)
        category = json.dumps(category_to_dict(category))
        return Response(category, mimetype='application/json', status=200)

    @AUTH.login_required
    def put(self, name):
        body = request.json
        LOG.debug("Updating category %s", name)
        categpry = get_item_by_slug(TABLE, name)
        if not categpry:
            return Response(status=404)
        run_db_action(action='update', item=categpry, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    def options(self, location):
        LOG.info('- CategoryAPI | OPTIONS | %s', location)
        return '', 200
