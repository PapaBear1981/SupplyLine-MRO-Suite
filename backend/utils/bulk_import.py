"""
Bulk import utilities for tools and chemicals
"""
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from models import db, Tool, Chemical
from utils.validation import validate_schema, ValidationError
import logging

logger = logging.getLogger(__name__)

class BulkImportError(Exception):
    """Custom exception for bulk import errors"""
    pass

class BulkImportResult:
    """Container for bulk import results"""
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.errors = []
        self.warnings = []
        self.created_items = []
        self.skipped_items = []
    
    def add_success(self, item_data: Dict[str, Any], created_item: Any):
        """Add a successful import"""
        self.success_count += 1
        self.created_items.append({
            'data': item_data,
            'created': created_item.to_dict() if hasattr(created_item, 'to_dict') else str(created_item)
        })
    
    def add_error(self, row_number: int, item_data: Dict[str, Any], error: str):
        """Add an import error"""
        self.error_count += 1
        self.errors.append({
            'row': row_number,
            'data': item_data,
            'error': error
        })
    
    def add_warning(self, row_number: int, item_data: Dict[str, Any], warning: str):
        """Add an import warning"""
        self.warnings.append({
            'row': row_number,
            'data': item_data,
            'warning': warning
        })
    
    def add_skipped(self, row_number: int, item_data: Dict[str, Any], reason: str):
        """Add a skipped item"""
        self.skipped_items.append({
            'row': row_number,
            'data': item_data,
            'reason': reason
        })
    
    def to_dict(self):
        """Convert result to dictionary for JSON response"""
        return {
            'success_count': self.success_count,
            'error_count': self.error_count,
            'warning_count': len(self.warnings),
            'skipped_count': len(self.skipped_items),
            'errors': self.errors,
            'warnings': self.warnings,
            'created_items': self.created_items,
            'skipped_items': self.skipped_items
        }

def parse_csv_content(content: str, expected_headers: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Parse CSV content and validate headers
    
    Args:
        content: CSV content as string
        expected_headers: List of expected column headers
    
    Returns:
        Tuple of (parsed_rows, validation_errors)
    """
    try:
        # Use StringIO to read CSV content
        csv_file = io.StringIO(content)
        reader = csv.DictReader(csv_file)
        
        # Validate headers
        if not reader.fieldnames:
            return [], ["CSV file appears to be empty or invalid"]
        
        # Check for required headers
        missing_headers = []
        for header in expected_headers:
            if header not in reader.fieldnames:
                missing_headers.append(header)
        
        if missing_headers:
            return [], [f"Missing required headers: {', '.join(missing_headers)}"]
        
        # Parse all rows
        rows = []
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is headers
            # Clean up the row data (strip whitespace, handle empty values)
            cleaned_row = {}
            for key, value in row.items():
                if value is not None:
                    cleaned_row[key] = str(value).strip() if value else ''
                else:
                    cleaned_row[key] = ''
            
            # Add row number for error reporting
            cleaned_row['_row_number'] = row_num
            rows.append(cleaned_row)
        
        return rows, []
    
    except Exception as e:
        logger.error(f"Error parsing CSV content: {str(e)}")
        return [], [f"Error parsing CSV file: {str(e)}"]

def validate_tool_data(row_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean tool data for import
    
    Args:
        row_data: Raw row data from CSV
    
    Returns:
        Cleaned and validated tool data
    """
    # Map CSV headers to model fields
    tool_data = {
        'tool_number': row_data.get('tool_number', ''),
        'serial_number': row_data.get('serial_number', ''),
        'description': row_data.get('description', ''),
        'condition': row_data.get('condition', 'good'),
        'location': row_data.get('location', ''),
        'category': row_data.get('category', 'General'),
        'status': row_data.get('status', 'available'),
        'requires_calibration': str(row_data.get('requires_calibration', 'false')).lower() in ['true', '1', 'yes'],
        'calibration_frequency_days': None
    }
    
    # Handle calibration frequency
    if tool_data['requires_calibration']:
        freq_str = row_data.get('calibration_frequency_days', '')
        if freq_str:
            try:
                tool_data['calibration_frequency_days'] = int(freq_str)
            except ValueError:
                raise ValidationError(f"Invalid calibration frequency: {freq_str}")
    
    # Validate using existing schema
    return validate_schema(tool_data, 'tool')

def validate_chemical_data(row_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean chemical data for import
    
    Args:
        row_data: Raw row data from CSV
    
    Returns:
        Cleaned and validated chemical data
    """
    # Map CSV headers to model fields
    chemical_data = {
        'part_number': row_data.get('part_number', ''),
        'lot_number': row_data.get('lot_number', ''),
        'description': row_data.get('description', ''),
        'manufacturer': row_data.get('manufacturer', ''),
        'quantity': 0,
        'unit': row_data.get('unit', 'each'),
        'location': row_data.get('location', ''),
        'category': row_data.get('category', 'General'),
        'expiration_date': None,
        'msds_url': row_data.get('msds_url', '')
    }
    
    # Handle quantity
    quantity_str = row_data.get('quantity', '0')
    try:
        chemical_data['quantity'] = float(quantity_str) if quantity_str else 0
    except ValueError:
        raise ValidationError(f"Invalid quantity: {quantity_str}")
    
    # Handle expiration date
    exp_date_str = row_data.get('expiration_date', '')
    if exp_date_str:
        try:
            # Try multiple date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    chemical_data['expiration_date'] = datetime.strptime(exp_date_str, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValidationError(f"Invalid expiration date format: {exp_date_str}")
        except Exception:
            raise ValidationError(f"Invalid expiration date: {exp_date_str}")
    
    # Validate using existing schema
    return validate_schema(chemical_data, 'chemical')

def check_duplicate_tool(tool_data: Dict[str, Any]) -> Optional[Tool]:
    """Check if a tool with the same tool_number and serial_number already exists"""
    return Tool.query.filter_by(
        tool_number=tool_data['tool_number'],
        serial_number=tool_data['serial_number']
    ).first()

def check_duplicate_chemical(chemical_data: Dict[str, Any]) -> Optional[Chemical]:
    """Check if a chemical with the same part_number and lot_number already exists"""
    return Chemical.query.filter_by(
        part_number=chemical_data['part_number'],
        lot_number=chemical_data['lot_number']
    ).first()

def bulk_import_tools(csv_content: str, skip_duplicates: bool = True) -> BulkImportResult:
    """
    Bulk import tools from CSV content
    
    Args:
        csv_content: CSV content as string
        skip_duplicates: Whether to skip duplicate tools or raise error
    
    Returns:
        BulkImportResult object with import results
    """
    result = BulkImportResult()
    
    # Define expected headers for tools
    expected_headers = ['tool_number', 'serial_number', 'description']
    
    # Parse CSV content
    rows, parse_errors = parse_csv_content(csv_content, expected_headers)
    
    if parse_errors:
        for error in parse_errors:
            result.add_error(0, {}, error)
        return result
    
    # Process each row
    for row in rows:
        row_number = row.pop('_row_number')
        
        try:
            # Validate tool data
            tool_data = validate_tool_data(row)
            
            # Check for duplicates
            existing_tool = check_duplicate_tool(tool_data)
            if existing_tool:
                if skip_duplicates:
                    result.add_skipped(row_number, row, 
                                     f"Tool with number {tool_data['tool_number']} and serial {tool_data['serial_number']} already exists")
                    continue
                else:
                    result.add_error(row_number, row, 
                                   f"Duplicate tool: {tool_data['tool_number']} - {tool_data['serial_number']}")
                    continue
            
            # Create new tool
            tool = Tool(**tool_data)
            
            # Set calibration status
            if tool.requires_calibration:
                tool.calibration_status = 'due_soon'
            else:
                tool.calibration_status = 'not_applicable'
            
            db.session.add(tool)
            db.session.flush()  # Get the ID without committing
            
            result.add_success(row, tool)
            
        except ValidationError as e:
            result.add_error(row_number, row, str(e))
        except Exception as e:
            logger.error(f"Unexpected error processing tool row {row_number}: {str(e)}")
            result.add_error(row_number, row, f"Unexpected error: {str(e)}")
    
    # Commit all successful imports
    try:
        if result.success_count > 0:
            db.session.commit()
            logger.info(f"Successfully imported {result.success_count} tools")
        else:
            db.session.rollback()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error committing tool imports: {str(e)}")
        # Convert all successes to errors
        for item in result.created_items:
            result.add_error(0, item['data'], f"Database commit failed: {str(e)}")
        result.success_count = 0
        result.created_items = []
    
    return result

def bulk_import_chemicals(csv_content: str, skip_duplicates: bool = True) -> BulkImportResult:
    """
    Bulk import chemicals from CSV content
    
    Args:
        csv_content: CSV content as string
        skip_duplicates: Whether to skip duplicate chemicals or raise error
    
    Returns:
        BulkImportResult object with import results
    """
    result = BulkImportResult()
    
    # Define expected headers for chemicals
    expected_headers = ['part_number', 'lot_number', 'quantity', 'unit']
    
    # Parse CSV content
    rows, parse_errors = parse_csv_content(csv_content, expected_headers)
    
    if parse_errors:
        for error in parse_errors:
            result.add_error(0, {}, error)
        return result
    
    # Process each row
    for row in rows:
        row_number = row.pop('_row_number')
        
        try:
            # Validate chemical data
            chemical_data = validate_chemical_data(row)
            
            # Check for duplicates
            existing_chemical = check_duplicate_chemical(chemical_data)
            if existing_chemical:
                if skip_duplicates:
                    result.add_skipped(row_number, row, 
                                     f"Chemical with part number {chemical_data['part_number']} and lot {chemical_data['lot_number']} already exists")
                    continue
                else:
                    result.add_error(row_number, row, 
                                   f"Duplicate chemical: {chemical_data['part_number']} - {chemical_data['lot_number']}")
                    continue
            
            # Create new chemical
            chemical = Chemical(**chemical_data)
            db.session.add(chemical)
            db.session.flush()  # Get the ID without committing
            
            result.add_success(row, chemical)
            
        except ValidationError as e:
            result.add_error(row_number, row, str(e))
        except Exception as e:
            logger.error(f"Unexpected error processing chemical row {row_number}: {str(e)}")
            result.add_error(row_number, row, f"Unexpected error: {str(e)}")
    
    # Commit all successful imports
    try:
        if result.success_count > 0:
            db.session.commit()
            logger.info(f"Successfully imported {result.success_count} chemicals")
        else:
            db.session.rollback()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error committing chemical imports: {str(e)}")
        # Convert all successes to errors
        for item in result.created_items:
            result.add_error(0, item['data'], f"Database commit failed: {str(e)}")
        result.success_count = 0
        result.created_items = []
    
    return result

def generate_tool_template() -> str:
    """Generate CSV template for tool imports"""
    headers = [
        'tool_number',
        'serial_number', 
        'description',
        'condition',
        'location',
        'category',
        'status',
        'requires_calibration',
        'calibration_frequency_days'
    ]
    
    # Create sample data
    sample_data = [
        'T001',
        'SN001',
        'Sample Tool Description',
        'good',
        'Lab A',
        'General',
        'available',
        'false',
        ''
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(sample_data)
    
    return output.getvalue()

def generate_chemical_template() -> str:
    """Generate CSV template for chemical imports"""
    headers = [
        'part_number',
        'lot_number',
        'description',
        'manufacturer',
        'quantity',
        'unit',
        'location',
        'category',
        'expiration_date',
        'msds_url'
    ]
    
    # Create sample data
    sample_data = [
        'CHEM001',
        'LOT001',
        'Sample Chemical Description',
        'Sample Manufacturer',
        '10.5',
        'each',
        'Storage A',
        'General',
        '2025-12-31',
        'https://example.com/msds'
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(sample_data)
    
    return output.getvalue()
