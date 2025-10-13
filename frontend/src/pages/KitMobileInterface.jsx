import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Container, Card, Button, Form, ListGroup, Badge, Alert, Modal, InputGroup } from 'react-bootstrap';
import { FaSearch, FaBarcode, FaBoxOpen, FaRedo, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import { fetchKits, fetchKitItems, issueFromKit, createReorderRequest } from '../store/kitsSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';

const KitMobileInterface = () => {
  const dispatch = useDispatch();
  const { kits, kitItems, loading, error } = useSelector((state) => state.kits);
  const { user } = useSelector((state) => state.auth);

  // State
  const [selectedKit, setSelectedKit] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [view, setView] = useState('kits'); // 'kits', 'items', 'issue', 'reorder'
  const [selectedItem, setSelectedItem] = useState(null);
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [showReorderModal, setShowReorderModal] = useState(false);
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Issue form state
  const [issueQuantity, setIssueQuantity] = useState(1);
  const [issuePurpose, setIssuePurpose] = useState('');
  const [issueWorkOrder, setIssueWorkOrder] = useState('');

  // Reorder form state
  const [reorderQuantity, setReorderQuantity] = useState(1);
  const [reorderPriority, setReorderPriority] = useState('medium');
  const [reorderNotes, setReorderNotes] = useState('');

  useEffect(() => {
    dispatch(fetchKits());
  }, [dispatch]);

  useEffect(() => {
    if (selectedKit) {
      dispatch(fetchKitItems(selectedKit.id));
    }
  }, [selectedKit, dispatch]);

  // Filter kits
  const filteredKits = kits.filter(kit => 
    kit.status === 'active' && 
    (kit.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
     kit.aircraft_type_name?.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Filter items
  const items = kitItems[selectedKit?.id] || [];
  const filteredItems = items.filter(item =>
    item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.part_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Handle kit selection
  const handleSelectKit = (kit) => {
    setSelectedKit(kit);
    setView('items');
    setSearchTerm('');
  };

  // Handle item selection for issue
  const handleIssueItem = (item) => {
    setSelectedItem(item);
    setIssueQuantity(1);
    setIssuePurpose('');
    setIssueWorkOrder('');
    setShowIssueModal(true);
  };

  // Handle item selection for reorder
  const handleReorderItem = (item) => {
    setSelectedItem(item);
    setReorderQuantity(1);
    setReorderPriority('medium');
    setReorderNotes('');
    setShowReorderModal(true);
  };

  // Submit issue
  const handleSubmitIssue = async () => {
    try {
      await dispatch(issueFromKit({
        kitId: selectedKit.id,
        itemId: selectedItem.id,
        itemType: selectedItem.item_type,
        quantity: issueQuantity,
        purpose: issuePurpose,
        workOrder: issueWorkOrder
      })).unwrap();

      setShowIssueModal(false);
      setSuccessMessage(`Successfully issued ${issueQuantity} ${selectedItem.description}`);
      setShowSuccessAlert(true);
      setTimeout(() => setShowSuccessAlert(false), 3000);

      // Refresh items
      dispatch(fetchKitItems(selectedKit.id));
    } catch (err) {
      console.error('Failed to issue item:', err);
    }
  };

  // Submit reorder
  const handleSubmitReorder = async () => {
    try {
      await dispatch(createReorderRequest({
        kitId: selectedKit.id,
        itemType: selectedItem.item_type,
        itemId: selectedItem.id,
        partNumber: selectedItem.part_number,
        description: selectedItem.description,
        quantityRequested: reorderQuantity,
        priority: reorderPriority,
        notes: reorderNotes
      })).unwrap();

      setShowReorderModal(false);
      setSuccessMessage(`Reorder request submitted for ${selectedItem.description}`);
      setShowSuccessAlert(true);
      setTimeout(() => setShowSuccessAlert(false), 3000);
    } catch (err) {
      console.error('Failed to create reorder:', err);
    }
  };

  // Back button handler
  const handleBack = () => {
    if (view === 'items') {
      setView('kits');
      setSelectedKit(null);
      setSearchTerm('');
    }
  };

  if (loading && kits.length === 0) {
    return (
      <Container className="py-4">
        <LoadingSpinner />
      </Container>
    );
  }

  return (
    <Container fluid className="p-3" style={{ maxWidth: '600px' }}>
      {/* Header */}
      <div className="mb-3">
        <h3 className="mb-2">
          <FaBoxOpen className="me-2" />
          Mobile Kits
        </h3>
        {selectedKit && (
          <Button 
            variant="outline-secondary" 
            size="sm" 
            onClick={handleBack}
            className="mb-2"
          >
            ← Back to Kits
          </Button>
        )}
      </div>

      {/* Success Alert */}
      {showSuccessAlert && (
        <Alert variant="success" className="mb-3">
          <FaCheckCircle className="me-2" />
          {successMessage}
        </Alert>
      )}

      {/* Search Bar */}
      <InputGroup className="mb-3" size="lg">
        <InputGroup.Text>
          <FaSearch />
        </InputGroup.Text>
        <Form.Control
          type="text"
          placeholder={view === 'kits' ? 'Search kits...' : 'Search items...'}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ fontSize: '1.1rem' }}
        />
        <Button variant="outline-secondary">
          <FaBarcode size={20} />
        </Button>
      </InputGroup>

      {/* Kits View */}
      {view === 'kits' && (
        <div>
          {filteredKits.length === 0 ? (
            <Alert variant="info">
              No active kits found. {searchTerm && 'Try a different search term.'}
            </Alert>
          ) : (
            <ListGroup>
              {filteredKits.map((kit) => (
                <ListGroup.Item
                  key={kit.id}
                  action
                  onClick={() => handleSelectKit(kit)}
                  className="py-3"
                  style={{ cursor: 'pointer' }}
                >
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="flex-grow-1">
                      <h5 className="mb-1">{kit.name}</h5>
                      <div className="text-muted">
                        {kit.aircraft_type_name || 'Unknown Aircraft'}
                      </div>
                      <div className="mt-2">
                        <Badge bg="info" className="me-2">
                          {kit.item_count || 0} Items
                        </Badge>
                        {kit.alert_count > 0 && (
                          <Badge bg="warning">
                            <FaExclamationTriangle className="me-1" />
                            {kit.alert_count} Alerts
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="text-end">
                      <Badge bg="success">Active</Badge>
                    </div>
                  </div>
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}
        </div>
      )}

      {/* Items View */}
      {view === 'items' && selectedKit && (
        <div>
          <Card className="mb-3">
            <Card.Header>
              <strong>{selectedKit.name}</strong>
              <div className="text-muted small">{selectedKit.aircraft_type_name}</div>
            </Card.Header>
          </Card>

          {filteredItems.length === 0 ? (
            <Alert variant="info">
              No items found. {searchTerm && 'Try a different search term.'}
            </Alert>
          ) : (
            <ListGroup>
              {filteredItems.map((item) => (
                <ListGroup.Item key={item.id} className="py-3">
                  <div className="mb-2">
                    <strong>{item.description || 'Unknown Item'}</strong>
                    {item.part_number && (
                      <div className="text-muted small">
                        Part: <code>{item.part_number}</code>
                      </div>
                    )}
                  </div>
                  <div className="mb-2">
                    <Badge bg={item.quantity > 0 ? 'success' : 'danger'} className="me-2">
                      Qty: {item.quantity || 0}
                    </Badge>
                    <Badge bg="secondary">{item.item_type}</Badge>
                  </div>
                  <div className="d-grid gap-2">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={() => handleIssueItem(item)}
                      disabled={!item.quantity || item.quantity === 0}
                    >
                      <FaBoxOpen className="me-2" />
                      Issue Item
                    </Button>
                    <Button
                      variant="warning"
                      size="lg"
                      onClick={() => handleReorderItem(item)}
                    >
                      <FaRedo className="me-2" />
                      Request Reorder
                    </Button>
                  </div>
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}
        </div>
      )}

      {/* Issue Modal */}
      <Modal show={showIssueModal} onHide={() => setShowIssueModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Issue Item</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedItem && (
            <>
              <div className="mb-3">
                <strong>{selectedItem.description}</strong>
                <div className="text-muted small">Part: {selectedItem.part_number}</div>
                <div className="text-muted small">Available: {selectedItem.quantity}</div>
              </div>

              <Form.Group className="mb-3">
                <Form.Label>Quantity *</Form.Label>
                <Form.Control
                  type="number"
                  min="1"
                  max={selectedItem.quantity}
                  value={issueQuantity}
                  onChange={(e) => setIssueQuantity(parseInt(e.target.value))}
                  size="lg"
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Purpose *</Form.Label>
                <Form.Control
                  type="text"
                  value={issuePurpose}
                  onChange={(e) => setIssuePurpose(e.target.value)}
                  placeholder="e.g., Maintenance, Repair"
                  size="lg"
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Work Order</Form.Label>
                <Form.Control
                  type="text"
                  value={issueWorkOrder}
                  onChange={(e) => setIssueWorkOrder(e.target.value)}
                  placeholder="Optional"
                  size="lg"
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowIssueModal(false)} size="lg">
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmitIssue}
            disabled={!issueQuantity || !issuePurpose}
            size="lg"
          >
            Issue Item
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Reorder Modal */}
      <Modal show={showReorderModal} onHide={() => setShowReorderModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Request Reorder</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedItem && (
            <>
              <div className="mb-3">
                <strong>{selectedItem.description}</strong>
                <div className="text-muted small">Part: {selectedItem.part_number}</div>
                <div className="text-muted small">Current Qty: {selectedItem.quantity}</div>
              </div>

              <Form.Group className="mb-3">
                <Form.Label>Quantity Needed *</Form.Label>
                <Form.Control
                  type="number"
                  min="1"
                  value={reorderQuantity}
                  onChange={(e) => setReorderQuantity(parseInt(e.target.value))}
                  size="lg"
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Priority *</Form.Label>
                <Form.Select
                  value={reorderPriority}
                  onChange={(e) => setReorderPriority(e.target.value)}
                  size="lg"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Notes</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={reorderNotes}
                  onChange={(e) => setReorderNotes(e.target.value)}
                  placeholder="Optional notes..."
                  size="lg"
                />
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowReorderModal(false)} size="lg">
            Cancel
          </Button>
          <Button
            variant="warning"
            onClick={handleSubmitReorder}
            disabled={!reorderQuantity}
            size="lg"
          >
            Submit Request
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default KitMobileInterface;

