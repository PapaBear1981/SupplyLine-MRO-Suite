import secrets
import string
from datetime import datetime

from flask import current_app, jsonify, request

from auth import admin_required
from models import AuditLog, User, db


def generate_secure_password(length=12):
    """Generate a cryptographically secure random password"""
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]

    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))

    # Shuffle to avoid predictable patterns
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)

    return "".join(password_list)


def register_password_reset_routes(app):
    @app.route("/api/admin/users/<int:user_id>/reset-password", methods=["POST"])
    @admin_required
    def reset_user_password(user_id):
        """
        Reset a user's password to a temporary password
        Requires admin privileges
        """
        try:
            # Get the admin user performing the reset
            admin_user_id = request.current_user.get("user_id")
            admin_user = User.query.get(admin_user_id)

            if not admin_user:
                return jsonify({
                    "error": "Admin user not found",
                    "code": "ADMIN_NOT_FOUND"
                }), 404

            # Get the target user
            target_user = User.query.get(user_id)

            if not target_user:
                return jsonify({
                    "error": "User not found",
                    "code": "USER_NOT_FOUND"
                }), 404

            # Prevent resetting own password through this endpoint
            if admin_user_id == user_id:
                return jsonify({
                    "error": "Cannot reset your own password through this endpoint. Use the change password feature instead.",
                    "code": "CANNOT_RESET_OWN_PASSWORD"
                }), 400

            # Generate a secure temporary password
            temporary_password = generate_secure_password(12)

            # Set the new password
            target_user.set_password(temporary_password)

            # Force password change on next login
            target_user.force_password_change = True

            # Update password changed timestamp
            target_user.password_changed_at = datetime.utcnow()

            # Commit the changes
            db.session.commit()

            # Log the password reset action
            audit_log = AuditLog(
                action_type="admin_password_reset",
                action_details=f"Admin {admin_user.name} (ID: {admin_user_id}) reset password for user {target_user.name} (ID: {user_id})"
            )
            db.session.add(audit_log)
            db.session.commit()

            current_app.logger.info(
                "Password reset by admin",
                extra={
                    "admin_user_id": admin_user_id,
                    "admin_name": admin_user.name,
                    "target_user_id": user_id,
                    "target_user_name": target_user.name,
                    "target_employee_number": target_user.employee_number
                }
            )

            return jsonify({
                "success": True,
                "message": f"Password reset successfully for {target_user.name}",
                "temporary_password": temporary_password,
                "user": {
                    "id": target_user.id,
                    "name": target_user.name,
                    "employee_number": target_user.employee_number,
                    "force_password_change": target_user.force_password_change
                },
                "warning": "This temporary password will only be shown once. Please copy it now."
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Password reset error: {e!s}",
                extra={
                    "admin_user_id": request.current_user.get("user_id"),
                    "target_user_id": user_id,
                    "error": str(e)
                }
            )
            return jsonify({
                "error": "Failed to reset password",
                "code": "PASSWORD_RESET_FAILED",
                "details": str(e)
            }), 500

    @app.route("/api/admin/users/search", methods=["GET"])
    @admin_required
    def search_users_for_password_reset():
        """
        Search users for password reset
        Supports filtering by employee number, name, or department
        """
        try:
            # Get search parameters
            search_query = request.args.get("q", "").strip()
            department = request.args.get("department", "").strip()
            include_inactive = request.args.get("include_inactive", "false").lower() == "true"

            # Build query
            query = User.query

            # Filter by active status
            if not include_inactive:
                query = query.filter_by(is_active=True)

            # Apply search filters
            if search_query:
                search_term = f"%{search_query}%"
                query = query.filter(
                    db.or_(
                        User.employee_number.like(search_term),
                        User.name.like(search_term)
                    )
                )

            if department:
                query = query.filter_by(department=department)

            # Order by name
            users = query.order_by(User.name).all()

            # Return user data with password change info
            return jsonify([{
                "id": user.id,
                "name": user.name,
                "employee_number": user.employee_number,
                "department": user.department,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "force_password_change": user.force_password_change,
                "password_changed_at": user.password_changed_at.isoformat() if user.password_changed_at else None,
                "created_at": user.created_at.isoformat()
            } for user in users]), 200

        except Exception as e:
            current_app.logger.error(
                f"User search error: {e!s}",
                extra={
                    "admin_user_id": request.current_user.get("user_id"),
                    "error": str(e)
                }
            )
            return jsonify({
                "error": "Failed to search users",
                "code": "USER_SEARCH_FAILED",
                "details": str(e)
            }), 500

    return app
