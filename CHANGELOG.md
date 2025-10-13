# Changelog

All notable changes to this project will be documented in this file.

## [5.0.0] - 2025-10-12 - Mobile Warehouse/Kits System

### 🚀 MAJOR FEATURE RELEASE

This release introduces the Mobile Warehouse (Kits) system, enabling tracking and management of mobile warehouses that follow aircraft to operating bases for maintenance operations.

### Added

#### Backend - Database & Models
- **9 New Database Models** for comprehensive kit management:
  - `AircraftType`: Manage aircraft types (Q400, RJ85, CL415) with admin controls
  - `Kit`: Main kit entity with aircraft type association and status tracking
  - `KitBox`: Box containers (expendable, tooling, consumable, loose, floor)
  - `KitItem`: Items transferred into kits (tools/chemicals) with quantity tracking
  - `KitExpendable`: Manually added expendables not linked to existing inventory
  - `KitIssuance`: Complete issuance tracking with work order integration
  - `KitTransfer`: Transfer system supporting kit-to-kit, kit-to-warehouse, warehouse-to-kit
  - `KitReorderRequest`: Automatic and manual reorder requests with approval workflow
  - `KitMessage`: Messaging system with threading, attachments, and read status
- **Database Migration Script** (`backend/migrate_kits.py`):
  - Creates all 9 tables with proper indexes and foreign keys
  - Seeds default aircraft types (Q400, RJ85, CL415)
  - Includes verification and rollback capability

#### Backend - API Endpoints (40+ new endpoints)
- **Kit Management** (`/api/kits`):
  - GET /api/kits - List all kits with filtering
  - POST /api/kits - Create new kit
  - GET /api/kits/:id - Get kit details
  - PUT /api/kits/:id - Update kit
  - DELETE /api/kits/:id - Delete kit (soft delete)
  - POST /api/kits/:id/duplicate - Duplicate kit as template
  - POST /api/kits/wizard - Multi-step kit creation wizard
- **Aircraft Type Management** (`/api/aircraft-types`) - Admin only:
  - GET /api/aircraft-types - List aircraft types
  - POST /api/aircraft-types - Create aircraft type
  - PUT /api/aircraft-types/:id - Update aircraft type
  - DELETE /api/aircraft-types/:id - Deactivate aircraft type
- **Box Management** (`/api/kits/:id/boxes`):
  - GET /api/kits/:id/boxes - List boxes
  - POST /api/kits/:id/boxes - Add box
  - PUT /api/kits/:id/boxes/:boxId - Update box
  - DELETE /api/kits/:id/boxes/:boxId - Remove box
- **Item Management** (`/api/kits/:id/items`):
  - GET /api/kits/:id/items - List items with filters
  - POST /api/kits/:id/items - Add item
  - PUT /api/kits/:id/items/:itemId - Update item
  - DELETE /api/kits/:id/items/:itemId - Remove item
- **Expendable Management** (`/api/kits/:id/expendables`):
  - GET /api/kits/:id/expendables - List expendables
  - POST /api/kits/:id/expendables - Add expendable
  - PUT /api/kits/:id/expendables/:id - Update expendable
  - DELETE /api/kits/:id/expendables/:id - Remove expendable
- **Issuance System** (`/api/kits/:id/issue`):
  - POST /api/kits/:id/issue - Issue items from kit
  - GET /api/kits/:id/issuances - Get issuance history
  - GET /api/kits/:id/issuances/:issuanceId - Get issuance details
  - Automatic reorder trigger on low stock
- **Transfer System** (`/api/transfers`):
  - POST /api/transfers - Initiate transfer
  - GET /api/transfers - List transfers with filters
  - GET /api/transfers/:id - Transfer details
  - PUT /api/transfers/:id/complete - Complete transfer
  - PUT /api/transfers/:id/cancel - Cancel transfer
- **Reorder Management** (`/api/reorder-requests`):
  - POST /api/kits/:id/reorder - Create reorder request
  - GET /api/reorder-requests - List all requests with filters
  - GET /api/reorder-requests/:id - Request details
  - PUT /api/reorder-requests/:id/approve - Approve request
  - PUT /api/reorder-requests/:id/order - Mark as ordered
  - PUT /api/reorder-requests/:id/fulfill - Mark as fulfilled
  - PUT /api/reorder-requests/:id/cancel - Cancel request
- **Messaging System** (`/api/messages`):
  - POST /api/kits/:id/messages - Send message
  - GET /api/kits/:id/messages - Get messages for kit
  - GET /api/messages - Get user's messages
  - GET /api/messages/:id - Message details
  - PUT /api/messages/:id/read - Mark as read
  - POST /api/messages/:id/reply - Reply to message
  - GET /api/messages/unread-count - Get unread count
- **Analytics & Reporting**:
  - GET /api/kits/:id/analytics - Kit usage statistics
  - GET /api/kits/reports/inventory - Inventory report
  - GET /api/kits/:id/alerts - Get alerts for kit

#### Frontend - State Management
- **Redux Slices**:
  - `kitsSlice.js`: Kit operations, wizard, analytics, alerts
  - `kitTransfersSlice.js`: Transfer operations with status tracking
  - `kitMessagesSlice.js`: Messaging with unread count tracking
- **Async Thunks**: 30+ async operations for all kit functionality
- **Error Handling**: Comprehensive error handling and loading states

#### Frontend - UI Components & Pages
- **KitsManagement Page**: Main dashboard with tabs (All, Active, Inactive, Alerts)
  - Search and filter by aircraft type
  - Kit cards showing status, aircraft type, item counts, alerts
  - Quick actions for create, view, messages
- **KitWizard Component**: 4-step guided kit creation
  - Step 1: Aircraft type selection
  - Step 2: Kit details (name, description)
  - Step 3: Box configuration
  - Step 4: Review and create
  - Progress indicator and validation
- **KitDetailPage**: Comprehensive kit detail view
  - Overview tab with kit information and statistics
  - Quick action buttons (Edit, Duplicate, Issue, Transfer, Reorder, Message)
  - Tabs for Items, Issuances, Transfers, Reorders, Messages
  - Alert display
- **KitItemsList Component**: Items display with filtering
  - Group by box with filters (box type, item type, status)
  - Item details with quantity, location, status badges
  - Action buttons for issue and transfer
- **KitAlerts Component**: Alert display system
  - Color-coded severity levels (high, medium, low)
  - Low stock alerts, pending reorders, unread messages
  - Dismissible alerts with action buttons
- **Navigation Integration**:
  - "Kits" link added to main navigation
  - Routes configured with protected route wrappers
  - Seamless integration with existing UI

### Features

#### Core Functionality
- ✅ **Aircraft Type Management**: Admin can manage aircraft types
- ✅ **Kit CRUD Operations**: Full create, read, update, delete for kits
- ✅ **Kit Wizard**: Guided 4-step kit creation process
- ✅ **Box System**: Numbered boxes with type constraints (expendable, tooling, consumable, loose, floor)
- ✅ **Item Tracking**: Track tools, chemicals, and expendables in kits
- ✅ **Issuance System**: Issue items with work order tracking
- ✅ **Transfer System**: Kit-to-kit, kit-to-warehouse, warehouse-to-kit transfers
- ✅ **Automatic Reordering**: Trigger reorders on low stock/issuance
- ✅ **Messaging**: Communication between mechanics and stores personnel
- ✅ **Alerts**: Low stock, expiring items, pending reorders notifications
- ✅ **Reporting**: Analytics and inventory reports

#### Security & Authorization
- **Department-based Access**: Materials department required for kit management
- **Admin Controls**: Aircraft type management restricted to admins
- **JWT Authentication**: All endpoints protected with JWT tokens
- **Audit Logging**: All kit operations logged for compliance

### Database Changes

#### New Tables (9)
1. `aircraft_types` - Aircraft type definitions
2. `kits` - Main kit records
3. `kit_boxes` - Box containers within kits
4. `kit_items` - Items in kits (tools/chemicals)
5. `kit_expendables` - Manually added expendables
6. `kit_issuances` - Issuance tracking
7. `kit_transfers` - Transfer records
8. `kit_reorder_requests` - Reorder requests
9. `kit_messages` - Messaging system

#### Indexes Added
- Performance indexes on all foreign keys
- Composite indexes for common queries
- Status and date indexes for filtering

### Migration Instructions

#### Database Migration
```bash
# Run the migration script
python backend/migrate_kits.py development

# For production
python backend/migrate_kits.py production
```

#### No Breaking Changes
- All existing functionality remains unchanged
- New feature is additive only
- No changes to existing database tables
- No changes to existing API endpoints

### Technical Details

#### Backend Architecture
- **Route Modules**: 4 new route files (`routes_kits.py`, `routes_kit_transfers.py`, `routes_kit_reorders.py`, `routes_kit_messages.py`)
- **Models**: 9 new SQLAlchemy models with proper relationships
- **Validation**: Comprehensive input validation and error handling
- **Logging**: Structured logging for all operations

#### Frontend Architecture
- **Redux Toolkit**: Modern state management with async thunks
- **React Router**: Protected routes with authentication
- **React-Bootstrap**: Consistent UI components
- **Component Composition**: Reusable components following existing patterns

### Known Limitations

#### Current Version
- Mobile interface not yet implemented (desktop only)
- Some advanced UI features pending (issuance/transfer forms)
- No automated tests yet (manual testing performed)
- Documentation in progress

#### Future Enhancements
- Real-time updates for messaging (WebSocket/polling)
- Barcode scanner integration for mobile
- Offline capability for field use
- Bulk operations for transfers
- Advanced reporting with charts

### Files Added

#### Backend
- `backend/models_kits.py` - Database models
- `backend/migrate_kits.py` - Migration script
- `backend/routes_kits.py` - Main kit routes
- `backend/routes_kit_transfers.py` - Transfer routes
- `backend/routes_kit_reorders.py` - Reorder routes
- `backend/routes_kit_messages.py` - Messaging routes

#### Frontend
- `frontend/src/store/kitsSlice.js` - Kit state management
- `frontend/src/store/kitTransfersSlice.js` - Transfer state
- `frontend/src/store/kitMessagesSlice.js` - Message state
- `frontend/src/pages/KitsManagement.jsx` - Main dashboard
- `frontend/src/pages/KitDetailPage.jsx` - Detail view
- `frontend/src/components/kits/KitWizard.jsx` - Creation wizard
- `frontend/src/components/kits/KitItemsList.jsx` - Items display
- `frontend/src/components/kits/KitAlerts.jsx` - Alert display

#### Documentation
- `mobile_warehouse_spec.txt` - Original specification
- `KITS_IMPLEMENTATION_STATUS.md` - Implementation tracking
- `IMPLEMENTATION_COMPLETE_SUMMARY.md` - Completion summary

### Acknowledgments
- Feature specification based on operational requirements for mobile maintenance operations
- Implementation follows existing codebase patterns and conventions
- Designed for scalability and future enhancements

---

## [4.0.0] - 2025-06-22 - AWS Production Beta

### 🚀 MAJOR RELEASE - BREAKING CHANGES

This is a major architectural release that migrates the SupplyLine MRO Suite to AWS cloud infrastructure with significant security and scalability improvements.

### Added
- **AWS Cloud Infrastructure**: Complete migration to AWS using ECS Fargate, RDS PostgreSQL, S3, CloudFront
- **JWT Authentication**: Modern token-based authentication system replacing session-based auth
- **AWS Secrets Manager**: Secure management of database passwords and JWT secrets
- **CloudFormation Templates**: Infrastructure as Code for reproducible deployments
- **GitHub Actions CI/CD**: Automated testing and deployment pipeline
- **Playwright Testing**: End-to-end browser testing integration
- **Security Enhancements**: CSRF protection, account lockout, audit logging
- **Auto-scaling**: ECS Fargate with Application Load Balancer
- **CDN**: CloudFront distribution for global performance
- **Container Registry**: Amazon ECR for secure Docker image management
- **VPC Security**: Private subnets with NAT Gateway for secure backend communication
- **SSL/TLS**: End-to-end encryption with AWS Certificate Manager
- **Health Monitoring**: Application health checks and CloudWatch logging
- **PyJWT 2.8.0**: Added JWT library for secure token management

### Changed
- **BREAKING**: Replaced Flask sessions with JWT token authentication
- **BREAKING**: Migrated from SQLite to PostgreSQL for production
- **BREAKING**: Updated API responses to include JWT token information
- **Database**: Production database now runs on Amazon RDS PostgreSQL
- **Frontend Deployment**: Now deployed to S3 with CloudFront CDN
- **Backend Deployment**: Now runs on ECS Fargate containers
- **Authentication Flow**: Complete overhaul to use access and refresh tokens
- **Security Model**: Enhanced with AWS IAM roles and policies
- **Environment Configuration**: New environment variables for AWS deployment

### Security
- **Critical Fix**: Resolved authentication bypass vulnerability (Issue #363)
- **Critical Fix**: Fixed privilege escalation security flaw (Issue #364)
- **Enhanced Admin Security**: Improved admin account creation and password reset
- **Secure Key Generation**: Automated secure key generation for production
- **Token Security**: JWT tokens with 15-minute access and 7-day refresh expiration
- **CSRF Protection**: Enhanced CSRF protection using JWT token secrets
- **Account Lockout**: Progressive lockout policy for failed login attempts

### Migration Notes
- **Data Migration Required**: Existing SQLite data must be migrated to PostgreSQL
- **User Re-authentication**: All users must log in again due to JWT migration
- **Environment Setup**: New AWS environment variables required
- **DNS Configuration**: Update DNS to point to new AWS infrastructure

### Deployment
- **One-Command Deployment**: `./scripts/deploy.sh` for complete AWS setup
- **Infrastructure Automation**: CloudFormation handles all AWS resource creation
- **Container Optimization**: Multi-stage Docker builds for smaller images
- **Automated Testing**: CI/CD pipeline with automated security and functionality tests

## [3.5.2] - 2025-05-19

### Fixed
- Fixed chemical dropdown menu issue (Issue #83)
  - Removed dropdown menu from chemical list to simplify interface
  - Removed dropdown menu toggle handler
  - Kept only essential buttons (View, Issue, and Barcode)
  - Improved user interface clarity and intuitiveness
- Fixed chemical issuance history endpoint (Issue #80)
  - Moved the chemical issuance history endpoint inside the register_chemical_routes function
  - Ensured proper API registration with the Flask application
  - Improved endpoint reliability and data retrieval
- Implemented missing API endpoints for marking chemicals as ordered and delivered (Issue #79)
  - Added endpoint for marking chemicals as ordered with expected delivery date
  - Added endpoint for marking chemicals as delivered
  - Updated chemical reorder status tracking
- Implemented chemical issuance functionality (Issue #77)
  - Added missing API endpoint for issuing chemicals
  - Implemented proper validation for chemical issuance
  - Added logging for chemical issuance actions
- Enhanced Chemical Usage Analytics with real-time data (Issue #41)
  - Modified analytics to calculate usage based on actual issuance data
  - Added calculation for projected depletion time
  - Improved user display with actual user names
- Removed debug login functionality and debug endpoints (Issue #67)
  - Removed debug components and test files
  - Removed debug endpoints from chemical analytics
  - Enhanced application security

## [3.5.1] - 2025-05-18

### Fixed
- Fixed "Add New Tool" functionality not working (Issue #4)
  - Updated backend API to return complete tool data
  - Added success message when a tool is created
  - Improved error handling for tool creation
  - Enhanced user feedback during form submission
- Fixed "Add New Chemical" functionality not working (Issue #5)
  - Added success notification when a chemical is created
  - Improved error handling for chemical creation
- Fixed "Add New User" functionality not working (Issue #6)
  - Added refresh functionality after user operations
  - Improved user feedback during user management operations
- Fixed calibration issues (Issues #7, #8)
  - Fixed date format handling in calibration forms
  - Fixed the order of operations when adding calibration standards
  - Improved error handling for calibration operations
- Fixed tool return functionality (Issues #3, #9, #11)
  - Updated backend to properly set tool status to "available" when returned
  - Enhanced frontend to update tool status across all interfaces
  - Added ability to specify the condition of the tool when returned
  - Added field for who returned the tool
  - Added option to mark a tool as 'found' on the production floor
  - Added field for additional notes about the return
- Fixed dark mode inconsistencies across pages (Issue #17)
  - Fixed table headers with bg-light class in dark mode
  - Fixed card headers with bg-light class in dark mode
  - Ensured consistent styling throughout the application
- Fixed calibration timeframe selector visibility issue (Issue #24)
  - Modified the CalibrationDueList component to always render the timeframe selector
  - Improved the selector text for better clarity
- Fixed Docker configuration (Issue #26)
  - Modified docker-compose.yml to use named volumes instead of local directory mounts
  - Tested the application in Docker and verified that it works correctly

### Changed
- Updated README.md to reflect the current version and features (Issue #21)
- Added comprehensive release notes documentation
- Improved version tracking and tagging

## [3.5.3] - 2025-05-18

### Fixed
- Fixed tool return functionality (Issues #3, #9)
- Fixed issue where returned tools remained in active checkouts list and showed as "Checked Out" in tools list
- Updated backend to properly set tool status to "available" when returned
- Enhanced frontend to update tool status across all interfaces when a tool is returned

## [3.5.0] - 2025-05-17

### Added
- Added tool calibration management functionality
- Implemented calibration tracking for tools requiring regular calibration
- Added calibration standards management
- Added calibration history tracking
- Added due soon and overdue calibration alerts
- Added calibration reports to the reporting system

### Changed
- Enhanced tool detail page to display calibration information
- Updated tool forms to include calibration fields
- Improved navigation with dedicated calibration section
- Enhanced admin dashboard to show calibration metrics

## [3.3.0] - 2025-05-20

### Added
- Added barcode generation functionality for chemical inventory
- Implemented barcode display with part number, lot number, and expiration date
- Added print functionality for chemical barcodes
- Added barcode button to chemical list and detail views

## [3.2.3] - 2025-05-19

### Fixed
- Fixed issue with return tool confirmation dialog in UserCheckouts and AllCheckouts components
- Replaced window.confirm() with proper modal dialog for better user experience
- Improved dialog handling to prevent browser freezing when returning tools

## [3.2.2] - 2025-05-18

### Fixed
- Fixed chemical reporting functionality in the Reports page
- Improved tab switching in the ReportingPage component
- Fixed backend implementation of the chemical usage analytics endpoint
- Updated UI for better user experience with button-based navigation

## [3.2.1] - 2025-05-16

### Fixed
- Fixed issue with registration requests count in Admin Dashboard showing incorrect number of pending requests
- Updated frontend to use actual data from backend API instead of hardcoded values
- Improved error handling for registration requests management

## [3.2.0] - 2025-05-14

### Added
- Added production-ready Docker configuration with multi-stage builds
- Implemented Nginx for serving frontend static files
- Enhanced database initialization process for first-time setup

### Changed
- Updated frontend build process for better performance and smaller bundle size
- Improved Docker container security and resource usage

## [3.1.0] - 2025-05-12

### Added
- Enhanced Admin Dashboard with real data integration instead of fallback data
- Improved System Statistics tab with detailed metrics and visualizations
- Added Performance Metrics section showing tool utilization and user activity rates
- Added System Health monitoring section with server and database status
- Added System Resources visualization with CPU, memory, and disk usage
- Improved Registration Requests management with better UI feedback

### Fixed
- Fixed issue with admin dashboard showing fallback data instead of real data
- Improved error handling in API requests with graceful fallbacks
- Enhanced user experience with better feedback on registration approval/denial

## [3.0.0] - 2025-06-15

### Added
- Added registration request system with admin approval workflow
- Created admin dashboard for managing registration requests
- Implemented approval/denial process for new user registrations
- Added system statistics and metrics in the admin dashboard
- Added mock data support for testing admin features

### Changed
- Enhanced security by requiring admin approval for new user registrations
- Improved user registration flow with clear status messages
- Updated UI components for better user experience
- Restructured backend API for registration management

### Fixed
 - Fixed issues with user authentication
- Improved error handling for registration and authentication processes

## [2.4.0] - 2025-06-05

### Added
- Added chemical usage analytics to the reports page
- Enhanced reporting capabilities with additional data visualization options
- Improved backend API performance for chemical analytics
- Added line graphs for chemical usage trends over time

### Changed
- Updated server configurations for better development experience
- Improved error handling in chemical analytics endpoints
- Enhanced UI responsiveness for reporting features

### Known Issues
- Chemical usage analytics feature is not functioning correctly
- API endpoint for chemical usage data returns incomplete information
- Line graphs for usage trends may display incorrect data

## [2.3.0] - 2025-05-31

### Added
- Added employee number search functionality to tool checkout process
- Added advanced filtering capabilities to tool inventory list
- Added ability to filter tools by status, category, and location
- Added option to hide retired tools in tool inventory list
- Added visual indicators for tool status in inventory list

## [2.2.1] - 2025-05-30

### Changed
- Updated table header styling to match background color across all pages
- Improved visual consistency throughout the application
- Enhanced UI flow with consistent styling

## [2.2.0] - 2025-05-25

### Changed
- Renamed application to "SupplyLine MRO Suite" throughout the codebase
- Updated all user interfaces with the new application name
- Updated container names in Docker configuration
- Updated package names and version information
- Modernized application branding to better reflect MRO capabilities

## [2.1.0] - 2025-05-20

### Added
- Enhanced chemical usage reporting with part number-specific analytics
- Added ability to track usage by part number, lot number, and location
- Added shelf life analytics with usage percentage calculations
- Added waste percentage tracking by part number
- Added part number analytics page with detailed metrics
- Added filtering capabilities to chemical waste analytics

### Changed
- Improved chemical waste analytics with location-based data
- Enhanced reporting interface with more detailed charts and tables
- Updated backend API to support more granular chemical tracking

## [1.4.0] - 2025-05-15

### Added
- Added chemicals tracking system for sealants, paints, and other materials
- Added chemical inventory management with expiration date tracking
- Added chemical issuance functionality to track usage by hangar
- Added low stock alerts based on minimum stock levels
- Added chemicals to reporting system for usage analytics

### Changed
- Updated navigation to include chemicals section
- Enhanced permission system to restrict chemicals management to Materials personnel and admins

## [1.3.0] - 2025-05-10

### Added
- Added user profile page with detailed user information
- Added avatar/profile picture upload functionality
- Added password change functionality in profile page
- Added user activity log viewing in profile page

### Changed
- Updated user interface to display user avatars throughout the application
- Improved static file handling for user-uploaded content

## [1.2.0] - 2025-05-07

### Added
- Added reporting page with data visualization
- Added PDF and Excel export capabilities for reports
- Added tool service status tracking (maintenance, retirement)

### Changed
- Improved tool inventory management interface
- Enhanced user experience with better error handling

## [1.1.1] - 2025-05-04

### Fixed
- Fixed Docker database path handling to correctly access the SQLite database in the Docker container
 - Updated Docker volume paths for database directory
- Fixed configuration to properly detect Docker environment

## [1.1.0] - 2025-05-01

### Added
- Added Materials department to user options
- Added tool search functionality with location tracking
- Added tool history tracking
- Added user management page for Materials and Admin users

### Changed
- Updated UI to full-page layout
- Changed user profile from dropdown to pop-out modal
- Added light/dark mode selector
- Updated header colors on tables

## [1.0.0] - 2025-04-15

### Added
- Initial release of the Tool Inventory Management System
- Basic tool inventory management
- Tool checkout/checkin functionality
- User authentication and authorization
- Department-based permissions
