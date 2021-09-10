import json
import os
import logging

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import FoodItem
from api.libs.db_utils import run_db_action, get_item_from_db

AUTH = HTTPBasicAuth()
TABLE = 'food_item'

class MenuDBException(Exception):
    """Base class for menu database exceptions"""


if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    app_log.info("Verifying %s", username)
    if password.strip() == api_pwd:
        verified = True
    else:
        app_log.info('Access Denied')
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
        'price': food_item.price
    }
    return food_item_dict


def get_active_food_items_by_category(category):
    app_log.debug('Getting all %s items', category)
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
        app_log.info("POST Body: %s", body)
        category = get_item_from_db('category', body["category_id"])
        body['slug'] = name.lower().replace(' ', '-')
        if not category:
            resp = {
                "status": 400,
                "response": "Bad Request: Category not found"
            }
            return resp
        run_db_action(action='create', item=category, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def get(self, name):
        food_item = get_item_from_db(TABLE, name)
        if not food_item:
            return Response(status=404)
        food_item = json.dumps(food_item_to_dict(food_item))
        return Response(food_item, mimetype='application/json', status=200)

    @AUTH.login_required
    def delete(self, name):
        app_log.debug('Deleting food item %s', name)
        food_item = get_item_from_db(TABLE, name)
        run_db_action(action='delete', item=food_item)
        return Response(status=204)

    @AUTH.login_required
    def put(self, name):
        body = request.json
        app_log.info("PUT Body: %s", body)
        food_item = get_item_from_db(TABLE, name)
        if not food_item:
            return Response(status=404)
        run_db_action(action='update', item=food_item, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    def options(self, location):
        app_log.info('- FoodAPI | OPTIONS | %s', location)
        return '', 200


class FoodItemsAPI(Resource):
    @AUTH.login_required
    def get(self, category):
        food_items = get_active_food_items_by_category(category)
        if food_items:
            food_items = json.dumps(food_items)
            return Response(food_items, mimetype='application/json', status=200)
        else:
            return Response(status=404)


class FoodItemsByCategoyryAPI(Resource):
    # @AUTH.login_required
    def get(self, category):
        food_items = get_active_food_items_by_category(category)
        if food_items:
            food_items = json.dumps(food_items)
            return Response(food_items, mimetype='application/json', status=200)
        else:
            return Response(status=404)

    def options(self, location):
        app_log.info('- MenuAPI | OPTIONS | %s', location)
        return '', 200
