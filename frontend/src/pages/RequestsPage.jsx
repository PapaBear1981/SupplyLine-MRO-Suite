import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Badge,
  Button,
  Card,
  Col,
  Form,
  ListGroup,
  Row,
  Spinner,
  Tabs,
  Tab,
  Alert,
} from 'react-bootstrap';
import { FaClipboardList, FaPaperPlane, FaPlusCircle, FaPaperclip, FaInfoCircle, FaCheckCircle, FaEdit, FaTimes } from 'react-icons/fa';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'react-toastify';
import { createOrder, fetchOrders, updateOrder } from '../store/ordersSlice';

const ORDER_TYPES = [
  { value: 'tool', label: 'Tool' },
  { value: 'chemical', label: 'Chemical' },
  { value: 'expendable', label: 'Expendable' },
  { value: 'kit', label: 'Kit Component' },
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

const getOrderTypeLabel = (orderType) => {
  const match = ORDER_TYPES.find((option) => option.value === orderType);
  if (match) {
    return match.label;
  }

  if (!orderType) {
    return 'Other';
  }

  return orderType.charAt(0).toUpperCase() + orderType.slice(1);
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

const formatStatusLabel = (status) => {
  if (!status) {
    return 'Unknown';
  }

  return status
    .replace(/_/g, ' ')
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
};

const INITIAL_FORM_STATE = {
  title: '',
  order_type: 'tool',
  part_number: '',
  quantity: '',
  unit: '',
  priority: 'normal',
  expected_due_date: '',
  description: '',
  notes: '',
};

const RequestsPage = () => {
  const dispatch = useDispatch();
  const { list, loading } = useSelector((state) => state.orders);
  const { user } = useSelector((state) => state.auth);

  const [activeTab, setActiveTab] = useState('submit');
  const [formState, setFormState] = useState(INITIAL_FORM_STATE);
  const [submitting, setSubmitting] = useState(false);
  const [documentationFile, setDocumentationFile] = useState(null);
  const [editingRequest, setEditingRequest] = useState(null);
  const [editFormState, setEditFormState] = useState(null);


  useEffect(() => {
    dispatch(fetchOrders({ sort: 'created', limit: 50 })).catch(() => {});
  }, [dispatch]);

  const myRequests = useMemo(() => {
    if (!user) return [];
    const mine = list.filter((order) => order.requester_id === user.id);
    return mine
      .slice()
      .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
  }, [list, user]);

  const openRequests = useMemo(
    () => myRequests.filter((order) => !['received', 'cancelled'].includes(order.status)).length,
    [myRequests],
  );

  const completedRequests = useMemo(
    () => myRequests.filter((order) => ['received'].includes(order.status)).length,
    [myRequests],
  );

  const awaitingInfoRequests = useMemo(
    () => myRequests.filter((order) => order.status === 'awaiting_info').length,
    [myRequests],
  );

  const needsAttentionRequests = useMemo(
    () => myRequests.filter((order) => order.needs_more_info),
    [myRequests],
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((previous) => ({ ...previous, [name]: value }));
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    setDocumentationFile(file);
  };

  const resetForm = () => {
    setFormState(INITIAL_FORM_STATE);
    setDocumentationFile(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!formState.title.trim()) {
      toast.error('Please provide a title for your request.');
      return;
    }

    const payload = {
      ...formState,
      requester_id: user?.id,
      quantity: formState.quantity ? Number(formState.quantity) : undefined,
      documentation: documentationFile || undefined,
    };

    if (payload.quantity !== undefined && (Number.isNaN(payload.quantity) || payload.quantity <= 0)) {
      toast.error('Quantity must be a positive number.');
      return;
    }

    setSubmitting(true);
    try {
      await dispatch(createOrder(payload)).unwrap();
      toast.success('Request submitted successfully.');
      resetForm();
      dispatch(fetchOrders({ sort: 'created', limit: 50 })).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Unable to submit request.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditRequest = (request) => {
    setEditingRequest(request.id);
    setEditFormState({
      description: request.description || '',
      notes: request.notes || '',
    });
  };

  const handleEditFormChange = (e) => {
    const { name, value } = e.target;
    setEditFormState((prev) => ({ ...prev, [name]: value }));
  };

  const handleSaveEdit = async (requestId) => {
    try {
      await dispatch(updateOrder({
        orderId: requestId,
        orderData: editFormState,
      })).unwrap();
      toast.success('Request updated successfully.');
      setEditingRequest(null);
      setEditFormState(null);
      dispatch(fetchOrders({ sort: 'created', limit: 50 })).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to update request.');
    }
  };

  const handleCancelEdit = () => {
    setEditingRequest(null);
    setEditFormState(null);
  };

  const handleResolveNeedsInfo = async (requestId) => {
    try {
      await dispatch(updateOrder({
        orderId: requestId,
        orderData: { needs_more_info: false },
      })).unwrap();
      toast.success('Request marked as resolved.');
      dispatch(fetchOrders({ sort: 'created', limit: 50 })).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to update request.');
    }
  };

  const handleCancelRequest = async (requestId) => {
    if (!window.confirm('Are you sure you want to cancel this request?')) {
      return;
    }
    try {
      await dispatch(updateOrder({
        orderId: requestId,
        orderData: { status: 'cancelled' },
      })).unwrap();
      toast.success('Request cancelled successfully.');
      dispatch(fetchOrders({ sort: 'created', limit: 50 })).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to cancel request.');
    }
  };

  return (
    <div className="requests-page">
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h1 className="mb-1 d-flex align-items-center gap-2">
            <FaClipboardList />
            Procurement Requests
          </h1>
          <p className="text-muted mb-0">
            Submit requests for tools, chemicals, expendables, or other materials that need to be ordered.
          </p>
        </div>
      </div>

      <Row className="g-4 mb-4">
        <Col md={3}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center gap-3 mb-3">
                <FaPlusCircle className="text-primary" size={28} />
                <div>
                  <h5 className="mb-0">Open Requests</h5>
                  <small className="text-muted">Awaiting processing or fulfillment</small>
                </div>
              </div>
              <h2 className="display-6 fw-bold mb-0">{openRequests}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="h-100 shadow-sm border-warning" style={{ cursor: 'pointer' }} onClick={() => setActiveTab('attention')}>
            <Card.Body>
              <div className="d-flex align-items-center gap-3 mb-3">
                <FaInfoCircle className="text-warning" size={28} />
                <div>
                  <h5 className="mb-0">Needs Attention</h5>
                  <small className="text-muted">Requests needing more info</small>
                </div>
              </div>
              <h2 className="display-6 fw-bold mb-0 text-warning">{needsAttentionRequests.length}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center gap-3 mb-3">
                <FaPaperPlane className="text-info" size={28} />
                <div>
                  <h5 className="mb-0">Awaiting Info</h5>
                  <small className="text-muted">Requests awaiting status update</small>
                </div>
              </div>
              <h2 className="display-6 fw-bold mb-0">{awaitingInfoRequests}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center gap-3 mb-3">
                <FaClipboardList className="text-success" size={28} />
                <div>
                  <h5 className="mb-0">Completed</h5>
                  <small className="text-muted">Delivered or picked up</small>
                </div>
              </div>
              <h2 className="display-6 fw-bold mb-0">{completedRequests}</h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Body>
          <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-3">
            {/* Submit Request Tab */}
            <Tab eventKey="submit" title="Submit Request">
              <Row className="g-4">
                <Col lg={8} className="mx-auto">
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Title <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    name="title"
                    value={formState.title}
                    onChange={handleChange}
                    placeholder="What do you need to order?"
                    required
                  />
                </Form.Group>

                <Row className="g-3">
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>Order Type</Form.Label>
                      <Form.Select name="order_type" value={formState.order_type} onChange={handleChange}>
                        {ORDER_TYPES.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>Priority</Form.Label>
                      <Form.Select name="priority" value={formState.priority} onChange={handleChange}>
                        {PRIORITIES.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>

                <Row className="g-3 mt-1">
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>Part Number</Form.Label>
                      <Form.Control
                        type="text"
                        name="part_number"
                        value={formState.part_number}
                        onChange={handleChange}
                        placeholder="Optional reference number"
                      />
                    </Form.Group>
                  </Col>
                  <Col md={3}>
                    <Form.Group>
                      <Form.Label>Quantity</Form.Label>
                      <Form.Control
                        type="number"
                        min="1"
                        name="quantity"
                        value={formState.quantity}
                        onChange={handleChange}
                        placeholder="e.g. 5"
                      />
                    </Form.Group>
                  </Col>
                  <Col md={3}>
                    <Form.Group>
                      <Form.Label>Unit</Form.Label>
                      <Form.Control
                        type="text"
                        name="unit"
                        value={formState.unit}
                        onChange={handleChange}
                        placeholder="Each, case, etc."
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Row className="g-3 mt-1">
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>Needed By</Form.Label>
                      <Form.Control
                        type="date"
                        name="expected_due_date"
                        value={formState.expected_due_date}
                        onChange={handleChange}
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <Form.Group className="mb-3 mt-3">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="description"
                    value={formState.description}
                    onChange={handleChange}
                    placeholder="Include details such as size, material, or specifications."
                  />
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Justification / Additional Notes</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={2}
                    name="notes"
                    value={formState.notes}
                    onChange={handleChange}
                    placeholder="Share why this item is needed or any special instructions."
                  />
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label className="d-flex align-items-center gap-2">
                    <FaPaperclip />
                    <span>Supporting Documentation</span>
                  </Form.Label>
                  <Form.Control
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.png,.jpg,.jpeg,.gif,.bmp,.txt,.rtf,.zip,.7z,.tar,.gz"
                  />
                  <Form.Text className="text-muted">
                    Not required, but highly recommended. Attach quotes, spec sheets, drawings, or approval emails to
                    help purchasing process your request faster.
                  </Form.Text>
                  {documentationFile && (
                    <div className="mt-2 small text-muted">
                      Selected file: <strong>{documentationFile.name}</strong>
                    </div>
                  )}
                </Form.Group>


                <div className="d-flex justify-content-end">
                  <Button type="submit" variant="primary" disabled={submitting}>
                    {submitting ? (
                      <>
                        <Spinner as="span" animation="border" size="sm" role="status" className="me-2" />
                        Submitting...
                      </>
                    ) : (
                      <>
                        <FaPaperPlane className="me-2" />
                        Submit Request
                      </>
                    )}
                  </Button>
                </div>
              </Form>
                </Col>
              </Row>
            </Tab>

            {/* My Requests Tab */}
            <Tab eventKey="requests" title={`My Requests (${myRequests.length})`}>
              {loading ? (
                <div className="text-center py-5">
                  <Spinner animation="border" />
                </div>
              ) : myRequests.length === 0 ? (
                <div className="text-center py-5 text-muted">
                  <p className="mb-1">No requests yet.</p>
                  <small>Submit your first request using the Submit Request tab.</small>
                </div>
              ) : (
                <ListGroup variant="flush" className="requests-list">
                  {myRequests.map((order) => (
                    <ListGroup.Item key={order.id} className="py-3">
                      {order.needs_more_info && (
                        <Alert variant="warning" className="mb-2">
                          <FaInfoCircle className="me-2" />
                          <strong>Attention Required:</strong> This request needs more information.
                        </Alert>
                      )}
                      <div className="d-flex flex-column flex-lg-row justify-content-between align-items-lg-start gap-3">
                        <div className="flex-grow-1">
                          <h6 className="mb-1">{order.title}</h6>
                          <div className="text-muted small">
                            Requested {order.created_at ? formatDistanceToNow(new Date(order.created_at), { addSuffix: true }) : 'N/A'}
                          </div>
                          {order.part_number && (
                            <div className="text-muted small">Part #: {order.part_number}</div>
                          )}
                          {order.expected_due_date && (
                            <div className="text-muted small">
                              Needed by {new Date(order.expected_due_date).toLocaleDateString()}
                            </div>
                          )}
                          {order.quantity && (
                            <div className="text-muted small">
                              Quantity: {order.quantity}
                              {order.unit ? ` ${order.unit}` : ''}
                            </div>
                          )}
                          {editingRequest === order.id ? (
                            <div className="mt-3">
                              <Form.Group className="mb-2">
                                <Form.Label>Description</Form.Label>
                                <Form.Control
                                  as="textarea"
                                  rows={2}
                                  name="description"
                                  value={editFormState.description}
                                  onChange={handleEditFormChange}
                                />
                              </Form.Group>
                              <Form.Group className="mb-2">
                                <Form.Label>Notes</Form.Label>
                                <Form.Control
                                  as="textarea"
                                  rows={2}
                                  name="notes"
                                  value={editFormState.notes}
                                  onChange={handleEditFormChange}
                                />
                              </Form.Group>
                              <div className="d-flex gap-2">
                                <Button size="sm" variant="primary" onClick={() => handleSaveEdit(order.id)}>
                                  <FaCheckCircle className="me-1" />
                                  Save
                                </Button>
                                <Button size="sm" variant="secondary" onClick={handleCancelEdit}>
                                  Cancel
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <>
                              {order.description && (
                                <div className="mt-2 small">
                                  <strong>Description:</strong> {order.description}
                                </div>
                              )}
                              {order.notes && (
                                <div className="mt-1 small">
                                  <strong>Notes:</strong> {order.notes}
                                </div>
                              )}
                            </>
                          )}
                        </div>
                        <div className="d-flex flex-column gap-2 align-items-end">
                          <div className="d-flex flex-wrap gap-2">
                            <Badge bg="light" text="dark">
                              Type: {getOrderTypeLabel(order.order_type)}
                            </Badge>
                            <Badge bg={PRIORITY_VARIANTS[order.priority] || 'secondary'}>
                              Priority: {PRIORITIES.find((item) => item.value === order.priority)?.label || order.priority}
                            </Badge>
                            <Badge bg={STATUS_VARIANTS[order.status] || 'secondary'}>
                              Status: {formatStatusLabel(order.status)}
                            </Badge>
                          </div>
                          {order.status !== 'cancelled' && order.status !== 'received' && editingRequest !== order.id && (
                            <div className="d-flex gap-2 flex-wrap">
                              <Button size="sm" variant="outline-primary" onClick={() => handleEditRequest(order)}>
                                <FaEdit className="me-1" />
                                Edit
                              </Button>
                              <Button size="sm" variant="outline-danger" onClick={() => handleCancelRequest(order.id)}>
                                <FaTimes className="me-1" />
                                Cancel
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Tab>

            {/* Needs Attention Tab */}
            <Tab eventKey="attention" title={
              <>
                Needs Attention
                {needsAttentionRequests.length > 0 && (
                  <Badge bg="warning" className="ms-2">{needsAttentionRequests.length}</Badge>
                )}
              </>
            }>
              {needsAttentionRequests.length === 0 ? (
                <div className="text-center py-5 text-muted">
                  <FaCheckCircle size={48} className="text-success mb-3" />
                  <p className="mb-1">All caught up!</p>
                  <small>No requests need attention at the moment.</small>
                </div>
              ) : (
                <>
                  <Alert variant="info" className="mb-3">
                    <FaInfoCircle className="me-2" />
                    The following requests need more information. Please provide additional details or clarification.
                  </Alert>
                  <ListGroup variant="flush">
                    {needsAttentionRequests.map((order) => (
                      <ListGroup.Item key={order.id} className="py-3">
                        <div className="d-flex flex-column gap-3">
                          <div className="d-flex justify-content-between align-items-start">
                            <div className="flex-grow-1">
                              <h6 className="mb-1">{order.title}</h6>
                              <div className="text-muted small">
                                Requested {order.created_at ? formatDistanceToNow(new Date(order.created_at), { addSuffix: true }) : 'N/A'}
                              </div>
                              {order.part_number && (
                                <div className="text-muted small">Part #: {order.part_number}</div>
                              )}
                              {editingRequest === order.id ? (
                                <div className="mt-3">
                                  <Form.Group className="mb-2">
                                    <Form.Label>Description</Form.Label>
                                    <Form.Control
                                      as="textarea"
                                      rows={3}
                                      name="description"
                                      value={editFormState.description}
                                      onChange={handleEditFormChange}
                                      placeholder="Add more details about what you need..."
                                    />
                                  </Form.Group>
                                  <Form.Group className="mb-3">
                                    <Form.Label>Notes</Form.Label>
                                    <Form.Control
                                      as="textarea"
                                      rows={2}
                                      name="notes"
                                      value={editFormState.notes}
                                      onChange={handleEditFormChange}
                                      placeholder="Add any additional notes or clarifications..."
                                    />
                                  </Form.Group>
                                  <div className="d-flex gap-2">
                                    <Button size="sm" variant="success" onClick={() => handleSaveEdit(order.id)}>
                                      <FaCheckCircle className="me-1" />
                                      Save & Mark Resolved
                                    </Button>
                                    <Button size="sm" variant="secondary" onClick={handleCancelEdit}>
                                      Cancel
                                    </Button>
                                  </div>
                                </div>
                              ) : (
                                <>
                                  {order.description && (
                                    <div className="mt-2 small">
                                      <strong>Description:</strong> {order.description}
                                    </div>
                                  )}
                                  {order.notes && (
                                    <div className="mt-1 small">
                                      <strong>Notes:</strong> {order.notes}
                                    </div>
                                  )}
                                </>
                              )}
                            </div>
                            <div className="d-flex flex-wrap gap-2">
                              <Badge bg={PRIORITY_VARIANTS[order.priority] || 'secondary'}>
                                {PRIORITIES.find((item) => item.value === order.priority)?.label || order.priority}
                              </Badge>
                              <Badge bg={STATUS_VARIANTS[order.status] || 'secondary'}>
                                {formatStatusLabel(order.status)}
                              </Badge>
                            </div>
                          </div>
                          {editingRequest !== order.id && (
                            <div className="d-flex gap-2">
                              <Button size="sm" variant="primary" onClick={() => handleEditRequest(order)}>
                                <FaEdit className="me-1" />
                                Add Information
                              </Button>
                              <Button size="sm" variant="outline-success" onClick={() => handleResolveNeedsInfo(order.id)}>
                                <FaCheckCircle className="me-1" />
                                Mark as Resolved
                              </Button>
                            </div>
                          )}
                        </div>
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                </>
              )}
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>
    </div>
  );
};

export default RequestsPage;
