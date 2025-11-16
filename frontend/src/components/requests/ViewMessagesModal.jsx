import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Alert, ListGroup, Badge, Spinner } from 'react-bootstrap';
import { FaEnvelope, FaSync } from 'react-icons/fa';
import { fetchOrderMessages } from '../../store/ordersSlice';
import { formatDistanceToNow } from 'date-fns';

const ViewMessagesModal = ({ show, onHide, order }) => {
  const dispatch = useDispatch();
  const { messages: allMessages, loading } = useSelector((state) => state.orders);
  const [fetchError, setFetchError] = useState(null);

  const orderMessages = order?.id ? (allMessages[order.id] || []) : [];

  useEffect(() => {
    if (show && order?.id) {
      setFetchError(null);
      dispatch(fetchOrderMessages(order.id))
        .unwrap()
        .catch((err) => {
          setFetchError(err.message || 'Failed to load messages');
        });
    }
  }, [show, order?.id, dispatch]);

  const handleRefresh = () => {
    if (order?.id) {
      setFetchError(null);
      dispatch(fetchOrderMessages(order.id))
        .unwrap()
        .catch((err) => {
          setFetchError(err.message || 'Failed to load messages');
        });
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaEnvelope className="me-2" />
          Messages for Request
        </Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <Alert variant="info" className="mb-3">
          <strong>Request:</strong> {order?.title}
        </Alert>

        {fetchError && (
          <Alert variant="danger" className="mb-3">
            {fetchError}
          </Alert>
        )}

        <div className="d-flex justify-content-between align-items-center mb-3">
          <h6 className="mb-0">Message History ({orderMessages.length})</h6>
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={handleRefresh}
            disabled={loading}
          >
            <FaSync className={`me-1 ${loading ? 'fa-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {loading && orderMessages.length === 0 ? (
          <div className="text-center py-4">
            <Spinner animation="border" size="sm" className="me-2" />
            Loading messages...
          </div>
        ) : orderMessages.length === 0 ? (
          <div className="text-center text-muted py-4">
            <FaEnvelope size={32} className="mb-2 opacity-50" />
            <p className="mb-0">No messages yet for this request.</p>
          </div>
        ) : (
          <ListGroup>
            {orderMessages.map((msg) => (
              <ListGroup.Item key={msg.id} className="py-3">
                <div className="d-flex justify-content-between align-items-start mb-2">
                  <div>
                    <strong>{msg.sender_name || 'Unknown'}</strong>
                    {msg.recipient_name && (
                      <Badge bg="secondary" className="ms-2">
                        To: {msg.recipient_name}
                      </Badge>
                    )}
                    {!msg.is_read && (
                      <Badge bg="primary" className="ms-2">
                        Unread
                      </Badge>
                    )}
                  </div>
                  <small className="text-muted">
                    {msg.sent_date
                      ? formatDistanceToNow(new Date(msg.sent_date), { addSuffix: true })
                      : 'Unknown date'}
                  </small>
                </div>
                <p className="mb-1 fw-semibold">{msg.subject}</p>
                <p className="mb-0 text-break">{msg.message}</p>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ViewMessagesModal;
