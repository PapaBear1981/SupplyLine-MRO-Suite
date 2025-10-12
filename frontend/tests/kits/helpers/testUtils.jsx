/**
 * Test Utilities for Kit Component Testing
 * 
 * Provides helper functions for rendering components with Redux and Router context
 */

import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { BrowserRouter } from 'react-router-dom';

// Import reducers
import kitsReducer from '../../../src/store/kitsSlice';
import kitTransfersReducer from '../../../src/store/kitTransfersSlice';
import kitMessagesReducer from '../../../src/store/kitMessagesSlice';
import authReducer from '../../../src/store/authSlice';

/**
 * Render component with Redux Provider and Router
 * 
 * @param {React.Component} ui - Component to render
 * @param {Object} options - Render options
 * @param {Object} options.preloadedState - Initial Redux state
 * @param {Object} options.store - Custom Redux store
 * @returns {Object} Render result with store
 */
export function renderWithProviders(
  ui,
  {
    preloadedState = {},
    store = configureStore({
      reducer: {
        kits: kitsReducer,
        kitTransfers: kitTransfersReducer,
        kitMessages: kitMessagesReducer,
        auth: authReducer,
      },
      preloadedState,
    }),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (
      <Provider store={store}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </Provider>
    );
  }

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

/**
 * Create mock authenticated user state
 */
export const mockAuthState = {
  auth: {
    user: {
      id: 1,
      name: 'Test User',
      employee_number: 'EMP001',
      department: 'Materials',
      is_admin: false,
    },
    isAuthenticated: true,
    token: 'mock-jwt-token',
  },
};

/**
 * Create mock admin user state
 */
export const mockAdminAuthState = {
  auth: {
    user: {
      id: 1,
      name: 'Admin User',
      employee_number: 'ADMIN001',
      department: 'Materials',
      is_admin: true,
    },
    isAuthenticated: true,
    token: 'mock-jwt-token',
  },
};

/**
 * Mock kit data
 */
export const mockKit = {
  id: 1,
  name: 'Test Kit Q400-001',
  aircraft_type_id: 1,
  aircraft_type_name: 'Q400',
  description: 'Test kit for Q400 aircraft',
  status: 'active',
  created_by: 1,
  created_date: '2025-01-01T00:00:00Z',
  box_count: 3,
  item_count: 15,
  expendable_count: 10,
};

/**
 * Mock kit box data
 */
export const mockKitBox = {
  id: 1,
  kit_id: 1,
  box_number: '1',
  box_type: 'expendable',
  description: 'Expendable items box',
};

/**
 * Mock kit expendable data
 */
export const mockKitExpendable = {
  id: 1,
  kit_id: 1,
  box_id: 1,
  part_number: 'EXP-001',
  description: 'Safety Wire',
  quantity: 100.0,
  unit: 'ft',
  minimum_stock_level: 50.0,
  status: 'available',
};

/**
 * Mock kit transfer data
 */
export const mockKitTransfer = {
  id: 1,
  item_type: 'expendable',
  item_id: 1,
  from_location_type: 'kit',
  from_location_id: 1,
  to_location_type: 'kit',
  to_location_id: 2,
  quantity: 25.0,
  transferred_by: 1,
  transfer_date: '2025-01-01T00:00:00Z',
  status: 'pending',
  notes: 'Test transfer',
};

/**
 * Mock kit message data
 */
export const mockKitMessage = {
  id: 1,
  kit_id: 1,
  sender_id: 1,
  sender_name: 'Test User',
  recipient_id: 2,
  recipient_name: 'Materials User',
  subject: 'Low Stock Alert',
  message: 'Safety wire is running low',
  is_read: false,
  sent_date: '2025-01-01T00:00:00Z',
  parent_message_id: null,
  reply_count: 0,
};

/**
 * Mock kit reorder request data
 */
export const mockReorderRequest = {
  id: 1,
  kit_id: 1,
  item_type: 'expendable',
  item_id: 1,
  part_number: 'EXP-001',
  description: 'Safety Wire',
  quantity_requested: 50.0,
  priority: 'high',
  requested_by: 1,
  requested_date: '2025-01-01T00:00:00Z',
  status: 'pending',
  is_automatic: true,
};

/**
 * Mock aircraft type data
 */
export const mockAircraftType = {
  id: 1,
  name: 'Q400',
  description: 'Bombardier Q400',
  is_active: true,
};

/**
 * Create mock kits state
 */
export const mockKitsState = {
  kits: {
    kits: [mockKit],
    currentKit: mockKit,
    aircraftTypes: [mockAircraftType],
    boxes: [mockKitBox],
    expendables: [mockKitExpendable],
    loading: false,
    error: null,
  },
};

/**
 * Create mock kit transfers state
 */
export const mockKitTransfersState = {
  kitTransfers: {
    transfers: [mockKitTransfer],
    currentTransfer: mockKitTransfer,
    loading: false,
    error: null,
  },
};

/**
 * Create mock kit messages state
 */
export const mockKitMessagesState = {
  kitMessages: {
    messages: [mockKitMessage],
    currentMessage: mockKitMessage,
    unreadCount: 1,
    loading: false,
    error: null,
  },
};

/**
 * Mock API response helper
 */
export const mockApiResponse = (data, delay = 0) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data });
    }, delay);
  });
};

/**
 * Mock API error helper
 */
export const mockApiError = (message = 'API Error', status = 500, delay = 0) => {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject({
        response: {
          data: { error: message },
          status,
        },
      });
    }, delay);
  });
};

// Re-export everything from @testing-library/react
export * from '@testing-library/react';

