import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert, Toast, ToastContainer } from 'react-bootstrap';
import { returnTool } from '../../store/checkoutsSlice';

const ReturnToolModal = ({ show, onHide, checkoutId, toolInfo }) => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.checkouts);

  // Form state
  const [condition, setCondition] = useState('Good');
  const [returnedBy, setReturnedBy] = useState('');
  const [found, setFound] = useState(false);
  const [notes, setNotes] = useState('');
  const [validated, setValidated] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    const returnData = {
      checkoutId,
      condition,
      returned_by: returnedBy,
      found,
      notes
    };

    dispatch(returnTool(returnData))
      .unwrap()
      .then(() => {
        resetForm();
        setShowSuccess(true);
        // Don't hide the modal immediately, let the user see the success message
        setTimeout(() => {
          onHide();
        }, 1500);
      })
      .catch((err) => {
        console.error('Failed to return tool:', err);
      });
  };

  const resetForm = () => {
    setCondition('Good');
    setReturnedBy('');
    setFound(false);
    setNotes('');
    setValidated(false);
  };

  return (
    <>
      <ToastContainer position="top-end" className="p-3">
        <Toast
          show={showSuccess}
          onClose={() => setShowSuccess(false)}
          delay={1500}
          autohide
          bg="success"
        >
          <Toast.Header>
            <strong className="me-auto">Success</strong>
          </Toast.Header>
          <Toast.Body className="text-white">
            Tool returned successfully!
          </Toast.Body>
        </Toast>
      </ToastContainer>

      <Modal show={show} onHide={onHide} centered>
        <Modal.Header closeButton>
          <Modal.Title>Return Tool</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && (
            <Alert variant="danger">
              {error.error || 'Failed to return tool'}
            </Alert>
          )}

          {showSuccess && (
            <Alert variant="success">
              Tool returned successfully!
            </Alert>
          )}

        {toolInfo && (
          <div className="mb-3">
            <p className="mb-1">
              <strong>Tool:</strong> {toolInfo.tool_number} - {toolInfo.serial_number}
            </p>
            <p className="mb-1">
              <strong>Description:</strong> {toolInfo.description}
            </p>
            <p className="mb-0">
              <strong>Checked out by:</strong> {toolInfo.user_name}
            </p>
          </div>
        )}

        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Condition</Form.Label>
            <Form.Select
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              required
            >
              <option value="Excellent">Excellent</option>
              <option value="Good">Good</option>
              <option value="Fair">Fair</option>
              <option value="Poor">Poor</option>
              <option value="Damaged">Damaged</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Returned By</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter name of person returning the tool"
              value={returnedBy}
              onChange={(e) => setReturnedBy(e.target.value)}
            />
            <Form.Text className="text-muted">
              Leave blank if returned by the person who checked it out
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Tool was found on production floor"
              checked={found}
              onChange={(e) => setFound(e.target.checked)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Notes</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Enter any additional notes about the return"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Return Tool'}
        </Button>
      </Modal.Footer>
    </Modal>
    </>
  );
};

export default ReturnToolModal;
