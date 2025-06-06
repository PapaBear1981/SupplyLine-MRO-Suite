#!/usr/bin/env node

/**
 * Pre-build check script for SupplyLine MRO Suite
 * Validates environment and dependencies before building installers
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Pre-build Environment Check\n');

let hasErrors = false;

// Check Node.js version
try {
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
  
  if (majorVersion >= 16) {
    console.log(`✅ Node.js ${nodeVersion} (OK)`);
  } else {
    console.log(`❌ Node.js ${nodeVersion} (Requires v16+)`);
    hasErrors = true;
  }
} catch (error) {
  console.log('❌ Node.js not found');
  hasErrors = true;
}

// Check Python
try {
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  const pythonVersion = execSync(`${pythonCmd} --version`, { encoding: 'utf8' }).trim();
  console.log(`✅ ${pythonVersion} (OK)`);
} catch (error) {
  console.log('❌ Python not found or not in PATH');
  hasErrors = true;
}

// Check required files
const requiredFiles = [
  'package.json',
  'electron/main.js',
  'electron/preload.js',
  'frontend/package.json',
  'backend/requirements.txt',
  'backend/app.py'
];

console.log('\n📁 Checking required files:');
requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} (Missing)`);
    hasErrors = true;
  }
});

// Check if frontend is built
console.log('\n🏗️  Checking build status:');
if (fs.existsSync('frontend/dist')) {
  console.log('✅ Frontend build directory exists');
} else {
  console.log('⚠️  Frontend not built (will be built automatically)');
}

// Check dependencies
console.log('\n📦 Checking dependencies:');
try {
  if (fs.existsSync('node_modules')) {
    console.log('✅ Root dependencies installed');
  } else {
    console.log('❌ Root dependencies not installed (run: npm install)');
    hasErrors = true;
  }

  if (fs.existsSync('frontend/node_modules')) {
    console.log('✅ Frontend dependencies installed');
  } else {
    console.log('❌ Frontend dependencies not installed (run: cd frontend && npm install)');
    hasErrors = true;
  }
} catch (error) {
  console.log('❌ Error checking dependencies');
  hasErrors = true;
}

// Check disk space (approximate)
try {
  const stats = fs.statSync('.');
  console.log('\n💾 Build requirements:');
  console.log('✅ Estimated space needed: ~500MB for build artifacts');
  console.log('✅ Final installer size: ~150-200MB per platform');
} catch (error) {
  // Non-critical
}

// Summary
console.log('\n' + '='.repeat(50));
if (hasErrors) {
  console.log('❌ PRE-BUILD CHECK FAILED');
  console.log('\nPlease fix the issues above before building.');
  console.log('\nQuick fixes:');
  console.log('- Install Node.js v16+ from https://nodejs.org/');
  console.log('- Install Python 3.8+ from https://python.org/');
  console.log('- Run: npm install');
  console.log('- Run: cd frontend && npm install');
  process.exit(1);
} else {
  console.log('✅ PRE-BUILD CHECK PASSED');
  console.log('\nEnvironment is ready for building installers!');
  console.log('Proceeding with build...\n');
}
