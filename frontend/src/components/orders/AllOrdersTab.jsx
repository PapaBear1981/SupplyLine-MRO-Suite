import { useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Badge, Form, Row, Col, Alert, Modal } from 'react-bootstrap';
import { FaFilter, FaSync, FaCheckCircle } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { formatDate } from '../../utils/dateUtils';
import { fetchOrders } from '../../store/ordersSlice';
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
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [deliveryForm, setDeliveryForm] = useState({
    received_quantity: '',
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
      await dispatch(markChemicalAsDelivered({
        id: selectedOrder.chemical_id || selectedOrder.id,
        received_quantity: deliveryForm.received_quantity ? parseFloat(deliveryForm.received_quantity) : null,
      })).unwrap();

      toast.success('Chemical marked as delivered and order updated!');
      handleCloseDeliveryModal();

      // Refresh the orders list
      dispatch(fetchOrders());
    } catch (error) {
      toast.error(error.message || 'Failed to mark chemical as delivered');
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
                <th>Title</th>
                <th>Part Number</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Due Status</th>
                <th>Expected Due Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map((order) => (
                <tr key={order.id}>
                  <td>{order.title}</td>
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
                  <td>
                    <Badge bg={DUE_STATUS_VARIANTS[order.due_status]}>{order.due_status?.replace('_', ' ') || 'N/A'}</Badge>
                  </td>
                  <td>{order.expected_due_date ? formatDate(order.expected_due_date) : '—'}</td>
                  <td>
                    <Button variant="primary" size="sm" onClick={() => onViewOrder(order)} className="me-2">
                      View
                    </Button>
                    {order.order_type === 'chemical' && (order.status === 'ordered' || order.status === 'shipped') && (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleOpenDeliveryModal(order)}
                      >
                        <FaCheckCircle className="me-1" />
                        Mark Delivered
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
          <Modal.Title>Mark Chemical as Delivered</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmitDelivery}>
          <Modal.Body>
            {selectedOrder && (
              <>
                <Alert variant="info">
                  <strong>Order Details:</strong>
                  <ul className="mb-0 mt-2">
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
                  <strong>Note:</strong> Marking this chemical as delivered will:
                  <ul className="mb-0 mt-2">
                    <li>Update the chemical status to "available"</li>
                    <li>Clear the reorder status</li>
                    <li>Close the associated procurement order</li>
                    <li>Add the chemical back to active inventory</li>
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
    </>
  );
};

export default AllOrdersTab;

