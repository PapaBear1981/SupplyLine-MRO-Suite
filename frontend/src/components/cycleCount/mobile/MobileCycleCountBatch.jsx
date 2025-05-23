import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, Form, Alert, Badge, ListGroup, Modal, Spinner } from 'react-bootstrap';
import { fetchCycleCountItems, submitCountResult } from '../../../store/cycleCountSlice';

const MobileCycleCountBatch = ({ batchId, onItemCounted }) => {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector(state => state.cycleCount);

  const [selectedItem, setSelectedItem] = useState(null);
  const [showCountModal, setShowCountModal] = useState(false);
  const [showScanModal, setShowScanModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [countData, setCountData] = useState({
    actual_quantity: '',
    actual_location: '',
    condition: 'good',
    notes: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [scanInput, setScanInput] = useState('');
  const [submissionError, setSubmissionError] = useState('');
  const [scanError, setScanError] = useState('');

  useEffect(() => {
    if (batchId) {
      dispatch(fetchCycleCountItems({ batchId }));
    }
  }, [dispatch, batchId]);

  const filteredItems = items.filter(item => {
    const matchesSearch = !searchTerm ||
      item.item_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.location?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = filterStatus === 'all' || item.status === filterStatus;

    return matchesSearch && matchesStatus;
  });

  const handleItemSelect = (item) => {
    setSelectedItem(item);
    setCountData({
      actual_quantity: item.expected_quantity?.toString() || '',
      actual_location: item.expected_location || '',
      condition: 'good',
      notes: ''
    });
    setShowCountModal(true);
  };

  const handleCountSubmit = async () => {
    if (!selectedItem) return;

    setSubmitting(true);
    try {
      await dispatch(submitCountResult({
        itemId: selectedItem.id,
        resultData: {
          ...countData,
          actual_quantity: parseInt(countData.actual_quantity, 10)
        }
      })).unwrap();

      setShowCountModal(false);
      setSelectedItem(null);
      setCountData({
        actual_quantity: '',
        actual_location: '',
        condition: 'good',
        notes: ''
      });

      // Refresh items
      dispatch(fetchCycleCountItems({ batchId }));

      if (onItemCounted) {
        onItemCounted();
      }
    } catch (err) {
      console.error('Error submitting count:', err);
      // Consider adding user-visible error feedback
      setSubmissionError(err.message || 'Failed to submit count');
    } finally {
      setSubmitting(false);
    }
  };

  const handleScanBarcode = () => {
    setScanInput('');
    setScanError('');
    setShowScanModal(true);
  };

  const handleScanSubmit = () => {
    if (!scanInput.trim()) {
      setScanError('Please enter a barcode or item number');
      return;
    }

    const item = items.find(i =>
      i.item_number === scanInput.trim() ||
      i.barcode === scanInput.trim()
    );

    if (item) {
      setShowScanModal(false);
      handleItemSelect(item);
    } else {
      setScanError('Item not found in this batch');
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'pending': 'warning',
      'counted': 'success',
      'discrepancy': 'danger'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <Spinner animation="border" />
        <p className="mt-2">Loading items...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error</Alert.Heading>
        <p>{error}</p>
      </Alert>
    );
  }

  return (
    <div className="mobile-cycle-count">
      {/* Search and Filter Controls */}
      <Card className="mb-3">
        <Card.Body className="p-3">
          <Form.Group className="mb-2">
            <Form.Control
              type="text"
              placeholder="Search items..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size="sm"
            />
          </Form.Group>

          <div className="d-flex gap-2 mb-2">
            <Form.Select
              size="sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Items</option>
              <option value="pending">Pending</option>
              <option value="counted">Counted</option>
            </Form.Select>

            <Button
              variant="outline-primary"
              size="sm"
              onClick={handleScanBarcode}
              className="flex-shrink-0"
            >
              <i className="bi bi-upc-scan me-1"></i>
              Scan
            </Button>
          </div>

          <div className="text-muted small">
            {filteredItems.length} of {items.length} items
          </div>
        </Card.Body>
      </Card>

      {/* Items List */}
      <ListGroup>
        {filteredItems.map(item => (
          <ListGroup.Item
            key={item.id}
            className="d-flex justify-content-between align-items-start p-3"
            style={{ cursor: 'pointer' }}
            onClick={() => handleItemSelect(item)}
          >
            <div className="flex-grow-1">
              <div className="d-flex justify-content-between align-items-start mb-1">
                <h6 className="mb-1">{item.item_number}</h6>
                {getStatusBadge(item.status)}
              </div>
              <p className="mb-1 text-muted small">{item.description}</p>
              <div className="small text-muted">
                <div>Location: {item.expected_location}</div>
                <div>Expected Qty: {item.expected_quantity}</div>
              </div>
            </div>
            <i className="bi bi-chevron-right text-muted"></i>
          </ListGroup.Item>
        ))}
      </ListGroup>

      {filteredItems.length === 0 && (
        <Alert variant="info" className="text-center">
          <i className="bi bi-info-circle me-2"></i>
          No items found matching your criteria.
        </Alert>
      )}

      {/* Count Modal */}
      <Modal
        show={showCountModal}
        onHide={() => setShowCountModal(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Count Item</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedItem && (
            <div>
              <div className="mb-3">
                <h6>{selectedItem.item_number}</h6>
                <p className="text-muted">{selectedItem.description}</p>
              </div>

              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Actual Quantity <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    value={countData.actual_quantity}
                    onChange={(e) => setCountData({...countData, actual_quantity: e.target.value})}
                    min="0"
                    required
                  />
                  <Form.Text className="text-muted">
                    Expected: {selectedItem.expected_quantity}
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Actual Location</Form.Label>
                  <Form.Control
                    type="text"
                    value={countData.actual_location}
                    onChange={(e) => setCountData({...countData, actual_location: e.target.value})}
                  />
                  <Form.Text className="text-muted">
                    Expected: {selectedItem.expected_location}
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Condition</Form.Label>
                  <Form.Select
                    value={countData.condition}
                    onChange={(e) => setCountData({...countData, condition: e.target.value})}
                  >
                    <option value="good">Good</option>
                    <option value="fair">Fair</option>
                    <option value="poor">Poor</option>
                    <option value="damaged">Damaged</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Notes</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={countData.notes}
                    onChange={(e) => setCountData({...countData, notes: e.target.value})}
                    placeholder="Any additional notes..."
                  />
                </Form.Group>
              </Form>

              {submissionError && (
                <Alert variant="danger" className="mt-3">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {submissionError}
                </Alert>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={() => setShowCountModal(false)}
            disabled={submitting}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleCountSubmit}
            disabled={submitting || !countData.actual_quantity}
          >
            {submitting ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Submitting...
              </>
            ) : (
              'Submit Count'
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Scan Modal */}
      <Modal
        show={showScanModal}
        onHide={() => setShowScanModal(false)}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Scan Barcode</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Barcode or Item Number</Form.Label>
              <Form.Control
                type="text"
                value={scanInput}
                onChange={(e) => setScanInput(e.target.value)}
                placeholder="Enter barcode or item number..."
                autoFocus
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleScanSubmit();
                  }
                }}
              />
              <Form.Text className="text-muted">
                In production, this would integrate with a barcode scanner
              </Form.Text>
            </Form.Group>
            {scanError && (
              <Alert variant="danger" className="mb-0">
                <i className="bi bi-exclamation-triangle me-2"></i>
                {scanError}
              </Alert>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={() => setShowScanModal(false)}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleScanSubmit}
            disabled={!scanInput.trim()}
          >
            <i className="bi bi-search me-2"></i>
            Find Item
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default MobileCycleCountBatch;
