from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from ..modelos import db, Task, TaskSchema
from celery import Celery
import json

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
celery_app = Celery('gestor',
                    broker='amqp://admin:mypass@rabbitmq:5672',
                    backend='rpc://')

class VistaTasks(Resource):
    def get(self):
        tasks = Task.query.all()
        return {"tasks": tasks_schema.dump(tasks, many=True)}, 200
    
    def post(self):
        nueva_task = Task(filename="Archivo.txt", newFormat = "MP3", timeCreated = "1", status = "UPLOADED",  userEmail = "a@a.com")
        db.session.add(nueva_task)
        db.session.commit()
        r = celery_app.send_task('tasks.convert_task', kwargs={'x': "Archivo.txt"})
        return {"task":task_schema.dump(nueva_task), "cola": r.id}, 200

class VistaUpdateTask(Resource):
    def post(self):
        f = open("demofile3.txt", "a")
        f.write("Algo")
        f.close()