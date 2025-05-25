# SupplyLine MRO Suite

## Version History

### Version 3.5.4 (2025-05-24)
- Fixed critical backend infrastructure issues
  - Fixed Resource Monitor Windows Compatibility (SystemError in disk usage monitoring)
  - Fixed Password Validation Import Issue (restored strong password validation)
- Fixed critical navigation issues
  - Fixed Admin Dashboard Tab Switching (User Management, Role Management, Audit Logs)
  - Fixed Main Navigation Menu Links (Tools, Chemicals, Reports, Admin Dashboard)
- Added major performance improvements
  - Added 26 new database indexes for cycle count functionality
  - Implemented composite indexes for complex queries
  - Enhanced query performance significantly improved
- Fixed comprehensive time handling
  - Updated all database models to use local time instead of UTC
  - Replaced all datetime.utcnow() calls with local time equivalents
  - Added get_current_time() utility function for consistency
- Enhanced tool management features (Phase 2)
  - Admin tool deletion capability with multi-step confirmation
  - Enhanced tool history with detailed transaction modals
  - Improved calibration workflow with visual status indicators
- Added new cycle count reports
  - Inventory Accuracy Report with trend analysis
  - Discrepancy Report with detailed variance tracking
  - Performance Report with efficiency metrics
  - Coverage Report with completion tracking
- Comprehensive testing and documentation
  - Backend test suite with pytest integration
  - Frontend test suite with React Testing Library
  - Complete user guide (356 lines) with step-by-step instructions
  - Technical guide with architecture and API documentation
- Security improvements
  - Enhanced session management security
  - Improved error handling with structured logging
  - Input validation and sanitization improvements
- UI/UX and accessibility enhancements
  - Added comprehensive tooltips across all components (QuickActions, DashboardStats, AdminDashboard, UserCheckoutStatus, OverdueChemicals, PastDueTools, ProfileModal, LoginForm, RegisterForm)
  - Standardized styling with unified Bootstrap-compatible CSS variables
  - Consistent button variants, sizes, focus states, and badge colors
  - Enhanced accessibility with ARIA labels, screen reader support, keyboard navigation focus indicators
  - Added support for high-contrast mode and reduced-motion preferences

### Version 3.5.3 (2025-05-20)
- Fixed login functionality for non-admin users
- Fixed Admin Dashboard tab switching for User Management, Role Management, System Settings, and Help Settings
- Fixed calibration due alert discrepancy between Tools and Calibration Reports pages
- Fixed Chemical Waste Analytics report to display real data
- Fixed Part Number Analytics to use real-time data instead of mock data
- Fixed Calibration History report to show serial numbers and descriptions
- Fixed Chemical Reorder Management delivery functionality
- Fixed Audit Logs display in Admin Dashboard
- Added alerts for chemicals past their expected delivery date
- Improved tool status display for overdue tools
- Removed redundant UI elements from several pages
- Removed Activity Log tab from profile page
- Standardized date formats across the application

### Version 3.5.2 (2025-05-19)
- Fixed chemical dropdown menu issue
- Removed dropdown menu from chemical list to simplify interface
- Fixed chemical issuance history endpoint
- Implemented missing API endpoints for marking chemicals as ordered and delivered
- Implemented chemical issuance functionality
- Enhanced Chemical Usage Analytics with real-time data
- Removed debug login functionality and debug endpoints

### Version 3.5.1 (2025-05-18)
- Fixed "Add New Tool" functionality
- Fixed "Add New Chemical" functionality
- Fixed "Add New User" functionality
- Fixed calibration issues
- Fixed tool return functionality
- Fixed dark mode inconsistencies across pages
- Fixed calibration timeframe selector visibility issue
- Fixed Docker configuration
- Updated README.md to reflect the current version and features
- Added comprehensive release notes documentation
- Improved version tracking and tagging

### Version 3.5.0 (2025-05-17)
- Added tool calibration management functionality
- Implemented calibration tracking for tools requiring regular calibration
- Added calibration standards management
- Added calibration history tracking
- Added due soon and overdue calibration alerts
- Added calibration reports to the reporting system
- Enhanced tool detail page to display calibration information
- Updated tool forms to include calibration fields
- Improved navigation with dedicated calibration section
- Enhanced admin dashboard to show calibration metrics

### Version 3.3.2 (2025-05-17)
- Fixed chemical management routes for reorder, on-order, expiring soon, and archived chemicals
- Improved route handling for chemical analytics
- Enhanced error handling for chemical management functionality

### Version 3.3.1 (2025-05-17)
- Fixed CORS issues for better API communication
- Removed debug login section from the login page
- Updated API service to use relative URLs for better proxy support

### Version 3.3.0 (2025-05-20)
- Added barcode generation functionality for chemical inventory
- Implemented barcode display with part number, lot number, and expiration date
- Added print functionality for chemical barcodes
- Added barcode button to chemical list and detail views

### Version 3.2.3 (2025-05-19)
- Fixed issue with return tool confirmation dialog in UserCheckouts and AllCheckouts components
- Replaced window.confirm() with proper modal dialog for better user experience
- Improved dialog handling to prevent browser freezing when returning tools

### Version 3.2.2 (2025-05-18)
- Fixed chemical reporting functionality in the Reports page
- Improved tab switching in the ReportingPage component
- Fixed backend implementation of the chemical usage analytics endpoint
- Updated UI for better user experience with button-based navigation

### Version 3.2.1 (2025-05-16)
- Fixed issue with registration requests count in Admin Dashboard showing incorrect number of pending requests
- Updated frontend to use actual data from backend API instead of hardcoded values
- Improved error handling for registration requests management

### Version 3.2.0 (2025-05-14)
- Added production-ready Docker configuration with multi-stage builds
- Implemented Nginx for serving frontend static files
- Enhanced database initialization process for first-time setup
- Updated frontend build process for better performance and smaller bundle size
- Improved Docker container security and resource usage

### Version 3.1.0 (2025-05-12)
- Enhanced Admin Dashboard with real data integration instead of fallback data
- Improved System Statistics tab with detailed metrics and visualizations
- Added Performance Metrics section showing tool utilization and user activity rates
- Added System Health monitoring section with server and database status
- Added System Resources visualization with CPU, memory, and disk usage
- Improved Registration Requests management with better UI feedback

### Version 3.0.0 (2025-06-15)
- Added registration request system with admin approval workflow
- Created admin dashboard for managing registration requests
- Implemented approval/denial process for new user registrations
- Added system statistics and metrics in the admin dashboard
- Enhanced security by requiring admin approval for new user registrations
- Improved user registration flow with clear status messages
- Fixed issues with user authentication and session management

### Version 2.4.0 (2025-06-05)
- Added chemical usage analytics to the reports page
- Enhanced reporting capabilities with additional data visualization options
- Improved backend API performance for chemical analytics
- Added line graphs for chemical usage trends over time

### Version 2.3.0 (2025-05-30)
- Added chemicals tracking functionality for materials personnel and admins
- Implemented tracking for chemical dates, part numbers, lot numbers, and quantities
- Added issue tracking for chemicals
- Implemented reporting capabilities for chemicals

### Version 2.2.0 (2025-05-25)
- Added reporting page with PDF/Excel export capabilities
- Implemented data visualization graphs for reporting
- Updated header colors to match background throughout the application
- Added profile update functionality with avatar/picture upload capability

### Version 2.1.0 (2025-05-22)
- Changed user profile from dropdown to pop-out modal
- Added light/dark mode selector
- Added Materials as an option in department listings
- Added tool search functionality with location and history tracking
- Added functionality to search for users by employee number when checking out tools

### Version 2.0.0 (2025-05-20)
- Major update with full-page layout for the application UI
- Added user management page for Materials users and Admins
- Implemented active/inactive status for users to preserve transaction history
- Enhanced tool inventory table with filtering and ability to hide retired tools
- Improved Active Checkouts table with better information display

### Version 1.1.1 (2025-05-20)
- Fixed database schema compatibility issues with tool categories
- Improved error handling for missing database columns
- Enhanced model resilience with fallback values for optional fields
- Fixed tool status display in tool list and detail views
- Ensured proper tracking of service history and checkout status

### Version 1.1.0 (2025-05-15)
- Added ability to remove tools from service temporarily for maintenance/calibration
- Added ability to permanently retire tools
- Added ability to return tools to service after maintenance/calibration
- Added service history tracking for tools
- Required comments for all service status changes
- Updated UI to display tool service status and history

### Version 1.0.0 (2025-05-04)
- Initial release
- Basic tool inventory management functionality
- User authentication and authorization
- Tool checkout and return functionality
- Admin dashboard for user management
- Materials department permissions for tool management
- Docker containerization for easy deployment
