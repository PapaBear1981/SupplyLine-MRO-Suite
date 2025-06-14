import { useState, useEffect } from 'react';
import { Table, Button, Spinner, Alert, Form, InputGroup, Pagination } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import { formatDate } from '../../utils/dateUtils';

const CalibrationHistoryList = () => {
  const [calibrations, setCalibrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [toolId, setToolId] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    const fetchCalibrationHistory = async () => {
      try {
        setLoading(true);

        // Build query parameters
        const params = new URLSearchParams();
        params.append('page', page);
        params.append('limit', 10);

        if (toolId) {
          params.append('tool_id', toolId);
        }

        if (status) {
          params.append('status', status);
        }

        const response = await api.get(`/calibrations?${params.toString()}`);
        setCalibrations(response.data.calibrations);
        setTotalPages(response.data.pagination.pages);
        setError(null);
      } catch (err) {
        console.error('Error fetching calibration history:', err);
        setError('Failed to load calibration history. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCalibrationHistory();
  }, [page, toolId, status]);

  const handleSearch = (e) => {
    e.preventDefault();
    // Search by tool number or serial number
    // This would typically call an API endpoint with the search term
    console.log('Searching for:', searchTerm);
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const renderPagination = () => {
    const items = [];

    // Previous button
    items.push(
      <Pagination.Prev
        key="prev"
        onClick={() => handlePageChange(Math.max(1, page - 1))}
        disabled={page === 1}
      />
    );

    // First page
    items.push(
      <Pagination.Item
        key={1}
        active={page === 1}
        onClick={() => handlePageChange(1)}
      >
        1
      </Pagination.Item>
    );

    // Ellipsis if needed
    if (page > 3) {
      items.push(<Pagination.Ellipsis key="ellipsis1" disabled />);
    }

    // Pages around current
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) {
      items.push(
        <Pagination.Item
          key={i}
          active={page === i}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </Pagination.Item>
      );
    }

    // Ellipsis if needed
    if (page < totalPages - 2) {
      items.push(<Pagination.Ellipsis key="ellipsis2" disabled />);
    }

    // Last page if not the first page
    if (totalPages > 1) {
      items.push(
        <Pagination.Item
          key={totalPages}
          active={page === totalPages}
          onClick={() => handlePageChange(totalPages)}
        >
          {totalPages}
        </Pagination.Item>
      );
    }

    // Next button
    items.push(
      <Pagination.Next
        key="next"
        onClick={() => handlePageChange(Math.min(totalPages, page + 1))}
        disabled={page === totalPages}
      />
    );

    return <Pagination>{items}</Pagination>;
  };

  if (loading && calibrations.length === 0) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" role="status" />
        <span className="ms-2">Loading calibration history...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error</Alert.Heading>
        <p>{error}</p>
      </Alert>
    );
  }

  return (
    <div>
      <div className="mb-4">
        <Form onSubmit={handleSearch}>
          <div className="d-flex flex-wrap gap-3">
            <div className="flex-grow-1">
              <InputGroup>
                <Form.Control
                  placeholder="Search by tool number or serial number"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Button variant="primary" type="submit">
                  <i className="bi bi-search"></i>
                </Button>
              </InputGroup>
            </div>

            <div>
              <Form.Select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-auto"
              >
                <option value="">All Statuses</option>
                <option value="pass">Pass</option>
                <option value="fail">Fail</option>
                <option value="limited">Limited</option>
              </Form.Select>
            </div>
          </div>
        </Form>
      </div>

      {calibrations.length === 0 ? (
        <Alert variant="info">
          <Alert.Heading>No Calibration Records</Alert.Heading>
          <p>No calibration records found matching the current filters.</p>
        </Alert>
      ) : (
        <>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Tool</th>
                <th>Calibration Date</th>
                <th>Next Due Date</th>
                <th>Performed By</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {calibrations.map((calibration) => (
                <tr key={calibration.id}>
                  <td>
                    <Link to={`/tools/${calibration.tool_id}`}>
                      {calibration.tool_number} - {calibration.serial_number}
                    </Link>
                  </td>
                  <td>{formatDate(calibration.calibration_date)}</td>
                  <td>{formatDate(calibration.next_calibration_date)}</td>
                  <td>{calibration.performed_by_name}</td>
                  <td>
                    <span className={`badge bg-${
                      calibration.calibration_status === 'pass' ? 'success' :
                      calibration.calibration_status === 'fail' ? 'danger' : 'warning'
                    }`}>
                      {calibration.calibration_status === 'pass' ? 'Pass' :
                       calibration.calibration_status === 'fail' ? 'Fail' : 'Limited'}
                    </span>
                  </td>
                  <td>
                    <Button
                      as={Link}
                      to={`/tools/${calibration.tool_id}/calibrations/${calibration.id}`}
                      variant="info"
                      size="sm"
                    >
                      View Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>

          <div className="d-flex justify-content-center mt-4">
            {renderPagination()}
          </div>
        </>
      )}
    </div>
  );
};

export default CalibrationHistoryList;
