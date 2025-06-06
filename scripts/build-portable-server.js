#!/usr/bin/env node

/**
 * Build script for portable server
 * 
 * This script prepares the portable server for distribution
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 Building Portable Server...');

const serverDir = path.join(__dirname, '../server');
const distDir = path.join(serverDir, 'dist');

// Ensure directories exist
if (!fs.existsSync(serverDir)) {
  fs.mkdirSync(serverDir, { recursive: true });
}

if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Copy server files
const serverFiles = [
  'portable-server.js'
];

serverFiles.forEach(file => {
  const srcPath = path.join(serverDir, file);
  const destPath = path.join(distDir, file);
  
  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
    console.log(`✅ Copied ${file}`);
  } else {
    console.log(`⚠️  ${file} not found`);
  }
});

// Create package.json for the server
const serverPackageJson = {
  name: "supplyline-portable-server",
  version: "3.6.0",
  description: "Portable HTTP server for SupplyLine MRO Suite PWA",
  main: "portable-server.js",
  scripts: {
    start: "node portable-server.js"
  },
  dependencies: {
    express: "^4.18.2",
    "serve-static": "^1.15.0",
    open: "^8.4.0"
  }
};

fs.writeFileSync(
  path.join(distDir, 'package.json'),
  JSON.stringify(serverPackageJson, null, 2)
);

console.log('✅ Created server package.json');

// Create startup scripts
const startupScripts = {
  'start-server.bat': `@echo off
echo Starting SupplyLine MRO Suite PWA Server...
echo.
node portable-server.js
pause`,
  
  'start-server.sh': `#!/bin/bash
echo "Starting SupplyLine MRO Suite PWA Server..."
echo
node portable-server.js`,
  
  'README.txt': `SupplyLine MRO Suite - Portable PWA Server
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
`
};

Object.entries(startupScripts).forEach(([filename, content]) => {
  fs.writeFileSync(path.join(distDir, filename), content);
  console.log(`✅ Created ${filename}`);
});

// Make shell script executable (on Unix systems)
try {
  fs.chmodSync(path.join(distDir, 'start-server.sh'), 0o755);
  console.log('✅ Made start-server.sh executable');
} catch (err) {
  console.log('⚠️  Could not make start-server.sh executable (Windows?)');
}

console.log('🎉 Portable server build completed!');
console.log(`📁 Output directory: ${distDir}`);
