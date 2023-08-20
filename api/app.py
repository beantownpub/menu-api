import logging
import os

from flask import Flask, request
from flask_restful import Api
from flask_cors import CORS

from api.database.db import init_database
from api.libs.logging import init_logger
from api.resources.routes import init_routes


class MenuAppException(Exception):
    """base class for menu exceptions """


LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
ORIGIN_URL = os.environ.get('ORIGIN_URL')
APP = Flask(__name__.split('.')[0], instance_path='/opt/app/api')
API = Api(APP)

PSQL = {
    'user': os.environ.get('DB_USER').rstrip("\n"),
    'password': os.environ.get('DB_PASSWORD').rstrip("\n"),
    'host': os.environ.get('DB_HOST').rstrip("\n"),
    'db': os.environ.get('DB_NAME').rstrip("\n"),
    'port': os.environ.get('DB_PORT').rstrip("\n")
}

for k, v in PSQL.items():
    if not v:
        msg = f"Env variable not set for database {k}"
        raise MenuAppException(msg)


database = f"postgresql://{PSQL['user']}:{PSQL['password']}@{PSQL['host']}:{PSQL['port']}/{PSQL['db']}"

APP.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
APP.config['SQLALCHEMY_POOL_SIZE'] = 10
APP.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
APP.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
APP.config['CORS_ALLOW_HEADERS'] = True
APP.config['CORS_EXPOSE_HEADERS'] = True
APP.config['SQLALCHEMY_DATABASE_URI'] = database
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ORIGINS = [
    "https://beantown.jalgraves.com",
    "http://localhost:3000",
    "http://localhost",
    "https://beantownpub.com",
    "https://dev.beantownpub.com",
    "https://www.beantownpub.com",
    "https://beantown.dev.jalgraves.com"
]

cors = CORS(
    APP,
    resources={r"/v1/menu/*": {"origins": ORIGINS}},
    supports_credentials=True
)

LOG = init_logger(LOG_LEVEL)
init_database(APP)
LOG.info('DB initialized')
init_routes(API)
LOG.info('Routes initialized')



@APP.after_request
def after_request(response):
    origin = request.environ.get('HTTP_ORIGIN')
    if origin and origin in ORIGINS:
        LOG.info(' - ADDING ORIGIN HEADER | %s', origin)
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
