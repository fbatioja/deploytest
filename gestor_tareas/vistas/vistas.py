from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from ..modelos import db, Task, TaskSchema
import json

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

class VistaTasks(Resource):
    def get(self):
        tasks = Task.query.all()
        return {"tasks": tasks_schema.dump(tasks, many=True)}, 200
    
    def post(self):
        nueva_task = Task(filename="Archivo.txt")
        db.session.add(nueva_task)
        db.session.commit()
        return task_schema.dump(nueva_task), 200