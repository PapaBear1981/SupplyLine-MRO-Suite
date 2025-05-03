import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Card, ListGroup, Badge, Alert } from 'react-bootstrap';
import { fetchAuditLogs } from '../../store/auditSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const RecentActivity = () => {
  const dispatch = useDispatch();
  const { logs, loading, error } = useSelector((state) => state.audit);
  const { user } = useSelector((state) => state.auth);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Only fetch audit logs if user is admin or in Materials department
    if (user) {
      const userIsAdmin = user.is_admin || user.department === 'Materials';
      setIsAdmin(userIsAdmin);

      if (userIsAdmin) {
        dispatch(fetchAuditLogs({ limit: 5 }));
      }
    }
  }, [dispatch, user]);

  // Function to format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Function to get badge variant based on action type
  const getBadgeVariant = (actionType) => {
    switch (actionType) {
      case 'checkout_tool':
        return 'warning';
      case 'return_tool':
        return 'success';
      case 'create_tool':
        return 'primary';
      case 'update_tool':
        return 'info';
      case 'delete_tool':
        return 'danger';
      case 'user_login':
        return 'info';
      case 'user_logout':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  if (loading && !logs.length) {
    return (
      <Card className="shadow-sm h-100">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Recent Activity</h4>
        </Card.Header>
        <Card.Body className="d-flex justify-content-center align-items-center">
          <LoadingSpinner />
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm h-100">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Recent Activity</h4>
      </Card.Header>
      <Card.Body className="p-0">
        {error ? (
          <Alert variant="warning" className="m-3">
            Unable to load activity data. Please try again later.
          </Alert>
        ) : !isAdmin ? (
          <Alert variant="info" className="m-3">
            Activity logs are only visible to administrators and Materials department.
          </Alert>
        ) : logs.length > 0 ? (
          <ListGroup variant="flush">
            {logs.map((log) => (
              <ListGroup.Item key={log.id} className="d-flex justify-content-between align-items-start">
                <div className="ms-2 me-auto">
                  <div className="fw-bold">{log.action_details}</div>
                  <small className="text-muted">{formatTimestamp(log.timestamp)}</small>
                </div>
                <Badge bg={getBadgeVariant(log.action_type)} pill>
                  {log.action_type.replace('_', ' ')}
                </Badge>
              </ListGroup.Item>
            ))}
          </ListGroup>
        ) : (
          <p className="text-center py-3">No recent activity found.</p>
        )}
      </Card.Body>
    </Card>
  );
};

export default RecentActivity;
