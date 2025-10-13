/**
 * KitItemsList Component Tests
 *
 * Tests the kit items list display and filtering functionality
 */

import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import {
  renderWithProviders,
  mockAuthState,
  mockKitBox,
  mockKitExpendable,
} from './helpers/testUtils';
import KitItemsList from '../../src/components/kits/KitItemsList';

describe('KitItemsList', () => {
  const mockKitId = 1;

  describe('Rendering', () => {
    it('renders kit items list component', () => {
      const preloadedState = {
        ...mockAuthState,
        kits: {
          aircraftTypes: [],
          kits: [],
          currentKit: null,
          kitBoxes: {
            [mockKitId]: [],
          },
          kitItems: {
            [mockKitId]: {
              items: [],
              expendables: [],
              total_count: 0,
            },
          },
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

      renderWithProviders(<KitItemsList kitId={mockKitId} />, { preloadedState });

      expect(screen.getByText(/kit items/i)).toBeInTheDocument();
    });

    it('displays items from Redux store', () => {
      const mockItem = {
        id: 1,
        box_id: 1,
        part_number: 'TOOL-001',
        description: 'Test Tool',
        status: 'available',
        item_type: 'tool',
      };

      const preloadedState = {
        ...mockAuthState,
        kits: {
          aircraftTypes: [],
          kits: [],
          currentKit: null,
          kitBoxes: {
            [mockKitId]: [mockKitBox],
          },
          kitItems: {
            [mockKitId]: {
              items: [mockItem],
              expendables: [mockKitExpendable],
              total_count: 2,
            },
          },
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

      renderWithProviders(<KitItemsList kitId={mockKitId} />, { preloadedState });

      expect(screen.getByText('TOOL-001')).toBeInTheDocument();
      expect(screen.getByText('EXP-001')).toBeInTheDocument();
    });
  });
});

