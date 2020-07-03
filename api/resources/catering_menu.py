import json
import logging
import os
from flask import Response, request
from flask_restful import Resource

from api.database.models import MenuItem

app_log = logging.getLogger()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


def get_menu():
    app_log.info('Retrieving Catering Menu')
    menu = ''
    if os.path.isdir('./api/config/'):
        with open('./api/config/beantown_menu.json') as f:
            menu = json.load(f)
    return menu['catering']


class CateringAPI(Resource):

    def get(self):
        uri = request.environ.get('RAW_URI')
        origin = request.environ.get('HTTP_ORIGIN')
        if uri and origin:
            app_log.info('- GET | ORIGIN: %s | PATH: %s', origin, uri)
        menu_items = get_menu()
        return Response(menu_items, mimetype='application/json', status=200)
