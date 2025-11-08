import { useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Table, Button, Badge, Form, Row, Col, Alert } from 'react-bootstrap';
import { FaFilter, FaSync } from 'react-icons/fa';
import { formatDate } from '../../utils/dateUtils';
import { fetchOrders } from '../../store/ordersSlice';

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
  const { orders, loading } = useSelector((state) => state.orders);
  
  const [filters, setFilters] = useState({
    order_type: 'all',
    status: 'all',
    priority: 'all',
    search: '',
  });

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleRefresh = () => {
    dispatch(fetchOrders());
  };

  const filteredOrders = useMemo(() => {
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
            <thead className="table-light">
              <tr>
                <th>Title</th>
                <th>Part Number</th>
                <th>Type</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Due Status</th>
                <th>Expected Delivery</th>
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
                    <Badge bg={PRIORITY_VARIANTS[order.priority]}>{order.priority}</Badge>
                  </td>
                  <td>
                    <Badge bg={STATUS_VARIANTS[order.status]}>{order.status.replace('_', ' ')}</Badge>
                  </td>
                  <td>
                    <Badge bg={DUE_STATUS_VARIANTS[order.due_status]}>{order.due_status?.replace('_', ' ') || 'N/A'}</Badge>
                  </td>
                  <td>{order.expected_delivery_date ? formatDate(order.expected_delivery_date) : '—'}</td>
                  <td>
                    <Button variant="primary" size="sm" onClick={() => onViewOrder(order)}>
                      View
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </>
  );
};

export default AllOrdersTab;

