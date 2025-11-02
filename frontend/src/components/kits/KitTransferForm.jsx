import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert, Row, Col, Badge, Card } from 'react-bootstrap';
import { FaExchangeAlt, FaCheckCircle, FaWarehouse, FaBox, FaSearch } from 'react-icons/fa';
import { createTransfer } from '../../store/kitTransfersSlice';
import { fetchKits, fetchKitItems } from '../../store/kitsSlice';
import api from '../../services/api';
import KitItemBarcode from './KitItemBarcode';

const KitTransferForm = ({ show, onHide, sourceKitId = null, preSelectedItem = null }) => {
  const dispatch = useDispatch();
  const { kits, kitItems } = useSelector((state) => state.kits);
  const { loading, error } = useSelector((state) => state.kitTransfers);

  const [formData, setFormData] = useState({
    from_location_type: sourceKitId ? 'kit' : '',
    from_location_id: sourceKitId || '',
    to_location_type: '',
    to_location_id: '',
    box_id: '',  // Added for destination box selection
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

  // Destination kit boxes state
  const [kitBoxes, setKitBoxes] = useState([]);
  const [loadingBoxes, setLoadingBoxes] = useState(false);

  // Warehouse items state (for when source is warehouse)
  const [warehouseItems, setWarehouseItems] = useState([]);
  const [loadingWarehouseItems, setLoadingWarehouseItems] = useState(false);
  const [warehouseSearchTerm, setWarehouseSearchTerm] = useState('');

  // Barcode modal state for kit-to-kit expendable transfers
  const [showBarcodeModal, setShowBarcodeModal] = useState(false);
  const [transferredItem, setTransferredItem] = useState(null);

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
      // Backend returns { warehouses: [...], pagination: {...} }
      const warehousesData = response.data.warehouses || response.data;
      setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
    } catch (err) {
      console.error('Failed to load warehouses:', err);
    } finally {
      setLoadingWarehouses(false);
    }
  };

  // Load kit boxes when destination kit is selected
  const loadKitBoxes = async (kitId) => {
    setLoadingBoxes(true);
    try {
      const response = await api.get(`/kits/${kitId}/boxes`);
      setKitBoxes(response.data || []);
    } catch (err) {
      console.error('Failed to load kit boxes:', err);
      setKitBoxes([]);
    } finally {
      setLoadingBoxes(false);
    }
  };

  // Load warehouse items when source warehouse is selected
  const loadWarehouseItems = async (warehouseId, searchTerm = '') => {
    setLoadingWarehouseItems(true);
    try {
      const params = {};
      if (searchTerm) {
        params.search = searchTerm;
      }
      const response = await api.get(`/warehouses/${warehouseId}/inventory`, { params });
      // Backend returns { warehouse: {...}, inventory: [...], total: N }
      setWarehouseItems(response.data.inventory || []);
    } catch (err) {
      console.error('Failed to load warehouse items:', err);
      setWarehouseItems([]);
    } finally {
      setLoadingWarehouseItems(false);
    }
  };

  // Load items when source is selected
  useEffect(() => {
    if (formData.from_location_type === 'kit' && formData.from_location_id) {
      dispatch(fetchKitItems({ kitId: formData.from_location_id }));
    } else if (formData.from_location_type === 'warehouse' && formData.from_location_id) {
      loadWarehouseItems(formData.from_location_id, warehouseSearchTerm);
    }
  }, [formData.from_location_type, formData.from_location_id, dispatch, warehouseSearchTerm]);

  // Debounced search for warehouse items
  useEffect(() => {
    if (formData.from_location_type === 'warehouse' && formData.from_location_id && warehouseSearchTerm !== '') {
      const timer = setTimeout(() => {
        loadWarehouseItems(formData.from_location_id, warehouseSearchTerm);
      }, 300); // 300ms debounce

      return () => clearTimeout(timer);
    }
  }, [formData.from_location_type, formData.from_location_id, warehouseSearchTerm]);

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

    // Load boxes when destination kit is selected
    if (name === 'to_location_id' && formData.to_location_type === 'kit' && value) {
      loadKitBoxes(value);
      // Reset box selection when kit changes
      setFormData(prev => ({
        ...prev,
        box_id: ''
      }));
    }

    // Update selected item when item selection changes
    if (name === 'item_id' && formData.from_location_id) {
      const availableItems = getAvailableItems();
      const item = availableItems.find(i => i.id === parseInt(value));
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
      box_id: formData.box_id ? parseInt(formData.box_id) : undefined,  // Include box_id if destination is kit
      item_type: formData.item_type,
      item_id: parseInt(formData.item_id),
      quantity: parseFloat(formData.quantity),
      notes: formData.notes
    };

    dispatch(createTransfer(transferData))
      .unwrap()
      .then((transferResponse) => {
        const isKitToKit =
          formData.from_location_type === 'kit' && formData.to_location_type === 'kit';
        const transferItemType = transferResponse?.item_type || formData.item_type;
        const isExpendableTransfer = transferItemType === 'expendable';
        const shouldShowBarcode = isKitToKit && isExpendableTransfer;

        let barcodeItem = null;
        if (shouldShowBarcode) {
          const baseItem = selectedItem || preSelectedItem || {};
          const destinationKitId = parseInt(formData.to_location_id);
          const destinationBoxId = formData.box_id ? parseInt(formData.box_id) : baseItem.box_id;
          const transferredQuantity = parseFloat(formData.quantity) || transferResponse.quantity;

          barcodeItem = {
            ...baseItem,
            item_type: 'expendable',
            source: 'expendable',
            item_id:
              baseItem.item_id || baseItem.expendable_id || transferResponse.item_id || baseItem.id,
            kit_item_id: baseItem.kit_item_id || baseItem.id,
            kit_id: destinationKitId,
            box_id: destinationBoxId,
            quantity: transferredQuantity,
            part_number: baseItem.part_number || transferResponse.part_number,
            description: baseItem.description || transferResponse.description,
            lot_number: baseItem.lot_number || transferResponse.lot_number,
            serial_number: baseItem.serial_number || transferResponse.serial_number,
            tracking_type:
              baseItem.tracking_type || (transferResponse.serial_number ? 'serial' : 'lot')
          };
          if (barcodeItem.item_id) {
            setTransferredItem(barcodeItem);
          } else {
            barcodeItem = null;
          }
        }

        setShowSuccess(true);
        setTimeout(() => {
          resetForm();
          onHide();
          if (shouldShowBarcode && barcodeItem) {
            setShowBarcodeModal(true);
          }
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
      box_id: '',
      item_type: '',
      item_id: '',
      quantity: '',
      notes: ''
    });
    setSelectedItem(null);
    setKitBoxes([]);
    setWarehouseItems([]);
    setWarehouseSearchTerm('');
    setValidated(false);
    setShowSuccess(false);
    setQuantityError('');
  };

  const handleClose = () => {
    resetForm();
    setTransferredItem(null);
    setShowBarcodeModal(false);
    onHide();
  };

  // Get available items based on source
  const getAvailableItems = () => {
    if (!formData.from_location_id) {
      return [];
    }

    if (formData.from_location_type === 'kit') {
      const items = kitItems[formData.from_location_id] || { items: [], expendables: [] };
      return [
        ...items.items.map(item => ({ ...item, source: 'item' })),
        ...items.expendables.map(exp => ({ ...exp, source: 'expendable' }))
      ];
    } else if (formData.from_location_type === 'warehouse') {
      // Warehouse items already have the correct structure from the API
      // Backend returns items with item_type, tracking_number, tracking_type already set
      return warehouseItems.map(item => ({
        ...item,
        source: item.item_type === 'tool' || item.item_type === 'chemical' ? 'item' : 'expendable',
        // Ensure we have the part_number field for display (tools use tool_number)
        part_number: item.part_number || item.tool_number,
        quantity: item.quantity || 1
      }));
    }

    return [];
  };

  const availableItems = getAvailableItems();

  // Handle warehouse search
  const handleWarehouseSearch = (e) => {
    setWarehouseSearchTerm(e.target.value);
  };

  return (
    <>
      <Modal show={show} onHide={handleClose} size="lg" centered backdrop="static" data-testid="transfer-modal">
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

              {/* Warehouse Search - Only show when warehouse is selected as source */}
              {formData.from_location_type === 'warehouse' && formData.from_location_id && (
                <Row>
                  <Col>
                    <Form.Group className="mb-3">
                      <Form.Label>
                        <FaSearch className="me-2" />
                        Search Warehouse Inventory
                      </Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Search by part number, serial, lot, or description..."
                        value={warehouseSearchTerm}
                        onChange={handleWarehouseSearch}
                      />
                      <Form.Text className="text-muted">
                        {loadingWarehouseItems
                          ? 'Searching...'
                          : `Found ${availableItems.length} item${availableItems.length !== 1 ? 's' : ''}`}
                      </Form.Text>
                    </Form.Group>
                  </Col>
                </Row>
              )}
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

              {/* Box Selection - Only show when destination is a kit */}
              {formData.to_location_type === 'kit' && formData.to_location_id && (
                <Row>
                  <Col>
                    <Form.Group className="mb-3">
                      <Form.Label>
                        <FaBox className="me-2" />
                        Destination Box *
                      </Form.Label>
                      <Form.Select
                        name="box_id"
                        value={formData.box_id}
                        onChange={handleChange}
                        required
                        disabled={loadingBoxes}
                      >
                        <option value="">
                          {loadingBoxes ? 'Loading boxes...' : '-- Select box --'}
                        </option>
                        {kitBoxes.map((box) => (
                          <option key={box.id} value={box.id}>
                            Box {box.box_number} - {box.box_type} {box.description ? `(${box.description})` : ''}
                          </option>
                        ))}
                      </Form.Select>
                      <Form.Text className="text-muted">
                        Select which box in the kit to place this item
                      </Form.Text>
                      <Form.Control.Feedback type="invalid">
                        Please select a destination box
                      </Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>
              )}
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
              <option value="">
                {formData.from_location_type === 'warehouse' && loadingWarehouseItems
                  ? 'Loading items...'
                  : '-- Select an item --'}
              </option>
              {availableItems.map((item) => (
                <option key={`${item.source}-${item.id}`} value={item.id}>
                  {item.part_number || item.tool_number} - {item.description} - Available: {item.quantity}
                </option>
              ))}
            </Form.Select>
            <Form.Text className="text-muted">
              {formData.from_location_type === 'warehouse'
                ? 'Select an item from the warehouse to transfer'
                : formData.from_location_type === 'kit'
                ? 'Select an item from the kit to transfer'
                : 'Select a source location first'}
            </Form.Text>
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

      <KitItemBarcode
        show={showBarcodeModal}
        onHide={() => {
          setShowBarcodeModal(false);
          setTransferredItem(null);
        }}
        item={transferredItem}
      />
    </>
  );
};

export default KitTransferForm;

