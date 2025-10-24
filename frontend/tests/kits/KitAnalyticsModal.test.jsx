/**
 * KitAnalyticsModal Component Tests
 *
 * Validates modal rendering states, including loading indicators and populated analytics data.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import KitAnalyticsModal from '../../src/components/kits/KitAnalyticsModal';

// Simplify react-bootstrap Fade animations for deterministic tests
vi.mock('react-bootstrap/Fade', () => ({
  __esModule: true,
  default: ({ in: showContent, children }) => (showContent ? children : null)
}));

describe('KitAnalyticsModal', () => {
  const defaultProps = {
    show: true,
    onHide: vi.fn(),
    kitName: 'Q400 AOG Kit',
    days: 30,
    data: null,
    loading: false,
    error: null,
    onChangeDays: vi.fn(),
    onRefresh: vi.fn()
  };

  it('renders loading state while analytics are being fetched', () => {
    render(
      <KitAnalyticsModal
        {...defaultProps}
        loading={true}
      />
    );

    expect(screen.getByText(/kit analytics/i)).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/loading analytics/i)).toBeInTheDocument();
  });

  it('renders analytics summary when data is available', () => {
    const mockData = {
      issuances: {
        total: 12,
        average_per_day: 1.2
      },
      transfers: {
        incoming: 5,
        outgoing: 3,
        net: 2
      },
      inventory: {
        stock_health: 'good',
        total_items: 48,
        low_stock_items: 4
      },
      reorders: {
        pending: 3,
        fulfilled: 1
      }
    };

    render(
      <KitAnalyticsModal
        {...defaultProps}
        data={mockData}
      />
    );

    expect(screen.getByText(/total issuances/i)).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText(/avg 1\.2 \/ day/i)).toBeInTheDocument();
    expect(screen.getByText(/transfers in/i)).toBeInTheDocument();
    expect(screen.getByText(/transfers out/i)).toBeInTheDocument();
    expect(screen.getByText(/stock health/i)).toBeInTheDocument();
    expect(screen.getByText(/pending reorders/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
  });
});