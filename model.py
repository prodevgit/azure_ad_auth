from flask import Flask
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import datetime
from _datetime import timedelta
ma = Marshmallow()
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    access_token = db.Column(db.Text,nullable=True)
    refresh_token = db.Column(db.Text,nullable=True)
    id_token = db.Column(db.Text,nullable=True)
    creation_date = db.Column(db.Integer, nullable=False)
    last_login = db.Column(db.Integer, nullable=False)

    def __init__(self, name , email , access_token , refresh_token ,id_token):
        self.name = name
        self.email = email
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.id_token = id_token
        t1 = datetime.now()
        self.creation_date = datetime.timestamp(t1)
        self.last_login = datetime.timestamp(t1)
    
        
class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(1))
    email = fields.String(required=True, validate=validate.Length(1))
    access_token = fields.String(validate=validate.Length(1))
    refresh_token = fields.String(validate=validate.Length(1))
    id_token = fields.String(validate=validate.Length(1))
    creation_date = fields.DateTime()
    last_login = fields.DateTime()