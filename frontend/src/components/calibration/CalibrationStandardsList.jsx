import { useState, useEffect } from 'react';
import { Table, Button, Spinner, Alert, Form, InputGroup, Badge, Pagination } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const CalibrationStandardsList = () => {
  const [standards, setStandards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [showExpired, setShowExpired] = useState(false);
  const [showExpiringSoon, setShowExpiringSoon] = useState(false);

  useEffect(() => {
    const fetchCalibrationStandards = async () => {
      try {
        setLoading(true);
        
        // Build query parameters
        const params = new URLSearchParams();
        params.append('page', page);
        params.append('limit', 10);
        
        if (showExpired) {
          params.append('expired', true);
        }
        
        if (showExpiringSoon) {
          params.append('expiring_soon', true);
        }
        
        const response = await api.get(`/calibration-standards?${params.toString()}`);
        setStandards(response.data.standards);
        setTotalPages(response.data.pagination.pages);
        setError(null);
      } catch (err) {
        console.error('Error fetching calibration standards:', err);
        setError('Failed to load calibration standards. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCalibrationStandards();
  }, [page, showExpired, showExpiringSoon]);

  const handleSearch = (e) => {
    e.preventDefault();
    // Search by standard name or number
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

  if (loading && standards.length === 0) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" role="status" />
        <span className="ms-2">Loading calibration standards...</span>
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
          <div className="d-flex flex-wrap gap-3 mb-3">
            <div className="flex-grow-1">
              <InputGroup>
                <Form.Control
                  placeholder="Search by standard name or number"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <Button variant="primary" type="submit">
                  <i className="bi bi-search"></i>
                </Button>
              </InputGroup>
            </div>
          </div>
          
          <div className="d-flex gap-3">
            <Form.Check 
              type="switch"
              id="show-expired"
              label="Show Expired"
              checked={showExpired}
              onChange={(e) => setShowExpired(e.target.checked)}
            />
            <Form.Check 
              type="switch"
              id="show-expiring-soon"
              label="Show Expiring Soon"
              checked={showExpiringSoon}
              onChange={(e) => setShowExpiringSoon(e.target.checked)}
            />
          </div>
        </Form>
      </div>

      {standards.length === 0 ? (
        <Alert variant="info">
          <Alert.Heading>No Calibration Standards</Alert.Heading>
          <p>No calibration standards found matching the current filters.</p>
        </Alert>
      ) : (
        <>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Name</th>
                <th>Standard Number</th>
                <th>Certification Date</th>
                <th>Expiration Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {standards.map((standard) => (
                <tr key={standard.id}>
                  <td>{standard.name}</td>
                  <td>{standard.standard_number}</td>
                  <td>{new Date(standard.certification_date).toLocaleDateString()}</td>
                  <td>{new Date(standard.expiration_date).toLocaleDateString()}</td>
                  <td>
                    {standard.is_expired ? (
                      <Badge bg="danger">Expired</Badge>
                    ) : standard.is_expiring_soon ? (
                      <Badge bg="warning">Expiring Soon</Badge>
                    ) : (
                      <Badge bg="success">Valid</Badge>
                    )}
                  </td>
                  <td>
                    <div className="d-flex gap-2">
                      <Button
                        as={Link}
                        to={`/calibration-standards/${standard.id}`}
                        variant="info"
                        size="sm"
                      >
                        View
                      </Button>
                      <Button
                        as={Link}
                        to={`/calibration-standards/${standard.id}/edit`}
                        variant="primary"
                        size="sm"
                      >
                        Edit
                      </Button>
                    </div>
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

export default CalibrationStandardsList;
