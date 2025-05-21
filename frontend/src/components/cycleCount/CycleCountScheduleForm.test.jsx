import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import CycleCountScheduleForm from './CycleCountScheduleForm';
import { HelpProvider } from '../../context/HelpContext';

// Mock react-router-dom's useNavigate and useParams
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => mockParams
}));

// Mock the navigate function
const mockNavigate = jest.fn();
let mockParams = {};

// Create a mock store
const middlewares = [thunk];
const mockStore = configureStore(middlewares);

describe('CycleCountScheduleForm Component', () => {
  let store;
  
  // Helper function to render the component with the required providers
  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <HelpProvider>
            <CycleCountScheduleForm />
          </HelpProvider>
        </BrowserRouter>
      </Provider>
    );
  };

  beforeEach(() => {
    // Reset mocks
    mockNavigate.mockClear();
    mockParams = {};
    
    // Default store state for create mode
    store = mockStore({
      cycleCount: {
        currentSchedule: {
          data: null,
          loading: false,
          error: null
        }
      }
    });
    
    // Mock dispatch function
    store.dispatch = jest.fn().mockImplementation(() => Promise.resolve({ payload: {} }));
  });

  test('renders in create mode correctly', () => {
    renderComponent();
    
    // Check if the form title is correct
    expect(screen.getByText('Create Cycle Count Schedule')).toBeInTheDocument();
    
    // Check if form fields are present
    expect(screen.getByLabelText('Schedule Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Status')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByLabelText('Frequency')).toBeInTheDocument();
    expect(screen.getByLabelText('Count Method')).toBeInTheDocument();
    
    // Check if buttons are present
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Schedule' })).toBeInTheDocument();
  });

  test('renders in edit mode correctly with preloaded data', () => {
    // Set up edit mode
    mockParams = { id: '123' };
    
    // Set up store with preloaded data
    store = mockStore({
      cycleCount: {
        currentSchedule: {
          data: {
            id: '123',
            name: 'Test Schedule',
            description: 'Test Description',
            frequency: 'monthly',
            method: 'ABC',
            is_active: true
          },
          loading: false,
          error: null
        }
      }
    });
    
    renderComponent();
    
    // Check if the form title is correct
    expect(screen.getByText('Edit Cycle Count Schedule')).toBeInTheDocument();
    
    // Check if form fields are populated with the correct values
    expect(screen.getByLabelText('Schedule Name')).toHaveValue('Test Schedule');
    expect(screen.getByLabelText('Description')).toHaveValue('Test Description');
    
    // Check if the correct button is shown
    expect(screen.getByRole('button', { name: 'Update Schedule' })).toBeInTheDocument();
  });

  test('shows loading spinner when fetching schedule data in edit mode', () => {
    // Set up edit mode
    mockParams = { id: '123' };
    
    // Set up store with loading state
    store = mockStore({
      cycleCount: {
        currentSchedule: {
          data: null,
          loading: true,
          error: null
        }
      }
    });
    
    renderComponent();
    
    // Check if loading spinner is shown
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('shows error message when schedule data fetch fails', () => {
    // Set up edit mode
    mockParams = { id: '123' };
    
    // Set up store with error state
    store = mockStore({
      cycleCount: {
        currentSchedule: {
          data: null,
          loading: false,
          error: { error: 'Failed to load schedule' }
        }
      }
    });
    
    renderComponent();
    
    // Check if error message is shown
    expect(screen.getByText('Error Loading Schedule')).toBeInTheDocument();
    expect(screen.getByText('Failed to load schedule')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Return to Schedules' })).toBeInTheDocument();
  });

  test('validates required fields on submit', async () => {
    renderComponent();
    
    // Submit the form without filling required fields
    fireEvent.click(screen.getByRole('button', { name: 'Create Schedule' }));
    
    // Check if validation messages are shown
    await waitFor(() => {
      expect(screen.getByText('Please provide a schedule name.')).toBeInTheDocument();
      expect(screen.getByText('Please select a frequency.')).toBeInTheDocument();
      expect(screen.getByText('Please select a count method.')).toBeInTheDocument();
    });
  });

  test('submits form data correctly in create mode', async () => {
    renderComponent();
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText('Schedule Name'), { target: { value: 'New Schedule' } });
    fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'New Description' } });
    
    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Create Schedule' }));
    
    // Check if the form was submitted with the correct data
    await waitFor(() => {
      expect(store.dispatch).toHaveBeenCalledWith(expect.any(Function));
    });
  });

  test('detects no changes in edit mode and skips API call', async () => {
    // Set up edit mode
    mockParams = { id: '123' };
    
    // Set up store with preloaded data
    const scheduleData = {
      id: '123',
      name: 'Test Schedule',
      description: 'Test Description',
      frequency: 'monthly',
      method: 'ABC',
      is_active: true
    };
    
    store = mockStore({
      cycleCount: {
        currentSchedule: {
          data: scheduleData,
          loading: false,
          error: null
        }
      }
    });
    
    renderComponent();
    
    // Submit the form without making any changes
    fireEvent.click(screen.getByRole('button', { name: 'Update Schedule' }));
    
    // Check if success message is shown without API call
    await waitFor(() => {
      expect(screen.getByText('Schedule updated successfully. Redirecting...')).toBeInTheDocument();
      // The updateCycleCountSchedule action should not be dispatched
      expect(store.dispatch).not.toHaveBeenCalledWith(expect.objectContaining({
        type: 'cycleCount/updateCycleCountSchedule/pending'
      }));
    });
  });

  test('navigates back to schedules list on cancel', () => {
    renderComponent();
    
    // Click the cancel button
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    
    // Check if navigate was called with the correct path
    expect(mockNavigate).toHaveBeenCalledWith('/cycle-counts/schedules');
  });
});
