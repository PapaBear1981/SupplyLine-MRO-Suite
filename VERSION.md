# SupplyLine MRO Suite

## Version History

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
