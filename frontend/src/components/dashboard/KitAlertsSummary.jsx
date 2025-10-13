import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Badge, Alert, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaExclamationTriangle, FaBox } from 'react-icons/fa';
import { fetchKits } from '../../store/kitsSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const KitAlertsSummary = () => {
  const dispatch = useDispatch();
  const { kits, loading, error } = useSelector((state) => state.kits);

  useEffect(() => {
    dispatch(fetchKits());
  }, [dispatch]);

  // Get kits with alerts
  const kitsWithAlerts = kits.filter(kit => kit.alert_count > 0);

  // Sort by alert count (highest first)
  const sortedKits = [...kitsWithAlerts].sort((a, b) => b.alert_count - a.alert_count);

  const totalAlerts = kitsWithAlerts.reduce((sum, kit) => sum + (kit.alert_count || 0), 0);

  if (loading && kits.length === 0) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h4 className="mb-0">
            <FaExclamationTriangle className="me-2" />
            Kit Alerts
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
            <FaExclamationTriangle className="me-2" />
            Kit Alerts
          </h4>
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">
            Failed to load kit alerts: {error.message || 'Unknown error'}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">
          <FaExclamationTriangle className="me-2" />
          Kit Alerts
        </h4>
        <Badge bg={totalAlerts > 0 ? "warning" : "success"} pill>
          {totalAlerts}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {kitsWithAlerts.length === 0 ? (
          <Alert variant="success" className="m-3">
            <FaBox className="me-2" />
            All kits are in good condition. No alerts at this time.
          </Alert>
        ) : (
          <ListGroup variant="flush">
            {sortedKits.slice(0, 5).map((kit) => (
              <ListGroup.Item 
                key={kit.id} 
                className="d-flex justify-content-between align-items-center"
              >
                <div className="flex-grow-1">
                  <div className="fw-bold">{kit.name}</div>
                  <div className="text-muted small">
                    {kit.aircraft_type_name || 'Unknown Aircraft'}
                  </div>
                  <div className="text-muted small mt-1">
                    {kit.alert_count} {kit.alert_count === 1 ? 'alert' : 'alerts'} requiring attention
                  </div>
                </div>
                <div className="d-flex align-items-center">
                  <Badge 
                    bg={kit.alert_count > 5 ? "danger" : kit.alert_count > 2 ? "warning" : "info"} 
                    className="me-2"
                  >
                    {kit.alert_count}
                  </Badge>
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
        {kitsWithAlerts.length > 5 && (
          <Card.Footer className="text-center">
            <Button
              as={Link}
              to="/kits"
              variant="link"
              size="sm"
            >
              View All Kits with Alerts ({kitsWithAlerts.length})
            </Button>
          </Card.Footer>
        )}
      </Card.Body>
    </Card>
  );
};

export default KitAlertsSummary;

