import { useEffect, useState, useCallback } from 'react';
import { Card, Row, Col, Spinner } from 'react-bootstrap';
import { toast } from 'react-toastify';
import api from '../../services/api';

const QuickStatsWidget = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      const response = await api.get('/api/dashboard/quick-stats');
      setStats(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      setError('Failed to load statistics');
      // Use a ref or state to track if it's the initial load
      setStats((prevStats) => {
        if (!prevStats) {
          // Only show toast on initial load failure
          toast.error('Failed to load dashboard statistics');
        }
        return prevStats;
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    // Refresh stats every 2 minutes
    const interval = setInterval(fetchStats, 120000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (loading) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Quick Stats</h4>
        </Card.Header>
        <Card.Body className="text-center py-5">
          <Spinner animation="border" variant="primary" role="status">
            <span className="visually-hidden">Loading statistics...</span>
          </Spinner>
          <p className="mt-2 text-muted" aria-live="polite">Loading statistics...</p>
        </Card.Body>
      </Card>
    );
  }

  if (error && !stats) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Quick Stats</h4>
        </Card.Header>
        <Card.Body className="text-center py-4">
          <i className="bi bi-exclamation-triangle text-warning fs-1"></i>
          <p className="mt-2 text-muted">{error}</p>
        </Card.Body>
      </Card>
    );
  }

  const StatItem = ({ icon, value, label, variant = 'primary', subtext = null }) => (
    <Col xs={6} md={6} lg={6} className="mb-3">
      <div className={`text-center p-3 rounded bg-${variant} bg-opacity-10 h-100`} role="group" aria-label={label}>
        <i className={`bi bi-${icon} fs-2 text-${variant} mb-2`} aria-hidden="true"></i>
        <h3 className="mb-0 fw-bold">{value}</h3>
        <p className="mb-0 text-muted small">{label}</p>
        {subtext && <p className="mb-0 text-muted" style={{ fontSize: '0.75rem' }}>{subtext}</p>}
      </div>
    </Col>
  );

  return (
    <Card className="shadow-sm mb-4 fade-in">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0" id="quick-stats-heading">Quick Stats</h4>
        <button
          className="btn btn-link btn-sm text-muted p-0"
          onClick={fetchStats}
          title="Refresh statistics"
          aria-label="Refresh statistics"
          type="button"
        >
          <i className="bi bi-arrow-clockwise" aria-hidden="true"></i>
        </button>
      </Card.Header>
      <Card.Body>
        <Row>
          <StatItem
            icon="people-fill"
            value={stats?.activeUsersNow || 0}
            label="Active Users"
            variant="success"
            subtext="Currently online"
          />
          <StatItem
            icon="person-check-fill"
            value={stats?.usersLoggedInToday || 0}
            label="Logins Today"
            variant="info"
          />
          <StatItem
            icon="arrow-left-right"
            value={stats?.transactionsToday?.total || 0}
            label="Transactions Today"
            variant="primary"
            subtext={`${stats?.transactionsToday?.checkouts || 0} checkouts, ${stats?.transactionsToday?.returns || 0} returns`}
          />
          <StatItem
            icon="tools"
            value={`${stats?.toolAvailability?.availabilityRate || 0}%`}
            label="Tool Availability"
            variant="warning"
            subtext={`${stats?.toolAvailability?.available || 0} of ${stats?.toolAvailability?.total || 0} available`}
          />
        </Row>

        {stats?.pendingItems && Object.keys(stats.pendingItems).length > 0 && (
          <>
            <hr className="my-3" />
            <Row>
              <Col xs={12}>
                <div className="d-flex justify-content-between align-items-center">
                  <span className="text-uppercase text-muted small">Pending Items</span>
                  <div className="d-flex gap-3">
                    {stats.pendingItems.orders > 0 && (
                      <span className="badge bg-danger">
                        {stats.pendingItems.orders} Orders
                      </span>
                    )}
                    {stats.pendingItems.requests > 0 && (
                      <span className="badge bg-warning text-dark">
                        {stats.pendingItems.requests} Requests
                      </span>
                    )}
                  </div>
                </div>
              </Col>
            </Row>
          </>
        )}

        <div className="text-center mt-3">
          <small className="text-muted" role="status" aria-live="polite">
            Last updated: {stats?.timestamp ? new Date(stats.timestamp).toLocaleTimeString() : 'N/A'}
          </small>
        </div>
      </Card.Body>
    </Card>
  );
};

export default QuickStatsWidget;
