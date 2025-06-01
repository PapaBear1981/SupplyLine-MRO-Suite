const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Supabase configuration
  getSupabaseConfig: () => ipcRenderer.invoke('get-supabase-config'),
  setSupabaseConfig: (config) => ipcRenderer.invoke('set-supabase-config', config),
  
  // App information
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // Dialog methods
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  
  // Event listeners
  onShowSettings: (callback) => ipcRenderer.on('show-settings', callback),
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // Platform information
  platform: process.platform,
  isElectron: true
});

// Log that preload script has loaded
console.log('Preload script loaded successfully');
