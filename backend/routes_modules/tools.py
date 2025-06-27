"""
Tool Management Routes for SupplyLine MRO Suite

This module provides endpoints for:
- Tool CRUD operations (Create, Read, Update, Delete)
- Tool search and filtering
- Tool checkout history and management
- Tool service records and maintenance
- Tool retirement and status management
"""

import logging
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, session
from models import db, Tool, User, Checkout, AuditLog, UserActivity, ToolServiceRecord
from models import ToolCalibration, ToolCalibrationStandard
from auth import login_required, admin_required, tool_manager_required
from sqlalchemy import func, extract
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)


def register_tool_routes(app):
    """Register tool management routes"""

    @app.route('/api/tools', methods=['GET', 'POST'])
    def tools_route():
        """Main tools endpoint for listing and creating tools"""
        # GET - List all tools
        if request.method == 'GET':
            print("Received request for all tools")

            # Check if there's a search query
            print(f"Request method: {request.method}")
            print(f"Request URL: {request.url}")
            print(f"Request args: {request.args}")
            print(f"Request args type: {type(request.args)}")
            print(f"Request args keys: {list(request.args.keys())}")

            search_query = request.args.get('q')
            print(f"Search query: {search_query}")
            print(f"Search query type: {type(search_query)}")

            if search_query:
                print(f"Searching for tools with query: {search_query}")
                search_term = f'%{search_query.lower()}%'
                print(f"Search term: {search_term}")

                try:
                    tools = Tool.query.filter(
                        db.or_(
                            db.func.lower(Tool.tool_number).like(search_term),
                            db.func.lower(Tool.serial_number).like(search_term),
                            db.func.lower(Tool.description).like(search_term),
                            db.func.lower(Tool.location).like(search_term)
                        )
                    ).all()
                    print(f"Found {len(tools)} tools matching search query")
                except Exception as e:
                    print(f"Error during search: {str(e)}")
                    tools = Tool.query.all()
                    print(f"Falling back to all tools: {len(tools)}")
            else:
                tools = Tool.query.all()
                print(f"Found {len(tools)} tools")

            # Get checkout status for each tool
            tool_status = {}
            active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()
            print(f"Found {len(active_checkouts)} active checkouts")

            for checkout in active_checkouts:
                tool_status[checkout.tool_id] = 'checked_out'
                print(f"Tool {checkout.tool_id} is checked out")

            result = [{
                'id': t.id,
                'tool_number': t.tool_number,
                'serial_number': t.serial_number,
                'description': t.description,
                'condition': t.condition,
                'location': t.location,
                'category': getattr(t, 'category', 'General'),  # Use 'General' if category attribute doesn't exist
                'status': tool_status.get(t.id, getattr(t, 'status', 'available')),  # Use 'available' if status attribute doesn't exist
                'status_reason': getattr(t, 'status_reason', None) if getattr(t, 'status', 'available') in ['maintenance', 'retired'] else None,
                'created_at': t.created_at.isoformat(),
                'requires_calibration': getattr(t, 'requires_calibration', False),
                'calibration_frequency_days': getattr(t, 'calibration_frequency_days', None),
                'last_calibration_date': t.last_calibration_date.isoformat() if hasattr(t, 'last_calibration_date') and t.last_calibration_date else None,
                'next_calibration_date': t.next_calibration_date.isoformat() if hasattr(t, 'next_calibration_date') and t.next_calibration_date else None,
                'calibration_status': getattr(t, 'calibration_status', 'not_applicable')
            } for t in tools]

            print(f"Returning {len(result)} tools")
            return jsonify(result)

        # POST - Create new tool (requires tool manager privileges)
        if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
            return jsonify({'error': 'Tool management privileges required'}), 403

        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['tool_number', 'serial_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if tool with same tool number AND serial number already exists
        if Tool.query.filter_by(tool_number=data['tool_number'], serial_number=data['serial_number']).first():
            return jsonify({'error': 'A tool with this tool number and serial number combination already exists'}), 400

        # Create new tool
        t = Tool(
            tool_number=data.get('tool_number'),
            serial_number=data.get('serial_number'),
            description=data.get('description'),
            condition=data.get('condition'),
            location=data.get('location'),
            category=data.get('category', 'General'),
            requires_calibration=data.get('requires_calibration', False),
            calibration_frequency_days=data.get('calibration_frequency_days')
        )

        # Set calibration status based on requires_calibration
        if t.requires_calibration:
            t.calibration_status = 'due_soon'  # Default to due_soon until first calibration
        else:
            t.calibration_status = 'not_applicable'
        db.session.add(t)
        db.session.commit()

        # Log the action
        log = AuditLog(
            action_type='create_tool',
            action_details=f'Created tool {t.id} ({t.tool_number})'
        )
        db.session.add(log)
        db.session.commit()

        # Return the complete tool object for the frontend
        return jsonify({
            'id': t.id,
            'tool_number': t.tool_number,
            'serial_number': t.serial_number,
            'description': t.description,
            'condition': t.condition,
            'location': t.location,
            'category': t.category,
            'status': getattr(t, 'status', 'available'),
            'status_reason': getattr(t, 'status_reason', None),
            'created_at': t.created_at.isoformat(),
            'requires_calibration': getattr(t, 'requires_calibration', False),
            'calibration_frequency_days': getattr(t, 'calibration_frequency_days', None),
            'last_calibration_date': t.last_calibration_date.isoformat() if hasattr(t, 'last_calibration_date') and t.last_calibration_date else None,
            'next_calibration_date': t.next_calibration_date.isoformat() if hasattr(t, 'next_calibration_date') and t.next_calibration_date else None,
            'calibration_status': getattr(t, 'calibration_status', 'not_applicable'),
            'message': 'Tool created successfully'
        }), 201

    @app.route('/api/tools/search', methods=['GET'])
    def search_tools():
        """Search tools by various criteria"""
        # Get search query from request parameters
        query = request.args.get('q', '')
        print(f"Search endpoint called with query: {query}")

        if not query:
            print("No search query provided")
            return jsonify([])

        # Search in multiple fields
        search_term = f'%{query.lower()}%'
        print(f"Searching for: {search_term}")

        try:
            tools = Tool.query.filter(
                db.or_(
                    db.func.lower(Tool.tool_number).like(search_term),
                    db.func.lower(Tool.serial_number).like(search_term),
                    db.func.lower(Tool.description).like(search_term),
                    db.func.lower(Tool.location).like(search_term),
                    db.func.lower(Tool.category).like(search_term)
                )
            ).all()

            print(f"Found {len(tools)} tools matching search")

            # Get checkout status for each tool
            tool_status = {}
            active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()
            for checkout in active_checkouts:
                tool_status[checkout.tool_id] = 'checked_out'

            result = [{
                'id': t.id,
                'tool_number': t.tool_number,
                'serial_number': t.serial_number,
                'description': t.description,
                'condition': t.condition,
                'location': t.location,
                'category': getattr(t, 'category', 'General'),
                'status': tool_status.get(t.id, getattr(t, 'status', 'available')),
                'status_reason': getattr(t, 'status_reason', None) if getattr(t, 'status', 'available') in ['maintenance', 'retired'] else None,
                'created_at': t.created_at.isoformat(),
                'requires_calibration': getattr(t, 'requires_calibration', False),
                'calibration_frequency_days': getattr(t, 'calibration_frequency_days', None),
                'last_calibration_date': t.last_calibration_date.isoformat() if hasattr(t, 'last_calibration_date') and t.last_calibration_date else None,
                'next_calibration_date': t.next_calibration_date.isoformat() if hasattr(t, 'next_calibration_date') and t.next_calibration_date else None,
                'calibration_status': getattr(t, 'calibration_status', 'not_applicable')
            } for t in tools]

            print(f"Returning {len(result)} search results")
            return jsonify(result)

        except Exception as e:
            print(f"Error during tool search: {str(e)}")
            return jsonify({'error': 'An error occurred during search'}), 500

    @app.route('/api/tools/new', methods=['GET'])
    @tool_manager_required
    def get_new_tool_form():
        """Get form data for creating a new tool"""
        # This endpoint returns the form data needed to create a new tool
        # It can include any default values or validation rules
        return jsonify({
            'form_fields': [
                {'name': 'tool_number', 'type': 'text', 'required': True, 'label': 'Tool Number'},
                {'name': 'serial_number', 'type': 'text', 'required': True, 'label': 'Serial Number'},
                {'name': 'description', 'type': 'text', 'required': False, 'label': 'Description'},
                {'name': 'condition', 'type': 'select', 'required': False, 'label': 'Condition',
                 'options': ['New', 'Good', 'Fair', 'Poor']},
                {'name': 'location', 'type': 'text', 'required': False, 'label': 'Location'}
            ]
        }), 200

    @app.route('/api/tools/new/checkouts', methods=['GET'])
    @login_required
    def get_new_tool_checkouts():
        """Get checkout history for a new tool (should be empty)"""
        # This endpoint returns checkout history for a new tool (which should be empty)
        return jsonify([]), 200

    @app.route('/api/tools/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def get_tool(id):
        """Individual tool management endpoint"""
        tool = Tool.query.get_or_404(id)

        # GET - Get tool details
        if request.method == 'GET':
            # Check if tool is currently checked out
            active_checkout = Checkout.query.filter_by(tool_id=id, return_date=None).first()

            # Determine status - checkout status takes precedence over tool status
            status = 'checked_out' if active_checkout else getattr(tool, 'status', 'available')

            # Debug tool attributes
            print(f"Tool ID: {tool.id}")
            print(f"Tool Number: {tool.tool_number}")
            print(f"Tool Serial Number: {tool.serial_number}")
            print(f"Tool Description: {tool.description}")
            print(f"Tool Condition: {tool.condition}")
            print(f"Tool Location: {tool.location}")
            print(f"Tool Category: {getattr(tool, 'category', 'General')}")
            print(f"Tool Status: {status}")

            # Check if category attribute exists
            has_category = hasattr(tool, 'category')
            print(f"Tool has category attribute: {has_category}")

            # Get category value directly
            category_value = tool.category if has_category else 'General'
            print(f"Tool category value: {category_value}")

            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'description': tool.description,
                'condition': tool.condition,
                'location': tool.location,
                'category': category_value,  # Use actual category value
                'status': status,
                'status_reason': getattr(tool, 'status_reason', None) if status in ['maintenance', 'retired'] else None,
                'created_at': tool.created_at.isoformat(),
                'requires_calibration': getattr(tool, 'requires_calibration', False),
                'calibration_frequency_days': getattr(tool, 'calibration_frequency_days', None),
                'last_calibration_date': tool.last_calibration_date.isoformat() if hasattr(tool, 'last_calibration_date') and tool.last_calibration_date else None,
                'next_calibration_date': tool.next_calibration_date.isoformat() if hasattr(tool, 'next_calibration_date') and tool.next_calibration_date else None,
                'calibration_status': getattr(tool, 'calibration_status', 'not_applicable')
            })

        elif request.method == 'DELETE':
            # DELETE - Delete tool (requires admin privileges)
            if not session.get('is_admin', False):
                return jsonify({'error': 'Admin privileges required to delete tools'}), 403

            # Accept force_delete from query parameters or JSON body
            force_delete = (
                request.args.get('force_delete', '').lower() in ('1', 'true')
                or (request.get_json(silent=True) or {}).get('force_delete', False)
            )

            # Check if tool has history (checkouts, calibrations, service records)
            has_checkouts = Checkout.query.filter_by(tool_id=id).count() > 0
            has_calibrations = ToolCalibration.query.filter_by(tool_id=id).count() > 0
            has_service_records = ToolServiceRecord.query.filter_by(tool_id=id).count() > 0

            if (has_checkouts or has_calibrations or has_service_records) and not force_delete:
                return jsonify({
                    'error': 'Tool has history and cannot be deleted',
                    'has_history': True,
                    'has_checkouts': has_checkouts,
                    'has_calibrations': has_calibrations,
                    'has_service_records': has_service_records,
                    'suggestion': 'Consider retiring the tool instead to preserve history'
                }), 400

            # Store tool details for audit log before deletion
            tool_number = tool.tool_number
            tool_description = tool.description

            try:
                # Delete related records if force_delete is True
                if force_delete:
                    # Delete calibration standards associations first
                    ToolCalibrationStandard.query.filter(
                        ToolCalibrationStandard.calibration_id.in_(
                            db.session.query(ToolCalibration.id).filter_by(tool_id=id)
                        )
                    ).delete(synchronize_session=False)

                    # Delete calibrations
                    ToolCalibration.query.filter_by(tool_id=id).delete()

                    # Delete checkouts
                    Checkout.query.filter_by(tool_id=id).delete()

                    # Delete service records
                    ToolServiceRecord.query.filter_by(tool_id=id).delete()

                # Delete the tool
                db.session.delete(tool)
                db.session.commit()

                # Log the action
                log = AuditLog(
                    action_type='delete_tool',
                    action_details=f'Deleted tool {id} ({tool_number}) - {tool_description}. Force delete: {force_delete}'
                )
                db.session.add(log)
                db.session.commit()

                return jsonify({'message': 'Tool deleted successfully'}), 200

            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Failed to delete tool: {str(e)}'}), 500

        # PUT - Update tool (requires tool manager privileges)
        print(f"Session: {session}")
        print(f"Session is_admin: {session.get('is_admin', False)}")
        print(f"Session department: {session.get('department', 'None')}")

        # Temporarily disable permission check for debugging
        # if not (session.get('is_admin', False) or session.get('department') == 'Materials'):
        #     return jsonify({'error': 'Tool management privileges required'}), 403

        data = request.get_json() or {}
        print(f"Received tool update request for tool ID {id} with data: {data}")
        print(f"Tool before update: {tool.__dict__}")

        # Debug request
        print(f"Request content type: {request.content_type}")
        print(f"Request headers: {request.headers}")
        print(f"Request data: {request.data}")

        # Check if category is in the data
        if 'category' in data:
            print(f"Category in data: {data['category']}")
        else:
            print("Category not in data")

        # Update fields
        if 'tool_number' in data or 'serial_number' in data:
            # If either tool_number or serial_number is being updated, we need to check for duplicates
            new_tool_number = data.get('tool_number', tool.tool_number)
            new_serial_number = data.get('serial_number', tool.serial_number)

            # Check if the combination of tool_number and serial_number already exists for another tool
            existing_tool = Tool.query.filter_by(tool_number=new_tool_number, serial_number=new_serial_number).first()
            if existing_tool and existing_tool.id != id:
                return jsonify({'error': 'A tool with this tool number and serial number combination already exists'}), 400

            # Update the fields if they were provided
            if 'tool_number' in data:
                tool.tool_number = data['tool_number']
                print(f"Updated tool_number to: {tool.tool_number}")
            if 'serial_number' in data:
                tool.serial_number = data['serial_number']
                print(f"Updated serial_number to: {tool.serial_number}")

        if 'description' in data:
            tool.description = data['description']
            print(f"Updated description to: {tool.description}")

        if 'condition' in data:
            tool.condition = data['condition']
            print(f"Updated condition to: {tool.condition}")

        if 'location' in data:
            tool.location = data['location']
            print(f"Updated location to: {tool.location}")

        if 'category' in data:
            old_category = tool.category
            tool.category = data['category']
            print(f"Updated tool category from {old_category} to: {tool.category}")

        # Update calibration fields
        if 'requires_calibration' in data:
            tool.requires_calibration = data['requires_calibration']
            print(f"Updated requires_calibration to: {tool.requires_calibration}")

            # If requires_calibration is being turned off, reset calibration status
            if not tool.requires_calibration:
                tool.calibration_status = 'not_applicable'
                print(f"Reset calibration_status to: {tool.calibration_status}")
            # If requires_calibration is being turned on, set initial calibration status
            elif tool.requires_calibration and not tool.calibration_status:
                tool.calibration_status = 'due_soon'
                print(f"Set initial calibration_status to: {tool.calibration_status}")

        if 'calibration_frequency_days' in data:
            tool.calibration_frequency_days = data['calibration_frequency_days']
            print(f"Updated calibration_frequency_days to: {tool.calibration_frequency_days}")

            # If we have a last calibration date and frequency, update the next calibration date
            if tool.last_calibration_date and tool.calibration_frequency_days:
                tool.next_calibration_date = tool.last_calibration_date + timedelta(days=tool.calibration_frequency_days)
                print(f"Updated next_calibration_date to: {tool.next_calibration_date}")

                # Update calibration status based on new next_calibration_date
                if hasattr(tool, 'update_calibration_status'):
                    tool.update_calibration_status()
                    print(f"Updated calibration_status to: {tool.calibration_status}")

        # Save changes
        try:
            db.session.commit()
            print("Tool update committed successfully")

            # Log the action
            log = AuditLog(
                action_type='update_tool',
                action_details=f'Updated tool {tool.id} ({tool.tool_number})'
            )
            db.session.add(log)
            db.session.commit()

            # Return updated tool data
            return jsonify({
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'description': tool.description,
                'condition': tool.condition,
                'location': tool.location,
                'category': tool.category,
                'status': getattr(tool, 'status', 'available'),
                'status_reason': getattr(tool, 'status_reason', None),
                'created_at': tool.created_at.isoformat(),
                'requires_calibration': getattr(tool, 'requires_calibration', False),
                'calibration_frequency_days': getattr(tool, 'calibration_frequency_days', None),
                'last_calibration_date': tool.last_calibration_date.isoformat() if hasattr(tool, 'last_calibration_date') and tool.last_calibration_date else None,
                'next_calibration_date': tool.next_calibration_date.isoformat() if hasattr(tool, 'next_calibration_date') and tool.next_calibration_date else None,
                'calibration_status': getattr(tool, 'calibration_status', 'not_applicable'),
                'message': 'Tool updated successfully'
            })

        except Exception as e:
            db.session.rollback()
            print(f"Error updating tool: {str(e)}")
            return jsonify({'error': f'Failed to update tool: {str(e)}'}), 500

    @app.route('/api/tools/<int:id>/retire', methods=['POST'])
    @admin_required
    def retire_tool(id):
        """Retire a tool instead of deleting it to preserve history."""
        tool = Tool.query.get_or_404(id)

        # Get retirement reason from request
        data = request.get_json() or {}
        retirement_reason = data.get('reason', 'Retired by administrator')

        # Update tool status
        tool.status = 'retired'
        tool.status_reason = retirement_reason

        try:
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='retire_tool',
                action_details=f'Retired tool {tool.id} ({tool.tool_number}). Reason: {retirement_reason}'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                'message': 'Tool retired successfully',
                'tool_id': tool.id,
                'status': tool.status,
                'status_reason': tool.status_reason
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to retire tool: {str(e)}'}), 500

    @app.route('/api/tools/<int:id>/checkouts', methods=['GET'])
    def get_tool_checkouts(id):
        """Get checkout history for a specific tool"""
        # Get checkout history for a specific tool
        tool = Tool.query.get_or_404(id)
        checkouts = Checkout.query.filter_by(tool_id=id).order_by(Checkout.checkout_date.desc()).all()

        return jsonify([{
            'id': checkout.id,
            'user_id': checkout.user_id,
            'user_name': checkout.user.name if checkout.user else 'Unknown',
            'checkout_date': checkout.checkout_date.isoformat(),
            'return_date': checkout.return_date.isoformat() if checkout.return_date else None,
            'purpose': checkout.purpose,
            'notes': checkout.notes,
            'status': 'returned' if checkout.return_date else 'active'
        } for checkout in checkouts])

    @app.route('/api/audit/tools/<int:tool_id>', methods=['GET'])
    def tool_audit_logs_route(tool_id):
        """Get audit logs for a specific tool"""
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Calculate offset
        offset = (page - 1) * limit

        # Get audit logs for the specific tool
        logs = AuditLog.query.filter(
            AuditLog.action_details.like(f'%tool {tool_id}%')
        ).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

        # Get total count for pagination
        total_count = AuditLog.query.filter(
            AuditLog.action_details.like(f'%tool {tool_id}%')
        ).count()

        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        })

    @app.route('/api/tools/<int:id>/service/remove', methods=['POST'])
    @tool_manager_required
    def remove_tool_from_service(id):
        """Remove a tool from service for maintenance"""
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get the reason from request data
            data = request.get_json() or {}
            reason = data.get('reason', 'Removed from service for maintenance')

            # Update tool status
            tool.status = 'maintenance'
            tool.status_reason = reason

            # Create service record
            service_record = ToolServiceRecord(
                tool_id=id,
                service_type='maintenance',
                description=f'Tool removed from service: {reason}',
                service_date=datetime.now(),
                performed_by=session.get('user_id'),
                status='in_progress'
            )

            db.session.add(service_record)
            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='remove_tool_from_service',
                action_details=f'Removed tool {tool.id} ({tool.tool_number}) from service. Reason: {reason}'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                'message': 'Tool removed from service successfully',
                'tool_id': tool.id,
                'status': tool.status,
                'status_reason': tool.status_reason,
                'service_record_id': service_record.id
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing tool from service: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    @app.route('/api/tools/<int:id>/service/return', methods=['POST'])
    @tool_manager_required
    def return_tool_to_service(id):
        """Return a tool to service after maintenance"""
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get the completion notes from request data
            data = request.get_json() or {}
            completion_notes = data.get('notes', 'Tool returned to service')

            # Update tool status
            tool.status = 'available'
            tool.status_reason = None

            # Find the most recent in-progress service record
            service_record = ToolServiceRecord.query.filter_by(
                tool_id=id,
                status='in_progress'
            ).order_by(ToolServiceRecord.service_date.desc()).first()

            if service_record:
                service_record.status = 'completed'
                service_record.completion_date = datetime.now()
                service_record.completion_notes = completion_notes

            db.session.commit()

            # Log the action
            log = AuditLog(
                action_type='return_tool_to_service',
                action_details=f'Returned tool {tool.id} ({tool.tool_number}) to service. Notes: {completion_notes}'
            )
            db.session.add(log)
            db.session.commit()

            return jsonify({
                'message': 'Tool returned to service successfully',
                'tool_id': tool.id,
                'status': tool.status,
                'service_record_id': service_record.id if service_record else None
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error returning tool to service: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    @app.route('/api/tools/<int:id>/service/history', methods=['GET'])
    def get_tool_service_history(id):
        """Get service history for a specific tool"""
        try:
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)

            # Calculate offset
            offset = (page - 1) * limit

            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get service history
            service_records = ToolServiceRecord.query.filter_by(tool_id=id).order_by(
                ToolServiceRecord.service_date.desc()
            ).offset(offset).limit(limit).all()

            # Get total count for pagination
            total_count = ToolServiceRecord.query.filter_by(tool_id=id).count()

            # Format service records
            formatted_records = []
            for record in service_records:
                formatted_record = {
                    'id': record.id,
                    'service_type': record.service_type,
                    'description': record.description,
                    'service_date': record.service_date.isoformat(),
                    'completion_date': record.completion_date.isoformat() if record.completion_date else None,
                    'performed_by': record.performed_by,
                    'completion_notes': record.completion_notes,
                    'status': record.status,
                    'cost': float(record.cost) if record.cost else None
                }
                formatted_records.append(formatted_record)

            return jsonify({
                'service_records': formatted_records,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                },
                'tool': {
                    'id': tool.id,
                    'tool_number': tool.tool_number,
                    'description': tool.description
                }
            }), 200

        except Exception as e:
            logger.error(f"Error getting tool service history: {str(e)}")
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
