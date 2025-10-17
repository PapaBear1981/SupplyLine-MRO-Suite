import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { Form, Button, Alert, Spinner, Row, Col } from 'react-bootstrap';
import { submitCountResult } from '../../store/cycleCountSlice';
import PropTypes from 'prop-types';

const CycleCountItemForm = ({ item, onSuccess }) => {
  const dispatch = useDispatch();

  const [formData, setFormData] = useState({
    actual_quantity: '',
    actual_location: '',
    condition: 'good',
    notes: ''
  });

  const [validated, setValidated] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Pre-fill the form with expected values
    if (item) {
      setFormData({
        actual_quantity: item.expected_quantity.toString(),
        actual_location: item.location,
        condition: 'good',
        notes: ''
      });
    }
  }, [item]);

  // Handle success callback after submission
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 1500);

      // Prevent state updates after unmount
      return () => clearTimeout(timer);
    }
  }, [success, onSuccess]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
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
    setSubmitting(true);
    setError(null);

    try {
      // Convert quantity to number
      const resultData = {
        ...formData,
        actual_quantity: parseInt(formData.actual_quantity, 10)
      };

      await dispatch(submitCountResult({
        itemId: item.id,
        resultData
      })).unwrap();

      setSuccess(true);
    } catch (err) {
      setError(err.error || 'An error occurred while submitting the count result');
    } finally {
      setSubmitting(false);
    }
  };

  if (!item) {
    return <Alert variant="warning">No item selected</Alert>;
  }

  return (
    <div>
      <div className="mb-4">
        <h5>Item Details</h5>
        <Row className="mb-2">
          <Col md={4} className="fw-bold">Item Type:</Col>
          <Col md={8}>{item.item_type === 'tool' ? 'Tool' : 'Chemical'}</Col>
        </Row>
        <Row className="mb-2">
          <Col md={4} className="fw-bold">Name:</Col>
          <Col md={8}>{item.item_name}</Col>
        </Row>
        <Row className="mb-2">
          <Col md={4} className="fw-bold">Expected Quantity:</Col>
          <Col md={8}>{item.expected_quantity}</Col>
        </Row>
        <Row className="mb-2">
          <Col md={4} className="fw-bold">Expected Location:</Col>
          <Col md={8}>{item.location}</Col>
        </Row>
      </div>

      {success ? (
        <Alert variant="success">
          <Alert.Heading>Count Submitted Successfully</Alert.Heading>
          <p>The count result has been recorded.</p>
        </Alert>
      ) : (
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          {error && (
            <Alert variant="danger">
              <Alert.Heading>Error</Alert.Heading>
              <p>{error}</p>
            </Alert>
          )}

          <Form.Group className="mb-3">
            <Form.Label>Actual Quantity <span className="text-danger">*</span></Form.Label>
            <Form.Control
              type="number"
              name="actual_quantity"
              value={formData.actual_quantity}
              onChange={handleChange}
              required
              min="0"
            />
            <Form.Control.Feedback type="invalid">
              Please enter a valid quantity.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Actual Location <span className="text-danger">*</span></Form.Label>
            <Form.Control
              type="text"
              name="actual_location"
              value={formData.actual_location}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please enter the actual location.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Condition</Form.Label>
            <Form.Select
              name="condition"
              value={formData.condition}
              onChange={handleChange}
            >
              <option value="good">Good</option>
              <option value="damaged">Damaged</option>
              <option value="expired">Expired</option>
              <option value="missing">Missing</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Notes</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Enter any additional notes about this count"
            />
          </Form.Group>

          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={onSuccess} className="me-2">
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? (
                <>
                  <Spinner
                    as="span"
                    animation="border"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                    className="me-2"
                  />
                  Submitting...
                </>
              ) : (
                'Submit Count'
              )}
            </Button>
          </div>
        </Form>
      )}
    </div>
  );
};

export default CycleCountItemForm;

CycleCountItemForm.propTypes = {
  item: PropTypes.shape({
    id: PropTypes.number.isRequired,
    expected_quantity: PropTypes.number.isRequired,
    location: PropTypes.string,
    item_type: PropTypes.string,
    item_name: PropTypes.string,
  }),
  onSuccess: PropTypes.func,
};
