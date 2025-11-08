import { useState } from 'react';
import { Modal, Form, Button, Row, Col, Badge, ListGroup, Tabs, Tab, Alert } from 'react-bootstrap';
import { FaSave, FaEnvelope, FaReply } from 'react-icons/fa';
import { formatDate, formatDateTime } from '../../utils/dateUtils';

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

const OrderDetailModal = ({
  show,
  onHide,
  order,
  detailForm,
  onDetailFormChange,
  onSubmitUpdate,
  messages,
  messageForm,
  onMessageFormChange,
  onSendMessage,
  replyForm,
  onReplyFormChange,
  onSendReply,
  activeMessageId,
  setActiveMessageId,
  onMarkMessageRead,
  users,
  messageActionLoading,
}) => {
  const [activeTab, setActiveTab] = useState('details');

  if (!order || !detailForm) return null;

  return (
    <Modal show={show} onHide={onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Order Details - {order.title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-3">
          {/* Details Tab */}
          <Tab eventKey="details" title="Details">
            <Form onSubmit={onSubmitUpdate}>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Title <span className="text-danger">*</span></Form.Label>
                    <Form.Control
                      type="text"
                      name="title"
                      value={detailForm.title}
                      onChange={onDetailFormChange}
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
                      value={detailForm.part_number}
                      onChange={onDetailFormChange}
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Order Type</Form.Label>
                    <Form.Select
                      name="order_type"
                      value={detailForm.order_type}
                      onChange={onDetailFormChange}
                    >
                      {ORDER_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Status</Form.Label>
                    <Form.Select
                      name="status"
                      value={detailForm.status}
                      onChange={onDetailFormChange}
                    >
                      {ORDER_STATUSES.map((status) => (
                        <option key={status.value} value={status.value}>{status.label}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Priority</Form.Label>
                    <Form.Select
                      name="priority"
                      value={detailForm.priority}
                      onChange={onDetailFormChange}
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
                      name="expected_delivery_date"
                      value={detailForm.expected_delivery_date}
                      onChange={onDetailFormChange}
                    />
                  </Form.Group>
                </Col>
                <Col md={12}>
                  <Form.Group className="mb-3">
                    <Form.Label>Tracking Number</Form.Label>
                    <Form.Control
                      type="text"
                      name="tracking_number"
                      value={detailForm.tracking_number}
                      onChange={onDetailFormChange}
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
                      value={detailForm.description}
                      onChange={onDetailFormChange}
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
                      value={detailForm.notes}
                      onChange={onDetailFormChange}
                    />
                  </Form.Group>
                </Col>
              </Row>
              <div className="d-flex justify-content-end">
                <Button variant="primary" type="submit">
                  <FaSave className="me-1" />
                  Save Changes
                </Button>
              </div>
            </Form>

            {/* Order Info */}
            <hr className="my-4" />
            <Row>
              <Col md={6}>
                <p><strong>Created:</strong> {formatDateTime(order.created_at)}</p>
                <p><strong>Requested By:</strong> {order.requested_by_name || 'N/A'}</p>
              </Col>
              <Col md={6}>
                <p><strong>Days Open:</strong> {order.days_open || 0}</p>
                {order.days_overdue > 0 && (
                  <p className="text-danger"><strong>Days Overdue:</strong> {order.days_overdue}</p>
                )}
              </Col>
            </Row>
          </Tab>

          {/* Messages Tab */}
          <Tab eventKey="messages" title={`Messages (${messages.length})`}>
            <div className="mb-4">
              <h5><FaEnvelope className="me-2" />Send New Message</h5>
              <Form onSubmit={onSendMessage}>
                <Form.Group className="mb-3">
                  <Form.Label>Recipient</Form.Label>
                  <Form.Select
                    name="recipient_id"
                    value={messageForm.recipient_id}
                    onChange={onMessageFormChange}
                    required
                  >
                    <option value="">Select recipient...</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id}>{u.user_name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Subject</Form.Label>
                  <Form.Control
                    type="text"
                    name="subject"
                    value={messageForm.subject}
                    onChange={onMessageFormChange}
                    required
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Message</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="message"
                    value={messageForm.message}
                    onChange={onMessageFormChange}
                    required
                  />
                </Form.Group>
                <Button variant="primary" type="submit" disabled={messageActionLoading}>
                  <FaEnvelope className="me-1" />
                  Send Message
                </Button>
              </Form>
            </div>

            <hr />

            <h5 className="mb-3">Message Thread</h5>
            {messages.length === 0 ? (
              <Alert variant="info">No messages yet for this order.</Alert>
            ) : (
              <ListGroup>
                {messages.map((msg) => (
                  <ListGroup.Item key={msg.id}>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <strong>{msg.sender_name}</strong>
                        <Badge bg="secondary" className="ms-2">To: {msg.recipient_name}</Badge>
                        {!msg.is_read && <Badge bg="primary" className="ms-2">Unread</Badge>}
                      </div>
                      <small className="text-muted">{formatDateTime(msg.created_at)}</small>
                    </div>
                    <p className="mb-1"><strong>{msg.subject}</strong></p>
                    <p className="mb-2">{msg.message}</p>
                    
                    {!msg.is_read && (
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => onMarkMessageRead(msg.id)}
                        disabled={messageActionLoading}
                      >
                        Mark as Read
                      </Button>
                    )}
                    
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      className="ms-2"
                      onClick={() => setActiveMessageId(activeMessageId === msg.id ? null : msg.id)}
                    >
                      <FaReply className="me-1" />
                      Reply
                    </Button>

                    {activeMessageId === msg.id && (
                      <Form className="mt-3" onSubmit={(e) => { e.preventDefault(); onSendReply(msg.id); }}>
                        <Form.Group>
                          <Form.Control
                            as="textarea"
                            rows={2}
                            placeholder="Type your reply..."
                            value={replyForm.message}
                            onChange={onReplyFormChange}
                            required
                          />
                        </Form.Group>
                        <div className="mt-2">
                          <Button variant="primary" size="sm" type="submit" disabled={messageActionLoading}>
                            Send Reply
                          </Button>
                          <Button
                            variant="secondary"
                            size="sm"
                            className="ms-2"
                            onClick={() => setActiveMessageId(null)}
                          >
                            Cancel
                          </Button>
                        </div>
                      </Form>
                    )}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}
          </Tab>
        </Tabs>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default OrderDetailModal;

