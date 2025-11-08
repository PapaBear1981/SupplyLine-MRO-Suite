import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Modal, Button, Form, Alert } from 'react-bootstrap';
import { markChemicalAsOrdered, fetchChemicals } from '../../store/chemicalsSlice';

const ChemicalReorderModal = ({ show, onHide, chemical }) => {
  const dispatch = useDispatch();
  const [expectedDeliveryDate, setExpectedDeliveryDate] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!expectedDeliveryDate) {
      setError('Expected delivery date is required');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await dispatch(markChemicalAsOrdered({
        id: chemical.id,
        expected_delivery_date: expectedDeliveryDate,
        notes: notes.trim() || undefined
      })).unwrap();

      // Refresh the chemicals list
      dispatch(fetchChemicals());

      // Reset form and close modal
      handleClose();
    } catch (err) {
      console.error('Failed to mark chemical as ordered:', err);
      setError(err.message || 'Failed to create reorder. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle modal close
  const handleClose = () => {
    setExpectedDeliveryDate('');
    setNotes('');
    setError(null);
    onHide();
  };

  // Get minimum date (tomorrow)
  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Reorder Chemical</Modal.Title>
      </Modal.Header>
      <Form onSubmit={handleSubmit}>
        <Modal.Body>
          {error && (
            <Alert variant="danger" onClose={() => setError(null)} dismissible>
              {error}
            </Alert>
          )}

          {chemical && (
            <>
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
                <p className="mb-0">
                  <strong>Manufacturer:</strong> {chemical.manufacturer || 'N/A'}
                </p>
              </div>

              <hr />

              <Form.Group className="mb-3" controlId="expectedDeliveryDate">
                <Form.Label>
                  Expected Delivery Date <span className="text-danger">*</span>
                </Form.Label>
                <Form.Control
                  type="date"
                  value={expectedDeliveryDate}
                  onChange={(e) => setExpectedDeliveryDate(e.target.value)}
                  min={getMinDate()}
                  required
                />
                <Form.Text className="text-muted">
                  Select the expected delivery date for this order
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3" controlId="reorderNotes">
                <Form.Label>Notes (Optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any additional notes about this order..."
                  maxLength={500}
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
            Cancel
          </Button>
          <Button
            variant="success"
            type="submit"
            disabled={!expectedDeliveryDate || submitting}
          >
            {submitting ? 'Processing...' : 'Mark as Ordered'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default ChemicalReorderModal;
