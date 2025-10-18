"""
Department management routes
"""
from flask import jsonify, request
from models import db, Department
from auth.jwt_manager import jwt_required, permission_required
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
        except Exception as e:
            logger.error(f"Error fetching departments: {str(e)}")
            return jsonify({'error': 'Failed to fetch departments'}), 500

    # Get a specific department
    @app.route('/api/departments/<int:id>', methods=['GET'])
    @jwt_required
    def get_department(id):
        """Get a specific department"""
        try:
            department = Department.query.get_or_404(id)
            return jsonify(department.to_dict())
        except Exception as e:
            logger.error(f"Error fetching department {id}: {str(e)}")
            return jsonify({'error': 'Failed to fetch department'}), 500

    # Create a new department
    @app.route('/api/departments', methods=['POST'])
    @permission_required('user.manage')
    def create_department():
        """Create a new department"""
        try:
            data = request.get_json() or {}

            # Validate required fields
            if not data.get('name'):
                return jsonify({'error': 'Department name is required'}), 400

            # Check if department already exists
            existing = Department.query.filter_by(name=data['name']).first()
            if existing:
                return jsonify({'error': 'Department with this name already exists'}), 400

            # Create new department
            department = Department(
                name=data['name'],
                description=data.get('description', ''),
                is_active=data.get('is_active', True)
            )

            db.session.add(department)
            db.session.commit()

            logger.info(f"Department created: {department.name} (ID: {department.id})")
            return jsonify(department.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating department: {str(e)}")
            return jsonify({'error': 'Failed to create department'}), 500

    # Update a department
    @app.route('/api/departments/<int:id>', methods=['PUT'])
    @permission_required('user.manage')
    def update_department(id):
        """Update a department"""
        try:
            department = Department.query.get_or_404(id)
            data = request.get_json() or {}

            # Update fields
            if 'name' in data:
                # Check if new name conflicts with existing department
                existing = Department.query.filter(
                    Department.name == data['name'],
                    Department.id != id
                ).first()
                if existing:
                    return jsonify({'error': 'Department with this name already exists'}), 400
                department.name = data['name']

            if 'description' in data:
                department.description = data['description']

            if 'is_active' in data:
                department.is_active = data['is_active']

            db.session.commit()

            logger.info(f"Department updated: {department.name} (ID: {department.id})")
            return jsonify(department.to_dict())

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating department {id}: {str(e)}")
            return jsonify({'error': 'Failed to update department'}), 500

    # Delete a department (soft delete)
    @app.route('/api/departments/<int:id>', methods=['DELETE'])
    @permission_required('user.manage')
    def delete_department(id):
        """Delete a department (soft delete by setting is_active to False)"""
        try:
            department = Department.query.get_or_404(id)

            # Soft delete - just mark as inactive
            department.is_active = False
            db.session.commit()

            logger.info(f"Department deactivated: {department.name} (ID: {department.id})")
            return jsonify({'message': 'Department deactivated successfully'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting department {id}: {str(e)}")
            return jsonify({'error': 'Failed to delete department'}), 500

    # Hard delete a department
    @app.route('/api/departments/<int:id>/hard-delete', methods=['DELETE'])
    @permission_required('user.manage')
    def hard_delete_department(id):
        """Permanently delete a department from the database"""
        try:
            department = Department.query.get_or_404(id)
            department_name = department.name

            # Hard delete - permanently remove from database
            db.session.delete(department)
            db.session.commit()

            logger.info(f"Department permanently deleted: {department_name} (ID: {id})")
            return jsonify({'message': 'Department permanently deleted successfully'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error hard deleting department {id}: {str(e)}")
            return jsonify({'error': 'Failed to permanently delete department'}), 500

