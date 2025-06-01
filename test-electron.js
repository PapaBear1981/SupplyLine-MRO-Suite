#!/usr/bin/env node

/**
 * Simple test script to verify Electron setup
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 Testing Electron Setup for SupplyLine MRO Suite\n');

// Check if required files exist
const requiredFiles = [
  'package.json',
  'electron/main.js',
  'electron/preload.js',
  'frontend/package.json',
  'backend/requirements.txt'
];

const requiredDirs = [
  'electron',
  'frontend/src',
  'backend',
  'scripts'
];

console.log('📁 Checking required files and directories...');

let allGood = true;

// Check files
requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - MISSING`);
    allGood = false;
  }
});

// Check directories
requiredDirs.forEach(dir => {
  if (fs.existsSync(dir) && fs.statSync(dir).isDirectory()) {
    console.log(`✅ ${dir}/`);
  } else {
    console.log(`❌ ${dir}/ - MISSING`);
    allGood = false;
  }
});

console.log('\n📦 Checking package.json configuration...');

try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  
  // Check main entry point
  if (packageJson.main === 'electron/main.js') {
    console.log('✅ Main entry point configured correctly');
  } else {
    console.log('❌ Main entry point should be "electron/main.js"');
    allGood = false;
  }

  // Check scripts
  const requiredScripts = ['electron', 'electron-dev', 'dist'];
  requiredScripts.forEach(script => {
    if (packageJson.scripts && packageJson.scripts[script]) {
      console.log(`✅ Script "${script}" defined`);
    } else {
      console.log(`❌ Script "${script}" missing`);
      allGood = false;
    }
  });

  // Check dependencies
  const requiredDeps = ['@supabase/supabase-js', 'electron-store', 'electron-updater'];
  requiredDeps.forEach(dep => {
    if (packageJson.dependencies && packageJson.dependencies[dep]) {
      console.log(`✅ Dependency "${dep}" installed`);
    } else {
      console.log(`❌ Dependency "${dep}" missing`);
      allGood = false;
    }
  });

  // Check devDependencies
  const requiredDevDeps = ['electron', 'electron-builder', 'concurrently', 'wait-on'];
  requiredDevDeps.forEach(dep => {
    if (packageJson.devDependencies && packageJson.devDependencies[dep]) {
      console.log(`✅ Dev dependency "${dep}" installed`);
    } else {
      console.log(`❌ Dev dependency "${dep}" missing`);
      allGood = false;
    }
  });

} catch (error) {
  console.log('❌ Error reading package.json:', error.message);
  allGood = false;
}

console.log('\n🔧 Checking frontend Supabase integration...');

const frontendSupabaseFiles = [
  'frontend/src/services/supabase.js',
  'frontend/src/services/syncService.js',
  'frontend/src/utils/offlineStorage.js',
  'frontend/src/components/SupabaseConfig.jsx'
];

frontendSupabaseFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - MISSING`);
    allGood = false;
  }
});

console.log('\n🗄️  Checking database migration files...');

const migrationFiles = [
  'scripts/supabase-migration.sql',
  'scripts/migrate-to-supabase.js',
  'setup-supabase.js'
];

migrationFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - MISSING`);
    allGood = false;
  }
});

console.log('\n📋 Summary:');

if (allGood) {
  console.log('🎉 All checks passed! Your Electron setup looks good.');
  console.log('\nNext steps:');
  console.log('1. Run "npm install" to install dependencies');
  console.log('2. Run "node setup-supabase.js" to set up your database');
  console.log('3. Run "npm run electron-dev" to start the application');
} else {
  console.log('❌ Some issues were found. Please fix them before proceeding.');
  console.log('\nTo fix missing files, make sure you have:');
  console.log('1. Created all required Electron files');
  console.log('2. Installed all dependencies with "npm install"');
  console.log('3. Set up the Supabase integration files');
}

console.log('\n📚 For more information, see ELECTRON_README.md');
