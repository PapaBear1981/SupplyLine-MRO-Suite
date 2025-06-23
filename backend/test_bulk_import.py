#!/usr/bin/env python3
"""
Test script for bulk import functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.bulk_import import (
    generate_tool_template, 
    generate_chemical_template,
    parse_csv_content,
    validate_tool_data,
    validate_chemical_data
)

def test_templates():
    """Test template generation"""
    print("Testing template generation...")
    
    # Test tool template
    tool_template = generate_tool_template()
    print(f"Tool template generated ({len(tool_template)} characters)")
    print("Tool template preview:")
    print(tool_template[:200] + "..." if len(tool_template) > 200 else tool_template)
    print()
    
    # Test chemical template
    chemical_template = generate_chemical_template()
    print(f"Chemical template generated ({len(chemical_template)} characters)")
    print("Chemical template preview:")
    print(chemical_template[:200] + "..." if len(chemical_template) > 200 else chemical_template)
    print()

def test_csv_parsing():
    """Test CSV parsing functionality"""
    print("Testing CSV parsing...")
    
    # Test tool CSV parsing
    tool_csv = """tool_number,serial_number,description,condition,location,category
T001,SN001,Test Tool 1,good,Lab A,General
T002,SN002,Test Tool 2,excellent,Lab B,Testing"""
    
    expected_headers = ['tool_number', 'serial_number', 'description']
    rows, errors = parse_csv_content(tool_csv, expected_headers)
    
    print(f"Parsed {len(rows)} tool rows with {len(errors)} errors")
    if errors:
        print("Errors:", errors)
    else:
        print("Sample parsed row:", rows[0] if rows else "No rows")
    print()

def test_validation():
    """Test data validation"""
    print("Testing data validation...")
    
    # Test tool validation
    tool_data = {
        'tool_number': 'T001',
        'serial_number': 'SN001',
        'description': 'Test Tool',
        'condition': 'good',
        'location': 'Lab A',
        'category': 'General',
        'requires_calibration': 'false',
        'calibration_frequency_days': ''
    }
    
    try:
        validated_tool = validate_tool_data(tool_data)
        print("Tool validation successful:", validated_tool)
    except Exception as e:
        print("Tool validation error:", str(e))
    
    # Test chemical validation
    chemical_data = {
        'part_number': 'CHEM001',
        'lot_number': 'LOT001',
        'description': 'Test Chemical',
        'manufacturer': 'Test Manufacturer',
        'quantity': '10.5',
        'unit': 'each',
        'location': 'Storage A',
        'category': 'General',
        'expiration_date': '2025-12-31',
        'msds_url': 'https://example.com/msds'
    }
    
    try:
        validated_chemical = validate_chemical_data(chemical_data)
        print("Chemical validation successful:", validated_chemical)
    except Exception as e:
        print("Chemical validation error:", str(e))
    print()

if __name__ == '__main__':
    print("=== Bulk Import Test Suite ===")
    print()
    
    try:
        test_templates()
        test_csv_parsing()
        test_validation()
        
        print("=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
