# SupplyLine MRO Suite - Portable Edition

## Overview
This is a portable version of the SupplyLine MRO Suite application that can be run from any Windows computer without installation.

## System Requirements
- Windows 10 or later (64-bit)
- Python 3.8 or later installed and available in PATH
- At least 4GB of available RAM
- 500MB of free disk space

## Quick Start
1. Extract this folder to any location on your computer
2. Double-click `Launch-SupplyLine.bat` to start the application
3. The application will open in a new window
4. Use the default login credentials:
   - Username: `ADMIN001`
   - Password: `admin123`

## What's Included
- **App/**: Contains the Electron application files
  - `SupplyLine MRO Suite.exe`: Main application executable
  - `resources/`: Application resources including frontend and backend code
- **Launch-SupplyLine.bat**: Convenient launcher script
- **README.md**: This documentation file

## Features
- Complete MRO (Maintenance, Repair, and Operations) management system
- Tool checkout and return tracking
- Chemical inventory management
- User management and role-based access control
- Reporting and analytics
- Offline-capable operation
- Integrated database (SQLite)

## Usage Notes
- The application runs entirely offline - no internet connection required
- All data is stored locally in the application directory
- The backend server starts automatically when you launch the app
- Close the application properly to ensure data is saved

## Troubleshooting

### Application Won't Start
- Ensure Python 3.8+ is installed and in your system PATH
- Try running as Administrator if you encounter permission issues
- Check that no antivirus software is blocking the application

### Performance Issues
- Ensure you have at least 4GB of available RAM
- Close other resource-intensive applications
- Consider moving the app to an SSD for better performance

### Data Issues
- All data is stored in the `App/resources/backend/app.db` file
- To reset the application, delete this file (you'll lose all data)
- To backup your data, copy the entire application folder

## Support
For technical support or questions about the SupplyLine MRO Suite, please contact your system administrator.

## Version Information
- Application Version: 3.5.4
- Build Date: June 2025
- Electron Version: 32.3.3
- Backend: Python Flask with SQLite database
- Frontend: React with Bootstrap UI

---
*SupplyLine MRO Suite - Streamlining maintenance operations*
