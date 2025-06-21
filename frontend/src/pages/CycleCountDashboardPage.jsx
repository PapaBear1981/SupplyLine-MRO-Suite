import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Row, Col, Button, Alert, Spinner, Tabs, Tab } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchCycleCountStats } from '../store/cycleCountSlice';
import CycleCountScheduleList from '../components/cycleCount/CycleCountScheduleList';
import CycleCountBatchList from '../components/cycleCount/CycleCountBatchList';
import CycleCountDiscrepancyList from '../components/cycleCount/CycleCountDiscrepancyList';
import CycleCountStatsOverview from '../components/cycleCount/CycleCountStatsOverview';
import CycleCountAdvancedAnalytics from '../components/cycleCount/CycleCountAdvancedAnalytics';
import { useHelp } from '../context/HelpContext';

const CycleCountDashboardPage = () => {
  const dispatch = useDispatch();
  const { showHelp } = useHelp();
  const { stats, schedules, batches, discrepancies } = useSelector((state) => state.cycleCount);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Dispatch with error handling
    dispatch(fetchCycleCountStats()).catch((error) => {
      console.error('Failed to fetch cycle count stats:', error);
    });
  }, [dispatch]);

  if (stats.loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading cycle count data...</span>
        </Spinner>
      </div>
    );
  }

  // If there's a critical error that prevents the page from loading
  if (stats.error && !stats.data) {
    return (
      <div className="container-fluid">
        <h1>Cycle Count Management</h1>
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Unable to Load Cycle Count System</Alert.Heading>
          <p>
            The cycle count system is currently unavailable. This may be due to missing database tables
            or a backend configuration issue.
          </p>
          <p className="mb-0">
            <strong>Error:</strong> {stats.error.error || 'Unknown error occurred'}
          </p>
          <hr />
          <p className="mb-0">
            Please contact your system administrator to resolve this issue. The cycle count database
            tables may need to be created or updated.
          </p>
        </Alert>
      </div>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">Cycle Count Dashboard</h1>
        <div>
          <Button as={Link} to="/cycle-counts/schedules/new" variant="success" className="me-2">
            <i className="bi bi-calendar-plus me-2"></i>
            New Schedule
          </Button>
          <Button as={Link} to="/cycle-counts/batches/new" variant="primary">
            <i className="bi bi-clipboard-plus me-2"></i>
            New Count Batch
          </Button>
        </div>
      </div>

      {showHelp && (
        <Alert variant="info" className="mb-4">
          <Alert.Heading>Cycle Count Management</Alert.Heading>
          <p>
            This dashboard allows you to manage inventory cycle counts. You can create count schedules,
            generate count batches, assign counters, and review discrepancies.
          </p>
          <hr />
          <p className="mb-0">
            <strong>Schedules</strong> define recurring count patterns. <strong>Batches</strong> are individual counting sessions.
            <strong>Discrepancies</strong> show items where the counted quantity or location differs from expected values.
          </p>
        </Alert>
      )}

      {stats.error && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Error Loading Cycle Count Data</Alert.Heading>
          <p>{stats.error.error || 'An error occurred while loading cycle count statistics'}</p>
        </Alert>
      )}

      {stats.data && <CycleCountStatsOverview stats={stats.data} />}

      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-0"
          >
            <Tab eventKey="overview" title="Overview">
              <div className="p-3">
                <p className="text-muted">
                  The cycle count system helps maintain accurate inventory records by systematically counting
                  portions of inventory on a regular basis. Select a tab to manage schedules, batches, or review discrepancies.
                </p>
              </div>
            </Tab>
            <Tab eventKey="schedules" title="Schedules">
              <CycleCountScheduleList />
            </Tab>
            <Tab eventKey="batches" title="Count Batches">
              <CycleCountBatchList />
            </Tab>
            <Tab eventKey="discrepancies" title="Discrepancies">
              <CycleCountDiscrepancyList />
            </Tab>
            <Tab eventKey="analytics" title="Advanced Analytics">
              <CycleCountAdvancedAnalytics />
            </Tab>
          </Tabs>
        </Card.Header>
      </Card>

      <Row>
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Recent Count Batches</h5>
            </Card.Header>
            <Card.Body>
              {stats.data?.recent_batches?.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Progress</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.data.recent_batches.map((batch) => (
                        <tr key={batch.id}>
                          <td>{batch.name}</td>
                          <td>
                            <span className={`badge bg-${getBatchStatusColor(batch.status)}`}>
                              {batch.status}
                            </span>
                          </td>
                          <td>
                            {batch.item_count && batch.item_count > 0 ? (
                              `${batch.completed_count || 0}/${batch.item_count} (${Math.round(((batch.completed_count || 0) / batch.item_count) * 100)}%)`
                            ) : (
                              'No items'
                            )}
                          </td>
                          <td>
                            <Button
                              as={Link}
                              to={`/cycle-counts/batches/${batch.id}`}
                              variant="outline-primary"
                              size="sm"
                            >
                              View
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-center text-muted">No recent count batches</p>
              )}
            </Card.Body>
            <Card.Footer className="bg-white">
              <Button
                as={Link}
                to="/cycle-counts/batches"
                variant="outline-secondary"
                size="sm"
                className="w-100"
              >
                View All Batches
              </Button>
            </Card.Footer>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-3">
                <Button as={Link} to="/cycle-counts/batches/new" variant="outline-primary">
                  <i className="bi bi-clipboard-plus me-2"></i>
                  Start New Count Batch
                </Button>
                <Button as={Link} to="/cycle-counts/schedules/new" variant="outline-success">
                  <i className="bi bi-calendar-plus me-2"></i>
                  Create Count Schedule
                </Button>
                <Button as={Link} to="/cycle-counts/discrepancies" variant="outline-warning">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  Review Discrepancies
                  {stats.data?.results?.with_discrepancies > 0 && (
                    <span className="badge bg-warning text-dark ms-2">
                      {stats.data.results.with_discrepancies}
                    </span>
                  )}
                </Button>
                <Button as={Link} to="/reports" variant="outline-info">
                  <i className="bi bi-graph-up me-2"></i>
                  View Count Reports
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// Helper function to get color for batch status
const getBatchStatusColor = (status) => {
  switch (status) {
    case 'pending':
      return 'secondary';
    case 'in_progress':
      return 'primary';
    case 'completed':
      return 'success';
    case 'cancelled':
      return 'danger';
    default:
      return 'secondary';
  }
};

export default CycleCountDashboardPage;
