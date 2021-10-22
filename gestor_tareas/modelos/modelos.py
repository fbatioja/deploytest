from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from enum import Enum

db = SQLAlchemy()

class Formatos(Enum):
    MP3 = 1
    AAC = 2
    OGG = 3
    WAV = 4
    WMA = 5

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