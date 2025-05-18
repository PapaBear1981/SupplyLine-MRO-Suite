# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [3.5.4] - 2025-05-18

### Fixed
- Fixed "Add New Tool" functionality not working (Issue #4)
  - Updated backend API to return complete tool data
  - Added success message when a tool is created
  - Improved error handling for tool creation
  - Enhanced user feedback during form submission

### Changed
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
- Fixed issues with user authentication and session management
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
- Updated Docker volume paths for database and session directories
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
