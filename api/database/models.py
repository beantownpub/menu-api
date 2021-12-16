from datetime import datetime

from .db import db


class FoodItem(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    slug = db.Column(db.String(50), unique=True)
    description = db.Column(db.String)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean)
    price = db.Column(db.Float)
    category_id = db.Column(db.String, db.ForeignKey('category.name'), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean)
    items = db.relationship('FoodItem', backref='category', lazy=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return '<Category %r>' % self.name


class Side(db.Model):
    _tablename_ = 'sides'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean)
    price = db.Column(db.Float)
    slug = db.Column(db.String(50), unique=True)
