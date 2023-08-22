import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Side
from api.libs.db_utils import run_db_action
from api.libs.logging import init_logger
from api.libs.utils import get_uuid, make_slug, ParamArgs
from api.libs.aws import get_secret

SECRET = get_secret()
AUTH = HTTPBasicAuth()
TABLE = 'sides'

class MenuDBException(Exception):
    """Base class for menu database exceptions"""

LOG_LEVEL = os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
LOG.info('sides.py logging level %s', LOG_LEVEL)


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


def side_to_dict(side):
    LOG.debug('Convert to dict %s', side)
    side_dict = {
        'name': side.name,
        'sku': side.id,
        'uuid': side.uuid,
        'location': side.location
    }
    return side_dict

def get_side(location, name):
    LOG.debug('Location: %s | Name: %s')
    sides = Side.query.filter_by(location=location, name=name).all()
    return sides

def get_sides(location):
    LOG.debug('CHECK | %s | Location: %s')
    # return Side.query.filter(Side.category.has(location=location)).all()
    return Side.query.filter_by(location=location).all()

def get_location(args):
    location = args.get('location')
    return location

class SidesAPI(Resource):
    @AUTH.login_required
    def post(self):
        body = request.json
        side = get_side(body['location'], body['name'])
        LOG.debug('[POST] SidesAPI | SIDE: %s', body)
        if not side:
            body['slug'] = make_slug(body['name'])
            body['uuid'] = get_uuid()
            LOG.debug("SidesAPI | PATH %s | Name: %s | Location: %s", request.path, body['name'], body['location'])
            self.create_item(body)
            resp = {"status": 201}
        else:
            LOG.debug("[POST] SidesAPI | 400 | Side %s already exists", side[0].name)
            resp = {"status": 400, "response": f"Side {side[0].name} already exists"}
        return Response(**resp)

    @AUTH.login_required
    def get(self):
        args = ParamArgs(request.args)
        location = args.location
        LOG.debug('[GET] SidesAPI | Location: %s | Args: %s', location, args.to_dict())
        if not args.to_dict()['name']:
            LOG.debug('[GET] SidesAPI | NO NAME |%s', args)
        sides = get_sides(location)
        sides_list = []
        if sides:
            for side in sides:
                LOG.debug('SidesAPI | SIDE: %s', side)
                sides_list.append(side.name)
        return Response(json.dumps(sides_list), mimetype='application/json', status=200)

    def create_item(self, body):
        LOG.debug('SidesAPI | Adding %s to DB', body['name'])
        run_db_action(action='create', body=body, table=TABLE)
