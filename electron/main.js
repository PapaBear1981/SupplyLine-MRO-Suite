const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Initialize electron-store for persistent settings (using dynamic import)
let Store;
let store;

let mainWindow;
let backendProcess;

// Development mode check
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    show: false,
    titleBarStyle: 'default'
  });

  // Load the app
  if (isDev) {
    // Development mode - load from dev server
    mainWindow.loadURL('http://localhost:5173');
    // Don't open DevTools automatically - user can open with F12 or Ctrl+Shift+I
    // mainWindow.webContents.openDevTools();
  } else {
    // Production mode - load from built files
    // Try multiple possible frontend locations
    const possibleFrontendPaths = [
      path.join(__dirname, '../frontend/dist/index.html'),  // Standard build location
      path.join(__dirname, 'frontend/dist/index.html'),     // Alternative location
      path.join(__dirname, '../dist/index.html'),           // Simplified location
      path.join(__dirname, 'dist/index.html'),              // Direct location
      path.join(__dirname, 'index.html')                    // Root location
    ];

    let frontendLoaded = false;
    for (const frontendPath of possibleFrontendPaths) {
      if (fs.existsSync(frontendPath)) {
        console.log(`Loading frontend from: ${frontendPath}`);
        mainWindow.loadFile(frontendPath);
        frontendLoaded = true;
        break;
      } else {
        console.log(`Frontend not found at: ${frontendPath}`);
      }
    }

    if (!frontendLoaded) {
      console.error('❌ Frontend files not found in any expected location');
      // Fallback: try to load from localhost (backend might serve static files)
      console.log('Attempting fallback: loading from backend server...');
      mainWindow.loadURL('http://localhost:5000');
    }
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Add keyboard shortcut to toggle DevTools (F12 or Ctrl+Shift+I)
  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.key === 'F12' ||
        (input.control && input.shift && input.key.toLowerCase() === 'i')) {
      mainWindow.webContents.toggleDevTools();
    }
  });
}

function findPythonExecutable() {
  const { execSync } = require('child_process');
  const fs = require('fs');
  const isWindows = process.platform === 'win32';

  console.log('🔍 Starting Python detection...');
  console.log(`Platform: ${process.platform}`);
  console.log(`App directory: ${__dirname}`);

  // First, check for embedded Python in the portable app
  const embeddedPythonPath = path.join(__dirname, '..', '..', 'Python', 'python.exe');
  console.log(`Checking for embedded Python at: ${embeddedPythonPath}`);

  if (fs.existsSync(embeddedPythonPath)) {
    try {
      const output = execSync(`"${embeddedPythonPath}" --version`, {
        encoding: 'utf8',
        timeout: 5000,
        windowsHide: true
      });

      if (output && output.includes('Python')) {
        console.log(`✅ Found embedded Python: ${embeddedPythonPath} - ${output.trim()}`);
        return embeddedPythonPath;
      }
    } catch (error) {
      console.log(`❌ Embedded Python test failed: ${error.message}`);
    }
  } else {
    console.log('❌ No embedded Python found');
  }

  if (!isWindows) {
    // For non-Windows, use simpler detection
    const possiblePaths = ['python3', 'python', '/usr/bin/python3', '/usr/local/bin/python3'];
    for (const pythonPath of possiblePaths) {
      try {
        const output = execSync(`${pythonPath} --version`, { encoding: 'utf8', timeout: 5000 });
        if (output && output.includes('Python')) {
          console.log(`✅ Found system Python: ${pythonPath} - ${output.trim()}`);
          return pythonPath;
        }
      } catch (error) {
        continue;
      }
    }
    return null;
  }

  // Windows-specific detection for system Python
  console.log('🔍 Checking for system Python installation...');
  const possibleCommands = [
    'python',
    'py -3',
    'py',
    'python3'
  ];

  // Try simple commands that should work if Python is in PATH
  for (const cmd of possibleCommands) {
    try {
      console.log(`Testing command: ${cmd}`);
      const output = execSync(`${cmd} --version`, {
        encoding: 'utf8',
        timeout: 10000,
        windowsHide: true
      });

      if (output && output.includes('Python')) {
        console.log(`✅ Found system Python with command: ${cmd} - ${output.trim()}`);
        return cmd;
      }
    } catch (error) {
      console.log(`❌ Command failed: ${cmd} - ${error.message}`);
      continue;
    }
  }

  // If simple commands fail, try specific paths
  const specificPaths = [];

  // Add common installation directories
  for (let version = 38; version <= 313; version++) {
    specificPaths.push(`C:\\Python${version}\\python.exe`);

    if (process.env.LOCALAPPDATA) {
      specificPaths.push(path.join(process.env.LOCALAPPDATA, 'Programs', 'Python', `Python${version}`, 'python.exe'));
    }
    if (process.env.APPDATA) {
      specificPaths.push(path.join(process.env.APPDATA, 'Python', `Python${version}`, 'python.exe'));
    }
  }

  // Test specific paths
  for (const pythonPath of specificPaths) {
    try {
      if (fs.existsSync(pythonPath)) {
        console.log(`Testing specific path: ${pythonPath}`);
        const output = execSync(`"${pythonPath}" --version`, {
          encoding: 'utf8',
          timeout: 5000,
          windowsHide: true
        });

        if (output && output.includes('Python')) {
          console.log(`✅ Found system Python at: ${pythonPath} - ${output.trim()}`);
          return pythonPath;
        }
      }
    } catch (error) {
      console.log(`❌ Specific path failed: ${pythonPath} - ${error.message}`);
      continue;
    }
  }

  console.log('❌ No working Python executable found');
  return null;
}

function showPythonErrorDialog() {
  const { dialog } = require('electron');

  dialog.showErrorBox(
    'Python Not Found',
    'SupplyLine MRO Suite requires Python 3.8 or higher to run.\n\n' +
    'TROUBLESHOOTING:\n' +
    '1. Install Python from https://python.org\n' +
    '2. During installation, CHECK "Add Python to PATH"\n' +
    '3. Try running "python --version" in Command Prompt\n' +
    '4. If that works, restart this application\n' +
    '5. If not, reinstall Python with PATH option checked\n\n' +
    'Alternative: Try using "py" command instead of "python"\n' +
    'This usually works with Python Launcher for Windows.'
  );
}

function startBackendServer() {
  if (isDev) {
    // In development, assume backend is running separately
    return;
  }

  console.log('🚀 Starting backend server...');

  // In production, start the Python backend
  const backendPath = path.join(__dirname, '../backend');
  console.log(`Backend path: ${backendPath}`);

  // Try multiple Python commands in order of preference
  const pythonCommands = ['python', 'py', 'python3', 'py -3'];
  let pythonFound = false;

  for (const pythonCmd of pythonCommands) {
    try {
      console.log(`Trying to start backend with: ${pythonCmd}`);

      const args = pythonCmd.includes(' ') ? pythonCmd.split(' ').concat(['app.py']) : [pythonCmd, 'app.py'];
      const command = args[0];
      const cmdArgs = args.slice(1);

      backendProcess = spawn(command, cmdArgs, {
        cwd: backendPath,
        stdio: 'pipe',
        shell: true,
        env: { ...process.env }
      });

      backendProcess.stdout.on('data', (data) => {
        console.log(`Backend stdout: ${data}`);
      });

      backendProcess.stderr.on('data', (data) => {
        console.error(`Backend stderr: ${data}`);
      });

      backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
        if (code !== 0) {
          console.error(`Backend process failed with code ${code}`);
        }
      });

      backendProcess.on('error', (error) => {
        console.error(`Failed to start backend with ${pythonCmd}: ${error.message}`);
        if (error.code === 'ENOENT' && !pythonFound) {
          // Try next Python command
          return;
        }
      });

      // If we get here, the process started successfully
      pythonFound = true;
      console.log(`✅ Backend started successfully with: ${pythonCmd}`);
      break;

    } catch (error) {
      console.error(`Error starting backend with ${pythonCmd}: ${error.message}`);
      continue;
    }
  }

  if (!pythonFound) {
    console.error('❌ Failed to start backend with any Python command');
    showPythonErrorDialog();
  }
}

function stopBackendServer() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

// App event handlers
app.whenReady().then(async () => {
  // Initialize electron-store with dynamic import
  try {
    Store = (await import('electron-store')).default;
    store = new Store();
  } catch (error) {
    console.error('Failed to load electron-store:', error);
    // Fallback to simple storage
    store = {
      get: (key, defaultValue) => {
        try {
          const value = fs.readFileSync(path.join(app.getPath('userData'), `${key}.json`), 'utf8');
          return JSON.parse(value);
        } catch {
          return defaultValue;
        }
      },
      set: (key, value) => {
        try {
          fs.writeFileSync(path.join(app.getPath('userData'), `${key}.json`), JSON.stringify(value));
        } catch (error) {
          console.error('Failed to save setting:', error);
        }
      }
    };
  }

  createWindow();
  startBackendServer();

  // Set up auto-updater
  if (!isDev) {
    autoUpdater.checkForUpdatesAndNotify();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopBackendServer();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackendServer();
});

// IPC handlers for secure communication
ipcMain.handle('get-supabase-config', () => {
  return {
    url: store.get('supabase.url', ''),
    key: store.get('supabase.key', '')
  };
});

ipcMain.handle('set-supabase-config', (event, config) => {
  store.set('supabase.url', config.url);
  store.set('supabase.key', config.key);
  return true;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

// Auto-updater events
autoUpdater.on('checking-for-update', () => {
  console.log('Checking for update...');
});

autoUpdater.on('update-available', (info) => {
  console.log('Update available.');
});

autoUpdater.on('update-not-available', (info) => {
  console.log('Update not available.');
});

autoUpdater.on('error', (err) => {
  console.log('Error in auto-updater. ' + err);
});

autoUpdater.on('download-progress', (progressObj) => {
  let log_message = "Download speed: " + progressObj.bytesPerSecond;
  log_message = log_message + ' - Downloaded ' + progressObj.percent + '%';
  log_message = log_message + ' (' + progressObj.transferred + "/" + progressObj.total + ')';
  console.log(log_message);
});

autoUpdater.on('update-downloaded', (info) => {
  console.log('Update downloaded');
  autoUpdater.quitAndInstall();
});

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Settings',
          click: () => {
            mainWindow.webContents.send('show-settings');
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About SupplyLine MRO Suite',
              message: `SupplyLine MRO Suite v${app.getVersion()}`,
              detail: 'A comprehensive tool and chemical management system for MRO operations.'
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

app.whenReady().then(() => {
  createMenu();
});
