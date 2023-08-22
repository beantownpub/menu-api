import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.libs.db_utils import run_db_action, get_all_items, get_category_uuid
from api.libs.logging import init_logger
from api.libs.utils import ParamArgs
from api.libs.aws import get_secret

SECRET = get_secret()
AUTH = HTTPBasicAuth()

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('menu.py logging level %s', LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_username = SECRET["api_username"].strip()
    api_password = SECRET["api_password"].strip()
    if username.strip() == api_username and password.strip() == api_password:
        verified = True
    else:
        verified = False
    return verified


@AUTH.error_handler
def unauthorized():
    LOG.info("Unauthorized request")
    resp = {
        "status": 401,
        "response": "Unauthorized",
        "mimetype": "application/json",
    }
    return Response(**resp)


def convert_to_dict(item):
    item_dict = item.__dict__
    if item_dict.get('_sa_instance_state'):
        del item_dict['_sa_instance_state']
    if item_dict.get('creation_date'):
        del item_dict['creation_date']
    return item_dict


def get_categories(location, all=False):
    item_list = []
    if not all:
        query = {"location": location, "is_active": True}
    else:
        query = {"location": location}
    items = get_all_items('categories', query)
    for item in items:
        item_list.append(convert_to_dict(item))
    return item_list


def get_items_by_category(location, category, all=False, to_dict=True):
    uuid = get_category_uuid(location, category)
    item_list = []
    if not all:
        query = {"location": location, "category_id": uuid, "is_active": True}
    else:
        query = {"location": location, "category_id": uuid}
    items = get_all_items('products', query)
    for item in items:
        if to_dict:
            item = convert_to_dict(item)
        item_list.append(item)
    return item_list


def get_sides(location, all=False, to_dict=True):
    item_list = []
    if not all:
        query = {"location": location, "is_active": True}
    else:
        query = {"location": location}
    items = get_all_items('sides', query)
    for item in items:
        if to_dict:
            item = convert_to_dict(item)
        item_list.append(item)
    return item_list


def delete_all_items_in_category(location, category_name):
    items = get_items_by_category(location, category_name, all=True, to_dict=False)
    LOG.debug('ITEMS %s to delete', len(items))
    if items:
        for item in items:
            name = item.name
            run_db_action(action='delete', item=item)
            LOG.debug('Deleted item %s', name)


class MenuAPI(Resource):
    @AUTH.login_required
    def get(self):
        '''GET Full menus'''
        menu = {}
        args = ParamArgs(request.args)
        LOG.debug("[GET] MenuAPI | Args: %s", args.map)
        categories = get_categories(args.location)
        for category in categories:
            category['items'] = get_items_by_category(args.location, category['name'])
        menu['categories'] = categories
        sides = get_sides(args.location)
        side_list = [side['name'] for side in sides]
        menu['sides'] = side_list
        resp = {"status": 200, "response": json.dumps(menu), "mimetype": "application/json"}
        return Response(**resp)

    def options(self, location):
        LOG.info('- ItemsAPI | OPTIONS | %s', location)
        return '', 200
