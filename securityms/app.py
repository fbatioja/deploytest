from flask import Flask, app, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_cors import CORS
from flask_jwt_extended.utils import get_jwt, get_jwt_identity
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///security.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'agilemates-jwt'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()
db = SQLAlchemy(app)

db.init_app(app)

cors = CORS(app)
jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password',)
        include_relationships = True
        load_instance = True

usuario_schema = UsuarioSchema()

@app.route('/signup', methods = ['POST'])
def post():
    new_user = User(username=request.json["username"], password=request.json["password"], email=request.json["email"])
    user = User.query.filter(User.email == new_user.email).first()
    if user is None:
        db.session.add(new_user)
        db.session.commit()
        # return usuario_schema.dump(nuevo_usuario)
        additional_claims = {"email": new_user.email}
        access_token = create_access_token(identity = new_user.id, additional_claims= additional_claims)
        return {"message": "User created sucessfully", "token": access_token}
    else:
        return {"message": "User with email {} is already created".format(new_user.email)}

@app.route('/login', methods = ['POST'])
def postAuth():
    user = User.query.filter(User.username == request.json["username"] and User.password == request.json["password"]).first()
    db.session.commit()
    if user is None:
        return "User doesn't exists", 404
    else:
        additional_claims = {"email": user.email}
        access_token = create_access_token(identity = user.id, additional_claims=additional_claims)
        return {"message": "Sucessfull login", "token": access_token,"user": usuario_schema.dump(user)}

@app.route('/validate', methods = ['GET'])
@jwt_required()
def get():
    jwtHeader = get_jwt()
    identity = get_jwt_identity()
    if((jwtHeader["email"] == "") or (identity is None)):
        return "The user is not authorized to access to the resource", 403

    return jwtHeader,200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')





