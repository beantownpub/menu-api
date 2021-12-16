import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import FoodItem
from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.logging import init_logger

AUTH = HTTPBasicAuth()
TABLE = 'food_item'

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('food.py logging level %s', LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    LOG.debug("Verifying %s", username)
    if password.strip() == api_pwd:
        verified = True
    else:
        LOG.info('Access Denied')
        verified = False
    return verified


def check_category_status(category):
    category = get_item_from_db('category', category)
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
    LOG.debug('Getting item %s ', slug)
    food_item = FoodItem.query.filter_by(slug=slug).first()
    if food_item:
        return food_item


def get_active_food_items_by_category(category):
    LOG.debug('Getting active %s items', category)
    food_item_list = []
    if check_category_status(category):
        food_items = FoodItem.query.filter(FoodItem.category.has(name=category)).all()
        for food_item in food_items:
            if food_item.is_active:
                food_item_list.append(food_item_to_dict(food_item))
    return food_item_list


def get_all_food_items_by_category(category):
    LOG.debug('Getting all %s items', category)
    food_item_list = []
    if check_category_status(category):
        food_items = FoodItem.query.filter(FoodItem.category.has(name=category)).all()
        for food_item in food_items:
            food_item_list.append(food_item_to_dict(food_item))
    return food_item_list


class FoodAPI(Resource):
    @AUTH.login_required
    def post(self, name):
        body = request.json
        LOG.debug("POST Item path /%s | %s", name, body)
        category = get_item_from_db('category', body["category_id"])
        if not body.get('slug'):
            body['slug'] = body['name'].lower().replace(' ', '-')
        if not category:
            resp = {
                "status": 400,
                "response": "Bad Request: Category not found"
            }
            LOG.info('404 POST Item %s not found', name)
            return resp
        run_db_action(action='create', item=category, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def get(self, name):
        food_item = get_food_item_by_slug(name)
        if not food_item:
            LOG.info('404 GET Item %s not found', name)
            return Response(status=404)
        food_item = json.dumps(food_item_to_dict(food_item))
        return Response(food_item, mimetype='application/json', status=200)

    @AUTH.login_required
    def delete(self, name):
        LOG.debug('Deleting food item %s', name)
        food_item = get_food_item_by_slug(name)
        if not food_item:
            LOG.info('404 DELETE Item %s not found', name)
            return Response(status=404)
        run_db_action(action='delete', item=food_item)
        return Response(status=204)

    @AUTH.login_required
    def put(self, name):
        body = request.json
        LOG.debug("Updating food item %s", name)
        food_item = get_food_item_by_slug(name)
        if not food_item:
            LOG.info('404 PUT Item %s not found', name)
            return Response(status=404)
        run_db_action(action='update', item=food_item, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    def options(self, location):
        LOG.info('- FoodAPI | OPTIONS | %s', location)
        return '', 200


class FoodItemsAPI(Resource):
    @AUTH.login_required
    def get(self, category):
        food_items = get_active_food_items_by_category(category)
        if food_items:
            food_items = json.dumps(food_items)
            return Response(food_items, mimetype='application/json', status=200)
        else:
            LOG.info('404 Category %s not found', category)
            return Response(status=404)


class FoodItemsByCategoyryAPI(Resource):
    @AUTH.login_required
    def get(self, category):
        food_items = get_active_food_items_by_category(category)
        if food_items:
            food_items = json.dumps(food_items)
            return Response(food_items, mimetype='application/json', status=200)
        else:
            LOG.info('404 Category %s food_items not found', category)
            return Response(status=404)

    def options(self, location):
        LOG.info('- MenuAPI | OPTIONS | %s', location)
        return '', 200
