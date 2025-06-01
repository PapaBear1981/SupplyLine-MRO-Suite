class OfflineStorage {
  constructor() {
    this.dbName = 'SupplyLineMRO';
    this.dbVersion = 2; // Incremented to force recreation with settings table
    this.db = null;
    this.tables = ['users', 'tools', 'checkouts', 'chemicals', 'audit_log', 'pending_sync', 'settings'];
  }

  async initialize() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        reject(new Error('Failed to open IndexedDB'));
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve(true);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Create object stores for each table
        this.tables.forEach(tableName => {
          if (!db.objectStoreNames.contains(tableName)) {
            // Settings table uses a different key structure
            const keyPath = tableName === 'settings' ? 'id' : 'id';
            const store = db.createObjectStore(tableName, { keyPath });

            // Create indexes for common queries
            if (tableName === 'tools') {
              store.createIndex('tool_number', 'tool_number', { unique: false });
              store.createIndex('location', 'location', { unique: false });
            } else if (tableName === 'users') {
              store.createIndex('employee_number', 'employee_number', { unique: true });
            } else if (tableName === 'checkouts') {
              store.createIndex('tool_id', 'tool_id', { unique: false });
              store.createIndex('user_id', 'user_id', { unique: false });
            } else if (tableName === 'chemicals') {
              store.createIndex('part_number', 'part_number', { unique: false });
              store.createIndex('status', 'status', { unique: false });
            }
            // Settings table doesn't need indexes
          }
        });
      };
    });
  }

  async getTable(tableName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([tableName], 'readonly');
      const store = transaction.objectStore(tableName);
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        reject(new Error(`Failed to get data from ${tableName}`));
      };
    });
  }

  async getItem(tableName, id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([tableName], 'readonly');
      const store = transaction.objectStore(tableName);
      const request = store.get(id);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(new Error(`Failed to get item ${id} from ${tableName}`));
      };
    });
  }

  async insertItem(tableName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([tableName], 'readwrite');
      const store = transaction.objectStore(tableName);
      
      // Ensure we have timestamps
      const now = new Date().toISOString();
      const itemToInsert = {
        ...data,
        created_at: data.created_at || now,
        updated_at: data.updated_at || now
      };

      const request = store.add(itemToInsert);

      request.onsuccess = () => {
        resolve(itemToInsert);
      };

      request.onerror = () => {
        reject(new Error(`Failed to insert item into ${tableName}`));
      };
    });
  }

  async updateItem(tableName, id, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([tableName], 'readwrite');
      const store = transaction.objectStore(tableName);
      
      // Get existing item first
      const getRequest = store.get(id);
      
      getRequest.onsuccess = () => {
        const existingItem = getRequest.result;
        if (!existingItem) {
          reject(new Error(`Item ${id} not found in ${tableName}`));
          return;
        }

        // Merge with existing data and update timestamp
        const updatedItem = {
          ...existingItem,
          ...data,
          id: id, // Ensure ID doesn't change
          updated_at: new Date().toISOString()
        };

        const putRequest = store.put(updatedItem);
        
        putRequest.onsuccess = () => {
          resolve(updatedItem);
        };

        putRequest.onerror = () => {
          reject(new Error(`Failed to update item ${id} in ${tableName}`));
        };
      };

      getRequest.onerror = () => {
        reject(new Error(`Failed to get item ${id} from ${tableName}`));
      };
    });
  }

  async deleteItem(tableName, id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([tableName], 'readwrite');
      const store = transaction.objectStore(tableName);
      const request = store.delete(id);

      request.onsuccess = () => {
        resolve(true);
      };

      request.onerror = () => {
        reject(new Error(`Failed to delete item ${id} from ${tableName}`));
      };
    });
  }

  async clearTable(tableName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([tableName], 'readwrite');
      const store = transaction.objectStore(tableName);
      const request = store.clear();

      request.onsuccess = () => {
        resolve(true);
      };

      request.onerror = () => {
        reject(new Error(`Failed to clear table ${tableName}`));
      };
    });
  }

  async query(tableName, indexName, value) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([tableName], 'readonly');
      const store = transaction.objectStore(tableName);
      
      let request;
      if (indexName) {
        const index = store.index(indexName);
        request = index.getAll(value);
      } else {
        request = store.getAll();
      }

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        reject(new Error(`Failed to query ${tableName}`));
      };
    });
  }

  // Pending sync operations
  async addPendingSync(tableName, data) {
    const syncItem = {
      id: `${tableName}_${data.id || Date.now()}`,
      tableName,
      data,
      timestamp: new Date().toISOString(),
      retryCount: 0
    };

    return this.insertItem('pending_sync', syncItem);
  }

  async getPendingSync() {
    return this.getTable('pending_sync');
  }

  async removePendingSync(tableName, itemId) {
    const pendingItems = await this.getPendingSync();
    const itemToRemove = pendingItems.find(item => 
      item.tableName === tableName && item.data.id === itemId
    );

    if (itemToRemove) {
      return this.deleteItem('pending_sync', itemToRemove.id);
    }
  }

  // Utility methods
  async setSetting(key, value) {
    const data = {
      id: key,
      value: value,
      timestamp: new Date().toISOString()
    };

    return new Promise((resolve, reject) => {
      try {
        // Check if settings store exists
        if (!this.db.objectStoreNames.contains('settings')) {
          // Fallback to localStorage if settings store doesn't exist
          localStorage.setItem(key, JSON.stringify(value));
          resolve(true);
          return;
        }

        const transaction = this.db.transaction(['settings'], 'readwrite');
        const store = transaction.objectStore('settings');
        const request = store.put(data);

        request.onsuccess = () => {
          resolve(true);
        };

        request.onerror = () => {
          // Fallback to localStorage
          localStorage.setItem(key, JSON.stringify(value));
          resolve(true);
        };
      } catch (error) {
        // Fallback to localStorage
        localStorage.setItem(key, JSON.stringify(value));
        resolve(true);
      }
    });
  }

  async getSetting(key) {
    return new Promise((resolve, reject) => {
      try {
        // Check if settings store exists
        if (!this.db.objectStoreNames.contains('settings')) {
          // Fallback to localStorage if settings store doesn't exist
          const value = localStorage.getItem(key);
          resolve(value ? JSON.parse(value) : null);
          return;
        }

        const transaction = this.db.transaction(['settings'], 'readonly');
        const store = transaction.objectStore('settings');
        const request = store.get(key);

        request.onsuccess = () => {
          if (request.result) {
            resolve(request.result.value);
          } else {
            // Fallback to localStorage
            const value = localStorage.getItem(key);
            resolve(value ? JSON.parse(value) : null);
          }
        };

        request.onerror = () => {
          // Fallback to localStorage
          const value = localStorage.getItem(key);
          resolve(value ? JSON.parse(value) : null);
        };
      } catch (error) {
        // Fallback to localStorage
        const value = localStorage.getItem(key);
        resolve(value ? JSON.parse(value) : null);
      }
    });
  }

  // Database management
  async exportData() {
    const exportData = {};
    
    for (const tableName of this.tables) {
      if (tableName !== 'pending_sync') {
        exportData[tableName] = await this.getTable(tableName);
      }
    }

    return exportData;
  }

  async importData(data) {
    for (const [tableName, items] of Object.entries(data)) {
      if (this.tables.includes(tableName) && tableName !== 'pending_sync') {
        await this.clearTable(tableName);
        
        for (const item of items) {
          await this.insertItem(tableName, item);
        }
      }
    }
  }

  async getStorageInfo() {
    const info = {
      tables: {},
      totalSize: 0
    };

    for (const tableName of this.tables) {
      const data = await this.getTable(tableName);
      info.tables[tableName] = {
        count: data.length,
        size: JSON.stringify(data).length
      };
      info.totalSize += info.tables[tableName].size;
    }

    return info;
  }
}

// Create singleton instance
const offlineStorage = new OfflineStorage();

export default offlineStorage;
