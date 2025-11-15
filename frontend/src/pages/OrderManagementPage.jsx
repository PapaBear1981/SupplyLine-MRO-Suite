import { useEffect, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Badge,
  Button,
  Card,
  Col,
  Form,
  Modal,
  Row,
  Tabs,
  Tab,
  ListGroup,
} from 'react-bootstrap';
import {
  FaPlus,
  FaEnvelope,
  FaClipboardList,
} from 'react-icons/fa';
import { toast } from 'react-toastify';
import {
  fetchOrders,
  createOrder,
  updateOrder,
  fetchOrderMessages,
  fetchOrderById,
  sendOrderMessage,
  replyToOrderMessage,
  markOrderMessageRead,
} from '../store/ordersSlice';
import { fetchUsers } from '../store/usersSlice';

// Import tab components
import AllOrdersTab from '../components/orders/AllOrdersTab';
import ChemicalsNeedingReorderTab from '../components/orders/ChemicalsNeedingReorderTab';
import ChemicalsOnOrderTab from '../components/orders/ChemicalsOnOrderTab';
import AnalyticsTab from '../components/orders/AnalyticsTab';
import OrderDetailModal from '../components/orders/OrderDetailModal';

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

const OrderManagementPage = () => {
  const dispatch = useDispatch();
  const {
    messages,
    selectedOrder,
    messageActionLoading,
  } = useSelector((state) => state.orders);
  const { users } = useSelector((state) => state.users);
  const { user } = useSelector((state) => state.auth);

  const [activeTab, setActiveTab] = useState('all-orders');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    order_type: 'tool',
    part_number: '',
    priority: 'normal',
    expected_due_date: '',
    description: '',
    notes: '',
    tracking_number: '',
    requester_id: '',
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
    dispatch(fetchOrders());
  }, [dispatch]);

  useEffect(() => {
    if (selectedOrder) {
      setDetailForm({
        id: selectedOrder.id,
        title: selectedOrder.title,
        order_type: selectedOrder.order_type,
        part_number: selectedOrder.part_number || '',
        status: selectedOrder.status,
        priority: selectedOrder.priority,
        expected_due_date: selectedOrder.expected_due_date
          ? selectedOrder.expected_due_date.substring(0, 10)
          : '',
        description: selectedOrder.description || '',
        notes: selectedOrder.notes || '',
        tracking_number: selectedOrder.tracking_number || '',
        requester_id: selectedOrder.requested_by_id || '',
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
      part_number: '',
      priority: 'normal',
      expected_due_date: '',
      description: '',
      notes: '',
      tracking_number: '',
      requester_id: user?.user_id || '',
    });
    setShowCreateModal(true);
  };

  const handleCloseCreate = () => {
    setShowCreateModal(false);
  };

  const handleCreateFormChange = (e) => {
    const { name, value } = e.target;
    setCreateForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmitCreate = async (e) => {
    e.preventDefault();
    try {
      await dispatch(createOrder(createForm)).unwrap();
      toast.success('Order created successfully!');
      handleCloseCreate();
      dispatch(fetchOrders());
    } catch (error) {
      toast.error(error.message || 'Failed to create order');
    }
  };

  const handleViewOrder = async (order) => {
    try {
      await dispatch(fetchOrderById({ orderId: order.id, includeMessages: true })).unwrap();
      setShowDetailModal(true);
    } catch (error) {
      toast.error(error.message || 'Failed to load order details');
    }
  };

  const handleCloseDetail = () => {
    setShowDetailModal(false);
  };

  const handleDetailFormChange = (e) => {
    const { name, value } = e.target;
    setDetailForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmitUpdate = async (e) => {
    e.preventDefault();
    try {
      // Convert date-only string to ISO 8601 datetime format with timezone
      const orderData = { ...detailForm };
      if (orderData.expected_due_date) {
        // If it's a date-only string (YYYY-MM-DD), convert to ISO datetime with UTC timezone
        if (orderData.expected_due_date.length === 10) {
          orderData.expected_due_date = `${orderData.expected_due_date}T00:00:00Z`;
        }
      }

      // Remove requester_id if it's empty to avoid validation errors
      if (!orderData.requester_id) {
        delete orderData.requester_id;
      }

      await dispatch(updateOrder({ orderId: detailForm.id, orderData })).unwrap();
      toast.success('Order updated successfully!');
      dispatch(fetchOrders());
      dispatch(fetchOrderById({ orderId: detailForm.id, includeMessages: true }));
      handleCloseDetail(); // Close the modal after successful save
    } catch (error) {
      toast.error(error.message || 'Failed to update order');
    }
  };

  const handleMessageFormChange = (e) => {
    const { name, value } = e.target;
    setMessageForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    try {
      await dispatch(sendOrderMessage({
        orderId: selectedOrder.id,
        ...messageForm,
      })).unwrap();
      toast.success('Message sent successfully!');
      setMessageForm({ subject: '', message: '', recipient_id: '' });
      dispatch(fetchOrderMessages(selectedOrder.id));
    } catch (error) {
      toast.error(error.message || 'Failed to send message');
    }
  };

  const handleReplyFormChange = (e) => {
    setReplyForm({ message: e.target.value });
  };

  const handleSendReply = async (messageId) => {
    try {
      await dispatch(replyToOrderMessage({
        orderId: selectedOrder.id,
        messageId,
        message: replyForm.message,
      })).unwrap();
      toast.success('Reply sent successfully!');
      setReplyForm({ message: '' });
      setActiveMessageId(null);
      dispatch(fetchOrderMessages(selectedOrder.id));
    } catch (error) {
      toast.error(error.message || 'Failed to send reply');
    }
  };

  const handleMarkMessageRead = async (messageId) => {
    try {
      await dispatch(markOrderMessageRead({
        orderId: selectedOrder.id,
        messageId,
      })).unwrap();
      dispatch(fetchOrderMessages(selectedOrder.id));
    } catch (error) {
      toast.error(error.message || 'Failed to mark message as read');
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">
            <FaClipboardList className="me-2" />
            Order Management Dashboard
          </h2>
          <p className="text-muted mb-0">Track and manage procurement orders</p>
        </div>
        <Button variant="primary" onClick={handleOpenCreate}>
          <FaPlus className="me-2" />
          Create Order
        </Button>
      </div>

      <Card>
        <Card.Body>
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-3"
          >
            <Tab eventKey="all-orders" title="All Orders">
              <AllOrdersTab onViewOrder={handleViewOrder} />
            </Tab>
            
            <Tab eventKey="chemicals-needing-reorder" title="Chemicals Needing Reorder">
              <ChemicalsNeedingReorderTab />
            </Tab>
            
            <Tab eventKey="chemicals-on-order" title="Chemicals On Order">
              <ChemicalsOnOrderTab />
            </Tab>
            
            <Tab eventKey="analytics" title="Analytics">
              <AnalyticsTab />
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      {/* Create Order Modal */}
      <Modal show={showCreateModal} onHide={handleCloseCreate} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Create New Order</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmitCreate}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Title <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    name="title"
                    value={createForm.title}
                    onChange={handleCreateFormChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Part Number</Form.Label>
                  <Form.Control
                    type="text"
                    name="part_number"
                    value={createForm.part_number}
                    onChange={handleCreateFormChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Order Type <span className="text-danger">*</span></Form.Label>
                  <Form.Select
                    name="order_type"
                    value={createForm.order_type}
                    onChange={handleCreateFormChange}
                    required
                  >
                    {ORDER_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Priority <span className="text-danger">*</span></Form.Label>
                  <Form.Select
                    name="priority"
                    value={createForm.priority}
                    onChange={handleCreateFormChange}
                    required
                  >
                    {PRIORITIES.map((priority) => (
                      <option key={priority.value} value={priority.value}>{priority.label}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Expected Delivery Date</Form.Label>
                  <Form.Control
                    type="date"
                    name="expected_due_date"
                    value={createForm.expected_due_date}
                    onChange={handleCreateFormChange}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tracking Number</Form.Label>
                  <Form.Control
                    type="text"
                    name="tracking_number"
                    value={createForm.tracking_number}
                    onChange={handleCreateFormChange}
                  />
                </Form.Group>
              </Col>
              <Col md={12}>
                <Form.Group className="mb-3">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="description"
                    value={createForm.description}
                    onChange={handleCreateFormChange}
                  />
                </Form.Group>
              </Col>
              <Col md={12}>
                <Form.Group className="mb-3">
                  <Form.Label>Notes</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    name="notes"
                    value={createForm.notes}
                    onChange={handleCreateFormChange}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseCreate}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              <FaPlus className="me-1" />
              Create Order
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Order Detail Modal */}
      <OrderDetailModal
        show={showDetailModal}
        onHide={handleCloseDetail}
        order={selectedOrder}
        detailForm={detailForm}
        onDetailFormChange={handleDetailFormChange}
        onSubmitUpdate={handleSubmitUpdate}
        messages={orderMessages}
        messageForm={messageForm}
        onMessageFormChange={handleMessageFormChange}
        onSendMessage={handleSendMessage}
        replyForm={replyForm}
        onReplyFormChange={handleReplyFormChange}
        onSendReply={handleSendReply}
        activeMessageId={activeMessageId}
        setActiveMessageId={setActiveMessageId}
        onMarkMessageRead={handleMarkMessageRead}
        users={users}
        messageActionLoading={messageActionLoading}
      />
    </div>
  );
};

export default OrderManagementPage;

