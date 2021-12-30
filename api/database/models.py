from datetime import datetime
from .db import db


class Products(db.Model):
    _tablename_ = 'products'
    category_id = db.Column(db.String, db.ForeignKey('category.uuid'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    id = db.Column(db.Integer, unique=True, primary_key=True)
    description = db.Column(db.String)
    is_active = db.Column(db.Boolean)
    location = db.Column(db.String(25), required=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    slug = db.Column(db.String(50))
    uuid = db.Column(db.String, unique=True)


class Category(db.Model):
    _tablename_ = 'categories'
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String)
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    is_active = db.Column(db.Boolean)
    items = db.relationship('Products', backref='category', lazy=True)
    location = db.Column(db.String(25), required=True)
    name = db.Column(db.String(50))
    slug = db.Column(db.String(50))
    uuid = db.Column(db.String, unique=True)
    order_number = db.Column(db.Integer)

    def __repr__(self):
        return '<Category %r>' % self.name


class Sides(db.Model):
    _tablename_ = 'sides'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean)
    location = db.Column(db.String(25), required=True)
    price = db.Column(db.Float)
    slug = db.Column(db.String(50))
    uuid = db.Column(db.String, unique=True)


class Flavors(db.Model):
    _tablename_ = 'flavors'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean)
    location = db.Column(db.String(25), required=True)
    price = db.Column(db.Float)
    slug = db.Column(db.String(50))
    uuid = db.Column(db.String, unique=True)
