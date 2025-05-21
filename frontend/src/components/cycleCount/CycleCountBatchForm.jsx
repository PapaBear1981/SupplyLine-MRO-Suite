import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, Form, Button, Alert, Spinner, Row, Col } from 'react-bootstrap';
import { createCycleCountBatch, fetchCycleCountSchedules } from '../../store/cycleCountSlice';
import { useHelp } from '../../context/HelpContext';

const CycleCountBatchForm = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { showHelp } = useHelp();
  
  // Get schedule ID from query params if available
  const queryParams = new URLSearchParams(location.search);
  const scheduleIdFromQuery = queryParams.get('schedule');
  
  const { items: schedules, loading: schedulesLoading } = 
    useSelector((state) => state.cycleCount.schedules);
  
  const [formData, setFormData] = useState({
    name: '',
    schedule_id: scheduleIdFromQuery || '',
    start_date: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
    end_date: '',
    notes: '',
    generate_items: true,
    item_selection: 'all', // all, random, category, location
    item_count: 50, // Only used if item_selection is 'random'
    category: '', // Only used if item_selection is 'category'
    location: '' // Only used if item_selection is 'location'
  });
  
  const [validated, setValidated] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Fetch schedules for dropdown
    dispatch(fetchCycleCountSchedules({ active_only: true }));
  }, [dispatch]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
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
    setError(null);
    
    try {
      // Prepare data for submission
      const batchData = {
        ...formData,
        // Only include selection criteria based on the selected method
        ...(formData.item_selection === 'random' ? { item_count: parseInt(formData.item_count, 10) } : {}),
        ...(formData.item_selection === 'category' ? { category: formData.category } : {}),
        ...(formData.item_selection === 'location' ? { location: formData.location } : {})
      };
      
      await dispatch(createCycleCountBatch(batchData)).unwrap();
      setSuccess(true);
      setTimeout(() => {
        navigate('/cycle-counts/batches');
      }, 1500);
    } catch (err) {
      setError(err.error || 'An error occurred while creating the count batch');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-100">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Create Cycle Count Batch</h1>
      </div>

      {showHelp && (
        <Alert variant="info" className="mb-4">
          <Alert.Heading>About Cycle Count Batches</Alert.Heading>
          <p>
            A cycle count batch is a specific instance of counting inventory items.
            You can create a batch from a schedule or as a standalone count.
          </p>
          <hr />
          <p className="mb-0">
            <strong>Generate Items</strong> automatically adds items to the batch based on your selection criteria.
            You can also manually add items to the batch after creation.
          </p>
        </Alert>
      )}

      {error && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {success && (
        <Alert variant="success" className="mb-4">
          <Alert.Heading>Success!</Alert.Heading>
          <p>Count batch created successfully. Redirecting...</p>
        </Alert>
      )}

      <Card className="shadow-sm">
        <Card.Body>
          <Form noValidate validated={validated} onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Batch Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    placeholder="Enter batch name"
                  />
                  <Form.Control.Feedback type="invalid">
                    Please provide a batch name.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Schedule (Optional)</Form.Label>
                  <Form.Select
                    name="schedule_id"
                    value={formData.schedule_id}
                    onChange={handleChange}
                  >
                    <option value="">-- No Schedule --</option>
                    {schedules.map((schedule) => (
                      <option key={schedule.id} value={schedule.id}>
                        {schedule.name}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Text className="text-muted">
                    Link this batch to a schedule or leave blank for a one-time count
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Start Date</Form.Label>
                  <Form.Control
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleChange}
                    required
                  />
                  <Form.Control.Feedback type="invalid">
                    Please select a start date.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>End Date (Optional)</Form.Label>
                  <Form.Control
                    type="date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleChange}
                  />
                  <Form.Text className="text-muted">
                    Target completion date for this count batch
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Notes</Form.Label>
              <Form.Control
                as="textarea"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={3}
                placeholder="Enter any notes about this count batch (optional)"
              />
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Check
                type="checkbox"
                id="generate-items-checkbox"
                name="generate_items"
                label="Automatically generate items for this count batch"
                checked={formData.generate_items}
                onChange={handleChange}
              />
            </Form.Group>

            {formData.generate_items && (
              <Card className="mb-3 bg-light">
                <Card.Body>
                  <h5>Item Selection Criteria</h5>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Selection Method</Form.Label>
                    <Form.Select
                      name="item_selection"
                      value={formData.item_selection}
                      onChange={handleChange}
                      required
                    >
                      <option value="all">All Items</option>
                      <option value="random">Random Sample</option>
                      <option value="category">By Category</option>
                      <option value="location">By Location</option>
                    </Form.Select>
                  </Form.Group>

                  {formData.item_selection === 'random' && (
                    <Form.Group className="mb-3">
                      <Form.Label>Number of Items</Form.Label>
                      <Form.Control
                        type="number"
                        name="item_count"
                        value={formData.item_count}
                        onChange={handleChange}
                        min="1"
                        required
                      />
                      <Form.Control.Feedback type="invalid">
                        Please enter a valid number of items.
                      </Form.Control.Feedback>
                    </Form.Group>
                  )}

                  {formData.item_selection === 'category' && (
                    <Form.Group className="mb-3">
                      <Form.Label>Category</Form.Label>
                      <Form.Control
                        type="text"
                        name="category"
                        value={formData.category}
                        onChange={handleChange}
                        required={formData.item_selection === 'category'}
                        placeholder="Enter category name"
                      />
                      <Form.Control.Feedback type="invalid">
                        Please enter a category.
                      </Form.Control.Feedback>
                    </Form.Group>
                  )}

                  {formData.item_selection === 'location' && (
                    <Form.Group className="mb-3">
                      <Form.Label>Location</Form.Label>
                      <Form.Control
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleChange}
                        required={formData.item_selection === 'location'}
                        placeholder="Enter location name"
                      />
                      <Form.Control.Feedback type="invalid">
                        Please enter a location.
                      </Form.Control.Feedback>
                    </Form.Group>
                  )}
                </Card.Body>
              </Card>
            )}

            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button
                variant="outline-secondary"
                onClick={() => navigate('/cycle-counts/batches')}
                disabled={submitting}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={submitting}
              >
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
                    Creating...
                  </>
                ) : (
                  'Create Count Batch'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CycleCountBatchForm;
