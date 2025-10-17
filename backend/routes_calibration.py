from flask import request, jsonify, current_app, send_from_directory
from models import db, Tool, ToolCalibration, CalibrationStandard, ToolCalibrationStandard, AuditLog, UserActivity
from datetime import datetime, timedelta
import os
from utils.error_handler import handle_errors, ValidationError
from utils.file_validation import FileValidationError, validate_certificate_upload
from utils.validation import validate_schema
from auth import department_required
import logging

logger = logging.getLogger(__name__)

tool_manager_required = department_required('Materials')


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
            # Use the calibration_status field to ensure consistency across the application
            tools = Tool.query.filter(
                Tool.requires_calibration is True,
                Tool.next_calibration_date.isnot(None),
                Tool.calibration_status == 'due_soon' if days == 30 else
                    ((Tool.next_calibration_date <= threshold_date) & (Tool.next_calibration_date >= now))
            ).all()

            # Log the query results for debugging
            logger.info(f"Found {len(tools)} tools due for calibration in the next {days} days", extra={
                'operation': 'get_calibrations_due',
                'days_ahead': days,
                'tools_found': len(tools),
                'tool_ids': [tool.id for tool in tools]
            })

            for tool in tools:
                logger.debug("Tool due for calibration", extra={
                    'tool_id': tool.id,
                    'tool_number': tool.tool_number,
                    'next_calibration_date': tool.next_calibration_date.isoformat() if tool.next_calibration_date else None,
                    'calibration_status': tool.calibration_status
                })

            return jsonify([tool.to_dict() for tool in tools]), 200

        except Exception as e:
            logger.error("Error getting calibrations due", exc_info=True, extra={
                'operation': 'get_calibrations_due',
                'days_ahead': days,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
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
                Tool.requires_calibration is True,
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
            Tool.query.get_or_404(id)

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
    @handle_errors
    def add_tool_calibration(id):
        # Get the tool
        tool = Tool.query.get_or_404(id)

        # Get and validate data from request
        data = request.get_json() or {}

        # Validate using calibration schema
        validated_data = validate_schema(data, 'calibration')

        logger.info(f"Adding calibration record for tool {tool.tool_number}")

        # Validate that calibration status is valid
        if validated_data['calibration_status'] not in ['pass', 'fail', 'limited']:
            raise ValidationError('Calibration status must be pass, fail, or limited')

        # Get calibration dates (already validated by schema)
        calibration_date = validated_data['calibration_date']
        next_calibration_date = validated_data.get('next_calibration_date')

        # Calculate next calibration date if not provided but tool has frequency
        if not next_calibration_date and tool.calibration_frequency_days:
            next_calibration_date = calibration_date + timedelta(days=tool.calibration_frequency_days)

        # Create calibration record
        calibration = ToolCalibration(
            tool_id=id,
            calibration_date=calibration_date,
            next_calibration_date=next_calibration_date,
            performed_by_user_id=request.current_user['user_id'],
            calibration_notes=validated_data.get('notes', ''),
            calibration_status=validated_data['calibration_status']
        )

        # IMPORTANT: The sequence of operations below is critical for database integrity

        # Step 1: Update tool calibration information
        tool.last_calibration_date = calibration_date
        tool.next_calibration_date = next_calibration_date
        tool.update_calibration_status()

        # Step 2: Add calibration to session and flush to get its ID
        # This ensures the calibration record gets an ID without committing
        db.session.add(calibration)
        db.session.flush()  # Flush to get the ID without committing

        # Step 3: Add calibration standards if provided
        # Now that we have a valid calibration.id, we can link standards to it
        if data.get('standard_ids'):
            for standard_id in data.get('standard_ids'):
                standard = CalibrationStandard.query.get(standard_id)
                if standard:
                    calibration_standard = ToolCalibrationStandard(
                        calibration_id=calibration.id,  # This ID is now available because we flushed above
                        standard_id=standard_id
                    )
                    db.session.add(calibration_standard)

        # Create audit log
        log = AuditLog(
            action_type='tool_calibration',
            action_details=f'User {request.current_user.get("user_name", "Unknown")} (ID: {request.current_user["user_id"]}) calibrated tool {tool.tool_number} (ID: {id})'
        )
        db.session.add(log)

        # Create user activity
        activity = UserActivity(
            user_id=request.current_user['user_id'],
            activity_type='tool_calibration',
            description=f'Calibrated tool {tool.tool_number}',
            ip_address=request.remote_addr
        )
        db.session.add(activity)

        # Single commit for all operations to ensure atomicity
        db.session.commit()

        logger.info(f"Calibration record added successfully for tool {tool.tool_number}")

        return jsonify({
            'message': 'Calibration record added successfully',
            'calibration': calibration.to_dict()
        }), 201

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
                action_details=f'User {request.current_user.get("user_name", "Unknown")} (ID: {request.current_user["user_id"]}) added calibration standard {standard.name} (ID: {standard.id})'
            )
            db.session.add(log)

            # Create user activity
            activity = UserActivity(
                user_id=request.current_user['user_id'],
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
                action_details=f'User {request.current_user.get("user_name", "Unknown")} (ID: {request.current_user["user_id"]}) updated calibration standard {standard.name} (ID: {id})'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                'message': 'Calibration standard updated successfully',
                'standard': standard.to_dict()
            }), 200

        except Exception as e:
            logger.error("Error updating calibration standard", exc_info=True, extra={
                'operation': 'update_calibration_standard',
                'standard_id': id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    @app.route('/api/calibrations/<int:calibration_id>/certificate', methods=['POST'])
    @tool_manager_required
    def upload_calibration_certificate(calibration_id):
        try:
            calibration = ToolCalibration.query.get_or_404(calibration_id)

            if 'certificate' not in request.files:
                return jsonify({'error': 'No certificate uploaded'}), 400

            file = request.files['certificate']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            try:
                max_size = current_app.config.get('MAX_CALIBRATION_CERTIFICATE_FILE_SIZE')
                safe_filename = validate_certificate_upload(file, max_size=max_size)
            except FileValidationError as exc:
                return jsonify({'error': str(exc)}), getattr(exc, 'status_code', 400)

            upload_dir = current_app.config.get('CALIBRATION_CERTIFICATE_FOLDER')
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, safe_filename)
            file.save(file_path)

            # Remove existing certificate if present
            if calibration.calibration_certificate_file:
                old_path = os.path.join(upload_dir, calibration.calibration_certificate_file)
                if os.path.exists(old_path) and old_path != file_path:
                    try:
                        os.remove(old_path)
                    except OSError as remove_error:
                        logger.warning(
                            "Failed to remove old calibration certificate",
                            extra={
                                'calibration_id': calibration_id,
                                'path': old_path,
                                'error': str(remove_error)
                            }
                        )

            calibration.calibration_certificate_file = safe_filename

            user_info = getattr(request, 'current_user', {}) or {}
            log = AuditLog(
                action_type='upload_calibration_certificate',
                action_details=(
                    f"User {user_info.get('user_name', 'Unknown')} (ID: {user_info.get('user_id')}) "
                    f"uploaded certificate for calibration {calibration_id}"
                )
            )
            db.session.add(log)

            activity = UserActivity(
                user_id=user_info.get('user_id'),
                activity_type='upload_calibration_certificate',
                description=f'Uploaded calibration certificate for calibration {calibration_id}',
                ip_address=request.remote_addr
            )
            db.session.add(activity)

            db.session.commit()

            return jsonify({
                'message': 'Calibration certificate uploaded successfully',
                'certificate': safe_filename
            }), 201

        except FileValidationError as exc:
            return jsonify({'error': str(exc)}), getattr(exc, 'status_code', 400)
        except Exception as e:
            logger.error("Error uploading calibration certificate", exc_info=True, extra={
                'operation': 'upload_calibration_certificate',
                'calibration_id': calibration_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            return jsonify({'error': 'Failed to upload calibration certificate'}), 500

    @app.route('/api/calibrations/<int:calibration_id>/certificate', methods=['GET'])
    @tool_manager_required
    def get_calibration_certificate(calibration_id):
        try:
            calibration = ToolCalibration.query.get_or_404(calibration_id)
            if not calibration.calibration_certificate_file:
                return jsonify({'error': 'No certificate available for this calibration'}), 404

            upload_dir = current_app.config.get('CALIBRATION_CERTIFICATE_FOLDER')
            file_path = os.path.join(upload_dir, calibration.calibration_certificate_file)
            if not os.path.exists(file_path):
                return jsonify({'error': 'Certificate file is missing'}), 404

            return send_from_directory(
                upload_dir,
                calibration.calibration_certificate_file,
                as_attachment=True,
                download_name=calibration.calibration_certificate_file
            )

        except Exception as e:
            logger.error("Error retrieving calibration certificate", exc_info=True, extra={
                'operation': 'get_calibration_certificate',
                'calibration_id': calibration_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            return jsonify({'error': 'Failed to retrieve calibration certificate'}), 500
