import json
import os
import logging

from flask import Response, request
from flask_restful import Resource

from api.database.models import FoodItem, Category
from api.database.db import db
# from api.utils import verify_password

from flask_httpauth import HTTPBasicAuth

AUTH = HTTPBasicAuth()


if __name__ != '__main__':
    # json_logging.init_non_web(enable_json=True)
    app_log = logging.getLogger()
    # json_logging.config_root_logger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers


def get_food_item(name):
    food_item = FoodItem.query.filter_by(name=name).first()
    if food_item:
        app_log.info('get_food_item Found %s', name)
        app_log.info('Food Item: %s', dir(food_item))
        info = {
            'name': food_item.name,
            'sku': food_item.id,
            'category': food_item.category.name,
            'description': food_item.description,
            'price': food_item.price
        }
        app_log.info(info)
        return info


def check_category_status(category):
    category = Category.query.filter_by(name=category).first()
    if category:
        category = category.is_active
    return category


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
    app_log.info('Getting all %s items', category)
    if check_category_status(category):
        # food_items = FoodItem.query.filter(Category.name == category).all()
        food_item_list = []
        food_items = FoodItem.query.filter(FoodItem.category.has(name=category)).all()
        app_log.info('PRODUCTS: %s', food_items)
        if food_items:
            for food_item in food_items:
                food_item_list.append(convert_food_item(food_item))
        app_log.info(food_items[0].category)
        return food_item_list


def get_category(name):
    category = Category.query.filter_by(name=name).first()
    if category:
        category = {
            'id': category.name
        }
    return category


def get_all_categories():
    categories = Category.query.filter_by().all()
    return categories


def create_food_item(body):
    app_log.debug('BODY - %s', body)
    name = body['name']
    slug = name.lower().replace(' ', '-')
    # sku = body['sku']
    description = body['description']
    # category = body['category']
    is_active = body['is_active']
    price = float(body['price'])
    if not get_food_item(name):
        category = Category.query.filter_by(name=body['category']).first()
        # db.session.commit()
        food_item = FoodItem(
            name=name,
            slug=slug,
            is_active=is_active,
            category_id=category.name,
            description=description,
            price=price
        )
        db.session.add(food_item)
        db.session.commit()
    food_item = get_food_item(name)
    if food_item:
        return food_item


def delete_food_item(food_item_name):
    food_item = FoodItem.query.filter_by(name=food_item_name).first()
    if food_item:
        db.session.delete(food_item)
        db.session.commit()


def update_food_item(food_item_name):
    food_item = FoodItem.query.filter_by(name=food_item_name).first()
    if food_item:
        db.session.add(food_item)
        db.session.commit()


class FoodAPI(Resource):
    @AUTH.login_required
    def post(self):
        body = request.json
        app_log.info("WTF: %s", body)
        if not get_category(body["category"]):
            resp = {
                "status": 400,
                "response": "Bad Request: Category not found"
            }
        else:
            food_item = create_food_item(body)
            if food_item:
                resp = {"status": 201}
            else:
                resp = {"status": 500}
        return Response(**resp)

    @AUTH.login_required
    def get(self):
        body = request.get_json()
        name = body['name']
        food_item = get_food_item(name)
        if food_item:
            return Response(status=200)
        else:
            return Response(status=404)

    @AUTH.login_required
    def delete(self):
        body = request.get_json()
        app_log.info('DELETING %s', body['name'])
        delete_food_item(body['name'])
        food_item = get_food_item(body['name'])
        if food_item:
            return Response(status=500)
        else:
            return Response(status=204)

    @AUTH.login_required
    def put(self):
        body = request.get_json()
        name = body['name']
        food_item = update_food_item(name)
        if food_item:
            return Response(status=200)
        else:
            return Response(status=404)

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
        app_log.info('- ContactAPI | OPTIONS | %s', location)
        return '', 200
