# Changelog

All notable changes to this project will be documented in this file.

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
