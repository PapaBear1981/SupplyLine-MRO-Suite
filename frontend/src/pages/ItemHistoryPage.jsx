import { useState } from 'react';
import { Container, Card, Form, Button, Row, Col, Badge, Alert, Spinner, Pagination } from 'react-bootstrap';
import { FaSearch, FaHistory, FaBox, FaWarehouse, FaTruck, FaCheckCircle, FaTimesCircle, FaExclamationTriangle, FaTools, FaFlask, FaBoxOpen, FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import axios from 'axios';
import './ItemHistoryPage.css';

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

  const getItemTypeIcon = (itemType) => {
    switch (itemType) {
      case 'tool':
        return <FaTools className="me-2" />;
      case 'chemical':
        return <FaFlask className="me-2" />;
      case 'expendable':
        return <FaBoxOpen className="me-2" />;
      default:
        return <FaBox className="me-2" />;
    }
  };

  const getEventIcon = (eventType) => {
    if (eventType.includes('transfer')) return <FaTruck />;
    if (eventType === 'issuance' || eventType === 'kit_issuance') return <FaCheckCircle />;
    if (eventType === 'checkout') return <FaCheckCircle />;
    if (eventType === 'return') return <FaCheckCircle />;
    if (eventType === 'retirement') return <FaTimesCircle />;
    if (eventType === 'creation') return <FaBox />;
    if (eventType === 'status_change') return <FaExclamationTriangle />;
    return <FaHistory />;
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
    // Scroll to timeline section
    const timelineElement = document.querySelector('.history-timeline-card');
    if (timelineElement) {
      timelineElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
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
    <Container fluid className="item-history-page">
      <div className="page-header fade-in">
        <h1 className="page-title">
          <FaHistory className="me-3" />
          Item History Lookup
        </h1>
        <p className="page-subtitle">
          Search for complete history of any chemical, expendable, or tool item
        </p>
      </div>

      {/* Search Form */}
      <Card className="search-card fade-in stagger-1">
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Row>
              <Col md={5}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold">
                    Part Number / Tool Number
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="identifier"
                    value={searchForm.identifier}
                    onChange={handleInputChange}
                    placeholder="e.g., T-12345 or CHEM-001"
                    className="search-input"
                    disabled={loading}
                  />
                  <Form.Text className="text-muted">
                    Enter the part number for chemicals/expendables or tool number for tools
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={5}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold">
                    Lot Number / Serial Number
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="tracking_number"
                    value={searchForm.tracking_number}
                    onChange={handleInputChange}
                    placeholder="e.g., LOT-251014-0001 or SN-001"
                    className="search-input"
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
                    className="w-100 search-button"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <FaSearch className="me-2" />
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
        <Alert variant="danger" className="mt-4 fade-in" onClose={() => setError(null)} dismissible>
          <FaExclamationTriangle className="me-2" />
          {error}
        </Alert>
      )}

      {/* No Results Message */}
      {searched && !loading && !historyData && !error && (
        <Alert variant="info" className="mt-4 fade-in">
          <FaExclamationTriangle className="me-2" />
          No item found with the provided identifiers. Please check your input and try again.
        </Alert>
      )}

      {/* Results */}
      {historyData && historyData.item_found && (
        <div className="results-container fade-in stagger-2">
          {/* Item Details Card */}
          <Card className="item-details-card mb-4">
            <Card.Header className="item-details-header">
              <h4 className="mb-0">
                {getItemTypeIcon(historyData.item_type)}
                {historyData.item_type.charAt(0).toUpperCase() + historyData.item_type.slice(1)} Details
              </h4>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <div className="detail-item">
                    <strong>Identifier:</strong>
                    <span>{historyData.item_details.part_number || historyData.item_details.tool_number}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Tracking Number:</strong>
                    <span>
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
                        <Badge bg="success" className="clickable-lot-badge">
                          {historyData.item_details.serial_number || historyData.item_details.lot_number} <FaSearch className="ms-1" size={10} />
                        </Badge>
                      </Button>
                    </span>
                  </div>
                  <div className="detail-item">
                    <strong>Description:</strong>
                    <span>{historyData.item_details.description || 'N/A'}</span>
                  </div>
                  {historyData.item_details.category && (
                    <div className="detail-item">
                      <strong>Category:</strong>
                      <span>{historyData.item_details.category}</span>
                    </div>
                  )}
                </Col>
                <Col md={6}>
                  <div className="detail-item">
                    <strong>Status:</strong>
                    <Badge bg={historyData.item_details.status === 'available' ? 'success' : 
                               historyData.item_details.status === 'retired' ? 'danger' : 'warning'}>
                      {historyData.item_details.status}
                    </Badge>
                  </div>
                  <div className="detail-item">
                    <strong>Current Location:</strong>
                    <span>
                      {historyData.current_location.type === 'warehouse' && <FaWarehouse className="me-1" />}
                      {historyData.current_location.type === 'kit' && <FaBox className="me-1" />}
                      {historyData.current_location.name}
                      {historyData.current_location.details && ` - ${historyData.current_location.details}`}
                    </span>
                  </div>
                  {historyData.item_details.quantity !== undefined && (
                    <div className="detail-item">
                      <strong>Quantity:</strong>
                      <span>{historyData.item_details.quantity} {historyData.item_details.unit || ''}</span>
                    </div>
                  )}
                </Col>
              </Row>

              {/* Parent/Child Lot Information */}
              {(historyData.parent_lot || (historyData.child_lots && historyData.child_lots.length > 0)) && (
                <div className="lot-lineage mt-4">
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
                        <Badge bg="warning" className="clickable-lot-badge me-2">
                          {historyData.parent_lot.lot_number} <FaSearch className="ms-1" size={10} />
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
                              <Badge bg="info" className="clickable-lot-badge me-2">
                                {child.lot_number} <FaSearch className="ms-1" size={10} />
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
          <Card className="history-timeline-card">
            <Card.Header className="history-timeline-header">
              <h4 className="mb-0">
                <FaHistory className="me-2" />
                Complete History ({historyData.history.length} events)
              </h4>
            </Card.Header>
            <Card.Body>
              {historyData.history.length === 0 ? (
                <Alert variant="info">No history events found for this item.</Alert>
              ) : (
                <>
                  <div className="timeline">
                    {getPaginatedEvents().map((event, index) => (
                      <div key={index} className={`timeline-item fade-in stagger-${Math.min(index, 5)}`}>
                        <div className="timeline-marker">
                          <div className={`timeline-icon bg-${getEventColor(event.event_type)}`}>
                            {getEventIcon(event.event_type)}
                          </div>
                        </div>
                        <div className="timeline-content">
                          <div className="timeline-header">
                            <Badge bg={getEventColor(event.event_type)} className="event-badge">
                              {event.event_type.replace(/_/g, ' ').toUpperCase()}
                            </Badge>
                            <span className="timeline-date">{formatDate(event.timestamp)}</span>
                          </div>
                          <div className="timeline-description">{event.description}</div>
                          <div className="timeline-user">
                            <small className="text-muted">By: {event.user}</small>
                          </div>
                          {event.details && Object.keys(event.details).length > 0 && (
                            <div className="timeline-details">
                              {Object.entries(event.details).map(([key, value]) => (
                                value && key !== 'child_lot_status' && (
                                  <div key={key} className="detail-row">
                                    <span className="detail-key">{key.replace(/_/g, ' ')}:</span>
                                    <span className="detail-value">
                                      {key === 'child_lot_number' ? (
                                        <div className="d-inline-flex align-items-center gap-2">
                                          <Button
                                            variant="link"
                                            size="sm"
                                            className="p-0 text-decoration-none"
                                            onClick={() => handleLotClick(historyData.item_details.part_number, value)}
                                            title="Click to view history of this child lot"
                                          >
                                            <Badge bg="info" className="clickable-lot-badge">
                                              {value} <FaSearch className="ms-1" size={10} />
                                            </Badge>
                                          </Button>
                                          {event.details.child_lot_status && (
                                            <Badge bg={getStatusBadgeColor(event.details.child_lot_status)} className="ms-2">
                                              {event.details.child_lot_status}
                                            </Badge>
                                          )}
                                        </div>
                                      ) : (
                                        typeof value === 'object' ? JSON.stringify(value) : value
                                      )}
                                    </span>
                                  </div>
                                )
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pagination Controls */}
                  {getTotalPages() > 1 && (
                    <div className="pagination-container mt-4">
                      <div className="d-flex justify-content-between align-items-center">
                        <div className="pagination-info">
                          <small className="text-muted">
                            Showing {((currentPage - 1) * eventsPerPage) + 1} - {Math.min(currentPage * eventsPerPage, historyData.history.length)} of {historyData.history.length} events
                          </small>
                        </div>
                        <Pagination className="mb-0">
                          <Pagination.Prev
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                          >
                            <FaChevronLeft className="me-1" /> Previous
                          </Pagination.Prev>

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
                          >
                            Next <FaChevronRight className="ms-1" />
                          </Pagination.Next>
                        </Pagination>
                      </div>
                    </div>
                  )}
                </>
              )}
            </Card.Body>
          </Card>
        </div>
      )}
    </Container>
  );
};

export default ItemHistoryPage;
