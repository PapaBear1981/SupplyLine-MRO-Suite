# SupplyLine MRO Suite Release Notes

## Version 3.5.4 (2025-05-24) - Current Release

### Critical Bug Fixes

#### Backend Infrastructure
- **Fixed Resource Monitor Windows Compatibility** (#215)
  - Resolved `SystemError: argument 1 (impossible<bad format char>)` in disk usage monitoring
  - Added proper Windows disk path resolution using `os.path.splitdrive()`
  - Enhanced error handling with graceful fallback for system monitoring

- **Fixed Password Validation Import Issue** (#215)
  - Resolved "Falling back to dummy password validation" security warning
  - Replaced problematic sys.path manipulation with `importlib.util`
  - Restored strong password validation functionality

#### Navigation and User Interface
- **Fixed Admin Dashboard Tab Switching** (#216)
  - Resolved critical issue preventing access to User Management, Role Management, Audit Logs
  - Restored full admin dashboard functionality
  - All admin tabs now switch correctly

- **Fixed Main Navigation Menu Links** (#218)
  - Resolved critical navigation issue affecting all main menu links
  - Users can now properly navigate between Tools, Chemicals, Reports, Admin Dashboard
  - Restored primary navigation functionality

- **UI/UX Enhancements** (#229)
  - Added descriptive tooltips to quick action buttons, dashboard statistics, tab navigation, status badges, action buttons, preference switches, and form fields
  - Standardized button variants, sizes, focus styles, and badge colors using unified Bootstrap-compatible CSS variables
  - Improved accessibility with ARIA labels, enhanced screen reader support, keyboard navigation focus indicators, high-contrast mode, and reduced-motion support

### Performance Improvements

#### Database Optimization
- **Added 26 New Database Indexes** for cycle count functionality
- **Implemented Composite Indexes** for complex queries
- **Enhanced Query Performance** significantly improved (up to 10x faster)
- **Database Constraints** enhanced for data integrity

#### System Resource Monitoring
- **Fixed System Resources Display** (#139, #143)
  - Real-time CPU, memory, and disk usage monitoring
  - Proper progress bar formatting and percentage display
  - Enhanced refresh functionality

### Time Handling Improvements

- **Comprehensive Time Handling Fix** (#154, #155)
  - Updated all database models to use local time instead of UTC
  - Replaced all `datetime.utcnow()` calls with local time equivalents
  - Added `get_current_time()` utility function for consistency
  - All timestamps throughout application now use local time

### Tool Management Enhancements

#### Phase 2 Tool Management Features
- **Admin Tool Deletion Capability** (#12)
  - Multi-step confirmation modal with history checking
  - Smart deletion workflow with retire option
  - Force delete option for tools with history
  - Comprehensive audit logging

- **Enhanced Tool History** (#19)
  - Detailed transaction modal with comprehensive checkout information
  - Improved status indicators with color-coded badges
  - Better data display with formatting and tooltips

- **Improved Calibration Workflow** (#34)
  - Visual calibration status indicators (Current, Due Soon, Overdue)
  - Calibration column in tool list with tooltips
  - Dashboard integration with calibration notifications
  - Enhanced calibration display in tool detail pages

### Reporting and Analytics

#### New Cycle Count Reports
- **Inventory Accuracy Report** with trend analysis
- **Discrepancy Report** with detailed variance tracking
- **Performance Report** with efficiency metrics
- **Coverage Report** with completion tracking
- **Interactive Filters** for all reports (location, category, type)
- **Real-time Data Visualization** with charts and graphs

### Testing and Documentation

#### Comprehensive Testing Infrastructure
- **Backend Test Suite** with pytest integration
- **Frontend Test Suite** with React Testing Library
- **Integration Tests** for API endpoints
- **Component Tests** for UI functionality

#### Complete Documentation Suite
- **User Guide** (356 lines) with step-by-step instructions
- **Technical Guide** with architecture and API documentation
- **Mobile Interface Guide** with barcode scanning
- **Troubleshooting Section** with common issues and solutions

### Security Improvements

- **Enhanced Session Management** security
- **Improved Error Handling** with structured logging
- **CORS Configuration** security enhancements
- **Input Validation** and sanitization improvements

### Deployment Notes

#### Database Updates Required
```bash
# Apply new indexes for performance
python apply_cycle_count_indexes.py

# Update time handling (if needed)
python migrate_time_handling.py
```

#### Environment Considerations
- **Windows Compatibility**: Resource monitoring now works correctly on Windows
- **Time Zones**: Application now uses local time consistently
- **Performance**: Database indexes significantly improve query performance

### Impact Summary

#### Performance Improvements
- **Database Queries**: Up to 10x faster with proper indexing
- **Page Load Times**: Reduced with optimized component rendering
- **System Monitoring**: Real-time accurate resource tracking

#### User Experience
- **Navigation**: Fully restored main menu and admin dashboard functionality
- **Tool Management**: Enhanced workflow with deletion and calibration features
- **Reporting**: Four new comprehensive cycle count reports
- **Time Display**: Consistent local time throughout application
- **User Interface**: Added contextual tooltips, standardized styling, and enhanced accessibility

#### Development Quality
- **Test Coverage**: Comprehensive testing for reliability
- **Documentation**: Complete guides for users and developers
- **Error Handling**: Improved debugging and user feedback
- **Security**: Enhanced session management and validation

---

## Previous Releases

### Bug Fixes (Historical)
- Fixed issue #4: Add New Tool functionality not working
  - Tools can now be successfully added through the UI
  - Added success message when a tool is created
  - Improved error handling for tool creation
  - Fixed backend API to return complete tool data

## Version 3.5.2 (Current)

### Features
- Added calibration management for tools
- Improved chemical inventory tracking
- Enhanced reporting capabilities

### Bug Fixes
- Fixed issue with checkout history not displaying correctly
- Resolved authentication issues for some user roles
- Improved error handling for network failures

## Version 3.5.1

### Features
- Added barcode generation for chemicals
- Implemented expiration date tracking for chemicals
- Added reorder notifications for low stock items

### Bug Fixes
- Fixed search functionality in tools list
- Resolved issue with user permissions for tool checkout
- Fixed date formatting in reports

## Version 3.5.0

### Major Features
- Complete UI redesign with improved user experience
- Added chemical inventory management
- Implemented tool service history tracking
- Added comprehensive reporting system
- Improved user management with role-based permissions

### Bug Fixes
- Multiple performance improvements
- Enhanced security for user authentication
- Fixed various UI inconsistencies
