"""
Department management routes
"""
from flask import jsonify, request, current_app
from models import db, Department, User
from auth.jwt_manager import jwt_required, permission_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


def register_department_routes(app):
    """Register department management routes"""

    # Get all departments
    @app.route('/api/departments', methods=['GET'])
    @jwt_required
    def get_departments():
        """Get all departments"""
        try:
            include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

            if include_inactive:
                departments = Department.query.all()
            else:
                departments = Department.query.filter_by(is_active=True).all()

            return jsonify([dept.to_dict() for dept in departments])
        except SQLAlchemyError:
            logger.exception("Error fetching departments")
            return jsonify({'error': 'Failed to fetch departments'}), 500

    # Get a specific department
    @app.route('/api/departments/<int:id>', methods=['GET'])
    @jwt_required
    def get_department(id):
        """Get a specific department"""
        try:
            department = Department.query.get_or_404(id)
            return jsonify(department.to_dict())
        except SQLAlchemyError:
            logger.exception("Error fetching department %s", id)
            return jsonify({'error': 'Failed to fetch department'}), 500

    # Create a new department
    @app.route('/api/departments', methods=['POST'])
    @permission_required('department.create')
    def create_department():
        """Create a new department"""
        try:
            data = request.get_json() or {}

            # Validate and normalize input
            raw_name = (data.get('name') or '').strip()
            if not raw_name:
                return jsonify({'error': 'Department name is required'}), 400

            # Pre-check for duplicate (case-insensitive)
            existing = Department.query.filter(
                db.func.lower(Department.name) == raw_name.lower()
            ).first()
            if existing:
                return jsonify({'error': 'Department with this name already exists'}), 400

            # Create new department
            department = Department(
                name=raw_name,
                description=(data.get('description') or '').strip(),
                is_active=data.get('is_active', True)
            )

            db.session.add(department)
            db.session.commit()

            logger.info(f"Department created: {department.name} (ID: {department.id})")
            return jsonify(department.to_dict()), 201

        except IntegrityError:
            db.session.rollback()
            logger.exception("Unique constraint violation creating department")
            return jsonify({'error': 'Department with this name already exists'}), 400
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error creating department")
            return jsonify({'error': 'Failed to create department'}), 500

    # Update a department
    @app.route('/api/departments/<int:id>', methods=['PUT'])
    @permission_required('department.update')
    def update_department(id):
        """Update a department"""
        try:
            department = Department.query.get_or_404(id)
            data = request.get_json() or {}

            # Update fields
            if 'name' in data:
                new_name = (data['name'] or '').strip()
                if not new_name:
                    return jsonify({'error': 'Department name cannot be empty'}), 400
                # Check if new name conflicts with existing department (case-insensitive)
                existing = Department.query.filter(
                    db.func.lower(Department.name) == new_name.lower(),
                    Department.id != id
                ).first()
                if existing:
                    return jsonify({'error': 'Department with this name already exists'}), 400
                department.name = new_name

            if 'description' in data:
                department.description = (data['description'] or '').strip()

            if 'is_active' in data:
                department.is_active = data['is_active']

            db.session.commit()

            logger.info(f"Department updated: {department.name} (ID: {department.id})")
            return jsonify(department.to_dict())

        except IntegrityError:
            db.session.rollback()
            logger.exception("Unique constraint violation updating department %s", id)
            return jsonify({'error': 'Department with this name already exists'}), 400
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error updating department %s", id)
            return jsonify({'error': 'Failed to update department'}), 500

    # Delete a department (soft delete)
    @app.route('/api/departments/<int:id>', methods=['DELETE'])
    @permission_required('department.delete')
    def delete_department(id):
        """Delete a department (soft delete by setting is_active to False)"""
        try:
            department = Department.query.get_or_404(id)

            # Soft delete - just mark as inactive
            department.is_active = False
            db.session.commit()

            logger.info(f"Department deactivated: {department.name} (ID: {department.id})")
            return jsonify({'message': 'Department deactivated successfully'})

        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error deleting department %s", id)
            return jsonify({'error': 'Failed to delete department'}), 500

    # Hard delete a department
    @app.route('/api/departments/<int:id>/hard-delete', methods=['DELETE'])
    @permission_required('department.hard_delete')
    def hard_delete_department(id):
        """Permanently delete a department from the database"""
        try:
            department = Department.query.get_or_404(id)
            department_name = department.name

            # Check for referential integrity - verify no users are assigned to this department
            user_count = User.query.filter_by(department=department_name).count()
            if user_count > 0:
                return jsonify({
                    'error': f'Cannot delete department. {user_count} user(s) are assigned to this department. Please reassign users before deleting.',
                    'user_count': user_count
                }), 409

            # Hard delete - permanently remove from database
            db.session.delete(department)
            db.session.commit()

            logger.info(f"Department permanently deleted: {department_name} (ID: {id})")
            return jsonify({'message': 'Department permanently deleted successfully'})

        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error hard deleting department %s", id)
            return jsonify({'error': 'Failed to permanently delete department'}), 500

