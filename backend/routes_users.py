from datetime import datetime
from flask import Blueprint, jsonify, request
from auth.jwt_manager import jwt_required as login_required, permission_required
from models import AuditLog, User, UserActivity, db
import utils as password_utils
from utils.error_handler import handle_errors, log_security_event

# Create blueprint
users_bp = Blueprint("users", __name__)

def register_user_routes(app):
    # Register the blueprint
    app.register_blueprint(users_bp, url_prefix="/api")

@users_bp.route("/users", methods=["GET", "POST"])
@login_required
def users_route():
    # Check permissions
    user_payload = request.current_user
    permissions = set(user_payload.get("permissions", []))
    is_admin = user_payload.get("is_admin", False)
    is_materials = user_payload.get("department") == "Materials"
    
    # Allow access if admin, materials, or has user.view permission
    can_view = is_admin or is_materials or "user.view" in permissions
    can_manage = is_admin or "user.manage" in permissions
    
    if request.method == "GET":
        if not can_view:
            return jsonify({"error": "Insufficient permissions to view users"}), 403

        # Check if there's a search query for employee number
        search_query = request.args.get("q")

        # Check if we should include sensitive info (admin only)
        include_sensitive_info = is_admin or "user.manage" in permissions

        if search_query:
            # Search for users by employee number or name
            search_term = f"%{search_query}%"
            users = User.query.filter(
                db.or_(
                    User.employee_number.ilike(search_term),
                    User.name.ilike(search_term)
                )
            ).all()
        else:
            # Get all users
            users = User.query.all()
            
        return jsonify([u.to_dict(
            include_roles=True, 
            include_lockout_info=include_sensitive_info
        ) for u in users])

    # POST - Create a new user
    if not can_manage:
        return jsonify({"error": "Insufficient permissions to create users"}), 403
        
    data = request.get_json() or {}

    # Validate required fields
    required_fields = ["name", "employee_number", "department", "password"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Check if employee number already exists
    if User.query.filter_by(employee_number=data["employee_number"]).first():
        return jsonify({"error": "Employee number already exists"}), 400

    # Validate password strength
    is_valid, errors = password_utils.validate_password_strength(data.get("password"))
    if not is_valid:
        return jsonify({"error": "Password does not meet security requirements", "details": errors}), 400

    # Create new user
    u = User(
        name=data.get("name"),
        employee_number=data.get("employee_number"),
        department=data.get("department"),
        is_admin=data.get("is_admin", False),
        is_active=data.get("is_active", True)
    )
    u.set_password(data.get("password"))

    db.session.add(u)
    db.session.commit()

    # Log the action
    log = AuditLog(
        action_type="create_user",
        action_details=f"Created user {u.id} ({u.name})"
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(u.to_dict()), 201

@users_bp.route("/users/<int:id>", methods=["GET", "PUT", "DELETE"])
@login_required
def user_detail_route(id):
    # Check permissions
    user_payload = request.current_user
    permissions = set(user_payload.get("permissions", []))
    is_admin = user_payload.get("is_admin", False)
    
    can_view = is_admin or "user.view" in permissions
    can_manage = is_admin or "user.manage" in permissions
    
    # Get the user
    user = User.query.get_or_404(id)

    if request.method == "GET":
        if not can_view:
            return jsonify({"error": "Insufficient permissions to view user details"}), 403
            
        # Return user details with roles and lockout info for admins
        include_sensitive_info = is_admin or "user.manage" in permissions
        return jsonify(user.to_dict(
            include_roles=True, 
            include_lockout_info=include_sensitive_info
        ))

    if request.method == "PUT":
        if not can_manage:
            return jsonify({"error": "Insufficient permissions to update users"}), 403
            
        # Update user
        data = request.get_json() or {}

        # Update fields
        if "name" in data:
            user.name = data["name"]
        if "department" in data:
            user.department = data["department"]
        if "email" in data:
            user.email = data["email"]
        if "is_admin" in data:
            user.is_admin = data["is_admin"]
        if "is_active" in data:
            user.is_active = data["is_active"]
        if data.get("password"):
            # Validate password strength
            is_valid, errors = password_utils.validate_password_strength(data["password"])
            if not is_valid:
                return jsonify({"error": "Password does not meet security requirements", "details": errors}), 400
            user.set_password(data["password"])

        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type="update_user",
            action_details=f"Updated user {user.id} ({user.name})"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(user.to_dict(include_roles=True))

    if request.method == "DELETE":
        if not can_manage:
            return jsonify({"error": "Insufficient permissions to delete users"}), 403
            
        # Deactivate user instead of deleting
        user.is_active = False
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type="deactivate_user",
            action_details=f"Deactivated user {user.id} ({user.name})"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"message": f"User {user.name} deactivated successfully"})
    return None

@users_bp.route("/users/<int:id>/unlock", methods=["POST"])
@permission_required("user.manage")
def unlock_user_account(id):
    """Unlock a user account that has been locked due to failed login attempts."""
    # Get the user
    user = User.query.get_or_404(id)

    # Check if the account is actually locked
    if not user.is_locked():
        return jsonify({"message": f"Account for {user.name} is not locked"}), 400

    # Unlock the account
    user.unlock_account()

    # Log the action (get admin info from JWT token)
    user_payload = request.current_user
    log = AuditLog(
        action_type="account_unlocked",
        action_details=f'Admin {user_payload.get("user_name", "Unknown")} (ID: {user_payload.get("user_id")}) manually unlocked account for user {user.name} (ID: {user.id})'
    )
    db.session.add(log)

    # Add user activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="account_unlocked",
        description=f'Account unlocked by admin {user_payload.get("user_name", "Unknown")}',
        ip_address=request.remote_addr
    )
    db.session.add(activity)

    db.session.commit()

    return jsonify({
        "message": f"Account for {user.name} has been successfully unlocked",
        "user": user.to_dict(include_roles=True, include_lockout_info=True)
    }), 200
