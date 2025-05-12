# SupplyLine MRO Suite

A comprehensive inventory management system for tools and chemicals built with React and Flask, designed for aerospace maintenance operations.

**Current Version: 2.4.0** - See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## Overview

This application provides a complete solution for managing tool and chemical inventories in aerospace maintenance environments. It allows for tracking tools, managing checkouts, monitoring chemical usage, and generating detailed reports. The system is designed with different user roles and permissions to ensure proper access control.

## Key Features

### User Management
- **Authentication & Authorization**: Secure login system with role-based access control
- **User Profiles**: Customizable user profiles with avatar/picture upload
- **Department-Based Permissions**: Different access levels for Maintenance, Materials, and Admin users
- **Activity Tracking**: Comprehensive logging of user actions for accountability
- **User Status Management**: Ability to activate/deactivate users while preserving transaction history

### Tool Management
- **Comprehensive Inventory**: Track tools by tool number, serial number, description, and location
- **Multiple Serial Numbers**: Support for multiple tools with the same tool number but different serial numbers
- **Tool Categories**: Organize tools by categories (CL415, RJ85, Q400, Engine, CNC, Sheetmetal, General)
- **Checkout System**: Track tool checkouts and returns with expected return dates
- **Service Status Tracking**: Monitor tools in maintenance or permanently removed from service
- **Service History**: Complete history of tool maintenance and status changes
- **Location Tracking**: Keep track of tool locations and movements

### Chemical Management
- **Chemical Inventory**: Track chemicals by part number, lot number, manufacturer, and location
- **Expiration Tracking**: Monitor chemical expiration dates with automatic status updates
- **Quantity Management**: Track chemical quantities with unit conversion support
- **Low Stock Alerts**: Automatic alerts when chemicals reach minimum stock levels
- **Issuance Tracking**: Record chemical issuances by user, quantity, location, and purpose
- **Archiving System**: Archive expired or depleted chemicals while maintaining history
- **Category Organization**: Organize chemicals by type (Sealant, Paint, Adhesive, etc.)

### Reporting & Analytics
- **Tool Reports**: Generate reports on tool inventory, checkout history, and department usage
- **Chemical Waste Analytics**: Analyze chemical waste by category, location, and reason
- **Part Number Analytics**: Detailed analytics for specific chemical part numbers
- **Usage Tracking**: Track chemical usage by location, user, and time period
- **Shelf Life Analytics**: Analyze average shelf life and usage percentage by part number
- **Data Visualization**: Interactive charts and graphs for better data interpretation
- **Export Options**: Export reports to PDF and Excel formats

### User Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Light/Dark Theme**: User-selectable interface theme
- **Full-Page Layout**: Optimized for maximum screen usage
- **Modal Interfaces**: Efficient pop-up interfaces for common actions
- **Real-time Updates**: Dynamic updates without page refreshes

## Tech Stack

### Frontend
- React
- Redux Toolkit
- React Router
- React Bootstrap
- Axios
- Nginx (for production deployment)

### Backend
- Flask
- SQLite
- Flask-SQLAlchemy
- Flask-CORS
- Flask-Session
- Gunicorn (for production deployment)

### Deployment
- Docker
- Docker Compose
- Nginx (as reverse proxy)

## Getting Started

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- npm or yarn
- Docker and Docker Compose (for containerized deployment)

### Installation

#### Option 1: Local Development Setup

##### Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

##### Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

#### Option 2: Docker Deployment

The application can be easily deployed using Docker and Docker Compose:

```bash
# Clone the repository
git clone https://github.com/PapaBear1981/Basic_inventory.git
cd Basic_inventory

# Create a .env file from the example
cp .env.example .env

# Build and start the containers
docker-compose up -d

# Access the application at http://localhost
```

For more detailed instructions on Docker deployment, see [DOCKER_README.md](DOCKER_README.md).

## Usage Guide

### Accessing the Application
- **Local Development**: Access at http://localhost:5173 (Frontend) and http://localhost:5000 (API)
- **Docker Deployment**: Access at http://localhost (Frontend) and http://localhost:5000 (API)

### Default Credentials
- **Admin User**:
  - Employee Number: ADMIN001
  - Password: admin123
- **Materials User**:
  - Employee Number: MAT001
  - Password: materials123
- **Maintenance User**:
  - Employee Number: MAINT001
  - Password: maintenance123

### User Roles and Permissions

#### Admin Users
- Full access to all system features
- Can manage users, tools, and chemicals
- Can view all reports and analytics
- Can configure system settings

#### Materials Department Users
- Can manage tool inventory
- Can check out/check in tools to other users
- Can manage chemical inventory
- Can issue chemicals to locations
- Can view reports and analytics
- Can manage users (limited)

#### Maintenance Department Users
- Can view tool inventory
- Can check out tools for personal use
- Can view chemical inventory
- Cannot issue chemicals to others
- Limited access to reports

### Tool Management

#### Adding a New Tool
1. Navigate to the "Tools" page
2. Click "Add Tool" button
3. Fill in the required information:
   - Tool Number (e.g., HT001)
   - Serial Number (unique identifier)
   - Description
   - Category
   - Location
4. Click "Save" to add the tool to inventory

#### Checking Out a Tool
1. Navigate to the "Tools" page
2. Find the tool you want to check out
3. Click the "Checkout" button
4. Select the user who is checking out the tool
5. Set an expected return date
6. Click "Confirm Checkout"

#### Returning a Tool
1. Navigate to the "Active Checkouts" page
2. Find the checkout record for the tool
3. Click the "Return" button
4. Add any notes about the condition of the tool
5. Click "Confirm Return"

#### Tool Service Management
1. Navigate to the "Tools" page
2. Find the tool that needs service
3. Click the "Service" button
4. Select the service type:
   - Temporary Maintenance
   - Permanent Removal
5. Add required comments
6. Click "Confirm"

### Chemical Management

#### Adding a New Chemical
1. Navigate to the "Chemicals" page
2. Click "Add Chemical" button
3. Fill in the required information:
   - Part Number
   - Lot Number
   - Description
   - Manufacturer
   - Quantity and Unit
   - Location
   - Category
   - Expiration Date
   - Minimum Stock Level
4. Click "Save" to add the chemical to inventory

#### Issuing a Chemical
1. Navigate to the "Chemicals" page
2. Find the chemical you want to issue
3. Click the "Issue" button
4. Fill in the required information:
   - Quantity to issue
   - Location/Hangar where it will be used
   - User receiving the chemical
   - Purpose (optional)
5. Click "Confirm Issue"

#### Archiving a Chemical
1. Navigate to the "Chemicals" page
2. Find the chemical you want to archive
3. Click the "Archive" button
4. Select a reason for archiving:
   - Expired
   - Depleted
   - Other (with comments)
5. Click "Confirm Archive"

### Reporting and Analytics

#### Tool Reports
1. Navigate to the "Reports & Analytics" page
2. Select "Tool Reports" tab
3. Choose the report type:
   - Tool Inventory Report
   - Checkout History Report
   - Department Usage Report
4. Apply any filters as needed
5. View the report or export to PDF/Excel

#### Chemical Waste Analytics
1. Navigate to the "Reports & Analytics" page
2. Select "Chemical Waste Analytics" tab
3. Choose a timeframe (week, month, quarter, year, all)
4. Optionally filter by part number
5. View analytics on:
   - Waste by category
   - Waste by location
   - Waste by part number
   - Waste over time
   - Shelf life analytics

#### Part Number Analytics
1. Navigate to the "Reports & Analytics" page
2. Select "Part Number Analytics" tab
3. Choose a specific part number from the dropdown
4. View detailed analytics for that part number:
   - Inventory statistics
   - Usage by location
   - Usage over time
   - Waste statistics
   - Shelf life analytics

### User Management

#### Adding a New User
1. Navigate to the "Users" page (Admin or Materials users only)
2. Click "Add User" button
3. Fill in the required information:
   - Name
   - Employee Number
   - Department
   - Password
   - Admin Status
4. Click "Save" to create the user

#### Updating User Profile
1. Click on your username in the top-right corner
2. Select "Profile" from the dropdown
3. Update your information:
   - Upload a profile picture
   - Change password
   - Update personal details
4. Click "Save Changes"

### Updating to the Latest Version
If you're updating from a previous version, follow these steps:

1. Pull the latest changes from the repository:
   ```bash
   git pull origin master
   ```

2. Run the database schema update script:
   ```bash
   python update_tools_schema.py
   ```

3. For chemical tracking features added in v1.4.0 and later, run:
   ```bash
   python migrate_chemicals.py
   ```

4. Restart the application:
   ```bash
   # For local development
   # Backend
   cd backend
   python app.py

   # Frontend
   cd frontend
   npm run dev

   # For Docker deployment
   docker-compose down
   docker-compose up -d
   ```

## Project Structure

```
supplyline-mro-suite/
├── backend/                      # Flask backend
│   ├── app.py                    # Main application entry point
│   ├── models.py                 # Database models
│   ├── routes.py                 # Main API routes
│   ├── routes_chemicals.py       # Chemical management routes
│   ├── routes_reports.py         # Reporting routes
│   ├── routes_users.py           # User management routes
│   ├── config.py                 # Configuration
│   ├── migrate_chemicals.py      # Chemical database migration script
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker configuration for backend
│   ├── .dockerignore             # Files to ignore in Docker build
│   └── static/                   # Static files
│       ├── uploads/              # User uploaded files
│       └── avatars/              # User profile pictures
├── frontend/                     # React frontend
│   ├── public/                   # Public assets
│   ├── src/                      # Source code
│   │   ├── components/           # React components
│   │   │   ├── auth/             # Authentication components
│   │   │   ├── chemicals/        # Chemical management components
│   │   │   ├── layout/           # Layout components
│   │   │   ├── reports/          # Reporting components
│   │   │   │   ├── ChemicalWasteAnalytics.jsx  # Chemical waste analytics
│   │   │   │   ├── PartNumberAnalytics.jsx     # Part number analytics
│   │   │   │   └── ...                         # Other report components
│   │   │   ├── tools/            # Tool management components
│   │   │   └── users/            # User management components
│   │   ├── pages/                # Page components
│   │   │   ├── ChemicalsPage.jsx # Chemicals management page
│   │   │   ├── ReportingPage.jsx # Reporting and analytics page
│   │   │   ├── ToolsPage.jsx     # Tool management page
│   │   │   └── ...               # Other pages
│   │   ├── services/             # API services
│   │   │   ├── api.js            # Base API configuration
│   │   │   ├── authService.js    # Authentication service
│   │   │   ├── chemicalService.js # Chemical management service
│   │   │   ├── reportService.js  # Reporting service
│   │   │   ├── toolService.js    # Tool management service
│   │   │   └── userService.js    # User management service
│   │   ├── store/                # Redux store
│   │   │   ├── authSlice.js      # Authentication state
│   │   │   ├── chemicalsSlice.js # Chemical management state
│   │   │   ├── reportSlice.js    # Reporting state
│   │   │   ├── toolsSlice.js     # Tool management state
│   │   │   └── usersSlice.js     # User management state
│   │   ├── utils/                # Utility functions
│   │   ├── App.jsx               # Main App component
│   │   └── main.jsx              # Entry point
│   ├── package.json              # Node.js dependencies
│   ├── vite.config.js            # Vite configuration
│   ├── Dockerfile                # Docker configuration for frontend
│   ├── .dockerignore             # Files to ignore in Docker build
│   └── nginx.conf                # Nginx configuration for production
├── database/                     # SQLite database
│   └── tools.db                  # Main database file
├── flask_session/                # Flask session files
├── docker-compose.yml            # Docker Compose configuration
├── .env.example                  # Example environment variables
├── DOCKER_README.md              # Docker deployment instructions
├── CHANGELOG.md                  # Version history and release notes
├── README.md                     # This file
├── update_tools_schema.py        # Tool database schema update script
└── migrate_chemicals.py          # Chemical database migration script
```

## Application Rebranding (v2.2.0)

Version 2.2.0 introduces a complete rebranding of the application to "SupplyLine MRO Suite". This update includes:

- Renaming the application throughout the entire codebase
- Updating all user-facing interfaces with the new name
- Modernizing the application's identity to better reflect its comprehensive MRO (Maintenance, Repair, and Operations) capabilities
- Maintaining all existing functionality while presenting a more professional and industry-specific brand

## Advanced Chemical Reporting Features (v2.1.0)

Version 2.1.0 introduces significant enhancements to the chemical reporting system, providing detailed analytics for better inventory management and waste reduction:

### Part Number Tracking
- Track usage patterns for specific part numbers
- Monitor inventory levels across multiple lot numbers
- Analyze usage trends over time

### Waste Analytics
- Compare expired vs. depleted chemicals
- Track waste percentages by part number and category
- Identify patterns in chemical expiration

### Location-Based Analytics
- Monitor chemical usage by location/hangar
- Identify high-usage areas
- Optimize chemical distribution

### Shelf Life Optimization
- Track average shelf life by part number
- Calculate usage percentage before expiration
- Identify chemicals with short effective shelf life

### Usage Reporting
- Track chemical usage by user
- Monitor usage patterns over time
- Generate detailed usage reports by part number

These advanced reporting features help aerospace maintenance operations optimize their chemical inventory, reduce waste, and ensure compliance with regulatory requirements.

## System Requirements

### Minimum Requirements
- **CPU**: Dual-core processor, 2.0 GHz or higher
- **RAM**: 4 GB
- **Storage**: 1 GB free space
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Browser**: Chrome 90+, Firefox 90+, Edge 90+, Safari 14+

### Recommended Requirements
- **CPU**: Quad-core processor, 2.5 GHz or higher
- **RAM**: 8 GB
- **Storage**: 5 GB free space
- **Network**: Broadband internet connection
- **Display**: 1920x1080 resolution or higher

## Support and Contribution

For support, feature requests, or bug reports, please open an issue on the GitHub repository. Contributions are welcome through pull requests.

## License

MIT

## Acknowledgments

- React Bootstrap for UI components
- Chart.js for data visualization
- Flask for the backend API
- SQLite for database management
- Docker for containerization
