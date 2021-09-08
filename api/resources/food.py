import json
import os
import logging

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import FoodItem, Category
from api.database.db import db

AUTH = HTTPBasicAuth()

class MenuDBException(Exception):
    """Base class for menu database exceptions"""


if __name__ != '__main__':
    # json_logging.init_non_web(enable_json=True)
    app_log = logging.getLogger()
    # json_logging.config_root_logger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers


@AUTH.verify_password
def verify_password(username, password):
    api_user = os.environ.get("API_USERNAME")
    api_pwd = os.environ.get("API_PASSWORD")
    if username == api_user and password == api_pwd:
        verified = True
    else:
        verified = False
    return verified


def get_food_item(name):
    food_item = FoodItem.query.filter_by(name=name).first()
    if food_item:
        app_log.debug('get_food_item Found %s', name)
        app_log.debug('Food Item: %s', dir(food_item))
        info = {
            'name': food_item.name,
            'sku': food_item.id,
            'category': food_item.category.name,
            'description': food_item.description,
            'price': food_item.price
        }
        app_log.debug(info)
        return info


def check_category_status(category):
    category = get_item_from_db('category', category)
    return category.is_active


def convert_food_item(food_item):
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
            food_item_list.append(convert_food_item(food_item))
    return food_item_list


def get_category(name):
    category = get_item_from_db('category', name)
    category = {
        'id': category.name
    }
    return category


def get_all_categories():
    categories = Category.query.filter_by().all()
    return categories


def get_item_from_db(table_name, item_name):
    if table_name == "food_item":
        item = FoodItem.query.filter_by(name=item_name).first()
    elif table_name == "category":
        item = Category.query.filter_by(name=item_name).first()
    else:
        raise MenuDBException(f"DB Table {table_name} not found")
    assert(item is not None)
    return item


def run_db_action(action, item=None, body=None):
    if not item:
        raise MenuDBException("Cannot run a DB action on empty item")
    if action == "delete":
        db.session.delete(item)
    elif action == "update":
        db.session.add(item)
    elif action == "create":
        slug = body['name'].lower().replace(' ', '-')
        try:
            get_item_from_db('food_item', body['name'])
        except MenuDBException:
            food_item = FoodItem(
                name=body['name'],
                slug=slug,
                is_active=body['is_active'],
                category_id=item.name,
                description=body['description'],
                price=float(body['price'])
            )
            db.session.add(food_item)
        db.session.commit()


class FoodAPI(Resource):
    @AUTH.login_required
    def post(self):
        body = request.json
        app_log.info("WTF: %s", body)
        try:
            category = get_item_from_db('category', body["category"])
        except MenuDBException:
            resp = {
                "status": 400,
                "response": "Bad Request: Category not found"
            }
            return resp
        try:
            run_db_action(category, 'create', body)
        except MenuDBException:
                resp = {"status": 500}
        finally:
            resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def get(self):
        body = request.get_json()
        try:
            get_item_from_db('food_item', body['name'])
        except MenuDBException:
            return Response(status=404)
        return Response(status=200)

    @AUTH.login_required
    def delete(self):
        body = request.get_json()
        app_log.debug('DELETING %s', body['name'])
        food_item = get_item_from_db('food_item', body['name'])
        try:
            run_db_action(food_item, 'delete')
        except MenuDBException:
            return Response(status=500)
        return Response(status=204)

    @AUTH.login_required
    def put(self):
        pass

    def options(self, location):
        app_log.info('- ContactAPI | OPTIONS | %s', location)
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
