import json
import os
import logging

import sqlalchemy

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Category
from api.libs.db_utils import run_db_action, get_item_from_db

AUTH = HTTPBasicAuth()
TABLE = 'category'


if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


@AUTH.verify_password
def verify_password(username, password):
    app_log.info("Verifying user %s", username)
    if password.strip() == os.environ.get("API_PASSWORD"):
        return True
    return False


def category_to_dict(category):
    category_dict = {
        'name': category.name,
        'sku': category.id,
        'is_active': category.is_active
    }
    return category_dict



def get_all_categories():
    category_list = []
    try:
        categories = Category.query.filter_by().all()
    except sqlalchemy.exc.OperationalError:
        app_log.error('DB GET ERROR')
        try:
            categories = Category.query.filter_by().all()
        except sqlalchemy.exc.OperationalError:
            raise
    if categories:
        for category in categories:
            category = get_item_from_db(TABLE, category.name)
            category_list.append(category)
        # app_log.info('Categories: %s', category_list)
        return [x for x in category_list if x]


class CategoriesAPI(Resource):
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
        app_log.info('Creating category %s', name)
        body = request.get_json()
        run_db_action(action='create', body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    @AUTH.login_required
    def delete(self, name):
        app_log.debug('Deleting category %s', name)
        category = get_item_from_db(TABLE, name)
        run_db_action(action='delete', item=category)
        return Response(status=204)

    @AUTH.login_required
    def get(self, name):
        app_log.info("GET Category: %s", name)
        category = get_item_from_db(TABLE, name)
        if not category:
            return Response(status=404)
        category = json.dumps(category_to_dict(category))
        return Response(category, mimetype='application/json', status=200)

    @AUTH.login_required
    def put(self, name):
        body = request.json
        app_log.info("PUT Body: %s", body)
        category = get_item_from_db(TABLE, name)
        if not category:
            return Response(status=404)
        run_db_action(action='update', item=category, body=body, table=TABLE)
        resp = {"status": 201}
        return Response(**resp)

    def options(self, location):
        app_log.info('- CategoryAPI | OPTIONS | %s', location)
        return '', 200
