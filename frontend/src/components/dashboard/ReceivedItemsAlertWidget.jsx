import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Spinner, Badge, Button } from 'react-bootstrap';
import { FaBell, FaCheckCircle, FaExternalLinkAlt, FaTimes } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { fetchRequestAlerts, dismissAlert, dismissAllAlerts } from '../../store/requestAlertsSlice';
import { formatDistanceToNow } from 'date-fns';

const ReceivedItemsAlertWidget = () => {
  const dispatch = useDispatch();
  const { alerts, loading } = useSelector((state) => state.requestAlerts);

  useEffect(() => {
    dispatch(fetchRequestAlerts(false)); // Only fetch non-dismissed alerts
  }, [dispatch]);

  const handleDismiss = (alertId, event) => {
    event.preventDefault();
    event.stopPropagation();
    dispatch(dismissAlert(alertId));
  };

  const handleDismissAll = (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (window.confirm(`Are you sure you want to dismiss all ${alerts.length} alert(s)?`)) {
      dispatch(dismissAllAlerts());
    }
  };

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div className="d-flex align-items-center">
          <FaBell className="me-2 text-warning" />
          <span>Received Items</span>
        </div>
        <div className="d-flex align-items-center gap-2">
          {alerts.length > 0 && (
            <>
              <Badge bg="warning" pill>{alerts.length}</Badge>
              <Button
                variant="link"
                size="sm"
                className="text-decoration-none p-0"
                onClick={handleDismissAll}
                title="Dismiss all alerts"
              >
                Clear All
              </Button>
            </>
          )}
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        {loading ? (
          <div className="d-flex justify-content-center align-items-center py-4">
            <Spinner animation="border" size="sm" />
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center text-muted py-4">
            <FaCheckCircle size={32} className="mb-2 text-success" />
            <p className="mb-1">No new alerts</p>
            <small>You will be notified when requested items are received.</small>
          </div>
        ) : (
          <ListGroup variant="flush">
            {alerts.map((alert) => (
              <ListGroup.Item key={alert.id} className="py-3">
                <div className="d-flex justify-content-between align-items-start">
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-center mb-2">
                      <Badge bg="success" className="me-2">
                        <FaBell className="me-1" />
                        Items Received
                      </Badge>
                      {alert.request_number && (
                        <span className="text-muted small">
                          {alert.request_number}
                        </span>
                      )}
                    </div>
                    <div className="fw-semibold mb-1">
                      <Link
                        to={`/requests?highlight=${alert.request_id}`}
                        className="text-decoration-none"
                      >
                        {alert.request_title || `Request #${alert.request_number}`}
                      </Link>
                    </div>
                    <div className="small text-muted mb-1">{alert.message}</div>
                    <div className="small text-muted">
                      {alert.created_at && formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                    </div>
                  </div>
                  <Button
                    variant="link"
                    size="sm"
                    className="text-muted p-0 ms-2"
                    onClick={(e) => handleDismiss(alert.id, e)}
                    title="Dismiss alert"
                  >
                    <FaTimes />
                  </Button>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Card.Body>
      {alerts.length > 0 && (
        <Card.Footer className="text-end">
          <Link to="/requests" className="text-decoration-none">
            View all requests <FaExternalLinkAlt className="ms-1" />
          </Link>
        </Card.Footer>
      )}
    </Card>
  );
};

export default ReceivedItemsAlertWidget;
