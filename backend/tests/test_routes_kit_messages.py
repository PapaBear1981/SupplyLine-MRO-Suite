"""
Unit tests for Kit Messaging API endpoints

Tests all messaging-related API endpoints including:
- Sending messages
- Getting messages for a kit
- Getting user messages
- Getting message details
- Marking messages as read
- Replying to messages
- Getting unread count
- Deleting messages
- Authentication and authorization
- Validation and error handling
- Threading support
- Broadcast messages
"""

import pytest
import json
from models import User
from models_kits import AircraftType, Kit, KitMessage, KitReorderRequest


@pytest.fixture
def aircraft_type(db_session):
    """Create a test aircraft type"""
    aircraft_type = AircraftType.query.filter_by(name='Q400').first()
    if not aircraft_type:
        aircraft_type = AircraftType(name='Q400', description='Test Aircraft', is_active=True)
        db_session.add(aircraft_type)
        db_session.commit()
    return aircraft_type


@pytest.fixture
def test_kit(db_session, admin_user, aircraft_type):
    """Create a test kit"""
    import uuid
    kit_name = f'Test Kit {uuid.uuid4().hex[:8]}'
    kit = Kit(
        name=kit_name,
        aircraft_type_id=aircraft_type.id,
        description='Test kit for messaging tests',
        status='active',
        created_by=admin_user.id
    )
    db_session.add(kit)
    db_session.commit()
    return kit


@pytest.fixture
def second_user(db_session):
    """Create a second test user"""
    import uuid
    emp_number = f'USR{uuid.uuid4().hex[:6]}'
    
    user = User(
        name='Second User',
        employee_number=emp_number,
        department='Maintenance',
        is_admin=False,
        is_active=True
    )
    user.set_password('second123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_headers_second(client, second_user):
    """Get auth headers for second user"""
    response = client.post('/api/auth/login', json={
        'employee_number': second_user.employee_number,
        'password': 'second123'
    })
    data = json.loads(response.data)
    return {'Authorization': f'Bearer {data["access_token"]}'}


@pytest.fixture
def test_message(db_session, test_kit, admin_user, second_user):
    """Create a test message"""
    message = KitMessage(
        kit_id=test_kit.id,
        sender_id=admin_user.id,
        recipient_id=second_user.id,
        subject='Test Message',
        message='This is a test message',
        is_read=False
    )
    db_session.add(message)
    db_session.commit()
    return message


@pytest.fixture
def broadcast_message(db_session, test_kit, admin_user):
    """Create a broadcast message (no recipient)"""
    message = KitMessage(
        kit_id=test_kit.id,
        sender_id=admin_user.id,
        recipient_id=None,
        subject='Broadcast Message',
        message='This is a broadcast message',
        is_read=False
    )
    db_session.add(message)
    db_session.commit()
    return message


@pytest.fixture
def test_reorder_request(db_session, test_kit, admin_user):
    """Create a test reorder request"""
    reorder = KitReorderRequest(
        kit_id=test_kit.id,
        item_type='expendable',
        part_number='EXP-001',
        description='Safety Wire',
        quantity_requested=100.0,
        priority='high',
        requested_by=admin_user.id,
        status='pending'
    )
    db_session.add(reorder)
    db_session.commit()
    return reorder


class TestSendKitMessage:
    """Test sending messages"""

    def test_send_message_to_specific_user(self, client, auth_headers_admin, test_kit, second_user):
        """Test sending message to specific user"""
        message_data = {
            'recipient_id': second_user.id,
            'subject': 'Need Parts',
            'message': 'Please send safety wire to this kit'
        }

        response = client.post(f'/api/kits/{test_kit.id}/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['subject'] == 'Need Parts'
        assert data['message'] == 'Please send safety wire to this kit'
        assert data['recipient_id'] == second_user.id
        assert data['is_read'] is False

    def test_send_broadcast_message(self, client, auth_headers_admin, test_kit):
        """Test sending broadcast message (no recipient)"""
        message_data = {
            'subject': 'Kit Update',
            'message': 'This kit is being relocated'
        }

        response = client.post(f'/api/kits/{test_kit.id}/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['subject'] == 'Kit Update'
        assert data['recipient_id'] is None

    def test_send_message_with_related_request(self, client, auth_headers_admin, test_kit, test_reorder_request, second_user):
        """Test sending message linked to reorder request"""
        message_data = {
            'recipient_id': second_user.id,
            'related_request_id': test_reorder_request.id,
            'subject': 'Reorder Status',
            'message': 'When will this reorder be fulfilled?'
        }

        response = client.post(f'/api/kits/{test_kit.id}/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['related_request_id'] == test_reorder_request.id

    def test_send_message_with_attachments(self, client, auth_headers_admin, test_kit, second_user):
        """Test sending message with attachments"""
        message_data = {
            'recipient_id': second_user.id,
            'subject': 'Photo Attached',
            'message': 'See attached photo of damaged part',
            'attachments': '/uploads/photo1.jpg,/uploads/photo2.jpg'
        }

        response = client.post(f'/api/kits/{test_kit.id}/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['attachments'] == '/uploads/photo1.jpg,/uploads/photo2.jpg'

    def test_send_message_missing_subject(self, client, auth_headers_admin, test_kit):
        """Test sending message without subject"""
        message_data = {
            'message': 'This message has no subject'
        }

        response = client.post(f'/api/kits/{test_kit.id}/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Subject is required' in data['error']

    def test_send_message_missing_message(self, client, auth_headers_admin, test_kit):
        """Test sending message without message body"""
        message_data = {
            'subject': 'Empty Message'
        }

        response = client.post(f'/api/kits/{test_kit.id}/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Message is required' in data['error']

    def test_send_message_kit_not_found(self, client, auth_headers_admin):
        """Test sending message for non-existent kit"""
        message_data = {
            'subject': 'Test',
            'message': 'Test message'
        }

        response = client.post('/api/kits/99999/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 404

    def test_send_message_unauthenticated(self, client, test_kit):
        """Test sending message without authentication"""
        message_data = {
            'subject': 'Test',
            'message': 'Test message'
        }

        response = client.post(f'/api/kits/{test_kit.id}/messages', json=message_data)

        assert response.status_code == 401


class TestGetKitMessages:
    """Test getting messages for a kit"""

    def test_get_kit_messages_as_sender(self, client, auth_headers_admin, test_kit, test_message):
        """Test getting kit messages as sender"""
        response = client.get(f'/api/kits/{test_kit.id}/messages', headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_kit_messages_as_recipient(self, client, auth_headers_second, test_kit, test_message):
        """Test getting kit messages as recipient"""
        response = client.get(f'/api/kits/{test_kit.id}/messages', headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_kit_messages_includes_broadcast(self, client, auth_headers_user, test_kit, broadcast_message):
        """Test that broadcast messages are visible to all users"""
        response = client.get(f'/api/kits/{test_kit.id}/messages', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        # Should see broadcast message even though not sender or recipient
        broadcast_msgs = [msg for msg in data if msg['recipient_id'] is None]
        assert len(broadcast_msgs) >= 1

    def test_get_kit_messages_filter_unread(self, client, auth_headers_second, test_kit, test_message):
        """Test filtering for unread messages only"""
        response = client.get(f'/api/kits/{test_kit.id}/messages?unread_only=true',
                            headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for msg in data:
            assert msg['is_read'] is False

    def test_get_kit_messages_filter_by_request(self, client, auth_headers_admin, test_kit, test_reorder_request, db_session, admin_user, second_user):
        """Test filtering messages by related request"""
        # Create message linked to request
        message = KitMessage(
            kit_id=test_kit.id,
            related_request_id=test_reorder_request.id,
            sender_id=admin_user.id,
            recipient_id=second_user.id,
            subject='About Reorder',
            message='Status update',
            is_read=False
        )
        db_session.add(message)
        db_session.commit()

        response = client.get(f'/api/kits/{test_kit.id}/messages?related_request_id={test_reorder_request.id}',
                            headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for msg in data:
            assert msg['related_request_id'] == test_reorder_request.id

    def test_get_kit_messages_kit_not_found(self, client, auth_headers_admin):
        """Test getting messages for non-existent kit"""
        response = client.get('/api/kits/99999/messages', headers=auth_headers_admin)

        assert response.status_code == 404

    def test_get_kit_messages_unauthenticated(self, client, test_kit):
        """Test getting kit messages without authentication"""
        response = client.get(f'/api/kits/{test_kit.id}/messages')

        assert response.status_code == 401


class TestGetUserMessages:
    """Test getting user's messages"""

    def test_get_received_messages(self, client, auth_headers_second, test_message):
        """Test getting messages received by user"""
        response = client.get('/api/messages', headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        # Should see messages where user is recipient
        assert len(data) >= 1

    def test_get_sent_messages(self, client, auth_headers_admin, test_message):
        """Test getting messages sent by user"""
        response = client.get('/api/messages?sent=true', headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        # Should see messages where user is sender
        assert len(data) >= 1

    def test_get_unread_messages_only(self, client, auth_headers_second, test_message):
        """Test filtering for unread messages"""
        response = client.get('/api/messages?unread_only=true', headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for msg in data:
            assert msg['is_read'] is False

    def test_get_user_messages_includes_broadcast(self, client, auth_headers_user, broadcast_message):
        """Test that broadcast messages appear in user's messages"""
        response = client.get('/api/messages', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        # Should see broadcast messages
        broadcast_msgs = [msg for msg in data if msg['recipient_id'] is None]
        assert len(broadcast_msgs) >= 1

    def test_get_user_messages_unauthenticated(self, client):
        """Test getting user messages without authentication"""
        response = client.get('/api/messages')

        assert response.status_code == 401


class TestGetMessageById:
    """Test getting message details"""

    def test_get_message_as_sender(self, client, auth_headers_admin, test_message):
        """Test getting message details as sender"""
        response = client.get(f'/api/messages/{test_message.id}', headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['id'] == test_message.id
        assert data['subject'] == test_message.subject
        assert 'reply_count' in data

    def test_get_message_as_recipient(self, client, auth_headers_second, test_message):
        """Test getting message details as recipient"""
        response = client.get(f'/api/messages/{test_message.id}', headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['id'] == test_message.id

    def test_get_message_with_replies(self, client, auth_headers_admin, test_message, db_session, second_user):
        """Test getting message with replies included"""
        # Create a reply
        reply = KitMessage(
            kit_id=test_message.kit_id,
            sender_id=second_user.id,
            recipient_id=test_message.sender_id,
            subject=f"Re: {test_message.subject}",
            message='This is a reply',
            parent_message_id=test_message.id,
            is_read=False
        )
        db_session.add(reply)
        db_session.commit()

        response = client.get(f'/api/messages/{test_message.id}', headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['reply_count'] >= 1
        assert 'replies' in data
        assert len(data['replies']) >= 1

    def test_get_message_unauthorized_user(self, client, auth_headers_user, test_message):
        """Test getting message by unauthorized user"""
        response = client.get(f'/api/messages/{test_message.id}', headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'You do not have access to this message' in data['error']

    def test_get_broadcast_message_any_user(self, client, auth_headers_user, broadcast_message):
        """Test that any user can view broadcast messages"""
        response = client.get(f'/api/messages/{broadcast_message.id}', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['id'] == broadcast_message.id
        assert data['recipient_id'] is None

    def test_get_message_not_found(self, client, auth_headers_admin):
        """Test getting non-existent message"""
        response = client.get('/api/messages/99999', headers=auth_headers_admin)

        assert response.status_code == 404

    def test_get_message_unauthenticated(self, client, test_message):
        """Test getting message without authentication"""
        response = client.get(f'/api/messages/{test_message.id}')

        assert response.status_code == 401


class TestMarkMessageRead:
    """Test marking messages as read"""

    def test_mark_message_read_as_recipient(self, client, auth_headers_second, test_message):
        """Test marking message as read by recipient"""
        response = client.put(f'/api/messages/{test_message.id}/read',
                            headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['is_read'] is True
        assert data['read_date'] is not None

    def test_mark_message_read_already_read(self, client, auth_headers_second, test_message, db_session):
        """Test marking already read message as read"""
        # Mark as read first
        test_message.is_read = True
        from datetime import datetime
        test_message.read_date = datetime.now()
        db_session.commit()

        response = client.put(f'/api/messages/{test_message.id}/read',
                            headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['is_read'] is True

    def test_mark_message_read_not_recipient(self, client, auth_headers_admin, test_message):
        """Test marking message as read by non-recipient"""
        response = client.put(f'/api/messages/{test_message.id}/read',
                            headers=auth_headers_admin)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'You can only mark your own messages as read' in data['error']

    def test_mark_broadcast_message_read(self, client, auth_headers_user, broadcast_message):
        """Test marking broadcast message as read"""
        response = client.put(f'/api/messages/{broadcast_message.id}/read',
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['is_read'] is True

    def test_mark_message_read_not_found(self, client, auth_headers_admin):
        """Test marking non-existent message as read"""
        response = client.put('/api/messages/99999/read',
                            headers=auth_headers_admin)

        assert response.status_code == 404

    def test_mark_message_read_unauthenticated(self, client, test_message):
        """Test marking message as read without authentication"""
        response = client.put(f'/api/messages/{test_message.id}/read')

        assert response.status_code == 401


class TestReplyToMessage:
    """Test replying to messages"""

    def test_reply_to_message(self, client, auth_headers_second, test_message):
        """Test replying to a message"""
        reply_data = {
            'message': 'Thanks for the update!'
        }

        response = client.post(f'/api/messages/{test_message.id}/reply',
                             json=reply_data,
                             headers=auth_headers_second)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['parent_message_id'] == test_message.id
        assert data['subject'].startswith('Re:')
        assert data['message'] == 'Thanks for the update!'
        assert data['kit_id'] == test_message.kit_id

    def test_reply_to_message_with_attachments(self, client, auth_headers_second, test_message):
        """Test replying with attachments"""
        reply_data = {
            'message': 'See attached photo',
            'attachments': '/uploads/reply_photo.jpg'
        }

        response = client.post(f'/api/messages/{test_message.id}/reply',
                             json=reply_data,
                             headers=auth_headers_second)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['attachments'] == '/uploads/reply_photo.jpg'

    def test_reply_to_own_message(self, client, auth_headers_admin, test_message):
        """Test replying to own message (should send to original recipient)"""
        reply_data = {
            'message': 'Follow-up information'
        }

        response = client.post(f'/api/messages/{test_message.id}/reply',
                             json=reply_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        data = json.loads(response.data)

        # Should be sent to original recipient
        assert data['recipient_id'] == test_message.recipient_id

    def test_reply_to_message_missing_message(self, client, auth_headers_second, test_message):
        """Test replying without message body"""
        reply_data = {}

        response = client.post(f'/api/messages/{test_message.id}/reply',
                             json=reply_data,
                             headers=auth_headers_second)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Message is required' in data['error']

    def test_reply_to_message_not_found(self, client, auth_headers_admin):
        """Test replying to non-existent message"""
        reply_data = {
            'message': 'Reply to nothing'
        }

        response = client.post('/api/messages/99999/reply',
                             json=reply_data,
                             headers=auth_headers_admin)

        assert response.status_code == 404

    def test_reply_to_message_unauthenticated(self, client, test_message):
        """Test replying to message without authentication"""
        reply_data = {
            'message': 'Unauthorized reply'
        }

        response = client.post(f'/api/messages/{test_message.id}/reply', json=reply_data)

        assert response.status_code == 401


class TestGetUnreadCount:
    """Test getting unread message count"""

    def test_get_unread_count(self, client, auth_headers_second, test_message):
        """Test getting unread message count"""
        response = client.get('/api/messages/unread-count', headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'unread_count' in data
        assert data['unread_count'] >= 1

    def test_get_unread_count_after_reading(self, client, auth_headers_second, test_message, db_session):
        """Test unread count decreases after reading message"""
        # Get initial count
        response = client.get('/api/messages/unread-count', headers=auth_headers_second)
        initial_count = json.loads(response.data)['unread_count']

        # Mark message as read
        test_message.is_read = True
        from datetime import datetime
        test_message.read_date = datetime.now()
        db_session.commit()

        # Get new count
        response = client.get('/api/messages/unread-count', headers=auth_headers_second)
        new_count = json.loads(response.data)['unread_count']

        assert new_count < initial_count

    def test_get_unread_count_includes_broadcast(self, client, auth_headers_user, broadcast_message):
        """Test unread count includes broadcast messages"""
        response = client.get('/api/messages/unread-count', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['unread_count'] >= 1

    def test_get_unread_count_unauthenticated(self, client):
        """Test getting unread count without authentication"""
        response = client.get('/api/messages/unread-count')

        assert response.status_code == 401


class TestDeleteMessage:
    """Test deleting messages"""

    def test_delete_message_as_sender(self, client, auth_headers_admin, test_message):
        """Test deleting message as sender"""
        response = client.delete(f'/api/messages/{test_message.id}',
                               headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'Message deleted successfully' in data['message']

        # Verify message is deleted
        from models_kits import KitMessage
        deleted_msg = KitMessage.query.get(test_message.id)
        assert deleted_msg is None

    def test_delete_message_as_recipient(self, client, auth_headers_second, test_message):
        """Test deleting message as recipient"""
        response = client.delete(f'/api/messages/{test_message.id}',
                               headers=auth_headers_second)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'Message deleted successfully' in data['message']

    def test_delete_message_unauthorized_user(self, client, auth_headers_user, test_message):
        """Test deleting message by unauthorized user"""
        response = client.delete(f'/api/messages/{test_message.id}',
                               headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'You can only delete your own messages' in data['error']

    def test_delete_message_not_found(self, client, auth_headers_admin):
        """Test deleting non-existent message"""
        response = client.delete('/api/messages/99999',
                               headers=auth_headers_admin)

        assert response.status_code == 404

    def test_delete_message_unauthenticated(self, client, test_message):
        """Test deleting message without authentication"""
        response = client.delete(f'/api/messages/{test_message.id}')

        assert response.status_code == 401

