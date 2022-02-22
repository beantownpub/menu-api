from datetime import datetime
from .db import DB


class Products(DB.Model):
    _tablename_ = 'products'
    category_id = DB.Column(DB.String, DB.ForeignKey('category.uuid'), nullable=False)
    creation_date = DB.Column(DB.DateTime, default=datetime.utcnow)
    id = DB.Column(DB.Integer, unique=True, primary_key=True)
    description = DB.Column(DB.String)
    is_active = DB.Column(DB.Boolean)
    location = DB.Column(DB.String(25), nullable=False)
    name = DB.Column(DB.String(50))
    price = DB.Column(DB.Float)
    slug = DB.Column(DB.String(50))
    uuid = DB.Column(DB.String, unique=True)


class Category(DB.Model):
    _tablename_ = 'categories'
    creation_date = DB.Column(DB.DateTime, default=datetime.utcnow)
    description = DB.Column(DB.String)
    id = DB.Column(DB.Integer, autoincrement=True, primary_key=True, unique=True)
    is_active = DB.Column(DB.Boolean)
    items = DB.relationship('Products', backref='category', lazy=True)
    location = DB.Column(DB.String(25), nullable=False)
    name = DB.Column(DB.String(50))
    slug = DB.Column(DB.String(50))
    uuid = DB.Column(DB.String, unique=True)
    order_number = DB.Column(DB.Integer)

    def __repr__(self):
        return '<Category %r>' % self.name


class Sides(DB.Model):
    _tablename_ = 'sides'
    id = DB.Column(DB.Integer, unique=True, primary_key=True)
    name = DB.Column(DB.String(50))
    creation_date = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_active = DB.Column(DB.Boolean)
    location = DB.Column(DB.String(25), nullable=False)
    price = DB.Column(DB.Float)
    slug = DB.Column(DB.String(50))
    uuid = DB.Column(DB.String, unique=True)


class Flavors(DB.Model):
    _tablename_ = 'flavors'
    id = DB.Column(DB.Integer, unique=True, primary_key=True)
    name = DB.Column(DB.String(50))
    creation_date = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_active = DB.Column(DB.Boolean)
    location = DB.Column(DB.String(25), nullable=False)
    price = DB.Column(DB.Float)
    slug = DB.Column(DB.String(50))
    uuid = DB.Column(DB.String, unique=True)
