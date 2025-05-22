import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, Table, Badge, Form, InputGroup, Spinner, Alert, ProgressBar } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchCycleCountBatches } from '../../store/cycleCountSlice';

const CycleCountBatchList = () => {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.cycleCount.batches);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    const params = {};
    if (statusFilter !== 'all') {
      params.status = statusFilter;
    }
    dispatch(fetchCycleCountBatches(params));
  }, [dispatch, statusFilter]);

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredBatches = items.filter((batch) => {
    return (
      (batch.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (batch.notes || '').toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const sortedBatches = [...filteredBatches].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    if (sortField === 'created_at' || sortField === 'updated_at' || sortField === 'start_date' || sortField === 'end_date') {
      aValue = aValue ? new Date(aValue) : new Date(0);
      bValue = bValue ? new Date(bValue) : new Date(0);
    }

    if (aValue < bValue) {
      return sortDirection === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortDirection === 'asc' ? 1 : -1;
    }
    return 0;
  });

  if (loading) {
    return (
      <div className="text-center p-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Batches</Alert.Heading>
        <p>{error.error || 'An error occurred while loading cycle count batches'}</p>
      </Alert>
    );
  }

  return (
    <div className="p-3">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <Form.Select
          style={{ width: '200px' }}
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </Form.Select>
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
      </div>

      {sortedBatches.length === 0 ? (
        <div className="text-center p-5">
          <p className="text-muted">No cycle count batches found</p>
          <Button as={Link} to="/cycle-counts/batches/new" variant="primary">
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
                <th onClick={() => handleSort('start_date')} className="cursor-pointer">
                  Start Date {sortField === 'start_date' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th>Progress</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedBatches.map((batch) => (
                <tr key={batch.id}>
                  <td>{batch.name}</td>
                  <td>
                    <Badge bg={getBatchStatusColor(batch.status)}>
                      {formatStatus(batch.status)}
                    </Badge>
                  </td>
                  <td>
                    {batch.start_date ? new Date(batch.start_date).toLocaleDateString() : 'Not started'}
                  </td>
                  <td>
                    {batch.item_count && batch.item_count > 0 ? (
                      <div>
                        <ProgressBar
                          now={Math.round(((batch.completed_count || 0) / batch.item_count) * 100)}
                          label={`${batch.completed_count || 0}/${batch.item_count}`}
                          variant={getProgressBarVariant(batch.completed_count || 0, batch.item_count)}
                        />
                      </div>
                    ) : (
                      <span className="text-muted">No items</span>
                    )}
                  </td>
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
                    {batch.status === 'pending' && (
                      <>
                        <Button
                          as={Link}
                          to={`/cycle-counts/batches/${batch.id}/edit`}
                          variant="outline-secondary"
                          size="sm"
                          className="me-2"
                        >
                          Edit
                        </Button>
                        <Button
                          as={Link}
                          to={`/cycle-counts/batches/${batch.id}/count`}
                          variant="outline-success"
                          size="sm"
                        >
                          Start Counting
                        </Button>
                      </>
                    )}
                    {batch.status === 'in_progress' && (
                      <Button
                        as={Link}
                        to={`/cycle-counts/batches/${batch.id}/count`}
                        variant="outline-success"
                        size="sm"
                      >
                        Continue
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </div>
  );
};

// Helper functions
const getBatchStatusColor = (status) => {
  switch (status) {
    case 'pending':
      return 'secondary';
    case 'in_progress':
      return 'primary';
    case 'completed':
      return 'success';
    case 'cancelled':
      return 'danger';
    default:
      return 'secondary';
  }
};

const formatStatus = (status) => {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'in_progress':
      return 'In Progress';
    case 'completed':
      return 'Completed';
    case 'cancelled':
      return 'Cancelled';
    default:
      return status;
  }
};

const getProgressBarVariant = (completed, total) => {
  const percentage = (completed / total) * 100;
  if (percentage === 100) return 'success';
  if (percentage > 60) return 'info';
  if (percentage > 30) return 'warning';
  return 'danger';
};

export default CycleCountBatchList;
