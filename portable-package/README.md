# SupplyLine MRO Suite - Portable PWA

A portable Progressive Web Application for MRO (Maintenance, Repair, and Operations) tool and chemical management.

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
1. Double-click `start.bat` (Windows) or run `./start.sh` (Linux/Mac)
2. The script will automatically install dependencies and start the server
3. Your browser will open to the application

### Option 2: Manual Setup
1. Install Node.js (version 14 or higher) if not already installed
2. Open terminal/command prompt in this directory
3. Run: `npm run install-deps` to install server dependencies
4. Run: `npm start` to start the server
5. Open browser to: http://localhost:3000

## 📋 Requirements

- **Node.js**: Version 14 or higher
- **Internet Connection**: Required for initial Supabase setup and sync (optional for offline use)
- **Modern Browser**: Chrome, Firefox, Safari, or Edge

## ⚙️ Configuration

### Environment Variables
- `PORT`: Server port (default: 3000)
- `HOST`: Server host (default: localhost, use 0.0.0.0 for external access)
- `AUTO_OPEN`: Auto-open browser (default: true, set to false to disable)

### Supabase Setup
1. On first run, you'll be prompted to configure Supabase
2. Enter your Supabase project URL and API key
3. Configuration is saved locally for future use

## 🌟 Features

- **Progressive Web App**: Install from browser for app-like experience
- **Offline Support**: Works without internet after initial setup
- **Real-time Sync**: Automatic data synchronization with Supabase
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Portable**: No installation required, runs from USB or any directory
- **Responsive Design**: Optimized for desktop, tablet, and mobile

## 📱 PWA Installation

1. Open the application in a supported browser
2. Look for "Install" or "Add to Home Screen" option
3. Follow browser prompts to install as a native app

## 🔧 Troubleshooting

### Port Already in Use
If port 3000 is busy, the server will automatically find the next available port.

### Browser Doesn't Open
- Manually navigate to the URL shown in the terminal
- Check if your firewall is blocking the connection
- Try setting `HOST=0.0.0.0` for external access

### Supabase Connection Issues
- Verify your Supabase URL and API key
- Check internet connection
- Ensure Supabase project is active

### Node.js Not Found
- Download and install Node.js from: https://nodejs.org/
- Restart terminal/command prompt after installation
- Verify installation: `node --version`

## 📁 Directory Structure

```
portable-package/
├── frontend/dist/     # Built React PWA files
├── server/           # Portable HTTP server
├── start.bat         # Windows startup script
├── start.sh          # Linux/Mac startup script
├── package.json      # Main package configuration
└── README.md         # This file
```

## 🔄 Updates

To update the application:
1. Download the latest portable package
2. Replace old files with new ones
3. Restart the server

Your Supabase configuration and local data will be preserved.

## 📞 Support

- **GitHub**: https://github.com/PapaBear1981/SupplyLine-MRO-Suite
- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Check the repository wiki for detailed guides

## 📄 License

This project is licensed under the MIT License - see the repository for details.

---

**Version**: 3.6.0  
**Build Date**: 2025-06-06  
**Type**: Portable PWA
