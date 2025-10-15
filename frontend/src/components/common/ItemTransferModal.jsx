import React, { useState, useEffect } from 'react';
import { Modal, Button, Form, Alert, Row, Col, Badge, Card } from 'react-bootstrap';
import { FaExchangeAlt, FaCheckCircle, FaWarehouse, FaBox } from 'react-icons/fa';
import api from '../../services/api';

const ItemTransferModal = ({ show, onHide, item, itemType, onTransferComplete }) => {
  const [formData, setFormData] = useState({
    from_location_type: 'warehouse',
    from_location_id: '',
    to_location_type: '',
    to_location_id: '',
    quantity: '1',
    notes: ''
  });

  const [warehouses, setWarehouses] = useState([]);
  const [kits, setKits] = useState([]);
  const [loadingWarehouses, setLoadingWarehouses] = useState(false);
  const [loadingKits, setLoadingKits] = useState(false);
  const [validated, setValidated] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Load warehouses and kits when modal opens
  useEffect(() => {
    if (show && item) {
      loadWarehouses();
      loadKits();
      
      // Pre-populate source warehouse if item has warehouse_id
      if (item.warehouse_id) {
        setFormData(prev => ({
          ...prev,
          from_location_type: 'warehouse',
          from_location_id: item.warehouse_id.toString()
        }));
      }
    }
  }, [show, item]);

  const loadWarehouses = async () => {
    setLoadingWarehouses(true);
    try {
      const response = await api.get('/warehouses');
      // Backend returns { warehouses: [...], pagination: {...} }
      const warehousesData = response.data.warehouses || response.data;
      setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
    } catch (err) {
      console.error('Failed to load warehouses:', err);
    } finally {
      setLoadingWarehouses(false);
    }
  };

  const loadKits = async () => {
    setLoadingKits(true);
    try {
      const response = await api.get('/kits');
      setKits(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Failed to load kits:', err);
    } finally {
      setLoadingKits(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
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
      const transferData = {
        from_location_type: formData.from_location_type,
        from_location_id: parseInt(formData.from_location_id),
        to_location_type: formData.to_location_type,
        to_location_id: parseInt(formData.to_location_id),
        item_type: itemType,
        item_id: item.id,
        quantity: parseFloat(formData.quantity),
        notes: formData.notes
      };

      await api.post('/transfers', transferData);
      
      setShowSuccess(true);
      setTimeout(() => {
        resetForm();
        onHide();
        if (onTransferComplete) {
          onTransferComplete();
        }
      }, 1500);
    } catch (err) {
      console.error('Failed to create transfer:', err);
      setError(err.response?.data?.error || 'Failed to create transfer');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      from_location_type: 'warehouse',
      from_location_id: '',
      to_location_type: '',
      to_location_id: '',
      quantity: '1',
      notes: ''
    });
    setValidated(false);
    setShowSuccess(false);
    setError(null);
  };

  const handleClose = () => {
    resetForm();
    onHide();
  };

  if (!item) return null;

  const sourceWarehouse = warehouses.find(w => w.id === item.warehouse_id);

  return (
    <Modal show={show} onHide={handleClose} size="lg" centered backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaExchangeAlt className="me-2" />
          Transfer {itemType === 'tool' ? 'Tool' : 'Chemical'}
        </Modal.Title>
      </Modal.Header>
      
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {showSuccess && (
            <Alert variant="success" className="d-flex align-items-center">
              <FaCheckCircle className="me-2" />
              Transfer created successfully!
            </Alert>
          )}

          {error && (
            <Alert variant="danger">
              {error}
            </Alert>
          )}

          {/* Item Information */}
          <Card className="mb-3">
            <Card.Header className="bg-info text-white">
              <strong>Item Details</strong>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <strong>{itemType === 'tool' ? 'Tool Number' : 'Part Number'}:</strong> {item.tool_number || item.part_number}
                </Col>
                <Col md={6}>
                  <strong>{itemType === 'tool' ? 'Serial Number' : 'Lot Number'}:</strong> {item.serial_number || item.lot_number}
                </Col>
              </Row>
              <Row className="mt-2">
                <Col>
                  <strong>Description:</strong> {item.description}
                </Col>
              </Row>
              {sourceWarehouse && (
                <Row className="mt-2">
                  <Col>
                    <strong>Current Location:</strong> <Badge bg="info">{sourceWarehouse.name}</Badge>
                  </Col>
                </Row>
              )}
            </Card.Body>
          </Card>

          {/* Source Location */}
          <Card className="mb-3">
            <Card.Header className="bg-primary text-white">
              <strong>From (Source)</strong>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Location Type *</Form.Label>
                    <Form.Select
                      name="from_location_type"
                      value={formData.from_location_type}
                      onChange={handleChange}
                      required
                    >
                      <option value="">-- Select type --</option>
                      <option value="warehouse">Warehouse</option>
                      <option value="kit">Kit</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      {formData.from_location_type === 'warehouse' ? 'Warehouse' : 'Kit'} *
                    </Form.Label>
                    {formData.from_location_type === 'warehouse' ? (
                      <Form.Select
                        name="from_location_id"
                        value={formData.from_location_id}
                        onChange={handleChange}
                        required
                        disabled={loadingWarehouses}
                      >
                        <option value="">-- Select warehouse --</option>
                        {warehouses.map((warehouse) => (
                          <option key={warehouse.id} value={warehouse.id}>
                            {warehouse.name} ({warehouse.city}, {warehouse.state})
                          </option>
                        ))}
                      </Form.Select>
                    ) : (
                      <Form.Select
                        name="from_location_id"
                        value={formData.from_location_id}
                        onChange={handleChange}
                        required
                        disabled={loadingKits}
                      >
                        <option value="">-- Select kit --</option>
                        {kits.map((kit) => (
                          <option key={kit.id} value={kit.id}>
                            {kit.name}{kit.aircraft_type?.name ? ` (${kit.aircraft_type.name})` : ''}
                          </option>
                        ))}
                      </Form.Select>
                    )}
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Destination Location */}
          <Card className="mb-3">
            <Card.Header className="bg-success text-white">
              <strong>To (Destination)</strong>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Location Type *</Form.Label>
                    <Form.Select
                      name="to_location_type"
                      value={formData.to_location_type}
                      onChange={handleChange}
                      required
                    >
                      <option value="">-- Select type --</option>
                      <option value="warehouse">Warehouse</option>
                      <option value="kit">Kit</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      {formData.to_location_type === 'warehouse' ? 'Warehouse' : 'Kit'} *
                    </Form.Label>
                    {formData.to_location_type === 'warehouse' ? (
                      <Form.Select
                        name="to_location_id"
                        value={formData.to_location_id}
                        onChange={handleChange}
                        required
                        disabled={loadingWarehouses}
                      >
                        <option value="">-- Select warehouse --</option>
                        {warehouses.map((warehouse) => (
                          <option key={warehouse.id} value={warehouse.id}>
                            {warehouse.name} ({warehouse.city}, {warehouse.state})
                          </option>
                        ))}
                      </Form.Select>
                    ) : (
                      <Form.Select
                        name="to_location_id"
                        value={formData.to_location_id}
                        onChange={handleChange}
                        required
                        disabled={loadingKits}
                      >
                        <option value="">-- Select kit --</option>
                        {kits.map((kit) => (
                          <option key={kit.id} value={kit.id}>
                            {kit.name}{kit.aircraft_type?.name ? ` (${kit.aircraft_type.name})` : ''}
                          </option>
                        ))}
                      </Form.Select>
                    )}
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Notes */}
          <Form.Group className="mb-3">
            <Form.Label>Notes (Optional)</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Add any notes about this transfer..."
            />
          </Form.Group>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="primary" type="submit" disabled={submitting || showSuccess}>
            {submitting ? 'Creating Transfer...' : 'Create Transfer'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default ItemTransferModal;

