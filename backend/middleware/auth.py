from functools import wraps
from flask import request, jsonify
from utils.token_utils import decode_jwt

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        decoded = decode_jwt(token)
        if not decoded:
            return jsonify({"success": False, "message": "Invalid or expired token"}), 401
        request.user = decoded
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Missing or invalid token"}), 401
        token = auth_header.split(" ")[1]
        decoded = decode_jwt(token)
        if not decoded:
            return jsonify({"success": False, "message": "Invalid or expired token"}), 401
        if decoded.get("role") != "admin":
            return jsonify({"success": False, "message": "Admin access required"}), 403
        request.user = decoded
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization", None)
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"success": False, "message": "Missing or invalid token"}), 401
            token = auth_header.split(" ")[1]
            decoded = decode_jwt(token)
            if not decoded:
                return jsonify({"success": False, "message": "Invalid or expired token"}), 401
            if decoded.get("role") != required_role:
                return jsonify({"success": False, "message": f"{required_role.title()} access required"}), 403
            request.user = decoded
            return f(*args, **kwargs)
        return decorated_function
    return decorator
