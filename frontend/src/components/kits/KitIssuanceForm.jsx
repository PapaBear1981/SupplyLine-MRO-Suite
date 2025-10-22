import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert, Row, Col, Badge } from 'react-bootstrap';
import { FaBox, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import { issueFromKit, fetchKitItems } from '../../store/kitsSlice';

const KitIssuanceForm = ({ show, onHide, kitId, preSelectedItem = null }) => {
  const dispatch = useDispatch();
  const { kitItems, loading, error } = useSelector((state) => state.kits);
  
  const [formData, setFormData] = useState({
    item_type: '',
    item_id: '',
    quantity: '',
    purpose: '',
    work_order: '',
    notes: ''
  });
  
  const [validated, setValidated] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [quantityError, setQuantityError] = useState('');

  // Pre-select item if provided
  useEffect(() => {
    if (preSelectedItem) {
      setFormData(prev => ({
        ...prev,
        item_type: preSelectedItem.source === 'item' ? preSelectedItem.item_type : 'expendable',
        item_id: preSelectedItem.id
      }));
      setSelectedItem(preSelectedItem);
    }
  }, [preSelectedItem]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear quantity error when user changes quantity
    if (name === 'quantity') {
      setQuantityError('');
    }
  };

  const validateQuantity = () => {
    const requestedQty = parseFloat(formData.quantity);
    const availableQty = selectedItem?.quantity || 0;

    if (!requestedQty || requestedQty <= 0) {
      setQuantityError('Quantity must be greater than 0');
      return false;
    }

    if (requestedQty > availableQty) {
      setQuantityError(`Requested quantity exceeds available quantity (${availableQty})`);
      return false;
    }

    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false || !validateQuantity()) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    // Prepare data for submission
    const issuanceData = {
      item_type: formData.item_type,
      item_id: parseInt(formData.item_id),
      quantity: parseFloat(formData.quantity),
      purpose: formData.purpose,
      work_order: formData.work_order,
      notes: formData.notes
    };

    dispatch(issueFromKit({ kitId, data: issuanceData }))
      .unwrap()
      .then(() => {
        setShowSuccess(true);
        // Reset form after short delay
        setTimeout(() => {
          resetForm();
          onHide();
        }, 1500);
      })
      .catch((err) => {
        console.error('Failed to issue item:', err);
      });
  };

  const resetForm = () => {
    setFormData({
      item_type: '',
      item_id: '',
      quantity: '',
      purpose: '',
      work_order: '',
      notes: ''
    });
    setSelectedItem(null);
    setValidated(false);
    setShowSuccess(false);
    setQuantityError('');
  };

  const handleClose = () => {
    resetForm();
    onHide();
  };

  // Check if item is low stock or will be after issuance
  const willBeLowStock = () => {
    if (!selectedItem) return false;
    const remainingQty = selectedItem.quantity - parseFloat(formData.quantity || 0);
    return selectedItem.minimum_stock_level && remainingQty <= selectedItem.minimum_stock_level;
  };

  return (
    <Modal show={show} onHide={handleClose} size="lg" centered backdrop="static" data-testid="issuance-modal">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaBox className="me-2" />
          Issue Item from Kit
        </Modal.Title>
      </Modal.Header>
      
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {showSuccess && (
            <Alert variant="success" className="d-flex align-items-center">
              <FaCheckCircle className="me-2" />
              Item issued successfully! Inventory updated.
            </Alert>
          )}

          {error && (
            <Alert variant="danger">
              {error.message || 'Failed to issue item'}
            </Alert>
          )}

          {/* Selected Item Details */}
          {selectedItem && (
            <Alert variant="info" className="mb-3">
              <Row>
                <Col md={6}>
                  <strong>Part Number:</strong> {selectedItem.part_number}<br />
                  <strong>Description:</strong> {selectedItem.description}<br />
                  <strong>Type:</strong> <Badge bg="secondary">{selectedItem.item_type || selectedItem.source}</Badge>
                </Col>
                <Col md={6}>
                  <strong>Available Quantity:</strong> {selectedItem.quantity} {selectedItem.unit || ''}<br />
                  {selectedItem.minimum_stock_level && (
                    <>
                      <strong>Minimum Stock:</strong> {selectedItem.minimum_stock_level}<br />
                    </>
                  )}
                  <strong>Location:</strong> {selectedItem.location || 'N/A'}
                </Col>
              </Row>
            </Alert>
          )}

          {/* Quantity */}
          <Form.Group className="mb-3">
            <Form.Label>Quantity *</Form.Label>
            <Form.Control
              type="number"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              min="0.01"
              step="0.01"
              required
              isInvalid={!!quantityError}
              placeholder="Enter quantity to issue"
            />
            <Form.Control.Feedback type="invalid">
              {quantityError || 'Please enter a valid quantity.'}
            </Form.Control.Feedback>
            {selectedItem && formData.quantity && !quantityError && (
              <Form.Text className="text-muted">
                Remaining after issuance: {(selectedItem.quantity - parseFloat(formData.quantity)).toFixed(2)} {selectedItem.unit || ''}
              </Form.Text>
            )}
          </Form.Group>

          {/* Low Stock Warning */}
          {willBeLowStock() && (
            <Alert variant="warning" className="d-flex align-items-center mb-3">
              <FaExclamationTriangle className="me-2" />
              <div>
                <strong>Low Stock Warning:</strong> This issuance will bring the item below minimum stock level.
                An automatic reorder request will be generated.
              </div>
            </Alert>
          )}

          {/* Work Order */}
          <Form.Group className="mb-3">
            <Form.Label>Work Order Number (Optional)</Form.Label>
            <Form.Control
              type="text"
              name="work_order"
              value={formData.work_order}
              onChange={handleChange}
              placeholder="Enter work order number"
            />
            <Form.Text className="text-muted">
              Optional: Enter work order number if applicable
            </Form.Text>
          </Form.Group>

          {/* Purpose */}
          <Form.Group className="mb-3">
            <Form.Label>Purpose *</Form.Label>
            <Form.Select
              name="purpose"
              value={formData.purpose}
              onChange={handleChange}
              required
            >
              <option value="">-- Select purpose --</option>
              <option value="maintenance">Maintenance</option>
              <option value="repair">Repair</option>
              <option value="inspection">Inspection</option>
              <option value="installation">Installation</option>
              <option value="replacement">Replacement</option>
              <option value="other">Other</option>
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Please select a purpose.
            </Form.Control.Feedback>
          </Form.Group>

          {/* Notes */}
          <Form.Group className="mb-3">
            <Form.Label>Notes (Optional)</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Additional notes or comments..."
            />
          </Form.Group>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="primary" type="submit" disabled={loading || showSuccess}>
            {loading ? 'Issuing...' : showSuccess ? 'Issued!' : 'Issue Item'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default KitIssuanceForm;

