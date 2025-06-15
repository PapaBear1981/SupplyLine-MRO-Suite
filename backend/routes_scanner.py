from flask import request, jsonify
from backend.models import db, Tool, Chemical
from datetime import datetime

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
            
            # Create barcode data
            barcode_data = f"{tool.tool_number}-{tool.serial_number}"
            
            # Create QR code data (JSON)
            qr_data = {
                'id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'description': tool.description,
                'category': tool.category,
                'location': tool.location,
                'status': tool.status
            }
            
            return jsonify({
                'tool_id': tool.id,
                'tool_number': tool.tool_number,
                'serial_number': tool.serial_number,
                'barcode_data': barcode_data,
                'qr_data': qr_data
            })
        except Exception as e:
            print(f"Error in tool barcode route: {str(e)}")
            return jsonify({'error': 'An error occurred while generating barcode data'}), 500
