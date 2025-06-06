# SupplyLine MRO Suite - Deployment Guide

This guide explains how to create installers for easy deployment of the SupplyLine MRO Suite Electron application.

## Quick Start (Automated)

### Windows
1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the project directory
3. Run: `scripts\build-installer.bat`
4. Wait for the build to complete
5. Find installers in the `dist` folder

### macOS/Linux
1. Open Terminal
2. Navigate to the project directory
3. Run: `./scripts/build-installer.sh`
4. Wait for the build to complete
5. Find installers in the `dist` folder

## Manual Build Process

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

### Step-by-Step Instructions

#### 1. Install Dependencies
```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

#### 2. Build the Application
```bash
# Build frontend
cd frontend
npm run build
cd ..

# Build for specific platforms
npm run dist:win    # Windows (NSIS + Portable)
npm run dist:mac    # macOS (DMG)
npm run dist:linux  # Linux (AppImage + DEB)

# Or build for all platforms
npm run dist
```

## Installer Types Created

### Windows
- **NSIS Installer** (`SupplyLine MRO Suite Setup.exe`)
  - Full installer with uninstaller
  - Creates desktop and start menu shortcuts
  - Allows custom installation directory
  - Includes license agreement

- **Portable Version** (`SupplyLine-MRO-Suite-{version}-portable.exe`)
  - No installation required
  - Run directly from any location
  - Perfect for USB drives or temporary use

### macOS
- **DMG Package** (`SupplyLine MRO Suite-{version}.dmg`)
  - Standard macOS installer
  - Drag-and-drop installation
  - Universal binary (Intel + Apple Silicon)

### Linux
- **AppImage** (`SupplyLine-MRO-Suite-{version}.AppImage`)
  - Portable application
  - No installation required
  - Works on most Linux distributions

- **DEB Package** (`supplyline-mro-suite_{version}_amd64.deb`)
  - Debian/Ubuntu package
  - Install with: `sudo dpkg -i package.deb`

## Distribution

### File Sizes (Approximate)
- Windows NSIS: ~150-200 MB
- Windows Portable: ~150-200 MB
- macOS DMG: ~150-200 MB
- Linux AppImage: ~150-200 MB
- Linux DEB: ~150-200 MB

### Sharing Options
1. **Direct Distribution**: Share installer files directly
2. **Network Share**: Place on company network drive
3. **USB Drive**: Copy portable versions to USB drives
4. **GitHub Releases**: Upload to GitHub for version management

## Auto-Updates

The application includes auto-update functionality:
- Checks for updates on startup
- Downloads and installs updates automatically
- Configured to use GitHub releases
- Users will be notified of available updates

## Code Signing (Optional)

For production deployment, consider code signing:

### Windows
```bash
# Install certificate and sign
npm run dist:win -- --publish=never --config.win.certificateFile=cert.p12 --config.win.certificatePassword=password
```

### macOS
```bash
# Sign with Apple Developer certificate
npm run dist:mac -- --publish=never --config.mac.identity="Developer ID Application: Your Name"
```

## Troubleshooting

### Common Issues

1. **Build Fails - Missing Dependencies**
   - Ensure all prerequisites are installed
   - Run `npm install` and `pip install -r requirements.txt`

2. **Python Not Found**
   - Ensure Python is in system PATH
   - Use `python3` on macOS/Linux

3. **Permission Denied (Linux/macOS)**
   - Make build script executable: `chmod +x scripts/build-installer.sh`

4. **Large File Size**
   - This is normal for Electron apps
   - Includes Node.js runtime and Python backend

### Build Logs
Check the console output for detailed error messages. Common solutions:
- Clear `node_modules` and reinstall
- Clear `dist` folder before rebuilding
- Ensure all source files are present

## Security Considerations

- The installer includes the entire backend with Python runtime
- Database files are excluded from the build
- Configuration is stored securely using electron-store
- No hardcoded credentials in the installer

## Support

For deployment issues:
1. Check this guide first
2. Review console output for errors
3. Ensure all prerequisites are met
4. Contact support with specific error messages
