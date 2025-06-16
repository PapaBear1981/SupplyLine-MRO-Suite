/**
 * Data seeding utilities for E2E tests
 * Provides functions to set up and tear down test data
 */

import { testUsers, testTools, testChemicals, testCycleCountSchedules, testCalibrationStandards } from '../fixtures/test-data.js';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

/**
 * Make authenticated API request
 * @param {string} endpoint 
 * @param {Object} options 
 * @param {string} token 
 * @returns {Promise<Response>}
 */
async function apiRequest(endpoint, options = {}, token = null) {
  const url = `${BACKEND_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  return response;
}

/**
 * Login and get authentication token
 * @param {Object} credentials 
 * @returns {Promise<string>} token
 */
async function login(credentials) {
  const response = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials)
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return data.token;
}

/**
 * Create a user via API
 * @param {Object} userData 
 * @param {string} adminToken 
 * @returns {Promise<Object>}
 */
async function createUser(userData, adminToken) {
  const response = await apiRequest('/api/users', {
    method: 'POST',
    body: JSON.stringify(userData)
  }, adminToken);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create user: ${response.status} ${error}`);
  }

  return await response.json();
}

/**
 * Create a tool via API
 * @param {Object} toolData 
 * @param {string} token 
 * @returns {Promise<Object>}
 */
async function createTool(toolData, token) {
  const response = await apiRequest('/api/tools', {
    method: 'POST',
    body: JSON.stringify(toolData)
  }, token);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create tool: ${response.status} ${error}`);
  }

  return await response.json();
}

/**
 * Create a chemical via API
 * @param {Object} chemicalData 
 * @param {string} token 
 * @returns {Promise<Object>}
 */
async function createChemical(chemicalData, token) {
  const response = await apiRequest('/api/chemicals', {
    method: 'POST',
    body: JSON.stringify(chemicalData)
  }, token);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create chemical: ${response.status} ${error}`);
  }

  return await response.json();
}

/**
 * Clear all test data from the database
 * @param {string} adminToken 
 */
async function clearTestData(adminToken) {
  console.log('Clearing test data...');

  // Clear in reverse dependency order
  const endpoints = [
    '/api/checkouts',
    '/api/chemicals', 
    '/api/tools',
    '/api/cycle-count/schedules',
    '/api/calibration/standards'
  ];

  for (const endpoint of endpoints) {
    try {
      // Get all items
      const response = await apiRequest(endpoint, { method: 'GET' }, adminToken);
      if (response.ok) {
        const items = await response.json();
        
        // Delete each item that looks like test data
        for (const item of items) {
          const isTestData = 
            (item.tool_number && item.tool_number.startsWith('TEST')) ||
            (item.part_number && item.part_number.startsWith('CHEM')) ||
            (item.name && item.name.includes('Test')) ||
            (item.description && item.description.includes('E2E testing'));

          if (isTestData) {
            await apiRequest(`${endpoint}/${item.id}`, { method: 'DELETE' }, adminToken);
          }
        }
      }
    } catch (error) {
      console.warn(`Warning: Could not clear ${endpoint}:`, error.message);
    }
  }

  console.log('Test data cleared');
}

/**
 * Seed basic test data
 * @param {string} adminToken 
 * @returns {Promise<Object>} Created data IDs
 */
async function seedBasicData(adminToken) {
  console.log('Seeding basic test data...');
  
  const createdData = {
    users: [],
    tools: [],
    chemicals: [],
    schedules: []
  };

  try {
    // Create test users (skip admin as it should already exist)
    for (const [key, userData] of Object.entries(testUsers)) {
      if (key !== 'admin') {
        try {
          const user = await createUser(userData, adminToken);
          createdData.users.push({ key, id: user.id, data: user });
          console.log(`Created user: ${userData.name}`);
        } catch (error) {
          console.warn(`Warning: Could not create user ${userData.name}:`, error.message);
        }
      }
    }

    // Create test tools
    for (const [key, toolData] of Object.entries(testTools)) {
      try {
        const tool = await createTool(toolData, adminToken);
        createdData.tools.push({ key, id: tool.id, data: tool });
        console.log(`Created tool: ${toolData.description}`);
      } catch (error) {
        console.warn(`Warning: Could not create tool ${toolData.description}:`, error.message);
      }
    }

    // Create test chemicals
    for (const [key, chemicalData] of Object.entries(testChemicals)) {
      try {
        const chemical = await createChemical(chemicalData, adminToken);
        createdData.chemicals.push({ key, id: chemical.id, data: chemical });
        console.log(`Created chemical: ${chemicalData.description}`);
      } catch (error) {
        console.warn(`Warning: Could not create chemical ${chemicalData.description}:`, error.message);
      }
    }

    console.log('Basic test data seeded successfully');
    return createdData;

  } catch (error) {
    console.error('Error seeding basic data:', error);
    throw error;
  }
}

/**
 * Complete test data setup for E2E tests
 * @returns {Promise<Object>} Setup result with tokens and data
 */
async function setupTestData() {
  console.log('Setting up test data for E2E tests...');

  try {
    // Login as admin
    const adminToken = await login(testUsers.admin);
    console.log('Admin login successful');

    // Clear existing test data
    await clearTestData(adminToken);

    // Seed fresh test data
    const createdData = await seedBasicData(adminToken);

    console.log('Test data setup complete');
    return {
      adminToken,
      createdData,
      success: true
    };

  } catch (error) {
    console.error('Failed to setup test data:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Cleanup test data after tests
 * @param {string} adminToken 
 */
async function cleanupTestData(adminToken) {
  console.log('Cleaning up test data...');
  
  try {
    await clearTestData(adminToken);
    console.log('Test data cleanup complete');
  } catch (error) {
    console.error('Error during cleanup:', error);
  }
}

export {
  setupTestData,
  cleanupTestData,
  seedBasicData,
  clearTestData,
  login,
  createUser,
  createTool,
  createChemical,
  apiRequest
};
