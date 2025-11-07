import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Spinner, Badge } from 'react-bootstrap';
import { FaExclamationTriangle, FaExternalLinkAlt } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { fetchLateOrders } from '../../store/ordersSlice';
import { formatDate } from '../../utils/dateUtils';

const statusVariantMap = {
  new: 'secondary',
  awaiting_info: 'warning',
  in_progress: 'info',
  ordered: 'primary',
  shipped: 'info',
  received: 'success',
  cancelled: 'secondary',
};

const LateOrdersWidget = () => {
  const dispatch = useDispatch();
  const { lateAlerts, alertsLoading } = useSelector((state) => state.orders);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    const canViewOrders = user?.is_admin || (user?.permissions || []).includes('page.orders');
    if (canViewOrders) {
      dispatch(fetchLateOrders({ limit: 5 }));
    }
  }, [dispatch, user]);

  return (
    <Card className="h-100 shadow-sm">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div className="d-flex align-items-center">
          <FaExclamationTriangle className="me-2 text-warning" />
          <span>Late Orders</span>
        </div>
        <Badge bg="secondary" pill>{lateAlerts.length}</Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {alertsLoading ? (
          <div className="d-flex justify-content-center align-items-center py-4">
            <Spinner animation="border" size="sm" />
          </div>
        ) : lateAlerts.length === 0 ? (
          <div className="text-center text-muted py-4">
            <p className="mb-1">All caught up!</p>
            <small>No overdue orders at the moment.</small>
          </div>
        ) : (
          <ListGroup variant="flush">
            {lateAlerts.map((order) => (
              <ListGroup.Item key={order.id} className="py-3">
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <div className="fw-semibold">{order.title}</div>
                    <div className="small text-muted">
                      Due {order.expected_due_date ? formatDate(order.expected_due_date) : 'N/A'}
                    </div>
                    <div className="small">
                      {order.days_overdue != null && (
                        <span className="text-danger fw-semibold">
                          {order.days_overdue} day{order.days_overdue === 1 ? '' : 's'} overdue
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-end">
                    <Badge bg={statusVariantMap[order.status] || 'secondary'} className="text-uppercase">
                      {order.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Card.Body>
      <Card.Footer className="text-end bg-light">
        <Link to="/orders" className="text-decoration-none">
          View all orders <FaExternalLinkAlt className="ms-1" />
        </Link>
      </Card.Footer>
    </Card>
  );
};

export default LateOrdersWidget;
