import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { Card, Form, Button, Alert, Spinner, Row, Col } from 'react-bootstrap';
import {
  createCycleCountBatch,
  fetchCycleCountSchedules,
  fetchCycleCountBatch,
  updateCycleCountBatch,
  clearCurrentBatch
} from '../../store/cycleCountSlice';
import { useHelp } from '../../context/HelpContext';

const CycleCountBatchForm = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  const { showHelp } = useHelp();
  const isEditMode = !!id;

  // Get schedule ID from query params if available (for new batch creation)
  const queryParams = new URLSearchParams(location.search);
  const scheduleIdFromQuery = queryParams.get('schedule');

  const { items: schedules, loading: schedulesLoading } =
    useSelector((state) => state.cycleCount.schedules);

  const { data: currentBatch, loading: batchLoading, error: batchError } =
    useSelector((state) => state.cycleCount.currentBatch);

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

    // If editing, fetch the batch data
    if (isEditMode) {
      dispatch(fetchCycleCountBatch({ id }));
    } else {
      // Clear any existing batch data when creating new
      dispatch(clearCurrentBatch());
    }

    // Cleanup on unmount
    return () => {
      dispatch(clearCurrentBatch());
    };
  }, [dispatch, id, isEditMode]);

  // Populate form when batch data is loaded
  useEffect(() => {
    if (isEditMode && currentBatch) {
      setFormData({
        name: currentBatch.name || '',
        schedule_id: currentBatch.schedule_id ? String(currentBatch.schedule_id) : '',
        start_date: currentBatch.start_date ? new Date(currentBatch.start_date).toISOString().split('T')[0] : '',
        end_date: currentBatch.end_date ? new Date(currentBatch.end_date).toISOString().split('T')[0] : '',
        notes: currentBatch.notes || '',
        generate_items: false, // Can't generate items when editing
        item_selection: 'all',
        item_count: 50,
        category: '',
        location: ''
      });
    }
  }, [currentBatch, isEditMode]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    // If changing start_date and there's an end_date, validate the relationship
    if (name === 'start_date' && formData.end_date && value > formData.end_date) {
      setFormData({
        ...formData,
        [name]: value,
        end_date: '' // Reset end_date if it's now before start_date
      });
      return;
    }

    // If changing item selection method, reset related fields
    if (name === 'item_selection') {
      const updatedFormData = {
        ...formData,
        [name]: value,
        // Reset all selection-specific fields
        item_count: value === 'random' ? 50 : '',
        category: value === 'category' ? '' : '',
        location: value === 'location' ? '' : ''
      };
      setFormData(updatedFormData);
      return;
    }

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

      if (isEditMode) {
        // If editing, check if there are any changes
        const originalBatch = currentBatch;
        const hasChanges =
          originalBatch.name !== batchData.name ||
          String(originalBatch.schedule_id ?? '') !== String(batchData.schedule_id ?? '') ||
          (originalBatch.start_date ? new Date(originalBatch.start_date).toISOString().split('T')[0] : '') !== batchData.start_date ||
          (originalBatch.end_date ? new Date(originalBatch.end_date).toISOString().split('T')[0] : '') !== batchData.end_date ||
          (originalBatch.notes || '') !== (batchData.notes || '');

        if (!hasChanges) {
          // No changes, show success and redirect
          setSuccess(true);
          setTimeout(() => {
            navigate('/cycle-counts/batches');
          }, 1500);
          setSubmitting(false);
          return;
        }

        // Update existing batch
        await dispatch(updateCycleCountBatch({ id, batchData })).unwrap();
        setSuccess(true);
        setTimeout(() => {
          navigate('/cycle-counts/batches');
        }, 1500);
      } else {
        // Create new batch
        await dispatch(createCycleCountBatch(batchData)).unwrap();
        setSuccess(true);
        setTimeout(() => {
          navigate('/cycle-counts/batches');
        }, 1500);
      }
    } catch (err) {
      setError(err.error || `An error occurred while ${isEditMode ? 'updating' : 'creating'} the count batch`);
    } finally {
      setSubmitting(false);
    }
  };

  // Show loading spinner when fetching batch data in edit mode
  if (batchLoading && isEditMode) {
    return (
      <div className="d-flex justify-content-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  // Show error message if batch data fetch fails in edit mode
  if (batchError && isEditMode) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Batch</Alert.Heading>
        <p>{batchError.error || 'Failed to load batch data'}</p>
        <Button variant="outline-danger" onClick={() => navigate('/cycle-counts/batches')}>
          Return to Batches
        </Button>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{isEditMode ? 'Edit Cycle Count Batch' : 'Create Cycle Count Batch'}</h1>
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
          <p>
            {isEditMode
              ? 'Batch updated successfully. Redirecting...'
              : 'Batch created successfully. Redirecting...'}
          </p>
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
                    disabled={schedulesLoading}
                  >
                    <option value="">-- No Schedule --</option>
                    {schedulesLoading ? (
                      <option value="" disabled>Loading schedules...</option>
                    ) : (
                      schedules.map((schedule) => (
                        <option key={schedule.id} value={schedule.id}>
                          {schedule.name}
                        </option>
                      ))
                    )}
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
                    min={formData.start_date}
                  />
                  <Form.Control.Feedback type="invalid">
                    End date must be after start date.
                  </Form.Control.Feedback>
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

            {!isEditMode && (
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
            )}

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
                    {isEditMode ? 'Updating...' : 'Creating...'}
                  </>
                ) : (
                  isEditMode ? 'Update Batch' : 'Create Count Batch'
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
