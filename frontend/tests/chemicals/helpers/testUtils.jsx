/**
 * Test Utilities for Chemical Component Testing
 *
 * Provides helper functions for rendering components with Redux and Router context
 */

import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { BrowserRouter } from 'react-router-dom';

// Import reducers
import chemicalsReducer from '../../../src/store/chemicalsSlice';
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
        chemicals: chemicalsReducer,
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
 * Create mock authenticated user state (Materials department)
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
    token: 'mock-admin-jwt-token',
  },
};

/**
 * Create mock chemical
 */
export const mockChemical = {
  id: 1,
  part_number: 'CHEM-001',
  lot_number: 'LOT-001',
  description: 'Test Chemical',
  manufacturer: 'Test Manufacturer',
  category: 'Solvent',
  quantity: 10.5,
  unit: 'L',
  status: 'available',
  location: 'A1-B2',
  warehouse_id: 1,
  expiration_date: '2025-12-31',
  reorder_status: 'not_needed',
};

/**
 * Create mock chemical needing reorder
 */
export const mockChemicalNeedingReorder = {
  id: 2,
  part_number: 'CHEM-002',
  lot_number: 'LOT-002',
  description: 'Low Stock Chemical',
  manufacturer: 'Test Manufacturer',
  category: 'Acid',
  quantity: 1.0,
  unit: 'L',
  status: 'low_stock',
  location: 'A2-B3',
  warehouse_id: 1,
  expiration_date: '2025-06-30',
  reorder_status: 'needed',
  needs_reorder: true,
};

/**
 * Create mock chemicals state
 */
export const mockChemicalsState = {
  chemicals: [mockChemical, mockChemicalNeedingReorder],
  archivedChemicals: [],
  chemicalsNeedingReorder: [mockChemicalNeedingReorder],
  chemicalsOnOrder: [],
  chemicalsExpiringSoon: [],
  currentChemical: null,
  issuances: [],
  loading: false,
  error: null,
};
