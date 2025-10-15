import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Card,
  Row,
  Col,
  Button,
  Alert,
  Spinner,
  Badge,
  Table,
  Form,
  InputGroup,
  Modal,
  ProgressBar
} from 'react-bootstrap';
import {
  fetchCycleCountBatch,
  fetchCycleCountItems,
  updateCycleCountBatch,
  deleteCycleCountBatch
} from '../store/cycleCountSlice';
import { useHelp } from '../context/HelpContext';
import ConfirmModal from '../components/common/ConfirmModal';
import CycleCountItemForm from '../components/cycleCount/CycleCountItemForm';
import CycleCountExportImport from '../components/cycleCount/CycleCountExportImport';

const CycleCountBatchDetailPage = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { showHelp } = useHelp();

  const { data: batch, loading: batchLoading, error: batchError } =
    useSelector((state) => state.cycleCount.currentBatch);

  const itemsState = useSelector((state) => state.cycleCount.items);
  const items = itemsState.byBatchId[id] || [];
  const itemsLoading = itemsState.loadingByBatchId[id] || false;
  const itemsError = itemsState.errorByBatchId[id];

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortField, setSortField] = useState('id');
  const [sortDirection, setSortDirection] = useState('asc');
  const [showCountModal, setShowCountModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    // Fetch batch with associated items
    dispatch(fetchCycleCountBatch({ id, includeItems: true }));

    // Fetch all items for this batch
    dispatch(fetchCycleCountItems({ batchId: id }));
  }, [dispatch, id]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleDelete = async () => {
    try {
      await dispatch(deleteCycleCountBatch(id)).unwrap();
      setShowDeleteModal(false);
      navigate('/cycle-counts/batches');
      // Optional: Show a toast notification for success
    } catch (error) {
      console.error('Failed to delete batch:', error);
      // Show error feedback to the user
      alert(`Failed to delete batch: ${error.message || 'Unknown error'}`);
    }
  };

  const handleStartBatch = async () => {
    try {
      await dispatch(updateCycleCountBatch({
        id,
        batchData: { status: 'in_progress' }
      })).unwrap();
    } catch (error) {
      console.error('Failed to start batch:', error);
    }
  };

  const handleCompleteBatch = async () => {
    try {
      await dispatch(updateCycleCountBatch({
        id,
        batchData: { status: 'completed' }
      })).unwrap();
    } catch (error) {
      console.error('Failed to complete batch:', error);
    }
  };

  const handleOpenCountModal = (item) => {
    setSelectedItem(item);
    setShowCountModal(true);
  };

  const formatStatus = (status) => {
    const statuses = {
      pending: { label: 'Pending', variant: 'warning' },
      in_progress: { label: 'In Progress', variant: 'primary' },
      completed: { label: 'Completed', variant: 'success' },
      cancelled: { label: 'Cancelled', variant: 'danger' }
    };
    return statuses[status] || { label: status, variant: 'secondary' };
  };

  const formatItemStatus = (status) => {
    const statuses = {
      pending: { label: 'Pending', variant: 'warning' },
      assigned: { label: 'Assigned', variant: 'info' },
      counted: { label: 'Counted', variant: 'success' },
      skipped: { label: 'Skipped', variant: 'secondary' }
    };
    return statuses[status] || { label: status, variant: 'secondary' };
  };

  const filteredItems = items.filter(item => {
    // Apply status filter
    if (statusFilter !== 'all' && item.status !== statusFilter) {
      return false;
    }

    // Apply search filter
    const searchLower = searchTerm.toLowerCase();
    return (
      item.item_type.toLowerCase().includes(searchLower) ||
      item.item_name.toLowerCase().includes(searchLower) ||
      (item.location?.toLowerCase() || '').includes(searchLower) ||
      (item.assigned_to?.toLowerCase() || '').includes(searchLower)
    );
  });

  const sortedItems = [...filteredItems].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    // Handle null/undefined values
    if (aValue === null || aValue === undefined) return sortDirection === 'asc' ? -1 : 1;
    if (bValue === null || bValue === undefined) return sortDirection === 'asc' ? 1 : -1;

    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  const calculateProgress = () => {
    if (!items || items.length === 0) return 0;
    const countedItems = items.filter(item => item.status === 'counted').length;
    return Math.round((countedItems / items.length) * 100);
  };

  if (batchLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (batchError) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Batch</Alert.Heading>
        <p>{batchError.error || `An error occurred while loading batch ${id}`}</p>
      </Alert>
    );
  }

  if (!batch) {
    return (
      <Alert variant="warning">
        <Alert.Heading>Batch Not Found</Alert.Heading>
        <p>The requested cycle count batch could not be found.</p>
        <Button as={Link} to="/cycle-counts/batches" variant="primary">
          Back to Batches
        </Button>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <div>
          <h1 className="mb-0">{batch.name}</h1>
          <p className="text-muted mb-0">
            Cycle Count Batch
            {batch.schedule && ` - Part of schedule: ${batch.schedule.name}`}
          </p>
        </div>
        <div>
          {batch.status === 'pending' && (
            <Button variant="success" onClick={handleStartBatch} className="me-2">
              <i className="bi bi-play-fill me-2"></i>
              Start Counting
            </Button>
          )}

          {batch.status === 'in_progress' && (
            <Button variant="success" onClick={handleCompleteBatch} className="me-2">
              <i className="bi bi-check-lg me-2"></i>
              Complete Batch
            </Button>
          )}

          <Button as={Link} to={`/cycle-counts/batches/${id}/edit`} variant="primary" className="me-2">
            <i className="bi bi-pencil me-2"></i>
            Edit Batch
          </Button>

          <Button variant="outline-danger" onClick={() => setShowDeleteModal(true)}>
            <i className="bi bi-trash me-2"></i>
            Delete
          </Button>
        </div>
      </div>

      {showHelp && (
        <Alert variant="info" className="mb-4">
          <Alert.Heading>Batch Details</Alert.Heading>
          <p>
            This page shows the details of a cycle count batch and all items included in it.
            You can start counting, assign items to users, and submit count results.
          </p>
        </Alert>
      )}

      <Row className="mb-4">
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Batch Details</h5>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Name:</Col>
                <Col md={8}>{batch.name}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Status:</Col>
                <Col md={8}>
                  <Badge bg={formatStatus(batch.status).variant}>
                    {formatStatus(batch.status).label}
                  </Badge>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Schedule:</Col>
                <Col md={8}>
                  {batch.schedule ? (
                    <Link to={`/cycle-counts/schedules/${batch.schedule.id}`}>
                      {batch.schedule.name}
                    </Link>
                  ) : (
                    'No schedule'
                  )}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Start Date:</Col>
                <Col md={8}>
                  {batch.start_date ? new Date(batch.start_date).toLocaleDateString() : 'Not set'}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">End Date:</Col>
                <Col md={8}>
                  {batch.end_date ? new Date(batch.end_date).toLocaleDateString() : 'Not set'}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Created:</Col>
                <Col md={8}>{new Date(batch.created_at).toLocaleString()}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Notes:</Col>
                <Col md={8}>{batch.notes || 'No notes'}</Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Progress</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <ProgressBar
                  now={calculateProgress()}
                  label={`${calculateProgress()}%`}
                  variant="success"
                  className="mb-2"
                  style={{ height: '25px' }}
                />
                <p className="text-center text-muted">
                  {items.filter(item => item.status === 'counted').length} of {items.length} items counted
                </p>
              </div>

              <Row className="mb-3">
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">{items.length}</h2>
                    <p className="text-muted mb-0">Total Items</p>
                  </div>
                </Col>
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">
                      {items.filter(item => item.status === 'counted').length}
                    </h2>
                    <p className="text-muted mb-0">Counted</p>
                  </div>
                </Col>
              </Row>
              <Row>
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">
                      {items.filter(item => item.status === 'assigned').length}
                    </h2>
                    <p className="text-muted mb-0">Assigned</p>
                  </div>
                </Col>
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">
                      {items.filter(item => item.status === 'pending').length}
                    </h2>
                    <p className="text-muted mb-0">Pending</p>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Export/Import Section */}
      <Row className="mb-4">
        <Col>
          <CycleCountExportImport
            batchId={id}
            batchName={batch.name}
            onImportSuccess={() => {
              // Refresh items after import
              dispatch(fetchCycleCountItems({ batchId: id }));
            }}
          />
        </Col>
      </Row>

      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Items</h5>
        </Card.Header>
        <Card.Body>
          <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
            <Form.Group className="d-flex align-items-center">
              <Form.Label className="me-2 mb-0">Status:</Form.Label>
              <Form.Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                style={{ width: '150px' }}
              >
                <option value="all">All</option>
                <option value="pending">Pending</option>
                <option value="assigned">Assigned</option>
                <option value="counted">Counted</option>
                <option value="skipped">Skipped</option>
              </Form.Select>
            </Form.Group>

            <InputGroup style={{ width: '300px' }}>
              <InputGroup.Text>
                <i className="bi bi-search"></i>
              </InputGroup.Text>
              <Form.Control
                type="text"
                placeholder="Search items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>
          </div>

          {itemsLoading ? (
            <div className="text-center p-3">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </div>
          ) : itemsError ? (
            <Alert variant="danger">
              <Alert.Heading>Error Loading Items</Alert.Heading>
              <p>{itemsError.error || 'An error occurred while loading items'}</p>
            </Alert>
          ) : sortedItems.length === 0 ? (
            <div className="text-center p-5">
              <p className="text-muted">No items found for this batch</p>
            </div>
          ) : (
            <div className="table-responsive">
              <Table hover>
                <thead>
                  <tr>
                    <th onClick={() => handleSort('id')} className="cursor-pointer">
                      ID {sortField === 'id' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th onClick={() => handleSort('item_type')} className="cursor-pointer">
                      Type {sortField === 'item_type' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th onClick={() => handleSort('item_name')} className="cursor-pointer">
                      Name {sortField === 'item_name' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th onClick={() => handleSort('expected_quantity')} className="cursor-pointer">
                      Qty {sortField === 'expected_quantity' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th onClick={() => handleSort('location')} className="cursor-pointer">
                      Location {sortField === 'location' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th onClick={() => handleSort('status')} className="cursor-pointer">
                      Status {sortField === 'status' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedItems.map((item) => (
                    <tr key={item.id}>
                      <td>{item.id}</td>
                      <td>{item.item_type === 'tool' ? 'Tool' : 'Chemical'}</td>
                      <td>{item.item_name}</td>
                      <td>{item.expected_quantity}</td>
                      <td>{item.location}</td>
                      <td>
                        <Badge bg={formatItemStatus(item.status).variant}>
                          {formatItemStatus(item.status).label}
                        </Badge>
                      </td>
                      <td>
                        {item.status !== 'counted' && (
                          <Button
                            variant="outline-primary"
                            size="sm"
                            className="me-2"
                            onClick={() => handleOpenCountModal(item)}
                          >
                            Count
                          </Button>
                        )}
                        {item.status === 'counted' && (
                          <Button
                            as={Link}
                            to={`/cycle-counts/items/${item.id}/result`}
                            variant="outline-success"
                            size="sm"
                          >
                            View Result
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>

      <ConfirmModal
        show={showDeleteModal}
        onHide={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
        title="Delete Batch"
        message={`Are you sure you want to delete the batch "${batch.name}"? This action cannot be undone.`}
        confirmButtonText="Delete Batch"
        confirmButtonVariant="danger"
      />

      <Modal
        show={showCountModal}
        onHide={() => setShowCountModal(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Count Item</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedItem && (
            <CycleCountItemForm
              item={selectedItem}
              onSuccess={() => {
                setShowCountModal(false);
                // Refresh items after count
                dispatch(fetchCycleCountItems({ batchId: id }));
              }}
            />
          )}
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default CycleCountBatchDetailPage;
