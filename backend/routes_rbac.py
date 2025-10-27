from flask import jsonify, request

from auth import jwt_required, permission_required
from models import AuditLog, Permission, Role, RolePermission, User, UserRole, db


# Decorator to check if user has a specific permission


def register_rbac_routes(app):
    # Get all roles
    @app.route("/api/roles", methods=["GET"])
    @permission_required("role.manage")
    def get_roles():
        roles = Role.query.all()
        return jsonify([role.to_dict() for role in roles])

    # Get a specific role with its permissions
    @app.route("/api/roles/<int:id>", methods=["GET"])
    @permission_required("role.manage")
    def get_role(id):
        role = Role.query.get_or_404(id)
        return jsonify(role.to_dict(include_permissions=True))

    # Create a new role
    @app.route("/api/roles", methods=["POST"])
    @permission_required("role.manage")
    def create_role():
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("name"):
            return jsonify({"error": "Role name is required"}), 400

        # Check if role name already exists
        if Role.query.filter_by(name=data["name"]).first():
            return jsonify({"error": "Role name already exists"}), 400

        # Create new role
        role = Role(
            name=data.get("name"),
            description=data.get("description", ""),
            is_system_role=False
        )

        db.session.add(role)
        db.session.commit()

        # Add permissions if provided
        if "permissions" in data and isinstance(data["permissions"], list):
            for permission_id in data["permissions"]:
                permission = Permission.query.get(permission_id)
                if permission:
                    role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
                    db.session.add(role_permission)

            db.session.commit()

        # Log the action
        log = AuditLog(
            action_type="create_role",
            action_details=f"Created role {role.id} ({role.name})"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(role.to_dict(include_permissions=True)), 201

    # Update a role
    @app.route("/api/roles/<int:id>", methods=["PUT"])
    @permission_required("role.manage")
    def update_role(id):
        role = Role.query.get_or_404(id)

        data = request.get_json() or {}

        # For system roles, only allow permission updates, not name/description changes
        if role.is_system_role:
            if "name" in data or "description" in data:
                return jsonify({"error": "System role name and description cannot be modified"}), 403
        else:
            # Update role properties for non-system roles
            if "name" in data:
                # Check if new name already exists for another role
                existing_role = Role.query.filter_by(name=data["name"]).first()
                if existing_role and existing_role.id != role.id:
                    return jsonify({"error": "Role name already exists"}), 400
                role.name = data["name"]

            if "description" in data:
                role.description = data["description"]

        # Update permissions if provided (allowed for both system and non-system roles)
        if "permissions" in data and isinstance(data["permissions"], list):
            # Remove all existing permissions
            RolePermission.query.filter_by(role_id=role.id).delete()

            # Add new permissions
            for permission_id in data["permissions"]:
                permission = Permission.query.get(permission_id)
                if permission:
                    role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
                    db.session.add(role_permission)

        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type="update_role",
            action_details=f"Updated role {role.id} ({role.name})"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(role.to_dict(include_permissions=True))

    # Delete a role
    @app.route("/api/roles/<int:id>", methods=["DELETE"])
    @permission_required("role.manage")
    def delete_role(id):
        role = Role.query.get_or_404(id)

        # Don't allow deletion of system roles
        if role.is_system_role:
            return jsonify({"error": "System roles cannot be deleted"}), 403

        # Remove all user-role associations
        UserRole.query.filter_by(role_id=role.id).delete()

        # Remove all role-permission associations
        RolePermission.query.filter_by(role_id=role.id).delete()

        # Delete the role
        db.session.delete(role)

        # Log the action
        log = AuditLog(
            action_type="delete_role",
            action_details=f"Deleted role {role.id} ({role.name})"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"message": "Role deleted successfully"})

    # Get all permissions
    @app.route("/api/permissions", methods=["GET"])
    @permission_required("role.manage")
    def get_permissions():
        permissions = Permission.query.all()
        return jsonify([permission.to_dict() for permission in permissions])

    # Get permissions by category
    @app.route("/api/permissions/categories", methods=["GET"])
    @permission_required("role.manage")
    def get_permissions_by_category():
        permissions = Permission.query.all()

        # Group permissions by category
        categories = {}
        for permission in permissions:
            category = permission.category or "Uncategorized"
            if category not in categories:
                categories[category] = []
            categories[category].append(permission.to_dict())

        return jsonify(categories)

    # Get user roles
    @app.route("/api/users/<int:user_id>/roles", methods=["GET"])
    @permission_required("user.view")
    def get_user_roles(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify([role.to_dict() for role in user.roles])

    # Update user roles
    @app.route("/api/users/<int:user_id>/roles", methods=["PUT"])
    @permission_required("user.edit")
    def update_user_roles(user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json() or {}

        if "roles" not in data or not isinstance(data["roles"], list):
            return jsonify({"error": "Roles list is required"}), 400

        # Remove all existing user-role associations
        UserRole.query.filter_by(user_id=user.id).delete()

        # Add new roles
        for role_id in data["roles"]:
            role = Role.query.get(role_id)
            if role:
                user_role = UserRole(user_id=user.id, role_id=role.id)
                db.session.add(user_role)

        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type="update_user_roles",
            action_details=f"Updated roles for user {user.id} ({user.name})"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify([role.to_dict() for role in user.roles])

    # Get current user permissions
    @app.route("/api/auth/permissions", methods=["GET"])
    @jwt_required
    def get_current_user_permissions():
        user = User.query.get(request.current_user["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "permissions": user.get_permissions(),
            "roles": [role.to_dict() for role in user.roles]
        })

    return app
