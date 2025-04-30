from flask import Blueprint, jsonify, request, current_app
from app.models import db, Users
import jwt
import datetime
from app.services.jwt import token_required

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/', methods=['GET'])
@token_required
def get_by_id(user_id):
    users = Users.query.get_or_404(user_id)
    return jsonify(users.to_dict())

@users_bp.route('/login', methods=['POST'])
def login():
    input = request.get_json()

    username = str(input['username'])
    password = str(input['password'])

    users = Users.query.filter_by(username=username).first()
    if not users:
        return jsonify({'message': 'username tidak ditemukan'}), 401

    if (username == users.username and password == users.password):
        token = jwt.encode({
            'username': username,
            'userId': users.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            "status":"Success",
            "token": token
            }), 200
    else:
        return jsonify({'message': 'username atau password salah'}), 401
        



