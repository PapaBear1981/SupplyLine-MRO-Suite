import { useState, useEffect } from 'react';
import { Card, ListGroup, Badge, Alert, Spinner } from 'react-bootstrap';
import { FaBox, FaExchangeAlt, FaClipboardList } from 'react-icons/fa';
import api from '../../services/api';

const RecentKitActivity = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchKitActivity = async () => {
      try {
        setLoading(true);
        // Fetch recent kit-related activities
        // This could be issuances, transfers, etc.
        const response = await api.get('/kits/recent-activity', {
          params: { limit: 10 }
        });
        setActivities(response.data || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching kit activity:', err);
        // Don't show error if endpoint doesn't exist yet
        if (err.response?.status !== 404) {
          setError('Failed to load kit activity');
        }
        setActivities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchKitActivity();
  }, []);

  const getActivityIcon = (type) => {
    switch (type) {
      case 'issuance':
        return <FaClipboardList className="me-2" />;
      case 'transfer':
        return <FaExchangeAlt className="me-2" />;
      case 'reorder':
        return <FaBox className="me-2" />;
      default:
        return <FaBox className="me-2" />;
    }
  };

  const getActivityBadge = (type) => {
    switch (type) {
      case 'issuance':
        return 'primary';
      case 'transfer':
        return 'info';
      case 'reorder':
        return 'warning';
      default:
        return 'secondary';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">
            <FaBox className="me-2" />
            Recent Kit Activity
          </h4>
        </Card.Header>
        <Card.Body className="text-center py-4">
          <Spinner animation="border" size="sm" />
          <div className="mt-2 text-muted">Loading activity...</div>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">
            <FaBox className="me-2" />
            Recent Kit Activity
          </h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">{error}</Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">
          <FaBox className="me-2" />
          Recent Kit Activity
        </h4>
        <Badge bg="primary" pill>
          {activities.length}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {activities.length === 0 ? (
          <Alert variant="info" className="m-3">
            No recent kit activity found.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {activities.slice(0, 10).map((activity, index) => (
              <ListGroup.Item 
                key={activity.id || index} 
                className="d-flex justify-content-between align-items-start"
              >
                <div className="ms-2 me-auto">
                  <div className="fw-bold">
                    {getActivityIcon(activity.type)}
                    {activity.description || activity.action || 'Kit Activity'}
                  </div>
                  <div className="text-muted small">
                    {activity.kit_name && `Kit: ${activity.kit_name}`}
                    {activity.details && ` - ${activity.details}`}
                  </div>
                  {activity.user_name && (
                    <div className="text-muted small">
                      By: {activity.user_name}
                    </div>
                  )}
                </div>
                <div className="d-flex flex-column align-items-end">
                  <Badge bg={getActivityBadge(activity.type)} className="mb-1">
                    {activity.type || 'activity'}
                  </Badge>
                  <small className="text-muted">
                    {formatDate(activity.timestamp || activity.created_at)}
                  </small>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Card.Body>
    </Card>
  );
};

export default RecentKitActivity;

