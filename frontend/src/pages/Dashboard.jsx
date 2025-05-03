import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Row, Col, Alert } from 'react-bootstrap';
import { fetchTools } from '../store/toolsSlice';
import { fetchUserCheckouts } from '../store/checkoutsSlice';
import { fetchAuditLogs } from '../store/auditSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ToolStats from '../components/dashboard/ToolStats';
import ActiveCheckouts from '../components/dashboard/ActiveCheckouts';
import QuickActions from '../components/dashboard/QuickActions';
import RecentActivity from '../components/dashboard/RecentActivity';

const Dashboard = () => {
  const dispatch = useDispatch();
  const { tools, loading: toolsLoading, error: toolsError } = useSelector((state) => state.tools);
  const { userCheckouts, loading: checkoutsLoading, error: checkoutsError } = useSelector((state) => state.checkouts);
  const { loading: auditLoading, error: auditError } = useSelector((state) => state.audit);
  const { user } = useSelector((state) => state.auth);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch tools and checkouts data
        await dispatch(fetchTools()).unwrap();
        await dispatch(fetchUserCheckouts()).unwrap();

        // Fetch audit logs only if user is admin or in Materials department
        if (user && (user.is_admin || user.department === 'Materials')) {
          try {
            await dispatch(fetchAuditLogs({ limit: 5 })).unwrap();
          } catch (auditErr) {
            console.error('Error loading audit logs:', auditErr);
            // Don't set global error for audit logs failure
          }
        }
      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setError('Failed to load some dashboard data. Please try refreshing the page.');
      }
    };

    fetchData();
  }, [dispatch, user]);

  // Combine errors from different sources
  useEffect(() => {
    if (toolsError || checkoutsError || auditError) {
      setError('Failed to load some dashboard data. Please try refreshing the page.');
    } else {
      setError(null);
    }
  }, [toolsError, checkoutsError, auditError]);

  const isLoading = toolsLoading || checkoutsLoading || auditLoading;
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  if (isLoading && (!tools.length || !userCheckouts.length)) {
    return <LoadingSpinner />;
  }

  return (
    <div className="w-100">
      <h1 className="mb-4">Dashboard</h1>

      {error && (
        <Alert variant="warning" className="mb-4">
          {error}
        </Alert>
      )}

      <ToolStats tools={tools} />

      <Row className="mb-4 g-4">
        <Col lg={6} md={12}>
          <ActiveCheckouts checkouts={userCheckouts} />
        </Col>

        <Col lg={6} md={12}>
          <QuickActions isAdmin={isAdmin} />
        </Col>
      </Row>

      <Row className="mb-4 g-4">
        <Col>
          <RecentActivity />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
