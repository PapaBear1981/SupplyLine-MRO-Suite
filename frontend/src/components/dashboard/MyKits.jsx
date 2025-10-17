import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Badge, Alert, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaBox, FaPlane, FaExclamationTriangle } from 'react-icons/fa';
import { fetchKits } from '../../store/kitsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const MyKits = () => {
  const dispatch = useDispatch();
  const { kits, loading, error } = useSelector((state) => state.kits);

  useEffect(() => {
    dispatch(fetchKits());
  }, [dispatch]);

  // Filter kits that are active and might be relevant to the user
  // For mechanics, show all active kits
  const activeKits = kits.filter(kit => kit.status === 'active');

  if (loading && kits.length === 0) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">
            <FaBox className="me-2" />
            My Kits
          </h4>
        </Card.Header>
        <Card.Body>
          <LoadingSpinner />
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
            My Kits
          </h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            Failed to load kits: {error.message || 'Unknown error'}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">
          <FaBox className="me-2" />
          My Kits
        </h4>
        <Badge bg={activeKits.length > 0 ? "success" : "secondary"} pill>
          {activeKits.length}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {activeKits.length === 0 ? (
          <Alert variant="info" className="m-3">
            No active kits available. Contact Materials department if you need access to a kit.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {activeKits.slice(0, 5).map((kit) => (
              <ListGroup.Item 
                key={kit.id} 
                className="d-flex justify-content-between align-items-center"
              >
                <div className="flex-grow-1">
                  <div className="fw-bold">{kit.name}</div>
                  <div className="text-muted small">
                    <FaPlane className="me-1" />
                    {kit.aircraft_type_name || 'Unknown Aircraft'}
                  </div>
                  <div className="text-muted small mt-1">
                    Items: {kit.item_count || 0} | Boxes: {kit.box_count || 0}
                  </div>
                </div>
                <div className="d-flex align-items-center">
                  {kit.alert_count > 0 && (
                    <Badge bg="warning" className="me-2">
                      <FaExclamationTriangle className="me-1" />
                      {kit.alert_count}
                    </Badge>
                  )}
                  <Button
                    as={Link}
                    to={`/kits/${kit.id}`}
                    variant="outline-primary"
                    size="sm"
                  >
                    View
                  </Button>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
        {activeKits.length > 5 && (
          <Card.Footer className="text-center">
            <Button
              as={Link}
              to="/kits"
              variant="link"
              size="sm"
            >
              View All Kits ({activeKits.length})
            </Button>
          </Card.Footer>
        )}
      </Card.Body>
    </Card>
  );
};

export default MyKits;

