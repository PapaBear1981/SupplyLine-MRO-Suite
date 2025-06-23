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

## Default Admin User

A default admin user is created when the application starts:
- Employee Number: ADMIN001
- Password: admin123
