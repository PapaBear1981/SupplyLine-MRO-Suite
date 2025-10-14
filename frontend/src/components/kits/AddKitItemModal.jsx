import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Button, Form, Alert, Row, Col, Badge, Tabs, Tab } from 'react-bootstrap';
import { FaPlus, FaBox, FaTools, FaFlask, FaCheckCircle } from 'react-icons/fa';
import { fetchKitBoxes } from '../../store/kitsSlice';
import api from '../../services/api';
import LotNumberInput from '../common/LotNumberInput';

const AddKitItemModal = ({ show, onHide, kitId, onSuccess }) => {
  const dispatch = useDispatch();
  const { kitBoxes } = useSelector((state) => state.kits);
  
  const [activeTab, setActiveTab] = useState('tool');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [validated, setValidated] = useState(false);

  // Warehouse state
  const [warehouses, setWarehouses] = useState([]);
  const [selectedWarehouse, setSelectedWarehouse] = useState('');
  const [loadingWarehouses, setLoadingWarehouses] = useState(false);

  // Available items from warehouse
  const [availableTools, setAvailableTools] = useState([]);
  const [availableChemicals, setAvailableChemicals] = useState([]);
  const [loadingItems, setLoadingItems] = useState(false);
  
  // Form data for adding existing items
  const [itemFormData, setItemFormData] = useState({
    box_id: '',
    item_type: 'tool',
    item_id: '',
    warehouse_id: '',  // Required for tools/chemicals
    quantity: 1,
    location: ''
  });
  
  // Form data for adding new expendables
  const [expendableFormData, setExpendableFormData] = useState({
    box_id: '',
    part_number: '',
    description: '',
    quantity: 1,
    unit: 'EA',
    minimum_stock_level: 0,
    maximum_stock_level: 0,
    location: '',
    tracking_type: 'lot',
    lot_number: '',
    serial_number: ''
  });

  useEffect(() => {
    if (show && kitId) {
      dispatch(fetchKitBoxes(kitId));
      loadWarehouses();
    }
  }, [show, kitId, dispatch]);

  // Load items when warehouse is selected
  useEffect(() => {
    if (selectedWarehouse) {
      loadAvailableItems(selectedWarehouse);
    }
  }, [selectedWarehouse]);

  const loadWarehouses = async () => {
    setLoadingWarehouses(true);
    try {
      const response = await api.get('/warehouses');
      // Backend returns array directly, not wrapped in {warehouses: [...]}
      setWarehouses(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Failed to load warehouses:', err);
      setError('Failed to load warehouses. Please try again.');
    } finally {
      setLoadingWarehouses(false);
    }
  };

  const loadAvailableItems = async (warehouseId) => {
    if (!warehouseId) {
      setAvailableTools([]);
      setAvailableChemicals([]);
      return;
    }

    setLoadingItems(true);
    try {
      // Load available tools from warehouse
      const toolsResponse = await api.get(`/warehouses/${warehouseId}/tools`);
      const tools = Array.isArray(toolsResponse.data) ? toolsResponse.data : (toolsResponse.data.tools || []);
      setAvailableTools(tools);

      // Load available chemicals from warehouse
      const chemicalsResponse = await api.get(`/warehouses/${warehouseId}/chemicals`);
      const chemicals = Array.isArray(chemicalsResponse.data) ? chemicalsResponse.data : (chemicalsResponse.data.chemicals || []);
      setAvailableChemicals(chemicals);
    } catch (err) {
      console.error('Failed to load available items:', err);
      setError('Failed to load items from warehouse. Please try again.');
    } finally {
      setLoadingItems(false);
    }
  };

  const boxes = kitBoxes[kitId] || [];

  const resetForm = () => {
    setSelectedWarehouse('');
    setItemFormData({
      box_id: '',
      item_type: 'tool',
      item_id: '',
      warehouse_id: '',
      quantity: 1,
      location: ''
    });
    setExpendableFormData({
      box_id: '',
      part_number: '',
      description: '',
      quantity: 1,
      unit: 'EA',
      minimum_stock_level: 0,
      maximum_stock_level: 0,
      location: '',
      tracking_type: 'lot',
      lot_number: '',
      serial_number: ''
    });
    setValidated(false);
    setError(null);
    setSuccess(false);
  };

  const handleClose = () => {
    resetForm();
    onHide();
  };

  const handleItemFormChange = (e) => {
    const { name, value } = e.target;
    setItemFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleExpendableFormChange = (e) => {
    const { name, value } = e.target;
    setExpendableFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmitItem = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);
    setLoading(true);
    setError(null);

    try {
      await api.post(`/kits/${kitId}/items`, {
        box_id: parseInt(itemFormData.box_id),
        item_type: itemFormData.item_type,
        item_id: parseInt(itemFormData.item_id),
        warehouse_id: parseInt(selectedWarehouse),  // Required for transfer tracking
        quantity: parseFloat(itemFormData.quantity),
        location: itemFormData.location
      });

      setSuccess(true);
      setTimeout(() => {
        if (onSuccess) onSuccess();
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to add item to kit');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitExpendable = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);
    setLoading(true);
    setError(null);

    try {
      await api.post(`/kits/${kitId}/expendables`, {
        box_id: parseInt(expendableFormData.box_id),
        part_number: expendableFormData.part_number,
        description: expendableFormData.description,
        quantity: parseFloat(expendableFormData.quantity),
        unit: expendableFormData.unit,
        minimum_stock_level: parseFloat(expendableFormData.minimum_stock_level),
        maximum_stock_level: parseFloat(expendableFormData.maximum_stock_level),
        location: expendableFormData.location,
        tracking_type: expendableFormData.tracking_type,
        lot_number: expendableFormData.lot_number || null,
        serial_number: expendableFormData.serial_number || null
      });

      setSuccess(true);
      setTimeout(() => {
        if (onSuccess) onSuccess();
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to add expendable to kit');
    } finally {
      setLoading(false);
    }
  };

  const getAvailableItems = () => {
    if (itemFormData.item_type === 'tool') {
      return availableTools;
    } else if (itemFormData.item_type === 'chemical') {
      return availableChemicals;
    }
    return [];
  };

  return (
    <Modal show={show} onHide={handleClose} size="lg" centered backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaPlus className="me-2" />
          Add Items to Kit
        </Modal.Title>
      </Modal.Header>

      <Modal.Body>
        {success && (
          <Alert variant="success" className="d-flex align-items-center">
            <FaCheckCircle className="me-2" />
            Item added successfully!
          </Alert>
        )}

        {error && (
          <Alert variant="danger">
            {error}
          </Alert>
        )}

        <Tabs
          activeKey={activeTab}
          onSelect={(k) => setActiveTab(k)}
          className="mb-3"
        >
          <Tab eventKey="tool" title={<><FaTools className="me-1" /> Tools & Chemicals</>}>
            <Form noValidate validated={validated} onSubmit={handleSubmitItem}>
              <Form.Group className="mb-3">
                <Form.Label>Select Box *</Form.Label>
                <Form.Select
                  name="box_id"
                  value={itemFormData.box_id}
                  onChange={handleItemFormChange}
                  required
                >
                  <option value="">Choose a box...</option>
                  {boxes.map(box => (
                    <option key={box.id} value={box.id}>
                      {box.box_number} - {box.box_type} ({box.description})
                    </option>
                  ))}
                </Form.Select>
                <Form.Control.Feedback type="invalid">
                  Please select a box.
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Item Type *</Form.Label>
                <Form.Select
                  name="item_type"
                  value={itemFormData.item_type}
                  onChange={handleItemFormChange}
                  required
                >
                  <option value="tool">Tool</option>
                  <option value="chemical">Chemical</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Source Warehouse *</Form.Label>
                <Form.Select
                  value={selectedWarehouse}
                  onChange={(e) => {
                    setSelectedWarehouse(e.target.value);
                    setItemFormData(prev => ({ ...prev, item_id: '', warehouse_id: e.target.value }));
                  }}
                  required
                  disabled={loadingWarehouses}
                >
                  <option value="">
                    {loadingWarehouses ? 'Loading warehouses...' : 'Select warehouse to transfer from...'}
                  </option>
                  {warehouses.map(warehouse => (
                    <option key={warehouse.id} value={warehouse.id}>
                      {warehouse.name} - {warehouse.city}, {warehouse.state}
                    </option>
                  ))}
                </Form.Select>
                <Form.Control.Feedback type="invalid">
                  Please select a warehouse.
                </Form.Control.Feedback>
                <Form.Text className="text-muted">
                  Tools and chemicals must be transferred from a warehouse
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Select Item *</Form.Label>
                <Form.Select
                  name="item_id"
                  value={itemFormData.item_id}
                  onChange={handleItemFormChange}
                  required
                  disabled={!selectedWarehouse || loadingItems}
                >
                  <option value="">
                    {!selectedWarehouse ? 'Select a warehouse first...' : loadingItems ? 'Loading items...' : 'Choose an item...'}
                  </option>
                  {getAvailableItems().map(item => (
                    <option key={item.id} value={item.id}>
                      {item.tool_number || item.part_number} - {item.description}
                      {item.serial_number && ` | S/N: ${item.serial_number}`}
                      {item.lot_number && ` | Lot: ${item.lot_number}`}
                    </option>
                  ))}
                </Form.Select>
                <Form.Control.Feedback type="invalid">
                  Please select an item.
                </Form.Control.Feedback>
                <Form.Text className="text-muted">
                  {selectedWarehouse
                    ? `Showing items from selected warehouse (${getAvailableItems().length} available)`
                    : 'Select a warehouse to see available items'}
                </Form.Text>
              </Form.Group>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Quantity *</Form.Label>
                    <Form.Control
                      type="number"
                      name="quantity"
                      value={itemFormData.quantity}
                      onChange={handleItemFormChange}
                      min="0.01"
                      step="0.01"
                      required
                    />
                    <Form.Control.Feedback type="invalid">
                      Please enter a valid quantity.
                    </Form.Control.Feedback>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Location (Optional)</Form.Label>
                    <Form.Control
                      type="text"
                      name="location"
                      value={itemFormData.location}
                      onChange={handleItemFormChange}
                      placeholder="e.g., Shelf A3"
                    />
                  </Form.Group>
                </Col>
              </Row>

              <div className="d-flex justify-content-end gap-2">
                <Button variant="secondary" onClick={handleClose} disabled={loading}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" disabled={loading || success}>
                  {loading ? 'Adding...' : success ? 'Added!' : 'Add Item'}
                </Button>
              </div>
            </Form>
          </Tab>

          <Tab eventKey="expendable" title={<><FaBox className="me-1" /> New Expendable</>}>
            <Form noValidate validated={validated} onSubmit={handleSubmitExpendable}>
              <Alert variant="info" className="mb-3">
                <small>Use this tab to add custom expendable items that aren't in the warehouse inventory.</small>
              </Alert>

              <Form.Group className="mb-3">
                <Form.Label>Select Box *</Form.Label>
                <Form.Select
                  name="box_id"
                  value={expendableFormData.box_id}
                  onChange={handleExpendableFormChange}
                  required
                >
                  <option value="">Choose a box...</option>
                  {boxes.map(box => (
                    <option key={box.id} value={box.id}>
                      {box.box_number} - {box.box_type} ({box.description})
                    </option>
                  ))}
                </Form.Select>
                <Form.Control.Feedback type="invalid">
                  Please select a box.
                </Form.Control.Feedback>
              </Form.Group>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Part Number *</Form.Label>
                    <Form.Control
                      type="text"
                      name="part_number"
                      value={expendableFormData.part_number}
                      onChange={handleExpendableFormChange}
                      required
                      placeholder="e.g., EXP-001"
                    />
                    <Form.Control.Feedback type="invalid">
                      Please enter a part number.
                    </Form.Control.Feedback>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Unit *</Form.Label>
                    <Form.Select
                      name="unit"
                      value={expendableFormData.unit}
                      onChange={handleExpendableFormChange}
                      required
                    >
                      <option value="EA">Each (EA)</option>
                      <option value="BOX">Box</option>
                      <option value="PKG">Package</option>
                      <option value="SET">Set</option>
                      <option value="LB">Pounds</option>
                      <option value="GAL">Gallons</option>
                      <option value="L">Liters</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>

              <Form.Group className="mb-3">
                <Form.Label>Description *</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  name="description"
                  value={expendableFormData.description}
                  onChange={handleExpendableFormChange}
                  required
                  placeholder="Describe the expendable item..."
                />
                <Form.Control.Feedback type="invalid">
                  Please enter a description.
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Tracking Type *</Form.Label>
                <div className="d-flex gap-3">
                  <Form.Check
                    type="radio"
                    id="tracking-lot"
                    label="Lot Number"
                    name="tracking_type"
                    value="lot"
                    checked={expendableFormData.tracking_type === 'lot'}
                    onChange={handleExpendableFormChange}
                  />
                  <Form.Check
                    type="radio"
                    id="tracking-serial"
                    label="Serial Number"
                    name="tracking_type"
                    value="serial"
                    checked={expendableFormData.tracking_type === 'serial'}
                    onChange={handleExpendableFormChange}
                  />
                  <Form.Check
                    type="radio"
                    id="tracking-both"
                    label="Both"
                    name="tracking_type"
                    value="both"
                    checked={expendableFormData.tracking_type === 'both'}
                    onChange={handleExpendableFormChange}
                  />
                </div>
                <Form.Text className="text-muted">
                  Choose how to track this expendable item
                </Form.Text>
              </Form.Group>

              {(expendableFormData.tracking_type === 'lot' || expendableFormData.tracking_type === 'both') && (
                <LotNumberInput
                  value={expendableFormData.lot_number}
                  onChange={(value) => setExpendableFormData(prev => ({ ...prev, lot_number: value }))}
                  disabled={loading}
                  required={expendableFormData.tracking_type === 'lot' || expendableFormData.tracking_type === 'both'}
                  label="Lot Number"
                  helpText="Auto-generate or enter manually"
                  showAutoGenerate={true}
                />
              )}

              {(expendableFormData.tracking_type === 'serial' || expendableFormData.tracking_type === 'both') && (
                <Form.Group className="mb-3">
                  <Form.Label>
                    Serial Number
                    {(expendableFormData.tracking_type === 'serial' || expendableFormData.tracking_type === 'both') && <span className="text-danger ms-1">*</span>}
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="serial_number"
                    value={expendableFormData.serial_number}
                    onChange={handleExpendableFormChange}
                    required={expendableFormData.tracking_type === 'serial' || expendableFormData.tracking_type === 'both'}
                    placeholder="Enter serial number"
                  />
                  <Form.Control.Feedback type="invalid">
                    Serial number is required for this tracking type.
                  </Form.Control.Feedback>
                </Form.Group>
              )}

              <Row>
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Quantity *</Form.Label>
                    <Form.Control
                      type="number"
                      name="quantity"
                      value={expendableFormData.quantity}
                      onChange={handleExpendableFormChange}
                      min="0.01"
                      step="0.01"
                      required
                    />
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Min Stock</Form.Label>
                    <Form.Control
                      type="number"
                      name="minimum_stock_level"
                      value={expendableFormData.minimum_stock_level}
                      onChange={handleExpendableFormChange}
                      min="0"
                      step="0.01"
                    />
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Max Stock</Form.Label>
                    <Form.Control
                      type="number"
                      name="maximum_stock_level"
                      value={expendableFormData.maximum_stock_level}
                      onChange={handleExpendableFormChange}
                      min="0"
                      step="0.01"
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Form.Group className="mb-3">
                <Form.Label>Location (Optional)</Form.Label>
                <Form.Control
                  type="text"
                  name="location"
                  value={expendableFormData.location}
                  onChange={handleExpendableFormChange}
                  placeholder="e.g., Shelf A3"
                />
              </Form.Group>

              <div className="d-flex justify-content-end gap-2">
                <Button variant="secondary" onClick={handleClose} disabled={loading}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" disabled={loading || success}>
                  {loading ? 'Adding...' : success ? 'Added!' : 'Add Expendable'}
                </Button>
              </div>
            </Form>
          </Tab>
        </Tabs>
      </Modal.Body>
    </Modal>
  );
};

export default AddKitItemModal;

