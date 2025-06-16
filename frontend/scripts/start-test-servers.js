#!/usr/bin/env node

/**
 * Script to start both frontend and backend servers for E2E testing
 * This provides better control over server startup and health checks
 */

import { spawn } from 'child_process';
import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const FRONTEND_PORT = process.env.FRONTEND_PORT || 5173;
const BACKEND_PORT = process.env.BACKEND_PORT || 5000;
const FRONTEND_URL = `http://localhost:${FRONTEND_PORT}`;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

let frontendProcess = null;
let backendProcess = null;

// Health check function
async function healthCheck(url, maxRetries = 30, interval = 2000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return true;
      }
    } catch (error) {
      // Server not ready yet
    }
    
    console.log(`Waiting for server at ${url}... (${i + 1}/${maxRetries})`);
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error(`Server at ${url} failed to start within ${maxRetries * interval / 1000} seconds`);
}

// Start frontend server
function startFrontend() {
  return new Promise((resolve, reject) => {
    console.log('Starting frontend server...');
    
    frontendProcess = spawn('npm', ['run', 'dev'], {
      cwd: path.join(__dirname, '..'),
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true
    });

    frontendProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Frontend] ${output.trim()}`);
      
      // Check if server is ready
      if (output.includes('Local:') || output.includes('ready')) {
        resolve();
      }
    });

    frontendProcess.stderr.on('data', (data) => {
      console.error(`[Frontend Error] ${data.toString().trim()}`);
    });

    frontendProcess.on('error', (error) => {
      reject(new Error(`Failed to start frontend: ${error.message}`));
    });

    frontendProcess.on('exit', (code) => {
      if (code !== 0) {
        reject(new Error(`Frontend process exited with code ${code}`));
      }
    });
  });
}

// Start backend server
function startBackend() {
  return new Promise((resolve, reject) => {
    console.log('Starting backend server...');
    
    const backendPath = path.join(__dirname, '..', '..', 'backend');
    
    backendProcess = spawn('python', ['app.py'], {
      cwd: backendPath,
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true,
      env: {
        ...process.env,
        FLASK_ENV: 'development',
        PYTHONUNBUFFERED: '1'
      }
    });

    backendProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Backend] ${output.trim()}`);
      
      // Check if server is ready
      if (output.includes('Running on') || output.includes('Application starting')) {
        resolve();
      }
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`[Backend Error] ${data.toString().trim()}`);
    });

    backendProcess.on('error', (error) => {
      reject(new Error(`Failed to start backend: ${error.message}`));
    });

    backendProcess.on('exit', (code) => {
      if (code !== 0) {
        reject(new Error(`Backend process exited with code ${code}`));
      }
    });
  });
}

// Cleanup function
function cleanup() {
  console.log('Cleaning up servers...');
  
  if (frontendProcess) {
    frontendProcess.kill();
    frontendProcess = null;
  }
  
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

// Main function
async function main() {
  try {
    // Handle cleanup on exit
    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);
    process.on('exit', cleanup);

    // Start servers
    await Promise.all([
      startFrontend(),
      startBackend()
    ]);

    // Wait a bit for servers to fully initialize
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Health checks
    console.log('Performing health checks...');
    await healthCheck(FRONTEND_URL);
    console.log('✅ Frontend server is ready');
    
    await healthCheck(`${BACKEND_URL}/api/health`);
    console.log('✅ Backend server is ready');

    console.log('🚀 Both servers are ready for E2E testing!');
    console.log(`Frontend: ${FRONTEND_URL}`);
    console.log(`Backend: ${BACKEND_URL}`);

    // Keep the script running
    process.stdin.resume();

  } catch (error) {
    console.error('❌ Failed to start servers:', error.message);
    cleanup();
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { startFrontend, startBackend, healthCheck, cleanup };
