import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert, Row, Col, Badge, Card } from 'react-bootstrap';
import { FaExchangeAlt, FaCheckCircle, FaWarehouse, FaBox } from 'react-icons/fa';
import { createTransfer } from '../../store/kitTransfersSlice';
import { fetchKits, fetchKitItems } from '../../store/kitsSlice';
import api from '../../services/api';

const KitTransferForm = ({ show, onHide, sourceKitId = null, preSelectedItem = null }) => {
  const dispatch = useDispatch();
  const { kits, kitItems } = useSelector((state) => state.kits);
  const { loading, error } = useSelector((state) => state.kitTransfers);

  const [formData, setFormData] = useState({
    from_location_type: sourceKitId ? 'kit' : '',
    from_location_id: sourceKitId || '',
    to_location_type: '',
    to_location_id: '',
    item_type: '',
    item_id: '',
    quantity: '',
    notes: ''
  });

  const [validated, setValidated] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [quantityError, setQuantityError] = useState('');

  // Warehouse state
  const [warehouses, setWarehouses] = useState([]);
  const [loadingWarehouses, setLoadingWarehouses] = useState(false);

  // Source kit state (when sourceKitId is provided)
  const [sourceKit, setSourceKit] = useState(null);
  const [loadingSourceKit, setLoadingSourceKit] = useState(false);

  // Load source kit information when sourceKitId is provided
  useEffect(() => {
    const loadSourceKit = async () => {
      if (sourceKitId && show) {
        setLoadingSourceKit(true);
        try {
          const response = await api.get(`/kits/${sourceKitId}`);
          setSourceKit(response.data);
        } catch (err) {
          console.error('Failed to load source kit:', err);
        } finally {
          setLoadingSourceKit(false);
        }
      }
    };
    loadSourceKit();
  }, [sourceKitId, show]);

  // Load kits and warehouses when modal opens
  useEffect(() => {
    if (show) {
      dispatch(fetchKits());
      loadWarehouses();
      // Reset form data with sourceKitId when modal opens
      if (sourceKitId) {
        setFormData(prev => ({
          ...prev,
          from_location_type: 'kit',
          from_location_id: sourceKitId
        }));
      }
    }
  }, [show, dispatch, sourceKitId]);

  const loadWarehouses = async () => {
    setLoadingWarehouses(true);
    try {
      const response = await api.get('/warehouses');
      setWarehouses(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Failed to load warehouses:', err);
    } finally {
      setLoadingWarehouses(false);
    }
  };

  // Load items when source is selected
  useEffect(() => {
    if (formData.from_location_type === 'kit' && formData.from_location_id) {
      dispatch(fetchKitItems({ kitId: formData.from_location_id }));
    }
  }, [formData.from_location_type, formData.from_location_id, dispatch]);

  // Pre-select item if provided
  useEffect(() => {
    if (preSelectedItem) {
      const availableQty = preSelectedItem.available_quantity || preSelectedItem.quantity || 0;
      setFormData(prev => ({
        ...prev,
        item_type: preSelectedItem.source === 'item' ? preSelectedItem.item_type : 'expendable',
        item_id: preSelectedItem.id,
        // Auto-populate quantity with 1 if there's only 1 available
        quantity: availableQty === 1 ? '1' : prev.quantity
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

    if (name === 'quantity') {
      setQuantityError('');
    }

    // Update selected item when item selection changes
    if (name === 'item_id' && formData.from_location_id) {
      const items = kitItems[formData.from_location_id] || { items: [], expendables: [] };
      const allItems = [
        ...items.items.map(item => ({ ...item, source: 'item' })),
        ...items.expendables.map(exp => ({ ...exp, source: 'expendable' }))
      ];
      const item = allItems.find(i => i.id === parseInt(value));
      setSelectedItem(item);
      setFormData(prev => ({
        ...prev,
        item_type: item?.source === 'item' ? item.item_type : 'expendable'
      }));
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

    const transferData = {
      from_location_type: formData.from_location_type,
      from_location_id: parseInt(formData.from_location_id),
      to_location_type: formData.to_location_type,
      to_location_id: parseInt(formData.to_location_id),
      item_type: formData.item_type,
      item_id: parseInt(formData.item_id),
      quantity: parseFloat(formData.quantity),
      notes: formData.notes
    };

    dispatch(createTransfer(transferData))
      .unwrap()
      .then(() => {
        setShowSuccess(true);
        setTimeout(() => {
          resetForm();
          onHide();
        }, 1500);
      })
      .catch((err) => {
        console.error('Failed to create transfer:', err);
      });
  };

  const resetForm = () => {
    setFormData({
      from_location_type: sourceKitId ? 'kit' : '',
      from_location_id: sourceKitId || '',
      to_location_type: '',
      to_location_id: '',
      item_type: '',
      item_id: '',
      quantity: '',
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

  // Get available items based on source
  const getAvailableItems = () => {
    if (formData.from_location_type !== 'kit' || !formData.from_location_id) {
      return [];
    }
    const items = kitItems[formData.from_location_id] || { items: [], expendables: [] };
    return [
      ...items.items.map(item => ({ ...item, source: 'item' })),
      ...items.expendables.map(exp => ({ ...exp, source: 'expendable' }))
    ];
  };

  const availableItems = getAvailableItems();

  return (
    <Modal show={show} onHide={handleClose} size="lg" centered backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaExchangeAlt className="me-2" />
          Transfer Item
        </Modal.Title>
      </Modal.Header>
      
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {showSuccess && (
            <Alert variant="success" className="d-flex align-items-center">
              <FaCheckCircle className="me-2" />
              Transfer created successfully! Awaiting completion.
            </Alert>
          )}

          {error && (
            <Alert variant="danger">
              {error.message || 'Failed to create transfer'}
            </Alert>
          )}

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
                      disabled={!!sourceKitId}
                    >
                      <option value="">-- Select type --</option>
                      <option value="kit">Kit</option>
                      <option value="warehouse">Warehouse</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      {formData.from_location_type === 'kit' ? 'Kit' : 'Warehouse'} *
                    </Form.Label>
                    {formData.from_location_type === 'kit' ? (
                      sourceKitId && sourceKit ? (
                        // Display kit name as text when sourceKitId is provided
                        <Form.Control
                          type="text"
                          value={`${sourceKit.name}${sourceKit.aircraft_type ? ` (${sourceKit.aircraft_type.name})` : ''}`}
                          disabled
                          readOnly
                        />
                      ) : (
                        <Form.Select
                          name="from_location_id"
                          value={formData.from_location_id}
                          onChange={handleChange}
                          required
                          disabled={loadingSourceKit}
                        >
                          <option value="">
                            {loadingSourceKit ? 'Loading kit...' : '-- Select kit --'}
                          </option>
                          {kits?.map(kit => (
                            <option key={kit.id} value={kit.id}>
                              {kit.name}{kit.aircraft_type?.name ? ` (${kit.aircraft_type.name})` : ''}
                            </option>
                          ))}
                        </Form.Select>
                      )
                    ) : (
                      <Form.Select
                        name="from_location_id"
                        value={formData.from_location_id}
                        onChange={handleChange}
                        required
                        disabled={loadingWarehouses}
                      >
                        <option value="">
                          {loadingWarehouses ? 'Loading warehouses...' : '-- Select warehouse --'}
                        </option>
                        {warehouses.map(warehouse => (
                          <option key={warehouse.id} value={warehouse.id}>
                            {warehouse.name} - {warehouse.city}, {warehouse.state}
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
                      <option value="kit">Kit</option>
                      <option value="warehouse">Warehouse</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      {formData.to_location_type === 'kit' ? 'Kit' : 'Warehouse'} *
                    </Form.Label>
                    {formData.to_location_type === 'kit' ? (
                      <Form.Select
                        name="to_location_id"
                        value={formData.to_location_id}
                        onChange={handleChange}
                        required
                      >
                        <option value="">-- Select kit --</option>
                        {kits?.map(kit => (
                          <option key={kit.id} value={kit.id}>
                            {kit.name}{kit.aircraft_type?.name ? ` (${kit.aircraft_type.name})` : ''}
                          </option>
                        ))}
                      </Form.Select>
                    ) : (
                      <Form.Select
                        name="to_location_id"
                        value={formData.to_location_id}
                        onChange={handleChange}
                        required
                        disabled={loadingWarehouses}
                      >
                        <option value="">
                          {loadingWarehouses ? 'Loading warehouses...' : '-- Select warehouse --'}
                        </option>
                        {warehouses.map(warehouse => (
                          <option key={warehouse.id} value={warehouse.id}>
                            {warehouse.name} - {warehouse.city}, {warehouse.state}
                          </option>
                        ))}
                      </Form.Select>
                    )}
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Item Selection */}
          <Form.Group className="mb-3">
            <Form.Label>Select Item *</Form.Label>
            <Form.Select
              name="item_id"
              value={formData.item_id}
              onChange={handleChange}
              required
              disabled={!formData.from_location_id || !!preSelectedItem}
            >
              <option value="">-- Select an item --</option>
              {availableItems.map((item) => (
                <option key={`${item.source}-${item.id}`} value={item.id}>
                  {item.part_number} - {item.description} - Available: {item.quantity}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

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
            />
            <Form.Control.Feedback type="invalid">
              {quantityError || 'Please enter a valid quantity.'}
            </Form.Control.Feedback>
          </Form.Group>

          {/* Notes */}
          <Form.Group className="mb-3">
            <Form.Label>Notes (Optional)</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              name="notes"
              value={formData.notes}
              onChange={handleChange}
            />
          </Form.Group>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="primary" type="submit" disabled={loading || showSuccess}>
            {loading ? 'Creating...' : showSuccess ? 'Created!' : 'Create Transfer'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default KitTransferForm;

