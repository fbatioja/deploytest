from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from enum import Enum

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class Formatos(Enum):
    mp3 = 1
    aac = 2
    ogg = 3
    wav = 4
    wma = 5

class Status(Enum):
    UPLOADED = 1
    PROCESSED = 2

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128))
    newFormat = db.Column(db.Enum(Formatos))
    timeCreated = db.Column(db.Integer)
    status = db.Column(db.Enum(Status))
    userEmail = db.Column(db.String(128))

class TaskSchema(Schema):
    id=fields.Int(dump_only=True)
    filename = fields.Str()
    newFormat = EnumField(Formatos)
    timeCreated = fields.Int(dump_only=True)
    status = EnumField(Status)
    userEmail = fields.Str()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    password2 = db.Column(db.String(50))
    email = db.Column(db.String(50))


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password', 'password2')
        include_relationships = True
        load_instance = True

