from flask import Flask
from flask_restful import Api
from vistas import VistaTasks, VistaUpdateTask, VistaGetFiles, VistaTask
from modelos import db
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)

dbHost = os.environ.get("DB_HOST")
dbNameGestorTareas = os.environ.get("DB_NAME_GESTORTAREAS")
dbUser = os.environ.get("DB_USER")
dbPassword = os.environ.get("DB_PASSWORD")

if not dbHost:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestor-tareas.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{dbUser}:{dbPassword}@{dbHost}/{dbNameGestorTareas}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET_KEY"]
app.config['PROPAGATE_EXCEPTIONS'] = True
app_context = app.app_context()
app_context.push()

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

api = Api(app)
api.add_resource(VistaTasks, '/tasks')
api.add_resource(VistaTask, '/tasks/<int:id_task>')
api.add_resource(VistaUpdateTask, '/updateTask')
api.add_resource(VistaGetFiles, '/tasks/<filename>')

jwt = JWTManager(app)