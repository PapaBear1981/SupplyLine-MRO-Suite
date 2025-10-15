/**
 * KitWizard Component Tests
 *
 * Tests the 4-step wizard for creating new kits
 */

import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders, mockAuthState, mockAircraftType } from './helpers/testUtils';
import KitWizard from '../../src/components/kits/KitWizard';

describe('KitWizard', () => {
  describe('Rendering', () => {
    it('renders the wizard component', () => {
      const preloadedState = {
        ...mockAuthState,
        kits: {
          aircraftTypes: [],
          kits: [],
          currentKit: null,
          kitBoxes: {},
          kitItems: {},
          kitExpendables: {},
          kitIssuances: {},
          kitAnalytics: {},
          kitAlerts: {},
          inventoryReport: [],
          issuanceReport: [],
          transferReport: [],
          reorderReport: [],
          utilizationReport: null,
          reorderRequests: [],
          wizardData: null,
          loading: false,
          error: null,
        },
      };

      renderWithProviders(<KitWizard />, { preloadedState });

      // Check that the wizard renders
      expect(screen.getByText(/select aircraft type/i)).toBeInTheDocument();
      expect(screen.getByText(/create new kit/i)).toBeInTheDocument();
    });

    it('displays aircraft types when available', () => {
      const preloadedState = {
        ...mockAuthState,
        kits: {
          aircraftTypes: [
            { id: 1, name: 'Q400', description: 'Bombardier Q400', is_active: true },
            { id: 2, name: 'B737', description: 'Boeing 737', is_active: true },
          ],
          kits: [],
          currentKit: null,
          kitBoxes: {},
          kitItems: {},
          kitExpendables: {},
          kitIssuances: {},
          kitAnalytics: {},
          kitAlerts: {},
          inventoryReport: [],
          issuanceReport: [],
          transferReport: [],
          reorderReport: [],
          utilizationReport: null,
          reorderRequests: [],
          wizardData: null,
          loading: false,
          error: null,
        },
      };

      renderWithProviders(<KitWizard />, { preloadedState });

      expect(screen.getByText('Q400')).toBeInTheDocument();
      expect(screen.getByText('B737')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('has a next button that is initially disabled', () => {
      const preloadedState = {
        ...mockAuthState,
        kits: {
          aircraftTypes: [mockAircraftType],
          kits: [],
          currentKit: null,
          kitBoxes: {},
          kitItems: {},
          kitExpendables: {},
          kitIssuances: {},
          kitAnalytics: {},
          kitAlerts: {},
          inventoryReport: [],
          issuanceReport: [],
          transferReport: [],
          reorderReport: [],
          utilizationReport: null,
          reorderRequests: [],
          wizardData: null,
          loading: false,
          error: null,
        },
      };

      renderWithProviders(<KitWizard />, { preloadedState });

      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeDisabled();
    });

    it('has a cancel button', () => {
      const preloadedState = {
        ...mockAuthState,
        kits: {
          aircraftTypes: [mockAircraftType],
          kits: [],
          currentKit: null,
          kitBoxes: {},
          kitItems: {},
          kitExpendables: {},
          kitIssuances: {},
          kitAnalytics: {},
          kitAlerts: {},
          inventoryReport: [],
          issuanceReport: [],
          transferReport: [],
          reorderReport: [],
          utilizationReport: null,
          reorderRequests: [],
          wizardData: null,
          loading: false,
          error: null,
        },
      };

      renderWithProviders(<KitWizard />, { preloadedState });

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      expect(cancelButton).toBeInTheDocument();
    });
  });
});

