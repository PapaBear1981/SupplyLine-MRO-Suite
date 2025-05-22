import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Card, 
  Row, 
  Col, 
  Button, 
  Alert, 
  Spinner, 
  Badge, 
  Form
} from 'react-bootstrap';
import axios from 'axios';
import { approveCountAdjustment } from '../store/cycleCountSlice';
import { useHelp } from '../context/HelpContext';

const CycleCountDiscrepancyDetailPage = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { showHelp } = useHelp();
  
  const [discrepancy, setDiscrepancy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    adjustment_type: 'quantity',
    new_value: '',
    notes: ''
  });
  
  const [validated, setValidated] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  useEffect(() => {
    const fetchDiscrepancy = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/cycle-counts/results/${id}`);
        setDiscrepancy(response.data);
        
        // Pre-fill form with appropriate values
        if (response.data.discrepancy_type === 'quantity') {
          setFormData(prev => ({
            ...prev,
            adjustment_type: 'quantity',
            new_value: response.data.actual_quantity.toString()
          }));
        } else if (response.data.discrepancy_type === 'location') {
          setFormData(prev => ({
            ...prev,
            adjustment_type: 'location',
            new_value: response.data.actual_location
          }));
        }
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to fetch discrepancy details');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDiscrepancy();
  }, [id]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const form = e.currentTarget;
    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }
    
    setValidated(true);
    setSubmitting(true);
    setSubmitError(null);
    
    try {
      // Prepare adjustment data
      const adjustmentData = {
        ...formData,
        // Convert to number if it's a quantity adjustment
        new_value: formData.adjustment_type === 'quantity' 
          ? parseInt(formData.new_value, 10) 
          : formData.new_value
      };
      
      await dispatch(approveCountAdjustment({ 
        resultId: id, 
        adjustmentData 
      })).unwrap();
      
      setSuccess(true);
      setTimeout(() => {
        navigate('/cycle-counts/discrepancies');
      }, 1500);
    } catch (err) {
      setSubmitError(err.error || 'An error occurred while approving the adjustment');
    } finally {
      setSubmitting(false);
    }
  };
  
  const formatDiscrepancyType = (type) => {
    const types = {
      quantity: 'Quantity Mismatch',
      location: 'Location Mismatch',
      condition: 'Condition Issue',
      multiple: 'Multiple Issues'
    };
    return types[type] || type;
  };
  
  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }
  
  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Discrepancy</Alert.Heading>
        <p>{error}</p>
      </Alert>
    );
  }
  
  if (!discrepancy) {
    return (
      <Alert variant="warning">
        <Alert.Heading>Discrepancy Not Found</Alert.Heading>
        <p>The requested count discrepancy could not be found.</p>
        <Button as={Link} to="/cycle-counts/discrepancies" variant="primary">
          Back to Discrepancies
        </Button>
      </Alert>
    );
  }
  
  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <div>
          <h1 className="mb-0">Discrepancy Details</h1>
          <p className="text-muted mb-0">
            {formatDiscrepancyType(discrepancy.discrepancy_type)} - Result ID: {discrepancy.id}
          </p>
        </div>
        <div>
          <Button as={Link} to="/cycle-counts/discrepancies" variant="outline-secondary">
            <i className="bi bi-arrow-left me-2"></i>
            Back to Discrepancies
          </Button>
        </div>
      </div>
      
      {showHelp && (
        <Alert variant="info" className="mb-4">
          <Alert.Heading>Discrepancy Resolution</Alert.Heading>
          <p>
            This page allows you to review and resolve discrepancies found during cycle counts.
            You can approve adjustments to inventory records based on the count results.
          </p>
        </Alert>
      )}
      
      <Row className="mb-4">
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Item Details</h5>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Item Type:</Col>
                <Col md={8}>{discrepancy.item.item_type === 'tool' ? 'Tool' : 'Chemical'}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Name:</Col>
                <Col md={8}>{discrepancy.item.item_name}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Batch:</Col>
                <Col md={8}>
                  <Link to={`/cycle-counts/batches/${discrepancy.item.batch_id}`}>
                    {discrepancy.item.batch_name}
                  </Link>
                </Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Counted By:</Col>
                <Col md={8}>{discrepancy.counted_by_name}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Count Date:</Col>
                <Col md={8}>{new Date(discrepancy.created_at).toLocaleString()}</Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="bg-light">
              <h5 className="mb-0">Discrepancy Details</h5>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Type:</Col>
                <Col md={8}>
                  <Badge bg="warning">{formatDiscrepancyType(discrepancy.discrepancy_type)}</Badge>
                </Col>
              </Row>
              
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Expected Quantity:</Col>
                <Col md={8}>{discrepancy.item.expected_quantity}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Actual Quantity:</Col>
                <Col md={8} className={discrepancy.discrepancy_type === 'quantity' ? 'text-danger' : ''}>
                  {discrepancy.actual_quantity}
                  {discrepancy.discrepancy_type === 'quantity' && (
                    <i className="bi bi-exclamation-triangle-fill ms-2"></i>
                  )}
                </Col>
              </Row>
              
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Expected Location:</Col>
                <Col md={8}>{discrepancy.item.location}</Col>
              </Row>
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Actual Location:</Col>
                <Col md={8} className={discrepancy.discrepancy_type === 'location' ? 'text-danger' : ''}>
                  {discrepancy.actual_location}
                  {discrepancy.discrepancy_type === 'location' && (
                    <i className="bi bi-exclamation-triangle-fill ms-2"></i>
                  )}
                </Col>
              </Row>
              
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Condition:</Col>
                <Col md={8} className={discrepancy.discrepancy_type === 'condition' ? 'text-danger' : ''}>
                  {discrepancy.condition}
                  {discrepancy.discrepancy_type === 'condition' && (
                    <i className="bi bi-exclamation-triangle-fill ms-2"></i>
                  )}
                </Col>
              </Row>
              
              <Row className="mb-3">
                <Col md={4} className="fw-bold">Notes:</Col>
                <Col md={8}>{discrepancy.notes || 'No notes'}</Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light">
          <h5 className="mb-0">Approve Adjustment</h5>
        </Card.Header>
        <Card.Body>
          {success ? (
            <Alert variant="success">
              <Alert.Heading>Adjustment Approved</Alert.Heading>
              <p>The inventory adjustment has been approved and processed.</p>
            </Alert>
          ) : (
            <Form noValidate validated={validated} onSubmit={handleSubmit}>
              {submitError && (
                <Alert variant="danger">
                  <Alert.Heading>Error</Alert.Heading>
                  <p>{submitError}</p>
                </Alert>
              )}
              
              <Form.Group className="mb-3">
                <Form.Label>Adjustment Type <span className="text-danger">*</span></Form.Label>
                <Form.Select
                  name="adjustment_type"
                  value={formData.adjustment_type}
                  onChange={handleChange}
                  required
                >
                  <option value="quantity">Update Quantity</option>
                  <option value="location">Update Location</option>
                  <option value="condition">Update Condition</option>
                  <option value="status">Update Status</option>
                </Form.Select>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>New Value <span className="text-danger">*</span></Form.Label>
                {formData.adjustment_type === 'quantity' ? (
                  <Form.Control
                    type="number"
                    name="new_value"
                    value={formData.new_value}
                    onChange={handleChange}
                    required
                    min="0"
                  />
                ) : formData.adjustment_type === 'condition' ? (
                  <Form.Select
                    name="new_value"
                    value={formData.new_value}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select condition...</option>
                    <option value="good">Good</option>
                    <option value="damaged">Damaged</option>
                    <option value="expired">Expired</option>
                    <option value="missing">Missing</option>
                  </Form.Select>
                ) : formData.adjustment_type === 'status' ? (
                  <Form.Select
                    name="new_value"
                    value={formData.new_value}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select status...</option>
                    <option value="available">Available</option>
                    <option value="in_use">In Use</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="retired">Retired</option>
                  </Form.Select>
                ) : (
                  <Form.Control
                    type="text"
                    name="new_value"
                    value={formData.new_value}
                    onChange={handleChange}
                    required
                  />
                )}
                <Form.Control.Feedback type="invalid">
                  Please enter a valid value.
                </Form.Control.Feedback>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Notes</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  placeholder="Enter any notes about this adjustment"
                />
              </Form.Group>
              
              <div className="d-flex justify-content-end">
                <Button 
                  as={Link} 
                  to="/cycle-counts/discrepancies" 
                  variant="secondary" 
                  className="me-2"
                >
                  Cancel
                </Button>
                <Button type="submit" variant="success" disabled={submitting}>
                  {submitting ? (
                    <>
                      <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        className="me-2"
                      />
                      Processing...
                    </>
                  ) : (
                    'Approve Adjustment'
                  )}
                </Button>
              </div>
            </Form>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default CycleCountDiscrepancyDetailPage;
