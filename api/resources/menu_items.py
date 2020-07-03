import logging
from flask import Response, request
from flask_restful import Resource

from api.database.models import MenuItem

app_log = logging.getLogger()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


class MenuItemsAPI(Resource):
    def get(self):
        uri = request.environ.get('RAW_URI')
        origin = request.environ.get('HTTP_ORIGIN')
        if uri and origin:
            app_log.info('- GET | ORIGIN: %s | PATH: %s', origin, uri)
        menu_items = MenuItem.objects().to_json()
        return Response(menu_items, mimetype='application/json', status=200)

    def options(self):
        return '', 200

    def post(self):
        body = request.get_json()
        logging.info(body)
        menu_item = MenuItem(**body).save()
        _id = menu_item.id
        return {'id': str(_id)}, 200

    def delete(self):
        name = request.get_json()['name']
        MenuItem.objects.get(name=name).delete()
        return '', 204


class MenuItemAPI(Resource):
    def get(self, item):
        menu_item = MenuItem.objects.get(name=item).to_json()
        return Response(menu_item, mimetype="application/json", status=200)

    def put(self, item):
        body = request.get_json()
        MenuItem.objects.get(name=item).update(**body)
        return '', 200

    def delete(self, item):
        MenuItem.objects.get(name=item).delete()
        return '', 200


class SectionsAPI(Resource):
    def get(self, category):
        menu_items = MenuItem.objects(category=category, is_active=True).to_json()
        app_log.info('- CategoryAPI | GET | Category: %s', category)
        app_log.info('- CategoryAPI | GET | Items: %s', menu_items)
        return Response(menu_items, mimetype='application/json', status=200)
