# Tool Inventory Management System - Backend

## What's New in 3.2.0
- Admin dashboard registration requests are now fully connected to the backend API.
- Approve and deny registration requests from the dashboard with live updates.
- Improved backend startup reliability (database directory checks).

## Setup and Running

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create the database directory if it doesn't exist:
   ```
   mkdir -p ../database
   ```
4. Run the backend server:
   ```
   python run.py
   ```

The server will start on http://localhost:5000

## API Endpoints

- Authentication:
  - POST /api/auth/login - Login with employee number and password
  - POST /api/auth/logout - Logout current user
  - GET /api/auth/status - Check authentication status
  - POST /api/auth/register - Register a new user
  
- Tools:
  - GET /api/tools - List all tools
  - POST /api/tools - Create a new tool (requires tool manager privileges)
  - GET /api/tools/:id - Get details for a specific tool
  
- Checkouts:
  - GET /api/checkouts - List all checkouts
  - POST /api/checkouts - Create a new checkout
  - POST /api/checkouts/:id/return - Return a checked out tool
  - GET /api/checkouts/user - Get current user's checkouts
  
- Users:
  - GET /api/users - List all users
  - POST /api/users - Create a new user
  
- Audit:
  - GET /api/audit - Get audit logs (requires admin privileges)

- Mobile Warehouses (Kits):
  - GET /api/kits - List all kits
  - POST /api/kits - Create a new kit (requires admin/materials privileges)
  - GET /api/kits/:id - Get kit details
  - PUT /api/kits/:id - Update kit (requires admin/materials privileges)
  - DELETE /api/kits/:id - Delete kit (requires admin privileges)
  - POST /api/kits/:id/duplicate - Duplicate kit as template
  - GET /api/kits/:id/items - List items in kit
  - POST /api/kits/:id/items - Add item to kit
  - PUT /api/kits/:id/items/:itemId - Update kit item
  - DELETE /api/kits/:id/items/:itemId - Remove item from kit
  - POST /api/kits/:id/issue - Issue items from kit
  - GET /api/kits/:id/issuances - Get issuance history
  - POST /api/kits/:id/reorder - Create reorder request
  - GET /api/kits/:id/alerts - Get kit alerts

- Aircraft Types:
  - GET /api/aircraft-types - List all aircraft types
  - POST /api/aircraft-types - Create aircraft type (requires admin privileges)
  - PUT /api/aircraft-types/:id - Update aircraft type (requires admin privileges)
  - DELETE /api/aircraft-types/:id - Deactivate aircraft type (requires admin privileges)

- Kit Transfers:
  - GET /api/transfers - List all transfers
  - POST /api/transfers - Create transfer
  - GET /api/transfers/:id - Get transfer details
  - PUT /api/transfers/:id/complete - Complete transfer
  - PUT /api/transfers/:id/cancel - Cancel transfer

- Kit Reorder Requests:
  - GET /api/reorder-requests - List all reorder requests
  - GET /api/reorder-requests/:id - Get request details
  - PUT /api/reorder-requests/:id/approve - Approve request (requires admin/materials privileges)
  - PUT /api/reorder-requests/:id/fulfill - Mark request fulfilled
  - PUT /api/reorder-requests/:id/cancel - Cancel request

- Kit Messages:
  - GET /api/messages - Get user's messages
  - POST /api/kits/:id/messages - Send message
  - GET /api/kits/:id/messages - Get messages for kit
  - GET /api/messages/:id - Get message details
  - PUT /api/messages/:id/read - Mark message as read
  - POST /api/messages/:id/reply - Reply to message

- Kit Reports:
  - GET /api/kits/reports/inventory - Inventory report
  - GET /api/kits/reports/issuances - Issuance history report
  - GET /api/kits/reports/transfers - Transfer history report
  - GET /api/kits/reports/reorders - Reorder status report
  - GET /api/kits/analytics/utilization - Kit utilization analytics

## Default Admin User

A default admin user is created when the application starts:
- Employee Number: ADMIN001
- Password: admin123
