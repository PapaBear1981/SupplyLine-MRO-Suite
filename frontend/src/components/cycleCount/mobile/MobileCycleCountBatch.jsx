import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, Form, Alert, Badge, ListGroup, Modal, Spinner } from 'react-bootstrap';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { fetchCycleCountItems, submitCountResult } from '../../../store/cycleCountSlice';

const MobileCycleCountBatch = ({ batchId, onItemCounted }) => {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector(state => ({
    items: state.cycleCount.items.byBatchId[batchId] || [],
    loading: state.cycleCount.items.loadingByBatchId[batchId] || false,
    error: state.cycleCount.items.errorByBatchId[batchId] || null
  }));

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
  const [isScanning, setIsScanning] = useState(false);
  const [scannerInitialized, setScannerInitialized] = useState(false);
  const scannerRef = useRef(null);
  const html5QrcodeScannerRef = useRef(null);

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
    setIsScanning(false);
    setScannerInitialized(false);
    setShowScanModal(true);
  };

  const initializeScanner = () => {
    if (html5QrcodeScannerRef.current) {
      html5QrcodeScannerRef.current.clear();
    }

    const config = {
      fps: 10,
      qrbox: { width: 250, height: 250 },
      aspectRatio: 1.0,
      supportedScanTypes: [
        Html5QrcodeScanner.SCAN_TYPE_CAMERA,
        Html5QrcodeScanner.SCAN_TYPE_FILE
      ]
    };

    html5QrcodeScannerRef.current = new Html5QrcodeScanner(
      "qr-reader",
      config,
      false
    );

    html5QrcodeScannerRef.current.render(
      (decodedText) => {
        // Success callback
        handleScanSuccess(decodedText);
      },
      (error) => {
        // Error callback - we can ignore most errors as they're just "no QR code found"
        if (error.includes('NotFoundException')) {
          // This is normal when no code is detected
          return;
        }
        console.warn('QR Code scan error:', error);
      }
    );

    setScannerInitialized(true);
  };

  const handleScanSuccess = (decodedText) => {
    const item = items.find(i =>
      i.item_number === decodedText.trim() ||
      i.barcode === decodedText.trim() ||
      i.id.toString() === decodedText.trim()
    );

    if (item) {
      // Stop scanner and close modal
      if (html5QrcodeScannerRef.current) {
        html5QrcodeScannerRef.current.clear();
      }
      setShowScanModal(false);
      handleItemSelect(item);
    } else {
      setScanError(`Item not found: ${decodedText}`);
    }
  };

  const handleScanSubmit = () => {
    if (!scanInput.trim()) {
      setScanError('Please enter a barcode or item number');
      return;
    }

    handleScanSuccess(scanInput.trim());
  };

  const startCameraScanning = () => {
    setIsScanning(true);
    setScanError('');
    setTimeout(() => {
      initializeScanner();
    }, 100);
  };

  const stopScanning = () => {
    if (html5QrcodeScannerRef.current) {
      html5QrcodeScannerRef.current.clear();
    }
    setIsScanning(false);
    setScannerInitialized(false);
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
        onHide={() => {
          stopScanning();
          setShowScanModal(false);
        }}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Scan Barcode</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {!isScanning ? (
            <div>
              <div className="d-grid gap-2 mb-3">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={startCameraScanning}
                >
                  <i className="bi bi-camera me-2"></i>
                  Use Camera Scanner
                </Button>
              </div>

              <div className="text-center mb-3">
                <span className="text-muted">or</span>
              </div>

              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Manual Entry</Form.Label>
                  <Form.Control
                    type="text"
                    value={scanInput}
                    onChange={(e) => setScanInput(e.target.value)}
                    placeholder="Enter barcode or item number..."
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleScanSubmit();
                      }
                    }}
                  />
                </Form.Group>
              </Form>
            </div>
          ) : (
            <div>
              <div className="text-center mb-3">
                <h6>Position barcode in the scanner area</h6>
                <p className="text-muted">The scanner will automatically detect and process barcodes</p>
              </div>

              <div id="qr-reader" ref={scannerRef} style={{ width: '100%' }}></div>

              <div className="text-center mt-3">
                <Button
                  variant="outline-secondary"
                  onClick={stopScanning}
                >
                  <i className="bi bi-stop-circle me-2"></i>
                  Stop Scanner
                </Button>
              </div>
            </div>
          )}

          {scanError && (
            <Alert variant="danger" className="mt-3">
              <i className="bi bi-exclamation-triangle me-2"></i>
              {scanError}
            </Alert>
          )}
        </Modal.Body>
        {!isScanning && (
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
        )}
      </Modal>
    </div>
  );
};

export default MobileCycleCountBatch;
