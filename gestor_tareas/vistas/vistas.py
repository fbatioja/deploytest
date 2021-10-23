from os import path
from flask import request, send_file
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..modelos import db, Task, TaskSchema
from celery import Celery
import os
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
celery_app = Celery('gestor',
                    broker='amqp://admin:mypass@rabbitmq:5672',
                    backend='rpc://')

smtp_server = "smtp.gmail.com"
port = 587
sender_email = "fileconvertergrupo18@gmail.com"
password = ""


class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        jwtHeader = get_jwt()
        tasks = Task.query.filter(Task.userEmail == jwtHeader["email"])
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
                                         "userId": userId,
                                         "taskId": nueva_task.id})
            return {"task": task_schema.dump(nueva_task), "cola": r.id}, 200
        except:
            return "Ocurrió un error al guardar el archivo", 400


class VistaGetFiles(Resource):
    @jwt_required()
    def get(self, filename):
        userIdentity = get_jwt_identity()
        userId = userIdentity["id"]
        #return "ok"
        return send_file(f"./Files/{userId}/Audio.mp3", mimetype=str(filename)[-3:], attachment_filename="Audio.mp3", as_attachment=True)


class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        jwtHeader = get_jwt()
        task = Task.query.filter_by(id=id_task, userEmail=jwtHeader["email"])
        if task is None:
            return None, 404

        return tasks_schema.dump(task), 200

    def put(self, id_task):
        pass

class VistaUpdateTask(Resource):
    def post(self):
        task = Task.query.get_or_404(request.json["taskId"])
        task.status = "PROCESSED"
        db.session.commit()
        message = MIMEMultipart("alternative")
        message["Subject"] = "Archivo procesado"
        message["From"] = sender_email
        message["To"] = task.userEmail

        newFile = task.filename[:-3] + str(task.newFormat)[-3:]

        text = f"""\
            Tu archivo está listo
            Hola,
            Nos alegra informarte que tu archivo {task.filename} se convirtió exitosamente.
            Para descargar tu archivo accede a la aplicación y solicita el archivo {newFile}.
            Grácias por preferirnos - Grupo 18"""

        html = f"""\
            <html>
                <body>
                    <h2>Tu archivo está listo</h2>
                        <p>
                            Hola...<br>
                            Nos alegra informarte que tu archivo <b>{task.filename}</b> se convirtió exitosamente.<br>
                            Para descargar tu archivo accede a la aplicación y solicita el archivo <b>{newFile}</b>.<br><br>
                            <i>Grácias por preferirnos - Grupo 18</i>
                        </p>
                    </body>
                </html>
            """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, task.userEmail, message.as_string()
                )
                server.quit()
        except Exception as e:
            print(e)
