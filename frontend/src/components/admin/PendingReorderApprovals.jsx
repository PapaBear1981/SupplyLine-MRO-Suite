import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Badge, Alert, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaRedo, FaExclamationCircle } from 'react-icons/fa';
import { fetchReorderRequests } from '../../store/kitsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const PendingReorderApprovals = () => {
  const dispatch = useDispatch();
  const { reorderRequests, loading, error } = useSelector((state) => state.kits);

  useEffect(() => {
    // Fetch pending reorder requests
    dispatch(fetchReorderRequests({ status: 'pending' }));
  }, [dispatch]);

  // Filter for pending requests
  const pendingRequests = reorderRequests.filter(req => req.status === 'pending');

  // Sort by priority (urgent > high > medium > low)
  const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
  const sortedRequests = [...pendingRequests].sort((a, b) => {
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

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

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'urgent':
        return <Badge bg="danger">Urgent</Badge>;
      case 'high':
        return <Badge bg="warning">High</Badge>;
      case 'medium':
        return <Badge bg="info">Medium</Badge>;
      case 'low':
        return <Badge bg="secondary">Low</Badge>;
      default:
        return <Badge bg="secondary">{priority}</Badge>;
    }
  };

  if (loading && reorderRequests.length === 0) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaRedo className="me-2" />
          Pending Reorder Approvals
        </Card.Header>
        <Card.Body>
          <LoadingSpinner />
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaRedo className="me-2" />
          Pending Reorder Approvals
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            Failed to load reorder requests: {error.message || 'Unknown error'}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  const urgentCount = pendingRequests.filter(req => req.priority === 'urgent').length;

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">
          <FaRedo className="me-2" />
          Pending Reorder Approvals
        </h5>
        <div>
          {urgentCount > 0 && (
            <Badge bg="danger" className="me-2">
              <FaExclamationCircle className="me-1" />
              {urgentCount} Urgent
            </Badge>
          )}
          <Badge bg={pendingRequests.length > 0 ? "warning" : "success"} pill>
            {pendingRequests.length}
          </Badge>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        {pendingRequests.length === 0 ? (
          <Alert variant="success" className="m-3 mb-0">
            No pending reorder approvals. All requests are processed.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {sortedRequests.slice(0, 10).map((request) => (
              <ListGroup.Item 
                key={request.id} 
                className="d-flex justify-content-between align-items-start"
              >
                <div className="flex-grow-1">
                  <div className="fw-bold mb-1">
                    {request.description || request.part_number}
                  </div>
                  <div className="text-muted small mb-1">
                    Kit: {request.kit_name || `Kit ${request.kit_id}`}
                    {request.part_number && ` | Part: ${request.part_number}`}
                  </div>
                  <div className="text-muted small">
                    Qty: {request.quantity_requested} | 
                    Requested: {formatDate(request.requested_date)}
                    {request.requested_by_name && ` | By: ${request.requested_by_name}`}
                  </div>
                </div>
                <div className="d-flex flex-column align-items-end">
                  {getPriorityBadge(request.priority)}
                  <Button
                    as={Link}
                    to={`/kits/${request.kit_id}`}
                    variant="outline-primary"
                    size="sm"
                    className="mt-2"
                  >
                    Review
                  </Button>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
        {pendingRequests.length > 10 && (
          <Card.Footer className="text-center">
            <Button
              as={Link}
              to="/kits/reorders"
              variant="link"
              size="sm"
            >
              View All Pending Requests ({pendingRequests.length})
            </Button>
          </Card.Footer>
        )}
      </Card.Body>
    </Card>
  );
};

export default PendingReorderApprovals;

