import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import FoodItem
from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.logging import init_logger
from api.libs.utils import convert_to_bool

AUTH = HTTPBasicAuth()
TABLE = 'food_items'

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('food.py logging level %s', LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    if password.strip() == api_pwd:
        verified = True
    else:
        LOG.info('Access Denied - %s', username)
        verified = False
    return verified


def check_category_exists(category):
    category = get_item_from_db('categories', category)
    if category:
        return True


def check_category_status(category):
    LOG.debug('%s', category)
    category = get_item_from_db('categories', category)
    if category:
        return category.is_active


def food_item_to_dict(food_item):
    food_item_dict = {
        'name': food_item.name,
        'sku': food_item.id,
        'category': food_item.category.name,
        'description': food_item.description,
        'price': food_item.price,
        'slug': food_item.slug,
        'is_active': food_item.is_active
    }
    return food_item_dict


def get_food_item_by_slug(slug):
    LOG.debug('%s', slug)
    food_item = FoodItem.query.filter_by(slug=slug).first()
    if food_item:
        return food_item


def get_items_by_category(category, location, active_only=True, inactive_only=False):
    LOG.debug('%s | Location: %s | Active: %s | Inactive: %s', category, location, active_only, inactive_only)
    food_item_list = []
    active_item_list = []
    inactive_item_list = []
    if check_category_status(category):
        LOG.debug('%s FOUND', category)
        food_items = FoodItem.query.filter(FoodItem.category.has(name=category, location=location)).all()
        for food_item in food_items:
            if food_item.is_active:
                active_item_list.append(food_item_to_dict(food_item))
            else:
                inactive_item_list.append(food_item_to_dict(food_item))
            food_item_list.append(food_item_to_dict(food_item))
        if active_only:
            food_item_list = active_item_list
        elif inactive_only:
            food_item_list = inactive_item_list
    LOG.debug('Items collected: %s', len(food_item_list))
    return food_item_list


def get_category_status(category_name):
    category = get_item_from_db('categories', category_name)
    response = {}
    if not category:
        response = {
            "status": 400,
            "response": "Bad Request: Category not found"
        }
        LOG.info('FoodAPI | 400 | %s does not exist', category_name)
    return category, response

class FoodAPI(Resource):
    @AUTH.login_required
    def post(self, name):
        body = request.json
        body['slug'] = body['name'].lower().replace(' ', '-').strip('*')
        LOG.debug("FoodAPI | PATH %s | Name: %s | Location: %s", request.path, body['name'], body['location'])
        category, response = get_category_status(body["category_id"])
        if not category:
            resp = response
        else:
            self.create_item(body, category)
            resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def get(self, name):
        LOG.debug("FoodAPI | PATH: %s | Name: %s | ARGS: %s", request.path, name, dict(request.args))
        food_item = get_food_item_by_slug(name)
        if not food_item:
            LOG.info('FoodAPI | 404 | %s not found', name)
            return Response(status=404)
        food_item = json.dumps(food_item_to_dict(food_item))
        return Response(food_item, mimetype='application/json', status=200)

    @AUTH.login_required
    def delete(self, name):
        LOG.debug("FoodAPI | PATH: %s | Name: %s", request.path, name)
        food_item = get_food_item_by_slug(name)
        if not food_item:
            LOG.info('404 DELETE Item %s not found', name)
            return Response(status=404)
        run_db_action(action='delete', item=food_item)
        return Response(status=204)

    @AUTH.login_required
    def put(self, name):
        LOG.debug("FoodAPI | PATH: %s | Name: %s", request.path, name)
        body = request.json
        food_item = get_food_item_by_slug(name)
        if not food_item:
            LOG.info('404 %s not found', name)
            return Response(status=404)
        run_db_action(action='update', item=food_item, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    def create_item(self, body, category):
        LOG.debug('FoodAPI | Adding %s to DB', body['name'])
        run_db_action(action='create', item=category, body=body, table=TABLE)

    def options(self, location):
        LOG.info('- FoodAPI | OPTIONS | %s', location)
        return '', 200


class FoodItemsAPI(Resource):
    @AUTH.login_required
    def get(self, category):
        LOG.debug("FoodItemsAPI | PATH: %s | Category: %s", request.path, category)
        food_items = get_items_by_category(category)
        if food_items:
            food_items = json.dumps(food_items)
            return Response(food_items, mimetype='application/json', status=200)
        else:
            LOG.info('FoodItemsAPI | 404 %s not found', category)
            return Response(status=404)


class ItemsByCategoryAPI(Resource):
    @AUTH.login_required
    def get(self, category=None, status=None):
        LOG.debug("ItemsByCategoryAPI | PATH: %s | Category: %s | Status: %s", request.path, category, status)
        if not category:
            category = request.args.get('category')
        if not status:
            status = request.args.get('is_active')
            status = convert_to_bool(status) if status else status
        location = request.args.get('location')
        LOG.debug('LOCATION: %s', location)
        if not check_category_exists(category):
            LOG.debug('ItemsByCategoryAPI | 404 | Category %s not found', category)
            return Response(status=404)
        if status:
            food_items = get_items_by_category(category, location, active_only=True, inactive_only=False)
        elif status == False:
            food_items = get_items_by_category(category, location, active_only=False, inactive_only=True)
        else:
            food_items = get_items_by_category(category, location, active_only=False, inactive_only=False)
        food_items = json.dumps(food_items)
        return Response(food_items, mimetype='application/json', status=200)

    def options(self, location):
        LOG.info('- MenuAPI | OPTIONS | %s', location)
        return '', 200


class AllItemsByCategoryAPI(Resource):
    @AUTH.login_required
    def get(self, category):
        LOG.debug("PATH: %s | %s | %s", request.path, category)
        if not check_category_exists(category):
            LOG.debug('FoodItemsByCategoyryAPI - GET - 404 - Category %s not found', category)
            return Response(status=404)
        food_items = get_items_by_category(category)
        food_items = json.dumps(food_items)
        return Response(food_items, mimetype='application/json', status=200)
