import React, { useEffect, useState, useCallback } from 'react';
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
import ReorderRequestDetailModal from './ReorderRequestDetailModal';

const KitReorderManagement = ({ kitId = null }) => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { loading, error, reorderRequests: allReorderRequests } = useSelector((state) => state.kits);

  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [boxes, setBoxes] = useState([]);

  // Filter reorder requests based on filters
  const reorderRequests = allReorderRequests || [];

  const loadBoxes = useCallback(async () => {
    try {
      const response = await api.get(`/kits/${kitId}/boxes`);
      setBoxes(response.data);
    } catch (error) {
      console.error('Failed to load boxes:', error);
    }
  }, [kitId]);

  const loadReorderRequests = useCallback(() => {
    const filters = {};
    if (filterStatus) filters.status = filterStatus;
    if (filterPriority) filters.priority = filterPriority;

    dispatch(fetchReorderRequests({ kitId, filters }));
  }, [dispatch, kitId, filterStatus, filterPriority]);

  useEffect(() => {
    loadReorderRequests();
    loadBoxes();
  }, [loadReorderRequests, loadBoxes]);

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

  const handleRowClick = (request) => {
    setSelectedRequest(request);
    setShowDetailModal(true);
  };

  const handleApprove = (requestId) => {
    dispatch(approveReorderRequest(requestId))
      .unwrap()
      .then(() => {
        loadReorderRequests();
        setShowDetailModal(false);
        setSelectedRequest(null);
      })
      .catch((err) => {
        console.error('Failed to approve reorder request:', err);
        alert(err.message || 'Failed to approve reorder request');
      });
  };

  const handleMarkAsOrdered = (requestId) => {
    dispatch(markReorderAsOrdered(requestId))
      .unwrap()
      .then(() => {
        loadReorderRequests();
        setShowDetailModal(false);
        setSelectedRequest(null);
      })
      .catch((err) => {
        console.error('Failed to mark reorder as ordered:', err);
        alert(err.message || 'Failed to mark reorder as ordered');
      });
  };

  const handleFulfill = (requestId, boxId) => {
    if (!boxId) {
      alert('Please select a box');
      return;
    }

    dispatch(fulfillReorderRequest({
      requestId,
      boxId
    }))
      .unwrap()
      .then(() => {
        loadReorderRequests();
        // Refresh kit items to show updated inventory
        dispatch(fetchKitItems({ kitId }));
        // Refresh kit overview to update item count
        dispatch(fetchKitById(kitId));
        setShowDetailModal(false);
        setSelectedRequest(null);
      })
      .catch((err) => {
        console.error('Failed to fulfill reorder request:', err);
        alert(err.message || 'Failed to fulfill reorder request');
      });
  };

  const handleCancel = (requestId) => {
    if (!window.confirm('Are you sure you want to cancel this reorder request?')) {
      return;
    }

    dispatch(cancelReorderRequest(requestId))
      .unwrap()
      .then(() => {
        loadReorderRequests();
        setShowDetailModal(false);
        setSelectedRequest(null);
      })
      .catch((err) => {
        console.error('Failed to cancel reorder request:', err);
        alert(err.message || 'Failed to cancel reorder request');
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
            <>
              <Alert variant="info" className="mb-3">
                <FaExclamationCircle className="me-2" />
                Click on any row to view full details and take action
              </Alert>
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
                  </tr>
                </thead>
                <tbody>
                  {filteredRequests.map((request) => (
                    <tr
                      key={request.id}
                      onClick={() => handleRowClick(request)}
                      style={{ cursor: 'pointer' }}
                      className="align-middle"
                    >
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
                      <td>{request.requester_name}</td>
                      <td>{new Date(request.requested_date).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </>
          )}
        </Card.Body>
      </Card>

      {/* Reorder Request Detail Modal */}
      <ReorderRequestDetailModal
        show={showDetailModal}
        onHide={() => {
          setShowDetailModal(false);
          setSelectedRequest(null);
        }}
        request={selectedRequest}
        onApprove={handleApprove}
        onMarkAsOrdered={handleMarkAsOrdered}
        onFulfill={handleFulfill}
        onCancel={handleCancel}
        canApprove={canApprove}
        canFulfill={canFulfill}
        loading={loading}
        boxes={boxes}
      />
    </>
  );
};

export default KitReorderManagement;

