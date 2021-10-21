from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import enum

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))

class TaskSchema(Schema):
    id=fields.Int(dump_only=True)
    filename = fields.Str()