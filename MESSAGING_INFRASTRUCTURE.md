# SupplyLine-MRO-Suite: Messaging Infrastructure Analysis

## Executive Summary

The SupplyLine-MRO-Suite application currently implements a **REST-based messaging system** specifically designed for kit-related communication between mechanics and stores personnel. The system is fully functional but lacks real-time capabilities, file attachment support in the frontend, and lacks WebSocket/Socket.io implementation for live updates.

---

## 1. Current Messaging Models & Database Schema

### Primary Message Model: `KitMessage`
**Location:** `/backend/models_kits.py` (lines 469-520)

```python
class KitMessage(db.Model):
    __tablename__ = "kit_messages"
    
    id                  - Integer (Primary Key)
    kit_id              - Integer (FK to kits.id) - Required
    related_request_id  - Integer (FK to kit_reorder_requests.id) - Optional
    sender_id           - Integer (FK to users.id) - Required
    recipient_id        - Integer (FK to users.id) - Optional (NULL = broadcast)
    subject             - String(200) - Required
    message             - String(5000) - Required
    is_read             - Boolean (default=False)
    sent_date           - DateTime (auto-set to current time)
    read_date           - DateTime (NULL until read)
    parent_message_id   - Integer (FK to kit_messages.id) - For threading
    attachments         - String(1000) - JSON string of attachment paths
```

### Key Characteristics

1. **Kit-Centric Design**: Every message is associated with a specific kit
2. **Recipient Flexibility**: 
   - Can be sent to specific user (recipient_id populated)
   - Can be broadcast (recipient_id = NULL, visible to all kit users)
3. **Threading Support**: Replies linked via `parent_message_id`
4. **Read Status Tracking**: `is_read` and `read_date` fields for tracking message status
5. **Reorder Context**: Optional link to `KitReorderRequest` for contextual messaging
6. **Attachment Support**: String field for JSON-serialized attachment paths (backend only)

### Supporting Model: `User`
**Location:** `/backend/models.py` (lines 131-356)

User model includes:
- `name`, `employee_number`, `department`
- `is_admin`, `is_active` flags
- `avatar` - Path to user avatar image
- Various security fields (password hash, failed login attempts, account lockout)

### Supporting Model: `KitReorderRequest`
**Location:** `/backend/models_kits.py` (lines 411-466)

Messages can be linked to reorder requests for contextual communication about specific item requests.

---

## 2. Message API Routes & Endpoints

**Location:** `/backend/routes_kit_messages.py`

### Route Registration
Routes are registered via the `register_kit_message_routes(app)` function, called from main routes initialization.

### Available Endpoints

#### 1. Send Kit Message
```
POST /api/kits/<kit_id>/messages
Authentication: Required (JWT)
Body:
{
  "subject": "string (required)",
  "message": "string (required)",
  "recipient_id": "integer (optional, null for broadcast)",
  "related_request_id": "integer (optional)",
  "attachments": "string (optional, comma-separated paths)"
}
Response: 201 Created
{
  "id": 123,
  "kit_id": 1,
  "sender_id": 5,
  "recipient_id": 10,
  "subject": "...",
  "message": "...",
  "is_read": false,
  "sent_date": "2025-11-07T...",
  "read_date": null,
  "attachments": "..."
}
```

#### 2. Get Kit Messages
```
GET /api/kits/<kit_id>/messages
Authentication: Required (JWT)
Query Parameters:
  - unread_only: boolean (default=false)
  - related_request_id: integer (optional filter)
Response: 200 OK - Array of message objects
Filtering:
  - Auto-filters by user role (sender, recipient, or broadcast)
  - Broadcast messages visible to all
```

#### 3. Get User's All Messages
```
GET /api/messages
Authentication: Required (JWT)
Query Parameters:
  - unread_only: boolean (default=false)
  - sent: boolean (default=false) - If true, returns sent messages
Response: 200 OK - Array of message objects
Default: Returns received messages + broadcasts
```

#### 4. Get Message Details
```
GET /api/messages/<message_id>
Authentication: Required (JWT)
Response: 200 OK - Message object with full details
Authorization:
  - Sender can view
  - Recipient can view
  - Any user can view broadcast messages
Includes:
  - Reply count
  - List of replies if include_replies=true
```

#### 5. Mark Message as Read
```
PUT /api/messages/<message_id>/read
Authentication: Required (JWT)
Response: 200 OK - Updated message object
Authorization:
  - Only recipient can mark as read
  - Sets is_read=true and read_date=current_time
```

#### 6. Reply to Message
```
POST /api/messages/<message_id>/reply
Authentication: Required (JWT)
Body:
{
  "message": "string (required)",
  "attachments": "string (optional)"
}
Response: 201 Created - New reply message object
Behavior:
  - Creates new message with parent_message_id set
  - Subject auto-prefixed with "Re: "
  - Reply sent to original message sender (or recipient if replying to own)
```

#### 7. Get Unread Count
```
GET /api/messages/unread-count
Authentication: Required (JWT)
Response: 200 OK
{
  "unread_count": 5
}
Includes: Unread messages + unread broadcasts
```

#### 8. Delete Message
```
DELETE /api/messages/<message_id>
Authentication: Required (JWT)
Response: 200 OK - Success message
Authorization:
  - Sender can delete
  - Recipient can delete
Note: Currently hard-deletes, not soft-delete
```

### Error Handling
- **400**: Validation errors (missing fields, unauthorized access)
- **401**: Unauthenticated requests
- **404**: Message or kit not found

---

## 3. Frontend Components & UI

### Main Components

#### 1. KitMessaging Component
**Location:** `/frontend/src/components/kits/KitMessaging.jsx`

**Features:**
- Inbox/Sent view toggle
- Unread message badge
- Reply interface with modal
- New message composition
- Message threading display
- Auto-refresh on send

**State Management:**
- Redux store (`kitMessagesSlice`)
- Local component state for modals and form data

**Key Functions:**
- `fetchKitMessages()` - Load messages for a kit
- `sendMessage()` - Compose and send new message
- `replyToMessage()` - Send reply to existing message
- `markMessageAsRead()` - Mark as read
- Message filtering by sender/recipient

#### 2. SendMessageModal Component
**Location:** `/frontend/src/components/kits/SendMessageModal.jsx`

**Features:**
- Modal-based message composition
- Form validation (required fields)
- Subject auto-prefill with kit name
- User ID input for recipient selection
- Broadcast option (leave recipient empty)
- Success/error messaging
- Loading state during send

**Props:**
- `show` - Modal visibility
- `onHide` - Dismiss handler
- `kitId` - Associated kit ID
- `kitName` - Kit display name

### Redux State Management

**Location:** `/frontend/src/store/kitMessagesSlice.js`

**State Structure:**
```javascript
{
  messages: {},           // Object keyed by kitId
  currentMessage: null,   // Selected message details
  unreadCount: 0,         // Total unread count
  loading: false,         // Loading state
  error: null             // Error object
}
```

**Async Thunks:**
- `sendMessage({ kitId, data })`
- `fetchKitMessages({ kitId, filters })`
- `fetchUserMessages(filters)`
- `fetchMessageById(id)`
- `markMessageAsRead(id)`
- `replyToMessage({ id, data })`
- `fetchUnreadCount()`

### UI Libraries
- **React Bootstrap**: Cards, ListGroups, Modals, Forms
- **React Icons** (Font Awesome): FaEnvelope, FaReply, FaPaperPlane, etc.
- **Redux Toolkit**: State management

---

## 4. Real-Time Implementation (Current State)

### Current Limitations
**No real-time/WebSocket implementation exists**

The system uses:
- **REST polling** (manual refresh required)
- **User-initiated actions** only
- No server push notifications
- No live message updates

### Search Results
Searched entire codebase for WebSocket/Socket.io:
- No Socket.io dependencies
- No WebSocket event handlers
- No real-time event listeners
- Only found references in dependency documentation (webpack, werkzeug)

### Implication
Users must:
1. Manually refresh to see new messages
2. Switch between inbox/sent views
3. Cannot receive live notifications
4. No presence indicators

---

## 5. File Upload/Attachment Handling

### Current Implementation

#### Attachment Storage
**Model Field:** `KitMessage.attachments`
- Stores as string (JSON format expected)
- Holds comma-separated file paths
- Example: `/uploads/photo1.jpg,/uploads/photo2.jpg`

#### File Validation Utilities
**Location:** `/backend/utils/file_validation.py`

**Supported File Types:**
```python
# Images
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/gif"}
IMAGE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": (".png", "image/png"),
    b"\xff\xd8\xff": (".jpg", "image/jpeg"),
    b"GIF87a": (".gif", "image/gif"),
    b"GIF89a": (".gif", "image/gif"),
}

# Certificates
ALLOWED_CERTIFICATE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

# CSV Files
ALLOWED_CSV_MIME_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "text/plain",
    "application/octet-stream"
}
```

**Size Limits:**
```python
DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_AVATAR_FILE_SIZE = 5 * 1024 * 1024   # 5MB
MAX_CALIBRATION_CERTIFICATE_FILE_SIZE = 5 * 1024 * 1024
```

**Validation Functions:**
- `_ensure_size_within_limit(stream, max_size)` - Check file size
- `_read_bytes(stream, max_bytes)` - Read file signature
- `_validate_file()` - Full validation pipeline
- Magic byte detection for image files
- CSV formula injection prevention (DANGEROUS_CSV_PREFIXES check)

#### Frontend Integration
**Current State:** **Partial/Not Fully Utilized**

The `attachments` field in `KitMessage.jsx` is prepared but:
- No file upload UI component in SendMessageModal
- No attachment display in message view
- No drag-and-drop support
- Attachments support exists in API (test shows it works)

**Test Coverage:**
`/backend/tests/test_routes_kit_messages.py` lines 190-206:
```python
def test_send_message_with_attachments(self):
    """Test sending message with attachments"""
    message_data = {
        "attachments": "/uploads/photo1.jpg,/uploads/photo2.jpg"
    }
    response = client.post(..., json=message_data, headers=...)
    assert response.status_code == 201
    assert data["attachments"] == "/uploads/photo1.jpg,/uploads/photo2.jpg"
```

### Attachment Recommendations
1. **Backend is ready** - Validation utilities exist
2. **Frontend needs UI** - No file picker implemented
3. **Storage path** - Uses `/uploads/` directory (configurable)
4. **Security** - File validation in place

---

## 6. Message Display & Chat UI Components

### Current UI Components

#### KitMessaging Card Layout
```
┌─────────────────────────────────────┐
│ Messages  [New Message Button]      │
├─────────────────────────────────────┤
│ [Inbox] [Sent] buttons              │
├─────────────────────────────────────┤
│ Message List (ListGroup)            │
│ ├─ [Envelope Icon] Subject          │
│ │  From: Sender Name • Timestamp    │
│ │  Message preview (truncated)      │
│ │  [Reply Button]                   │
│ ├─ [Envelope Icon] Subject 2        │
│ │  ...                              │
│ └─ No messages (empty state)        │
└─────────────────────────────────────┘
```

#### Message List Item Features
- **Read Status Icon**: FaEnvelope (unread) vs FaEnvelopeOpen (read)
- **Reply Badge**: Shown for threaded replies
- **Sender/Recipient**: Displayed as "From:" or "To:"
- **Timestamp**: ISO formatted, displayed with locale string
- **Preview**: First ~200 chars of message
- **Reply Button**: Only in inbox view

#### Compose Modal
```
┌──────────────────────────────────────┐
│ New Message            [Close Button]│
├──────────────────────────────────────┤
│ Subject *                            │
│ [________________]                   │
│ Recipient (Optional)                 │
│ [________________]                   │
│ Message *                            │
│ [_________________________]           │
│ [_________________________]           │
│ [_________________________]           │
│                                      │
│ [Cancel] [Send Message]              │
└──────────────────────────────────────┘
```

#### Reply Modal
```
┌──────────────────────────────────────┐
│ Reply to: {subject}    [Close Button]│
├──────────────────────────────────────┤
│ Original Message:                    │
│ ┌────────────────────────────────┐  │
│ │ [message text preview]         │  │
│ │ From: Sender • Timestamp       │  │
│ └────────────────────────────────┘  │
│ Your Reply *                        │
│ [_________________________]          │
│ [_________________________]          │
│                                      │
│ [Cancel] [Send Reply]                │
└──────────────────────────────────────┘
```

### Visual Indicators
- **Bold Text**: Unread messages
- **Icon Color**: Primary (unread), Muted (read)
- **Truncation**: Message text limited to single line
- **Loading State**: Spinner on send button
- **Error Messages**: Alert boxes (danger variant)
- **Success Messages**: Alert boxes (success variant)

### Accessibility Features
- Form validation feedback
- Semantic HTML (Form, ListGroup, Button)
- Icon labels via React-icons
- Disabled states during loading

---

## 7. System Architecture Overview

### Technology Stack

#### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM (supports PostgreSQL, MySQL, SQLite)
- **Authentication**: JWT (JSON Web Tokens)
- **Database Models**: 
  - `KitMessage` - Main message model
  - `User` - Sender/recipient
  - `Kit` - Message context
  - `KitReorderRequest` - Optional context

#### Frontend
- **Framework**: React 18+
- **State Management**: Redux Toolkit
- **API Client**: Axios (via api service)
- **UI Library**: React Bootstrap
- **Icons**: React-Icons (FontAwesome)

#### API Communication
**Service:** `/frontend/src/services/api.js`
```javascript
API Base: `/api/`
Auth Header: `Authorization: Bearer {token}`
CORS: Configured for localhost:5173
```

### Data Flow

```
User Action (React Component)
    ↓
Redux Dispatch (kitMessagesSlice.js)
    ↓
API Call (services/api.js)
    ↓
Flask Route Handler (routes_kit_messages.py)
    ↓
Database Query (SQLAlchemy)
    ↓
JSON Response
    ↓
Redux Reducer
    ↓
Component Re-render
```

### Messaging Workflow

#### Sending a Message
1. User opens SendMessageModal
2. Fills in subject, message, optional recipient_id
3. Frontend validates form
4. Dispatches `sendMessage()` action
5. API POST to `/api/kits/<id>/messages`
6. Backend validates & saves to database
7. Returns 201 with message object
8. Redux updates `messages[kitId]` state
9. Modal closes, success message shown
10. Message appears in list

#### Receiving a Message
1. User navigates to kit or refreshes manually
2. Dispatches `fetchKitMessages({ kitId })`
3. API GET to `/api/kits/<id>/messages`
4. Backend filters by user role
5. Returns all visible messages
6. Redux updates state
7. Component renders message list

#### Reading a Message
1. User clicks message in list
2. Message marked as read (optional)
3. Dispatches `markMessageAsRead(id)`
4. API PUT to `/api/messages/<id>/read`
5. Backend updates is_read=true, sets read_date
6. Redux updates unreadCount

---

## 8. Testing Coverage

**Location:** `/backend/tests/test_routes_kit_messages.py` (726 lines)

### Test Categories

#### TestSendKitMessage (259 lines)
- ✓ Send message to specific user
- ✓ Send broadcast message (null recipient)
- ✓ Send message linked to reorder request
- ✓ Send message with attachments
- ✓ Validation: missing subject
- ✓ Validation: missing message
- ✓ Error: kit not found
- ✓ Error: unauthenticated

#### TestGetKitMessages (82 lines)
- ✓ Get messages as sender
- ✓ Get messages as recipient
- ✓ Broadcast messages visible to all
- ✓ Filter for unread only
- ✓ Filter by related request
- ✓ Error: kit not found
- ✓ Error: unauthenticated

#### TestGetUserMessages (50 lines)
- ✓ Get received messages
- ✓ Get sent messages (sent=true filter)
- ✓ Filter unread only
- ✓ Broadcast messages included
- ✓ Error: unauthenticated

#### TestGetMessageById (75 lines)
- ✓ Get message as sender
- ✓ Get message as recipient
- ✓ Get message with replies
- ✓ Authorization check
- ✓ Broadcast messages accessible
- ✓ Error: not found
- ✓ Error: unauthenticated

#### TestMarkMessageRead (60 lines)
- ✓ Mark as read by recipient
- ✓ Already read message
- ✓ Non-recipient cannot mark as read
- ✓ Broadcast message read
- ✓ Error: not found
- ✓ Error: unauthenticated

#### TestReplyToMessage (85 lines)
- ✓ Reply to message
- ✓ Reply with attachments
- ✓ Reply to own message (recipient swap)
- ✓ Validation: missing message
- ✓ Error: parent not found
- ✓ Error: unauthenticated

#### TestGetUnreadCount (45 lines)
- ✓ Get unread count
- ✓ Count after reading
- ✓ Broadcast messages included
- ✓ Error: unauthenticated

#### TestDeleteMessage (49 lines)
- ✓ Delete by sender
- ✓ Delete by recipient
- ✓ Unauthorized user cannot delete
- ✓ Error: not found
- ✓ Error: unauthenticated

---

## 9. Known Limitations & Gaps

### Major Gaps
1. **No Real-Time Updates**
   - Manual refresh required
   - No WebSocket/Socket.io
   - No server push notifications
   - No presence indicators

2. **Incomplete File Attachment Support**
   - Backend validation ready
   - Frontend has no UI component
   - No upload handler endpoint
   - No download/preview functionality

3. **Limited Recipient Selection**
   - Manual user ID entry (poor UX)
   - No user picker/dropdown
   - No multi-recipient support
   - No distribution lists/teams

4. **No Message Archival**
   - No soft delete implementation
   - Hard delete only
   - No retention policies
   - No message export

5. **Missing UI Polish**
   - No message search
   - No sorting options
   - No filtering by date range
   - No conversation threading UI
   - No message reactions/emojis
   - No typing indicators

### Minor Gaps
- No message editing (create only)
- No message preview on hover
- No keyboard shortcuts
- No notification badges in app header
- No email notifications
- No message templates
- No bulk actions (delete multiple)
- No unread indicators in sidebar

---

## 10. Configuration & Deployment

### Flask Configuration
**Location:** `/backend/config.py`

**Relevant Settings:**
```python
# File uploads
MAX_AVATAR_FILE_SIZE = 5 * 1024 * 1024
MAX_BULK_IMPORT_FILE_SIZE = 5 * 1024 * 1024
MAX_CALIBRATION_CERTIFICATE_FILE_SIZE = 5 * 1024 * 1024

# CORS
CORS_ORIGINS = ["http://localhost:5173"]  # Frontend URL
CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
CORS_SUPPORTS_CREDENTIALS = False

# Session (JWT used instead)
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = instance/flask_session
```

### Frontend Environment
**Location:** `/frontend/.env` (example)
```
VITE_API_URL=http://localhost:5000/api
VITE_ASSET_PATH=/
```

### Database
- Supports: PostgreSQL, MySQL, SQLite
- Uses SQLAlchemy ORM
- Migrations: Alembic (if configured)
- Transaction support: Full ACID compliance

---

## 11. Enhancement Opportunities

### Priority 1: Real-Time Messaging
```
Benefits: Better UX, Live collaboration
Effort: High
Options:
1. WebSocket via Socket.io (full real-time)
2. Server-Sent Events (SSE) (simpler, unidirectional)
3. GraphQL Subscriptions (modern approach)
```

### Priority 2: File Attachments UI
```
Benefits: Full attachment workflow
Effort: Medium
Implementation:
1. Add file input to SendMessageModal
2. Implement upload handler
3. Display attachments in message view
4. Add download/preview
```

### Priority 3: User Experience
```
Benefits: Better usability
Effort: Low-Medium
Items:
1. User picker dropdown (no manual ID entry)
2. Message search
3. Conversation view (threaded)
4. Read receipts
5. Typing indicators
```

### Priority 4: Message Management
```
Benefits: Better data governance
Effort: Medium
Items:
1. Message archival/soft delete
2. Retention policies
3. Export functionality
4. Message editing
5. Bulk actions
```

---

## 12. Security Considerations

### Current Protections
- ✓ JWT authentication required
- ✓ Authorization checks (sender/recipient)
- ✓ File validation (magic bytes, MIME type)
- ✓ SQL injection protection (SQLAlchemy ORM)
- ✓ CORS configuration
- ✓ File size limits (5MB)
- ✓ CSV formula injection prevention

### Recommendations
1. Implement rate limiting on message endpoints
2. Add message encryption at rest (optional)
3. Add audit logging for deleted messages
4. Implement attachment virus scanning
5. Add message retention policies
6. Consider end-to-end encryption for sensitive messages

---

## 13. Summary Table

| Component | Status | Technology | Location |
|-----------|--------|-----------|----------|
| Database Model | ✓ Complete | SQLAlchemy | models_kits.py |
| API Routes | ✓ Complete | Flask | routes_kit_messages.py |
| Frontend Components | ⚠️ Partial | React | components/kits/ |
| State Management | ✓ Complete | Redux Toolkit | store/kitMessagesSlice.js |
| Real-Time | ✗ Missing | None | — |
| File Attachments | ⚠️ Backend Only | Flask | utils/file_validation.py |
| Authentication | ✓ Complete | JWT | auth/jwt_manager.py |
| Testing | ✓ Comprehensive | Pytest | tests/ |
| UI Components | ⚠️ Basic | React Bootstrap | components/kits/ |

---

## Conclusion

The messaging system is **functionally complete for basic use cases** but lacks modern features like real-time updates and full file attachment support. The architecture is well-designed, properly tested, and ready for enhancement. The backend is production-ready; the frontend would benefit from UX improvements and real-time capabilities.

**Recommendation:** Start with Priority 1 (Real-time) for better user experience, then address file attachments UI for complete functionality.
