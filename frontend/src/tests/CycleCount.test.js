/**
 * Comprehensive test suite for cycle count frontend components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import '@testing-library/jest-dom';

// Import components to test
import CycleCountDashboard from '../components/cycleCount/CycleCountDashboard';
import CycleCountScheduleForm from '../components/cycleCount/CycleCountScheduleForm';
import CycleCountBatchForm from '../components/cycleCount/CycleCountBatchForm';
import CycleCountItemList from '../components/cycleCount/CycleCountItemList';
import MobileCycleCountBatch from '../components/cycleCount/mobile/MobileCycleCountBatch';

// Import Redux slices
import cycleCountReducer from '../store/cycleCountSlice';
import authReducer from '../store/authSlice';

// Mock data
const mockSchedules = [
  {
    id: 1,
    name: 'Weekly Tool Count',
    frequency: 'weekly',
    method: 'ABC',
    is_active: true,
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: 'Monthly Chemical Count',
    frequency: 'monthly',
    method: 'random',
    is_active: true,
    created_at: '2025-01-01T00:00:00Z'
  }
];

const mockBatches = [
  {
    id: 1,
    schedule_id: 1,
    name: 'Batch 2025-01',
    status: 'active',
    item_count: 25,
    completed_count: 15,
    start_date: '2025-01-01T00:00:00Z',
    end_date: '2025-01-07T00:00:00Z'
  }
];

const mockItems = [
  {
    id: 1,
    batch_id: 1,
    item_type: 'tool',
    item_id: 1,
    status: 'pending',
    expected_quantity: 1,
    expected_location: 'Workshop A',
    item_details: {
      id: 1,
      number: 'T001',
      description: 'Test Tool',
      location: 'Workshop A'
    }
  },
  {
    id: 2,
    batch_id: 1,
    item_type: 'chemical',
    item_id: 1,
    status: 'counted',
    expected_quantity: 100,
    expected_location: 'Storage B',
    item_details: {
      id: 1,
      part_number: 'C001',
      name: 'Test Chemical',
      location: 'Storage B'
    }
  }
];

// Create test store
const createTestStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      cycleCount: cycleCountReducer,
      auth: authReducer
    },
    preloadedState: {
      cycleCount: {
        schedules: {
          items: mockSchedules,
          loading: false,
          error: null
        },
        batches: {
          items: mockBatches,
          loading: false,
          error: null
        },
        items: {
          byBatchId: {
            1: mockItems
          },
          loadingByBatchId: {
            1: false
          },
          errorByBatchId: {
            1: null
          }
        },
        analytics: {
          data: null,
          loading: false,
          error: null
        }
      },
      auth: {
        user: {
          id: 1,
          name: 'Test User',
          employee_number: 'TEST001',
          is_admin: true
        },
        isAuthenticated: true
      },
      ...initialState
    }
  });
};

// Test wrapper component
const TestWrapper = ({ children, store = createTestStore() }) => (
  <Provider store={store}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </Provider>
);

describe('CycleCountDashboard', () => {
  test('renders dashboard with schedules and batches', () => {
    render(
      <TestWrapper>
        <CycleCountDashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Cycle Count Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Weekly Tool Count')).toBeInTheDocument();
    expect(screen.getByText('Monthly Chemical Count')).toBeInTheDocument();
  });

  test('displays analytics section', () => {
    render(
      <TestWrapper>
        <CycleCountDashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Analytics')).toBeInTheDocument();
  });

  test('shows create schedule button for admin users', () => {
    render(
      <TestWrapper>
        <CycleCountDashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Create Schedule')).toBeInTheDocument();
  });
});

describe('CycleCountScheduleForm', () => {
  test('renders form fields correctly', () => {
    render(
      <TestWrapper>
        <CycleCountScheduleForm />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/schedule name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/frequency/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/method/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(
      <TestWrapper>
        <CycleCountScheduleForm />
      </TestWrapper>
    );

    const submitButton = screen.getByText('Create Schedule');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/schedule name is required/i)).toBeInTheDocument();
    });
  });

  test('submits form with valid data', async () => {
    const mockOnSubmit = jest.fn();
    
    render(
      <TestWrapper>
        <CycleCountScheduleForm onSubmit={mockOnSubmit} />
      </TestWrapper>
    );

    fireEvent.change(screen.getByLabelText(/schedule name/i), {
      target: { value: 'Test Schedule' }
    });
    
    fireEvent.change(screen.getByLabelText(/frequency/i), {
      target: { value: 'weekly' }
    });
    
    fireEvent.change(screen.getByLabelText(/method/i), {
      target: { value: 'ABC' }
    });

    fireEvent.click(screen.getByText('Create Schedule'));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'Test Schedule',
        frequency: 'weekly',
        method: 'ABC',
        description: ''
      });
    });
  });
});

describe('CycleCountBatchForm', () => {
  test('renders form with schedule selection', () => {
    render(
      <TestWrapper>
        <CycleCountBatchForm />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/schedule/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/batch name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/end date/i)).toBeInTheDocument();
  });

  test('populates schedule options', () => {
    render(
      <TestWrapper>
        <CycleCountBatchForm />
      </TestWrapper>
    );

    const scheduleSelect = screen.getByLabelText(/schedule/i);
    expect(scheduleSelect).toBeInTheDocument();
    
    // Check if schedule options are available
    fireEvent.click(scheduleSelect);
    expect(screen.getByText('Weekly Tool Count')).toBeInTheDocument();
    expect(screen.getByText('Monthly Chemical Count')).toBeInTheDocument();
  });
});

describe('CycleCountItemList', () => {
  test('renders item list with correct data', () => {
    render(
      <TestWrapper>
        <CycleCountItemList batchId={1} />
      </TestWrapper>
    );

    expect(screen.getByText('T001')).toBeInTheDocument();
    expect(screen.getByText('Test Tool')).toBeInTheDocument();
    expect(screen.getByText('C001')).toBeInTheDocument();
    expect(screen.getByText('Test Chemical')).toBeInTheDocument();
  });

  test('shows item status correctly', () => {
    render(
      <TestWrapper>
        <CycleCountItemList batchId={1} />
      </TestWrapper>
    );

    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('Counted')).toBeInTheDocument();
  });

  test('filters items by status', () => {
    render(
      <TestWrapper>
        <CycleCountItemList batchId={1} />
      </TestWrapper>
    );

    const statusFilter = screen.getByLabelText(/filter by status/i);
    fireEvent.change(statusFilter, { target: { value: 'pending' } });

    expect(screen.getByText('T001')).toBeInTheDocument();
    expect(screen.queryByText('C001')).not.toBeInTheDocument();
  });
});

describe('MobileCycleCountBatch', () => {
  test('renders mobile interface correctly', () => {
    render(
      <TestWrapper>
        <MobileCycleCountBatch batchId={1} />
      </TestWrapper>
    );

    expect(screen.getByText('Mobile Cycle Count')).toBeInTheDocument();
    expect(screen.getByText('Scan Barcode')).toBeInTheDocument();
  });

  test('shows item cards in mobile format', () => {
    render(
      <TestWrapper>
        <MobileCycleCountBatch batchId={1} />
      </TestWrapper>
    );

    // Check for mobile-specific styling classes
    const itemCards = screen.getAllByTestId('mobile-item-card');
    expect(itemCards).toHaveLength(2);
  });

  test('handles barcode scanning', async () => {
    const mockOnItemCounted = jest.fn();
    
    render(
      <TestWrapper>
        <MobileCycleCountBatch batchId={1} onItemCounted={mockOnItemCounted} />
      </TestWrapper>
    );

    const scanButton = screen.getByText('Scan Barcode');
    fireEvent.click(scanButton);

    // Mock barcode scan result
    const mockScanResult = 'T001';
    
    // Simulate successful scan
    await waitFor(() => {
      expect(screen.getByText('Barcode Scanner')).toBeInTheDocument();
    });
  });
});

describe('Redux Integration', () => {
  test('dispatches actions correctly', async () => {
    const store = createTestStore();
    const mockDispatch = jest.spyOn(store, 'dispatch');

    render(
      <TestWrapper store={store}>
        <CycleCountDashboard />
      </TestWrapper>
    );

    // Verify that initial data loading actions are dispatched
    expect(mockDispatch).toHaveBeenCalled();
  });

  test('handles loading states', () => {
    const loadingStore = createTestStore({
      cycleCount: {
        schedules: {
          items: [],
          loading: true,
          error: null
        }
      }
    });

    render(
      <TestWrapper store={loadingStore}>
        <CycleCountDashboard />
      </TestWrapper>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('handles error states', () => {
    const errorStore = createTestStore({
      cycleCount: {
        schedules: {
          items: [],
          loading: false,
          error: 'Failed to load schedules'
        }
      }
    });

    render(
      <TestWrapper store={errorStore}>
        <CycleCountDashboard />
      </TestWrapper>
    );

    expect(screen.getByText(/failed to load schedules/i)).toBeInTheDocument();
  });
});
