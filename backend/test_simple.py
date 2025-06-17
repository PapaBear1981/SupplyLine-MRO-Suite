import unittest
import tempfile
import os
from models import db, User, Tool

class SimpleTestCase(unittest.TestCase):
    """Simple test case to verify the environment is working"""

    def test_imports(self):
        """Test that we can import the required modules"""
        self.assertIsNotNone(db)
        self.assertIsNotNone(User)
        self.assertIsNotNone(Tool)

    def test_user_model(self):
        """Test basic User model functionality"""
        user = User(
            name='Test User',
            employee_number='TEST001',
            department='Testing',
            is_admin=False,
            is_active=True
        )
        user.set_password('test123')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.employee_number, 'TEST001')
        self.assertTrue(user.check_password('test123'))
        self.assertFalse(user.check_password('wrong'))

    def test_tool_model(self):
        """Test basic Tool model functionality"""
        tool = Tool(
            tool_number='T001',
            serial_number='S001',
            description='Test Tool',
            category='Testing',
            location='Test Location',
            status='available'
        )
        self.assertEqual(tool.tool_number, 'T001')
        self.assertEqual(tool.status, 'available')

if __name__ == '__main__':
    unittest.main()
