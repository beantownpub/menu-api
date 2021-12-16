import os
from flask_sqlalchemy import SQLAlchemy

from api.libs.logging import init_logger

db = SQLAlchemy()

LOG = init_logger(os.environ.get('LOG_LEVEL'))

def init_database(app):
    LOG.info('Initializing databases')
    db.init_app(app=app)
    with app.app_context():
        db.create_all()
