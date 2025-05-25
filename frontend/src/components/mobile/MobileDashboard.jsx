import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Card, Button, Badge, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import MobileQuickActions from './MobileQuickActions';
import MobilePullToRefresh from './MobilePullToRefresh';

const MobileDashboard = () => {
  const { user } = useSelector((state) => state.auth);
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  // Mock data - in real implementation, this would come from Redux store
  const dashboardData = {
    myCheckouts: 3,
    overdueTools: 1,
    expiringChemicals: 2,
    calibrationsDue: 1,
    recentActivity: [
      { id: 1, action: 'Checked out Tool #T001', time: '2 hours ago' },
      { id: 2, action: 'Returned Tool #T005', time: '1 day ago' },
      { id: 3, action: 'Chemical issued: Acetone', time: '2 days ago' }
    ]
  };

  return (
    <MobilePullToRefresh onRefresh={handleRefresh} refreshing={refreshing}>
      <div className="mobile-dashboard">
        {/* Welcome Section */}
        <div className="mobile-welcome-section">
          <h4>Welcome back, {user?.name?.split(' ')[0] || 'User'}!</h4>
          <p className="text-muted">Here's what's happening today</p>
        </div>

        {/* Quick Actions */}
        <MobileQuickActions />

        {/* Status Cards */}
        <div className="mobile-status-cards">
          <Card className="mobile-card mb-3">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="card-title mb-1">My Checkouts</h6>
                  <h3 className="text-primary mb-0">{dashboardData.myCheckouts}</h3>
                </div>
                <div className="mobile-card-icon">
                  <i className="bi bi-clipboard-check text-primary"></i>
                </div>
              </div>
              <Link to="/checkouts" className="btn btn-sm btn-outline-primary mt-2">
                View All
              </Link>
            </Card.Body>
          </Card>

          {dashboardData.overdueTools > 0 && (
            <Card className="mobile-card mb-3 border-warning">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 className="card-title mb-1 text-warning">Overdue Tools</h6>
                    <h3 className="text-warning mb-0">{dashboardData.overdueTools}</h3>
                  </div>
                  <div className="mobile-card-icon">
                    <i className="bi bi-exclamation-triangle text-warning"></i>
                  </div>
                </div>
                <Button variant="outline-warning" size="sm" className="mt-2">
                  Return Now
                </Button>
              </Card.Body>
            </Card>
          )}

          {user && (user.is_admin || user.department === 'Materials') && (
            <>
              <Card className="mobile-card mb-3">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 className="card-title mb-1">Expiring Chemicals</h6>
                      <h3 className="text-info mb-0">{dashboardData.expiringChemicals}</h3>
                    </div>
                    <div className="mobile-card-icon">
                      <i className="bi bi-flask text-info"></i>
                    </div>
                  </div>
                  <Link to="/chemicals" className="btn btn-sm btn-outline-info mt-2">
                    Review
                  </Link>
                </Card.Body>
              </Card>

              <Card className="mobile-card mb-3">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 className="card-title mb-1">Calibrations Due</h6>
                      <h3 className="text-success mb-0">{dashboardData.calibrationsDue}</h3>
                    </div>
                    <div className="mobile-card-icon">
                      <i className="bi bi-speedometer2 text-success"></i>
                    </div>
                  </div>
                  <Link to="/calibrations" className="btn btn-sm btn-outline-success mt-2">
                    Schedule
                  </Link>
                </Card.Body>
              </Card>
            </>
          )}
        </div>

        {/* Recent Activity */}
        <Card className="mobile-card mb-3">
          <Card.Header>
            <h6 className="mb-0">Recent Activity</h6>
          </Card.Header>
          <Card.Body className="p-0">
            {dashboardData.recentActivity.map((activity, index) => (
              <div 
                key={activity.id} 
                className={`mobile-activity-item ${index !== dashboardData.recentActivity.length - 1 ? 'border-bottom' : ''}`}
              >
                <div className="mobile-activity-content">
                  <p className="mb-1">{activity.action}</p>
                  <small className="text-muted">{activity.time}</small>
                </div>
              </div>
            ))}
          </Card.Body>
        </Card>

        {/* Announcements */}
        <Card className="mobile-card mb-4">
          <Card.Header>
            <h6 className="mb-0">Announcements</h6>
          </Card.Header>
          <Card.Body>
            <Alert variant="info" className="mb-0">
              <i className="bi bi-info-circle me-2"></i>
              System maintenance scheduled for this weekend.
            </Alert>
          </Card.Body>
        </Card>
      </div>
    </MobilePullToRefresh>
  );
};

export default MobileDashboard;
