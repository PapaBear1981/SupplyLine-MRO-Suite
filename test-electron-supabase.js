#!/usr/bin/env node

/**
 * Electron + Supabase Integration Test Script
 * 
 * This script tests the Electron app's Supabase integration
 * Run this in the browser console of the Electron app
 */

console.log('🧪 Starting Electron + Supabase Integration Tests...\n');

// Test 1: Check if Electron API is available
function testElectronAPI() {
  console.log('📱 Test 1: Electron API Availability');
  
  if (typeof window.electronAPI !== 'undefined') {
    console.log('✅ window.electronAPI is available');
    console.log('✅ Platform:', window.electronAPI.platform);
    console.log('✅ isElectron:', window.electronAPI.isElectron);
    return true;
  } else {
    console.log('❌ window.electronAPI is not available');
    return false;
  }
}

// Test 2: Check Supabase service initialization
async function testSupabaseService() {
  console.log('\n🗄️  Test 2: Supabase Service');
  
  try {
    // Check if supabaseService is available globally
    if (typeof window.supabaseService === 'undefined') {
      console.log('⚠️  supabaseService not available globally, checking import...');
      
      // Try to access through module system
      const module = await import('./src/services/supabase.js');
      const supabaseService = module.default;
      
      if (supabaseService) {
        console.log('✅ Supabase service imported successfully');
        window.supabaseService = supabaseService; // Make it available globally for testing
      } else {
        console.log('❌ Failed to import Supabase service');
        return false;
      }
    }
    
    const isReady = window.supabaseService.isReady();
    console.log('✅ Supabase service ready:', isReady);
    
    if (isReady) {
      const config = window.supabaseService.getConfig();
      console.log('✅ Supabase URL configured:', config.url ? 'Yes' : 'No');
      console.log('✅ Supabase key configured:', config.key ? 'Yes' : 'No');
    }
    
    return isReady;
  } catch (error) {
    console.log('❌ Supabase service test failed:', error.message);
    return false;
  }
}

// Test 3: Check offline storage
async function testOfflineStorage() {
  console.log('\n💾 Test 3: Offline Storage');
  
  try {
    // Try to access offline storage
    const module = await import('./src/utils/offlineStorage.js');
    const offlineStorage = module.default;
    
    // Test basic storage operations
    await offlineStorage.setItem('test_key', 'test_value');
    const value = await offlineStorage.getItem('test_key');
    
    if (value === 'test_value') {
      console.log('✅ Offline storage read/write working');
    } else {
      console.log('❌ Offline storage read/write failed');
      return false;
    }
    
    // Test table operations
    const users = await offlineStorage.getTable('users');
    console.log('✅ Users table accessible, count:', users.length);
    
    const tools = await offlineStorage.getTable('tools');
    console.log('✅ Tools table accessible, count:', tools.length);
    
    return true;
  } catch (error) {
    console.log('❌ Offline storage test failed:', error.message);
    return false;
  }
}

// Test 4: Check sync service
async function testSyncService() {
  console.log('\n🔄 Test 4: Sync Service');
  
  try {
    const module = await import('./src/services/syncService.js');
    const syncService = module.default;
    
    const status = syncService.getStatus();
    console.log('✅ Sync service status:');
    console.log('  - Online:', status.isOnline);
    console.log('  - Sync in progress:', status.syncInProgress);
    console.log('  - Last sync:', status.lastSyncTime || 'Never');
    console.log('  - Queue length:', status.queueLength);
    console.log('  - Supabase ready:', status.supabaseReady);
    
    return true;
  } catch (error) {
    console.log('❌ Sync service test failed:', error.message);
    return false;
  }
}

// Test 5: Test Supabase connection
async function testSupabaseConnection() {
  console.log('\n🌐 Test 5: Supabase Connection');
  
  try {
    if (!window.supabaseService || !window.supabaseService.isReady()) {
      console.log('⚠️  Supabase service not ready, skipping connection test');
      return false;
    }
    
    const isConnected = await window.supabaseService.testConnection();
    console.log('✅ Supabase connection test:', isConnected ? 'PASSED' : 'FAILED');
    
    if (isConnected) {
      // Try a simple query
      const { data, error } = await window.supabaseService.select('users', 'id, name', {});
      
      if (error) {
        console.log('⚠️  Query test failed:', error.message);
      } else {
        console.log('✅ Query test passed, users found:', data ? data.length : 0);
      }
    }
    
    return isConnected;
  } catch (error) {
    console.log('❌ Supabase connection test failed:', error.message);
    return false;
  }
}

// Test 6: Test data synchronization
async function testDataSync() {
  console.log('\n🔄 Test 6: Data Synchronization');
  
  try {
    if (!window.supabaseService || !window.supabaseService.isReady()) {
      console.log('⚠️  Supabase service not ready, skipping sync test');
      return false;
    }
    
    // Create a test record locally
    const testData = {
      id: Date.now(),
      name: 'Test User for Sync',
      employee_number: `TEST${Date.now()}`,
      department: 'Testing',
      password_hash: 'test_hash',
      is_admin: false,
      is_active: true
    };
    
    console.log('📝 Creating test user locally...');
    const offlineModule = await import('./src/utils/offlineStorage.js');
    const offlineStorage = offlineModule.default;
    
    await offlineStorage.insertItem('users', testData);
    console.log('✅ Test user created locally');
    
    // Try to sync to Supabase
    console.log('🔄 Attempting to sync to Supabase...');
    const { data, error } = await window.supabaseService.insert('users', testData);
    
    if (error) {
      console.log('⚠️  Sync to Supabase failed:', error.message);
      return false;
    } else {
      console.log('✅ Sync to Supabase successful');
      
      // Clean up - delete the test record
      if (data && data[0]) {
        await window.supabaseService.delete('users', data[0].id);
        console.log('✅ Test record cleaned up');
      }
    }
    
    return true;
  } catch (error) {
    console.log('❌ Data sync test failed:', error.message);
    return false;
  }
}

// Main test runner
async function runAllTests() {
  console.log('🚀 Running Electron + Supabase Integration Tests\n');
  
  const results = {
    electronAPI: false,
    supabaseService: false,
    offlineStorage: false,
    syncService: false,
    supabaseConnection: false,
    dataSync: false
  };
  
  try {
    results.electronAPI = testElectronAPI();
    results.supabaseService = await testSupabaseService();
    results.offlineStorage = await testOfflineStorage();
    results.syncService = await testSyncService();
    results.supabaseConnection = await testSupabaseConnection();
    results.dataSync = await testDataSync();
    
    // Summary
    console.log('\n📊 Test Results Summary:');
    console.log('========================');
    
    const passed = Object.values(results).filter(r => r).length;
    const total = Object.keys(results).length;
    
    Object.entries(results).forEach(([test, result]) => {
      console.log(`${result ? '✅' : '❌'} ${test}: ${result ? 'PASSED' : 'FAILED'}`);
    });
    
    console.log(`\n🎯 Overall: ${passed}/${total} tests passed`);
    
    if (passed === total) {
      console.log('🎉 All tests passed! Electron + Supabase integration is working correctly.');
    } else {
      console.log('⚠️  Some tests failed. Check the details above.');
    }
    
    return results;
    
  } catch (error) {
    console.log('❌ Test runner failed:', error.message);
    return results;
  }
}

// Export for use in browser console
if (typeof window !== 'undefined') {
  window.runElectronSupabaseTests = runAllTests;
  window.testElectronAPI = testElectronAPI;
  window.testSupabaseService = testSupabaseService;
  window.testOfflineStorage = testOfflineStorage;
  window.testSyncService = testSyncService;
  window.testSupabaseConnection = testSupabaseConnection;
  window.testDataSync = testDataSync;
  
  console.log('🔧 Test functions available in console:');
  console.log('  - runElectronSupabaseTests() - Run all tests');
  console.log('  - testElectronAPI() - Test Electron API');
  console.log('  - testSupabaseService() - Test Supabase service');
  console.log('  - testOfflineStorage() - Test offline storage');
  console.log('  - testSyncService() - Test sync service');
  console.log('  - testSupabaseConnection() - Test Supabase connection');
  console.log('  - testDataSync() - Test data synchronization');
}

// Auto-run if in browser
if (typeof window !== 'undefined' && window.location) {
  console.log('\n🎬 Auto-running tests in 3 seconds...');
  setTimeout(runAllTests, 3000);
}
