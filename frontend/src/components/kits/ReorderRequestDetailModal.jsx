import React, { useState } from 'react';
import { Modal, Button, Row, Col, Badge, Alert, Form, ButtonGroup } from 'react-bootstrap';
import { FaCheck, FaTimes, FaShoppingCart, FaImage, FaExclamationTriangle } from 'react-icons/fa';

const ReorderRequestDetailModal = ({
  show,
  onHide,
  request,
  onApprove,
  onMarkAsOrdered,
  onFulfill,
  onCancel,
  canApprove,
  canFulfill,
  loading,
  boxes = []
}) => {
  const [selectedBox, setSelectedBox] = useState(null);

  if (!request) return null;

  const getStatusBadge = (status) => {
    const variants = {
      pending: 'warning',
      approved: 'info',
      ordered: 'primary',
      fulfilled: 'success',
      cancelled: 'secondary'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status.toUpperCase()}</Badge>;
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

  const handleFulfill = () => {
    if (!selectedBox) {
      alert('Please select a box to place the item');
      return;
    }
    // Convert selectedBox to integer before sending
    onFulfill(request.id, parseInt(selectedBox, 10));
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  // Parse notes to extract structured information
  const parseNotes = (notes) => {
    if (!notes) return { reasonNeeded: '', referenceInfo: '', vendor: '', additionalNotes: '' };
    
    const reasonMatch = notes.match(/REASON NEEDED:\s*([^\n]*)/);
    const refMatch = notes.match(/REFERENCE INFO:\s*([^\n]*)/);
    const vendorMatch = notes.match(/VENDOR:\s*([^\n]*)/);
    const notesMatch = notes.match(/ADDITIONAL NOTES:\s*([^\n]*)/);

    return {
      reasonNeeded: reasonMatch ? reasonMatch[1].trim() : '',
      referenceInfo: refMatch ? refMatch[1].trim() : '',
      vendor: vendorMatch ? vendorMatch[1].trim() : '',
      additionalNotes: notesMatch ? notesMatch[1].trim() : notes
    };
  };

  const parsedNotes = parseNotes(request.notes);

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>
          <FaShoppingCart className="me-2" />
          Reorder Request Details
        </Modal.Title>
      </Modal.Header>
      
      <Modal.Body>
        {/* Status and Priority Row */}
        <Row className="mb-4">
          <Col md={6}>
            <div className="mb-2">
              <strong className="text-muted d-block mb-1">Status</strong>
              {getStatusBadge(request.status)}
            </div>
          </Col>
          <Col md={6}>
            <div className="mb-2">
              <strong className="text-muted d-block mb-1">Priority</strong>
              {getPriorityBadge(request.priority)}
            </div>
          </Col>
        </Row>

        {/* Item Information */}
        <Alert variant="light" className="border">
          <h6 className="mb-3">Item Information</h6>
          <Row>
            <Col md={6}>
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Part Number</strong>
                <code className="fs-6">{request.part_number}</code>
              </div>
            </Col>
            <Col md={6}>
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Item Type</strong>
                <Badge bg="secondary">{request.item_type?.toUpperCase() || 'N/A'}</Badge>
              </div>
            </Col>
          </Row>
          <Row className="mt-2">
            <Col md={12}>
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Description</strong>
                <div>{request.description}</div>
              </div>
            </Col>
          </Row>
          <Row className="mt-2">
            <Col md={6}>
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Quantity Requested</strong>
                <span className="fs-5 fw-bold text-primary">{request.quantity_requested}</span>
              </div>
            </Col>
            <Col md={6}>
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Request Type</strong>
                {request.is_automatic ? (
                  <Badge bg="info">Automatic</Badge>
                ) : (
                  <Badge bg="secondary">Manual</Badge>
                )}
              </div>
            </Col>
          </Row>
        </Alert>

        {/* Request Details */}
        <Alert variant="light" className="border">
          <h6 className="mb-3">Request Details</h6>
          <Row>
            <Col md={6}>
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Requested By</strong>
                <div>{request.requester_name || 'Unknown'}</div>
              </div>
            </Col>
            <Col md={6}>
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Request Date</strong>
                <div>{formatDate(request.requested_date)}</div>
              </div>
            </Col>
          </Row>
          {request.approved_by_name && (
            <Row className="mt-2">
              <Col md={6}>
                <div className="mb-2">
                  <strong className="text-muted d-block mb-1">Approved By</strong>
                  <div>{request.approved_by_name}</div>
                </div>
              </Col>
              <Col md={6}>
                <div className="mb-2">
                  <strong className="text-muted d-block mb-1">Approval Date</strong>
                  <div>{formatDate(request.approved_date)}</div>
                </div>
              </Col>
            </Row>
          )}
          {request.fulfillment_date && (
            <Row className="mt-2">
              <Col md={12}>
                <div className="mb-2">
                  <strong className="text-muted d-block mb-1">Fulfillment Date</strong>
                  <div>{formatDate(request.fulfillment_date)}</div>
                </div>
              </Col>
            </Row>
          )}
        </Alert>

        {/* Additional Information (for new item requests) */}
        {(parsedNotes.reasonNeeded || parsedNotes.referenceInfo || parsedNotes.vendor) && (
          <Alert variant="light" className="border">
            <h6 className="mb-3">Additional Information</h6>
            {parsedNotes.reasonNeeded && parsedNotes.reasonNeeded !== 'N/A' && (
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Reason Needed</strong>
                <div>{parsedNotes.reasonNeeded}</div>
              </div>
            )}
            {parsedNotes.referenceInfo && parsedNotes.referenceInfo !== 'N/A' && (
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Reference Information</strong>
                <div>{parsedNotes.referenceInfo}</div>
              </div>
            )}
            {parsedNotes.vendor && parsedNotes.vendor !== 'Unknown' && (
              <div className="mb-2">
                <strong className="text-muted d-block mb-1">Vendor</strong>
                <div>{parsedNotes.vendor}</div>
              </div>
            )}
          </Alert>
        )}

        {/* Notes */}
        {parsedNotes.additionalNotes && parsedNotes.additionalNotes !== 'None' && (
          <Alert variant="light" className="border">
            <h6 className="mb-2">Notes</h6>
            <div className="text-muted">{parsedNotes.additionalNotes}</div>
          </Alert>
        )}

        {/* Image */}
        {request.image_path && (
          <Alert variant="light" className="border">
            <h6 className="mb-2">
              <FaImage className="me-2" />
              Attached Image
            </h6>
            <img 
              src={request.image_path} 
              alt="Request attachment" 
              className="img-fluid rounded border"
              style={{ maxHeight: '300px' }}
            />
          </Alert>
        )}

        {/* Box Selection for Fulfill Action */}
        {request.status === 'ordered' && canFulfill && (
          <Alert variant="info" className="border">
            <h6 className="mb-3">
              <FaExclamationTriangle className="me-2" />
              Fulfillment Required
            </h6>
            <Form.Group>
              <Form.Label>Select Box to Place Item</Form.Label>
              <Form.Select
                value={selectedBox || ''}
                onChange={(e) => setSelectedBox(e.target.value)}
                required
              >
                <option value="">-- Select a Box --</option>
                {boxes.map((box) => (
                  <option key={box.id} value={box.id}>
                    Box {box.box_number} - {box.box_type} {box.description ? `(${box.description})` : ''}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Alert>
        )}
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        
        {/* Action Buttons Based on Status */}
        <ButtonGroup>
          {request.status === 'pending' && canApprove && (
            <>
              <Button
                variant="success"
                onClick={() => onApprove(request.id)}
                disabled={loading}
              >
                <FaCheck className="me-1" />
                {loading ? 'Processing...' : 'Approve'}
              </Button>
              <Button
                variant="danger"
                onClick={() => onCancel(request.id)}
                disabled={loading}
              >
                <FaTimes className="me-1" />
                Cancel Request
              </Button>
            </>
          )}

          {request.status === 'approved' && canFulfill && (
            <>
              <Button
                variant="info"
                onClick={() => onMarkAsOrdered(request.id)}
                disabled={loading}
              >
                <FaShoppingCart className="me-1" />
                {loading ? 'Processing...' : 'Mark as Ordered'}
              </Button>
              <Button
                variant="danger"
                onClick={() => onCancel(request.id)}
                disabled={loading}
              >
                <FaTimes className="me-1" />
                Cancel Request
              </Button>
            </>
          )}

          {request.status === 'ordered' && canFulfill && (
            <>
              <Button
                variant="primary"
                onClick={handleFulfill}
                disabled={!selectedBox || loading}
              >
                <FaCheck className="me-1" />
                {loading ? 'Processing...' : 'Fulfill Order'}
              </Button>
              <Button
                variant="danger"
                onClick={() => onCancel(request.id)}
                disabled={loading}
              >
                <FaTimes className="me-1" />
                Cancel Request
              </Button>
            </>
          )}
        </ButtonGroup>
      </Modal.Footer>
    </Modal>
  );
};

export default ReorderRequestDetailModal;

