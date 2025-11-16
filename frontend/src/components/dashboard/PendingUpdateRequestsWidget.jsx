import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, ListGroup, Spinner, Badge } from 'react-bootstrap';
import { FaEnvelope, FaExternalLinkAlt } from 'react-icons/fa';
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

const PendingUpdateRequestsWidget = () => {
  const dispatch = useDispatch();
  const { list, loading } = useSelector((state) => state.orders);

  useEffect(() => {
    dispatch(fetchOrders({ sort: 'created', limit: 50 }));
  }, [dispatch]);

  // Filter orders that have messages (indicating update requests) and are still open
  const ordersWithMessages = list
    .filter((order) =>
      order.message_count > 0 &&
      !['received', 'cancelled'].includes(order.status)
    )
    .sort((a, b) => {
      // Sort by latest_message_at descending
      const dateA = a.latest_message_at ? new Date(a.latest_message_at) : new Date(0);
      const dateB = b.latest_message_at ? new Date(b.latest_message_at) : new Date(0);
      return dateB - dateA;
    })
    .slice(0, 5); // Limit to 5 most recent

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div className="d-flex align-items-center">
          <FaEnvelope className="me-2 text-info" />
          <span>Pending Update Requests</span>
        </div>
        <Badge bg={ordersWithMessages.length > 0 ? 'info' : 'secondary'} pill>
          {ordersWithMessages.length}
        </Badge>
      </Card.Header>
      <Card.Body className="p-0">
        {loading ? (
          <div className="d-flex justify-content-center align-items-center py-4">
            <Spinner animation="border" size="sm" />
          </div>
        ) : ordersWithMessages.length === 0 ? (
          <div className="text-center text-muted py-4">
            <p className="mb-1">No pending update requests</p>
            <small>Orders with messages will appear here.</small>
          </div>
        ) : (
          <ListGroup variant="flush">
            {ordersWithMessages.map((order) => (
              <ListGroup.Item key={order.id} className="py-3">
                <div className="d-flex justify-content-between align-items-start">
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-center gap-2 mb-1">
                      <span className="fw-semibold">{order.title}</span>
                      <Badge bg="info" pill title="Message count">
                        <FaEnvelope className="me-1" />
                        {order.message_count}
                      </Badge>
                    </div>
                    <div className="small text-muted">
                      {order.latest_message_at && (
                        <>Last message {formatDistanceToNow(new Date(order.latest_message_at), { addSuffix: true })}</>
                      )}
                    </div>
                    {order.requested_by_name && (
                      <div className="small text-muted">
                        Requested by: {order.requested_by_name}
                      </div>
                    )}
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
        <Link to="/orders" className="text-decoration-none">
          View all orders <FaExternalLinkAlt className="ms-1" />
        </Link>
      </Card.Footer>
    </Card>
  );
};

export default PendingUpdateRequestsWidget;
