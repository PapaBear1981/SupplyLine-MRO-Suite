# Messaging System - Quick Reference Guide

## Key Files at a Glance

### Backend Files
```
/backend/models_kits.py               - KitMessage model definition
/backend/routes_kit_messages.py       - All API endpoints (8 routes)
/backend/utils/file_validation.py     - File upload validation
/backend/tests/test_routes_kit_messages.py - Comprehensive tests (726 lines)
```

### Frontend Files
```
/frontend/src/components/kits/KitMessaging.jsx       - Main messaging UI
/frontend/src/components/kits/SendMessageModal.jsx   - Message composer
/frontend/src/store/kitMessagesSlice.js              - Redux state
/frontend/src/services/api.js                        - API client
```

## Quick API Reference

```bash
# Send a message
POST /api/kits/{kit_id}/messages
{
  "subject": "Help needed",
  "message": "Kit is missing parts",
  "recipient_id": 5,           # optional (null = broadcast)
  "related_request_id": 3,     # optional
  "attachments": "/path/to/file.jpg"  # optional
}

# Get messages for a kit
GET /api/kits/{kit_id}/messages?unread_only=true

# Get all user messages
GET /api/messages?sent=true

# Mark message as read
PUT /api/messages/{msg_id}/read

# Reply to message
POST /api/messages/{msg_id}/reply
{
  "message": "Thanks for the update"
}

# Get unread count
GET /api/messages/unread-count

# Delete message
DELETE /api/messages/{msg_id}
```

## Database Schema Summary

| Field | Type | Purpose |
|-------|------|---------|
| kit_id | FK | Which kit this message belongs to |
| sender_id | FK | Who sent it |
| recipient_id | FK | Who receives it (NULL = broadcast) |
| subject | String(200) | Message title |
| message | String(5000) | Message body |
| is_read | Boolean | Read status |
| sent_date | DateTime | When sent |
| read_date | DateTime | When read |
| parent_message_id | FK | For threading (replies) |
| attachments | String(1000) | Comma-separated file paths |

## Frontend Components

### KitMessaging.jsx
- Main UI component
- Inbox/Sent tabs
- Message list with threading
- Compose & reply modals
- Auto-refresh on send

### SendMessageModal.jsx
- Modal form for new messages
- Subject auto-fill with kit name
- User ID input for recipient
- Broadcast support (leave recipient empty)
- Form validation
- Success/error alerts

### kitMessagesSlice.js
Redux state with:
- `messages` - Keyed by kit_id
- `unreadCount` - Total unread
- `loading` - API state
- `error` - Error handling

## Current Capabilities

✓ One-to-one messaging
✓ Broadcast messaging (to all kit users)
✓ Message threading (replies)
✓ Read status tracking
✓ Unread count tracking
✓ Link to reorder requests
✓ File validation backend
✓ Full test coverage

## Current Limitations

✗ No real-time updates (manual refresh needed)
✗ No file upload UI (backend ready, frontend missing)
✗ No user picker (manual ID entry required)
✗ No message search
✗ No message editing
✗ No soft delete (hard delete only)
✗ No WebSocket/Socket.io
✗ No typing indicators

## Security Features

✓ JWT authentication required
✓ Role-based authorization (sender/recipient check)
✓ File validation (magic bytes, MIME type)
✓ File size limits (5MB)
✓ CSV formula injection prevention
✓ SQL injection protection (ORM)
✓ CORS configured

## Testing Coverage

8 test classes, 726 lines of tests:
- Send message (8 tests)
- Get messages (7 tests)
- Get user messages (5 tests)
- Get message detail (7 tests)
- Mark as read (6 tests)
- Reply to message (6 tests)
- Unread count (4 tests)
- Delete message (5 tests)

Run with: `pytest /backend/tests/test_routes_kit_messages.py`

## Enhancement Roadmap

1. **Real-time (High Priority)**
   - WebSocket support
   - Live message delivery
   - Typing indicators
   - Presence indicators

2. **File Attachments (Medium Priority)**
   - Upload UI in modal
   - File preview
   - Download functionality
   - Image gallery

3. **UX Improvements (Medium Priority)**
   - User picker dropdown
   - Message search
   - Conversation view
   - Read receipts

4. **Management (Low Priority)**
   - Soft delete
   - Message archival
   - Retention policies
   - Export functionality

## Architecture Notes

- **Pattern**: REST API + Redux state management
- **Database**: SQLAlchemy ORM (PostgreSQL/MySQL/SQLite)
- **Auth**: JWT tokens
- **Polling**: Manual (no auto-refresh)
- **Threading**: Parent-child via foreign key
- **Broadcasting**: NULL recipient_id = all users

## Common Tasks

### Add a new message field
1. Update `KitMessage` model in `models_kits.py`
2. Update `to_dict()` method
3. Update API endpoint in `routes_kit_messages.py`
4. Update tests in `test_routes_kit_messages.py`
5. Update frontend form if needed

### Add file upload UI
1. Add file input to `SendMessageModal.jsx`
2. Create upload handler endpoint
3. Update Redux thunk to handle upload
4. Add attachment display to message view

### Implement real-time
Option 1: Socket.io
- Add socket events (new_message, read, typing)
- Client listener setup
- Namespace: `/messages`

Option 2: Server-Sent Events
- Create SSE endpoint `/api/messages/stream`
- Client EventSource listener
- No bidirectional needed

Option 3: WebSocket (raw)
- Flask-SocketIO or websocket library
- Full duplex communication
- More overhead

## Debugging Tips

```python
# Check message details
msg = KitMessage.query.get(123)
print(msg.to_dict())

# Check visibility
messages = KitMessage.query.filter_by(kit_id=1).all()

# Check unread count
count = KitMessage.query.filter_by(
    recipient_id=user_id, 
    is_read=False
).count()
```

```javascript
// Redux debugging
console.log(store.getState().kitMessages)

// API debugging
api.get('/messages').then(r => console.log(r.data))

// Component state
console.log({ messages, loading, error })
```

## Contact / Support

- Architecture: Flask + React + SQLAlchemy
- Test Framework: Pytest
- Frontend State: Redux Toolkit
- UI Library: React Bootstrap
- Icons: Font Awesome (react-icons)
