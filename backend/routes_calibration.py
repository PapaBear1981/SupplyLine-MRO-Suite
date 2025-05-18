from flask import request, jsonify, session
from models import db, Tool, User, ToolCalibration, CalibrationStandard, ToolCalibrationStandard, AuditLog, UserActivity
from datetime import datetime, timedelta
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename

# Decorator for requiring tool manager privileges
def tool_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not session.get('user_id'):
            return jsonify({'error': 'Authentication required'}), 401

        # Check if user has admin or Materials department privileges
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Tool management privileges required'}), 403

        return f(*args, **kwargs)
    return decorated_function

def register_calibration_routes(app):
    # Get all calibration records
    @app.route('/api/calibrations', methods=['GET'])
    @tool_manager_required
    def get_calibrations():
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)

            # Calculate offset
            offset = (page - 1) * limit

            # Get filter parameters
            tool_id = request.args.get('tool_id', type=int)
            status = request.args.get('status')

            # Start with base query
            query = ToolCalibration.query

            # Apply filters if provided
            if tool_id:
                query = query.filter(ToolCalibration.tool_id == tool_id)
            if status:
                query = query.filter(ToolCalibration.calibration_status == status)

            # Get total count for pagination
            total_count = query.count()

            # Get calibrations with pagination
            calibrations = query.order_by(ToolCalibration.calibration_date.desc()).offset(offset).limit(limit).all()

            return jsonify({
                'calibrations': [calibration.to_dict() for calibration in calibrations],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }), 200

        except Exception as e:
            print(f"Error getting calibrations: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Get tools due for calibration
    @app.route('/api/calibrations/due', methods=['GET'])
    @tool_manager_required
    def get_calibrations_due():
        try:
            # Get days parameter (default to 30 days)
            days = request.args.get('days', 30, type=int)

            # Calculate the date threshold
            now = datetime.utcnow()
            threshold_date = now + timedelta(days=days)

            # Find tools that require calibration and are due within the specified days
            tools = Tool.query.filter(
                Tool.requires_calibration == True,
                Tool.next_calibration_date.isnot(None),
                Tool.next_calibration_date <= threshold_date,
                Tool.next_calibration_date >= now
            ).all()

            return jsonify([tool.to_dict() for tool in tools]), 200

        except Exception as e:
            print(f"Error getting calibrations due: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Get tools overdue for calibration
    @app.route('/api/calibrations/overdue', methods=['GET'])
    @tool_manager_required
    def get_calibrations_overdue():
        try:
            # Calculate the current date
            now = datetime.utcnow()

            # Find tools that require calibration and are overdue
            tools = Tool.query.filter(
                Tool.requires_calibration == True,
                Tool.next_calibration_date.isnot(None),
                Tool.next_calibration_date < now
            ).all()

            return jsonify([tool.to_dict() for tool in tools]), 200

        except Exception as e:
            print(f"Error getting overdue calibrations: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Get calibration history for a specific tool
    @app.route('/api/tools/<int:id>/calibrations', methods=['GET'])
    @tool_manager_required
    def get_tool_calibrations(id):
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)

            # Calculate offset
            offset = (page - 1) * limit

            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get calibration history
            calibrations = ToolCalibration.query.filter_by(tool_id=id).order_by(
                ToolCalibration.calibration_date.desc()
            ).offset(offset).limit(limit).all()

            # Get total count for pagination
            total_count = ToolCalibration.query.filter_by(tool_id=id).count()

            return jsonify({
                'calibrations': [calibration.to_dict() for calibration in calibrations],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }), 200

        except Exception as e:
            print(f"Error getting tool calibration history: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Add a new calibration record for a tool
    @app.route('/api/tools/<int:id>/calibrations', methods=['POST'])
    @tool_manager_required
    def add_tool_calibration(id):
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get data from request
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['calibration_date', 'calibration_status']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Parse calibration date
            try:
                # Remove any timezone information to create naive datetime
                cal_date_str = data.get('calibration_date')
                if '+' in cal_date_str:
                    cal_date_str = cal_date_str.split('+')[0]
                if 'Z' in cal_date_str:
                    cal_date_str = cal_date_str.replace('Z', '')
                calibration_date = datetime.fromisoformat(cal_date_str)
            except ValueError as e:
                print(f"Error parsing calibration date: {str(e)}")
                return jsonify({'error': 'Invalid calibration date format'}), 400

            # Parse next calibration date if provided
            next_calibration_date = None
            if data.get('next_calibration_date'):
                try:
                    # Remove any timezone information to create naive datetime
                    next_cal_date_str = data.get('next_calibration_date')
                    if '+' in next_cal_date_str:
                        next_cal_date_str = next_cal_date_str.split('+')[0]
                    if 'Z' in next_cal_date_str:
                        next_cal_date_str = next_cal_date_str.replace('Z', '')
                    next_calibration_date = datetime.fromisoformat(next_cal_date_str)
                except ValueError as e:
                    print(f"Error parsing next calibration date: {str(e)}")
                    return jsonify({'error': 'Invalid next calibration date format'}), 400
            elif tool.calibration_frequency_days:
                # Calculate next calibration date based on frequency
                next_calibration_date = calibration_date + timedelta(days=tool.calibration_frequency_days)

            # Create calibration record
            calibration = ToolCalibration(
                tool_id=id,
                calibration_date=calibration_date,
                next_calibration_date=next_calibration_date,
                performed_by_user_id=session['user_id'],
                calibration_notes=data.get('calibration_notes', ''),
                calibration_status=data.get('calibration_status')
            )

            # Update tool calibration information
            tool.last_calibration_date = calibration_date
            tool.next_calibration_date = next_calibration_date
            tool.update_calibration_status()

            # Save calibration to database first to get its ID
            db.session.add(calibration)
            db.session.commit()

            # Add calibration standards if provided
            if data.get('standard_ids'):
                for standard_id in data.get('standard_ids'):
                    standard = CalibrationStandard.query.get(standard_id)
                    if standard:
                        calibration_standard = ToolCalibrationStandard(
                            calibration_id=calibration.id,
                            standard_id=standard_id
                        )
                        db.session.add(calibration_standard)

                # Commit the standards
                db.session.commit()

            # Create audit log
            log = AuditLog(
                action_type='tool_calibration',
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) calibrated tool {tool.tool_number} (ID: {id})'
            )
            db.session.add(log)

            # Create user activity
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='tool_calibration',
                description=f'Calibrated tool {tool.tool_number}',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'message': 'Calibration record added successfully',
                'calibration': calibration.to_dict()
            }), 201

        except Exception as e:
            print(f"Error adding calibration record: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Get all calibration standards
    @app.route('/api/calibration-standards', methods=['GET'])
    @tool_manager_required
    def get_calibration_standards():
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)

            # Calculate offset
            offset = (page - 1) * limit

            # Get filter parameters
            expired = request.args.get('expired', type=bool)
            expiring_soon = request.args.get('expiring_soon', type=bool)

            # Start with base query
            query = CalibrationStandard.query

            # Apply filters if provided
            if expired is not None:
                now = datetime.utcnow()
                if expired:
                    query = query.filter(CalibrationStandard.expiration_date < now)
                else:
                    query = query.filter(CalibrationStandard.expiration_date >= now)

            if expiring_soon is not None and expiring_soon:
                now = datetime.utcnow()
                thirty_days_later = now + timedelta(days=30)
                query = query.filter(
                    CalibrationStandard.expiration_date >= now,
                    CalibrationStandard.expiration_date <= thirty_days_later
                )

            # Get total count for pagination
            total_count = query.count()

            # Get standards with pagination
            standards = query.order_by(CalibrationStandard.name).offset(offset).limit(limit).all()

            return jsonify({
                'standards': [standard.to_dict() for standard in standards],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }), 200

        except Exception as e:
            print(f"Error getting calibration standards: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Add a new calibration standard
    @app.route('/api/calibration-standards', methods=['POST'])
    @tool_manager_required
    def add_calibration_standard():
        try:
            # Get data from request
            data = request.get_json() or {}

            # Validate required fields
            required_fields = ['name', 'standard_number', 'certification_date', 'expiration_date']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Parse dates
            try:
                # Remove any timezone information to create naive datetime
                cert_date_str = data.get('certification_date')
                if '+' in cert_date_str:
                    cert_date_str = cert_date_str.split('+')[0]
                if 'Z' in cert_date_str:
                    cert_date_str = cert_date_str.replace('Z', '')
                certification_date = datetime.fromisoformat(cert_date_str)

                # Remove any timezone information to create naive datetime
                exp_date_str = data.get('expiration_date')
                if '+' in exp_date_str:
                    exp_date_str = exp_date_str.split('+')[0]
                if 'Z' in exp_date_str:
                    exp_date_str = exp_date_str.replace('Z', '')
                expiration_date = datetime.fromisoformat(exp_date_str)
            except ValueError as e:
                print(f"Error parsing dates: {str(e)}")
                return jsonify({'error': 'Invalid date format'}), 400

            # Create standard
            standard = CalibrationStandard(
                name=data.get('name'),
                description=data.get('description', ''),
                standard_number=data.get('standard_number'),
                certification_date=certification_date,
                expiration_date=expiration_date
            )

            # Save to database
            db.session.add(standard)
            db.session.commit()

            # Create audit log
            log = AuditLog(
                action_type='add_calibration_standard',
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) added calibration standard {standard.name} (ID: {standard.id})'
            )
            db.session.add(log)

            # Create user activity
            activity = UserActivity(
                user_id=session['user_id'],
                activity_type='add_calibration_standard',
                description=f'Added calibration standard {standard.name}',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'message': 'Calibration standard added successfully',
                'standard': standard.to_dict()
            }), 201

        except Exception as e:
            print(f"Error adding calibration standard: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Get a specific calibration record
    @app.route('/api/tools/<int:tool_id>/calibrations/<int:calibration_id>', methods=['GET'])
    @tool_manager_required
    def get_calibration_detail(tool_id, calibration_id):
        try:
            # Get the calibration record
            calibration = ToolCalibration.query.filter_by(
                tool_id=tool_id,
                id=calibration_id
            ).first_or_404()

            # Get the calibration standards used
            standards = []
            for cs in calibration.calibration_standards:
                standard = CalibrationStandard.query.get(cs.standard_id)
                if standard:
                    standards.append(standard.to_dict())

            # Create response with standards included
            calibration_data = calibration.to_dict()
            calibration_data['standards'] = standards

            return jsonify(calibration_data), 200

        except Exception as e:
            print(f"Error getting calibration details: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Get a specific calibration standard
    @app.route('/api/calibration-standards/<int:id>', methods=['GET'])
    @tool_manager_required
    def get_calibration_standard(id):
        try:
            standard = CalibrationStandard.query.get_or_404(id)
            return jsonify(standard.to_dict()), 200

        except Exception as e:
            print(f"Error getting calibration standard: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # Update a calibration standard
    @app.route('/api/calibration-standards/<int:id>', methods=['PUT'])
    @tool_manager_required
    def update_calibration_standard(id):
        try:
            standard = CalibrationStandard.query.get_or_404(id)

            # Get data from request
            data = request.get_json() or {}

            # Update fields
            if 'name' in data:
                standard.name = data['name']
            if 'description' in data:
                standard.description = data['description']
            if 'standard_number' in data:
                standard.standard_number = data['standard_number']

            # Parse dates if provided
            if 'certification_date' in data:
                try:
                    # Remove any timezone information to create naive datetime
                    cert_date_str = data['certification_date']
                    if '+' in cert_date_str:
                        cert_date_str = cert_date_str.split('+')[0]
                    if 'Z' in cert_date_str:
                        cert_date_str = cert_date_str.replace('Z', '')
                    standard.certification_date = datetime.fromisoformat(cert_date_str)
                except ValueError as e:
                    print(f"Error parsing certification date: {str(e)}")
                    return jsonify({'error': 'Invalid certification date format'}), 400

            if 'expiration_date' in data:
                try:
                    # Remove any timezone information to create naive datetime
                    exp_date_str = data['expiration_date']
                    if '+' in exp_date_str:
                        exp_date_str = exp_date_str.split('+')[0]
                    if 'Z' in exp_date_str:
                        exp_date_str = exp_date_str.replace('Z', '')
                    standard.expiration_date = datetime.fromisoformat(exp_date_str)
                except ValueError as e:
                    print(f"Error parsing expiration date: {str(e)}")
                    return jsonify({'error': 'Invalid expiration date format'}), 400

            # Save changes
            db.session.commit()

            # Create audit log
            log = AuditLog(
                action_type='update_calibration_standard',
                action_details=f'User {session.get("name", "Unknown")} (ID: {session["user_id"]}) updated calibration standard {standard.name} (ID: {id})'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                'message': 'Calibration standard updated successfully',
                'standard': standard.to_dict()
            }), 200

        except Exception as e:
            print(f"Error updating calibration standard: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500