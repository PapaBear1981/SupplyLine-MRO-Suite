import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Badge, Alert, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaExchangeAlt, FaArrowRight } from 'react-icons/fa';
import { fetchTransfers } from '../../store/kitTransfersSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const PendingKitTransfers = () => {
  const dispatch = useDispatch();
  const { transfers, loading, error } = useSelector((state) => state.kitTransfers);

  useEffect(() => {
    // Fetch pending transfers
    dispatch(fetchTransfers({ status: 'pending' }));
  }, [dispatch]);

  // Filter for pending transfers
  const pendingTransfers = transfers.filter(transfer => transfer.status === 'pending');

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

  const getLocationDisplay = (locationType, locationId, locationName) => {
    if (locationName) return locationName;
    if (locationType === 'kit') return `Kit ${locationId}`;
    if (locationType === 'warehouse') return `Warehouse ${locationId}`;
    return 'Unknown';
  };

  if (loading && transfers.length === 0) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaExchangeAlt className="me-2" />
          Pending Kit Transfers
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
          <FaExchangeAlt className="me-2" />
          Pending Kit Transfers
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            Failed to load pending transfers: {error.message || 'Unknown error'}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">
          <FaExchangeAlt className="me-2" />
          Pending Kit Transfers
        </h5>
        <Badge bg={pendingTransfers.length > 0 ? "warning" : "success"} pill>
          {pendingTransfers.length}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {pendingTransfers.length === 0 ? (
          <Alert variant="success" className="m-3 mb-0">
            No pending transfers. All transfers are up to date.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {pendingTransfers.slice(0, 10).map((transfer) => (
              <ListGroup.Item 
                key={transfer.id} 
                className="d-flex justify-content-between align-items-start"
              >
                <div className="flex-grow-1">
                  <div className="fw-bold mb-1">
                    {transfer.item_description || `${transfer.item_type} Transfer`}
                  </div>
                  <div className="text-muted small mb-1">
                    <span className="me-2">
                      {getLocationDisplay(
                        transfer.from_location_type,
                        transfer.from_location_id,
                        transfer.from_location_name
                      )}
                    </span>
                    <FaArrowRight className="mx-1" />
                    <span className="ms-2">
                      {getLocationDisplay(
                        transfer.to_location_type,
                        transfer.to_location_id,
                        transfer.to_location_name
                      )}
                    </span>
                  </div>
                  <div className="text-muted small">
                    Quantity: {transfer.quantity} | 
                    Requested: {formatDate(transfer.transfer_date || transfer.created_at)}
                    {transfer.transferred_by_name && ` | By: ${transfer.transferred_by_name}`}
                  </div>
                </div>
                <div className="d-flex flex-column align-items-end">
                  <Badge bg="warning" className="mb-2">
                    Pending
                  </Badge>
                  <Button
                    as={Link}
                    to={`/kits/transfers/${transfer.id}`}
                    variant="outline-primary"
                    size="sm"
                  >
                    Review
                  </Button>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
        {pendingTransfers.length > 10 && (
          <Card.Footer className="text-center">
            <Button
              as={Link}
              to="/kits/transfers"
              variant="link"
              size="sm"
            >
              View All Pending Transfers ({pendingTransfers.length})
            </Button>
          </Card.Footer>
        )}
      </Card.Body>
    </Card>
  );
};

export default PendingKitTransfers;

