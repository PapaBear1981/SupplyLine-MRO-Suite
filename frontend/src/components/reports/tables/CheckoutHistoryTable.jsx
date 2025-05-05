import { useState } from 'react';
import { Table, Form, InputGroup, Badge, Card } from 'react-bootstrap';

const CheckoutHistoryTable = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('checkout_date');
  const [sortDirection, setSortDirection] = useState('desc');

  if (!data || !data.checkouts || data.checkouts.length === 0) {
    return (
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Checkout History</h5>
        </Card.Header>
        <Card.Body className="text-center text-muted p-5">
          No checkout history data available
        </Card.Body>
      </Card>
    );
  }

  // Filter checkouts based on search term
  const filteredCheckouts = data.checkouts.filter(checkout => {
    const searchLower = searchTerm.toLowerCase();
    return (
      checkout.tool_number.toLowerCase().includes(searchLower) ||
      (checkout.serial_number && checkout.serial_number.toLowerCase().includes(searchLower)) ||
      (checkout.description && checkout.description.toLowerCase().includes(searchLower)) ||
      checkout.user_name.toLowerCase().includes(searchLower)
    );
  });

  // Sort checkouts based on sort field and direction
  const sortedCheckouts = [...filteredCheckouts].sort((a, b) => {
    if (sortField === 'checkout_date' || sortField === 'return_date') {
      const aDate = a[sortField] ? new Date(a[sortField]) : new Date(0);
      const bDate = b[sortField] ? new Date(b[sortField]) : new Date(0);
      
      if (sortDirection === 'asc') {
        return aDate - bDate;
      } else {
        return bDate - aDate;
      }
    } else {
      const aValue = a[sortField] || '';
      const bValue = b[sortField] || '';
      
      if (sortDirection === 'asc') {
        return aValue.localeCompare(bValue);
      } else {
        return bValue.localeCompare(aValue);
      }
    }
  });

  // Handle sort click
  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get status badge
  const getStatusBadge = (checkout) => {
    if (checkout.return_date) {
      return <Badge bg="success">Returned</Badge>;
    } else if (checkout.expected_return_date && new Date(checkout.expected_return_date) < new Date()) {
      return <Badge bg="danger">Overdue</Badge>;
    } else {
      return <Badge bg="warning">Checked Out</Badge>;
    }
  };

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Checkout History</h5>
          <InputGroup style={{ width: '300px' }}>
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search checkouts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table hover className="mb-0">
            <thead className="bg-light">
              <tr>
                <th 
                  onClick={() => handleSort('tool_number')}
                  className="cursor-pointer"
                >
                  Tool # {sortField === 'tool_number' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th 
                  onClick={() => handleSort('description')}
                  className="cursor-pointer"
                >
                  Description {sortField === 'description' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th 
                  onClick={() => handleSort('user_name')}
                  className="cursor-pointer"
                >
                  User {sortField === 'user_name' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th 
                  onClick={() => handleSort('checkout_date')}
                  className="cursor-pointer"
                >
                  Checkout Date {sortField === 'checkout_date' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th 
                  onClick={() => handleSort('return_date')}
                  className="cursor-pointer"
                >
                  Return Date {sortField === 'return_date' && (
                    <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                  )}
                </th>
                <th>Status</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {sortedCheckouts.map((checkout) => (
                <tr key={checkout.id}>
                  <td>{checkout.tool_number}</td>
                  <td>{checkout.description || 'N/A'}</td>
                  <td>{checkout.user_name}</td>
                  <td>{formatDate(checkout.checkout_date)}</td>
                  <td>{formatDate(checkout.return_date)}</td>
                  <td>{getStatusBadge(checkout)}</td>
                  <td>
                    {checkout.duration ? `${checkout.duration} days` : 'N/A'}
                  </td>
                </tr>
              ))}
              {sortedCheckouts.length === 0 && (
                <tr>
                  <td colSpan="7" className="text-center py-4">
                    No checkouts found matching your search criteria
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </div>
      </Card.Body>
      <Card.Footer className="bg-light">
        <small className="text-muted">
          Showing {sortedCheckouts.length} of {data.checkouts.length} checkouts
        </small>
      </Card.Footer>
    </Card>
  );
};

export default CheckoutHistoryTable;
