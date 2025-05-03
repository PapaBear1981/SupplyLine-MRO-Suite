import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Card, ListGroup, Badge } from 'react-bootstrap';
import { fetchAuditLogs } from '../../store/auditSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const RecentActivity = () => {
  const dispatch = useDispatch();
  const { logs, loading } = useSelector((state) => state.audit);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchAuditLogs({ limit: 5 }));
  }, [dispatch]);

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
      default:
        return 'secondary';
    }
  };

  if (loading && !logs.length) {
    return <LoadingSpinner />;
  }

  return (
    <Card className="shadow-sm h-100">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Recent Activity</h4>
      </Card.Header>
      <Card.Body className="p-0">
        {logs.length > 0 ? (
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
