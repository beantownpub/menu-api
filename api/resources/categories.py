import json
import os
import logging

import sqlalchemy

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Category, FoodItem
from api.database.db import db

AUTH = HTTPBasicAuth()


if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


@AUTH.verify_password
def verify_password(username, password):
    api_user = os.environ.get("API_USER")
    api_pwd = os.environ.get("API_USER_PWD")
    if username == api_user and password == api_pwd:
        return True
    return False


def food_item_to_dict(food_item):
    food_item_dict = {
        'name': food_item.name,
        'sku': food_item.id,
        'category': food_item.category.name,
        'description': food_item.description,
        'price': food_item.price,
        'is_active': food_item.is_active
    }
    return food_item_dict


def convert_category(category):
    category_dict = {
        'name': category.name,
        'is_active': category.is_active,
        'id': category.id
    }
    return category_dict


def get_category(name):
    category = Category.query.filter_by(name=name).first()
    if category:
        category = {
            'name': category.name,
            'is_active': category.is_active,
            'id': category.id
        }
    return category


def update_category(name, request):
    category = Category.query.filter_by(name=name).first()
    if category:
        body = request.get_json()
        category.name = body['name']
        category.is_active = body['is_active']
        db.session.add(category)
        db.session.commit()
        return get_category(body['name'])


def read_categories_from_db():
    try:
        categories = Category.query.filter_by().all()
    except sqlalchemy.exc.OperationalError:
        app_log.error('DB GET ERROR')
        try:
            categories = Category.query.filter_by().all()
        except sqlalchemy.exc.OperationalError:
            raise
    return categories


def get_all_categories():
    category_list = []
    categories = read_categories_from_db()
    if categories:
        for category in categories:
            category = get_category(category.name)
            category_list.append(category)
        # app_log.info('Categories: %s', category_list)
    return [x for x in category_list if x]


def get_categories_and_food_items():
    app_log.info('Getting all categories and food items')
    category_list = []
    categories = get_all_categories()
    if categories:
        app_log.info('Categories: %s', categories)
        for cat in categories:
            app_log.info('Category: %s', cat)
            food_item_list = []
            food_items = FoodItem.query.filter(FoodItem.category.has(name=cat['name'])).all()
            if food_items:
                app_log.info('Items: %s', food_items)
                for food_item in food_items:
                    food_item_list.append(food_item_to_dict(food_item))
            cat['items'] = food_item_list
            category_list.append(cat)
    return category_list


def write_to_db(name, is_active):
    try:
        category = Category(name=name, is_active=is_active)
        db.session.add(category)
        db.session.commit()
    except sqlalchemy.exc.OperationalError:
        app_log.error('DB ERROR')
        try:
            category = Category(name=name, is_active=is_active)
            db.session.add(category)
            db.session.commit()
        except sqlalchemy.exc.OperationalError:
            raise


def create_category(request):
    body = request.get_json()
    name = body['name']
    is_active = body['is_active']
    if not get_category(name):
        write_to_db(name, is_active)
    category = get_category(name)
    if category:
        return category


def delete_category(category_name):
    category = Category.query.filter_by(name=category_name).first()
    if category:
        db.session.delete(category)
        db.session.commit()


class CategoriesAPI(Resource):
    @AUTH.login_required
    def get(self):
        categories = get_categories_and_food_items()
        if categories:
            categories = json.dumps(categories)
            return Response(categories, mimetype='application/json', status=200)
        else:
            return Response(status=404)


class CategoryAPI(Resource):
    @AUTH.login_required
    def post(self, category):
        app_log.info('Creating category %s', category)
        category = create_category(request)
        if category:
            return Response(status=201)
        else:
            return Response(status=500)

    @AUTH.login_required
    def delete(self, category):
        app_log.info('DELETING %s', category)
        delete_category(category)
        category = get_category(category)
        if category:
            return Response(status=500)
        else:
            return Response(status=204)

    @AUTH.login_required
    def get(self, category):
        app_log.info("GET Category: %s", category)
        category = get_category(category)
        if category:
            return Response(status=200)
        else:
            return Response(status=404)

    @AUTH.login_required
    def put(self, category):
        app_log.info('Updating category %s', category)
        category = update_category(category, request)
        if category:
            return Response(status=204)
        else:
            return Response(status=500)
