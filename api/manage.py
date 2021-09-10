from flask_script import Manager
from flask_migrate import Migrate
from app import APP
from database.db import db

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

migrate = Migrate(APP, db)
manager = Manager(APP)

# manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
