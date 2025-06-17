#!/usr/bin/env node

/**
 * Cross-platform backend startup script for Playwright tests
 * Handles Python interpreter detection and virtual environment compatibility
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Detect the appropriate Python command
function getPythonCommand() {
  // On Windows, try 'py' launcher first, then 'python'
  if (process.platform === 'win32') {
    return 'py';
  }
  // On Unix-like systems, try 'python3' first, then 'python'
  return 'python3';
}

// Get the backend directory
const backendDir = path.resolve(__dirname, '..', '..', 'backend');

// Start the backend server
const pythonCmd = getPythonCommand();
const args = ['-m', 'flask', 'run', '--host=0.0.0.0', '--port=5000'];

console.log(`Starting backend server with: ${pythonCmd} ${args.join(' ')}`);
console.log(`Working directory: ${backendDir}`);

const backendProcess = spawn(pythonCmd, args, {
  cwd: backendDir,
  stdio: 'inherit',
  env: {
    ...process.env,
    FLASK_APP: 'app.py',
    FLASK_ENV: 'development',
    PYTHONUNBUFFERED: '1'
  }
});

backendProcess.on('error', (error) => {
  console.error(`Failed to start backend: ${error.message}`);
  
  // Try fallback Python command
  const fallbackCmd = process.platform === 'win32' ? 'python' : 'python';
  console.log(`Trying fallback command: ${fallbackCmd}`);
  
  const fallbackProcess = spawn(fallbackCmd, ['app.py'], {
    cwd: backendDir,
    stdio: 'inherit',
    env: {
      ...process.env,
      FLASK_ENV: 'development',
      PYTHONUNBUFFERED: '1'
    }
  });
  
  fallbackProcess.on('error', (fallbackError) => {
    console.error(`Fallback also failed: ${fallbackError.message}`);
    process.exit(1);
  });
});

backendProcess.on('exit', (code) => {
  if (code !== 0) {
    console.error(`Backend process exited with code ${code}`);
    process.exit(code);
  }
});

// Handle cleanup
process.on('SIGINT', () => {
  console.log('Shutting down backend server...');
  backendProcess.kill('SIGTERM');
});

process.on('SIGTERM', () => {
  console.log('Shutting down backend server...');
  backendProcess.kill('SIGTERM');
});
