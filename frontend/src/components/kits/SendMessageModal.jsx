import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Form, Button, Alert } from 'react-bootstrap';
import { FaEnvelope, FaPaperPlane } from 'react-icons/fa';
import { sendMessage } from '../../store/kitMessagesSlice';

const SendMessageModal = ({ show, onHide, kitId, kitName }) => {
  const dispatch = useDispatch();
  const { loading } = useSelector((state) => state.kitMessages);

  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    recipient_id: ''
  });
  const [validated, setValidated] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    // Reset form when modal closes
    if (!show) {
      setFormData({
        subject: '',
        message: '',
        recipient_id: ''
      });
      setValidated(false);
      setSubmitError(null);
      setSubmitSuccess(false);
    } else {
      // Pre-fill subject with kit name when modal opens
      setFormData(prev => ({
        ...prev,
        subject: `Regarding Kit: ${kitName || 'Kit #' + kitId}`
      }));
    }
  }, [show, kitId, kitName]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setSubmitError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);
    setSubmitError(null);

    try {
      await dispatch(sendMessage({
        kitId,
        data: {
          subject: formData.subject,
          message: formData.message,
          recipient_id: formData.recipient_id || null
        }
      })).unwrap();

      setSubmitSuccess(true);
      
      // Close modal after short delay to show success message
      setTimeout(() => {
        onHide();
      }, 1500);
    } catch (err) {
      console.error('Failed to send message:', err);
      setSubmitError(err.message || 'Failed to send message');
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaEnvelope className="me-2" />
          Send Message
        </Modal.Title>
      </Modal.Header>

      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {submitError && <Alert variant="danger">{submitError}</Alert>}
          {submitSuccess && (
            <Alert variant="success">
              Message sent successfully!
            </Alert>
          )}

          <Alert variant="info" className="mb-3">
            <strong>About this message:</strong> This message will be associated with <strong>{kitName || `Kit #${kitId}`}</strong> and can be viewed in the Messages tab.
            Leave the recipient field blank to send a broadcast message to all users with access to this kit.
          </Alert>

          <Form.Group className="mb-3">
            <Form.Label>Subject *</Form.Label>
            <Form.Control
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
              placeholder="Enter message subject"
            />
            <Form.Control.Feedback type="invalid">
              Subject is required
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Recipient (Optional)</Form.Label>
            <Form.Control
              type="text"
              name="recipient_id"
              value={formData.recipient_id}
              onChange={handleChange}
              placeholder="Leave blank for broadcast message"
            />
            <Form.Text className="text-muted">
              Enter a user ID to send to a specific person, or leave blank to broadcast to all users with kit access
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Message *</Form.Label>
            <Form.Control
              as="textarea"
              rows={6}
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
              placeholder="Type your message here..."
            />
            <Form.Control.Feedback type="invalid">
              Message is required
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Provide details about issues, requests, or updates related to this kit
            </Form.Text>
          </Form.Group>

          <Alert variant="light" className="mb-0">
            <strong>Common use cases:</strong>
            <ul className="mb-0 mt-2">
              <li>Report missing or damaged items</li>
              <li>Request urgent reorders or replacements</li>
              <li>Notify about kit location changes</li>
              <li>Communicate maintenance or inspection results</li>
              <li>Coordinate kit transfers between locations</li>
            </ul>
          </Alert>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={onHide} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={loading || submitSuccess}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Sending...
              </>
            ) : submitSuccess ? (
              <>
                <FaPaperPlane className="me-1" />
                Message Sent!
              </>
            ) : (
              <>
                <FaPaperPlane className="me-1" />
                Send Message
              </>
            )}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default SendMessageModal;

