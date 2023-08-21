import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.libs.db_utils import run_db_action, get_item_by_slug, get_all_items, get_item_by_sku
from api.libs.logging import init_logger
from api.libs.utils import convert_to_dict, make_slug, make_uuid, ParamArgs
from .menu import delete_all_items_in_category, get_items_by_category

AUTH = HTTPBasicAuth()

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('products.py logging level %s', LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    if password.strip() == api_pwd.strip():
        verified = True
    else:
        LOG.info('Access Denied - %s', username)
        verified = False
    return verified


def get_items(location, status, table, all=False):
    item_list = []
    if not all:
        query = {"location": location, "is_active": status}
    else:
        query = {"location": location}
    items = get_all_items(table, query)
    for item in items:
        item_list.append(convert_to_dict(item))
    return item_list


def add_items_to_categories(categories):
    for category in categories:
        category['items'] = get_items_by_category(category['location'], category['name'], all=True)
    return categories


class ItemsAPI(Resource):
    @AUTH.login_required
    def post(self, table_name):
        '''Create a new product'''
        body = request.json
        if body.get('sku'):
            del body['sku']
        body['slug'] = make_slug(body['name'])
        LOG.debug("[POST] ItemsAPI | PATH %s | Name: %s | Location: %s", request.path, body['name'], body['location'])
        item = self._item_by('slug', table_name, body['slug'], body['location'], with_response=False)
        LOG.debug("[POST] ITEM %s", item)
        if item:
            LOG.debug("[POST] Item %s already exists", item.name)
            resp = {"status": 400, "response": f"Table: {table_name} {item.name} already exists"}
        else:
            self._create_item(body, table_name=table_name, location=body['location'])
            resp = {"status": 201, "response": f"Product {body['name']} created"}
        return Response(**resp)

    @AUTH.login_required
    def get(self, table_name):
        '''GET products
        PARAMS
        :category: The category the products belong to
        :location: The location products belong to (REQUIRED)
        :status: active, inactive, all (default is all)
        :name: name of the product
        :sku: The SKU of the product
        '''
        args = ParamArgs(request.args)
        LOG.debug("[GET] ItemsAPI | Table: %s | PATH: %s | Args: %s", table_name, request.path, args.map)
        if args.sku:
            resp = self._item_by('sku', table_name, args.sku, args.location)
        elif args.name:
            LOG.debug("[GET] Item by slug | %s | Location: %s", args.name, args.location)
            resp = self._item_by('slug', table_name, args.name, args.location)
        else:
            if args.status != None:
                items = get_items(args.location, args.status, table_name)
            else:
                items = get_items(args.location, args.status, table_name, all=True)
                if args.with_items:
                    items = add_items_to_categories(items)
            resp = {"status": 200, "response": json.dumps(items), "mimetype": "application/json"}
        return Response(**resp)

    @AUTH.login_required
    def delete(self, table_name):
        args = ParamArgs(request.args)
        LOG.debug("[DELETE] ItemsAPI | PATH: %s | Args: %s", request.path, args)
        item = self._item_by('sku', table_name, args.sku, args.location, with_response=False)
        if not item:
            LOG.info('404 DELETE Item SKU %s not found', args.sku)
            resp = {"status": 404, "response": "Product not found"}
        else:
            if table_name == 'categories':
                delete_all_items_in_category(args.location, item.name)
            run_db_action(action='delete', item=item)
            resp = {"status": 204, "response": "Product deleted"}
        return Response(**resp)

    @AUTH.login_required
    def put(self, table_name):
        body = request.json
        LOG.debug("[PUT] ItemsAPI | Args: %s | Body: %s", request.path, body)
        item = self._item_by('slug', table_name, body['slug'], body['location'], with_response=False)
        LOG.debug("[PUT] ITEM %s", item)
        if not item:
            LOG.info('[PUT] ItemsAPI | 404 %s not found', body['name'])
            resp = {"status": 404, "response": f"{table_name} {body['slug']} not found"}
        else:
            LOG.debug('UPDATING %s', body['slug'])
            run_db_action(action='update', item=item, body=body, table=table_name)
            resp = {"status": 201, "response": "Product updated"}
        return Response(**resp)

    def options(self, table_name):
        LOG.info('ItemsAPI | OPTIONS | %s', table_name)
        return '', 200

    def _create_item(self, body, category=None, table_name=None, location=None):
        if not body.get('uuid'):
            body['uuid'] = make_uuid()
        LOG.debug('ItemsAPI | CREATE | %s', body)
        run_db_action(action='create', item=category, body=body, table=table_name, location=location)

    def _item_by(self, by, table_name, value, location, with_response=True):
        LOG.debug("[BY] %s | Table: %s | Value: %s | Location: %s", by, table_name, value, location)
        if by == 'sku':
            item = get_item_by_sku(table_name, value)
        elif by == 'slug':
            item = get_item_by_slug(table_name, value, location)
        else:
            raise MenuDBException('Cannot find items by %s', by)
        LOG.debug("[BY] %s  ITEM %s", by, item)
        if not with_response:
            return item
        if not item:
            LOG.debug("[BY] %s | 404 | ITEM %s", by, item)
            response = {"status": 404, "response": "Product not found"}
        else:
            LOG.debug("[WTF] ITEM %s", item)
            response = {"status": 200, "response": json.dumps(convert_to_dict(item)), "mimetype": "application/json"}
        return response
