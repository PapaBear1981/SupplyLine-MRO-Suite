import { useState } from 'react';
import { Table, Form, InputGroup, Badge, Card, Row, Col } from 'react-bootstrap';

const ToolInventoryTable = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('tool_number');
  const [sortDirection, setSortDirection] = useState('asc');

  if (!data || data.length === 0) {
    return (
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Tool Inventory</h5>
        </Card.Header>
        <Card.Body className="text-center text-muted p-5">
          No tool inventory data available
        </Card.Body>
      </Card>
    );
  }

  // Filter tools based on search term
  const filteredTools = data.filter(tool => {
    const searchLower = searchTerm.toLowerCase();
    return (
      tool.tool_number.toLowerCase().includes(searchLower) ||
      tool.serial_number.toLowerCase().includes(searchLower) ||
      (tool.description && tool.description.toLowerCase().includes(searchLower)) ||
      (tool.location && tool.location.toLowerCase().includes(searchLower)) ||
      (tool.category && tool.category.toLowerCase().includes(searchLower))
    );
  });

  // Sort tools based on sort field and direction
  const sortedTools = [...filteredTools].sort((a, b) => {
    const aValue = a[sortField] || '';
    const bValue = b[sortField] || '';

    if (sortDirection === 'asc') {
      return aValue.localeCompare(bValue);
    } else {
      return bValue.localeCompare(aValue);
    }
  });

  // Handle sort click
  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Calculate summary statistics
  const totalTools = data.length;
  const availableTools = data.filter(tool => tool.status === 'available').length;
  const checkedOutTools = data.filter(tool => tool.status === 'checked_out').length;
  const maintenanceTools = data.filter(tool => tool.status === 'maintenance').length;
  const retiredTools = data.filter(tool => tool.status === 'retired').length;

  // Get status badge variant
  const getStatusBadge = (status) => {
    switch (status) {
      case 'available':
        return <Badge bg="success">Available</Badge>;
      case 'checked_out':
        return <Badge bg="warning">Checked Out</Badge>;
      case 'maintenance':
        return <Badge bg="info">Maintenance</Badge>;
      case 'retired':
        return <Badge bg="danger">Retired</Badge>;
      default:
        return <Badge bg="secondary">{status}</Badge>;
    }
  };

  return (
    <div>
      {/* Summary Statistics */}
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Inventory Summary</h5>
        </Card.Header>
        <Card.Body>
          <Row className="text-center">
            <Col xs={6} md={2} className="mb-3">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body>
                  <h3 className="text-primary">{totalTools}</h3>
                  <div className="text-muted small">Total Tools</div>
                </Card.Body>
              </Card>
            </Col>
            <Col xs={6} md={2} className="mb-3">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body>
                  <h3 className="text-success">{availableTools}</h3>
                  <div className="text-muted small">Available</div>
                </Card.Body>
              </Card>
            </Col>
            <Col xs={6} md={3} className="mb-3">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body>
                  <h3 className="text-warning">{checkedOutTools}</h3>
                  <div className="text-muted small">Checked Out</div>
                </Card.Body>
              </Card>
            </Col>
            <Col xs={6} md={2} className="mb-3">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body>
                  <h3 className="text-info">{maintenanceTools}</h3>
                  <div className="text-muted small">In Maintenance</div>
                </Card.Body>
              </Card>
            </Col>
            <Col xs={6} md={3} className="mb-3">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body>
                  <h3 className="text-danger">{retiredTools}</h3>
                  <div className="text-muted small">Retired</div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Search and Table */}
      <Card className="shadow-sm">
        <Card.Header className="bg-light">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Details</h5>
            <InputGroup style={{ width: '300px' }}>
              <InputGroup.Text>
                <i className="bi bi-search"></i>
              </InputGroup.Text>
              <Form.Control
                type="text"
                placeholder="Search tools..."
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
                    onClick={() => handleSort('serial_number')}
                    className="cursor-pointer"
                  >
                    Serial # {sortField === 'serial_number' && (
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
                    onClick={() => handleSort('category')}
                    className="cursor-pointer"
                  >
                    Category {sortField === 'category' && (
                      <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                    )}
                  </th>
                  <th
                    onClick={() => handleSort('location')}
                    className="cursor-pointer"
                  >
                    Location {sortField === 'location' && (
                      <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                    )}
                  </th>
                  <th
                    onClick={() => handleSort('status')}
                    className="cursor-pointer"
                  >
                    Status {sortField === 'status' && (
                      <i className={`bi bi-arrow-${sortDirection === 'asc' ? 'up' : 'down'}`}></i>
                    )}
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedTools.map((tool) => (
                  <tr key={tool.id}>
                    <td>{tool.tool_number}</td>
                    <td>{tool.serial_number}</td>
                    <td>{tool.description || 'N/A'}</td>
                    <td>{tool.category || 'General'}</td>
                    <td>{tool.location || 'N/A'}</td>
                    <td>{getStatusBadge(tool.status)}</td>
                  </tr>
                ))}
                {sortedTools.length === 0 && (
                  <tr>
                    <td colSpan="6" className="text-center py-4">
                      No tools found matching your search criteria
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>
        </Card.Body>
        <Card.Footer className="bg-light">
          <small className="text-muted">
            Showing {sortedTools.length} of {data.length} tools
          </small>
        </Card.Footer>
      </Card>
    </div>
  );
};

export default ToolInventoryTable;
