import json
import os
import uuid

import sqlalchemy

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import FoodItem
from api.database.models import Category
from api.libs.db_utils import run_db_action, get_item_from_db, get_item_by_slug
from api.libs.utils import convert_to_bool
from api.libs.logging import init_logger
from api.resources.food import food_item_to_dict, check_category_exists

AUTH = HTTPBasicAuth()
TABLE = 'categories'


LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('Log Level | %s', LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_password = os.environ.get("API_PASSWORD")
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
        'slug': category.slug,
        'uuid': category.uuid,
        'location': category.location
    }
    if items:
        category_dict['items'] = items
    return category_dict


def get_all_categories(location=None, active_only=False, inactive_only=False) -> list:
    LOG.debug('Location: %s | Active: %s | Inactive: %s', location, active_only, inactive_only)
    category_list, active_items, inactive_items = [],[],[]
    try:
        categories = Category.query.filter_by(location=location).all()
    except sqlalchemy.exc.OperationalError:
        LOG.error('DB GET ERROR')
        try:
            categories = Category.query.filter_by(location=location).all()
        except sqlalchemy.exc.OperationalError:
            LOG.error('ANOTHER DB GET ERROR')
            raise
    if categories:
        for category in categories:
            # category = get_item_from_db(TABLE, category.name)
            if category:
                items = get_all_items_in_category(category.name)
                if category.is_active:
                    active_items.append(category_to_dict(category, items=items))
                else:
                    inactive_items.append(category_to_dict(category, items=items))
                category_list.append(category_to_dict(category, items=items))
        if active_only:
            category_list = active_items
        elif inactive_only:
            category_list = inactive_items
        category_list = [x for x in category_list if x]
        LOG.debug('%s Categories found', len(category_list))
    return category_list


def get_all_items_in_category(category):
    food_item_list = []
    food_items = FoodItem.query.filter(FoodItem.category.has(name=category)).all()
    for food_item in food_items:
        food_item_list.append(food_item_to_dict(food_item))
    LOG.debug('Category %s | %s Items found', category, len(food_item_list))
    return food_item_list


def create_category(body):
    LOG.debug('%s | Location: %s', body['name'], body['location'])
    if not body.get('slug'):
        body['slug'] = body['name'].lower().replace(' ', '-')
    if not check_category_exists(body['name']):
        body['uuid'] = str(uuid.uuid4())
    run_db_action(action='create', body=body, table=TABLE)

class CategoriesAPI(Resource):
    locations = ['beantown', 'thehubpub', 'drdavisicecream']

    @AUTH.login_required
    def post(self):
        LOG.debug('CategoriesAPI | PATH: %s | ARGS: %s', request.path, dict(request.args))
        create_category(request.get_json())
        resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def get(self):
        LOG.debug('CategoriesAPI | PATH: %s | ARGS: %s', request.path, dict(request.args))
        location = request.args.get('location')
        status = request.args.get('is_active')
        status = convert_to_bool(status) if status else status
        categories = []
        if location:
            if location not in self.locations:
                return Response(status=400)
        if status:
            categories = get_all_categories(location, active_only=True, inactive_only=False)
        elif status == False:
            categories = get_all_categories(location, active_only=False, inactive_only=True)
        else:
            categories = get_all_categories(location, active_only=False, inactive_only=False)
        categories = json.dumps(categories)
        return Response(categories, mimetype='application/json', status=200)


class CategoryAPI(Resource):
    @AUTH.login_required
    def post(self, name):
        LOG.debug('CategoryAPI | PATH: %s | ARGS: %s', request.path, request.args)
        body = request.get_json()
        if not body.get('slug'):
            body['slug'] = body['name'].lower().replace(' ', '-')
        run_db_action(action='create', body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def delete(self, name):
        LOG.debug('CategoryAPI | PATH: %s | Name: %s | ARGS: %s', request.path, name, request.args)
        category = get_item_by_slug(TABLE, name)
        if not category:
            return Response(status=404)
        food_items = get_all_items_in_category(category.name)
        if food_items:
            LOG.debug('Deleting all items in %s', category.name)
            for item in food_items:
                LOG.debug('Deleting %s', item)
                item = get_item_by_slug('food_items', item['slug'])
                run_db_action(action='delete', item=item)
                LOG.debug('Deleted item %s', item.name)
        run_db_action(action='delete', item=category)
        return Response(status=204)

    @AUTH.login_required
    def get(self, name):
        LOG.debug('CategoryAPI | PATH: %s | ARGS: %s', request.path, dict(request.args))
        category = get_item_from_db(TABLE, name)
        if not category:
            return Response(status=404)
        category = json.dumps(category_to_dict(category))
        return Response(category, mimetype='application/json', status=200)

    @AUTH.login_required
    def put(self, name):
        body = request.json
        LOG.debug('CategoryAPI | PATH: %s | Name: %s', request.path, name)
        categpry = get_item_by_slug(TABLE, name)
        if not categpry:
            return Response(status=404)
        run_db_action(action='update', item=categpry, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    def options(self, location):
        LOG.info('- CategoryAPI | OPTIONS | %s', location)
        return '', 200


class AllItemsByCategoryAPI(Resource):
    @AUTH.login_required
    def post(self, location, status):
        LOG.debug('CategoriesAPI | Location %s | Status %s', location, status)
        LOG.debug('CategoriesAPI | Location %s | Status %s', location, status)
        body = request.get_json()
        LOG.debug('CategoriesAPI Creating category %s', body['name'])
        if not body.get('slug'):
            body['slug'] = body['name'].lower().replace(' ', '-')
        run_db_action(action='create', body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)
