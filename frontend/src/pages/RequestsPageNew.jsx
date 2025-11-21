import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FaClipboardList, FaPaperPlane, FaPlusCircle, FaInfoCircle, FaCheckCircle, FaEdit, FaTimes, FaSync, FaEnvelope, FaTrash, FaPlus, FaBoxes, FaTruck, FaFlask, FaSuitcase, FaBell } from 'react-icons/fa';
import { Loader2 } from 'lucide-react';
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
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';

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
  new: 'default',
  awaiting_info: 'warning',
  in_progress: 'secondary',
  partially_ordered: 'secondary',
  ordered: 'success',
  partially_received: 'secondary',
  received: 'success',
  cancelled: 'outline',
  pending: 'warning',
  shipped: 'secondary',
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
  manual: { label: 'Manual', variant: 'outline', icon: null },
  chemical_reorder: { label: 'Chemical Reorder', variant: 'warning', icon: FaFlask },
  kit_reorder: { label: 'Kit Reorder', variant: 'secondary', icon: FaSuitcase },
};

const renderSourceBadge = (sourceType) => {
  if (!sourceType || sourceType === 'manual') return null;
  const config = SOURCE_TYPE_CONFIG[sourceType] || SOURCE_TYPE_CONFIG.manual;
  const Icon = config.icon;
  return (
    <Badge variant={config.variant} className="ml-1 text-xs">
      {Icon && <Icon className="mr-1 inline h-3 w-3" />}
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

const RequestsPageNew = () => {
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
    const variant = STATUS_VARIANTS[status] || 'outline';
    return <Badge variant={variant}>{formatStatusLabel(status)}</Badge>;
  };

  return (
    <div className="requests-page p-4 md:p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="mb-1 flex items-center gap-2 text-3xl font-bold text-foreground">
            <FaClipboardList className="text-primary" />
            Procurement Requests
          </h1>
          <p className="text-muted-foreground">
            Submit multi-item requests for tools, chemicals, expendables, or other materials.
          </p>
        </div>
      </div>

      {/* Alerts Section */}
      {alerts && alerts.length > 0 && (
        <Alert className="mb-6 border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="mb-3 flex items-center gap-2">
                <FaBell className="text-green-600 dark:text-green-400" />
                <strong className="text-green-900 dark:text-green-100">Items Received</strong>
              </div>
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between border-b border-green-200 pb-3 last:border-0 dark:border-green-800">
                    <div className="flex-1">
                      <div className="font-semibold text-green-900 dark:text-green-100">{alert.request_title || `Request ${alert.request_number}`}</div>
                      <div className="text-sm text-green-700 dark:text-green-300">{alert.message}</div>
                      <div className="text-sm text-green-600 dark:text-green-400">
                        {alert.created_at && formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDismissAlert(alert.id)}
                      className="ml-4 hover:bg-green-100 dark:hover:bg-green-900"
                    >
                      <FaTimes className="mr-1" /> Dismiss
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="shadow-sm transition-shadow hover:shadow-md">
          <CardContent className="p-6">
            <div className="mb-3 flex items-center gap-3">
              <FaPlusCircle className="text-primary" size={28} />
              <div>
                <h5 className="font-semibold">Open Requests</h5>
                <small className="text-muted-foreground">Awaiting processing</small>
              </div>
            </div>
            <h2 className="text-4xl font-bold">{openRequests}</h2>
          </CardContent>
        </Card>
        <Card
          className="cursor-pointer border-yellow-300 shadow-sm transition-all hover:shadow-md dark:border-yellow-700"
          onClick={() => setActiveTab('attention')}
        >
          <CardContent className="p-6">
            <div className="mb-3 flex items-center gap-3">
              <FaInfoCircle className="text-yellow-600 dark:text-yellow-500" size={28} />
              <div>
                <h5 className="font-semibold">Needs Attention</h5>
                <small className="text-muted-foreground">Requests needing more info</small>
              </div>
            </div>
            <h2 className="text-4xl font-bold text-yellow-600 dark:text-yellow-500">{needsAttentionRequests.length}</h2>
          </CardContent>
        </Card>
        <Card className="shadow-sm transition-shadow hover:shadow-md">
          <CardContent className="p-6">
            <div className="mb-3 flex items-center gap-3">
              <FaBoxes className="text-blue-600 dark:text-blue-400" size={28} />
              <div>
                <h5 className="font-semibold">Total Items</h5>
                <small className="text-muted-foreground">Across all requests</small>
              </div>
            </div>
            <h2 className="text-4xl font-bold">{totalItemsRequested}</h2>
          </CardContent>
        </Card>
        <Card className="shadow-sm transition-shadow hover:shadow-md">
          <CardContent className="p-6">
            <div className="mb-3 flex items-center gap-3">
              <FaCheckCircle className="text-green-600 dark:text-green-400" size={28} />
              <div>
                <h5 className="font-semibold">Completed</h5>
                <small className="text-muted-foreground">Fully received</small>
              </div>
            </div>
            <h2 className="text-4xl font-bold">{completedRequests}</h2>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="mb-4 w-full justify-start">
              <TabsTrigger value="submit">Submit Request</TabsTrigger>
              <TabsTrigger value="requests">My Requests ({myRequests.length})</TabsTrigger>
              <TabsTrigger value="attention" className="relative">
                Needs Attention
                {needsAttentionRequests.length > 0 && (
                  <Badge variant="warning" className="ml-2 h-5 min-w-5 px-1.5 text-xs">
                    {needsAttentionRequests.length}
                  </Badge>
                )}
              </TabsTrigger>
            </TabsList>

            {/* Submit Request Tab */}
            <TabsContent value="submit">
              <div className="mx-auto max-w-4xl">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Request Details</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label htmlFor="title">Request Title <span className="text-red-500">*</span></Label>
                        <Input
                          id="title"
                          name="title"
                          value={formState.title}
                          onChange={handleChange}
                          placeholder="Brief description of what you need"
                          required
                          className="mt-1.5"
                        />
                      </div>

                      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div>
                          <Label htmlFor="priority">Priority</Label>
                          <Select value={formState.priority} onValueChange={(value) => setFormState(prev => ({ ...prev, priority: value }))}>
                            <SelectTrigger className="mt-1.5">
                              <SelectValue placeholder="Select priority" />
                            </SelectTrigger>
                            <SelectContent>
                              {PRIORITIES.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="expected_due_date">Needed By</Label>
                          <Input
                            id="expected_due_date"
                            type="date"
                            name="expected_due_date"
                            value={formState.expected_due_date}
                            onChange={handleChange}
                            className="mt-1.5"
                          />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="description">Overall Description</Label>
                        <Textarea
                          id="description"
                          name="description"
                          value={formState.description}
                          onChange={handleChange}
                          placeholder="General description or purpose of this request"
                          rows={2}
                          className="mt-1.5"
                        />
                      </div>

                      <div>
                        <Label htmlFor="notes">Additional Notes</Label>
                        <Textarea
                          id="notes"
                          name="notes"
                          value={formState.notes}
                          onChange={handleChange}
                          placeholder="Any special instructions or justifications"
                          rows={2}
                          className="mt-1.5"
                        />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0">
                      <CardTitle>Items to Request ({formState.items.length})</CardTitle>
                      <Button type="button" variant="outline" size="sm" onClick={addItem}>
                        <FaPlus className="mr-2 h-3 w-3" />
                        Add Item
                      </Button>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {formState.items.map((item, index) => (
                        <Card key={index} className="border">
                          <CardHeader className="flex flex-row items-center justify-between space-y-0 py-3">
                            <strong className="text-sm">Item #{index + 1}</strong>
                            {formState.items.length > 1 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => removeItem(index)}
                                className="text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950"
                              >
                                <FaTrash className="h-3 w-3" />
                              </Button>
                            )}
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
                              <div className="md:col-span-4">
                                <Label>Type</Label>
                                <Select
                                  value={item.item_type}
                                  onValueChange={(value) => handleItemChange(index, 'item_type', value)}
                                >
                                  <SelectTrigger className="mt-1.5">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {ITEM_TYPES.map((opt) => (
                                      <SelectItem key={opt.value} value={opt.value}>
                                        {opt.label}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="md:col-span-4">
                                <Label>Part Number</Label>
                                <Input
                                  value={item.part_number}
                                  onChange={(e) => handleItemChange(index, 'part_number', e.target.value)}
                                  placeholder="Optional"
                                  className="mt-1.5"
                                />
                              </div>
                              <div className="md:col-span-2">
                                <Label>Quantity <span className="text-red-500">*</span></Label>
                                <Input
                                  type="number"
                                  min="1"
                                  value={item.quantity}
                                  onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                                  className="mt-1.5"
                                />
                              </div>
                              <div className="md:col-span-2">
                                <Label>Unit</Label>
                                <Input
                                  value={item.unit}
                                  onChange={(e) => handleItemChange(index, 'unit', e.target.value)}
                                  placeholder="each"
                                  className="mt-1.5"
                                />
                              </div>
                            </div>
                            <div>
                              <Label>Description <span className="text-red-500">*</span></Label>
                              <Textarea
                                value={item.description}
                                onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                                placeholder="Describe what you need, including specifications, size, material, etc."
                                rows={2}
                                className="mt-1.5"
                              />
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </CardContent>
                  </Card>

                  <div className="flex justify-end">
                    <Button type="submit" size="lg" disabled={submitting}>
                      {submitting ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Submitting...
                        </>
                      ) : (
                        <>
                          <FaPaperPlane className="mr-2" />
                          Submit Request ({formState.items.length} item{formState.items.length !== 1 ? 's' : ''})
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </div>
            </TabsContent>

            {/* My Requests Tab */}
            <TabsContent value="requests">
              {loading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : myRequests.length === 0 ? (
                <div className="py-12 text-center text-muted-foreground">
                  <p className="mb-1">No requests yet.</p>
                  <small>Submit your first request using the Submit Request tab.</small>
                </div>
              ) : (
                <div className="space-y-4">
                  {myRequests.map((req) => (
                    <Card key={req.id} className="transition-shadow hover:shadow-md">
                      <CardContent className="p-6">
                        {req.needs_more_info && (
                          <Alert variant="warning" className="mb-4">
                            <FaInfoCircle className="mr-2 inline h-4 w-4" />
                            <strong>Attention Required:</strong> This request needs more information.
                          </Alert>
                        )}
                        <div className="space-y-4">
                          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
                            <div className="flex-1">
                              <h5 className="mb-2 text-lg font-semibold">
                                {req.request_number && (
                                  <Badge variant="secondary" className="mr-2">{req.request_number}</Badge>
                                )}
                                {req.title}
                              </h5>
                              <div className="text-sm text-muted-foreground">
                                Requested {req.created_at ? formatDistanceToNow(new Date(req.created_at), { addSuffix: true }) : 'N/A'}
                                {' | '}
                                {req.item_count} item{req.item_count !== 1 ? 's' : ''}
                              </div>
                              {req.expected_due_date && (
                                <div className="text-sm text-muted-foreground">
                                  Needed by {new Date(req.expected_due_date).toLocaleDateString()}
                                </div>
                              )}
                            </div>
                            <div className="flex flex-wrap gap-2">
                              <Badge variant={PRIORITY_VARIANTS[req.priority] || 'outline'}>
                                {PRIORITIES.find((p) => p.value === req.priority)?.label || req.priority}
                              </Badge>
                              <Badge variant={STATUS_VARIANTS[req.status] || 'outline'}>
                                {formatStatusLabel(req.status)}
                              </Badge>
                              {req.message_count > 0 && (
                                <Badge variant="secondary" title="Messages">
                                  <FaEnvelope className="mr-1 h-3 w-3" />
                                  {req.message_count}
                                </Badge>
                              )}
                            </div>
                          </div>

                          {editingRequest === req.id ? (
                            <div className="space-y-3 rounded-md border bg-muted/50 p-4">
                              <div>
                                <Label>Description</Label>
                                <Textarea
                                  name="description"
                                  value={editFormState.description}
                                  onChange={handleEditFormChange}
                                  rows={2}
                                  className="mt-1.5"
                                />
                              </div>
                              <div>
                                <Label>Notes</Label>
                                <Textarea
                                  name="notes"
                                  value={editFormState.notes}
                                  onChange={handleEditFormChange}
                                  rows={2}
                                  className="mt-1.5"
                                />
                              </div>
                              <div className="flex gap-2">
                                <Button size="sm" onClick={() => handleSaveEdit(req.id)}>
                                  <FaCheckCircle className="mr-1" />
                                  Save
                                </Button>
                                <Button size="sm" variant="outline" onClick={handleCancelEdit}>
                                  Cancel
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <>
                              {req.description && (
                                <div className="text-sm">
                                  <strong>Description:</strong> {req.description}
                                </div>
                              )}
                              {req.notes && (
                                <div className="text-sm">
                                  <strong>Notes:</strong> {req.notes}
                                </div>
                              )}
                            </>
                          )}

                          {/* Items Table */}
                          {req.items && req.items.length > 0 && (
                            <div>
                              <h6 className="mb-2 font-semibold">Items:</h6>
                              <div className="overflow-x-auto rounded-md border">
                                <Table>
                                  <TableHeader>
                                    <TableRow>
                                      <TableHead>Type</TableHead>
                                      <TableHead>Description</TableHead>
                                      <TableHead>Part #</TableHead>
                                      <TableHead>Qty</TableHead>
                                      <TableHead>Status</TableHead>
                                      <TableHead>Source</TableHead>
                                      <TableHead>Vendor</TableHead>
                                      <TableHead>Tracking</TableHead>
                                    </TableRow>
                                  </TableHeader>
                                  <TableBody>
                                    {req.items.map((item) => (
                                      <TableRow key={item.id}>
                                        <TableCell>{getItemTypeLabel(item.item_type)}</TableCell>
                                        <TableCell className="max-w-xs truncate">
                                          {item.description}
                                        </TableCell>
                                        <TableCell>{item.part_number || '-'}</TableCell>
                                        <TableCell>{item.quantity} {item.unit}</TableCell>
                                        <TableCell>{renderItemStatusBadge(item.status)}</TableCell>
                                        <TableCell>{renderSourceBadge(item.source_type) || '-'}</TableCell>
                                        <TableCell>{item.vendor || '-'}</TableCell>
                                        <TableCell>
                                          {item.tracking_number ? (
                                            <span className="text-blue-600 dark:text-blue-400">
                                              <FaTruck className="mr-1 inline h-3 w-3" />
                                              {item.tracking_number}
                                            </span>
                                          ) : '-'}
                                        </TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </div>
                            </div>
                          )}

                          {editingRequest !== req.id && (
                            <div className="flex flex-wrap gap-2">
                              {req.message_count > 0 && (
                                <Button size="sm" variant="outline" onClick={() => handleViewMessages(req)}>
                                  <FaEnvelope className="mr-1" />
                                  View Messages
                                </Button>
                              )}
                              {req.buyer_id && req.status !== 'cancelled' && req.status !== 'received' && (
                                <Button size="sm" variant="outline" onClick={() => handleViewMessages(req)}>
                                  <FaSync className="mr-1" />
                                  Send Message
                                </Button>
                              )}
                              {req.status !== 'cancelled' && req.status !== 'received' && (
                                <>
                                  <Button size="sm" variant="outline" onClick={() => handleEditRequest(req)}>
                                    <FaEdit className="mr-1" />
                                    Edit
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleCancelRequest(req.id)}
                                    className="text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950"
                                  >
                                    <FaTimes className="mr-1" />
                                    Cancel
                                  </Button>
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Needs Attention Tab */}
            <TabsContent value="attention">
              {needsAttentionRequests.length === 0 ? (
                <div className="py-12 text-center text-muted-foreground">
                  <FaCheckCircle size={48} className="mx-auto mb-4 text-green-600 dark:text-green-400" />
                  <p className="mb-1 text-lg font-semibold">All caught up!</p>
                  <small>No requests need attention at the moment.</small>
                </div>
              ) : (
                <>
                  <Alert variant="info" className="mb-4">
                    <FaInfoCircle className="mr-2 inline h-4 w-4" />
                    The following requests need more information. Please provide additional details.
                  </Alert>
                  <div className="space-y-4">
                    {needsAttentionRequests.map((req) => (
                      <Card key={req.id} className="transition-shadow hover:shadow-md">
                        <CardContent className="p-6">
                          <div className="space-y-4">
                            <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
                              <div className="flex-1">
                                <h6 className="mb-2 font-semibold">
                                  {req.request_number && (
                                    <Badge variant="secondary" className="mr-2">{req.request_number}</Badge>
                                  )}
                                  {req.title}
                                </h6>
                                <div className="text-sm text-muted-foreground">
                                  {req.item_count} item{req.item_count !== 1 ? 's' : ''} |{' '}
                                  Requested {req.created_at ? formatDistanceToNow(new Date(req.created_at), { addSuffix: true }) : 'N/A'}
                                </div>
                                {editingRequest === req.id ? (
                                  <div className="mt-4 space-y-3 rounded-md border bg-muted/50 p-4">
                                    <div>
                                      <Label>Description</Label>
                                      <Textarea
                                        name="description"
                                        value={editFormState.description}
                                        onChange={handleEditFormChange}
                                        placeholder="Add more details..."
                                        rows={3}
                                        className="mt-1.5"
                                      />
                                    </div>
                                    <div>
                                      <Label>Notes</Label>
                                      <Textarea
                                        name="notes"
                                        value={editFormState.notes}
                                        onChange={handleEditFormChange}
                                        placeholder="Add clarifications..."
                                        rows={2}
                                        className="mt-1.5"
                                      />
                                    </div>
                                    <div className="flex gap-2">
                                      <Button size="sm" onClick={() => handleSaveEdit(req.id)}>
                                        <FaCheckCircle className="mr-1" />
                                        Save
                                      </Button>
                                      <Button size="sm" variant="outline" onClick={handleCancelEdit}>
                                        Cancel
                                      </Button>
                                    </div>
                                  </div>
                                ) : (
                                  <>
                                    {req.description && (
                                      <div className="mt-2 text-sm">
                                        <strong>Description:</strong> {req.description}
                                      </div>
                                    )}
                                    {req.notes && (
                                      <div className="mt-1 text-sm">
                                        <strong>Notes:</strong> {req.notes}
                                      </div>
                                    )}
                                  </>
                                )}
                              </div>
                              <div className="flex flex-wrap gap-2">
                                <Badge variant={PRIORITY_VARIANTS[req.priority] || 'outline'}>
                                  {PRIORITIES.find((p) => p.value === req.priority)?.label || req.priority}
                                </Badge>
                              </div>
                            </div>
                            {editingRequest !== req.id && (
                              <div className="flex gap-2">
                                <Button size="sm" onClick={() => handleEditRequest(req)}>
                                  <FaEdit className="mr-1" />
                                  Add Information
                                </Button>
                                <Button size="sm" variant="outline" onClick={() => handleResolveNeedsInfo(req.id)}>
                                  <FaCheckCircle className="mr-1" />
                                  Mark as Resolved
                                </Button>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Messages Modal */}
      <Dialog open={showMessagesModal} onOpenChange={setShowMessagesModal}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>
              Messages for: {selectedRequestForMessage?.request_number && `${selectedRequestForMessage.request_number} - `}{selectedRequestForMessage?.title}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {selectedRequestForMessage?.buyer_id && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Send New Message</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <Label htmlFor="messageSubject">Subject</Label>
                    <Input
                      id="messageSubject"
                      value={messageSubject}
                      onChange={(e) => setMessageSubject(e.target.value)}
                      placeholder="Message subject"
                      className="mt-1.5"
                    />
                  </div>
                  <div>
                    <Label htmlFor="messageText">Message</Label>
                    <Textarea
                      id="messageText"
                      value={messageText}
                      onChange={(e) => setMessageText(e.target.value)}
                      placeholder="Your message..."
                      rows={3}
                      className="mt-1.5"
                    />
                  </div>
                  <Button
                    size="sm"
                    onClick={handleSendMessage}
                    disabled={sendingMessage}
                  >
                    {sendingMessage ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      'Send Message'
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}

            <div>
              <h6 className="mb-3 font-semibold">Message History</h6>
              {requestMessages.length === 0 ? (
                <div className="text-muted-foreground">No messages yet.</div>
              ) : (
                <div className="space-y-3">
                  {requestMessages.map((msg) => (
                    <Card key={msg.id}>
                      <CardContent className="p-4">
                        <div className="mb-2 flex items-start justify-between">
                          <strong className="text-sm">{msg.subject}</strong>
                          <small className="text-muted-foreground">
                            {msg.sent_date ? new Date(msg.sent_date).toLocaleString() : ''}
                          </small>
                        </div>
                        <div className="mb-2 text-xs text-muted-foreground">
                          From: {msg.sender_name} | To: {msg.recipient_name}
                        </div>
                        <div className="text-sm">{msg.message}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowMessagesModal(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RequestsPageNew;
