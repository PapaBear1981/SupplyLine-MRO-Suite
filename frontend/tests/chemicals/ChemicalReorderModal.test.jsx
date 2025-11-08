/**
 * ChemicalReorderModal Component Tests
 *
 * Tests the reorder modal functionality for chemicals
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  renderWithProviders,
  mockAuthState,
  mockChemical,
  mockChemicalsState,
} from './helpers/testUtils';
import ChemicalReorderModal from '../../src/components/chemicals/ChemicalReorderModal';
import * as chemicalsSlice from '../../src/store/chemicalsSlice';

// Mock the Redux actions
vi.mock('../../src/store/chemicalsSlice', async () => {
  const actual = await vi.importActual('../../src/store/chemicalsSlice');
  return {
    ...actual,
    markChemicalAsOrdered: vi.fn(() => ({
      type: 'chemicals/markChemicalAsOrdered',
      payload: {},
    })),
    fetchChemicals: vi.fn(() => ({
      type: 'chemicals/fetchChemicals',
      payload: [],
    })),
  };
});

describe('ChemicalReorderModal', () => {
  const mockOnHide = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const preloadedState = {
    ...mockAuthState,
    chemicals: mockChemicalsState,
  };

  describe('Rendering', () => {
    it('renders modal when show is true', () => {
      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      expect(screen.getByText('Reorder Chemical')).toBeInTheDocument();
      expect(screen.getByText(/CHEM-001/)).toBeInTheDocument();
      expect(screen.getByText(/LOT-001/)).toBeInTheDocument();
    });

    it('does not render modal when show is false', () => {
      renderWithProviders(
        <ChemicalReorderModal show={false} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      expect(screen.queryByText('Reorder Chemical')).not.toBeInTheDocument();
    });

    it('displays chemical information correctly', () => {
      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      expect(screen.getByText(/Part Number:/)).toBeInTheDocument();
      expect(screen.getByText(/CHEM-001/)).toBeInTheDocument();
      expect(screen.getByText(/Lot Number:/)).toBeInTheDocument();
      expect(screen.getByText(/LOT-001/)).toBeInTheDocument();
      expect(screen.getByText(/Description:/)).toBeInTheDocument();
      expect(screen.getByText(/Test Chemical/)).toBeInTheDocument();
      expect(screen.getByText(/Manufacturer:/)).toBeInTheDocument();
      expect(screen.getByText(/Test Manufacturer/)).toBeInTheDocument();
    });
  });

  describe('Form Interaction', () => {
    it('allows user to enter expected delivery date', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const dateInput = screen.getByLabelText(/Expected Delivery Date/);
      await user.type(dateInput, '2025-12-31');

      expect(dateInput.value).toBe('2025-12-31');
    });

    it('allows user to enter optional notes', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const notesInput = screen.getByLabelText(/Notes \(Optional\)/);
      await user.type(notesInput, 'Urgent order needed');

      expect(notesInput.value).toBe('Urgent order needed');
    });

    it('shows character count for notes field', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const notesInput = screen.getByLabelText(/Notes \(Optional\)/);
      await user.type(notesInput, 'Test note');

      expect(screen.getByText(/9\/500 characters/)).toBeInTheDocument();
    });

    it('disables submit button when delivery date is not provided', () => {
      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const submitButton = screen.getByRole('button', { name: /Mark as Ordered/i });
      expect(submitButton).toBeDisabled();
    });

    it('enables submit button when delivery date is provided', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const dateInput = screen.getByLabelText(/Expected Delivery Date/);
      await user.type(dateInput, '2025-12-31');

      const submitButton = screen.getByRole('button', { name: /Mark as Ordered/i });
      expect(submitButton).not.toBeDisabled();
    });
  });

  describe('Form Submission', () => {
    it('calls markChemicalAsOrdered action on submit', async () => {
      const user = userEvent.setup();
      const mockDispatch = vi.fn(() => Promise.resolve({ unwrap: () => Promise.resolve({}) }));

      // Mock the dispatch to return a promise
      chemicalsSlice.markChemicalAsOrdered.mockReturnValue({
        type: 'chemicals/markChemicalAsOrdered',
        payload: {},
      });

      const { store } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      // Override dispatch
      store.dispatch = mockDispatch.mockReturnValue({
        unwrap: () => Promise.resolve({}),
      });

      const dateInput = screen.getByLabelText(/Expected Delivery Date/);
      await user.type(dateInput, '2025-12-31');

      const submitButton = screen.getByRole('button', { name: /Mark as Ordered/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalled();
      });
    });

    it('closes modal after successful submission', async () => {
      const user = userEvent.setup();
      const mockDispatch = vi.fn(() => ({
        unwrap: () => Promise.resolve({}),
      }));

      const { store } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      store.dispatch = mockDispatch;

      const dateInput = screen.getByLabelText(/Expected Delivery Date/);
      await user.type(dateInput, '2025-12-31');

      const submitButton = screen.getByRole('button', { name: /Mark as Ordered/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnHide).toHaveBeenCalled();
      });
    });

    it('displays error message on submission failure', async () => {
      const user = userEvent.setup();
      const mockDispatch = vi.fn(() => ({
        unwrap: () => Promise.reject(new Error('Failed to create order')),
      }));

      const { store } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      store.dispatch = mockDispatch;

      const dateInput = screen.getByLabelText(/Expected Delivery Date/);
      await user.type(dateInput, '2025-12-31');

      const submitButton = screen.getByRole('button', { name: /Mark as Ordered/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to create order/)).toBeInTheDocument();
      });
    });
  });

  describe('Modal Actions', () => {
    it('calls onHide when Cancel button is clicked', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      await user.click(cancelButton);

      expect(mockOnHide).toHaveBeenCalled();
    });

    it('calls onHide when close button is clicked', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const closeButton = screen.getByLabelText(/Close/i);
      await user.click(closeButton);

      expect(mockOnHide).toHaveBeenCalled();
    });

    it('resets form fields when modal is closed', async () => {
      const user = userEvent.setup();

      const { rerender } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const dateInput = screen.getByLabelText(/Expected Delivery Date/);
      await user.type(dateInput, '2025-12-31');

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      await user.click(cancelButton);

      // Reopen the modal
      rerender(
        <ChemicalReorderModal show={false} onHide={mockOnHide} chemical={mockChemical} />
      );
      rerender(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />
      );

      const newDateInput = screen.getByLabelText(/Expected Delivery Date/);
      expect(newDateInput.value).toBe('');
    });
  });
});
