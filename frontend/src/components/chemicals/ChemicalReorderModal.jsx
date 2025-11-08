import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Modal, Button, Form, Alert, InputGroup } from 'react-bootstrap';
import { requestChemicalReorder, fetchChemicals } from '../../store/chemicalsSlice';

const ChemicalReorderModal = ({ show, onHide, chemical }) => {
  const dispatch = useDispatch();
  const [requestedQuantity, setRequestedQuantity] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate quantity
    const qty = parseInt(requestedQuantity);
    if (!requestedQuantity || isNaN(qty) || qty <= 0) {
      setError('Please enter a valid quantity greater than 0');
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await dispatch(requestChemicalReorder({
        id: chemical.id,
        requested_quantity: qty,
        notes: notes.trim() || undefined
      })).unwrap();

      // Show success message
      setSuccess(true);

      // Refresh the chemicals list
      dispatch(fetchChemicals());

      // Close modal after a short delay to show success message
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      console.error('Failed to request reorder:', err);
      setError(err.error || err.message || 'Failed to request reorder. Please try again.');
      setSubmitting(false);
    }
  };

  // Handle modal close
  const handleClose = () => {
    setRequestedQuantity('');
    setNotes('');
    setError(null);
    setSuccess(false);
    setSubmitting(false);
    onHide();
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Request Chemical Reorder</Modal.Title>
      </Modal.Header>
      <Form onSubmit={handleSubmit}>
        <Modal.Body>
          {error && (
            <Alert variant="danger" onClose={() => setError(null)} dismissible>
              {error}
            </Alert>
          )}

          {success && (
            <Alert variant="success">
              Reorder request submitted successfully! This chemical will appear in "Chemicals Needing Reorder" on the Orders page.
            </Alert>
          )}

          {chemical && !success && (
            <>
              <Alert variant="info" className="mb-3">
                <i className="bi bi-info-circle me-2"></i>
                <strong>Note:</strong> This will create a reorder request. The chemical will appear in the
                "Chemicals Needing Reorder" section on the Orders page where it can be processed and ordered.
              </Alert>

              <div className="mb-3">
                <p className="mb-1">
                  <strong>Part Number:</strong> {chemical.part_number}
                </p>
                <p className="mb-1">
                  <strong>Lot Number:</strong> {chemical.lot_number}
                </p>
                <p className="mb-1">
                  <strong>Description:</strong> {chemical.description || 'N/A'}
                </p>
                <p className="mb-1">
                  <strong>Manufacturer:</strong> {chemical.manufacturer || 'N/A'}
                </p>
                <p className="mb-0">
                  <strong>Current Quantity:</strong> {chemical.quantity} {chemical.unit}
                </p>
              </div>

              <hr />

              <Form.Group className="mb-3" controlId="requestedQuantity">
                <Form.Label>
                  Requested Quantity <span className="text-danger">*</span>
                </Form.Label>
                <InputGroup>
                  <Form.Control
                    type="number"
                    value={requestedQuantity}
                    onChange={(e) => setRequestedQuantity(e.target.value)}
                    placeholder="Enter quantity to order"
                    min="1"
                    step="1"
                    required
                    disabled={submitting}
                  />
                  <InputGroup.Text>{chemical.unit}</InputGroup.Text>
                </InputGroup>
                <Form.Text className="text-muted">
                  How many {chemical.unit} do you need to order?
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3" controlId="reorderNotes">
                <Form.Label>Request Notes (Optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any notes about this reorder request (e.g., urgency, preferred vendor)..."
                  maxLength={500}
                  disabled={submitting}
                />
                <Form.Text className="text-muted">
                  {notes.length}/500 characters
                </Form.Text>
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose} disabled={submitting}>
            {success ? 'Close' : 'Cancel'}
          </Button>
          {!success && (
            <Button
              variant="primary"
              type="submit"
              disabled={submitting || !requestedQuantity}
            >
              {submitting ? 'Submitting...' : 'Submit Reorder Request'}
            </Button>
          )}
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default ChemicalReorderModal;
