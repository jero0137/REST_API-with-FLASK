from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from blocklist import BLOCKLIST

from db import db  
from models import UserModel
from schemas import UserSchema

blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        if UserModel.query.filter_by(username=user_data["username"]).first():
            abort(400, message="A user with that username already exists")
        
        user = UserModel(**user_data)
        user.password = sha256.hash(user.password)
        
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error has ocurred while inserting the user")
        
        return user
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data["username"]).first()
        
        if user and sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=str(user.id))
            return {"access_token": access_token}
        abort(401, message="Invalid username or password")

@blp.route("/logout")
class UserLogout(MethodView):
    @blp.response(200)
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}
        
    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blp.response(200, UserSchema)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return user