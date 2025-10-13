import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Table, Badge, Button, ButtonGroup, Form, Row, Col, Modal, Alert } from 'react-bootstrap';
import { FaShoppingCart, FaCheck, FaTimes, FaExclamationCircle, FaFilter } from 'react-icons/fa';
import {
  fetchReorderRequests,
  approveReorderRequest,
  markReorderAsOrdered,
  fulfillReorderRequest,
  cancelReorderRequest,
  fetchKitItems,
  fetchKitById
} from '../../store/kitsSlice';
import api from '../../services/api';

const KitReorderManagement = ({ kitId = null }) => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { loading, error, reorderRequests: allReorderRequests } = useSelector((state) => state.kits);

  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [confirmAction, setConfirmAction] = useState('');
  const [showBoxSelectionModal, setShowBoxSelectionModal] = useState(false);
  const [selectedBox, setSelectedBox] = useState(null);
  const [boxes, setBoxes] = useState([]);

  // Filter reorder requests based on filters
  const reorderRequests = allReorderRequests || [];

  useEffect(() => {
    loadReorderRequests();
    loadBoxes();
  }, [kitId, filterStatus, filterPriority, dispatch]);

  const loadBoxes = async () => {
    try {
      const response = await api.get(`/kits/${kitId}/boxes`);
      setBoxes(response.data);
    } catch (error) {
      console.error('Failed to load boxes:', error);
    }
  };

  const loadReorderRequests = () => {
    const filters = {};
    if (filterStatus) filters.status = filterStatus;
    if (filterPriority) filters.priority = filterPriority;

    dispatch(fetchReorderRequests({ kitId, filters }));
  };

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

  const handleAction = (request, action) => {
    setSelectedRequest(request);
    setConfirmAction(action);

    // For fulfill action, show box selection modal instead
    if (action === 'fulfill') {
      setShowBoxSelectionModal(true);
    } else {
      setShowConfirmModal(true);
    }
  };

  const confirmActionHandler = () => {
    const requestId = selectedRequest.id;

    switch (confirmAction) {
      case 'approve':
        dispatch(approveReorderRequest(requestId))
          .unwrap()
          .then(() => {
            loadReorderRequests();
            setShowConfirmModal(false);
          })
          .catch((err) => {
            console.error('Failed to approve reorder request:', err);
          });
        break;
      case 'order':
        dispatch(markReorderAsOrdered(requestId))
          .unwrap()
          .then(() => {
            loadReorderRequests();
            setShowConfirmModal(false);
          })
          .catch((err) => {
            console.error('Failed to mark reorder as ordered:', err);
          });
        break;
      case 'cancel':
        dispatch(cancelReorderRequest(requestId))
          .unwrap()
          .then(() => {
            loadReorderRequests();
            setShowConfirmModal(false);
          })
          .catch((err) => {
            console.error('Failed to cancel reorder request:', err);
          });
        break;
      default:
        break;
    }
  };

  const handleFulfillWithBox = () => {
    if (!selectedBox) {
      alert('Please select a box');
      return;
    }

    dispatch(fulfillReorderRequest({
      requestId: selectedRequest.id,
      boxId: selectedBox
    }))
      .unwrap()
      .then(() => {
        loadReorderRequests();
        // Refresh kit items to show updated inventory
        dispatch(fetchKitItems({ kitId }));
        // Refresh kit overview to update item count
        dispatch(fetchKitById(kitId));
        setShowBoxSelectionModal(false);
        setSelectedBox(null);
        setSelectedRequest(null);
      })
      .catch((err) => {
        console.error('Failed to fulfill reorder request:', err);
        alert(err.message || 'Failed to fulfill reorder request');
      });
  };

  const filteredRequests = reorderRequests.filter(req => {
    if (filterStatus && req.status !== filterStatus) return false;
    if (filterPriority && req.priority !== filterPriority) return false;
    return true;
  });

  const canApprove = user?.is_admin || user?.department === 'Materials';
  const canFulfill = user?.is_admin || user?.department === 'Materials';

  return (
    <>
      <Card>
        <Card.Header>
          <Row className="align-items-center">
            <Col>
              <h5 className="mb-0">
                <FaShoppingCart className="me-2" />
                Reorder Requests
              </h5>
            </Col>
          </Row>
        </Card.Header>

        <Card.Body>
          {/* Filters */}
          <Row className="mb-3">
            <Col md={6}>
              <Form.Group>
                <Form.Label className="small">
                  <FaFilter className="me-1" />
                  Filter by Status
                </Form.Label>
                <Form.Select
                  size="sm"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="ordered">Ordered</option>
                  <option value="fulfilled">Fulfilled</option>
                  <option value="cancelled">Cancelled</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group>
                <Form.Label className="small">Filter by Priority</Form.Label>
                <Form.Select
                  size="sm"
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                >
                  <option value="">All Priorities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          {error && (
            <Alert variant="danger">
              {error.message || 'Failed to load reorder requests'}
            </Alert>
          )}

          {/* Requests Table */}
          {filteredRequests.length === 0 ? (
            <div className="text-center py-5 text-muted">
              <FaShoppingCart size={48} className="mb-3" />
              <p>No reorder requests found</p>
            </div>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Part Number</th>
                  <th>Description</th>
                  <th>Qty</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Type</th>
                  <th>Requested By</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRequests.map((request) => (
                  <tr key={request.id}>
                    <td><code>{request.part_number}</code></td>
                    <td>{request.description}</td>
                    <td><strong>{request.quantity_requested}</strong></td>
                    <td>{getPriorityBadge(request.priority)}</td>
                    <td>{getStatusBadge(request.status)}</td>
                    <td>
                      {request.is_automatic ? (
                        <Badge bg="info">Auto</Badge>
                      ) : (
                        <Badge bg="secondary">Manual</Badge>
                      )}
                    </td>
                    <td>{request.requested_by_name}</td>
                    <td>{new Date(request.requested_date).toLocaleDateString()}</td>
                    <td>
                      <ButtonGroup size="sm">
                        {request.status === 'pending' && canApprove && (
                          <Button
                            variant="success"
                            title="Approve"
                            onClick={() => handleAction(request, 'approve')}
                          >
                            <FaCheck />
                          </Button>
                        )}
                        {request.status === 'approved' && canFulfill && (
                          <Button
                            variant="info"
                            title="Mark as Ordered"
                            onClick={() => handleAction(request, 'order')}
                          >
                            <FaShoppingCart /> Order
                          </Button>
                        )}
                        {request.status === 'ordered' && canFulfill && (
                          <Button
                            variant="primary"
                            title="Mark as Fulfilled"
                            onClick={() => handleAction(request, 'fulfill')}
                          >
                            <FaCheck /> Fulfill
                          </Button>
                        )}
                        {request.status !== 'fulfilled' && request.status !== 'cancelled' && (
                          <Button
                            variant="danger"
                            title="Cancel"
                            onClick={() => handleAction(request, 'cancel')}
                          >
                            <FaTimes />
                          </Button>
                        )}
                      </ButtonGroup>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Confirmation Modal */}
      <Modal show={showConfirmModal} onHide={() => setShowConfirmModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Action</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedRequest && (
            <>
              <p>
                Are you sure you want to <strong>{confirmAction}</strong> this reorder request?
              </p>
              <Alert variant="light">
                <strong>Part:</strong> {selectedRequest.part_number}<br />
                <strong>Description:</strong> {selectedRequest.description}<br />
                <strong>Quantity:</strong> {selectedRequest.quantity_requested}<br />
                <strong>Priority:</strong> {getPriorityBadge(selectedRequest.priority)}
              </Alert>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowConfirmModal(false)}>
            Cancel
          </Button>
          <Button
            variant={confirmAction === 'cancel' ? 'danger' : 'primary'}
            onClick={confirmActionHandler}
            disabled={loading}
          >
            {loading ? 'Processing...' : `Confirm ${confirmAction}`}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Box Selection Modal for Fulfill */}
      <Modal show={showBoxSelectionModal} onHide={() => setShowBoxSelectionModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Select Box for Item</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedRequest && (
            <>
              <Alert variant="info">
                <strong>Item:</strong> {selectedRequest.part_number} - {selectedRequest.description}<br />
                <strong>Quantity:</strong> {selectedRequest.quantity_requested}
              </Alert>

              <Form.Group className="mb-3">
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
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => {
            setShowBoxSelectionModal(false);
            setSelectedBox(null);
          }}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleFulfillWithBox}
            disabled={!selectedBox || loading}
          >
            {loading ? 'Processing...' : 'Fulfill Order'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default KitReorderManagement;

