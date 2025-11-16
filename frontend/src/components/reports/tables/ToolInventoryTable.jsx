import { useState, useEffect } from 'react';
import { Table, Form, InputGroup, Badge, Card, Row, Col, Pagination } from 'react-bootstrap';

const ToolInventoryTable = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('tool_number');
  const [sortDirection, setSortDirection] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

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

  // Reset to page 1 when search term or sort changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, sortField, sortDirection]);

  // Calculate pagination
  const totalPages = Math.ceil(sortedTools.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedTools = sortedTools.slice(startIndex, endIndex);

  // Pagination handlers
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;

    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);

      let startPage = Math.max(2, currentPage - 1);
      let endPage = Math.min(totalPages - 1, currentPage + 1);

      if (startPage > 2) {
        pages.push('...');
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      if (endPage < totalPages - 1) {
        pages.push('...');
      }

      pages.push(totalPages);
    }

    return pages;
  };

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
                {paginatedTools.map((tool) => (
                  <tr key={tool.id}>
                    <td>{tool.tool_number}</td>
                    <td>{tool.serial_number}</td>
                    <td>{tool.description || 'N/A'}</td>
                    <td>{tool.category || 'General'}</td>
                    <td>{tool.location || 'N/A'}</td>
                    <td>{getStatusBadge(tool.status)}</td>
                  </tr>
                ))}
                {paginatedTools.length === 0 && (
                  <tr>
                    <td colSpan="6" className="text-center py-4">
                      No tools found matching your search criteria
                    </td>
                  </tr>
                )}
              </tbody>
            </Table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="d-flex justify-content-between align-items-center p-3 border-top">
              <div className="text-muted">
                <small>
                  Showing {startIndex + 1}-{Math.min(endIndex, sortedTools.length)} of {sortedTools.length} tools
                </small>
              </div>
              <Pagination className="mb-0">
                <Pagination.First
                  onClick={() => handlePageChange(1)}
                  disabled={currentPage === 1}
                />
                <Pagination.Prev
                  onClick={handlePreviousPage}
                  disabled={currentPage === 1}
                />

                {getPageNumbers().map((page, index) => (
                  page === '...' ? (
                    <Pagination.Ellipsis key={`ellipsis-${index}`} disabled />
                  ) : (
                    <Pagination.Item
                      key={page}
                      active={page === currentPage}
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </Pagination.Item>
                  )
                ))}

                <Pagination.Next
                  onClick={handleNextPage}
                  disabled={currentPage === totalPages}
                />
                <Pagination.Last
                  onClick={() => handlePageChange(totalPages)}
                  disabled={currentPage === totalPages}
                />
              </Pagination>
            </div>
          )}
        </Card.Body>
        <Card.Footer>
          <small className="text-muted">
            Showing {sortedTools.length} of {data.length} tools
            {searchTerm && ` (filtered by "${searchTerm}")`}
          </small>
        </Card.Footer>
      </Card>
    </div>
  );
};

export default ToolInventoryTable;
