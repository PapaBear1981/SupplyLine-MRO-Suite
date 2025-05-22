import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, Table, Badge, Form, InputGroup, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchCycleCountSchedules } from '../../store/cycleCountSlice';

const CycleCountScheduleList = () => {
  const dispatch = useDispatch();
  const { items, loading, error } = useSelector((state) => state.cycleCount.schedules);
  const [searchTerm, setSearchTerm] = useState('');
  const [showActiveOnly, setShowActiveOnly] = useState(true);
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');

  useEffect(() => {
    dispatch(fetchCycleCountSchedules({ active_only: showActiveOnly }));
  }, [dispatch, showActiveOnly]);

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredSchedules = items.filter((schedule) => {
    return (
      (schedule.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (schedule.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (schedule.method || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (schedule.frequency || '').toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const sortedSchedules = [...filteredSchedules].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    if (sortField === 'created_at' || sortField === 'updated_at') {
      // Handle invalid or missing dates
      try {
        aValue = aValue ? new Date(aValue) : new Date(0);
        bValue = bValue ? new Date(bValue) : new Date(0);
      } catch (error) {
        console.error('Error parsing date:', error);
        aValue = new Date(0);
        bValue = new Date(0);
      }
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
        <Alert.Heading>Error Loading Schedules</Alert.Heading>
        <p>{error.error || 'An error occurred while loading cycle count schedules'}</p>
      </Alert>
    );
  }

  return (
    <div className="p-3">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <Form.Check
          type="switch"
          id="active-only-switch"
          label="Show active schedules only"
          checked={showActiveOnly}
          onChange={(e) => setShowActiveOnly(e.target.checked)}
        />
        <InputGroup style={{ width: '300px' }}>
          <InputGroup.Text>
            <i className="bi bi-search"></i>
          </InputGroup.Text>
          <Form.Control
            type="text"
            placeholder="Search schedules..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>
      </div>

      {sortedSchedules.length === 0 ? (
        <div className="text-center p-5">
          <p className="text-muted">No cycle count schedules found</p>
          <Button as={Link} to="/cycle-counts/schedules/new" variant="primary">
            Create New Schedule
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
                <th onClick={() => handleSort('frequency')} className="cursor-pointer">
                  Frequency {sortField === 'frequency' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th onClick={() => handleSort('method')} className="cursor-pointer">
                  Method {sortField === 'method' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th onClick={() => handleSort('created_at')} className="cursor-pointer">
                  Created {sortField === 'created_at' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedSchedules.map((schedule) => (
                <tr key={schedule.id}>
                  <td>{schedule.name}</td>
                  <td>{formatFrequency(schedule.frequency)}</td>
                  <td>{formatMethod(schedule.method)}</td>
                  <td>{new Date(schedule.created_at).toLocaleDateString()}</td>
                  <td>
                    <Badge bg={schedule.is_active ? 'success' : 'secondary'}>
                      {schedule.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td>
                    <Button
                      as={Link}
                      to={`/cycle-counts/schedules/${schedule.id}`}
                      variant="outline-primary"
                      size="sm"
                      className="me-2"
                    >
                      View
                    </Button>
                    <Button
                      as={Link}
                      to={`/cycle-counts/schedules/${schedule.id}/edit`}
                      variant="outline-secondary"
                      size="sm"
                      className="me-2"
                    >
                      Edit
                    </Button>
                    <Button
                      as={Link}
                      to={`/cycle-counts/batches/new?schedule=${schedule.id}`}
                      variant="outline-success"
                      size="sm"
                    >
                      Create Batch
                    </Button>
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

// Helper functions to format values
const formatFrequency = (frequency) => {
  const map = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    quarterly: 'Quarterly',
    annual: 'Annual'
  };
  return map[frequency] || frequency;
};

const formatMethod = (method) => {
  const map = {
    ABC: 'ABC Analysis',
    random: 'Random Sampling',
    location: 'By Location',
    category: 'By Category'
  };
  return map[method] || method;
};

export default CycleCountScheduleList;
