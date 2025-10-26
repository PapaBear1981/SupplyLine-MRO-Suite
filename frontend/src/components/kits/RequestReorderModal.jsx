import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal, Form, Button, Alert, Table, Badge, Tabs, Tab } from 'react-bootstrap';
import { FaShoppingCart, FaExclamationTriangle, FaPlus, FaImage } from 'react-icons/fa';
import { createReorderRequest, fetchKitItems } from '../../store/kitsSlice';

const RequestReorderModal = ({ show, onHide, kitId, onSuccess }) => {
  const dispatch = useDispatch();
  const { kitItems, loading } = useSelector((state) => state.kits);

  // Tab state
  const [activeTab, setActiveTab] = useState('existing');

  // Existing item reorder state
  const [selectedItem, setSelectedItem] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [priority, setPriority] = useState('medium');
  const [notes, setNotes] = useState('');
  const [validated, setValidated] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // New item request state
  const [newItemType, setNewItemType] = useState('tool');
  const [newPartNumber, setNewPartNumber] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newQuantity, setNewQuantity] = useState(1);
  const [newPriority, setNewPriority] = useState('medium');
  const [newReasonNeeded, setNewReasonNeeded] = useState('');
  const [newReferenceInfo, setNewReferenceInfo] = useState('');
  const [newVendor, setNewVendor] = useState('');
  const [newImage, setNewImage] = useState(null);
  const [newImagePreview, setNewImagePreview] = useState(null);
  const [newNotes, setNewNotes] = useState('');

  // Get items for this specific kit
  const items = kitItems[kitId] || { items: [], expendables: [], total_count: 0 };
  const allItems = [
    ...items.items.map(item => ({ ...item, source: 'item' })),
    ...items.expendables.map(exp => ({ ...exp, source: 'expendable' }))
  ];

  useEffect(() => {
    if (show && kitId) {
      // Fetch kit items when modal opens
      dispatch(fetchKitItems({ kitId }));
    }
  }, [show, kitId, dispatch]);

  useEffect(() => {
    // Reset form when modal closes
    if (!show) {
      setActiveTab('existing');
      setSelectedItem(null);
      setQuantity(1);
      setPriority('medium');
      setNotes('');
      setValidated(false);
      setSubmitError(null);
      setSubmitSuccess(false);
      // Reset new item form
      setNewItemType('tool');
      setNewPartNumber('');
      setNewDescription('');
      setNewQuantity(1);
      setNewPriority('medium');
      setNewReasonNeeded('');
      setNewReferenceInfo('');
      setNewVendor('');
      setNewImage(null);
      setNewImagePreview(null);
      setNewNotes('');
    }
  }, [show]);

  const handleItemSelect = (item) => {
    setSelectedItem(item);
    setSubmitError(null);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setNewImage(file);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setNewImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (activeTab === 'existing') {
      // Existing item reorder validation
      if (form.checkValidity() === false || !selectedItem) {
        e.stopPropagation();
        setValidated(true);
        if (!selectedItem) {
          setSubmitError('Please select an item to reorder');
        }
        return;
      }

      setValidated(true);
      setSubmitError(null);

      try {
        await dispatch(createReorderRequest({
          kitId,
          item_type: selectedItem.item_type,
          item_id: selectedItem.id,
          part_number: selectedItem.part_number,
          description: selectedItem.description,
          quantity_requested: quantity,
          priority,
          notes
        })).unwrap();

        setSubmitSuccess(true);

        // Call onSuccess callback if provided
        if (onSuccess) {
          onSuccess();
        }

        // Close modal after short delay to show success message
        setTimeout(() => {
          onHide();
        }, 1500);
      } catch (err) {
        console.error('Failed to create reorder request:', err);
        setSubmitError(err.message || 'Failed to create reorder request');
      }
    } else {
      // New item request validation
      if (form.checkValidity() === false) {
        e.stopPropagation();
        setValidated(true);
        return;
      }

      setValidated(true);
      setSubmitError(null);

      try {
        // For new items with images, we need to use FormData
        const requestData = {
          kitId,
          item_type: newItemType,
          part_number: newPartNumber,
          description: newDescription,
          quantity_requested: newQuantity,
          priority: newPriority,
          notes: `REASON NEEDED: ${newReasonNeeded}\n\nREFERENCE INFO: ${newReferenceInfo || 'N/A'}\n\nVENDOR: ${newVendor || 'Unknown'}\n\nADDITIONAL NOTES: ${newNotes || 'None'}`,
          is_new_item: true
        };

        // If there's an image, add it to the request
        if (newImage) {
          requestData.image = newImage;
        }

        await dispatch(createReorderRequest(requestData)).unwrap();

        setSubmitSuccess(true);

        // Call onSuccess callback if provided
        if (onSuccess) {
          onSuccess();
        }

        // Close modal after short delay to show success message
        setTimeout(() => {
          onHide();
        }, 1500);
      } catch (err) {
        console.error('Failed to create new item request:', err);
        setSubmitError(err.message || 'Failed to create new item request');
      }
    }
  };

  const getPriorityBadge = (priority) => {
    const variants = {
      low: 'secondary',
      medium: 'info',
      high: 'warning',
      urgent: 'danger'
    };
    return <Badge bg={variants[priority] || 'secondary'}>{priority.toUpperCase()}</Badge>;
  };

  const getItemTypeBadge = (type) => {
    const variants = {
      tool: 'primary',
      chemical: 'success',
      expendable: 'warning'
    };
    return <Badge bg={variants[type] || 'secondary'}>{type}</Badge>;
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          <FaShoppingCart className="me-2" />
          Request Reorder
        </Modal.Title>
      </Modal.Header>

      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          {submitError && <Alert variant="danger">{submitError}</Alert>}
          {submitSuccess && (
            <Alert variant="success">
              Reorder request submitted successfully!
            </Alert>
          )}

          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-3"
          >
            {/* Existing Item Tab */}
            <Tab eventKey="existing" title={<><FaShoppingCart className="me-2" />Reorder Existing Item</>}>
              {/* Step 1: Select Item */}
              <div className="mb-4">
            <h6 className="mb-3">Step 1: Select Item to Reorder</h6>
            {loading ? (
              <div className="text-center py-3">
                <div className="spinner-border spinner-border-sm me-2" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                Loading items...
              </div>
            ) : allItems.length > 0 ? (
              <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <Table hover size="sm">
                  <thead className="sticky-top bg-white">
                    <tr>
                      <th>Select</th>
                      <th>Part Number</th>
                      <th>Description</th>
                      <th>Type</th>
                      <th>Current Qty</th>
                      <th>Box</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allItems.map((item, index) => (
                      <tr
                        key={`${item.source}-${item.id}-${index}`}
                        onClick={() => handleItemSelect(item)}
                        style={{ cursor: 'pointer' }}
                        className={selectedItem?.id === item.id && selectedItem?.source === item.source ? 'table-active' : ''}
                      >
                        <td>
                          <Form.Check
                            type="radio"
                            name="selectedItem"
                            checked={selectedItem?.id === item.id}
                            onChange={() => handleItemSelect(item)}
                          />
                        </td>
                        <td>
                          <code>{item.part_number || 'N/A'}</code>
                        </td>
                        <td>{item.description || 'Unknown'}</td>
                        <td>{getItemTypeBadge(item.item_type)}</td>
                        <td>
                          <Badge bg={item.quantity > 0 ? 'success' : 'danger'}>
                            {item.quantity || 0}
                          </Badge>
                        </td>
                        <td className="text-muted small">{item.box_name || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            ) : (
              <Alert variant="info">
                No items found in this kit. Add items before requesting reorders.
              </Alert>
            )}
          </div>

          {/* Step 2: Reorder Details */}
          {selectedItem && (
            <div className="border-top pt-4">
              <h6 className="mb-3">Step 2: Reorder Details</h6>
              
              <Alert variant="light" className="mb-3">
                <strong>Selected Item:</strong> {selectedItem.description}
                <br />
                <small className="text-muted">
                  Part: <code>{selectedItem.part_number}</code> | 
                  Current Qty: <Badge bg={selectedItem.quantity > 0 ? 'success' : 'danger'} className="ms-1">
                    {selectedItem.quantity || 0}
                  </Badge>
                </small>
              </Alert>

              <Form.Group className="mb-3">
                <Form.Label>Quantity Needed *</Form.Label>
                <Form.Control
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                  required
                  placeholder="Enter quantity needed"
                />
                <Form.Control.Feedback type="invalid">
                  Quantity is required and must be at least 1
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Priority *</Form.Label>
                <Form.Select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  required
                >
                  <option value="low">Low - Can wait for regular ordering cycle</option>
                  <option value="medium">Medium - Needed within 2 weeks</option>
                  <option value="high">High - Needed within 1 week</option>
                  <option value="urgent">Urgent - Needed ASAP (AOG situation)</option>
                </Form.Select>
                <Form.Text className="text-muted">
                  {getPriorityBadge(priority)} selected
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Notes (Optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any additional information about this reorder request..."
                />
                <Form.Text className="text-muted">
                  Include justification for urgent requests or any special requirements
                </Form.Text>
              </Form.Group>

              {priority === 'urgent' && (
                <Alert variant="warning">
                  <FaExclamationTriangle className="me-2" />
                  <strong>Urgent Priority:</strong> Please provide justification in the notes field.
                  Urgent requests require immediate approval from Materials department.
                </Alert>
              )}
            </div>
          )}
            </Tab>

            {/* New Item Tab */}
            <Tab eventKey="new" title={<><FaPlus className="me-2" />Request New Item</>}>
              <Alert variant="info" className="mb-3">
                <strong>Request a new item</strong> that doesn't exist in the system yet.
                This will be reviewed by the Materials department before being added to inventory.
              </Alert>

              <Form.Group className="mb-3">
                <Form.Label>Item Type *</Form.Label>
                <Form.Select
                  value={newItemType}
                  onChange={(e) => setNewItemType(e.target.value)}
                  required
                >
                  <option value="tool">Tool</option>
                  <option value="chemical">Chemical</option>
                  <option value="expendable">Expendable/Part</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Part/Tool Number *</Form.Label>
                <Form.Control
                  type="text"
                  value={newPartNumber}
                  onChange={(e) => setNewPartNumber(e.target.value)}
                  required
                  placeholder="Enter part or tool number"
                />
                <Form.Control.Feedback type="invalid">
                  Part/Tool number is required
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Description *</Form.Label>
                <Form.Control
                  type="text"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  required
                  placeholder="Enter item description"
                />
                <Form.Control.Feedback type="invalid">
                  Description is required
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Quantity Needed *</Form.Label>
                <Form.Control
                  type="number"
                  min="1"
                  value={newQuantity}
                  onChange={(e) => setNewQuantity(parseInt(e.target.value) || 1)}
                  required
                  placeholder="Enter quantity needed"
                />
                <Form.Control.Feedback type="invalid">
                  Quantity is required and must be at least 1
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Reason Needed *</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={newReasonNeeded}
                  onChange={(e) => setNewReasonNeeded(e.target.value)}
                  required
                  placeholder="Explain why this item is needed..."
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a reason for this request
                </Form.Control.Feedback>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Reference Information (Optional but Encouraged)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={newReferenceInfo}
                  onChange={(e) => setNewReferenceInfo(e.target.value)}
                  placeholder="Add reference numbers, specifications, or other relevant information..."
                />
                <Form.Text className="text-muted">
                  Include manufacturer specs, reference manuals, or other documentation
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Vendor (If Known)</Form.Label>
                <Form.Control
                  type="text"
                  value={newVendor}
                  onChange={(e) => setNewVendor(e.target.value)}
                  placeholder="Enter vendor name if known"
                />
                <Form.Text className="text-muted">
                  Helps expedite ordering if you know where to source this item
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Priority *</Form.Label>
                <Form.Select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  required
                >
                  <option value="low">Low - Can wait for regular ordering cycle</option>
                  <option value="medium">Medium - Needed within 2 weeks</option>
                  <option value="high">High - Needed within 1 week</option>
                  <option value="urgent">Urgent - Needed ASAP (AOG situation)</option>
                </Form.Select>
                <Form.Text className="text-muted">
                  {getPriorityBadge(newPriority)} selected
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>
                  <FaImage className="me-2" />
                  Picture of Item (If Available)
                </Form.Label>
                <Form.Control
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                />
                <Form.Text className="text-muted">
                  Upload a photo to help identify the item (optional)
                </Form.Text>
                {newImagePreview && (
                  <div className="mt-2">
                    <img
                      src={newImagePreview}
                      alt="Preview"
                      style={{ maxWidth: '200px', maxHeight: '200px', borderRadius: '4px' }}
                    />
                  </div>
                )}
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Additional Notes</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  placeholder="Add any additional information..."
                />
                <Form.Text className="text-muted">
                  Include any other details that might be helpful
                </Form.Text>
              </Form.Group>

              {newPriority === 'urgent' && (
                <Alert variant="warning">
                  <FaExclamationTriangle className="me-2" />
                  <strong>Urgent Priority:</strong> Please provide detailed justification in the reason needed field.
                  Urgent requests for new items require immediate approval from Materials department.
                </Alert>
              )}
            </Tab>
          </Tabs>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={onHide} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="warning"
            disabled={loading || (activeTab === 'existing' && !selectedItem) || submitSuccess}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Submitting...
              </>
            ) : submitSuccess ? (
              'Request Submitted!'
            ) : activeTab === 'existing' ? (
              'Submit Reorder Request'
            ) : (
              'Submit New Item Request'
            )}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default RequestReorderModal;

