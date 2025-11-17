import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Badge,
  Button,
  Card,
  Form,
  ListGroup,
  Modal,
  Spinner,
  Table,
  Row,
  Col,
  Alert,
} from 'react-bootstrap';
import { FaEdit, FaEnvelope, FaTruck, FaCheckCircle, FaBoxOpen, FaUser, FaCalendarAlt } from 'react-icons/fa';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'react-toastify';
import {
  fetchUserRequests,
  updateUserRequest,
  markItemsOrdered,
  markItemsReceived,
  sendRequestMessage,
  fetchRequestMessages,
} from '../../store/userRequestsSlice';

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
  new: 'primary',
  awaiting_info: 'warning',
  in_progress: 'info',
  partially_ordered: 'info',
  ordered: 'success',
  partially_received: 'info',
  received: 'success',
  cancelled: 'secondary',
  pending: 'warning',
  shipped: 'info',
};

const formatStatusLabel = (status) => {
  if (!status) return 'Unknown';
  return status
    .replace(/_/g, ' ')
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
};

const UserRequestsManagementTab = () => {
  const dispatch = useDispatch();
  const { list, loading } = useSelector((state) => state.userRequests);
  const { user } = useSelector((state) => state.auth);

  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showFulfillmentModal, setShowFulfillmentModal] = useState(false);
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [itemUpdates, setItemUpdates] = useState({});
  const [messageSubject, setMessageSubject] = useState('');
  const [messageText, setMessageText] = useState('');
  const [messages, setMessages] = useState([]);
  const [statusFilter, setStatusFilter] = useState('open');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [assignmentFilter, setAssignmentFilter] = useState('all');

  useEffect(() => {
    dispatch(fetchUserRequests()).catch(() => {});
  }, [dispatch]);

  const filteredRequests = list.filter((req) => {
    // Status filter
    if (statusFilter === 'open' && ['received', 'cancelled'].includes(req.status)) {
      return false;
    }
    if (statusFilter === 'closed' && !['received', 'cancelled'].includes(req.status)) {
      return false;
    }
    if (statusFilter === 'new' && req.status !== 'new') {
      return false;
    }
    if (statusFilter === 'in_progress' && !['in_progress', 'partially_ordered', 'ordered', 'partially_received'].includes(req.status)) {
      return false;
    }

    // Priority filter
    if (priorityFilter && req.priority !== priorityFilter) {
      return false;
    }

    // Assignment filter
    if (assignmentFilter === 'mine' && req.buyer_id !== user?.id) {
      return false;
    }
    if (assignmentFilter === 'unassigned' && req.buyer_id) {
      return false;
    }

    return true;
  });

  const handleOpenFulfillment = (request) => {
    setSelectedRequest(request);
    // Initialize item updates
    const updates = {};
    request.items?.forEach((item) => {
      updates[item.id] = {
        vendor: item.vendor || '',
        tracking_number: item.tracking_number || '',
        expected_delivery_date: item.expected_delivery_date ? item.expected_delivery_date.substring(0, 10) : '',
        unit_cost: item.unit_cost || '',
        order_notes: item.order_notes || '',
        selected: item.status === 'pending',
      };
    });
    setItemUpdates(updates);
    setShowFulfillmentModal(true);
  };

  const handleItemUpdateChange = (itemId, field, value) => {
    setItemUpdates((prev) => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value,
      },
    }));
  };

  const handleAssignToMe = async () => {
    if (!selectedRequest) return;

    try {
      await dispatch(updateUserRequest({
        requestId: selectedRequest.id,
        requestData: { buyer_id: user?.id },
      })).unwrap();
      toast.success('Request assigned to you.');
      setSelectedRequest({ ...selectedRequest, buyer_id: user?.id, buyer_name: user?.name });
      dispatch(fetchUserRequests()).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to assign request.');
    }
  };

  const handleMarkItemsOrdered = async () => {
    const selectedItems = Object.entries(itemUpdates)
      .filter(([, data]) => data.selected)
      .map(([itemId, data]) => ({
        item_id: parseInt(itemId, 10),
        vendor: data.vendor,
        tracking_number: data.tracking_number,
        expected_delivery_date: data.expected_delivery_date || undefined,
        unit_cost: data.unit_cost ? parseFloat(data.unit_cost) : undefined,
        order_notes: data.order_notes,
      }));

    if (selectedItems.length === 0) {
      toast.warning('Please select at least one item to mark as ordered.');
      return;
    }

    // Validate that all selected items have at least a vendor
    const missingVendor = selectedItems.find((item) => !item.vendor);
    if (missingVendor) {
      toast.warning('Please provide vendor information for all selected items.');
      return;
    }

    try {
      await dispatch(markItemsOrdered({
        requestId: selectedRequest.id,
        items: selectedItems,
      })).unwrap();
      toast.success(`${selectedItems.length} item(s) marked as ordered.`);
      setShowFulfillmentModal(false);
      dispatch(fetchUserRequests()).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to mark items as ordered.');
    }
  };

  const handleMarkItemsReceived = async (itemIds) => {
    try {
      await dispatch(markItemsReceived({
        requestId: selectedRequest.id,
        itemIds,
      })).unwrap();
      toast.success('Item(s) marked as received.');
      dispatch(fetchUserRequests()).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to mark items as received.');
    }
  };

  const handleNeedsMoreInfo = async () => {
    try {
      await dispatch(updateUserRequest({
        requestId: selectedRequest.id,
        requestData: {
          needs_more_info: true,
          status: 'awaiting_info',
        },
      })).unwrap();
      toast.success('Request marked as needing more information.');
      setShowFulfillmentModal(false);
      dispatch(fetchUserRequests()).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to update request.');
    }
  };

  const handleOpenMessages = async (request) => {
    setSelectedRequest(request);
    setShowMessageModal(true);
    try {
      const result = await dispatch(fetchRequestMessages(request.id)).unwrap();
      setMessages(result.messages || []);
    } catch {
      toast.error('Failed to load messages.');
      setMessages([]);
    }
  };

  const handleSendMessage = async () => {
    if (!messageSubject.trim() || !messageText.trim()) {
      toast.error('Please provide both subject and message.');
      return;
    }

    try {
      const result = await dispatch(sendRequestMessage({
        requestId: selectedRequest.id,
        messageData: {
          subject: messageSubject.trim(),
          message: messageText.trim(),
        },
      })).unwrap();
      setMessages([result.message, ...messages]);
      setMessageSubject('');
      setMessageText('');
      toast.success('Message sent to requester.');
      dispatch(fetchUserRequests()).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to send message.');
    }
  };

  return (
    <div>
      {/* Filters */}
      <Card className="mb-4">
        <Card.Body>
          <Row className="g-3">
            <Col md={3}>
              <Form.Group>
                <Form.Label>Status</Form.Label>
                <Form.Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                  <option value="all">All Requests</option>
                  <option value="open">Open Requests</option>
                  <option value="new">New Requests</option>
                  <option value="in_progress">In Progress</option>
                  <option value="closed">Closed</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label>Priority</Form.Label>
                <Form.Select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
                  <option value="">All Priorities</option>
                  {PRIORITIES.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group>
                <Form.Label>Assignment</Form.Label>
                <Form.Select value={assignmentFilter} onChange={(e) => setAssignmentFilter(e.target.value)}>
                  <option value="all">All</option>
                  <option value="mine">Assigned to Me</option>
                  <option value="unassigned">Unassigned</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3} className="d-flex align-items-end">
              <Button
                variant="outline-secondary"
                onClick={() => dispatch(fetchUserRequests()).catch(() => {})}
                disabled={loading}
              >
                {loading ? <Spinner size="sm" /> : 'Refresh'}
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Requests List */}
      {loading ? (
        <div className="text-center py-5">
          <Spinner animation="border" />
        </div>
      ) : filteredRequests.length === 0 ? (
        <Alert variant="info">No requests match the selected filters.</Alert>
      ) : (
        <ListGroup>
          {filteredRequests.map((req) => (
            <ListGroup.Item key={req.id} className="py-3">
              <div className="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <h5 className="mb-1">
                    {req.request_number && (
                      <Badge bg="dark" className="me-2">{req.request_number}</Badge>
                    )}
                    {req.title}
                  </h5>
                  <div className="text-muted small">
                    <FaUser className="me-1" />
                    {req.requester_name || 'Unknown'} |{' '}
                    <FaCalendarAlt className="me-1" />
                    {req.created_at ? formatDistanceToNow(new Date(req.created_at), { addSuffix: true }) : 'N/A'} |{' '}
                    {req.item_count} item{req.item_count !== 1 ? 's' : ''}
                  </div>
                  {req.expected_due_date && (
                    <div className="small text-muted">
                      Needed by: {new Date(req.expected_due_date).toLocaleDateString()}
                      {req.is_late && <Badge bg="danger" className="ms-2">LATE</Badge>}
                    </div>
                  )}
                  {req.buyer_name && (
                    <div className="small text-info">
                      Assigned to: {req.buyer_name}
                    </div>
                  )}
                </div>
                <div className="d-flex flex-wrap gap-2">
                  <Badge bg={PRIORITY_VARIANTS[req.priority] || 'secondary'}>
                    {PRIORITIES.find((p) => p.value === req.priority)?.label || req.priority}
                  </Badge>
                  <Badge bg={STATUS_VARIANTS[req.status] || 'secondary'}>
                    {formatStatusLabel(req.status)}
                  </Badge>
                  {req.needs_more_info && (
                    <Badge bg="warning">Needs Info</Badge>
                  )}
                </div>
              </div>

              {req.description && (
                <div className="small mb-2">
                  <strong>Description:</strong> {req.description}
                </div>
              )}

              {/* Items Summary Table */}
              {req.items && req.items.length > 0 && (
                <Table size="sm" bordered className="mb-2">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Description</th>
                      <th>Qty</th>
                      <th>Status</th>
                      <th>Vendor</th>
                      <th>Tracking</th>
                    </tr>
                  </thead>
                  <tbody>
                    {req.items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.item_type}</td>
                        <td className="text-truncate" style={{ maxWidth: '200px' }}>
                          {item.description}
                        </td>
                        <td>{item.quantity} {item.unit}</td>
                        <td>
                          <Badge bg={STATUS_VARIANTS[item.status] || 'secondary'} size="sm">
                            {formatStatusLabel(item.status)}
                          </Badge>
                        </td>
                        <td>{item.vendor || '-'}</td>
                        <td>
                          {item.tracking_number ? (
                            <span className="text-info small">
                              <FaTruck className="me-1" />
                              {item.tracking_number}
                            </span>
                          ) : (
                            '-'
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}

              <div className="d-flex gap-2">
                <Button size="sm" variant="primary" onClick={() => handleOpenFulfillment(req)}>
                  <FaEdit className="me-1" />
                  Manage Order
                </Button>
                <Button size="sm" variant="outline-info" onClick={() => handleOpenMessages(req)}>
                  <FaEnvelope className="me-1" />
                  Messages {req.message_count > 0 && `(${req.message_count})`}
                </Button>
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}

      {/* Fulfillment Modal */}
      <Modal show={showFulfillmentModal} onHide={() => setShowFulfillmentModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>Manage Order: {selectedRequest?.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedRequest && (
            <>
              <Card className="mb-3">
                <Card.Body>
                  <Row>
                    <Col md={4}>
                      <strong>Requester:</strong> {selectedRequest.requester_name}
                    </Col>
                    <Col md={4}>
                      <strong>Priority:</strong>{' '}
                      <Badge bg={PRIORITY_VARIANTS[selectedRequest.priority]}>
                        {PRIORITIES.find((p) => p.value === selectedRequest.priority)?.label}
                      </Badge>
                    </Col>
                    <Col md={4}>
                      <strong>Status:</strong>{' '}
                      <Badge bg={STATUS_VARIANTS[selectedRequest.status]}>
                        {formatStatusLabel(selectedRequest.status)}
                      </Badge>
                    </Col>
                  </Row>
                  {selectedRequest.expected_due_date && (
                    <div className="mt-2">
                      <strong>Needed by:</strong> {new Date(selectedRequest.expected_due_date).toLocaleDateString()}
                    </div>
                  )}
                  {selectedRequest.description && (
                    <div className="mt-2">
                      <strong>Description:</strong> {selectedRequest.description}
                    </div>
                  )}
                  {selectedRequest.notes && (
                    <div className="mt-2">
                      <strong>Notes:</strong> {selectedRequest.notes}
                    </div>
                  )}

                  {!selectedRequest.buyer_id && (
                    <div className="mt-3">
                      <Button variant="success" onClick={handleAssignToMe}>
                        <FaUser className="me-1" />
                        Assign to Me
                      </Button>
                    </div>
                  )}
                </Card.Body>
              </Card>

              <h5 className="mb-3">Line Items</h5>
              {selectedRequest.items?.map((item) => (
                <Card key={item.id} className="mb-3">
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    <div>
                      <Form.Check
                        type="checkbox"
                        label={<strong>{item.description}</strong>}
                        checked={itemUpdates[item.id]?.selected || false}
                        onChange={(e) => handleItemUpdateChange(item.id, 'selected', e.target.checked)}
                        disabled={item.status !== 'pending'}
                      />
                    </div>
                    <Badge bg={STATUS_VARIANTS[item.status]}>
                      {formatStatusLabel(item.status)}
                    </Badge>
                  </Card.Header>
                  <Card.Body>
                    <Row className="g-3 mb-3">
                      <Col md={3}>
                        <strong>Type:</strong> {item.item_type}
                      </Col>
                      <Col md={3}>
                        <strong>Part #:</strong> {item.part_number || 'N/A'}
                      </Col>
                      <Col md={3}>
                        <strong>Quantity:</strong> {item.quantity} {item.unit}
                      </Col>
                      <Col md={3}>
                        {item.status === 'ordered' && (
                          <Button
                            size="sm"
                            variant="success"
                            onClick={() => handleMarkItemsReceived([item.id])}
                          >
                            <FaCheckCircle className="me-1" />
                            Mark Received
                          </Button>
                        )}
                      </Col>
                    </Row>

                    {item.status === 'pending' && (
                      <Row className="g-3">
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label>Vendor <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                              type="text"
                              value={itemUpdates[item.id]?.vendor || ''}
                              onChange={(e) => handleItemUpdateChange(item.id, 'vendor', e.target.value)}
                              placeholder="Vendor name"
                            />
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label>Tracking Number</Form.Label>
                            <Form.Control
                              type="text"
                              value={itemUpdates[item.id]?.tracking_number || ''}
                              onChange={(e) => handleItemUpdateChange(item.id, 'tracking_number', e.target.value)}
                              placeholder="Tracking #"
                            />
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label>Expected Delivery</Form.Label>
                            <Form.Control
                              type="date"
                              value={itemUpdates[item.id]?.expected_delivery_date || ''}
                              onChange={(e) => handleItemUpdateChange(item.id, 'expected_delivery_date', e.target.value)}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label>Unit Cost</Form.Label>
                            <Form.Control
                              type="number"
                              step="0.01"
                              value={itemUpdates[item.id]?.unit_cost || ''}
                              onChange={(e) => handleItemUpdateChange(item.id, 'unit_cost', e.target.value)}
                              placeholder="$0.00"
                            />
                          </Form.Group>
                        </Col>
                        <Col md={8}>
                          <Form.Group>
                            <Form.Label>Order Notes</Form.Label>
                            <Form.Control
                              type="text"
                              value={itemUpdates[item.id]?.order_notes || ''}
                              onChange={(e) => handleItemUpdateChange(item.id, 'order_notes', e.target.value)}
                              placeholder="PO number, order confirmation, etc."
                            />
                          </Form.Group>
                        </Col>
                      </Row>
                    )}

                    {item.status !== 'pending' && item.vendor && (
                      <Row className="g-3">
                        <Col md={3}>
                          <strong>Vendor:</strong> {item.vendor}
                        </Col>
                        <Col md={3}>
                          <strong>Tracking:</strong> {item.tracking_number || 'N/A'}
                        </Col>
                        <Col md={3}>
                          <strong>Ordered:</strong>{' '}
                          {item.ordered_date ? new Date(item.ordered_date).toLocaleDateString() : 'N/A'}
                        </Col>
                        <Col md={3}>
                          <strong>Expected:</strong>{' '}
                          {item.expected_delivery_date
                            ? new Date(item.expected_delivery_date).toLocaleDateString()
                            : 'N/A'}
                        </Col>
                      </Row>
                    )}
                  </Card.Body>
                </Card>
              ))}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="warning" onClick={handleNeedsMoreInfo}>
            Request More Info
          </Button>
          <Button variant="secondary" onClick={() => setShowFulfillmentModal(false)}>
            Close
          </Button>
          <Button variant="primary" onClick={handleMarkItemsOrdered}>
            <FaBoxOpen className="me-1" />
            Mark Selected as Ordered
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Messages Modal */}
      <Modal show={showMessageModal} onHide={() => setShowMessageModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Messages for: {selectedRequest?.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Card className="mb-3">
            <Card.Header>Send Message to Requester</Card.Header>
            <Card.Body>
              <Form.Group className="mb-2">
                <Form.Label>Subject</Form.Label>
                <Form.Control
                  type="text"
                  value={messageSubject}
                  onChange={(e) => setMessageSubject(e.target.value)}
                  placeholder="Message subject"
                />
              </Form.Group>
              <Form.Group className="mb-2">
                <Form.Label>Message</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  placeholder="Your message..."
                />
              </Form.Group>
              <Button variant="primary" size="sm" onClick={handleSendMessage}>
                Send Message
              </Button>
            </Card.Body>
          </Card>

          <h6>Message History</h6>
          {messages.length === 0 ? (
            <div className="text-muted">No messages yet.</div>
          ) : (
            <ListGroup>
              {messages.map((msg) => (
                <ListGroup.Item key={msg.id}>
                  <div className="d-flex justify-content-between">
                    <strong>{msg.subject}</strong>
                    <small className="text-muted">
                      {msg.sent_date ? new Date(msg.sent_date).toLocaleString() : ''}
                    </small>
                  </div>
                  <div className="small text-muted mb-1">
                    From: {msg.sender_name} | To: {msg.recipient_name}
                  </div>
                  <div>{msg.message}</div>
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowMessageModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default UserRequestsManagementTab;
