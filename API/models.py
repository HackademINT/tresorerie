#!/usr/bin/python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from flask_marshmallow import Marshmallow
from werkzeug.security import check_password_hash
from marshmallow import Schema, fields
from config import Config

# Initialization

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Initialize user login

class APIuser(db.Model):
    __tablename__ = 'api_user'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return 'APIuser %r' % self.id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Database SQLAlchemy models

class User(db.Model):
    __tablename__ = 'user'
    id            = db.Column(db.Integer, primary_key=True)
    fname         = db.Column(db.String(100), nullable=False)
    lname         = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return '<User %r %r>' % (self.fname, self.lname)


class Event(db.Model):
    __tablename__ = 'event'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    date          = db.Column(db.Date, nullable=False)
    description   = db.Column(db.String(500), default='')

    def __repr__(self):
        return '<Event %r>' % self.name


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id            = db.Column(db.Integer, primary_key=True)
    sum           = db.Column(db.Float, nullable=False)
    description   = db.Column(db.String(500), default='')
    user          = db.relationship('User', backref=backref('transaction', cascade="all,delete"))
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    event         = db.relationship('Event', backref=backref('transaction', cascade="all,delete"))
    event_id      = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), nullable=False)
    type          = db.Column(db.Boolean, nullable=False) # 0 for outflows, 1 for inflows
    onhold        = db.Column(db.Boolean, nullable=False, default=1)

    def __repr__(self):
        return '<Transaction %r>' % self.id


# Database Marshmallow schemas

class SimpleUserSchema(ma.ModelSchema):
    class Meta:
        model = User

class SimpleEventSchema(ma.ModelSchema):
    class Meta:
        model = Event

class SimpleTransactionSchema(ma.ModelSchema):
    class Meta:
        model = Transaction

class TransactionSchema(ma.ModelSchema):
    id = fields.Integer()
    sum = fields.Float()
    description = fields.String()
    user = fields.Nested(SimpleUserSchema)
    event = fields.Nested(SimpleEventSchema)
    type = fields.Boolean()
    onhold = fields.Boolean()


class UserSchema(ma.ModelSchema):
    id = fields.Integer()
    fname = fields.String()
    lname = fields.String()
    email = fields.String()
    transaction = fields.Nested(SimpleTransactionSchema, many=True)


class EventSchema(ma.ModelSchema):
    id = fields.Integer()
    name = fields.String()
    date = fields.String()
    description = fields.String()
    transaction = fields.Nested(SimpleTransactionSchema, many=True)

