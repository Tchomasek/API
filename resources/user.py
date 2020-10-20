import sqlite3
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
    )

from models.user import UserModel
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
                        'username',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
)
_user_parser.add_argument(
                        'password',
                        type=str,
                        required=True,
                        help="This field cannot be blank. "
)

class UserList(Resource):
    def get(self):
        return {'users': [user.json() for user in UserModel.find_all()]}

class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message':'Username already exist'}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message':'User Create Successfully.'}, 201

class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message':'user not found'}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message':'user not found'}, 404
        user.delete_from_db()
        return {'message':'user deleted'}

class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity = user.id, fresh = True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'message': 'authentication failed'}, 401

class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # jti is "JWT ID", a unique identifier for a JWT
        BLACKLIST.add(jti)
        return {'message':'successfully logged out'}, 200

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200












#-
