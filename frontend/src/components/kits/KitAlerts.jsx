import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Alert, Badge, Button, Row, Col } from 'react-bootstrap';
import { FaExclamationTriangle, FaExclamationCircle, FaInfoCircle, FaTimes } from 'react-icons/fa';
import { fetchKitAlerts } from '../../store/kitsSlice';

const KitAlerts = ({ kitId }) => {
  const dispatch = useDispatch();
  const { kitAlerts } = useSelector((state) => state.kits);
  
  const alerts = kitAlerts[kitId] || { alerts: [], alert_count: 0 };

  useEffect(() => {
    if (kitId) {
      dispatch(fetchKitAlerts(kitId));
    }
  }, [dispatch, kitId]);

  if (!alerts.alerts || alerts.alerts.length === 0) {
    return null;
  }

  const getAlertVariant = (severity) => {
    const variants = {
      high: 'danger',
      medium: 'warning',
      low: 'info'
    };
    return variants[severity] || 'info';
  };

  const getAlertIcon = (severity) => {
    const icons = {
      high: <FaExclamationCircle />,
      medium: <FaExclamationTriangle />,
      low: <FaInfoCircle />
    };
    return icons[severity] || <FaInfoCircle />;
  };

  return (
    <Row className="mb-4">
      <Col>
        {alerts.alerts.map((alert, index) => (
          <Alert 
            key={index} 
            variant={getAlertVariant(alert.severity)}
            className="d-flex justify-content-between align-items-center"
          >
            <div className="d-flex align-items-center">
              <span className="me-2">{getAlertIcon(alert.severity)}</span>
              <div>
                <strong>{alert.type.replace('_', ' ').toUpperCase()}</strong>
                {alert.count && <Badge bg="dark" className="ms-2">{alert.count}</Badge>}
                <div className="small">{alert.message}</div>
                {alert.part_number && (
                  <div className="small text-muted">Part: {alert.part_number}</div>
                )}
              </div>
            </div>
            <Button variant="link" size="sm" className="text-muted">
              <FaTimes />
            </Button>
          </Alert>
        ))}
      </Col>
    </Row>
  );
};

export default KitAlerts;

