from . import create_app
from flask_restful import Api

from .vistas import VistaTasks, VistaUpdateTask
from .modelos import db
from flask_jwt_extended import JWTManager

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

api = Api(app)
api.add_resource(VistaTasks, '/tasks')
api.add_resource(VistaUpdateTask, '/updateTask')

jwt = JWTManager(app)