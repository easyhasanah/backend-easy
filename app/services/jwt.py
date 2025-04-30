from flask import request, jsonify, current_app
import jwt
from functools import wraps

# Dekorator untuk verifikasi token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = data['userId']
            # bisa gunakan data['username'] jika ingin validasi user di sini
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token sudah kadaluarsa'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token tidak valid'}), 401

        return f(user_id, *args, **kwargs)

    return decorated