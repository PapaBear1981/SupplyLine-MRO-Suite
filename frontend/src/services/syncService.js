import supabaseService from './supabase.js';
import offlineStorage from '../utils/offlineStorage.js';

class SyncService {
  constructor() {
    this.isOnline = navigator.onLine;
    this.syncInProgress = false;
    this.syncQueue = [];
    this.lastSyncTime = null;
    this.syncInterval = null;
    this.conflictResolutionStrategy = 'server_wins'; // 'server_wins', 'client_wins', 'manual'
    this.retryAttempts = new Map(); // Track retry attempts per item
    this.maxRetries = 5;
    this.baseRetryDelay = 1000; // 1 second
    
    // Listen for online/offline events
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.handleOnline();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.handleOffline();
    });
  }

  async initialize() {
    try {
      // Load last sync time from storage
      this.lastSyncTime = await offlineStorage.getSetting('lastSyncTime');
      
      // Start periodic sync if online
      if (this.isOnline && supabaseService.isReady()) {
        this.startPeriodicSync();
      }
      
      return true;
    } catch (error) {
      console.error('Failed to initialize sync service:', error);
      return false;
    }
  }

  startPeriodicSync(intervalMs = 30000) { // 30 seconds default
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
    
    this.syncInterval = setInterval(() => {
      if (this.isOnline && supabaseService.isReady() && !this.syncInProgress) {
        this.performSync();
      }
    }, intervalMs);
  }

  stopPeriodicSync() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  async handleOnline() {
    console.log('Device came online, starting sync...');
    if (supabaseService.isReady()) {
      await this.performSync();
      this.startPeriodicSync();
    }
  }

  handleOffline() {
    console.log('Device went offline, stopping periodic sync...');
    this.stopPeriodicSync();
  }

  async performSync() {
    if (this.syncInProgress) {
      console.log('Sync already in progress, skipping...');
      return;
    }

    this.syncInProgress = true;
    console.log('Starting data synchronization...');

    try {
      // Sync each table
      const tables = ['users', 'tools', 'checkouts', 'chemicals'];

      for (const table of tables) {
        await this.syncTable(table);
      }

      // Process sync queue (pending operations)
      await this.processSyncQueue();

      // Update last sync time
      this.lastSyncTime = new Date().toISOString();
      try {
        await offlineStorage.setSetting('lastSyncTime', this.lastSyncTime);
      } catch (error) {
        console.warn('Failed to save last sync time:', error.message);
        // Continue anyway, this is not critical
      }

      console.log('Synchronization completed successfully');
      
      // Emit sync complete event
      window.dispatchEvent(new CustomEvent('syncComplete', {
        detail: { success: true, timestamp: this.lastSyncTime }
      }));

    } catch (error) {
      console.error('Synchronization failed:', error);
      
      // Emit sync error event
      window.dispatchEvent(new CustomEvent('syncError', {
        detail: { error: error.message, timestamp: new Date().toISOString() }
      }));
    } finally {
      this.syncInProgress = false;
    }
  }

  async syncTable(tableName) {
    try {
      // Get local data
      const localData = await offlineStorage.getTable(tableName);

      // Get remote data (only changes since last sync)
      let remoteQuery = {};
      if (this.lastSyncTime) {
        // Only use updated_at filter for tables that have this column
        const tablesWithUpdatedAt = ['users', 'tools', 'checkouts', 'chemicals'];
        if (tablesWithUpdatedAt.includes(tableName)) {
          remoteQuery = {
            updated_at: { operator: 'gte', value: this.lastSyncTime }
          };
        }
      }

      const { data: remoteData, error } = await supabaseService.select(tableName, '*', remoteQuery);

      if (error) {
        console.error(`Failed to fetch remote data for ${tableName}:`, error);
        return;
      }

      // Merge data and resolve conflicts
      await this.mergeTableData(tableName, localData, remoteData || []);

    } catch (error) {
      console.error(`Failed to sync table ${tableName}:`, error);
    }
  }

  async mergeTableData(tableName, localData, remoteData) {
    const localMap = new Map(localData.map(item => [item.id, item]));
    const remoteMap = new Map(remoteData.map(item => [item.id, item]));
    
    // Handle remote changes
    for (const remoteItem of remoteData) {
      const localItem = localMap.get(remoteItem.id);
      
      if (!localItem) {
        // New item from server
        await offlineStorage.insertItem(tableName, remoteItem);
      } else {
        // Check for conflicts
        const conflict = this.detectConflict(localItem, remoteItem);
        
        if (conflict) {
          const resolvedItem = await this.resolveConflict(tableName, localItem, remoteItem);
          await offlineStorage.updateItem(tableName, resolvedItem.id, resolvedItem);
        } else if (new Date(remoteItem.updated_at) > new Date(localItem.updated_at)) {
          // Remote is newer, update local
          await offlineStorage.updateItem(tableName, remoteItem.id, remoteItem);
        }
      }
    }

    // Handle local changes that need to be pushed to server
    for (const localItem of localData) {
      if (localItem._pendingSync) {
        await this.pushLocalChange(tableName, localItem);
      }
    }
  }

  detectConflict(localItem, remoteItem) {
    // Simple conflict detection based on timestamps
    const localTime = new Date(localItem.updated_at || localItem.created_at);
    const remoteTime = new Date(remoteItem.updated_at || remoteItem.created_at);
    const lastSync = new Date(this.lastSyncTime || 0);
    
    // Conflict if both items were modified since last sync
    return localTime > lastSync && remoteTime > lastSync && localTime.getTime() !== remoteTime.getTime();
  }

  async resolveConflict(tableName, localItem, remoteItem) {
    switch (this.conflictResolutionStrategy) {
      case 'server_wins':
        return remoteItem;
      
      case 'client_wins':
        // Push local changes to server
        await this.pushLocalChange(tableName, localItem);
        return localItem;
      
      case 'manual':
        // Emit conflict event for manual resolution
        return new Promise((resolve) => {
          window.dispatchEvent(new CustomEvent('syncConflict', {
            detail: {
              tableName,
              localItem,
              remoteItem,
              resolve
            }
          }));
        });
      
      default:
        return remoteItem;
    }
  }

  async pushLocalChange(tableName, localItem) {
    try {
      const itemToSync = { ...localItem };
      delete itemToSync._pendingSync;
      delete itemToSync._localId;
      
      if (localItem._operation === 'insert') {
        const { data, error } = await supabaseService.insert(tableName, itemToSync);
        if (!error && data?.[0]) {
          // Update local item with server-generated ID
          await offlineStorage.updateItem(tableName, localItem.id, data[0]);
        }
      } else if (localItem._operation === 'update') {
        await supabaseService.update(tableName, localItem.id, itemToSync);
      } else if (localItem._operation === 'delete') {
        await supabaseService.delete(tableName, localItem.id);
        await offlineStorage.deleteItem(tableName, localItem.id);
      }
      
      // Remove from local pending sync
      await offlineStorage.removePendingSync(tableName, localItem.id);
      
    } catch (error) {
      console.error(`Failed to push local change for ${tableName}:`, error);
      // Use exponential backoff for retries
      this.pushLocalChangeWithRetry(tableName, localItem, 0);
    }
  }

  async processSyncQueue() {
    while (this.syncQueue.length > 0) {
      const { tableName, item } = this.syncQueue.shift();
      await this.pushLocalChange(tableName, item);
    }
  }

  addToSyncQueue(tableName, item) {
    this.syncQueue.push({ tableName, item });
  }

  async pushLocalChangeWithRetry(tableName, item, attempt = 0) {
    const itemKey = `${tableName}-${item.id}`;

    try {
      await this.pushLocalChange(tableName, item);
      this.retryAttempts.delete(itemKey);
    } catch (error) {
      if (attempt < this.maxRetries) {
        const delay = this.baseRetryDelay * Math.pow(2, attempt);
        console.log(`Retrying sync for ${itemKey} in ${delay}ms (attempt ${attempt + 1}/${this.maxRetries})`);

        setTimeout(() => {
          this.pushLocalChangeWithRetry(tableName, item, attempt + 1);
        }, delay);
      } else {
        console.error(`Max retries reached for ${itemKey}, giving up`);
        this.retryAttempts.delete(itemKey);
        // Add to sync queue as last resort
        this.addToSyncQueue(tableName, item);
      }
    }
  }

  // Public methods for manual operations
  async forceSync() {
    if (!this.isOnline || !supabaseService.isReady()) {
      throw new Error('Cannot sync while offline or Supabase not configured');
    }
    
    await this.performSync();
  }

  async queueLocalChange(tableName, operation, data) {
    // Mark data for sync
    const syncData = {
      ...data,
      _pendingSync: true,
      _operation: operation,
      _timestamp: new Date().toISOString()
    };
    
    await offlineStorage.addPendingSync(tableName, syncData);
    
    // Try to sync immediately if online
    if (this.isOnline && supabaseService.isReady() && !this.syncInProgress) {
      setTimeout(() => this.performSync(), 1000); // Debounce
    }
  }

  getStatus() {
    return {
      isOnline: this.isOnline,
      syncInProgress: this.syncInProgress,
      lastSyncTime: this.lastSyncTime,
      queueLength: this.syncQueue.length,
      supabaseReady: supabaseService.isReady()
    };
  }

  setConflictResolutionStrategy(strategy) {
    this.conflictResolutionStrategy = strategy;
  }
}

// Create singleton instance
const syncService = new SyncService();

export default syncService;
