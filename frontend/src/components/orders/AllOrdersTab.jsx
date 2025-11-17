import { useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Badge, Form, Row, Col, Alert, Modal } from 'react-bootstrap';
import { FaFilter, FaSync, FaCheckCircle, FaShoppingCart, FaEnvelope } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { formatDate } from '../../utils/dateUtils';
import { fetchOrders, markOrderAsDelivered, markOrderAsOrdered } from '../../store/ordersSlice';
import { markChemicalAsDelivered } from '../../store/chemicalsSlice';

const ORDER_TYPES = [
  { value: 'tool', label: 'Tool' },
  { value: 'chemical', label: 'Chemical' },
  { value: 'expendable', label: 'Expendable' },
  { value: 'kit', label: 'Kit Component' },
];

const ORDER_STATUSES = [
  { value: 'new', label: 'New' },
  { value: 'awaiting_info', label: 'Awaiting Info' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'ordered', label: 'Ordered' },
  { value: 'shipped', label: 'Shipped' },
  { value: 'received', label: 'Received' },
  { value: 'cancelled', label: 'Cancelled' },
];

const PRIORITIES = [
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'normal', label: 'Normal' },
  { value: 'low', label: 'Low' },
];

const PRIORITY_VARIANTS = {
  critical: 'danger',
  high: 'warning',
  normal: 'secondary',
  low: 'info',
};

const STATUS_VARIANTS = {
  new: 'secondary',
  awaiting_info: 'warning',
  in_progress: 'info',
  ordered: 'primary',
  shipped: 'info',
  received: 'success',
  cancelled: 'secondary',
};

const DUE_STATUS_VARIANTS = {
  late: 'danger',
  due_soon: 'warning',
  completed: 'success',
  on_track: 'info',
  unscheduled: 'secondary',
};

const AllOrdersTab = ({ onViewOrder }) => {
  const dispatch = useDispatch();
  const { list: orders, loading } = useSelector((state) => state.orders);

  const [filters, setFilters] = useState({
    order_type: 'all',
    status: 'all',
    priority: 'all',
    search: '',
  });

  const [showDeliveryModal, setShowDeliveryModal] = useState(false);
  const [showOrderedModal, setShowOrderedModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [deliveryForm, setDeliveryForm] = useState({
    received_quantity: '',
  });
  const [orderedForm, setOrderedForm] = useState({
    expected_due_date: '',
    tracking_number: '',
    vendor: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleRefresh = () => {
    dispatch(fetchOrders());
  };

  const handleOpenDeliveryModal = (order) => {
    setSelectedOrder(order);
    setDeliveryForm({
      received_quantity: order.quantity || '',
    });
    setShowDeliveryModal(true);
  };

  const handleCloseDeliveryModal = () => {
    setShowDeliveryModal(false);
    setSelectedOrder(null);
    setDeliveryForm({
      received_quantity: '',
    });
  };

  const handleDeliveryFormChange = (e) => {
    const { name, value } = e.target;
    setDeliveryForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmitDelivery = async (e) => {
    e.preventDefault();

    setSubmitting(true);
    try {
      // For chemical orders, use the chemical-specific endpoint
      if (selectedOrder.order_type === 'chemical' && selectedOrder.chemical_id) {
        await dispatch(markChemicalAsDelivered({
          id: selectedOrder.chemical_id,
          received_quantity: deliveryForm.received_quantity ? parseFloat(deliveryForm.received_quantity) : null,
        })).unwrap();
        toast.success('Chemical marked as delivered and order updated!');
      } else {
        // For all other order types, use the general order endpoint
        await dispatch(markOrderAsDelivered({
          orderId: selectedOrder.id,
          received_quantity: deliveryForm.received_quantity ? parseFloat(deliveryForm.received_quantity) : null,
        })).unwrap();
        toast.success('Order marked as delivered successfully!');
      }

      handleCloseDeliveryModal();

      // Refresh the orders list
      dispatch(fetchOrders());
    } catch (error) {
      toast.error(error.message || 'Failed to mark order as delivered');
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenOrderedModal = (order) => {
    setSelectedOrder(order);
    setOrderedForm({
      expected_due_date: '',
      tracking_number: order.tracking_number || '',
      vendor: order.vendor || '',
      notes: '',
    });
    setShowOrderedModal(true);
  };

  const handleCloseOrderedModal = () => {
    setShowOrderedModal(false);
    setSelectedOrder(null);
    setOrderedForm({
      expected_due_date: '',
      tracking_number: '',
      vendor: '',
      notes: '',
    });
  };

  const handleOrderedFormChange = (e) => {
    const { name, value } = e.target;
    setOrderedForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmitOrdered = async (e) => {
    e.preventDefault();

    setSubmitting(true);
    try {
      const orderData = {};

      if (orderedForm.expected_due_date) {
        orderData.expected_due_date = orderedForm.expected_due_date;
      }
      if (orderedForm.tracking_number) {
        orderData.tracking_number = orderedForm.tracking_number;
      }
      if (orderedForm.vendor) {
        orderData.vendor = orderedForm.vendor;
      }
      if (orderedForm.notes) {
        orderData.notes = orderedForm.notes;
      }

      await dispatch(markOrderAsOrdered({
        orderId: selectedOrder.id,
        orderData,
      })).unwrap();

      toast.success('Order marked as ordered successfully!');
      handleCloseOrderedModal();

      // Refresh the orders list
      dispatch(fetchOrders());
    } catch (error) {
      toast.error(error.message || 'Failed to mark order as ordered');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredOrders = useMemo(() => {
    if (!Array.isArray(orders)) return [];
    return orders.filter((order) => {
      if (filters.order_type !== 'all' && order.order_type !== filters.order_type) return false;
      if (filters.status !== 'all' && order.status !== filters.status) return false;
      if (filters.priority !== 'all' && order.priority !== filters.priority) return false;
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        return (
          order.title?.toLowerCase().includes(searchLower) ||
          order.part_number?.toLowerCase().includes(searchLower) ||
          order.description?.toLowerCase().includes(searchLower)
        );
      }
      return true;
    });
  }, [orders, filters]);

  return (
    <>
      {/* Filters */}
      <Row className="mb-3">
        <Col md={3}>
          <Form.Group>
            <Form.Label><FaFilter className="me-1" />Type</Form.Label>
            <Form.Select name="order_type" value={filters.order_type} onChange={handleFilterChange}>
              <option value="all">All Types</option>
              {ORDER_TYPES.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Col>
        <Col md={3}>
          <Form.Group>
            <Form.Label>Status</Form.Label>
            <Form.Select name="status" value={filters.status} onChange={handleFilterChange}>
              <option value="all">All Statuses</option>
              {ORDER_STATUSES.map((status) => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Col>
        <Col md={3}>
          <Form.Group>
            <Form.Label>Priority</Form.Label>
            <Form.Select name="priority" value={filters.priority} onChange={handleFilterChange}>
              <option value="all">All Priorities</option>
              {PRIORITIES.map((priority) => (
                <option key={priority.value} value={priority.value}>{priority.label}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Col>
        <Col md={3}>
          <Form.Group>
            <Form.Label>Search</Form.Label>
            <Form.Control
              type="text"
              name="search"
              placeholder="Search orders..."
              value={filters.search}
              onChange={handleFilterChange}
            />
          </Form.Group>
        </Col>
      </Row>

      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <strong>{filteredOrders.length}</strong> order{filteredOrders.length !== 1 ? 's' : ''} found
        </div>
        <Button variant="outline-primary" size="sm" onClick={handleRefresh}>
          <FaSync className="me-1" />Refresh
        </Button>
      </div>

      {/* Orders Table */}
      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : filteredOrders.length === 0 ? (
        <Alert variant="info">No orders match your current filters.</Alert>
      ) : (
        <div className="table-responsive">
          <Table hover bordered className="align-middle">
            <thead>
              <tr>
                <th>Order #</th>
                <th>Title</th>
                <th>Part Number</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created Date</th>
                <th>Due Status</th>
                <th>Expected Due Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map((order) => (
                <tr key={order.id}>
                  <td>
                    {order.order_number ? (
                      <Badge bg="dark">{order.order_number}</Badge>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td>
                    <div className="d-flex align-items-center gap-2">
                      {order.title}
                      {order.unread_message_count > 0 && (
                        <Badge bg="danger" pill title={`${order.unread_message_count} unread message(s) - update request pending`}>
                          <FaEnvelope className="me-1" />
                          {order.unread_message_count} unread
                        </Badge>
                      )}
                      {order.message_count > 0 && order.unread_message_count === 0 && (
                        <Badge bg="secondary" pill title={`${order.message_count} message(s)`}>
                          <FaEnvelope className="me-1" />
                          {order.message_count}
                        </Badge>
                      )}
                    </div>
                  </td>
                  <td>{order.part_number || '—'}</td>
                  <td>
                    <Badge bg="secondary">{ORDER_TYPES.find(t => t.value === order.order_type)?.label || order.order_type}</Badge>
                  </td>
                  <td>
                    {order.quantity ? (
                      <strong>{order.quantity} {order.unit}</strong>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td>
                    <Badge bg={PRIORITY_VARIANTS[order.priority]}>{order.priority}</Badge>
                  </td>
                  <td>
                    <Badge bg={STATUS_VARIANTS[order.status]}>{order.status.replace('_', ' ')}</Badge>
                  </td>
                  <td>{order.created_at ? formatDate(order.created_at) : '—'}</td>
                  <td>
                    <Badge bg={DUE_STATUS_VARIANTS[order.due_status]}>{order.due_status?.replace('_', ' ') || 'N/A'}</Badge>
                  </td>
                  <td>{order.expected_due_date ? formatDate(order.expected_due_date) : '—'}</td>
                  <td>
                    <Button variant="primary" size="sm" onClick={() => onViewOrder(order)} className="me-1" title="View Details">
                      View
                    </Button>
                    {(order.status === 'new' || order.status === 'awaiting_info' || order.status === 'in_progress') && (
                      <Button
                        variant="info"
                        size="sm"
                        onClick={() => handleOpenOrderedModal(order)}
                        className="me-1"
                        title="Mark as Ordered"
                      >
                        <FaShoppingCart />
                      </Button>
                    )}
                    {(order.status === 'new' || order.status === 'ordered' || order.status === 'shipped' || order.status === 'in_progress') && (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleOpenDeliveryModal(order)}
                        title="Mark as Delivered"
                      >
                        <FaCheckCircle />
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}

      {/* Delivery Modal */}
      <Modal show={showDeliveryModal} onHide={handleCloseDeliveryModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Mark Order as Delivered</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmitDelivery}>
          <Modal.Body>
            {selectedOrder && (
              <>
                <Alert variant="info">
                  <strong>Order Details:</strong>
                  <ul className="mb-0 mt-2">
                    <li><strong>Type:</strong> {selectedOrder.order_type}</li>
                    <li><strong>Title:</strong> {selectedOrder.title}</li>
                    <li><strong>Part Number:</strong> {selectedOrder.part_number || 'N/A'}</li>
                    <li><strong>Description:</strong> {selectedOrder.description || 'N/A'}</li>
                    <li><strong>Order Quantity:</strong> {selectedOrder.quantity} {selectedOrder.unit}</li>
                    <li><strong>Status:</strong> {selectedOrder.status}</li>
                    <li><strong>Expected Due Date:</strong> {selectedOrder.expected_due_date ? formatDate(selectedOrder.expected_due_date) : 'N/A'}</li>
                  </ul>
                </Alert>

                <Row>
                  <Col md={12}>
                    <Form.Group className="mb-3">
                      <Form.Label>Received Quantity (Optional)</Form.Label>
                      <Form.Control
                        type="number"
                        step="0.01"
                        name="received_quantity"
                        value={deliveryForm.received_quantity}
                        onChange={handleDeliveryFormChange}
                        placeholder="Enter quantity received (if different from ordered)"
                      />
                      <Form.Text className="text-muted">
                        Leave blank to keep the current quantity ({selectedOrder.quantity || 0} {selectedOrder.unit})
                      </Form.Text>
                    </Form.Group>
                  </Col>
                </Row>

                <Alert variant="warning" className="mb-0">
                  <i className="bi bi-info-circle-fill me-2"></i>
                  <strong>Note:</strong> Marking this order as delivered will:
                  <ul className="mb-0 mt-2">
                    <li>Update the order status to "received"</li>
                    <li>Set the completion date to today</li>
                    {selectedOrder.order_type === 'chemical' && (
                      <>
                        <li>Update the chemical status to "available"</li>
                        <li>Clear the chemical reorder status</li>
                        <li>Add the chemical back to active inventory</li>
                      </>
                    )}
                  </ul>
                </Alert>
              </>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseDeliveryModal} disabled={submitting}>
              Cancel
            </Button>
            <Button variant="success" type="submit" disabled={submitting}>
              {submitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Processing...
                </>
              ) : (
                <>
                  <FaCheckCircle className="me-1" />
                  Mark as Delivered
                </>
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Mark as Ordered Modal */}
      <Modal show={showOrderedModal} onHide={handleCloseOrderedModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Mark Request as Ordered</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmitOrdered}>
          <Modal.Body>
            {selectedOrder && (
              <>
                <Alert variant="info">
                  <strong>Request Details:</strong>
                  <ul className="mb-0 mt-2">
                    <li><strong>Type:</strong> {selectedOrder.order_type}</li>
                    <li><strong>Title:</strong> {selectedOrder.title}</li>
                    <li><strong>Part Number:</strong> {selectedOrder.part_number || 'N/A'}</li>
                    <li><strong>Description:</strong> {selectedOrder.description || 'N/A'}</li>
                    <li><strong>Quantity:</strong> {selectedOrder.quantity} {selectedOrder.unit}</li>
                    <li><strong>Current Status:</strong> {selectedOrder.status}</li>
                  </ul>
                </Alert>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Expected Due Date</Form.Label>
                      <Form.Control
                        type="date"
                        name="expected_due_date"
                        value={orderedForm.expected_due_date}
                        onChange={handleOrderedFormChange}
                      />
                      <Form.Text className="text-muted">
                        When do you expect the order to arrive?
                      </Form.Text>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Tracking Number (Optional)</Form.Label>
                      <Form.Control
                        type="text"
                        name="tracking_number"
                        value={orderedForm.tracking_number}
                        onChange={handleOrderedFormChange}
                        placeholder="Enter tracking number if available"
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={12}>
                    <Form.Group className="mb-3">
                      <Form.Label>Vendor (Optional)</Form.Label>
                      <Form.Control
                        type="text"
                        name="vendor"
                        value={orderedForm.vendor}
                        onChange={handleOrderedFormChange}
                        placeholder="Enter vendor/supplier name"
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={12}>
                    <Form.Group className="mb-3">
                      <Form.Label>Additional Notes (Optional)</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        name="notes"
                        value={orderedForm.notes}
                        onChange={handleOrderedFormChange}
                        placeholder="Any additional notes about the order..."
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Alert variant="warning" className="mb-0">
                  <i className="bi bi-info-circle-fill me-2"></i>
                  <strong>Note:</strong> Marking this request as ordered will:
                  <ul className="mb-0 mt-2">
                    <li>Update the status to &quot;ordered&quot;</li>
                    <li>Set the expected due date (if provided)</li>
                    <li>Record the vendor and tracking information</li>
                    <li>Log this action for audit purposes</li>
                  </ul>
                </Alert>
              </>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseOrderedModal} disabled={submitting}>
              Cancel
            </Button>
            <Button variant="info" type="submit" disabled={submitting}>
              {submitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Processing...
                </>
              ) : (
                <>
                  <FaShoppingCart className="me-1" />
                  Mark as Ordered
                </>
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
};

export default AllOrdersTab;

