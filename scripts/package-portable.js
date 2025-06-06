#!/usr/bin/env node

/**
 * Package script for portable SupplyLine MRO Suite PWA
 * 
 * Creates a complete portable package with frontend, server, and dependencies
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('📦 Packaging Portable SupplyLine MRO Suite PWA...');

const rootDir = path.join(__dirname, '..');
const packageDir = path.join(rootDir, 'portable-package');
const frontendDistDir = path.join(rootDir, 'frontend', 'dist');
const serverDistDir = path.join(rootDir, 'server', 'dist');

// Clean and create package directory
if (fs.existsSync(packageDir)) {
  fs.rmSync(packageDir, { recursive: true, force: true });
}
fs.mkdirSync(packageDir, { recursive: true });

console.log('📁 Created package directory');

// Check if frontend is built
if (!fs.existsSync(frontendDistDir)) {
  console.log('🔧 Frontend not built, building now...');
  try {
    execSync('npm run frontend:build', { cwd: rootDir, stdio: 'inherit' });
  } catch (error) {
    console.error('❌ Failed to build frontend:', error.message);
    process.exit(1);
  }
}

// Check if server is built
if (!fs.existsSync(serverDistDir)) {
  console.log('🔧 Server not built, building now...');
  try {
    execSync('npm run server:build', { cwd: rootDir, stdio: 'inherit' });
  } catch (error) {
    console.error('❌ Failed to build server:', error.message);
    process.exit(1);
  }
}

// Copy frontend dist
const frontendPackageDir = path.join(packageDir, 'frontend', 'dist');
fs.mkdirSync(frontendPackageDir, { recursive: true });
copyDirectory(frontendDistDir, frontendPackageDir);
console.log('✅ Copied frontend files');

// Copy server files
const serverPackageDir = path.join(packageDir, 'server');
fs.mkdirSync(serverPackageDir, { recursive: true });
copyDirectory(serverDistDir, serverPackageDir);
console.log('✅ Copied server files');

// Create main package.json
const mainPackageJson = {
  name: "supplyline-mro-suite-portable",
  version: "3.6.0",
  description: "Portable SupplyLine MRO Suite Progressive Web Application",
  main: "server/portable-server.js",
  scripts: {
    start: "node server/portable-server.js",
    "install-deps": "cd server && npm install"
  },
  engines: {
    node: ">=14.0.0"
  },
  keywords: ["mro", "tools", "inventory", "pwa", "portable"],
  author: "SupplyLine MRO Suite",
  license: "MIT"
};

fs.writeFileSync(
  path.join(packageDir, 'package.json'),
  JSON.stringify(mainPackageJson, null, 2)
);
console.log('✅ Created main package.json');

// Create comprehensive README
const readmeContent = `# SupplyLine MRO Suite - Portable PWA

A portable Progressive Web Application for MRO (Maintenance, Repair, and Operations) tool and chemical management.

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
1. Double-click \`start.bat\` (Windows) or run \`./start.sh\` (Linux/Mac)
2. The script will automatically install dependencies and start the server
3. Your browser will open to the application

### Option 2: Manual Setup
1. Install Node.js (version 14 or higher) if not already installed
2. Open terminal/command prompt in this directory
3. Run: \`npm run install-deps\` to install server dependencies
4. Run: \`npm start\` to start the server
5. Open browser to: http://localhost:3000

## 📋 Requirements

- **Node.js**: Version 14 or higher
- **Internet Connection**: Required for initial Supabase setup and sync (optional for offline use)
- **Modern Browser**: Chrome, Firefox, Safari, or Edge

## ⚙️ Configuration

### Environment Variables
- \`PORT\`: Server port (default: 3000)
- \`HOST\`: Server host (default: localhost, use 0.0.0.0 for external access)
- \`AUTO_OPEN\`: Auto-open browser (default: true, set to false to disable)

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
- Try setting \`HOST=0.0.0.0\` for external access

### Supabase Connection Issues
- Verify your Supabase URL and API key
- Check internet connection
- Ensure Supabase project is active

### Node.js Not Found
- Download and install Node.js from: https://nodejs.org/
- Restart terminal/command prompt after installation
- Verify installation: \`node --version\`

## 📁 Directory Structure

\`\`\`
portable-package/
├── frontend/dist/     # Built React PWA files
├── server/           # Portable HTTP server
├── start.bat         # Windows startup script
├── start.sh          # Linux/Mac startup script
├── package.json      # Main package configuration
└── README.md         # This file
\`\`\`

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
**Build Date**: ${new Date().toISOString().split('T')[0]}  
**Type**: Portable PWA
`;

fs.writeFileSync(path.join(packageDir, 'README.md'), readmeContent);
console.log('✅ Created comprehensive README');

// Create startup scripts
const startupScripts = {
  'start.bat': `@echo off
title SupplyLine MRO Suite - Portable PWA
echo ========================================
echo  SupplyLine MRO Suite - Portable PWA
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js found
echo.

REM Install dependencies if needed
if not exist "server\\node_modules" (
    echo 📦 Installing server dependencies...
    cd server
    npm install
    cd ..
    echo.
)

echo 🚀 Starting SupplyLine MRO Suite PWA Server...
echo.
npm start
pause`,

  'start.sh': `#!/bin/bash

echo "========================================"
echo " SupplyLine MRO Suite - Portable PWA"
echo "========================================"
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    echo
    echo "Please install Node.js from: https://nodejs.org/"
    echo
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo

# Install dependencies if needed
if [ ! -d "server/node_modules" ]; then
    echo "📦 Installing server dependencies..."
    cd server
    npm install
    cd ..
    echo
fi

echo "🚀 Starting SupplyLine MRO Suite PWA Server..."
echo
npm start`
};

Object.entries(startupScripts).forEach(([filename, content]) => {
  fs.writeFileSync(path.join(packageDir, filename), content);
  console.log(`✅ Created ${filename}`);
});

// Make shell script executable
try {
  fs.chmodSync(path.join(packageDir, 'start.sh'), 0o755);
  console.log('✅ Made start.sh executable');
} catch (err) {
  console.log('⚠️  Could not make start.sh executable (Windows?)');
}

console.log('🎉 Portable package created successfully!');
console.log(`📁 Package location: ${packageDir}`);
console.log('');
console.log('📋 Next steps:');
console.log('1. Copy the portable-package folder to your desired location');
console.log('2. Run start.bat (Windows) or ./start.sh (Linux/Mac)');
console.log('3. Configure Supabase when prompted');

// Helper function to copy directories recursively
function copyDirectory(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}
