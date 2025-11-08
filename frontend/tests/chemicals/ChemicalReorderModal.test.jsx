/**
 * ChemicalReorderModal Component Tests
 *
 * Tests the reorder request modal functionality for chemicals
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


// Mock the Redux actions
vi.mock('../../src/store/chemicalsSlice', async () => {
  const actual = await vi.importActual('../../src/store/chemicalsSlice');
  return {
    ...actual,
    requestChemicalReorder: vi.fn(() => ({
      type: 'chemicals/requestChemicalReorder',
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

      expect(screen.getByText('Request Chemical Reorder')).toBeInTheDocument();
      expect(screen.getByText(/CHEM-001/)).toBeInTheDocument();
      expect(screen.getByText(/LOT-001/)).toBeInTheDocument();
    });

    it('does not render modal when show is false', () => {
      renderWithProviders(
        <ChemicalReorderModal show={false} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      expect(screen.queryByText('Request Chemical Reorder')).not.toBeInTheDocument();
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
      expect(screen.getByText(/Current Quantity:/)).toBeInTheDocument();
    });

    it('displays informational alert about reorder requests', () => {
      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      expect(screen.getByText(/This will create a reorder request/)).toBeInTheDocument();
      expect(screen.getByText(/Chemicals Needing Reorder/)).toBeInTheDocument();
    });
  });

  describe('Form Interaction', () => {
    it('allows user to enter notes', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const notesInput = screen.getByLabelText(/Request Notes \(Optional\)/);
      await user.type(notesInput, 'Urgent order needed');

      expect(notesInput.value).toBe('Urgent order needed');
    });

    it('shows character count for notes field', async () => {
      const user = userEvent.setup();

      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const notesInput = screen.getByLabelText(/Request Notes \(Optional\)/);
      await user.type(notesInput, 'Test note');

      expect(screen.getByText(/9\/500 characters/)).toBeInTheDocument();
    });

    it('submit button is always enabled (notes are optional)', () => {
      renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      const submitButton = screen.getByRole('button', { name: /Submit Reorder Request/i });
      expect(submitButton).not.toBeDisabled();
    });
  });

  describe('Form Submission', () => {
    it('calls requestChemicalReorder action on submit', async () => {
      const user = userEvent.setup();
      const mockUnwrap = vi.fn(() => Promise.resolve({ message: 'Success' }));
      const mockDispatch = vi.fn(() => ({ unwrap: mockUnwrap }));

      const { store } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      // Override dispatch
      store.dispatch = mockDispatch;

      const submitButton = screen.getByRole('button', { name: /Submit Reorder Request/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalled();
        expect(mockUnwrap).toHaveBeenCalled();
      });
    });

    it('submits with notes when provided', async () => {
      const user = userEvent.setup();
      const mockDispatch = vi.fn(() => ({
        unwrap: () => Promise.resolve({}),
      }));

      const { store } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      store.dispatch = mockDispatch;

      const notesInput = screen.getByLabelText(/Request Notes \(Optional\)/);
      await user.type(notesInput, 'Need 5 units ASAP');

      const submitButton = screen.getByRole('button', { name: /Submit Reorder Request/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalled();
      });
    });

    it('displays success message after submission', async () => {
      const user = userEvent.setup();
      const mockUnwrap = vi.fn(() => Promise.resolve({ message: 'Success' }));
      const mockDispatch = vi.fn(() => ({ unwrap: mockUnwrap }));

      const { store } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      store.dispatch = mockDispatch;

      const submitButton = screen.getByRole('button', { name: /Submit Reorder Request/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Reorder request submitted successfully!/)).toBeInTheDocument();
      }, { timeout: 3000 });
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

      const submitButton = screen.getByRole('button', { name: /Submit Reorder Request/i });
      await user.click(submitButton);

      // Wait for the timeout to close the modal (1500ms + buffer)
      await waitFor(() => {
        expect(mockOnHide).toHaveBeenCalled();
      }, { timeout: 2000 });
    });

    it('displays error message on submission failure', async () => {
      const user = userEvent.setup();
      const mockUnwrap = vi.fn(() => Promise.reject(new Error('Failed to request reorder')));
      const mockDispatch = vi.fn(() => ({ unwrap: mockUnwrap }));

      const { store } = renderWithProviders(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />,
        { preloadedState }
      );

      store.dispatch = mockDispatch;

      const submitButton = screen.getByRole('button', { name: /Submit Reorder Request/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to request reorder/)).toBeInTheDocument();
      }, { timeout: 3000 });
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

      const notesInput = screen.getByLabelText(/Request Notes \(Optional\)/);
      await user.type(notesInput, 'Test notes');

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      await user.click(cancelButton);

      // Reopen the modal
      rerender(
        <ChemicalReorderModal show={false} onHide={mockOnHide} chemical={mockChemical} />
      );
      rerender(
        <ChemicalReorderModal show={true} onHide={mockOnHide} chemical={mockChemical} />
      );

      const newNotesInput = screen.getByLabelText(/Request Notes \(Optional\)/);
      expect(newNotesInput.value).toBe('');
    });
  });
});
