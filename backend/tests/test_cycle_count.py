"""
Comprehensive test suite for cycle count functionality
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import the Flask app and models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User, Tool, Chemical
from models_cycle_count import (
    CycleCountSchedule, CycleCountBatch, CycleCountItem,
    CycleCountResult, CycleCountAdjustment
)


class CycleCountTestCase(unittest.TestCase):
    """Base test case for cycle count functionality"""

    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        # Create a temporary database
        self.db_fd, self.app.config['DATABASE'] = tempfile.mkstemp()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.app.config['DATABASE']

        self.client = self.app.test_client()
        self.headers = {}

        with self.app.app_context():
            db.create_all()
            self._create_test_data()

    def tearDown(self):
        """Clean up test environment"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])

    def _create_test_data(self):
        """Create test data"""
        # Create test user
        self.test_user = User(
            employee_number='TEST001',
            name='Test User',
            department='Testing',
            is_admin=True,
            is_active=True
        )
        self.test_user.set_password('test123')
        db.session.add(self.test_user)

        # Create test tools
        self.test_tool = Tool(
            tool_number='T001',
            serial_number='S001',
            description='Test Tool',
            category='Testing',
            location='Test Location',
            status='available'
        )
        db.session.add(self.test_tool)

        # Create test chemical
        self.test_chemical = Chemical(
            part_number='C001',
            description='Test Chemical',
            category='Testing',
            quantity=100.0,
            unit='ml',
            location='Test Location',
            status='available'
        )
        db.session.add(self.test_chemical)

        db.session.commit()

    def _login(self):
        """Helper method to log in using JWT auth"""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({
                'employee_number': 'TEST001',
                'password': 'test123'
            }),
            content_type='application/json'
        )

        if response.status_code == 200:
            data = json.loads(response.data)
            self.headers = {
                'Authorization': f"Bearer {data['access_token']}"
            }

        return response


class TestCycleCountSchedules(CycleCountTestCase):
    """Test cycle count schedule functionality"""

    def test_create_schedule(self):
        """Test creating a cycle count schedule"""
        self._login()

        schedule_data = {
            'name': 'Test Schedule',
            'description': 'Test Description',
            'frequency': 'monthly',
            'method': 'ABC'
        }

        response = self.client.post(
            '/api/cycle-count/schedules',
            data=json.dumps(schedule_data),
            content_type='application/json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test Schedule')
        self.assertEqual(data['frequency'], 'monthly')

    def test_get_schedules(self):
        """Test retrieving cycle count schedules"""
        self._login()

        # Create a test schedule
        with self.app.app_context():
            schedule = CycleCountSchedule(
                name='Test Schedule',
                frequency='weekly',
                method='random',
                created_by=self.test_user.id
            )
            db.session.add(schedule)
            db.session.commit()

        response = self.client.get('/api/cycle-count/schedules', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Schedule')

    def test_update_schedule(self):
        """Test updating a cycle count schedule"""
        self._login()

        # Create a test schedule
        with self.app.app_context():
            schedule = CycleCountSchedule(
                name='Test Schedule',
                frequency='weekly',
                method='random',
                created_by=self.test_user.id
            )
            db.session.add(schedule)
            db.session.commit()
            schedule_id = schedule.id

        update_data = {
            'name': 'Updated Schedule',
            'frequency': 'monthly'
        }

        response = self.client.put(
            f'/api/cycle-count/schedules/{schedule_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Schedule')
        self.assertEqual(data['frequency'], 'monthly')


class TestCycleCountBatches(CycleCountTestCase):
    """Test cycle count batch functionality"""

    def setUp(self):
        super().setUp()
        # Create a test schedule
        with self.app.app_context():
            self.test_schedule = CycleCountSchedule(
                name='Test Schedule',
                frequency='weekly',
                method='random',
                created_by=self.test_user.id
            )
            db.session.add(self.test_schedule)
            db.session.commit()

    def test_create_batch(self):
        """Test creating a cycle count batch"""
        self._login()

        batch_data = {
            'schedule_id': self.test_schedule.id,
            'name': 'Test Batch',
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=7)).isoformat()
        }

        response = self.client.post(
            '/api/cycle-count/batches',
            data=json.dumps(batch_data),
            content_type='application/json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test Batch')
        self.assertEqual(data['schedule_id'], self.test_schedule.id)

    def test_generate_batch_items(self):
        """Test generating items for a batch"""
        self._login()

        # Create a test batch
        with self.app.app_context():
            batch = CycleCountBatch(
                schedule_id=self.test_schedule.id,
                name='Test Batch',
                status='draft',
                created_by=self.test_user.id
            )
            db.session.add(batch)
            db.session.commit()
            batch_id = batch.id

        generate_data = {
            'item_types': ['tool', 'chemical'],
            'sample_size': 10
        }

        response = self.client.post(
            f'/api/cycle-count/batches/{batch_id}/generate-items',
            data=json.dumps(generate_data),
            content_type='application/json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('items_generated', data)


class TestCycleCountItems(CycleCountTestCase):
    """Test cycle count item functionality"""

    def setUp(self):
        super().setUp()
        # Create test schedule and batch
        with self.app.app_context():
            self.test_schedule = CycleCountSchedule(
                name='Test Schedule',
                frequency='weekly',
                method='random',
                created_by=self.test_user.id
            )
            db.session.add(self.test_schedule)

            self.test_batch = CycleCountBatch(
                schedule_id=self.test_schedule.id,
                name='Test Batch',
                status='active',
                created_by=self.test_user.id
            )
            db.session.add(self.test_batch)

            self.test_item = CycleCountItem(
                batch_id=self.test_batch.id,
                item_type='tool',
                item_id=self.test_tool.id,
                expected_quantity=1,
                expected_location='Test Location',
                status='pending'
            )
            db.session.add(self.test_item)

            db.session.commit()

    def test_get_batch_items(self):
        """Test retrieving items for a batch"""
        self._login()

        response = self.client.get(
            f'/api/cycle-count/batches/{self.test_batch.id}/items',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['item_type'], 'tool')

    def test_submit_count_result(self):
        """Test submitting a count result"""
        self._login()

        result_data = {
            'actual_quantity': 1,
            'actual_location': 'Test Location',
            'condition': 'good',
            'notes': 'Test count'
        }

        response = self.client.post(
            f'/api/cycle-count/items/{self.test_item.id}/count',
            data=json.dumps(result_data),
            content_type='application/json',
            headers=self.headers
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['actual_quantity'], 1)
        self.assertEqual(data['condition'], 'good')


if __name__ == '__main__':
    unittest.main()
