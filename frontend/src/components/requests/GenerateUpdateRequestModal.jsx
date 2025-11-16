import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Form, Button, Alert } from 'react-bootstrap';
import { FaPaperPlane, FaSync } from 'react-icons/fa';
import { sendOrderMessage } from '../../store/ordersSlice';

const GenerateUpdateRequestModal = ({ show, onHide, order }) => {
  const dispatch = useDispatch();
  const { messageActionLoading } = useSelector((state) => state.orders);

  const closeTimeoutRef = useRef(null);
  const [message, setMessage] = useState('');
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    // Reset form when modal closes
    if (!show) {
      setMessage('');
      setSubmitError(null);
      setSubmitSuccess(false);

      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current);
        closeTimeoutRef.current = null;
      }
    }

    return () => {
      if (closeTimeoutRef.current) {
        clearTimeout(closeTimeoutRef.current);
        closeTimeoutRef.current = null;
      }
    };
  }, [show]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);

    if (!order?.id) {
      setSubmitError('Order information is missing.');
      return;
    }

    if (!order?.buyer_id) {
      setSubmitError('A buyer has not been assigned yet. Please try again after a buyer is assigned.');
      return;
    }

    if (closeTimeoutRef.current) {
      clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }

    try {
      await dispatch(sendOrderMessage({
        orderId: order.id,
        data: {
          subject: 'Update Request',
          message: message.trim() || 'Please provide an update on the status of this request.',
        }
      })).unwrap();

      setSubmitSuccess(true);

      // Close modal after short delay to show success message
      closeTimeoutRef.current = setTimeout(() => {
        onHide();
        closeTimeoutRef.current = null;
      }, 1500);
    } catch (err) {
      console.error('Failed to send update request:', err);
      setSubmitError(err.message || 'Failed to send update request');
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="md">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaSync className="me-2" />
          Request Update
        </Modal.Title>
      </Modal.Header>

      <Form onSubmit={handleSubmit}>
        <Modal.Body>
          {submitError && <Alert variant="danger">{submitError}</Alert>}
          {submitSuccess && (
            <Alert variant="success">
              Update request sent successfully!
            </Alert>
          )}

          {!order?.buyer_id && !submitSuccess && (
            <Alert variant="warning" className="mb-3">
              A buyer has not been assigned to this request yet. Update requests can be sent once a buyer is assigned.
            </Alert>
          )}

          <Alert variant="info" className="mb-3">
            <strong>Request:</strong> {order?.title}
            <br />
            <small className="text-muted">
              This will send a message to the buyer requesting an update on your procurement request.
            </small>
          </Alert>

          <Form.Group className="mb-3">
            <Form.Label>Message (Optional)</Form.Label>
            <Form.Control
              as="textarea"
              rows={4}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value);
                setSubmitError(null);
              }}
              placeholder="Add any additional details or specific questions about the status of your request..."
              disabled={submitSuccess}
            />
            <Form.Text className="text-muted">
              Leave blank to send a standard update request, or add your own message for more context.
            </Form.Text>
          </Form.Group>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={onHide} disabled={messageActionLoading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={messageActionLoading || submitSuccess || !order?.buyer_id}
          >
            {messageActionLoading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Sending...
              </>
            ) : submitSuccess ? (
              <>
                <FaPaperPlane className="me-1" />
                Request Sent!
              </>
            ) : (
              <>
                <FaPaperPlane className="me-1" />
                Send Request
              </>
            )}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default GenerateUpdateRequestModal;
