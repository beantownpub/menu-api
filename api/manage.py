import os
from flask_script import Manager
from flask_migrate import Migrate
from app import APP
from database.db import db


PSQL = {
    'user': os.environ.get('DATABASE_USERNAME'),
    'password': os.environ.get('DATABASE_PASSWORD'),
    'host': os.environ.get('DATABASE_HOST'),
    'db': os.environ.get('DATABASE_NAME'),
    'port': os.environ.get('DATABASE_PORT')
}

database = f"postgresql://{PSQL['user']}:{PSQL['password']}@{PSQL['host']}:{PSQL['port']}/{PSQL['db']}"

APP.config['SQLALCHEMY_DATABASE_URI'] = database
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(APP, db)
manager = Manager(APP)

# manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
