from flask import Blueprint, request, jsonify
from models.user_model import (
    create_user, find_user_by_email, verify_password,
    update_user, to_safe_user
)
from utils.token_utils import create_jwt
from middleware.auth import jwt_required
from datetime import datetime

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
      data = request.get_json(force=True)
      first_name = (data.get("firstName") or "").strip()
      last_name  = (data.get("lastName") or "").strip()
      email      = (data.get("email") or "").strip()
      password   = (data.get("password") or "")
      # Force role to be "user" for public registration
      role       = "user"

      if len(first_name) < 2 or len(last_name) < 2:
          return jsonify({"success": False, "message": "First/Last name too short"}), 400
      if len(password) < 6:
          return jsonify({"success": False, "message": "Password must be at least 6 chars"}), 400

      if find_user_by_email(email):
          return jsonify({"success": False, "message": "Email already registered!"}), 400

      user_doc = create_user(first_name, last_name, email, password, role=role)
      safe_user = to_safe_user(user_doc)

      token = create_jwt({"sub": safe_user["id"], "role": safe_user["role"]})
      return jsonify({
          "success": True,
          "message": "Registration successful!",
          "data": {"user": safe_user, "token": token}
      }), 201
    except Exception as e:
      print("Register error:", e)
      return jsonify({"success": False, "message": "Server error during registration"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        role = (data.get("role") or "").strip().lower()

        if role and role not in ["user", "admin"]:
            return jsonify({"success": False, "message": "Invalid role. Must be 'user' or 'admin'"}), 400

        user = find_user_by_email(email)
        if not user:
            return jsonify({"success": False, "message": "Invalid email or password!"}), 401
        if not user.get("isActive", True):
            return jsonify({"success": False, "message": "Account is deactivated"}), 403
        if not verify_password(user["password"], password):
            return jsonify({"success": False, "message": "Invalid email or password!"}), 401
        if not user.get("isEmailVerified", True):
            return jsonify({"success": False, "message": "Please verify your email!"}), 403
        
        # Check if role matches if provided
        user_role = user.get("role", "user")
        if role and user_role != role:
            return jsonify({"success": False, "message": f"Account is not registered as {role}"}), 403
        usage = user.get("usageStats", {"lastLogin": None, "totalLogins": 0})
        usage["lastLogin"] = datetime.utcnow()
        usage["totalLogins"] = (usage.get("totalLogins") or 0) + 1
        update_user({"_id": user["_id"]}, {"usageStats": usage})

        safe_user = to_safe_user(user)
        token = create_jwt({"sub": safe_user["id"], "role": safe_user["role"]})

        return jsonify({
            "success": True,
            "message": "Login successful",
            "data": {"user": safe_user, "token": token}
        })
    except Exception as e:
        print("Login error:", e)
        return jsonify({"success": False, "message": "Server error during login"}), 500

@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    from models.user_model import to_safe_user
    user = to_safe_user(getattr(request, "user", None))
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify({"success": True, "data": {"user": user}})

@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    return jsonify({"success": True, "message": "Logged out successfully"})
