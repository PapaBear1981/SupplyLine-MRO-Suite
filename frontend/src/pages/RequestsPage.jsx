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
  Table,
} from 'react-bootstrap';
import { FaClipboardList, FaPaperPlane, FaPlusCircle, FaInfoCircle, FaCheckCircle, FaEdit, FaTimes, FaSync, FaEnvelope, FaTrash, FaPlus, FaBoxes, FaTruck, FaFlask, FaSuitcase, FaBell } from 'react-icons/fa';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'react-toastify';
import {
  createUserRequest,
  fetchUserRequests,
  updateUserRequest,
  cancelUserRequest,
  fetchRequestMessages,
  sendRequestMessage,
} from '../store/userRequestsSlice';
import { fetchRequestAlerts, dismissAlert } from '../store/requestAlertsSlice';
import { PRIORITY_VARIANTS } from '../constants/orderConstants';

const ITEM_TYPES = [
  { value: 'tool', label: 'Tool' },
  { value: 'chemical', label: 'Chemical' },
  { value: 'expendable', label: 'Expendable' },
  { value: 'other', label: 'Other' },
];

const PRIORITIES = [
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'normal', label: 'Normal' },
  { value: 'low', label: 'Low' },
];

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

const getItemTypeLabel = (itemType) => {
  const match = ITEM_TYPES.find((option) => option.value === itemType);
  return match ? match.label : itemType?.charAt(0).toUpperCase() + itemType?.slice(1) || 'Other';
};

const formatStatusLabel = (status) => {
  if (!status) return 'Unknown';
  return status
    .replace(/_/g, ' ')
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
};

const SOURCE_TYPE_CONFIG = {
  manual: { label: 'Manual', variant: 'secondary', icon: null },
  chemical_reorder: { label: 'Chemical Reorder', variant: 'warning', icon: FaFlask },
  kit_reorder: { label: 'Kit Reorder', variant: 'info', icon: FaSuitcase },
};

const renderSourceBadge = (sourceType) => {
  if (!sourceType || sourceType === 'manual') return null;
  const config = SOURCE_TYPE_CONFIG[sourceType] || SOURCE_TYPE_CONFIG.manual;
  const Icon = config.icon;
  return (
    <Badge bg={config.variant} className="ms-1" style={{ fontSize: '0.7em' }}>
      {Icon && <Icon className="me-1" />}
      {config.label}
    </Badge>
  );
};

const INITIAL_ITEM = {
  item_type: 'tool',
  part_number: '',
  description: '',
  quantity: 1,
  unit: 'each',
};

const INITIAL_FORM_STATE = {
  title: '',
  description: '',
  priority: 'normal',
  expected_due_date: '',
  notes: '',
  items: [{ ...INITIAL_ITEM }],
};

const RequestsPage = () => {
  const dispatch = useDispatch();
  const { list, loading } = useSelector((state) => state.userRequests);
  const { alerts } = useSelector((state) => state.requestAlerts);
  const { user } = useSelector((state) => state.auth);

  const [activeTab, setActiveTab] = useState('submit');
  const [formState, setFormState] = useState(INITIAL_FORM_STATE);
  const [submitting, setSubmitting] = useState(false);
  const [editingRequest, setEditingRequest] = useState(null);
  const [editFormState, setEditFormState] = useState(null);
  const [showMessagesModal, setShowMessagesModal] = useState(false);
  const [selectedRequestForMessage, setSelectedRequestForMessage] = useState(null);
  const [messageSubject, setMessageSubject] = useState('');
  const [messageText, setMessageText] = useState('');
  const [requestMessages, setRequestMessages] = useState([]);
  const [sendingMessage, setSendingMessage] = useState(false);

  useEffect(() => {
    dispatch(fetchUserRequests({ sort: 'created' })).catch(() => {});
    dispatch(fetchRequestAlerts(false)).catch(() => {});
  }, [dispatch]);

  const myRequests = useMemo(() => {
    if (!user) return [];
    const mine = list.filter((req) => req.requester_id === user.id);
    return mine.slice().sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
  }, [list, user]);

  const openRequests = useMemo(
    () => myRequests.filter((req) => !['received', 'cancelled'].includes(req.status)).length,
    [myRequests],
  );

  const completedRequests = useMemo(
    () => myRequests.filter((req) => req.status === 'received').length,
    [myRequests],
  );

  const needsAttentionRequests = useMemo(
    () => myRequests.filter((req) => req.needs_more_info),
    [myRequests],
  );

  const totalItemsRequested = useMemo(() => {
    return myRequests.reduce((sum, req) => sum + (req.item_count || 0), 0);
  }, [myRequests]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((previous) => ({ ...previous, [name]: value }));
  };

  const handleItemChange = (index, field, value) => {
    setFormState((prev) => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };
      return { ...prev, items: newItems };
    });
  };

  const addItem = () => {
    setFormState((prev) => ({
      ...prev,
      items: [...prev.items, { ...INITIAL_ITEM }],
    }));
  };

  const removeItem = (index) => {
    if (formState.items.length <= 1) {
      toast.warning('At least one item is required.');
      return;
    }
    setFormState((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }));
  };

  const resetForm = () => {
    setFormState(INITIAL_FORM_STATE);
  };

  const handleDismissAlert = (alertId) => {
    dispatch(dismissAlert(alertId));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!formState.title.trim()) {
      toast.error('Please provide a title for your request.');
      return;
    }

    // Validate items
    for (let i = 0; i < formState.items.length; i++) {
      const item = formState.items[i];
      if (!item.description.trim()) {
        toast.error(`Item ${i + 1} is missing a description.`);
        return;
      }
      if (!item.quantity || item.quantity < 1) {
        toast.error(`Item ${i + 1} must have a valid quantity.`);
        return;
      }
    }

    const payload = {
      title: formState.title.trim(),
      description: formState.description.trim() || undefined,
      priority: formState.priority,
      expected_due_date: formState.expected_due_date || undefined,
      notes: formState.notes.trim() || undefined,
      items: formState.items.map((item) => ({
        item_type: item.item_type,
        part_number: item.part_number.trim() || undefined,
        description: item.description.trim(),
        quantity: parseInt(item.quantity, 10),
        unit: item.unit.trim() || 'each',
      })),
    };

    setSubmitting(true);
    try {
      await dispatch(createUserRequest(payload)).unwrap();
      toast.success(`Request submitted with ${payload.items.length} item(s).`);
      resetForm();
      dispatch(fetchUserRequests({ sort: 'created' })).catch(() => {});
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
      await dispatch(updateUserRequest({
        requestId,
        requestData: editFormState,
      })).unwrap();
      toast.success('Request updated successfully.');
      setEditingRequest(null);
      setEditFormState(null);
      dispatch(fetchUserRequests({ sort: 'created' })).catch(() => {});
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
      await dispatch(updateUserRequest({
        requestId,
        requestData: { needs_more_info: false },
      })).unwrap();
      toast.success('Request marked as resolved.');
      dispatch(fetchUserRequests({ sort: 'created' })).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to update request.');
    }
  };

  const handleCancelRequest = async (requestId) => {
    if (!window.confirm('Are you sure you want to cancel this request?')) {
      return;
    }
    try {
      await dispatch(cancelUserRequest(requestId)).unwrap();
      toast.success('Request cancelled successfully.');
      dispatch(fetchUserRequests({ sort: 'created' })).catch(() => {});
    } catch (error) {
      toast.error(error.message || 'Failed to cancel request.');
    }
  };

  const handleViewMessages = async (request) => {
    setSelectedRequestForMessage(request);
    setShowMessagesModal(true);
    try {
      const result = await dispatch(fetchRequestMessages(request.id)).unwrap();
      setRequestMessages(result.messages || []);
    } catch {
      toast.error('Failed to load messages.');
      setRequestMessages([]);
    }
  };

  const handleSendMessage = async () => {
    if (!messageSubject.trim() || !messageText.trim()) {
      toast.error('Please provide both subject and message.');
      return;
    }

    setSendingMessage(true);
    try {
      const result = await dispatch(sendRequestMessage({
        requestId: selectedRequestForMessage.id,
        messageData: {
          subject: messageSubject.trim(),
          message: messageText.trim(),
        },
      })).unwrap();
      setRequestMessages([result.message, ...requestMessages]);
      setMessageSubject('');
      setMessageText('');
      toast.success('Message sent successfully.');
    } catch (error) {
      toast.error(error.message || 'Failed to send message.');
    } finally {
      setSendingMessage(false);
    }
  };

  const renderItemStatusBadge = (status) => {
    const variant = STATUS_VARIANTS[status] || 'secondary';
    return <Badge bg={variant}>{formatStatusLabel(status)}</Badge>;
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
            Submit multi-item requests for tools, chemicals, expendables, or other materials.
          </p>
        </div>
      </div>

      {/* Alerts Section */}
      {alerts && alerts.length > 0 && (
        <Alert variant="success" className="mb-4">
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <FaBell className="me-2" />
              <strong>Items Received</strong>
              <div className="mt-2">
                {alerts.map((alert) => (
                  <div key={alert.id} className="d-flex align-items-center justify-content-between mb-2 pb-2 border-bottom">
                    <div className="flex-grow-1">
                      <div className="fw-semibold">{alert.request_title || `Request ${alert.request_number}`}</div>
                      <div className="small text-muted">{alert.message}</div>
                      <div className="small text-muted">
                        {alert.created_at && formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                      </div>
                    </div>
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      onClick={() => handleDismissAlert(alert.id)}
                      className="ms-3"
                    >
                      <FaTimes /> Dismiss
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Alert>
      )}

      <Row className="g-4 mb-4">
        <Col md={3}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center gap-3 mb-3">
                <FaPlusCircle className="text-primary" size={28} />
                <div>
                  <h5 className="mb-0">Open Requests</h5>
                  <small className="text-muted">Awaiting processing</small>
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
                <FaBoxes className="text-info" size={28} />
                <div>
                  <h5 className="mb-0">Total Items</h5>
                  <small className="text-muted">Across all requests</small>
                </div>
              </div>
              <h2 className="display-6 fw-bold mb-0">{totalItemsRequested}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center gap-3 mb-3">
                <FaCheckCircle className="text-success" size={28} />
                <div>
                  <h5 className="mb-0">Completed</h5>
                  <small className="text-muted">Fully received</small>
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
                <Col lg={10} className="mx-auto">
                  <Form onSubmit={handleSubmit}>
                    <Card className="mb-4">
                      <Card.Header>
                        <h5 className="mb-0">Request Details</h5>
                      </Card.Header>
                      <Card.Body>
                        <Form.Group className="mb-3">
                          <Form.Label>Request Title <span className="text-danger">*</span></Form.Label>
                          <Form.Control
                            type="text"
                            name="title"
                            value={formState.title}
                            onChange={handleChange}
                            placeholder="Brief description of what you need"
                            required
                          />
                        </Form.Group>

                        <Row className="g-3">
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
                          <Form.Label>Overall Description</Form.Label>
                          <Form.Control
                            as="textarea"
                            rows={2}
                            name="description"
                            value={formState.description}
                            onChange={handleChange}
                            placeholder="General description or purpose of this request"
                          />
                        </Form.Group>

                        <Form.Group>
                          <Form.Label>Additional Notes</Form.Label>
                          <Form.Control
                            as="textarea"
                            rows={2}
                            name="notes"
                            value={formState.notes}
                            onChange={handleChange}
                            placeholder="Any special instructions or justifications"
                          />
                        </Form.Group>
                      </Card.Body>
                    </Card>

                    <Card className="mb-4">
                      <Card.Header className="d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">Items to Request ({formState.items.length})</h5>
                        <Button variant="outline-primary" size="sm" onClick={addItem}>
                          <FaPlus className="me-1" />
                          Add Item
                        </Button>
                      </Card.Header>
                      <Card.Body>
                        {formState.items.map((item, index) => (
                          <Card key={index} className="mb-3 border">
                            <Card.Header className="d-flex justify-content-between align-items-center py-2">
                              <strong>Item #{index + 1}</strong>
                              {formState.items.length > 1 && (
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => removeItem(index)}
                                >
                                  <FaTrash />
                                </Button>
                              )}
                            </Card.Header>
                            <Card.Body>
                              <Row className="g-3">
                                <Col md={4}>
                                  <Form.Group>
                                    <Form.Label>Type</Form.Label>
                                    <Form.Select
                                      value={item.item_type}
                                      onChange={(e) => handleItemChange(index, 'item_type', e.target.value)}
                                    >
                                      {ITEM_TYPES.map((opt) => (
                                        <option key={opt.value} value={opt.value}>
                                          {opt.label}
                                        </option>
                                      ))}
                                    </Form.Select>
                                  </Form.Group>
                                </Col>
                                <Col md={4}>
                                  <Form.Group>
                                    <Form.Label>Part Number</Form.Label>
                                    <Form.Control
                                      type="text"
                                      value={item.part_number}
                                      onChange={(e) => handleItemChange(index, 'part_number', e.target.value)}
                                      placeholder="Optional"
                                    />
                                  </Form.Group>
                                </Col>
                                <Col md={2}>
                                  <Form.Group>
                                    <Form.Label>Quantity <span className="text-danger">*</span></Form.Label>
                                    <Form.Control
                                      type="number"
                                      min="1"
                                      value={item.quantity}
                                      onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                                    />
                                  </Form.Group>
                                </Col>
                                <Col md={2}>
                                  <Form.Group>
                                    <Form.Label>Unit</Form.Label>
                                    <Form.Control
                                      type="text"
                                      value={item.unit}
                                      onChange={(e) => handleItemChange(index, 'unit', e.target.value)}
                                      placeholder="each"
                                    />
                                  </Form.Group>
                                </Col>
                              </Row>
                              <Form.Group className="mt-3">
                                <Form.Label>Description <span className="text-danger">*</span></Form.Label>
                                <Form.Control
                                  as="textarea"
                                  rows={2}
                                  value={item.description}
                                  onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                                  placeholder="Describe what you need, including specifications, size, material, etc."
                                />
                              </Form.Group>
                            </Card.Body>
                          </Card>
                        ))}
                      </Card.Body>
                    </Card>

                    <div className="d-flex justify-content-end">
                      <Button type="submit" variant="primary" size="lg" disabled={submitting}>
                        {submitting ? (
                          <>
                            <Spinner as="span" animation="border" size="sm" role="status" className="me-2" />
                            Submitting...
                          </>
                        ) : (
                          <>
                            <FaPaperPlane className="me-2" />
                            Submit Request ({formState.items.length} item{formState.items.length !== 1 ? 's' : ''})
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
                  {myRequests.map((req) => (
                    <ListGroup.Item key={req.id} className="py-3">
                      {req.needs_more_info && (
                        <Alert variant="warning" className="mb-2">
                          <FaInfoCircle className="me-2" />
                          <strong>Attention Required:</strong> This request needs more information.
                        </Alert>
                      )}
                      <div className="d-flex flex-column gap-3">
                        <div className="d-flex justify-content-between align-items-start">
                          <div className="flex-grow-1">
                            <h5 className="mb-1">
                              {req.request_number && (
                                <Badge bg="dark" className="me-2">{req.request_number}</Badge>
                              )}
                              {req.title}
                            </h5>
                            <div className="text-muted small">
                              Requested {req.created_at ? formatDistanceToNow(new Date(req.created_at), { addSuffix: true }) : 'N/A'}
                              {' | '}
                              {req.item_count} item{req.item_count !== 1 ? 's' : ''}
                            </div>
                            {req.expected_due_date && (
                              <div className="text-muted small">
                                Needed by {new Date(req.expected_due_date).toLocaleDateString()}
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
                            {req.message_count > 0 && (
                              <Badge bg="info" title="Messages">
                                <FaEnvelope className="me-1" />
                                {req.message_count}
                              </Badge>
                            )}
                          </div>
                        </div>

                        {editingRequest === req.id ? (
                          <div className="mt-2">
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
                              <Button size="sm" variant="primary" onClick={() => handleSaveEdit(req.id)}>
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
                            {req.description && (
                              <div className="small">
                                <strong>Description:</strong> {req.description}
                              </div>
                            )}
                            {req.notes && (
                              <div className="small">
                                <strong>Notes:</strong> {req.notes}
                              </div>
                            )}
                          </>
                        )}

                        {/* Items Table */}
                        {req.items && req.items.length > 0 && (
                          <div className="mt-2">
                            <h6 className="mb-2">Items:</h6>
                            <Table size="sm" bordered hover responsive>
                              <thead>
                                <tr>
                                  <th>Type</th>
                                  <th>Description</th>
                                  <th>Part #</th>
                                  <th>Qty</th>
                                  <th>Status</th>
                                  <th>Source</th>
                                  <th>Vendor</th>
                                  <th>Tracking</th>
                                </tr>
                              </thead>
                              <tbody>
                                {req.items.map((item) => (
                                  <tr key={item.id}>
                                    <td>{getItemTypeLabel(item.item_type)}</td>
                                    <td className="text-truncate" style={{ maxWidth: '200px' }}>
                                      {item.description}
                                    </td>
                                    <td>{item.part_number || '-'}</td>
                                    <td>{item.quantity} {item.unit}</td>
                                    <td>{renderItemStatusBadge(item.status)}</td>
                                    <td>{renderSourceBadge(item.source_type) || '-'}</td>
                                    <td>{item.vendor || '-'}</td>
                                    <td>
                                      {item.tracking_number ? (
                                        <span className="text-info">
                                          <FaTruck className="me-1" />
                                          {item.tracking_number}
                                        </span>
                                      ) : '-'}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </Table>
                          </div>
                        )}

                        {editingRequest !== req.id && (
                          <div className="d-flex gap-2 flex-wrap">
                            {req.message_count > 0 && (
                              <Button size="sm" variant="outline-secondary" onClick={() => handleViewMessages(req)}>
                                <FaEnvelope className="me-1" />
                                View Messages
                              </Button>
                            )}
                            {req.buyer_id && req.status !== 'cancelled' && req.status !== 'received' && (
                              <Button size="sm" variant="outline-info" onClick={() => handleViewMessages(req)}>
                                <FaSync className="me-1" />
                                Send Message
                              </Button>
                            )}
                            {req.status !== 'cancelled' && req.status !== 'received' && (
                              <>
                                <Button size="sm" variant="outline-primary" onClick={() => handleEditRequest(req)}>
                                  <FaEdit className="me-1" />
                                  Edit
                                </Button>
                                <Button size="sm" variant="outline-danger" onClick={() => handleCancelRequest(req.id)}>
                                  <FaTimes className="me-1" />
                                  Cancel
                                </Button>
                              </>
                            )}
                          </div>
                        )}
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Tab>

            {/* Needs Attention Tab */}
            <Tab
              eventKey="attention"
              title={
                <>
                  Needs Attention
                  {needsAttentionRequests.length > 0 && (
                    <Badge bg="warning" className="ms-2">
                      {needsAttentionRequests.length}
                    </Badge>
                  )}
                </>
              }
            >
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
                    The following requests need more information. Please provide additional details.
                  </Alert>
                  <ListGroup variant="flush">
                    {needsAttentionRequests.map((req) => (
                      <ListGroup.Item key={req.id} className="py-3">
                        <div className="d-flex flex-column gap-3">
                          <div className="d-flex justify-content-between align-items-start">
                            <div className="flex-grow-1">
                              <h6 className="mb-1">
                                {req.request_number && (
                                  <Badge bg="dark" className="me-2">{req.request_number}</Badge>
                                )}
                                {req.title}
                              </h6>
                              <div className="text-muted small">
                                {req.item_count} item{req.item_count !== 1 ? 's' : ''} |{' '}
                                Requested {req.created_at ? formatDistanceToNow(new Date(req.created_at), { addSuffix: true }) : 'N/A'}
                              </div>
                              {editingRequest === req.id ? (
                                <div className="mt-3">
                                  <Form.Group className="mb-2">
                                    <Form.Label>Description</Form.Label>
                                    <Form.Control
                                      as="textarea"
                                      rows={3}
                                      name="description"
                                      value={editFormState.description}
                                      onChange={handleEditFormChange}
                                      placeholder="Add more details..."
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
                                      placeholder="Add clarifications..."
                                    />
                                  </Form.Group>
                                  <div className="d-flex gap-2">
                                    <Button size="sm" variant="success" onClick={() => handleSaveEdit(req.id)}>
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
                                  {req.description && (
                                    <div className="mt-2 small">
                                      <strong>Description:</strong> {req.description}
                                    </div>
                                  )}
                                  {req.notes && (
                                    <div className="mt-1 small">
                                      <strong>Notes:</strong> {req.notes}
                                    </div>
                                  )}
                                </>
                              )}
                            </div>
                            <div className="d-flex flex-wrap gap-2">
                              <Badge bg={PRIORITY_VARIANTS[req.priority] || 'secondary'}>
                                {PRIORITIES.find((p) => p.value === req.priority)?.label || req.priority}
                              </Badge>
                            </div>
                          </div>
                          {editingRequest !== req.id && (
                            <div className="d-flex gap-2">
                              <Button size="sm" variant="primary" onClick={() => handleEditRequest(req)}>
                                <FaEdit className="me-1" />
                                Add Information
                              </Button>
                              <Button size="sm" variant="outline-success" onClick={() => handleResolveNeedsInfo(req.id)}>
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

      {/* Messages Modal */}
      {showMessagesModal && selectedRequestForMessage && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  Messages for: {selectedRequestForMessage.request_number && `${selectedRequestForMessage.request_number} - `}{selectedRequestForMessage.title}
                </h5>
                <button type="button" className="btn-close" onClick={() => setShowMessagesModal(false)} />
              </div>
              <div className="modal-body">
                {selectedRequestForMessage.buyer_id && (
                  <Card className="mb-3">
                    <Card.Header>Send New Message</Card.Header>
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
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={handleSendMessage}
                        disabled={sendingMessage}
                      >
                        {sendingMessage ? 'Sending...' : 'Send Message'}
                      </Button>
                    </Card.Body>
                  </Card>
                )}

                <h6>Message History</h6>
                {requestMessages.length === 0 ? (
                  <div className="text-muted">No messages yet.</div>
                ) : (
                  <ListGroup>
                    {requestMessages.map((msg) => (
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
              </div>
              <div className="modal-footer">
                <Button variant="secondary" onClick={() => setShowMessagesModal(false)}>
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RequestsPage;
