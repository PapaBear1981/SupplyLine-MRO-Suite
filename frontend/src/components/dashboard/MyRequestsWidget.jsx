import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Spinner, Badge } from 'react-bootstrap';
import { FaClipboardList, FaExternalLinkAlt, FaInfoCircle } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { fetchOrders } from '../../store/ordersSlice';
import { formatDistanceToNow } from 'date-fns';

const statusVariantMap = {
  new: 'secondary',
  awaiting_info: 'warning',
  in_progress: 'info',
  ordered: 'primary',
  shipped: 'info',
  received: 'success',
  cancelled: 'secondary',
};

const priorityVariantMap = {
  critical: 'danger',
  high: 'warning',
  normal: 'secondary',
  low: 'info',
};

const MyRequestsWidget = () => {
  const dispatch = useDispatch();
  const { list, loading } = useSelector((state) => state.orders);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchOrders({ sort: 'created', limit: 50 }));
  }, [dispatch]);

  // Filter to get user's open requests (not received or cancelled)
  const myOpenRequests = list
    .filter((order) =>
      order.requester_id === user?.id &&
      !['received', 'cancelled'].includes(order.status)
    )
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
    .slice(0, 5); // Limit to 5 most recent

  // Count requests needing attention
  const alertCount = myOpenRequests.filter((order) => order.needs_more_info).length;

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div className="d-flex align-items-center">
          <FaClipboardList className="me-2 text-primary" />
          <span>My Open Requests</span>
        </div>
        <div className="d-flex align-items-center gap-2">
          {alertCount > 0 && (
            <Badge bg="warning" pill title="Requests needing attention">
              <FaInfoCircle className="me-1" />
              {alertCount}
            </Badge>
          )}
          <Badge bg="secondary" pill>{myOpenRequests.length}</Badge>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        {loading ? (
          <div className="d-flex justify-content-center align-items-center py-4">
            <Spinner animation="border" size="sm" />
          </div>
        ) : myOpenRequests.length === 0 ? (
          <div className="text-center text-muted py-4">
            <p className="mb-1">No open requests</p>
            <small>All your requests have been fulfilled or cancelled.</small>
          </div>
        ) : (
          <ListGroup variant="flush">
            {myOpenRequests.map((order) => (
              <ListGroup.Item key={order.id} className="py-3">
                {order.needs_more_info && (
                  <div className="mb-2">
                    <Badge bg="warning" className="me-1">
                      <FaInfoCircle className="me-1" />
                      Needs Attention
                    </Badge>
                  </div>
                )}
                <div className="d-flex justify-content-between align-items-start">
                  <div className="flex-grow-1">
                    <div className="fw-semibold">{order.title}</div>
                    <div className="small text-muted">
                      {order.created_at && formatDistanceToNow(new Date(order.created_at), { addSuffix: true })}
                    </div>
                    {order.part_number && (
                      <div className="small text-muted">
                        Part #: {order.part_number}
                      </div>
                    )}
                  </div>
                  <div className="text-end">
                    <div className="d-flex flex-column gap-1 align-items-end">
                      <Badge bg={statusVariantMap[order.status] || 'secondary'} className="text-uppercase">
                        {order.status.replace('_', ' ')}
                      </Badge>
                      <Badge bg={priorityVariantMap[order.priority] || 'secondary'}>
                        {order.priority}
                      </Badge>
                    </div>
                  </div>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Card.Body>
      <Card.Footer className="text-end">
        <Link to="/requests" className="text-decoration-none">
          View all requests <FaExternalLinkAlt className="ms-1" />
        </Link>
      </Card.Footer>
    </Card>
  );
};

export default MyRequestsWidget;
