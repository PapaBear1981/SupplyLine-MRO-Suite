import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Badge,
  Button,
  Card,
  Col,
  Form,
  Modal,
  Row,
  Spinner,
  Table,
  Alert,
  ListGroup,
} from 'react-bootstrap';
import {
  FaPlus,
  FaSync,
  FaFilter,
  FaChartPie,
  FaChartLine,
  FaEnvelope,
  FaClipboardList,
} from 'react-icons/fa';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { toast } from 'react-toastify';
import {
  fetchOrders,
  createOrder,
  updateOrder,
  fetchOrderAnalytics,
  fetchOrderMessages,
  fetchOrderById,
  sendOrderMessage,
  replyToOrderMessage,
  markOrderMessageRead,
} from '../store/ordersSlice';
import { fetchUsers } from '../store/usersSlice';
import { formatDate, formatDateTime } from '../utils/dateUtils';

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

const CHART_COLORS = ['#0d6efd', '#6f42c1', '#20c997', '#ffc107', '#dc3545', '#0dcaf0'];

const buildQueryParams = (values) => {
  const params = {};
  Object.entries(values).forEach(([key, value]) => {
    if (value && value !== 'all') {
      params[key] = value;
    }
  });
  return params;
};

const OrderManagementPage = () => {
  const dispatch = useDispatch();
  const {
    list,
    loading,
    analytics,
    analyticsLoading,
    messages,
    selectedOrder,
    messageActionLoading,
    error,
  } = useSelector((state) => state.orders);
  const { users } = useSelector((state) => state.users);
  const { user } = useSelector((state) => state.auth);

  const [filters, setFilters] = useState({
    status: '',
    order_type: '',
    priority: '',
    buyer_id: '',
    requester_id: '',
    due_after: '',
    due_before: '',
    search: '',
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    order_type: 'tool',
    priority: 'normal',
    expected_due_date: '',
    description: '',
    notes: '',
    reference_type: '',
    reference_number: '',
    tracking_number: '',
    requester_id: '',
    buyer_id: '',
  });
  const [detailForm, setDetailForm] = useState(null);
  const [messageForm, setMessageForm] = useState({ subject: '', message: '', recipient_id: '' });
  const [replyForm, setReplyForm] = useState({ message: '' });
  const [activeMessageId, setActiveMessageId] = useState(null);

  const orderMessages = useMemo(() => {
    if (!selectedOrder) return [];
    return messages[selectedOrder.id] || [];
  }, [messages, selectedOrder]);

  useEffect(() => {
    dispatch(fetchUsers()).catch(() => {});
  }, [dispatch]);

  useEffect(() => {
    const params = buildQueryParams(filters);
    dispatch(fetchOrders(params));
  }, [dispatch, filters]);

  useEffect(() => {
    dispatch(fetchOrderAnalytics());
  }, [dispatch]);

  useEffect(() => {
    if (selectedOrder) {
      setDetailForm({
        id: selectedOrder.id,
        title: selectedOrder.title,
        order_type: selectedOrder.order_type,
        status: selectedOrder.status,
        priority: selectedOrder.priority,
        expected_due_date: selectedOrder.expected_due_date
          ? selectedOrder.expected_due_date.substring(0, 10)
          : '',
        description: selectedOrder.description || '',
        notes: selectedOrder.notes || '',
        reference_type: selectedOrder.reference_type || '',
        reference_number: selectedOrder.reference_number || '',
        tracking_number: selectedOrder.tracking_number || '',
        requester_id: selectedOrder.requester_id || '',
        buyer_id: selectedOrder.buyer_id || '',
        kit_id: selectedOrder.kit_id || '',
      });
      setMessageForm({ subject: '', message: '', recipient_id: '' });
      setReplyForm({ message: '' });
      setActiveMessageId(null);
    }
  }, [selectedOrder]);

  const handleOpenCreate = () => {
    setCreateForm({
      title: '',
      order_type: 'tool',
      priority: 'normal',
      expected_due_date: '',
      description: '',
      notes: '',
      reference_type: '',
      reference_number: '',
      tracking_number: '',
      requester_id: user?.id || '',
      buyer_id: user?.id || '',
    });
    setShowCreateModal(true);
  };

  const handleCreateChange = (event) => {
    const { name, value } = event.target;
    setCreateForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleDetailChange = (event) => {
    const { name, value } = event.target;
    setDetailForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const resetFilters = () => {
    setFilters({
      status: '',
      order_type: '',
      priority: '',
      buyer_id: '',
      requester_id: '',
      due_after: '',
      due_before: '',
      search: '',
    });
  };

  const transformDate = (value) => {
    if (!value) return undefined;
    return `${value}T00:00:00`;
  };

  const handleCreateSubmit = (event) => {
    event.preventDefault();
    const payload = {
      ...createForm,
      expected_due_date: transformDate(createForm.expected_due_date),
      requester_id: createForm.requester_id ? Number(createForm.requester_id) : undefined,
      buyer_id: createForm.buyer_id ? Number(createForm.buyer_id) : undefined,
    };

    dispatch(createOrder(payload))
      .unwrap()
      .then(() => {
        toast.success('Order created');
        setShowCreateModal(false);
        dispatch(fetchOrderAnalytics());
        dispatch(fetchOrders(buildQueryParams(filters)));
      })
      .catch((err) => {
        toast.error(err?.message || err?.error || 'Failed to create order');
      });
  };

  const handleUpdateOrder = (event) => {
    event.preventDefault();
    if (!detailForm) return;

    const payload = {
      title: detailForm.title,
      order_type: detailForm.order_type,
      status: detailForm.status,
      priority: detailForm.priority,
      expected_due_date: transformDate(detailForm.expected_due_date),
      description: detailForm.description,
      notes: detailForm.notes,
      reference_type: detailForm.reference_type,
      reference_number: detailForm.reference_number,
      tracking_number: detailForm.tracking_number,
      requester_id: detailForm.requester_id ? Number(detailForm.requester_id) : null,
      buyer_id: detailForm.buyer_id ? Number(detailForm.buyer_id) : null,
      kit_id: detailForm.kit_id ? Number(detailForm.kit_id) : null,
    };

    dispatch(updateOrder({ orderId: detailForm.id, orderData: payload }))
      .unwrap()
      .then((updated) => {
        toast.success('Order updated');
        dispatch(fetchOrderAnalytics());
        dispatch(fetchOrders(buildQueryParams(filters)));
        dispatch(fetchOrderById({ orderId: updated.id, includeMessages: true }));
      })
      .catch((err) => {
        toast.error(err?.message || err?.error || 'Failed to update order');
      });
  };

  const handleOpenDetails = (order) => {
    dispatch(fetchOrderById({ orderId: order.id, includeMessages: true }))
      .unwrap()
      .then(() => {
        dispatch(fetchOrderMessages(order.id));
        setShowDetailModal(true);
      })
      .catch((err) => {
        toast.error(err?.message || err?.error || 'Failed to load order details');
      });
  };

  const handleMessageChange = (event) => {
    const { name, value } = event.target;
    setMessageForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSendMessage = (event) => {
    event.preventDefault();
    if (!selectedOrder || !messageForm.message) return;

    const payload = {
      subject: messageForm.subject || `Order ${selectedOrder.id} update`,
      message: messageForm.message,
      recipient_id: messageForm.recipient_id ? Number(messageForm.recipient_id) : undefined,
    };

    dispatch(sendOrderMessage({ orderId: selectedOrder.id, data: payload }))
      .unwrap()
      .then(() => {
        toast.success('Message sent');
        setMessageForm({ subject: '', message: '', recipient_id: '' });
        dispatch(fetchOrderMessages(selectedOrder.id));
        dispatch(fetchOrderById({ orderId: selectedOrder.id, includeMessages: true }));
      })
      .catch((err) => {
        toast.error(err?.message || err?.error || 'Failed to send message');
      });
  };

  const handleReplySubmit = (event, message) => {
    event.preventDefault();
    if (!replyForm.message) return;

    dispatch(replyToOrderMessage({ messageId: message.id, data: { message: replyForm.message } }))
      .unwrap()
      .then(() => {
        toast.success('Reply sent');
        setReplyForm({ message: '' });
        setActiveMessageId(null);
        dispatch(fetchOrderMessages(message.order_id));
        dispatch(fetchOrderById({ orderId: message.order_id, includeMessages: true }));
      })
      .catch((err) => {
        toast.error(err?.message || err?.error || 'Failed to send reply');
      });
  };

  const handleSelectMessage = (message) => {
    setActiveMessageId((prev) => (prev === message.id ? null : message.id));
    setReplyForm({ message: '' });
    if (!message.is_read && message.recipient_id === user?.id) {
      dispatch(markOrderMessageRead(message.id));
    }
  };

  const statusChartData = useMemo(() => {
    if (!analytics?.status_breakdown) return [];
    return analytics.status_breakdown.map((item) => ({
      name: item.status.replace('_', ' '),
      value: item.count,
    }));
  }, [analytics]);

  const priorityChartData = useMemo(() => {
    if (!analytics?.priority_breakdown) return [];
    return analytics.priority_breakdown.map((item) => ({
      name: item.priority,
      value: item.count,
    }));
  }, [analytics]);

  const monthlyChartData = useMemo(() => {
    if (!analytics?.orders_per_month) return [];
    return analytics.orders_per_month.map((item) => ({ month: item.month, count: item.count }));
  }, [analytics]);

  const uniqueUsers = useMemo(() => {
    return users || [];
  }, [users]);

  return (
    <div className="pb-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3 mb-1">Order Management</h1>
          <p className="text-muted mb-0">Track procurement activity for replacement tools, chemicals, and expendables.</p>
        </div>
        <div className="d-flex gap-2">
          <Button variant="outline-secondary" onClick={() => dispatch(fetchOrders(buildQueryParams(filters)))}>
            <FaSync className="me-2" />Refresh
          </Button>
          <Button variant="primary" onClick={handleOpenCreate}>
            <FaPlus className="me-2" />New Order
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || error.error || 'An unexpected error occurred.'}
        </Alert>
      )}

      <Card className="mb-4 shadow-sm">
        <Card.Header className="d-flex align-items-center">
          <FaFilter className="me-2 text-primary" /> Filters
        </Card.Header>
        <Card.Body>
          <Row className="g-3 align-items-end">
            <Col md={3}>
              <Form.Group controlId="filterStatus">
                <Form.Label>Status</Form.Label>
                <Form.Select name="status" value={filters.status} onChange={handleFilterChange}>
                  <option value="">All</option>
                  {ORDER_STATUSES.map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="filterType">
                <Form.Label>Type</Form.Label>
                <Form.Select name="order_type" value={filters.order_type} onChange={handleFilterChange}>
                  <option value="">All</option>
                  {ORDER_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="filterPriority">
                <Form.Label>Priority</Form.Label>
                <Form.Select name="priority" value={filters.priority} onChange={handleFilterChange}>
                  <option value="">All</option>
                  {PRIORITIES.map((priority) => (
                    <option key={priority.value} value={priority.value}>
                      {priority.label}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="filterBuyer">
                <Form.Label>Buyer</Form.Label>
                <Form.Select name="buyer_id" value={filters.buyer_id} onChange={handleFilterChange}>
                  <option value="">Any</option>
                  {uniqueUsers.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="filterRequester">
                <Form.Label>Requester</Form.Label>
                <Form.Select name="requester_id" value={filters.requester_id} onChange={handleFilterChange}>
                  <option value="">Any</option>
                  {uniqueUsers.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="filterDueAfter">
                <Form.Label>Due After</Form.Label>
                <Form.Control type="date" name="due_after" value={filters.due_after} onChange={handleFilterChange} />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="filterDueBefore">
                <Form.Label>Due Before</Form.Label>
                <Form.Control type="date" name="due_before" value={filters.due_before} onChange={handleFilterChange} />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group controlId="filterSearch">
                <Form.Label>Search</Form.Label>
                <Form.Control
                  type="text"
                  name="search"
                  placeholder="Reference, tracking, keywords"
                  value={filters.search}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Button variant="outline-secondary" onClick={resetFilters}>
                Clear Filters
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Row className="g-4 mb-4">
        <Col lg={3}>
          <Card className="shadow-sm h-100 border-0 bg-gradient-primary text-white">
            <Card.Body>
              <div className="d-flex align-items-center">
                <FaClipboardList className="me-3" size={28} />
                <div>
                  <div className="text-uppercase small">Open Orders</div>
                  <div className="fs-3 fw-semibold">{analytics?.total_open ?? 0}</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100 border-0">
            <Card.Body>
              <div className="d-flex align-items-center">
                <FaChartPie className="me-3 text-warning" size={28} />
                <div>
                  <div className="text-uppercase small text-muted">Due Soon</div>
                  <div className="fs-3 fw-semibold text-warning">{analytics?.due_soon_count ?? 0}</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100 border-0">
            <Card.Body>
              <div className="d-flex align-items-center">
                <FaChartLine className="me-3 text-danger" size={28} />
                <div>
                  <div className="text-uppercase small text-muted">Late Orders</div>
                  <div className="fs-3 fw-semibold text-danger">{analytics?.late_count ?? 0}</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={3}>
          <Card className="shadow-sm h-100 border-0">
            <Card.Body>
              <div className="d-flex align-items-center">
                <FaChartLine className="me-3 text-info" size={28} />
                <div>
                  <div className="text-uppercase small text-muted">Average Days Open</div>
                  <div className="fs-3 fw-semibold text-info">
                    {analytics?.average_open_days ? analytics.average_open_days.toFixed(1) : '0.0'}
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col xl={6}>
          <Card className="shadow-sm h-100">
            <Card.Header className="d-flex align-items-center">
              <FaChartPie className="me-2 text-primary" /> Status Breakdown
            </Card.Header>
            <Card.Body className="d-flex justify-content-center align-items-center" style={{ minHeight: 280 }}>
              {analyticsLoading ? (
                <Spinner animation="border" />
              ) : statusChartData.length === 0 ? (
                <div className="text-muted">No data available</div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={statusChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={90}>
                      {statusChartData.map((entry, index) => (
                        <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend layout="vertical" align="right" verticalAlign="middle" />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col xl={6}>
          <Card className="shadow-sm h-100">
            <Card.Header className="d-flex align-items-center">
              <FaChartPie className="me-2 text-success" /> Priority Distribution
            </Card.Header>
            <Card.Body className="d-flex justify-content-center align-items-center" style={{ minHeight: 280 }}>
              {analyticsLoading ? (
                <Spinner animation="border" />
              ) : priorityChartData.length === 0 ? (
                <div className="text-muted">No data available</div>
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={priorityChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={95}>
                      {priorityChartData.map((entry, index) => (
                        <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend layout="vertical" align="right" verticalAlign="middle" />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="g-4 mb-4">
        <Col xl={12}>
          <Card className="shadow-sm h-100">
            <Card.Header className="d-flex align-items-center">
              <FaChartLine className="me-2 text-success" /> Orders per Month
            </Card.Header>
            <Card.Body style={{ minHeight: 280 }}>
              {analyticsLoading ? (
                <div className="d-flex justify-content-center align-items-center h-100">
                  <Spinner animation="border" />
                </div>
              ) : monthlyChartData.length === 0 ? (
                <div className="text-muted">No data available</div>
              ) : (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={monthlyChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#0d6efd" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="shadow-sm">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <span>Orders</span>
          {loading && <Spinner animation="border" size="sm" />}
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table hover responsive className="mb-0 align-middle">
              <thead className="table-light">
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Requester</th>
                  <th>Buyer</th>
                  <th>Reference</th>
                  <th>Expected Due</th>
                  <th>Due Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {list.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="text-center py-4 text-muted">
                      No orders found
                    </td>
                  </tr>
                ) : (
                  list.map((order) => (
                    <tr key={order.id} className={order.due_status === 'late' ? 'table-danger' : order.due_status === 'due_soon' ? 'table-warning' : ''}>
                      <td className="fw-semibold">{order.title}</td>
                      <td>{order.order_type}</td>
                      <td>
                        <Badge bg={STATUS_VARIANTS[order.status] || 'secondary'} className="text-uppercase">
                          {order.status.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg={PRIORITY_VARIANTS[order.priority] || 'secondary'} className="text-uppercase">
                          {order.priority}
                        </Badge>
                      </td>
                      <td>{order.requester_name || '—'}</td>
                      <td>{order.buyer_name || '—'}</td>
                      <td>{order.reference_number || '—'}</td>
                      <td>{order.expected_due_date ? formatDate(order.expected_due_date) : 'N/A'}</td>
                      <td>
                        <Badge bg={DUE_STATUS_VARIANTS[order.due_status] || 'secondary'} className="text-uppercase">
                          {order.due_status.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td>
                        <Button variant="outline-primary" size="sm" onClick={() => handleOpenDetails(order)}>
                          View
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>

      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>New Order</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCreateSubmit}>
          <Modal.Body>
            <Row className="g-3">
              <Col md={8}>
                <Form.Group controlId="createTitle">
                  <Form.Label>Title</Form.Label>
                  <Form.Control name="title" value={createForm.title} onChange={handleCreateChange} required placeholder="What are you ordering?" />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group controlId="createType">
                  <Form.Label>Type</Form.Label>
                  <Form.Select name="order_type" value={createForm.order_type} onChange={handleCreateChange}>
                    {ORDER_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group controlId="createPriority">
                  <Form.Label>Priority</Form.Label>
                  <Form.Select name="priority" value={createForm.priority} onChange={handleCreateChange}>
                    {PRIORITIES.map((priority) => (
                      <option key={priority.value} value={priority.value}>
                        {priority.label}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group controlId="createDueDate">
                  <Form.Label>Expected Due Date</Form.Label>
                  <Form.Control type="date" name="expected_due_date" value={createForm.expected_due_date} onChange={handleCreateChange} />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group controlId="createReferenceType">
                  <Form.Label>Reference Type</Form.Label>
                  <Form.Control name="reference_type" value={createForm.reference_type} onChange={handleCreateChange} placeholder="PO, RO, etc." />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group controlId="createReferenceNumber">
                  <Form.Label>Reference Number</Form.Label>
                  <Form.Control name="reference_number" value={createForm.reference_number} onChange={handleCreateChange} placeholder="PO-123" />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group controlId="createTrackingNumber">
                  <Form.Label>Tracking Number</Form.Label>
                  <Form.Control name="tracking_number" value={createForm.tracking_number} onChange={handleCreateChange} placeholder="Tracking number" />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group controlId="createRequester">
                  <Form.Label>Requester</Form.Label>
                  <Form.Select name="requester_id" value={createForm.requester_id} onChange={handleCreateChange}>
                    <option value="">Select requester</option>
                    {uniqueUsers.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group controlId="createBuyer">
                  <Form.Label>Buyer</Form.Label>
                  <Form.Select name="buyer_id" value={createForm.buyer_id} onChange={handleCreateChange}>
                    <option value="">Assign later</option>
                    {uniqueUsers.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={12}>
                <Form.Group controlId="createDescription">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="description"
                    value={createForm.description}
                    onChange={handleCreateChange}
                    placeholder="Describe the item or need"
                  />
                </Form.Group>
              </Col>
              <Col md={12}>
                <Form.Group controlId="createNotes">
                  <Form.Label>Notes</Form.Label>
                  <Form.Control as="textarea" rows={2} name="notes" value={createForm.notes} onChange={handleCreateChange} placeholder="Internal notes" />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Create Order
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      <Modal show={showDetailModal} onHide={() => setShowDetailModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>Order Details</Modal.Title>
        </Modal.Header>
        {detailForm ? (
          <Modal.Body>
            <Row className="g-4">
              <Col lg={7}>
                <Form onSubmit={handleUpdateOrder}>
                  <Row className="g-3">
                    <Col md={8}>
                      <Form.Group controlId="detailTitle">
                        <Form.Label>Title</Form.Label>
                        <Form.Control name="title" value={detailForm.title} onChange={handleDetailChange} required />
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group controlId="detailType">
                        <Form.Label>Type</Form.Label>
                        <Form.Select name="order_type" value={detailForm.order_type} onChange={handleDetailChange}>
                          {ORDER_TYPES.map((type) => (
                            <option key={type.value} value={type.value}>
                              {type.label}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group controlId="detailStatus">
                        <Form.Label>Status</Form.Label>
                        <Form.Select name="status" value={detailForm.status} onChange={handleDetailChange}>
                          {ORDER_STATUSES.map((status) => (
                            <option key={status.value} value={status.value}>
                              {status.label}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group controlId="detailPriority">
                        <Form.Label>Priority</Form.Label>
                        <Form.Select name="priority" value={detailForm.priority} onChange={handleDetailChange}>
                          {PRIORITIES.map((priority) => (
                            <option key={priority.value} value={priority.value}>
                              {priority.label}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group controlId="detailDueDate">
                        <Form.Label>Expected Due Date</Form.Label>
                        <Form.Control type="date" name="expected_due_date" value={detailForm.expected_due_date} onChange={handleDetailChange} />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group controlId="detailReferenceType">
                        <Form.Label>Reference Type</Form.Label>
                        <Form.Control name="reference_type" value={detailForm.reference_type} onChange={handleDetailChange} />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group controlId="detailReferenceNumber">
                        <Form.Label>Reference Number</Form.Label>
                        <Form.Control name="reference_number" value={detailForm.reference_number} onChange={handleDetailChange} />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group controlId="detailTrackingNumber">
                        <Form.Label>Tracking Number</Form.Label>
                        <Form.Control name="tracking_number" value={detailForm.tracking_number} onChange={handleDetailChange} />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group controlId="detailKit">
                        <Form.Label>Kit ID (optional)</Form.Label>
                        <Form.Control name="kit_id" value={detailForm.kit_id || ''} onChange={handleDetailChange} placeholder="Associate with kit" />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group controlId="detailRequester">
                        <Form.Label>Requester</Form.Label>
                        <Form.Select name="requester_id" value={detailForm.requester_id} onChange={handleDetailChange}>
                          <option value="">Unassigned</option>
                          {uniqueUsers.map((u) => (
                            <option key={u.id} value={u.id}>
                              {u.name}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group controlId="detailBuyer">
                        <Form.Label>Buyer</Form.Label>
                        <Form.Select name="buyer_id" value={detailForm.buyer_id} onChange={handleDetailChange}>
                          <option value="">Unassigned</option>
                          {uniqueUsers.map((u) => (
                            <option key={u.id} value={u.id}>
                              {u.name}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={12}>
                      <Form.Group controlId="detailDescription">
                        <Form.Label>Description</Form.Label>
                        <Form.Control as="textarea" rows={3} name="description" value={detailForm.description} onChange={handleDetailChange} />
                      </Form.Group>
                    </Col>
                    <Col md={12}>
                      <Form.Group controlId="detailNotes">
                        <Form.Label>Notes</Form.Label>
                        <Form.Control as="textarea" rows={2} name="notes" value={detailForm.notes} onChange={handleDetailChange} />
                      </Form.Group>
                    </Col>
                  </Row>
                  <div className="d-flex justify-content-end mt-4">
                    <Button type="submit" variant="primary">
                      Save Changes
                    </Button>
                  </div>
                </Form>
              </Col>
              <Col lg={5}>
                <Card className="shadow-sm h-100">
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    <span>
                      <FaEnvelope className="me-2" /> Messages
                    </span>
                    <Badge bg="secondary" pill>
                      {selectedOrder?.message_count ?? 0}
                    </Badge>
                  </Card.Header>
                  <Card.Body className="d-flex flex-column">
                    <Form onSubmit={handleSendMessage} className="mb-3">
                      <Form.Group className="mb-2" controlId="messageSubject">
                        <Form.Label>Subject</Form.Label>
                        <Form.Control name="subject" value={messageForm.subject} onChange={handleMessageChange} placeholder="Order update subject" />
                      </Form.Group>
                      <Form.Group className="mb-2" controlId="messageRecipient">
                        <Form.Label>Recipient</Form.Label>
                        <Form.Select name="recipient_id" value={messageForm.recipient_id} onChange={handleMessageChange}>
                          <option value="">Auto (requester/buyer)</option>
                          {uniqueUsers.map((u) => (
                            <option key={u.id} value={u.id}>
                              {u.name}
                            </option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                      <Form.Group className="mb-2" controlId="messageBody">
                        <Form.Label>Message</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={3}
                          name="message"
                          value={messageForm.message}
                          onChange={handleMessageChange}
                          placeholder="Ask for more information or provide an update"
                          required
                        />
                      </Form.Group>
                      <div className="d-flex justify-content-end">
                        <Button type="submit" variant="primary" disabled={!messageForm.message || messageActionLoading}>
                          Send Message
                        </Button>
                      </div>
                    </Form>
                    <div className="flex-grow-1 overflow-auto" style={{ maxHeight: 320 }}>
                      {orderMessages.length === 0 ? (
                        <div className="text-center text-muted py-3">No messages yet</div>
                      ) : (
                        <ListGroup variant="flush">
                          {orderMessages.map((message) => (
                            <ListGroup.Item key={message.id} className="py-3">
                              <div className="d-flex justify-content-between align-items-start">
                                <div>
                                  <div className="fw-semibold">{message.subject}</div>
                                  <div className="small text-muted">
                                    From {message.sender_name || 'Unknown'} • {formatDateTime(message.sent_date)}
                                  </div>
                                </div>
                                <div className="text-end">
                                  {!message.is_read && message.recipient_id === user?.id && (
                                    <Badge bg="primary">New</Badge>
                                  )}
                                </div>
                              </div>
                              <p className="mt-2 mb-2">{message.message}</p>
                              <div className="d-flex justify-content-end gap-2">
                                {!message.is_read && message.recipient_id === user?.id && (
                                  <Button
                                    variant="outline-success"
                                    size="sm"
                                    onClick={() => dispatch(markOrderMessageRead(message.id))}
                                  >
                                    Mark Read
                                  </Button>
                                )}
                                <Button variant="outline-primary" size="sm" onClick={() => handleSelectMessage(message)}>
                                  {activeMessageId === message.id ? 'Cancel' : 'Reply'}
                                </Button>
                              </div>
                              {activeMessageId === message.id && (
                                <Form className="mt-3" onSubmit={(event) => handleReplySubmit(event, message)}>
                                  <Form.Group controlId={`reply-${message.id}`} className="mb-2">
                                    <Form.Control
                                      as="textarea"
                                      rows={2}
                                      value={replyForm.message}
                                      onChange={(event) => setReplyForm({ message: event.target.value })}
                                      placeholder="Type your reply"
                                      required
                                    />
                                  </Form.Group>
                                  <div className="d-flex justify-content-end gap-2">
                                    <Button variant="outline-secondary" size="sm" onClick={() => setActiveMessageId(null)}>
                                      Cancel
                                    </Button>
                                    <Button type="submit" variant="primary" size="sm" disabled={messageActionLoading || !replyForm.message}>
                                      Send Reply
                                    </Button>
                                  </div>
                                </Form>
                              )}
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      )}
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Modal.Body>
        ) : (
          <div className="d-flex justify-content-center align-items-center py-5">
            <Spinner animation="border" />
          </div>
        )}
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default OrderManagementPage;
