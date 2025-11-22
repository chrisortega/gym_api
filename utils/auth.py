import jwt, os
from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")

def generate_access_token(token_data):
    payload = {
        "user_id": token_data["user_id"],
        "gym_id": token_data["gym_id"],
        "exp": datetime.utcnow() + timedelta(days=1)      
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def authenticate_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")        
        if not auth_header:
            return jsonify({"message": "Access token missing"}), 401
        try:
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded
            
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 403
        return f(*args, **kwargs)
    return wrapper
