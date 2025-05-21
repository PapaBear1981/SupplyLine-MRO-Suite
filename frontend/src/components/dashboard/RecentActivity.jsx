import { useState, useEffect } from 'react';
import { Card, ListGroup, Badge, Alert, Spinner } from 'react-bootstrap';
import api from '../../services/api';
import { formatDateTime } from '../../utils/dateUtils';

const RecentActivity = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUserActivity = async () => {
      try {
        setLoading(true);
        const response = await api.get('/user/activity');
        setActivities(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching user activity:', err);
        setError('Failed to load activity data');
      } finally {
        setLoading(false);
      }
    };

    fetchUserActivity();
  }, []);

  // Function to format timestamp using shared utility
  const formatTimestamp = (timestamp) => formatDateTime(timestamp);

  // Function to get badge color based on activity type
  const getActivityBadgeVariant = (activityType) => {
    switch (activityType) {
      case 'login':
      case 'logout':
        return 'info';
      case 'checkout_tool':
        return 'primary';
      case 'return_tool':
        return 'success';
      case 'password_change':
      case 'profile_update':
        return 'warning';
      case 'login_failed':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  // Function to get human-readable activity type
  const getActivityTypeLabel = (activityType) => {
    switch (activityType) {
      case 'login':
        return 'Login';
      case 'logout':
        return 'Logout';
      case 'checkout_tool':
        return 'Tool Checkout';
      case 'return_tool':
        return 'Tool Return';
      case 'password_change':
        return 'Password Changed';
      case 'profile_update':
        return 'Profile Updated';
      case 'login_failed':
        return 'Failed Login Attempt';
      default:
        return activityType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  if (loading) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Recent Activity</h4>
        </Card.Header>
        <Card.Body className="text-center p-4">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">Recent Activity</h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            <Alert.Heading>Error</Alert.Heading>
            <p>{error}</p>
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Recent Activity</h4>
      </Card.Header>
      <Card.Body className="p-0">
        {activities.length === 0 ? (
          <Alert variant="info" className="m-3">
            No recent activity found.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {activities.slice(0, 10).map((activity) => (
              <ListGroup.Item key={activity.id} className="d-flex justify-content-between align-items-start">
                <div className="ms-2 me-auto">
                  <div className="fw-bold">
                    <Badge bg={getActivityBadgeVariant(activity.activity_type)} className="me-2">
                      {getActivityTypeLabel(activity.activity_type)}
                    </Badge>
                  </div>
                  <div className="text-muted small">
                    {activity.description || getActivityTypeLabel(activity.activity_type)}
                  </div>
                </div>
                <Badge bg="light" text="dark" pill>
                  {formatTimestamp(activity.timestamp)}
                </Badge>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Card.Body>
    </Card>
  );
};

export default RecentActivity;
