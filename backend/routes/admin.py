from flask import Blueprint, request, jsonify
from middleware.auth import admin_required, jwt_required
from models.user_model import users, to_safe_user
from bson.objectid import ObjectId

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
    """Admin dashboard endpoint - only accessible to admin users"""
    try:
        # Get basic stats
        total_users = users.count_documents({})
        active_users = users.count_documents({"isActive": True})
        admin_users = users.count_documents({"role": "admin"})
        regular_users = users.count_documents({"role": "user"})
        
        stats = {
            "totalUsers": total_users,
            "activeUsers": active_users,
            "adminUsers": admin_users,
            "regularUsers": regular_users
        }
        
        return jsonify({
            "success": True,
            "message": "Admin dashboard data",
            "data": {"stats": stats}
        })
    except Exception as e:
        print("Admin dashboard error:", e)
        return jsonify({"success": False, "message": "Server error"}), 500

@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    """Get all users - admin only"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit
        
        users_cursor = users.find({}).skip(skip).limit(limit)
        user_list = [to_safe_user(user) for user in users_cursor]
        total_count = users.count_documents({})
        
        return jsonify({
            "success": True,
            "data": {
                "users": user_list,
                "pagination": {
                    "currentPage": page,
                    "totalPages": (total_count + limit - 1) // limit,
                    "totalCount": total_count,
                    "limit": limit
                }
            }
        })
    except Exception as e:
        print("Get users error:", e)
        return jsonify({"success": False, "message": "Server error"}), 500

@admin_bp.route("/users/<user_id>/toggle-status", methods=["PUT"])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status - admin only"""
    try:
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        new_status = not user.get("isActive", True)
        users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"isActive": new_status}}
        )
        
        return jsonify({
            "success": True,
            "message": f"User {'activated' if new_status else 'deactivated'} successfully"
        })
    except Exception as e:
        print("Toggle user status error:", e)
        return jsonify({"success": False, "message": "Server error"}), 500

@admin_bp.route("/create-admin", methods=["POST"])
@admin_required
def create_admin_user():
    """Create new admin user - admin only"""
    try:
        from models.user_model import create_user, find_user_by_email
        
        data = request.get_json(force=True)
        first_name = (data.get("firstName") or "").strip()
        last_name  = (data.get("lastName") or "").strip()
        email      = (data.get("email") or "").strip()
        password   = (data.get("password") or "")

        if len(first_name) < 2 or len(last_name) < 2:
            return jsonify({"success": False, "message": "First/Last name too short"}), 400
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 chars"}), 400

        if find_user_by_email(email):
            return jsonify({"success": False, "message": "Email already registered!"}), 400

        # Create admin user
        user_doc = create_user(first_name, last_name, email, password, role="admin")
        safe_user = to_safe_user(user_doc)

        return jsonify({
            "success": True,
            "message": "Admin user created successfully!",
            "data": {"user": safe_user}
        }), 201
    except Exception as e:
        print("Create admin error:", e)
        return jsonify({"success": False, "message": "Server error during admin creation"}), 500

@admin_bp.route("/promote-user", methods=["PUT"])
@admin_required
def promote_user_to_admin():
    """Promote existing user to admin - admin only"""
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        
        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400
        
        user = users.find_one({"email": email.lower().strip()})
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        if user.get("role") == "admin":
            return jsonify({"success": False, "message": "User is already an admin"}), 400
        
        # Update user role to admin
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"role": "admin"}}
        )
        
        return jsonify({
            "success": True,
            "message": f"User {user['firstName']} {user['lastName']} promoted to admin successfully"
        })
    except Exception as e:
        print("Promote user error:", e)
        return jsonify({"success": False, "message": "Server error"}), 500