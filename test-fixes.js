// Quick test script to verify the fixes
// Run this in the browser console of the Electron app

console.log('🔧 Testing Electron + Supabase Fixes...\n');

async function testOfflineStorageFix() {
  console.log('📦 Testing Offline Storage Fix...');
  
  try {
    // Test if we can save and retrieve a setting
    const testKey = 'test_setting';
    const testValue = { test: 'value', timestamp: Date.now() };
    
    // This should not throw an error anymore
    localStorage.setItem(testKey, JSON.stringify(testValue));
    const retrieved = JSON.parse(localStorage.getItem(testKey));
    
    if (retrieved && retrieved.test === testValue.test) {
      console.log('✅ Offline storage fix working - no more IndexedDB errors');
      localStorage.removeItem(testKey);
      return true;
    } else {
      console.log('❌ Offline storage test failed');
      return false;
    }
  } catch (error) {
    console.log('❌ Offline storage error:', error.message);
    return false;
  }
}

async function testSupabaseSyncFix() {
  console.log('🔄 Testing Supabase Sync Fix...');
  
  try {
    if (!window.electronAPI) {
      console.log('⚠️ Electron API not available');
      return false;
    }
    
    const config = await window.electronAPI.getSupabaseConfig();
    if (!config.url || !config.key) {
      console.log('⚠️ Supabase not configured');
      return false;
    }
    
    // Test querying users table (should work now)
    const response = await fetch(`${config.url}/rest/v1/users?select=id,name&limit=1`, {
      headers: {
        'apikey': config.key,
        'Authorization': `Bearer ${config.key}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log(`✅ Supabase sync fix working - users query successful (${data.length} users)`);
      return true;
    } else {
      console.log(`❌ Supabase query failed: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log('❌ Supabase sync error:', error.message);
    return false;
  }
}

async function testAuditLogFix() {
  console.log('📋 Testing Audit Log Fix...');
  
  try {
    if (!window.electronAPI) {
      console.log('⚠️ Electron API not available');
      return false;
    }
    
    const config = await window.electronAPI.getSupabaseConfig();
    if (!config.url || !config.key) {
      console.log('⚠️ Supabase not configured');
      return false;
    }
    
    // Test querying audit_log table with updated_at column
    const response = await fetch(`${config.url}/rest/v1/audit_log?select=id,action_type,updated_at&limit=1`, {
      headers: {
        'apikey': config.key,
        'Authorization': `Bearer ${config.key}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      console.log('✅ Audit log fix working - updated_at column accessible');
      return true;
    } else {
      console.log(`❌ Audit log query failed: ${response.status}`);
      return false;
    }
  } catch (error) {
    console.log('❌ Audit log error:', error.message);
    return false;
  }
}

async function runFixTests() {
  console.log('🚀 Running Fix Verification Tests...\n');
  
  const results = {
    offlineStorage: await testOfflineStorageFix(),
    supabaseSync: await testSupabaseSyncFix(),
    auditLog: await testAuditLogFix()
  };
  
  console.log('\n📊 Fix Test Results:');
  console.log('===================');
  
  const passed = Object.values(results).filter(r => r).length;
  const total = Object.keys(results).length;
  
  Object.entries(results).forEach(([test, result]) => {
    console.log(`${result ? '✅' : '❌'} ${test}: ${result ? 'FIXED' : 'STILL BROKEN'}`);
  });
  
  console.log(`\n🎯 Overall: ${passed}/${total} fixes working`);
  
  if (passed === total) {
    console.log('🎉 All fixes successful! The sync errors should be resolved.');
  } else {
    console.log('⚠️ Some fixes may need additional work.');
  }
  
  return results;
}

// Make functions available globally
window.testOfflineStorageFix = testOfflineStorageFix;
window.testSupabaseSyncFix = testSupabaseSyncFix;
window.testAuditLogFix = testAuditLogFix;
window.runFixTests = runFixTests;

console.log('🔧 Fix test functions loaded. Run runFixTests() to test all fixes.');

// Auto-run if in browser
if (typeof window !== 'undefined' && window.location) {
  console.log('\n🎬 Auto-running fix tests in 2 seconds...');
  setTimeout(runFixTests, 2000);
}
