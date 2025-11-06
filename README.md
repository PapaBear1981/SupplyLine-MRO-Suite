# SupplyLine MRO Suite

A comprehensive, secure, and scalable Maintenance, Repair, and Operations (MRO) management system built with modern technologies and containerized deployment.

**Current Version: 5.1.0 - Barcode System Refactoring & Inventory Enhancements** - See [RELEASE_NOTES.md](RELEASE_NOTES.md) for complete version history and release notes.

## 🚀 Version 5.1.0 - Barcode System Refactoring & Inventory Enhancements

This release introduces a professional PDF-based barcode system, kit-only expendables management, child lot tracking for partial chemical issuances, and numerous UI/UX improvements. The barcode system has been completely refactored to use WeasyPrint for magazine-quality labels with support for multiple label sizes.

### Key Highlights

- **🏷️ Professional Barcode System**: PDF-based labels with WeasyPrint, 4 label sizes, vector graphics (SVG)
- **📦 Kit-Only Expendables**: Direct consumable management within kits without warehouse overhead
- **🧬 Child Lot Tracking**: Automatic child lot creation for partial chemical issuances with full lineage tracking
- **📊 Enhanced UI/UX**: Sortable tables, improved dark mode, better tool location display
- **🔧 Code Quality**: Migrated from flake8 to Ruff for faster linting and modern Python practices
- **🐛 Critical Fixes**: Chemical inventory tracking, transfer logic, tool location display

### New Features in v5.1.0

#### 🏷️ Professional PDF-Based Barcode System
- **Magazine-Quality Labels**: WeasyPrint-generated PDFs with professional typography and design
- **Multiple Label Sizes**: 4x6, 3x4, 2x4, 2x2 inches with responsive content scaling
- **Vector Graphics**: SVG-based barcodes and QR codes for crisp printing at any resolution
- **Unified API**: Single endpoint pattern for tools, chemicals, expendables, and kit items
- **Future-Ready**: Designed for Zebra printer compatibility while supporting standard PDF printing
- **Automatic Printing**: Barcode modals appear after transfers and partial issuances for immediate labeling

#### 📦 Kit-Only Expendables System
- **Direct Kit Storage**: Add consumables directly to kits without warehouse management overhead
- **Full CRUD Operations**: Complete create, read, update, delete functionality via REST API
- **Lot/Serial Tracking**: Mutually exclusive lot or serial number validation
- **Auto-Complete Transfers**: Immediate feedback for warehouse-to-kit expendable transfers
- **Integrated Workflow**: Seamless integration with kit transfers and reorder systems

#### 🧬 Child Lot Tracking & Lineage
- **Automatic Child Lot Creation**: Partial chemical issuances automatically create child lots
- **Parent-Child Lineage**: Complete tracking of lot splits with parent_lot_number field
- **Lot Sequence Counter**: Track number of child lots created from each parent
- **Auto-Generated Lot Numbers**: Format LOT-YYMMDD-XXXX with atomic generation and row-level locking
- **Immediate Barcode Printing**: Automatic barcode modal for new child lots
- **Complete Audit Trail**: Full transaction history for lot splits and transfers

#### 📊 UI/UX Improvements
- **Sortable Tables**: Click column headers to sort in All Active Checkouts and Kit Items tables
- **Dark Mode Fixes**: Improved table header hover effects and theme consistency
- **Tool Location Display**: Tools now correctly show warehouse OR kit location (never both)
- **Pagination Support**: Handle large datasets efficiently with paginated tool lists
- **Theme Flash Prevention**: Inline script applies theme immediately on page load

### Technical Improvements

#### Backend Enhancements
- **Ruff Linting**: Migrated from flake8 to Ruff for 10x faster linting
- **Code Quality**: Auto-fixed thousands of linting issues (imports, quotes, whitespace)
- **Modern Python**: Includes pyupgrade and bugbear rules for best practices
- **Enhanced Transfer Logic**: Better distinction between KitExpendable and KitItem
- **Improved Reorder Fulfillment**: Modify existing expendables instead of creating duplicates

#### Frontend Enhancements
- **Centralized Barcode Service**: Single service for all barcode PDF generation
- **Component Updates**: Improved ChemicalBarcode, ToolBarcode, ExpendableBarcode components
- **Better State Management**: Enhanced Redux slices for transfers and inventory
- **React 19**: Updated to latest React version with improved performance

### Critical Bug Fixes

- **Chemical Inventory Tracking**: Fixed child lot quantities and status not updating after issuance
- **Transfer Logic**: Fixed expendable transfer validation and auto-completion issues
- **Tool Location**: Fixed tools showing in both warehouse and kit simultaneously
- **Reorder Fulfillment**: Fixed duplicate expendable creation during reorder fulfillment
- **Dark Mode**: Fixed table header hover effects and theme consistency issues

## Overview

This application provides a complete solution for managing tool and chemical inventories in aerospace maintenance environments. It allows for tracking tools, managing checkouts, monitoring chemical usage, and generating detailed reports. The system is designed with different user roles and permissions to ensure proper access control.

Built with modern security practices and designed for enterprise-scale deployments with comprehensive security hardening.

## Key Features

### Admin Dashboard (Enhanced in v3.1.0)
- **Real-time System Overview**: Dashboard with real-time data on users, tools, and checkouts
- **Performance Metrics**: Tool utilization rates, user activity rates, and checkout statistics
- **System Health Monitoring**: Server status, database connection, and system version information
- **Resource Visualization**: CPU, memory, and disk usage monitoring
- **Department Distribution**: Visual breakdown of users by department
- **Activity Tracking**: Recent system activities with detailed timestamps
- **Registration Management**: Streamlined approval/denial workflow for new user registrations

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
- **Child Lot Creation**: Automatic child lot generation for partial issuances with full lineage tracking
- **Lot Number Auto-Generation**: Format LOT-YYMMDD-XXXX with atomic generation
- **Archiving System**: Archive expired or depleted chemicals while maintaining history
- **Category Organization**: Organize chemicals by type (Sealant, Paint, Adhesive, etc.)

### Mobile Warehouse/Kits Management (v5.0.0+)
- **Aircraft Type Management**: Define and manage aircraft types (Q400, RJ85, CL415, etc.)
- **Kit Creation Wizard**: Guided 4-step process for creating new kits
- **Box System**: Numbered boxes with type constraints (expendable, tooling, consumable, loose, floor)
- **Item Tracking**: Track tools, chemicals, and expendables within kits
- **Issuance System**: Issue items from kits with work order tracking
- **Transfer System**: Kit-to-kit, kit-to-warehouse, warehouse-to-kit transfers
- **Automatic Reordering**: Trigger reorders on low stock or after issuance
- **Messaging System**: Communication between mechanics and stores personnel
- **Alerts & Notifications**: Low stock, expiring items, pending reorders
- **Analytics & Reporting**: Kit usage statistics and inventory reports

### Warehouse Management (v5.1.0+)
- **Warehouse Creation**: Create and manage multiple warehouse locations
- **Address Management**: Track warehouse addresses, city, state, zip code, country
- **Warehouse Types**: Main and satellite warehouse classifications
- **Inventory Tracking**: Track tools, chemicals, and expendables by warehouse
- **Transfer Management**: Complete audit trail for all warehouse transfers
- **Location Hierarchy**: Warehouses → Kits → Boxes for organized inventory

### Expendables Management (v5.1.0+)
- **Kit-Only Consumables**: Direct storage of expendables within kits without warehouse overhead
- **Full CRUD Operations**: Create, read, update, delete expendables via REST API
- **Lot/Serial Tracking**: Mutually exclusive lot or serial number validation
- **Auto-Complete Transfers**: Immediate feedback for warehouse-to-kit transfers
- **Integrated Workflow**: Seamless integration with kit transfers and reorder systems
- **Barcode Printing**: Professional PDF labels for all expendables

### Barcode & Label System (v5.1.0+)
- **Professional PDF Labels**: WeasyPrint-generated labels with magazine-quality design
- **Multiple Label Sizes**: 4x6, 3x4, 2x4, 2x2 inches with responsive scaling
- **Vector Graphics**: SVG-based barcodes and QR codes for crisp printing
- **Unified API**: Single endpoint pattern for all item types
- **Automatic Printing**: Barcode modals after transfers and partial issuances
- **QR Code Landing Pages**: Mobile-friendly pages with item details and calibration info
- **Future-Ready**: Designed for Zebra printer compatibility

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
- **React 19** - Modern UI framework with latest features
- **Redux Toolkit** - State management
- **React Router** - Client-side routing
- **React Bootstrap** - UI components
- **Axios** - HTTP client with JWT token management
- **Chart.js & Recharts** - Data visualization
- **Vite** - Fast build tool and development server

### Backend
- **Flask 2.2.3** - Python web framework
- **SQLite** - Lightweight database (default)
- **PostgreSQL** - Optional production database
- **Flask-SQLAlchemy** - ORM
- **Flask-CORS** - Cross-origin resource sharing
- **PyJWT 2.8.0** - JWT token authentication
- **Gunicorn** - WSGI HTTP server

### Deployment & Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server and reverse proxy
- **Multi-stage Docker builds** - Optimized container images

### Security & Authentication
- **JWT Tokens** - Stateless authentication
- **CSRF Protection** - Cross-site request forgery protection
- **Rate Limiting** - Brute force protection
- **Password Security** - History tracking and expiration
- **Secure Token Generation** - Cryptographically secure tokens

### Testing & Quality
- **Playwright** - End-to-end testing
- **Pytest** - Backend unit testing
- **ESLint** - Frontend code quality

## 🚀 Docker Deployment

### Prerequisites
- **Docker** and **Docker Compose** installed
- **Git** for version control
- At least 2GB of available RAM
- 5GB of available disk space

### Quick Start with Docker

The application is fully containerized and can be deployed with a single command:

```bash
# Clone the repository
git clone https://github.com/PapaBear1981/SupplyLine-MRO-Suite.git
cd SupplyLine-MRO-Suite

# Create environment file from template
cp .env.example .env

# Generate secure keys (REQUIRED)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))" >> .env
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))" >> .env

# Build and start the containers
docker-compose up -d

# Access the application at http://localhost
```

### Docker Deployment Features

The Docker deployment includes:
1. **Backend Container**: Flask API with SQLite database
2. **Frontend Container**: Nginx serving React application
3. **Persistent Volumes**: Database and session data preserved across restarts
4. **Health Checks**: Automatic container health monitoring
5. **Resource Limits**: CPU and memory constraints for stability
6. **Network Isolation**: Containers communicate on isolated network

### Docker Commands

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild containers after code changes
docker-compose up -d --build

# Remove all data (including database)
docker-compose down -v
```

### Production Deployment

For production deployments:
1. Update the `.env` file with production values
2. Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
3. Generate strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`
4. Configure appropriate `CORS_ORIGINS` for your domain
5. Consider using a reverse proxy (like Traefik or Nginx) for SSL/TLS
6. Set up regular database backups of the `database` volume

## Getting Started (Local Development)

### Prerequisites
- Node.js (v20+)
- Python (v3.11+)
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

See the **Docker Deployment** section above for complete instructions on deploying with Docker and Docker Compose.

### QR Code Configuration for External Devices

By default, QR codes generated by the system use `localhost` URLs, which only work on the same machine. To make QR codes scannable from phones and other external devices:

1. **Find your server's network IP address**:
   ```bash
   # On Windows
   ipconfig
   # Look for "IPv4 Address" under your active network adapter

   # On macOS/Linux
   ifconfig
   # or
   ip addr show
   ```

2. **Set the PUBLIC_URL environment variable**:
   ```bash
   # In your .env file, add:
   PUBLIC_URL=http://192.168.1.100:5000
   # Replace 192.168.1.100 with your actual IP address
   ```

3. **Restart the backend server** for the changes to take effect.

4. **Test the QR code**: Generate a QR code for a tool or chemical, scan it with your phone, and verify it opens the correct page.

**Note**: For production deployments, use your domain name instead:
```bash
PUBLIC_URL=https://yourdomain.com
```

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

#### Tool Calibration Management (New in v3.5.0)
1. Navigate to the "Calibration" page
2. To add a tool for calibration:
   - Click "Add Tool to Calibration"
   - Select the tool from the dropdown
   - Set calibration interval (days)
   - Set next calibration date
   - Add calibration standards used
   - Click "Save"
3. To record a calibration:
   - Find the tool in the calibration list
   - Click "Record Calibration"
   - Enter calibration date
   - Select calibration standards used
   - Add calibration results and notes
   - Upload calibration certificate (optional)
   - Click "Save"
4. To view calibration history:
   - Click on the tool name in the calibration list
   - View complete calibration history with dates and results

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
   - Calibration Status Report (New in v3.5.0)
4. Apply any filters as needed
5. View the report or export to PDF/Excel

#### Calibration Reports (New in v3.5.0)
1. Navigate to the "Reports & Analytics" page
2. Select "Calibration Reports" tab
3. Choose the report type:
   - Due Soon Report (tools due for calibration in the next 30 days)
   - Overdue Report (tools past their calibration due date)
   - Calibration History Report (complete calibration history)
   - Standards Usage Report (which standards were used for calibrations)
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

### Updating to the Latest Version (v3.5.3)
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

4. For tool calibration features added in v3.5.0, run:
   ```bash
   python migrate_calibration.py
   ```

5. Restart the application:
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
│   ├── routes_calibration.py     # Tool calibration routes
│   ├── routes_reports.py         # Reporting routes
│   ├── routes_users.py           # User management routes
│   ├── config.py                 # Configuration
│   ├── migrate_chemicals.py      # Chemical database migration script
│   ├── migrate_calibration.py    # Calibration database migration script
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
│   │   │   ├── calibration/      # Tool calibration components
│   │   │   │   ├── CalibrationList.jsx         # List of tools requiring calibration
│   │   │   │   ├── CalibrationForm.jsx         # Form for recording calibrations
│   │   │   │   ├── CalibrationHistory.jsx      # Calibration history view
│   │   │   │   └── CalibrationStandards.jsx    # Calibration standards management
│   │   │   ├── chemicals/        # Chemical management components
│   │   │   ├── layout/           # Layout components
│   │   │   ├── reports/          # Reporting components
│   │   │   │   ├── ChemicalWasteAnalytics.jsx  # Chemical waste analytics
│   │   │   │   ├── PartNumberAnalytics.jsx     # Part number analytics
│   │   │   │   ├── CalibrationReports.jsx      # Calibration reports
│   │   │   │   └── ...                         # Other report components
│   │   │   ├── tools/            # Tool management components
│   │   │   └── users/            # User management components
│   │   ├── pages/                # Page components
│   │   │   ├── CalibrationPage.jsx # Tool calibration management page
│   │   │   ├── ChemicalsPage.jsx # Chemicals management page
│   │   │   ├── ReportingPage.jsx # Reporting and analytics page
│   │   │   ├── ToolsPage.jsx     # Tool management page
│   │   │   └── ...               # Other pages
│   │   ├── services/             # API services
│   │   │   ├── api.js            # Base API configuration
│   │   │   ├── authService.js    # Authentication service
│   │   │   ├── calibrationService.js # Calibration management service
│   │   │   ├── chemicalService.js # Chemical management service
│   │   │   ├── reportService.js  # Reporting service
│   │   │   ├── toolService.js    # Tool management service
│   │   │   └── userService.js    # User management service
│   │   ├── store/                # Redux store
│   │   │   ├── authSlice.js      # Authentication state
│   │   │   ├── calibrationSlice.js # Calibration management state
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
├── docker-compose.yml            # Docker Compose configuration
├── .env.example                  # Example environment variables
├── DOCKER_README.md              # Docker deployment instructions
├── CHANGELOG.md                  # Version history and release notes
├── README.md                     # This file
├── update_tools_schema.py        # Tool database schema update script
├── migrate_chemicals.py          # Chemical database migration script
└── migrate_calibration.py        # Calibration database migration script
```

## Testing

Run the automated test suites to validate JWT authentication and overall functionality.

### Backend Unit Tests

```bash
cd backend
python -m pytest tests/ -v
```

These tests verify login, protected routes, and the refresh token flow.

### End-to-End Tests

```bash
cd frontend
npm run test:e2e
```

Playwright tests inject JWT tokens to emulate authenticated users.

## Enhanced Admin Dashboard (v3.1.0)

Version 3.1.0 introduces significant improvements to the Admin Dashboard, providing administrators with comprehensive system insights and enhanced user management capabilities:

### Real-time Data Integration
- **Live System Metrics**: Dashboard now displays real-time data from the backend instead of fallback data
- **Comprehensive Overview**: At-a-glance view of users, tools, checkouts, and system health
- **Performance Analytics**: Advanced metrics including tool utilization rates and user activity rates

### System Health Monitoring
- **Server Status**: Real-time monitoring of server availability and performance
- **Database Connection**: Database health and connection status monitoring
- **System Version**: Current version information with update notifications
- **Resource Utilization**: CPU, memory, and disk usage visualization

### Registration Management
- **Streamlined Workflow**: Improved interface for managing user registration requests
- **Approval/Denial Process**: Enhanced workflow for reviewing and processing registration requests
- **Detailed Feedback**: Better notification system for registration status changes
- **Historical Tracking**: Complete history of registration approvals and denials

### Activity Visualization
- **Department Distribution**: Interactive pie chart showing user distribution by department
- **Activity Timeline**: Graphical representation of system activity over time
- **Recent Actions Log**: Detailed log of recent system activities with timestamps

These enhancements provide administrators with powerful tools for monitoring system health, managing users, and optimizing resource utilization.

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
