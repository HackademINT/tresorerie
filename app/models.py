#!/usr/bin/python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

class LdapUser(db.Model, UserMixin):
    __tablename__ = 'ldap_user'
    id        = db.Column(db.Integer, primary_key=True)
    login     = db.Column(db.String(100), nullable=False)
    is_admin  = db.Column(db.Boolean, nullable=False, default=False)
