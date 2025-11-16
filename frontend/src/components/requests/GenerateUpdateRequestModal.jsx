import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Form, Button, Alert } from 'react-bootstrap';
import { FaPaperPlane, FaSync } from 'react-icons/fa';
import { sendOrderMessage } from '../../store/ordersSlice';

const GenerateUpdateRequestModal = ({ show, onHide, order }) => {
  const dispatch = useDispatch();
  const { messageActionLoading } = useSelector((state) => state.orders);

  const [message, setMessage] = useState('');
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    // Reset form when modal closes
    if (!show) {
      setMessage('');
      setSubmitError(null);
      setSubmitSuccess(false);
    }
  }, [show]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);

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
      setTimeout(() => {
        onHide();
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
            disabled={messageActionLoading || submitSuccess}
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
