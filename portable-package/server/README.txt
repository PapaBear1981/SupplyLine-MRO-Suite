SupplyLine MRO Suite - Portable PWA Server
==========================================

This is a portable version of SupplyLine MRO Suite that runs as a Progressive Web Application.

REQUIREMENTS:
- Node.js (version 14 or higher)
- Internet connection for Supabase (optional for offline mode)

QUICK START:
1. Double-click "start-server.bat" (Windows) or run "./start-server.sh" (Linux/Mac)
2. The application will open in your default browser
3. Configure Supabase connection when prompted

MANUAL START:
1. Open terminal/command prompt in this directory
2. Run: node portable-server.js
3. Open browser to: http://localhost:3000

CONFIGURATION:
- Set PORT environment variable to change port (default: 3000)
- Set HOST environment variable to change host (default: localhost)
- Set AUTO_OPEN=false to disable auto-opening browser

FEATURES:
- Works offline after initial setup
- Automatic data synchronization with Supabase
- Progressive Web App - can be "installed" from browser
- Cross-platform compatibility

For support, visit: https://github.com/PapaBear1981/SupplyLine-MRO-Suite
