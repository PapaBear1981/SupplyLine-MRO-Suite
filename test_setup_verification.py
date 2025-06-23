"""
Simple test to verify the development environment setup is working correctly
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models import db, User, Tool, Chemical, ChemicalIssuance
from models import ToolCalibration, CalibrationStandard, ToolCalibrationStandard
from models import UserActivity, ToolServiceRecord

def test_flask_app_creation():
    """Test that Flask app can be created successfully"""
    app = create_app()
    assert app is not None
    assert app.config is not None

def test_database_models_import():
    """Test that all database models can be imported successfully"""
    # Test basic models
    assert User is not None
    assert Tool is not None
    assert Chemical is not None
    assert ChemicalIssuance is not None
    
    # Test calibration models
    assert ToolCalibration is not None
    assert CalibrationStandard is not None
    assert ToolCalibrationStandard is not None
    
    # Test activity models
    assert UserActivity is not None
    assert ToolServiceRecord is not None

def test_database_initialization():
    """Test that database can be initialized with models"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Test creating a user
        user = User(
            name='Test User',
            employee_number='TEST001',
            department='Test'
        )
        user.set_password('testpass')
        db.session.add(user)
        
        # Test creating a tool
        tool = Tool(
            tool_number='T001',
            serial_number='SN001',
            description='Test Tool',
            condition='Good',
            location='Test Location'
        )
        db.session.add(tool)
        
        # Test creating a chemical
        chemical = Chemical(
            part_number='C001',
            lot_number='L001',
            description='Test Chemical',
            quantity=10.0,
            unit='ml'
        )
        db.session.add(chemical)
        
        db.session.commit()
        
        # Verify records were created
        assert User.query.count() == 1
        assert Tool.query.count() == 1
        assert Chemical.query.count() == 1

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
