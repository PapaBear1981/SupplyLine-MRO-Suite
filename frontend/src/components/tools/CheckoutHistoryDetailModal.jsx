import { useState, useEffect } from 'react';
import { Modal, Button, Table, Badge, Spinner, Alert, Card, Row, Col } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHistory, faUser, faClock, faCheckCircle, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';

const CheckoutHistoryDetailModal = ({ show, onHide, checkoutId }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [checkoutDetails, setCheckoutDetails] = useState(null);

  useEffect(() => {
    if (!show || !checkoutId) return;

    const controller = new AbortController();
    fetchCheckoutDetails(controller.signal);

    return () => controller.abort();
  }, [show, checkoutId]);

  const fetchCheckoutDetails = async (signal) => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `/api/checkouts/${checkoutId}/details`,
        { credentials: 'include', signal }
      );

      const data = await response.clone().json().catch(() => ({}));

      if (response.ok) {
        setCheckoutDetails(data);
      } else {
        setError(data.error || `Failed to fetch checkout details (HTTP ${response.status})`);
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError('Network error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setCheckoutDetails(null);
    setError('');
    onHide();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (days) => {
    if (days === null || days === undefined) return 'N/A';
    if (days === 0) return 'Same day';
    if (days === 1) return '1 day';
    return `${days} days`;
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Returned':
        return <Badge bg="success"><FontAwesomeIcon icon={faCheckCircle} className="me-1" />Returned</Badge>;
      case 'Overdue':
        return <Badge bg="danger"><FontAwesomeIcon icon={faExclamationTriangle} className="me-1" />Overdue</Badge>;
      case 'Checked Out':
        return <Badge bg="primary"><FontAwesomeIcon icon={faClock} className="me-1" />Checked Out</Badge>;
      default:
        return <Badge bg="secondary">{status}</Badge>;
    }
  };

  const getConditionBadge = (condition) => {
    if (!condition) return <span className="text-muted">Not specified</span>;

    const badgeVariant = {
      'New': 'success',
      'Good': 'success',
      'Fair': 'warning',
      'Poor': 'danger'
    }[condition] || 'secondary';

    return <Badge bg={badgeVariant}>{condition}</Badge>;
  };

  return (
    <Modal show={show} onHide={handleClose} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          <FontAwesomeIcon icon={faHistory} className="me-2" />
          Checkout Transaction Details
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && (
          <div className="text-center py-4">
            <Spinner animation="border" role="status" />
            <div className="mt-2">Loading checkout details...</div>
          </div>
        )}

        {error && (
          <Alert variant="danger">
            <FontAwesomeIcon icon={faExclamationTriangle} className="me-2" />
            {error}
          </Alert>
        )}

        {checkoutDetails && (
          <div>
            {/* Status and Overview */}
            <Card className="mb-3">
              <Card.Header>
                <h5 className="mb-0">Transaction Overview</h5>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={6}>
                    <p><strong>Status:</strong> {getStatusBadge(checkoutDetails.status)}</p>
                    <p><strong>Transaction ID:</strong> #{checkoutDetails.id}</p>
                    {checkoutDetails.duration_days !== null && (
                      <p><strong>Duration:</strong> {formatDuration(checkoutDetails.duration_days)}</p>
                    )}
                  </Col>
                  <Col md={6}>
                    {checkoutDetails.is_overdue && (
                      <Alert variant="warning" className="py-2">
                        <FontAwesomeIcon icon={faExclamationTriangle} className="me-2" />
                        This checkout is overdue!
                      </Alert>
                    )}
                  </Col>
                </Row>
              </Card.Body>
            </Card>

            {/* Tool Information */}
            {checkoutDetails.tool && (
              <Card className="mb-3">
                <Card.Header>
                  <h5 className="mb-0">Tool Information</h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <p><strong>Tool Number:</strong> {checkoutDetails.tool.tool_number}</p>
                      <p><strong>Serial Number:</strong> {checkoutDetails.tool.serial_number}</p>
                      <p><strong>Description:</strong> {checkoutDetails.tool.description || 'N/A'}</p>
                    </Col>
                    <Col md={6}>
                      <p><strong>Category:</strong> {checkoutDetails.tool.category || 'General'}</p>
                      <p><strong>Location:</strong> {checkoutDetails.tool.location || 'N/A'}</p>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            )}

            {/* User Information */}
            {checkoutDetails.user && (
              <Card className="mb-3">
                <Card.Header>
                  <h5 className="mb-0">
                    <FontAwesomeIcon icon={faUser} className="me-2" />
                    User Information
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <p><strong>Name:</strong> {checkoutDetails.user.name}</p>
                      <p><strong>Employee Number:</strong> {checkoutDetails.user.employee_number}</p>
                    </Col>
                    <Col md={6}>
                      <p><strong>Department:</strong> {checkoutDetails.user.department}</p>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            )}

            {/* Timeline */}
            <Card className="mb-3">
              <Card.Header>
                <h5 className="mb-0">
                  <FontAwesomeIcon icon={faClock} className="me-2" />
                  Timeline
                </h5>
              </Card.Header>
              <Card.Body>
                <Table striped bordered hover size="sm">
                  <tbody>
                    <tr>
                      <td><strong>Checkout Date:</strong></td>
                      <td>{formatDate(checkoutDetails.checkout_date)}</td>
                    </tr>
                    <tr>
                      <td><strong>Expected Return Date:</strong></td>
                      <td>{formatDate(checkoutDetails.expected_return_date)}</td>
                    </tr>
                    <tr>
                      <td><strong>Actual Return Date:</strong></td>
                      <td>
                        {checkoutDetails.return_date ? (
                          formatDate(checkoutDetails.return_date)
                        ) : (
                          <Badge bg="warning">Still checked out</Badge>
                        )}
                      </td>
                    </tr>
                  </tbody>
                </Table>
              </Card.Body>
            </Card>

            {/* Return Information */}
            {checkoutDetails.return_date && (
              <Card className="mb-3">
                <Card.Header>
                  <h5 className="mb-0">Return Information</h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <p><strong>Condition at Return:</strong> {getConditionBadge(checkoutDetails.condition_at_return)}</p>
                      <p><strong>Returned By:</strong> {checkoutDetails.returned_by || 'Not specified'}</p>
                    </Col>
                    <Col md={6}>
                      <p><strong>Found/Lost Status:</strong>
                        {checkoutDetails.found === true && <Badge bg="success" className="ms-2">Found</Badge>}
                        {checkoutDetails.found === false && <Badge bg="danger" className="ms-2">Lost</Badge>}
                        {checkoutDetails.found === null && <span className="text-muted ms-2">Not specified</span>}
                      </p>
                    </Col>
                  </Row>

                  {checkoutDetails.return_notes && (
                    <div className="mt-3">
                      <strong>Return Notes:</strong>
                      <div className="border rounded p-2 mt-1 bg-light">
                        {checkoutDetails.return_notes}
                      </div>
                    </div>
                  )}
                </Card.Body>
              </Card>
            )}
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default CheckoutHistoryDetailModal;
