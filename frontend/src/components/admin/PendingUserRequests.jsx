import { useSelector } from 'react-redux';
import { Card, ListGroup, Badge, Alert, Button } from 'react-bootstrap';
import { FaUserPlus, FaBuilding, FaIdBadge } from 'react-icons/fa';
import LoadingSpinner from '../common/LoadingSpinner';

const PendingUserRequests = ({ onNavigateToRequests }) => {
  const { registrationRequests, loading, error } = useSelector((state) => state.admin);

  const pendingRequests = registrationRequests.pending || [];

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading.registrationRequests && pendingRequests.length === 0) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaUserPlus className="me-2" />
          Pending User Requests
        </Card.Header>
        <Card.Body>
          <LoadingSpinner />
        </Card.Body>
      </Card>
    );
  }

  if (error.registrationRequests) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaUserPlus className="me-2" />
          Pending User Requests
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            Failed to load pending requests: {error.registrationRequests.message || 'Unknown error'}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">
          <FaUserPlus className="me-2" />
          Pending User Requests
        </h5>
        <Badge bg={pendingRequests.length > 0 ? "danger" : "success"} pill>
          {pendingRequests.length}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {pendingRequests.length === 0 ? (
          <Alert variant="success" className="m-3 mb-0">
            No pending user requests. All requests have been processed.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {pendingRequests.slice(0, 5).map((request) => (
              <ListGroup.Item
                key={request.id}
                className="d-flex justify-content-between align-items-start"
              >
                <div className="flex-grow-1">
                  <div className="fw-bold mb-1">
                    {request.name}
                  </div>
                  <div className="text-muted small mb-1">
                    <FaIdBadge className="me-1" />
                    <span className="me-3">
                      Employee #{request.employee_number}
                    </span>
                    <FaBuilding className="me-1" />
                    <span>
                      {request.department}
                    </span>
                  </div>
                  <div className="text-muted small">
                    Requested: {formatDate(request.created_at)}
                  </div>
                </div>
                <div className="d-flex flex-column align-items-end">
                  <Badge bg="warning" className="mb-2">
                    Pending
                  </Badge>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
        {pendingRequests.length > 0 && (
          <Card.Footer className="text-center">
            <Button
              variant="primary"
              size="sm"
              onClick={onNavigateToRequests}
            >
              Review All Requests ({pendingRequests.length})
            </Button>
          </Card.Footer>
        )}
      </Card.Body>
    </Card>
  );
};

export default PendingUserRequests;
