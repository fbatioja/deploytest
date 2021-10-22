from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestor-tareas.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'agilemates-jwt'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app
