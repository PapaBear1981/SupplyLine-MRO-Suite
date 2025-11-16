"""
Warehouse management routes.
Handles CRUD operations for warehouses and warehouse inventory.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from auth.jwt_manager import jwt_required
from models import Chemical, Tool, User, Warehouse, db


warehouses_bp = Blueprint("warehouses", __name__)


def require_admin():
    """Decorator to require admin privileges."""
    user_id = request.current_user.get("user_id")
    user = db.session.get(User, user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Admin privileges required"}), 403
    return None


@warehouses_bp.route("/warehouses", methods=["GET"])
@jwt_required
def get_warehouses():
    """
    Get list of all warehouses with pagination.
    Query params:
        - include_inactive: Include inactive warehouses (default: false)
        - warehouse_type: Filter by type (main/satellite)
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50, max: 200)
    """
    try:
        # PERFORMANCE: Add pagination to prevent unbounded dataset returns
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        include_inactive = request.args.get("include_inactive", "false").lower() == "true"
        warehouse_type = request.args.get("warehouse_type")

        # Validate pagination parameters
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 200:
            return jsonify({"error": "Per page must be between 1 and 200"}), 400

        query = Warehouse.query

        # Filter by active status
        if not include_inactive:
            query = query.filter_by(is_active=True)

        # Filter by warehouse type
        if warehouse_type:
            query = query.filter_by(warehouse_type=warehouse_type)

        # Order by type (main first) then name
        query = query.order_by(
            Warehouse.warehouse_type.desc(),  # main before satellite
            Warehouse.name
        )

        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        warehouses = pagination.items

        # Return paginated response
        response = {
            "warehouses": [w.to_dict(include_counts=True) for w in warehouses],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }

        return jsonify(response), 200

    except Exception as e:
        import traceback
        print(f"ERROR in get_warehouses: {e!s}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses", methods=["POST"])
@jwt_required
def create_warehouse():
    """
    Create a new warehouse (admin only).
    Required fields: name
    Optional fields: address, city, state, zip_code, country, warehouse_type, contact_person, contact_phone, contact_email
    """
    # Check admin privileges
    admin_check = require_admin()
    if admin_check:
        return admin_check

    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("name"):
            return jsonify({"error": "Warehouse name is required"}), 400

        # Check if warehouse with same name already exists
        existing = Warehouse.query.filter_by(name=data["name"]).first()
        if existing:
            return jsonify({"error": "Warehouse with this name already exists"}), 400

        # Create warehouse
        current_user_id = request.current_user.get("user_id")
        warehouse = Warehouse(
            name=data["name"],
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            country=data.get("country", "USA"),
            warehouse_type=data.get("warehouse_type", "satellite"),
            contact_person=data.get("contact_person"),
            contact_phone=data.get("contact_phone"),
            contact_email=data.get("contact_email"),
            is_active=True,
            created_by_id=current_user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(warehouse)
        db.session.commit()

        return jsonify({
            "message": "Warehouse created successfully",
            "warehouse": warehouse.to_dict()
        }), 201

    except Exception as e:
        import traceback
        print(f"ERROR in create_warehouse: {e!s}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses/<int:warehouse_id>", methods=["GET"])
@jwt_required
def get_warehouse(warehouse_id):
    """Get details of a specific warehouse."""
    try:
        warehouse = db.session.get(Warehouse, warehouse_id)

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        return jsonify(warehouse.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses/<int:warehouse_id>", methods=["PUT"])
@jwt_required
def update_warehouse(warehouse_id):
    """
    Update warehouse details (admin only).
    Updatable fields: name, address, city, state, zip_code, country, warehouse_type, is_active, contact_person, contact_phone, contact_email
    """
    # Check admin privileges
    admin_check = require_admin()
    if admin_check:
        return admin_check

    try:
        warehouse = db.session.get(Warehouse, warehouse_id)

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        data = request.get_json()

        # Check if new name conflicts with existing warehouse
        if data.get("name") and data["name"] != warehouse.name:
            existing = Warehouse.query.filter_by(name=data["name"]).first()
            if existing:
                return jsonify({"error": "Warehouse with this name already exists"}), 400

        # Update fields
        if "name" in data:
            warehouse.name = data["name"]
        if "address" in data:
            warehouse.address = data["address"]
        if "city" in data:
            warehouse.city = data["city"]
        if "state" in data:
            warehouse.state = data["state"]
        if "zip_code" in data:
            warehouse.zip_code = data["zip_code"]
        if "country" in data:
            warehouse.country = data["country"]
        if "warehouse_type" in data:
            warehouse.warehouse_type = data["warehouse_type"]
        if "is_active" in data:
            warehouse.is_active = data["is_active"]
        if "contact_person" in data:
            warehouse.contact_person = data["contact_person"]
        if "contact_phone" in data:
            warehouse.contact_phone = data["contact_phone"]
        if "contact_email" in data:
            warehouse.contact_email = data["contact_email"]

        warehouse.updated_at = datetime.now()

        db.session.commit()

        return jsonify({
            "message": "Warehouse updated successfully",
            "warehouse": warehouse.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses/<int:warehouse_id>", methods=["DELETE"])
@jwt_required
def delete_warehouse(warehouse_id):
    """
    Soft delete a warehouse (admin only).
    Sets is_active to False instead of actually deleting.
    """
    # Check admin privileges
    admin_check = require_admin()
    if admin_check:
        return admin_check

    try:
        warehouse = db.session.get(Warehouse, warehouse_id)

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        # Check if warehouse has items
        tools_count = warehouse.tools.count()
        chemicals_count = warehouse.chemicals.count()

        if tools_count > 0 or chemicals_count > 0:
            return jsonify({
                "error": f"Cannot delete warehouse with items. Please transfer {tools_count} tools and {chemicals_count} chemicals first."
            }), 400

        # Soft delete
        warehouse.is_active = False
        warehouse.updated_at = datetime.now()

        db.session.commit()

        return jsonify({
            "message": "Warehouse deactivated successfully",
            "warehouse": warehouse.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses/<int:warehouse_id>/stats", methods=["GET"])
@jwt_required
def get_warehouse_stats(warehouse_id):
    """Get statistics for a warehouse."""
    try:
        warehouse = db.session.get(Warehouse, warehouse_id)

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        # Debug: Check direct query
        tools_count_direct = Tool.query.filter_by(warehouse_id=warehouse_id).count()
        print(f"DEBUG: Warehouse {warehouse_id} - Direct query tools count: {tools_count_direct}")
        print(f"DEBUG: Warehouse {warehouse_id} - Relationship tools count: {warehouse.tools.count()}")

        # Get counts by category
        tools_by_category = db.session.query(
            Tool.category,
            db.func.count(Tool.id)
        ).filter(
            Tool.warehouse_id == warehouse_id
        ).group_by(Tool.category).all()

        chemicals_by_category = db.session.query(
            Chemical.category,
            db.func.count(Chemical.id)
        ).filter(
            Chemical.warehouse_id == warehouse_id
        ).group_by(Chemical.category).all()

        # Get counts by status
        tools_by_status = db.session.query(
            Tool.status,
            db.func.count(Tool.id)
        ).filter(
            Tool.warehouse_id == warehouse_id
        ).group_by(Tool.status).all()

        chemicals_by_status = db.session.query(
            Chemical.status,
            db.func.count(Chemical.id)
        ).filter(
            Chemical.warehouse_id == warehouse_id
        ).group_by(Chemical.status).all()

        return jsonify({
            "warehouse": warehouse.to_dict(),
            "tools": {
                "total": tools_count_direct,  # Use direct query instead of relationship
                "by_category": dict(tools_by_category),
                "by_status": dict(tools_by_status)
            },
            "chemicals": {
                "total": warehouse.chemicals.count(),
                "by_category": dict(chemicals_by_category),
                "by_status": dict(chemicals_by_status)
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses/<int:warehouse_id>/tools", methods=["GET"])
@jwt_required
def get_warehouse_tools(warehouse_id):
    """
    Get all tools in a warehouse.
    Query params:
        - status: Filter by status
        - category: Filter by category
        - search: Search in tool_number, serial_number, description
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)
    """
    try:
        warehouse = db.session.get(Warehouse, warehouse_id)

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        # Get query parameters
        status = request.args.get("status")
        category = request.args.get("category")
        search = request.args.get("search")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        # Build query
        query = Tool.query.filter_by(warehouse_id=warehouse_id)

        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Tool.tool_number.like(search_pattern),
                    Tool.serial_number.like(search_pattern),
                    Tool.description.like(search_pattern)
                )
            )

        # Paginate
        pagination = query.order_by(Tool.tool_number).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            "tools": [tool.to_dict() for tool in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses/<int:warehouse_id>/chemicals", methods=["GET"])
@jwt_required
def get_warehouse_chemicals(warehouse_id):
    """
    Get all chemicals in a warehouse.
    Query params:
        - status: Filter by status
        - category: Filter by category
        - search: Search in part_number, lot_number, description
        - page: Page number (default: 1)
        - per_page: Items per page (default: 50)
    """
    try:
        warehouse = db.session.get(Warehouse, warehouse_id)

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        # Get query parameters
        status = request.args.get("status")
        category = request.args.get("category")
        search = request.args.get("search")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        # Build query
        query = Chemical.query.filter_by(warehouse_id=warehouse_id)

        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Chemical.part_number.like(search_pattern),
                    Chemical.lot_number.like(search_pattern),
                    Chemical.description.like(search_pattern)
                )
            )

        # Paginate
        pagination = query.order_by(Chemical.part_number).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            "chemicals": [chemical.to_dict() for chemical in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@warehouses_bp.route("/warehouses/<int:warehouse_id>/inventory", methods=["GET"])
@jwt_required
def get_warehouse_inventory(warehouse_id):
    """
    Get combined inventory (tools and chemicals) for a warehouse.
    Query params:
        - item_type: Filter by type (tool/chemical)
        - search: Search across all items
    """
    try:
        warehouse = db.session.get(Warehouse, warehouse_id)

        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        # Get query parameters
        item_type = request.args.get("item_type")
        search = request.args.get("search")

        inventory = []

        # Get tools
        if not item_type or item_type == "tool":
            tools_query = Tool.query.filter_by(warehouse_id=warehouse_id)

            if search:
                search_pattern = f"%{search}%"
                tools_query = tools_query.filter(
                    or_(
                        Tool.tool_number.like(search_pattern),
                        Tool.serial_number.like(search_pattern),
                        Tool.description.like(search_pattern)
                    )
                )

            tools = tools_query.all()
            for tool in tools:
                tool_dict = tool.to_dict()
                tool_dict["item_type"] = "tool"
                tool_dict["tracking_number"] = tool.serial_number
                tool_dict["tracking_type"] = "serial"
                inventory.append(tool_dict)

        # Get chemicals
        if not item_type or item_type == "chemical":
            chemicals_query = Chemical.query.filter_by(warehouse_id=warehouse_id)

            if search:
                search_pattern = f"%{search}%"
                chemicals_query = chemicals_query.filter(
                    or_(
                        Chemical.part_number.like(search_pattern),
                        Chemical.lot_number.like(search_pattern),
                        Chemical.description.like(search_pattern)
                    )
                )

            chemicals = chemicals_query.all()
            for chemical in chemicals:
                chemical_dict = chemical.to_dict()
                chemical_dict["item_type"] = "chemical"
                chemical_dict["tracking_number"] = chemical.lot_number
                chemical_dict["tracking_type"] = "lot"
                inventory.append(chemical_dict)

        # Sort by description
        inventory.sort(key=lambda x: x.get("description", ""))

        return jsonify({
            "warehouse": warehouse.to_dict(),
            "inventory": inventory,
            "total": len(inventory)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
