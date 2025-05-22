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
  Modal,
  Form,
  InputGroup
} from 'react-bootstrap';
import {
  fetchCycleCountSchedule,
  fetchCycleCountBatches,
  deleteCycleCountSchedule
} from '../store/cycleCountSlice';
import { useHelp } from '../context/HelpContext';
import ConfirmModal from '../components/common/ConfirmModal';

const CycleCountScheduleDetailPage = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { showHelp } = useHelp();

  const { data: schedule, loading: scheduleLoading, error: scheduleError } =
    useSelector((state) => state.cycleCount.currentSchedule);

  const { items: batches, loading: batchesLoading } =
    useSelector((state) => state.cycleCount.batches);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    // Fetch schedule with associated batches
    dispatch(fetchCycleCountSchedule({ id, includeBatches: true }));

    // Fetch all batches for this schedule
    dispatch(fetchCycleCountBatches({ schedule_id: id }));
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
      await dispatch(deleteCycleCountSchedule(id)).unwrap();
      setShowDeleteModal(false);
      navigate('/cycle-counts/schedules');
    } catch (error) {
      console.error('Failed to delete schedule:', error);
    }
  };

  const formatFrequency = (frequency) => {
    const frequencies = {
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      quarterly: 'Quarterly',
      annual: 'Annual'
    };
    return frequencies[frequency] || frequency;
  };

  const formatMethod = (method) => {
    const methods = {
      abc: 'ABC Analysis',
      random: 'Random Selection',
      location: 'By Location',
      category: 'By Category'
    };
    return methods[method] || method;
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

  const filteredBatches = batches
    .filter(batch => batch.schedule_id === parseInt(id))
    .filter(batch =>
      batch.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      batch.status.toLowerCase().includes(searchTerm.toLowerCase())
    );

  const sortedBatches = [...filteredBatches].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  if (scheduleLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (scheduleError) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Schedule</Alert.Heading>
        <p>{scheduleError.error || `An error occurred while loading schedule ${id}`}</p>
      </Alert>
    );
  }

  if (!schedule) {
    return (
      <Alert variant="warning">
        <Alert.Heading>Schedule Not Found</Alert.Heading>
        <p>The requested cycle count schedule could not be found.</p>
        <Button as={Link} to="/cycle-counts/schedules" variant="primary">
          Back to Schedules
        </Button>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <div>
          <h1 className="mb-0">{schedule.name}</h1>
          <p className="text-muted mb-0">
            {formatFrequency(schedule.frequency)} cycle count using {formatMethod(schedule.method)} method
          </p>
        </div>
        <div>
          <Button as={Link} to={`/cycle-counts/schedules/${id}/edit`} variant="primary" className="me-2">
            <i className="bi bi-pencil me-2"></i>
            Edit Schedule
          </Button>
          <Button as={Link} to={`/cycle-counts/batches/new?schedule=${id}`} variant="success" className="me-2">
            <i className="bi bi-clipboard-plus me-2"></i>
            New Batch
          </Button>
          <Button variant="outline-danger" onClick={() => setShowDeleteModal(true)}>
            <i className="bi bi-trash me-2"></i>
            Delete
          </Button>
        </div>
      </div>

      {showHelp && (
        <Alert variant="info" className="mb-4">
          <Alert.Heading>Schedule Details</Alert.Heading>
          <p>
            This page shows the details of a cycle count schedule and all batches associated with it.
            You can edit the schedule, create new count batches, or view existing batches.
          </p>
        </Alert>
      )}

      <Row className="mb-4">
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Schedule Details</h5>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Name:</Col>
                <Col md={8}>{schedule.name}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Description:</Col>
                <Col md={8}>{schedule.description || 'No description provided'}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Frequency:</Col>
                <Col md={8}>{formatFrequency(schedule.frequency)}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Method:</Col>
                <Col md={8}>{formatMethod(schedule.method)}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Status:</Col>
                <Col md={8}>
                  <Badge bg={schedule.is_active ? 'success' : 'secondary'}>
                    {schedule.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Created:</Col>
                <Col md={8}>{new Date(schedule.created_at).toLocaleString()}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Last Updated:</Col>
                <Col md={8}>{new Date(schedule.updated_at).toLocaleString()}</Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Schedule Statistics</h5>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">{filteredBatches.length}</h2>
                    <p className="text-muted mb-0">Total Batches</p>
                  </div>
                </Col>
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">
                      {filteredBatches.filter(b => b.status === 'completed').length}
                    </h2>
                    <p className="text-muted mb-0">Completed Batches</p>
                  </div>
                </Col>
              </Row>
              <Row>
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">
                      {filteredBatches.filter(b => b.status === 'in_progress').length}
                    </h2>
                    <p className="text-muted mb-0">In Progress</p>
                  </div>
                </Col>
                <Col md={6}>
                  <div className="d-flex flex-column align-items-center p-3 border rounded">
                    <h2 className="mb-0">
                      {filteredBatches.filter(b => b.status === 'pending').length}
                    </h2>
                    <p className="text-muted mb-0">Pending</p>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Associated Batches</h5>
          <InputGroup style={{ width: '300px' }}>
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search batches..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Card.Header>
        <Card.Body>
          {batchesLoading ? (
            <div className="text-center p-3">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </div>
          ) : sortedBatches.length === 0 ? (
            <div className="text-center p-5">
              <p className="text-muted">No batches found for this schedule</p>
              <Button as={Link} to={`/cycle-counts/batches/new?schedule=${id}`} variant="primary">
                Create New Batch
              </Button>
            </div>
          ) : (
            <div className="table-responsive">
              <Table hover>
                <thead>
                  <tr>
                    <th onClick={() => handleSort('name')} className="cursor-pointer">
                      Name {sortField === 'name' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th onClick={() => handleSort('status')} className="cursor-pointer">
                      Status {sortField === 'status' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th onClick={() => handleSort('created_at')} className="cursor-pointer">
                      Created {sortField === 'created_at' && (
                        <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                      )}
                    </th>
                    <th>Items</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedBatches.map((batch) => (
                    <tr key={batch.id}>
                      <td>{batch.name}</td>
                      <td>
                        <Badge bg={formatStatus(batch.status).variant}>
                          {formatStatus(batch.status).label}
                        </Badge>
                      </td>
                      <td>{new Date(batch.created_at).toLocaleDateString()}</td>
                      <td>{batch.item_count || 0}</td>
                      <td>
                        <Button
                          as={Link}
                          to={`/cycle-counts/batches/${batch.id}`}
                          variant="outline-primary"
                          size="sm"
                          className="me-2"
                        >
                          View
                        </Button>
                        <Button
                          as={Link}
                          to={`/cycle-counts/batches/${batch.id}/edit`}
                          variant="outline-secondary"
                          size="sm"
                        >
                          Edit
                        </Button>
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
        title="Delete Schedule"
        message={`Are you sure you want to delete the schedule "${schedule.name}"? This action cannot be undone.`}
        confirmText="Delete Schedule"
        confirmVariant="danger"
      />
    </div>
  );
};

export default CycleCountScheduleDetailPage;
