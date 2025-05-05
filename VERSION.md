# Tool Inventory Management System

## Version History

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
