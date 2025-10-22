"""
Database Management Routes

Provides API endpoints for database backup, restore, and health monitoring.
Admin-only access required for all operations.
"""

from flask import request, jsonify, send_file, current_app
from functools import wraps
import logging
import os
from pathlib import Path
from utils.database_backup import DatabaseBackupManager
from auth import jwt_required, admin_required

logger = logging.getLogger(__name__)


def register_database_routes(app):
    """Register database management routes."""
    
    def get_backup_manager():
        """Get a DatabaseBackupManager instance with current app config."""
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Extract database path from SQLite URI
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            # For PostgreSQL or other databases, this feature is not supported
            return None
        
        return DatabaseBackupManager(db_path)
    
    @app.route('/api/admin/database/backup', methods=['POST'])
    @jwt_required
    @admin_required
    def create_database_backup():
        """
        Create a manual backup of the database.

        Request body (optional):
            {
                "backup_name": "custom_name",
                "compress": true
            }
        """
        try:
            backup_manager = get_backup_manager()
            if not backup_manager:
                return jsonify({
                    'success': False,
                    'message': 'Database backup is only supported for SQLite databases'
                }), 400

            data = request.get_json() or {}
            backup_name = data.get('backup_name')
            compress = data.get('compress')

            success, message, backup_path = backup_manager.create_backup(
                backup_name=backup_name,
                compress=compress
            )

            if success:
                logger.info(f"Manual backup created by {request.current_user.get('user_name', 'Unknown')}", extra={
                    'user_id': request.current_user.get('user_id'),
                    'backup_path': backup_path
                })

                return jsonify({
                    'success': True,
                    'message': message,
                    'backup_path': backup_path
                })
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 500
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error creating backup: {str(e)}'
            }), 500
    
    @app.route('/api/admin/database/backups', methods=['GET'])
    @jwt_required
    @admin_required
    def list_database_backups():
        """List all available database backups."""
        try:
            backup_manager = get_backup_manager()
            if not backup_manager:
                return jsonify({
                    'success': False,
                    'message': 'Database backup is only supported for SQLite databases'
                }), 400
            
            backups = backup_manager.list_backups()
            
            return jsonify({
                'success': True,
                'backups': backups,
                'count': len(backups)
            })
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error listing backups: {str(e)}'
            }), 500
    
    @app.route('/api/admin/database/backup/<path:backup_filename>', methods=['DELETE'])
    @jwt_required
    @admin_required
    def delete_database_backup(backup_filename):
        """Delete a specific backup file."""
        try:
            backup_manager = get_backup_manager()
            if not backup_manager:
                return jsonify({
                    'success': False,
                    'message': 'Database backup is only supported for SQLite databases'
                }), 400
            
            # Construct full path
            backup_path = backup_manager.backup_dir / backup_filename
            
            success, message = backup_manager.delete_backup(str(backup_path))
            
            if success:
                logger.info(f"Backup deleted by {current_user.name}", extra={
                    'user_id': current_user.id,
                    'backup_filename': backup_filename
                })
                
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error(f"Error deleting backup: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error deleting backup: {str(e)}'
            }), 500
    
    @app.route('/api/admin/database/backup/<path:backup_filename>/download', methods=['GET'])
    @jwt_required
    @admin_required
    def download_database_backup(backup_filename):
        """Download a specific backup file."""
        try:
            backup_manager = get_backup_manager()
            if not backup_manager:
                return jsonify({
                    'success': False,
                    'message': 'Database backup is only supported for SQLite databases'
                }), 400
            
            # Construct full path
            backup_path = backup_manager.backup_dir / backup_filename
            
            if not backup_path.exists():
                return jsonify({
                    'success': False,
                    'message': 'Backup file not found'
                }), 404
            
            # Ensure the file is in the backup directory (security check)
            if backup_manager.backup_dir not in backup_path.parents and backup_path.parent != backup_manager.backup_dir:
                return jsonify({
                    'success': False,
                    'message': 'Invalid backup path'
                }), 400
            
            logger.info(f"Backup downloaded by {current_user.name}", extra={
                'user_id': current_user.id,
                'backup_filename': backup_filename
            })
            
            return send_file(
                backup_path,
                as_attachment=True,
                download_name=backup_filename
            )
            
        except Exception as e:
            logger.error(f"Error downloading backup: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error downloading backup: {str(e)}'
            }), 500
    
    @app.route('/api/admin/database/restore', methods=['POST'])
    @jwt_required
    @admin_required
    def restore_database_backup():
        """
        Restore database from a backup file.
        
        Request body:
            {
                "backup_filename": "backup_20240101_120000.db",
                "create_backup_before_restore": true
            }
        """
        try:
            backup_manager = get_backup_manager()
            if not backup_manager:
                return jsonify({
                    'success': False,
                    'message': 'Database backup is only supported for SQLite databases'
                }), 400
            
            data = request.get_json()
            if not data or 'backup_filename' not in data:
                return jsonify({
                    'success': False,
                    'message': 'backup_filename is required'
                }), 400
            
            backup_filename = data['backup_filename']
            create_backup_before = data.get('create_backup_before_restore', True)
            
            # Construct full path
            backup_path = backup_manager.backup_dir / backup_filename
            
            success, message = backup_manager.restore_backup(
                str(backup_path),
                create_backup_before_restore=create_backup_before
            )
            
            if success:
                logger.warning(f"Database restored by {current_user.name}", extra={
                    'user_id': current_user.id,
                    'backup_filename': backup_filename,
                    'security_event': 'database_restore'
                })
                
                return jsonify({
                    'success': True,
                    'message': message
                })
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 500
                
        except Exception as e:
            logger.error(f"Error restoring backup: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error restoring backup: {str(e)}'
            }), 500
    
    @app.route('/api/admin/database/health', methods=['GET'])
    @jwt_required
    @admin_required
    def check_database_health():
        """Check database integrity and health."""
        try:
            backup_manager = get_backup_manager()
            if not backup_manager:
                return jsonify({
                    'success': False,
                    'message': 'Database health check is only supported for SQLite databases'
                }), 400
            
            is_healthy, message, details = backup_manager.check_database_integrity()
            
            return jsonify({
                'success': True,
                'healthy': is_healthy,
                'message': message,
                'details': details
            })
            
        except Exception as e:
            logger.error(f"Error checking database health: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'message': f'Error checking database health: {str(e)}'
            }), 500

