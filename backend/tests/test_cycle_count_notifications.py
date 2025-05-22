import unittest
import json
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User
from models_cycle_count import CycleCountNotification

class CycleCountNotificationsTestCase(unittest.TestCase):
    """Test case for the cycle count notifications API"""

    def setUp(self):
        """Set up test client and create test data"""
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        
        # Create application context
        with self.app.app_context():
            # Create tables
            db.create_all()
            
            # Create test users
            self.admin_user = User(
                name='Test Admin',
                employee_number='TESTADMIN',
                department='IT',
                is_admin=True,
                password='password123'
            )
            
            self.regular_user = User(
                name='Test User',
                employee_number='TESTUSER',
                department='Engineering',
                is_admin=False,
                password='password123'
            )
            
            db.session.add(self.admin_user)
            db.session.add(self.regular_user)
            db.session.commit()
            
            # Create test notifications
            notifications = [
                CycleCountNotification(
                    user_id=self.regular_user.id,
                    notification_type='batch_assigned',
                    reference_id=1,
                    reference_type='batch',
                    message='You have been assigned 5 items to count in batch "Test Batch".',
                    is_read=False,
                    created_at=datetime.utcnow() - timedelta(hours=2)
                ),
                CycleCountNotification(
                    user_id=self.regular_user.id,
                    notification_type='discrepancy_found',
                    reference_id=2,
                    reference_type='result',
                    message='Discrepancy found in batch "Test Batch" for tool T1001 - Test Tool. Type: quantity.',
                    is_read=True,
                    created_at=datetime.utcnow() - timedelta(hours=1)
                ),
                CycleCountNotification(
                    user_id=self.admin_user.id,
                    notification_type='batch_completed',
                    reference_id=1,
                    reference_type='batch',
                    message='Cycle count batch "Test Batch" has been completed.',
                    is_read=False,
                    created_at=datetime.utcnow() - timedelta(minutes=30)
                )
            ]
            
            for notification in notifications:
                db.session.add(notification)
            
            db.session.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def login(self, user):
        """Helper method to log in a user"""
        return self.client.post(
            '/api/login',
            data=json.dumps({
                'employee_number': user.employee_number,
                'password': 'password123'
            }),
            content_type='application/json'
        )
    
    def test_get_notifications(self):
        """Test getting notifications for the current user"""
        # Log in as regular user
        login_response = self.login(self.regular_user)
        self.assertEqual(login_response.status_code, 200)
        
        # Get notifications
        response = self.client.get('/api/cycle-counts/notifications')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('notifications', data)
        self.assertIn('unread_count', data)
        
        # Check that we got the correct number of notifications
        self.assertEqual(len(data['notifications']), 2)
        self.assertEqual(data['unread_count'], 1)
        
        # Check that the notifications are for the correct user
        for notification in data['notifications']:
            self.assertEqual(notification['user_id'], self.regular_user.id)
    
    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        # Log in as regular user
        login_response = self.login(self.regular_user)
        self.assertEqual(login_response.status_code, 200)
        
        # Get notifications to find an unread one
        response = self.client.get('/api/cycle-counts/notifications')
        data = json.loads(response.data)
        
        unread_notification = None
        for notification in data['notifications']:
            if not notification['is_read']:
                unread_notification = notification
                break
        
        self.assertIsNotNone(unread_notification)
        
        # Mark notification as read
        response = self.client.post(f'/api/cycle-counts/notifications/{unread_notification["id"]}/read')
        self.assertEqual(response.status_code, 200)
        
        # Verify notification is now marked as read
        response = self.client.get('/api/cycle-counts/notifications')
        data = json.loads(response.data)
        
        for notification in data['notifications']:
            if notification['id'] == unread_notification['id']:
                self.assertTrue(notification['is_read'])
    
    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read"""
        # Log in as regular user
        login_response = self.login(self.regular_user)
        self.assertEqual(login_response.status_code, 200)
        
        # Mark all notifications as read
        response = self.client.post('/api/cycle-counts/notifications/read-all')
        self.assertEqual(response.status_code, 200)
        
        # Verify all notifications are now marked as read
        response = self.client.get('/api/cycle-counts/notifications')
        data = json.loads(response.data)
        
        self.assertEqual(data['unread_count'], 0)
        for notification in data['notifications']:
            self.assertTrue(notification['is_read'])

if __name__ == '__main__':
    unittest.main()
