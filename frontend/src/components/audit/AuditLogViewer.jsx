import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Card, Table, Button, Badge, Form, Alert, Pagination, Row, Col
} from 'react-bootstrap';
import { fetchAuditLogs } from '../../store/auditSlice';
import LoadingSpinner from '../common/LoadingSpinner';

const AuditLogViewer = () => {
  const dispatch = useDispatch();
  const { logs, loading, error } = useSelector((state) => state.audit);
  const { user: currentUser } = useSelector((state) => state.auth);

  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [logsPerPage] = useState(20);
  const [totalPages, setTotalPages] = useState(1);

  // State for filters
  const [filters, setFilters] = useState({
    actionType: '',
    startDate: '',
    endDate: '',
    userId: ''
  });

  // Load audit logs on component mount
  useEffect(() => {
    dispatch(fetchAuditLogs({ page: currentPage, limit: logsPerPage }));
  }, [dispatch, currentPage, logsPerPage]);

  // Update total pages when logs change
  useEffect(() => {
    if (logs && logs.total) {
      setTotalPages(Math.ceil(logs.total / logsPerPage));
    }
  }, [logs, logsPerPage]);

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  // Apply filters
  const applyFilters = () => {
    setCurrentPage(1);
    dispatch(fetchAuditLogs({
      page: 1,
      limit: logsPerPage,
      ...filters
    }));
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      actionType: '',
      startDate: '',
      endDate: '',
      userId: ''
    });
    setCurrentPage(1);
    dispatch(fetchAuditLogs({ page: 1, limit: logsPerPage }));
  };

  // Handle page change
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    dispatch(fetchAuditLogs({
      page: pageNumber,
      limit: logsPerPage,
      ...filters
    }));
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Format action type for display
  const formatActionType = (actionType) => {
    return actionType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Get badge variant based on action type
  const getActionBadgeVariant = (actionType) => {
    if (actionType.includes('create')) return 'success';
    if (actionType.includes('update')) return 'info';
    if (actionType.includes('delete')) return 'danger';
    if (actionType.includes('login')) return 'primary';
    if (actionType.includes('logout')) return 'secondary';
    return 'dark';
  };

  // Check if user has permission to view audit logs
  // Admins (is_admin: true) have FULL access to audit logs
  const hasPermission = currentUser?.is_admin || currentUser?.permissions?.includes('system.audit');

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        You do not have permission to access audit logs. Only administrators with audit permissions can view this page.
      </Alert>
    );
  }

  if (loading && !logs.items) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <h3 className="mb-4">Audit Logs</h3>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error.message || 'An error occurred while loading audit logs.'}
        </Alert>
      )}

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Filters</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Action Type</Form.Label>
                <Form.Select
                  name="actionType"
                  value={filters.actionType}
                  onChange={handleFilterChange}
                >
                  <option value="">All Actions</option>
                  <option value="create">Create</option>
                  <option value="update">Update</option>
                  <option value="delete">Delete</option>
                  <option value="login">Login</option>
                  <option value="logout">Logout</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Start Date</Form.Label>
                <Form.Control
                  type="date"
                  name="startDate"
                  value={filters.startDate}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>End Date</Form.Label>
                <Form.Control
                  type="date"
                  name="endDate"
                  value={filters.endDate}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>User ID</Form.Label>
                <Form.Control
                  type="text"
                  name="userId"
                  value={filters.userId}
                  onChange={handleFilterChange}
                  placeholder="Enter user ID"
                />
              </Form.Group>
            </Col>
          </Row>
          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={resetFilters} className="me-2">
              Reset
            </Button>
            <Button variant="primary" onClick={applyFilters}>
              Apply Filters
            </Button>
          </div>
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Audit Logs</h5>
            {logs.total && (
              <span className="text-muted">
                Showing {logs.items?.length || 0} of {logs.total} logs
              </span>
            )}
          </div>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table striped bordered hover className="mb-0">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Action Type</th>
                  <th>Details</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {logs.items && logs.items.length > 0 ? (
                  logs.items.map((log) => (
                    <tr key={log.id}>
                      <td>{log.id}</td>
                      <td>
                        <Badge bg={getActionBadgeVariant(log.action_type)}>
                          {formatActionType(log.action_type)}
                        </Badge>
                      </td>
                      <td>{log.action_details}</td>
                      <td>{formatDate(log.timestamp)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="4" className="text-center py-4">
                      No audit logs found.
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
        {totalPages > 1 && (
          <Card.Footer>
            <div className="d-flex justify-content-center">
              <Pagination>
                <Pagination.First
                  onClick={() => handlePageChange(1)}
                  disabled={currentPage === 1}
                />
                <Pagination.Prev
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                />

                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }

                  return (
                    <Pagination.Item
                      key={pageNum}
                      active={pageNum === currentPage}
                      onClick={() => handlePageChange(pageNum)}
                    >
                      {pageNum}
                    </Pagination.Item>
                  );
                })}

                <Pagination.Next
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                />
                <Pagination.Last
                  onClick={() => handlePageChange(totalPages)}
                  disabled={currentPage === totalPages}
                />
              </Pagination>
            </div>
          </Card.Footer>
        )}
      </Card>
    </div>
  );
};

export default AuditLogViewer;
