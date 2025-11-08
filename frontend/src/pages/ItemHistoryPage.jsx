import { useState } from 'react';
import { Card, Form, Button, Row, Col, Badge, Alert, Spinner, Pagination, Table } from 'react-bootstrap';
import axios from 'axios';

const ItemHistoryPage = () => {
  const [searchForm, setSearchForm] = useState({
    identifier: '',
    tracking_number: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [searched, setSearched] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const eventsPerPage = 5;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!searchForm.identifier.trim() || !searchForm.tracking_number.trim()) {
      setError('Both Part/Tool Number and Lot/Serial Number are required');
      return;
    }

    setLoading(true);
    setError(null);
    setHistoryData(null);
    setSearched(true);
    setCurrentPage(1); // Reset to first page on new search

    try {
      const response = await axios.post('/api/history/lookup', {
        identifier: searchForm.identifier.trim(),
        tracking_number: searchForm.tracking_number.trim()
      });

      setHistoryData(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`No item found with the provided identifiers`);
      } else {
        setError(err.response?.data?.error || 'Failed to fetch item history');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSearchForm({ identifier: '', tracking_number: '' });
    setHistoryData(null);
    setError(null);
    setSearched(false);
    setCurrentPage(1);
  };

  const handleLotClick = async (partNumber, lotNumber) => {
    // Update search form and trigger search for the clicked lot
    setSearchForm({
      identifier: partNumber,
      tracking_number: lotNumber
    });

    setLoading(true);
    setError(null);
    setHistoryData(null);
    setSearched(true);
    setCurrentPage(1); // Reset to first page

    try {
      const response = await axios.post('/api/history/lookup', {
        identifier: partNumber,
        tracking_number: lotNumber
      });

      setHistoryData(response.data);
      // Scroll to top to show the new results
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`No item found with the provided identifiers`);
      } else {
        setError(err.response?.data?.error || 'Failed to fetch item history');
      }
    } finally {
      setLoading(false);
    }
  };

  const getItemTypeLabel = (itemType) => {
    switch (itemType) {
      case 'tool':
        return 'Tool';
      case 'chemical':
        return 'Chemical';
      case 'expendable':
        return 'Expendable';
      default:
        return 'Item';
    }
  };

  const getEventColor = (eventType) => {
    if (eventType.includes('transfer')) return 'primary';
    if (eventType === 'issuance' || eventType === 'kit_issuance') return 'success';
    if (eventType === 'checkout') return 'info';
    if (eventType === 'return') return 'success';
    if (eventType === 'retirement') return 'danger';
    if (eventType === 'creation') return 'secondary';
    if (eventType === 'status_change') return 'warning';
    return 'secondary';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Pagination logic
  const getPaginatedEvents = () => {
    if (!historyData || !historyData.history) return [];
    const startIndex = (currentPage - 1) * eventsPerPage;
    const endIndex = startIndex + eventsPerPage;
    return historyData.history.slice(startIndex, endIndex);
  };

  const getTotalPages = () => {
    if (!historyData || !historyData.history) return 0;
    return Math.ceil(historyData.history.length / eventsPerPage);
  };

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    // Scroll to top of page
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getStatusBadgeColor = (status) => {
    if (!status) return 'secondary';
    const statusLower = status.toLowerCase();
    if (statusLower === 'available') return 'success';
    if (statusLower === 'issued') return 'primary';
    if (statusLower === 'retired' || statusLower === 'expired') return 'danger';
    if (statusLower === 'in_use' || statusLower === 'checked_out') return 'warning';
    return 'secondary';
  };

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <div>
          <h1 className="mb-0">Item History Lookup</h1>
          <p className="text-muted mb-0 mt-2">
            Search for complete history of any chemical, expendable, or tool item
          </p>
        </div>
      </div>

      {/* Search Form */}
      <Card className="mb-4 shadow-sm">
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Row>
              <Col md={5}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold">
                    Part Number / Tool Number
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="identifier"
                    value={searchForm.identifier}
                    onChange={handleInputChange}
                    placeholder="e.g., T-12345 or CHEM-001"
                    disabled={loading}
                  />
                  <Form.Text className="text-muted">
                    Enter the part number for chemicals/expendables or tool number for tools
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={5}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-semibold">
                    Lot Number / Serial Number
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="tracking_number"
                    value={searchForm.tracking_number}
                    onChange={handleInputChange}
                    placeholder="e.g., LOT-251014-0001 or SN-001"
                    disabled={loading}
                  />
                  <Form.Text className="text-muted">
                    Enter the lot number or serial number (items have one or the other, never both)
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={2} className="d-flex align-items-end">
                <div className="w-100 mb-3">
                  <Button
                    type="submit"
                    variant="primary"
                    className="w-100"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-search me-2"></i>
                        Search
                      </>
                    )}
                  </Button>
                  {searched && (
                    <Button
                      variant="outline-secondary"
                      className="w-100 mt-2"
                      onClick={handleReset}
                      disabled={loading}
                    >
                      Reset
                    </Button>
                  )}
                </div>
              </Col>
            </Row>
          </Form>
        </Card.Body>
      </Card>

      {/* Error Message */}
      {error && (
        <Alert variant="danger" onClose={() => setError(null)} dismissible>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      {/* No Results Message */}
      {searched && !loading && !historyData && !error && (
        <Alert variant="info">
          <i className="bi bi-info-circle-fill me-2"></i>
          No item found with the provided identifiers. Please check your input and try again.
        </Alert>
      )}

      {/* Results */}
      {historyData && historyData.item_found && (
        <div>
          {/* Item Details Card */}
          <Card className="mb-4 shadow-sm">
            <Card.Header className="bg-light">
              <h4 className="mb-0">
                {getItemTypeLabel(historyData.item_type)} Details
              </h4>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <div className="mb-3">
                    <strong className="text-muted d-block mb-1">Identifier</strong>
                    <div>{historyData.item_details.part_number || historyData.item_details.tool_number}</div>
                  </div>
                  <div className="mb-3">
                    <strong className="text-muted d-block mb-1">Tracking Number</strong>
                    <div>
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 text-decoration-none"
                        onClick={() => handleLotClick(
                          historyData.item_details.part_number || historyData.item_details.tool_number,
                          historyData.item_details.serial_number || historyData.item_details.lot_number
                        )}
                        title="Click to refresh history for this item"
                      >
                        <Badge bg="success">
                          {historyData.item_details.serial_number || historyData.item_details.lot_number} <i className="bi bi-search ms-1"></i>
                        </Badge>
                      </Button>
                    </div>
                  </div>
                  <div className="mb-3">
                    <strong className="text-muted d-block mb-1">Description</strong>
                    <div>{historyData.item_details.description || 'N/A'}</div>
                  </div>
                  {historyData.item_details.category && (
                    <div className="mb-3">
                      <strong className="text-muted d-block mb-1">Category</strong>
                      <div>{historyData.item_details.category}</div>
                    </div>
                  )}
                </Col>
                <Col md={6}>
                  <div className="mb-3">
                    <strong className="text-muted d-block mb-1">Status</strong>
                    <div>
                      <Badge bg={historyData.item_details.status === 'available' ? 'success' :
                                 historyData.item_details.status === 'retired' ? 'danger' : 'warning'}>
                        {historyData.item_details.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="mb-3">
                    <strong className="text-muted d-block mb-1">Current Location</strong>
                    <div>
                      {historyData.current_location.type === 'warehouse' && <i className="bi bi-building me-1"></i>}
                      {historyData.current_location.type === 'kit' && <i className="bi bi-box me-1"></i>}
                      {historyData.current_location.name}
                      {historyData.current_location.details && ` - ${historyData.current_location.details}`}
                    </div>
                  </div>
                  {historyData.item_details.quantity !== undefined && (
                    <div className="mb-3">
                      <strong className="text-muted d-block mb-1">Quantity</strong>
                      <div>{historyData.item_details.quantity} {historyData.item_details.unit || ''}</div>
                    </div>
                  )}
                </Col>
              </Row>

              {/* Parent/Child Lot Information */}
              {(historyData.parent_lot || (historyData.child_lots && historyData.child_lots.length > 0)) && (
                <div className="border-top pt-4 mt-4">
                  <h6 className="text-muted mb-3">Lot Lineage</h6>
                  {historyData.parent_lot && (
                    <Alert variant="info" className="mb-2">
                      <strong>Parent Lot:</strong>{' '}
                      <Button
                        variant="link"
                        size="sm"
                        className="p-0 text-decoration-none"
                        onClick={() => handleLotClick(historyData.parent_lot.part_number, historyData.parent_lot.lot_number)}
                        title="Click to view history of this parent lot"
                      >
                        <Badge bg="warning" className="me-2">
                          {historyData.parent_lot.lot_number} <i className="bi bi-search ms-1"></i>
                        </Badge>
                      </Button>
                      {historyData.parent_lot.description}
                    </Alert>
                  )}
                  {historyData.child_lots && historyData.child_lots.length > 0 && (
                    <Alert variant="secondary">
                      <strong>Child Lots ({historyData.child_lots.length}):</strong>
                      <ul className="mb-0 mt-2">
                        {historyData.child_lots.map((child, idx) => (
                          <li key={idx}>
                            <Button
                              variant="link"
                              size="sm"
                              className="p-0 text-decoration-none"
                              onClick={() => handleLotClick(child.part_number, child.lot_number)}
                              title="Click to view history of this child lot"
                            >
                              <Badge bg="info" className="me-2">
                                {child.lot_number} <i className="bi bi-search ms-1"></i>
                              </Badge>
                            </Button>
                            {child.description} ({child.quantity} - {child.status})
                          </li>
                        ))}
                      </ul>
                    </Alert>
                  )}
                </div>
              )}
            </Card.Body>
          </Card>

          {/* History Timeline */}
          <Card className="shadow-sm">
            <Card.Header className="bg-light">
              <h4 className="mb-0">
                <i className="bi bi-clock-history me-2"></i>
                Complete History ({historyData.history.length} events)
              </h4>
            </Card.Header>
            <Card.Body>
              {historyData.history.length === 0 ? (
                <Alert variant="info">No history events found for this item.</Alert>
              ) : (
                <>
                  <Table hover responsive>
                    <thead>
                      <tr>
                        <th style={{ width: '15%' }}>Event Type</th>
                        <th style={{ width: '18%' }}>Date & Time</th>
                        <th style={{ width: '35%' }}>Description</th>
                        <th style={{ width: '12%' }}>User</th>
                        <th style={{ width: '20%' }}>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getPaginatedEvents().map((event, index) => (
                        <tr key={index}>
                          <td>
                            <Badge bg={getEventColor(event.event_type)}>
                              {event.event_type.replace(/_/g, ' ').toUpperCase()}
                            </Badge>
                          </td>
                          <td>
                            <small className="text-muted">{formatDate(event.timestamp)}</small>
                          </td>
                          <td>{event.description}</td>
                          <td>
                            <small className="text-muted">{event.user}</small>
                          </td>
                          <td>
                            {event.details && Object.keys(event.details).length > 0 && (
                              <div>
                                {Object.entries(event.details).map(([key, value]) => (
                                  value && key !== 'child_lot_status' && (
                                    <div key={key} className="mb-1">
                                      <small>
                                        <strong className="text-muted">{key.replace(/_/g, ' ')}:</strong>{' '}
                                        {key === 'child_lot_number' ? (
                                          <span className="d-inline-flex align-items-center gap-1">
                                            <Button
                                              variant="link"
                                              size="sm"
                                              className="p-0 text-decoration-none"
                                              onClick={() => handleLotClick(historyData.item_details.part_number, value)}
                                              title="Click to view history of this child lot"
                                            >
                                              <Badge bg="info">
                                                {value} <i className="bi bi-search ms-1"></i>
                                              </Badge>
                                            </Button>
                                            {event.details.child_lot_status && (
                                              <Badge bg={getStatusBadgeColor(event.details.child_lot_status)}>
                                                {event.details.child_lot_status}
                                              </Badge>
                                            )}
                                          </span>
                                        ) : (
                                          typeof value === 'object' ? JSON.stringify(value) : value
                                        )}
                                      </small>
                                    </div>
                                  )
                                ))}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>

                  {/* Pagination Controls */}
                  {getTotalPages() > 1 && (
                    <div className="d-flex justify-content-between align-items-center border-top pt-3 mt-3">
                      <div>
                        <small className="text-muted">
                          Showing {((currentPage - 1) * eventsPerPage) + 1} - {Math.min(currentPage * eventsPerPage, historyData.history.length)} of {historyData.history.length} events
                        </small>
                      </div>
                      <Pagination className="mb-0">
                        <Pagination.Prev
                          onClick={() => handlePageChange(currentPage - 1)}
                          disabled={currentPage === 1}
                        />

                        {[...Array(getTotalPages())].map((_, idx) => {
                          const pageNum = idx + 1;
                          // Show first page, last page, current page, and pages around current
                          if (
                            pageNum === 1 ||
                            pageNum === getTotalPages() ||
                            (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                          ) {
                            return (
                              <Pagination.Item
                                key={pageNum}
                                active={pageNum === currentPage}
                                onClick={() => handlePageChange(pageNum)}
                              >
                                {pageNum}
                              </Pagination.Item>
                            );
                          } else if (
                            pageNum === currentPage - 2 ||
                            pageNum === currentPage + 2
                          ) {
                            return <Pagination.Ellipsis key={pageNum} disabled />;
                          }
                          return null;
                        })}

                        <Pagination.Next
                          onClick={() => handlePageChange(currentPage + 1)}
                          disabled={currentPage === getTotalPages()}
                        />
                      </Pagination>
                    </div>
                  )}
                </>
              )}
            </Card.Body>
          </Card>
        </div>
      )}
    </div>
  );
};

export default ItemHistoryPage;
