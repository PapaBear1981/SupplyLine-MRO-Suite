from flask import request, jsonify, render_template_string, current_app
from models import db, Tool, Chemical, ToolCalibration
from datetime import datetime
import os

def register_scanner_routes(app):
    """
    Register routes for barcode/QR code scanner functionality
    """
    
    # Lookup item by barcode/QR code
    @app.route('/api/scanner/lookup', methods=['POST'])
    def scanner_lookup():
        try:
            data = request.get_json()
            
            if not data or 'code' not in data:
                return jsonify({'error': 'No code provided'}), 400
                
            code = data['code']
            
            # Parse the code to determine if it's a tool or chemical
            # Format for tools: tool_number-serial_number
            # Format for chemicals: part_number-lot_number-expiration_date
            parts = code.split('-')
            
            # Try to find a tool first
            if len(parts) >= 2:
                # Check if it's a tool
                tool = Tool.query.filter_by(
                    tool_number=parts[0],
                    serial_number=parts[1]
                ).first()
                
                if tool:
                    return jsonify({
                        'item_type': 'tool',
                        'item_id': tool.id,
                        'item_data': {
                            'id': tool.id,
                            'tool_number': tool.tool_number,
                            'serial_number': tool.serial_number,
                            'description': tool.description,
                            'category': tool.category,
                            'location': tool.location,
                            'status': tool.status
                        }
                    })
            
            # If not a tool or if tool not found, check if it's a chemical
            if len(parts) >= 3:
                # Check if it's a chemical
                chemical = Chemical.query.filter_by(
                    part_number=parts[0],
                    lot_number=parts[1]
                ).first()
                
                if chemical:
                    # If expiration date is included, verify it
                    if len(parts) >= 3 and parts[2] != 'NOEXP':
                        try:
                            # Parse expiration date from YYYYMMDD format
                            exp_date = datetime.strptime(parts[2], '%Y%m%d').date()
                            
                            # If chemical has expiration date, check if it matches
                            if chemical.expiration_date and chemical.expiration_date.date() != exp_date:
                                # Still return the chemical, but with a warning
                                return jsonify({
                                    'item_type': 'chemical',
                                    'item_id': chemical.id,
                                    'warning': 'Expiration date in barcode does not match database record',
                                    'item_data': {
                                        'id': chemical.id,
                                        'part_number': chemical.part_number,
                                        'lot_number': chemical.lot_number,
                                        'description': chemical.description,
                                        'manufacturer': chemical.manufacturer,
                                        'status': chemical.status,
                                        'expiration_date': chemical.expiration_date.isoformat() if chemical.expiration_date else None
                                    }
                                })
                        except ValueError:
                            # Invalid date format, ignore and continue
                            pass
                    
                    # Return chemical data
                    return jsonify({
                        'item_type': 'chemical',
                        'item_id': chemical.id,
                        'item_data': {
                            'id': chemical.id,
                            'part_number': chemical.part_number,
                            'lot_number': chemical.lot_number,
                            'description': chemical.description,
                            'manufacturer': chemical.manufacturer,
                            'status': chemical.status,
                            'expiration_date': chemical.expiration_date.isoformat() if chemical.expiration_date else None
                        }
                    })
            
            # If no matching item found
            return jsonify({'error': 'No matching item found for the provided code'}), 404
            
        except Exception as e:
            print(f"Error in scanner lookup: {str(e)}")
            return jsonify({'error': 'An error occurred while processing the code'}), 500
    
    # Get barcode data for a tool
    @app.route('/api/tools/<int:id>/barcode', methods=['GET'])
    def tool_barcode_route(id):
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get the latest calibration record if tool requires calibration
            latest_calibration = None
            if tool.requires_calibration:
                latest_calibration = ToolCalibration.query.filter_by(
                    tool_id=tool.id
                ).order_by(ToolCalibration.calibration_date.desc()).first()

            # Create barcode data
            barcode_data = f"{tool.tool_number}-{tool.serial_number}"

            # Get the base URL for QR code (use request host or configured URL)
            base_url = request.host_url.rstrip('/')

            # Create QR code URL that points to the tool view page
            qr_url = f"{base_url}/tool-view/{tool.id}"

            # Prepare calibration data
            calibration_data = None
            if latest_calibration:
                calibration_data = {
                    'id': latest_calibration.id,
                    'calibration_date': latest_calibration.calibration_date.isoformat() if latest_calibration.calibration_date else None,
                    'next_calibration_date': latest_calibration.next_calibration_date.isoformat() if latest_calibration.next_calibration_date else None,
                    'calibration_status': latest_calibration.calibration_status,
                    'has_certificate': latest_calibration.calibration_certificate_file is not None
                }

            return jsonify({
                'tool_id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'barcode_data': barcode_data,
                'qr_url': qr_url,
                'calibration': calibration_data,
                'requires_calibration': tool.requires_calibration,
                'last_calibration_date': tool.last_calibration_date.isoformat() if tool.last_calibration_date else None,
                'next_calibration_date': tool.next_calibration_date.isoformat() if tool.next_calibration_date else None
            })
        except Exception as e:
            print(f"Error in tool barcode route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating barcode data'}), 500

    # Public tool view page (accessible via QR code scan)
    @app.route('/tool-view/<int:id>', methods=['GET'])
    def tool_view_page(id):
        try:
            # Get the tool
            tool = Tool.query.get_or_404(id)

            # Get the latest calibration record if tool requires calibration
            latest_calibration = None
            certificate_url = None
            if tool.requires_calibration:
                latest_calibration = ToolCalibration.query.filter_by(
                    tool_id=tool.id
                ).order_by(ToolCalibration.calibration_date.desc()).first()

                # If there's a calibration certificate, create the URL
                if latest_calibration and latest_calibration.calibration_certificate_file:
                    certificate_url = f"/api/calibrations/{latest_calibration.id}/certificate"

            # Format dates for display
            def format_date(dt):
                if dt:
                    return dt.strftime('%B %d, %Y')
                return 'N/A'

            # Create HTML template for the tool view page
            html_template = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ tool.tool_number }} - Tool Information</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 20px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .container {
                        background: white;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        max-width: 600px;
                        width: 100%;
                        overflow: hidden;
                        animation: slideIn 0.5s ease-out;
                    }
                    @keyframes slideIn {
                        from {
                            opacity: 0;
                            transform: translateY(30px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    .header {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }
                    .header h1 {
                        font-size: 28px;
                        margin-bottom: 10px;
                        font-weight: 600;
                    }
                    .header p {
                        font-size: 16px;
                        opacity: 0.9;
                    }
                    .content {
                        padding: 30px;
                    }
                    .info-section {
                        margin-bottom: 25px;
                    }
                    .info-section h2 {
                        font-size: 18px;
                        color: #333;
                        margin-bottom: 15px;
                        padding-bottom: 10px;
                        border-bottom: 2px solid #667eea;
                        font-weight: 600;
                    }
                    .info-row {
                        display: flex;
                        padding: 12px 0;
                        border-bottom: 1px solid #f0f0f0;
                    }
                    .info-row:last-child {
                        border-bottom: none;
                    }
                    .info-label {
                        font-weight: 600;
                        color: #666;
                        min-width: 140px;
                        font-size: 14px;
                    }
                    .info-value {
                        color: #333;
                        flex: 1;
                        font-size: 14px;
                    }
                    .status-badge {
                        display: inline-block;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: 600;
                        text-transform: uppercase;
                    }
                    .status-available {
                        background: #d4edda;
                        color: #155724;
                    }
                    .status-checked-out {
                        background: #fff3cd;
                        color: #856404;
                    }
                    .status-maintenance {
                        background: #f8d7da;
                        color: #721c24;
                    }
                    .calibration-alert {
                        background: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 4px;
                    }
                    .calibration-alert.overdue {
                        background: #f8d7da;
                        border-left-color: #dc3545;
                    }
                    .calibration-alert.current {
                        background: #d4edda;
                        border-left-color: #28a745;
                    }
                    .certificate-button {
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 12px 24px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: 600;
                        margin-top: 15px;
                        transition: transform 0.2s, box-shadow 0.2s;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    }
                    .certificate-button:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
                    }
                    .footer {
                        background: #f8f9fa;
                        padding: 20px;
                        text-align: center;
                        color: #666;
                        font-size: 12px;
                    }
                    @media (max-width: 600px) {
                        .container {
                            border-radius: 0;
                        }
                        .info-row {
                            flex-direction: column;
                        }
                        .info-label {
                            margin-bottom: 5px;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{{ tool.tool_number }}</h1>
                        <p>{{ tool.description or 'Tool Information' }}</p>
                    </div>

                    <div class="content">
                        <div class="info-section">
                            <h2>Tool Details</h2>
                            <div class="info-row">
                                <div class="info-label">Serial Number:</div>
                                <div class="info-value">{{ tool.serial_number }}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Category:</div>
                                <div class="info-value">{{ tool.category or 'N/A' }}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Location:</div>
                                <div class="info-value">{{ tool.location or 'N/A' }}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Condition:</div>
                                <div class="info-value">{{ tool.condition or 'N/A' }}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Status:</div>
                                <div class="info-value">
                                    <span class="status-badge status-{{ tool.status }}">{{ tool.status }}</span>
                                </div>
                            </div>
                        </div>

                        {% if tool.requires_calibration %}
                        <div class="info-section">
                            <h2>Calibration Information</h2>

                            {% if latest_calibration %}
                            <div class="info-row">
                                <div class="info-label">Last Calibration:</div>
                                <div class="info-value">{{ format_date(latest_calibration.calibration_date) }}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Next Due Date:</div>
                                <div class="info-value">{{ format_date(latest_calibration.next_calibration_date) }}</div>
                            </div>
                            <div class="info-row">
                                <div class="info-label">Status:</div>
                                <div class="info-value">{{ latest_calibration.calibration_status }}</div>
                            </div>

                            {% if certificate_url %}
                            <div style="text-align: center;">
                                <a href="{{ certificate_url }}" class="certificate-button" target="_blank">
                                    📄 View Calibration Certificate
                                </a>
                            </div>
                            {% endif %}

                            {% else %}
                            <div class="calibration-alert">
                                <strong>⚠️ No Calibration Records</strong><br>
                                This tool requires calibration but has no calibration records on file.
                            </div>
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>

                    <div class="footer">
                        SupplyLine MRO Suite - Tool Management System
                    </div>
                </div>
            </body>
            </html>
            """

            return render_template_string(
                html_template,
                tool=tool,
                latest_calibration=latest_calibration,
                certificate_url=certificate_url,
                format_date=format_date
            )

        except Exception as e:
            print(f"Error in tool view page: {str(e)}")
            return f"<html><body><h1>Error</h1><p>Tool not found or an error occurred.</p></body></html>", 404
