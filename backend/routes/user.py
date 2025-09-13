from flask import Blueprint, request, jsonify
from models.user_model import (
    find_user_by_id, to_safe_user, update_user,
    verify_password, _hash_password
)
from middleware.auth import jwt_required

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user(current_user):
    user_doc = find_user_by_id(current_user["id"])
    if not user_doc:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    return jsonify({
        "success": True,
        "data": {"user": to_safe_user(user_doc)}
    })

@user_bp.route("/profile", methods=["PUT"])
@jwt_required
def update_profile(current_user):
    try:
        data = request.get_json(force=True)
        allowed_fields = [
            'firstName', 'lastName', 'phone', 'dateOfBirth', 'gender',
            'location', 'academicInfo', 'preferences'
        ]
        
        # Only update allowed fields
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        user_doc = update_user(current_user["id"], update_data)
        if not user_doc:
            return jsonify({"success": False, "message": "User not found"}), 404

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "data": {"user": to_safe_user(user_doc)}
        })

    except Exception as e:
        print("Update profile error:", e)
        return jsonify({
            "success": False,
            "message": "Server error while updating profile"
        }), 500

@user_bp.route("/change-password", methods=["PUT"])
@jwt_required
def change_password(current_user):
    try:
        data = request.get_json(force=True)
        current_password = data.get("currentPassword")
        new_password = data.get("newPassword")

        if not current_password or not new_password:
            return jsonify({
                "success": False,
                "message": "Current and new password are required"
            }), 400

        if len(new_password) < 6:
            return jsonify({
                "success": False,
                "message": "New password must be at least 6 characters"
            }), 400

        user_doc = find_user_by_id(current_user["id"])
        if not user_doc:
            return jsonify({"success": False, "message": "User not found"}), 404

        if not verify_password(current_password, user_doc["password"]):
            return jsonify({
                "success": False,
                "message": "Current password is incorrect"
            }), 400

        hashed_password = _hash_password(new_password)
        update_user(current_user["id"], {"password": hashed_password})

        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        })

    except Exception as e:
        print("Change password error:", e)
        return jsonify({
            "success": False,
            "message": "Server error while changing password"
        }), 500