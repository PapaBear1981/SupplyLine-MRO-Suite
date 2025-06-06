# 🚀 SupplyLine MRO Suite - Easy Installer Creation

This directory contains everything you need to create professional installers for the SupplyLine MRO Suite Electron application.

## 🎯 Quick Start

### Option 1: Automated Scripts (Recommended)
**Windows:**
```cmd
scripts\build-installer.bat
```

**macOS/Linux:**
```bash
./scripts/build-installer.sh
```

### Option 2: GUI Builder
Open `scripts/build-gui.html` in your web browser for a visual interface.

### Option 3: Manual Commands
```bash
# Check environment first
npm run build:installer:win    # Windows only
npm run build:installer:mac    # macOS only  
npm run build:installer:linux  # Linux only
npm run dist:all               # All platforms
```

## 📦 What Gets Created

### Windows
- **`SupplyLine MRO Suite Setup.exe`** - Full installer with uninstaller
- **`SupplyLine-MRO-Suite-{version}-portable.exe`** - Portable version

### macOS
- **`SupplyLine MRO Suite-{version}.dmg`** - Standard Mac installer

### Linux
- **`SupplyLine-MRO-Suite-{version}.AppImage`** - Portable Linux app
- **`supplyline-mro-suite_{version}_amd64.deb`** - Debian package

## ✨ Features

- **Professional Installers**: NSIS for Windows, DMG for Mac, DEB/AppImage for Linux
- **Auto-Updates**: Built-in update mechanism using GitHub releases
- **Code Signing Ready**: Prepared for production code signing
- **Custom Branding**: Uses your app icons and branding
- **License Agreement**: Includes EULA in installer
- **Desktop Shortcuts**: Creates shortcuts automatically
- **Uninstaller**: Clean removal with option to keep user data

## 🔧 Prerequisites

- Node.js v16+
- Python 3.8+
- Git

## 📁 File Structure

```
scripts/
├── build-installer.bat      # Windows build script
├── build-installer.sh       # macOS/Linux build script
├── build-check.js          # Environment validation
└── build-gui.html          # Visual build interface

build/
├── installer.nsh           # Custom NSIS installer script
├── license.txt            # End User License Agreement
└── dmg-background.png     # macOS DMG background (optional)

dist/                      # Output directory for installers
```

## 🚀 Distribution

### File Sizes
- Windows: ~150-200 MB
- macOS: ~150-200 MB  
- Linux: ~150-200 MB

### Sharing Methods
1. **Direct**: Email or file sharing
2. **Network**: Company network drive
3. **USB**: Portable versions work great
4. **GitHub**: Upload to releases for auto-updates

## 🔒 Security

- No hardcoded credentials
- Secure configuration storage
- Optional code signing support
- Database files excluded from installer

## 🆘 Troubleshooting

### Common Issues

**"Python not found"**
- Install Python from python.org
- Ensure it's in your system PATH

**"Build failed"**
- Run `npm run clean` first
- Check `npm install` completed successfully
- Verify all prerequisites are installed

**"Permission denied"**
- Run as Administrator (Windows)
- Use `sudo` if needed (Linux/Mac)
- Check file permissions

### Getting Help

1. Check the full [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
2. Run the environment check: `node scripts/build-check.js`
3. Review console output for specific errors

## 🎨 Customization

### Icons
Replace files in `assets/` directory:
- `icon.ico` - Windows icon
- `icon.icns` - macOS icon  
- `icon.png` - Linux icon

### Installer Text
Edit `build/installer.nsh` for custom installer messages.

### License
Update `build/license.txt` with your license terms.

## 📈 Auto-Updates

The app includes automatic update checking:
- Checks GitHub releases on startup
- Downloads and installs updates automatically
- Users are notified of available updates
- Configure in `package.json` under `publish` section

## 🏆 Best Practices

1. **Test First**: Always test installers before distribution
2. **Version Bump**: Update version in `package.json` before building
3. **Clean Build**: Use `npm run clean` between builds
4. **Code Sign**: Consider code signing for production
5. **Release Notes**: Document changes for users

---

**Ready to deploy? Run the build script and share your professional installer!** 🎉
