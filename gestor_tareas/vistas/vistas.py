from os import path
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..modelos import db, Task, TaskSchema
from celery import Celery
import json
import os
import time

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
celery_app = Celery('gestor',
                    broker='amqp://admin:mypass@rabbitmq:5672',
                    backend='rpc://')


class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        tasks = Task.query.all()
        return {"tasks": tasks_schema.dump(tasks, many=True)}, 200

    @jwt_required()
    def post(self):
        # Get user data
        userIdentity = get_jwt_identity()
        userEmail = userIdentity["email"]
        userId = userIdentity["id"]
        tiempo = round(time.time() * 1000)
        file = request.files['file']
        try:
            if not os.path.exists(f"./Files/{userId}"):
                os.mkdir(f"./Files/{userId}/")
            file_location = f"./Files/{userId}/{file.filename}"
            with open(file_location, "wb+") as file_save:
                file_save.write(file.read())

            nueva_task = Task(filename=file.filename,
                              newFormat=request.form.get("newFormat"),
                              timeCreated=tiempo,
                              status="UPLOADED",
                              userEmail=userEmail)
            db.session.add(nueva_task)
            db.session.commit()
            r = celery_app.send_task('tasks.convert_task',
                                     kwargs={
                                         'filename': file.filename,
                                         "newFormat": request.form.get("newFormat"),
                                         "userId": userId})
            return {"task": task_schema.dump(nueva_task), "cola": r.id}, 200
        except:

            return "Ocurrió un error al guardar el archivo", 400


class VistaGetFiles(Resource):
    def get(self):
        return "ok"


class VistaUpdateTask(Resource):
    def post(self):
        f = open("demofile3.txt", "a")
        f.write("Algo")
        f.close()
