from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


def role_check(role):
    def decorator(function):
        @jwt_required()
        @wraps(function)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if role in claims['role']:
                return function(*args, **kwargs)
            return jsonify({"message":"User not authorized"}), 401

        return wrapper

    return decorator
