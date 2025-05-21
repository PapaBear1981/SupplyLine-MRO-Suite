import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, Form, Button, Alert, Spinner, Row, Col } from 'react-bootstrap';
import { createCycleCountSchedule, fetchCycleCountSchedule, updateCycleCountSchedule, clearCurrentSchedule } from '../../store/cycleCountSlice';
import { useHelp } from '../../context/HelpContext';

const CycleCountScheduleForm = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { id } = useParams();
  const { showHelp } = useHelp();
  const isEditMode = !!id;
  
  const { data: currentSchedule, loading: scheduleLoading, error: scheduleError } = 
    useSelector((state) => state.cycleCount.currentSchedule);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    frequency: 'weekly',
    method: 'random',
    is_active: true
  });
  
  const [validated, setValidated] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // If editing, fetch the schedule data
    if (isEditMode) {
      dispatch(fetchCycleCountSchedule({ id }));
    } else {
      // Clear any existing schedule data when creating new
      dispatch(clearCurrentSchedule());
    }
    
    // Cleanup on unmount
    return () => {
      dispatch(clearCurrentSchedule());
    };
  }, [dispatch, id, isEditMode]);

  // Populate form when schedule data is loaded
  useEffect(() => {
    if (isEditMode && currentSchedule) {
      setFormData({
        name: currentSchedule.name || '',
        description: currentSchedule.description || '',
        frequency: currentSchedule.frequency || 'weekly',
        method: currentSchedule.method || 'random',
        is_active: currentSchedule.is_active !== undefined ? currentSchedule.is_active : true
      });
    }
  }, [currentSchedule, isEditMode]);

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
      if (isEditMode) {
        await dispatch(updateCycleCountSchedule({ id, scheduleData: formData })).unwrap();
      } else {
        await dispatch(createCycleCountSchedule(formData)).unwrap();
      }
      setSuccess(true);
      setTimeout(() => {
        navigate('/cycle-counts/schedules');
      }, 1500);
    } catch (err) {
      setError(err.error || 'An error occurred while saving the schedule');
    } finally {
      setSubmitting(false);
    }
  };

  if (scheduleLoading && isEditMode) {
    return (
      <div className="d-flex justify-content-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (scheduleError && isEditMode) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Schedule</Alert.Heading>
        <p>{scheduleError.error || 'Failed to load schedule data'}</p>
        <Button variant="outline-danger" onClick={() => navigate('/cycle-counts/schedules')}>
          Return to Schedules
        </Button>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{isEditMode ? 'Edit Cycle Count Schedule' : 'Create Cycle Count Schedule'}</h1>
      </div>

      {showHelp && (
        <Alert variant="info" className="mb-4">
          <Alert.Heading>About Cycle Count Schedules</Alert.Heading>
          <p>
            Cycle count schedules define how frequently and which method to use when counting inventory.
            They help maintain accurate inventory records by systematically counting portions of inventory
            on a regular basis.
          </p>
          <hr />
          <p className="mb-0">
            <strong>Frequency</strong> determines how often counts occur.
            <strong>Method</strong> determines which items are selected for counting.
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
              ? 'Schedule updated successfully. Redirecting...'
              : 'Schedule created successfully. Redirecting...'}
          </p>
        </Alert>
      )}

      <Card className="shadow-sm">
        <Card.Body>
          <Form noValidate validated={validated} onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Schedule Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    placeholder="Enter schedule name"
                  />
                  <Form.Control.Feedback type="invalid">
                    Please provide a schedule name.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Status</Form.Label>
                  <Form.Check
                    type="switch"
                    id="is-active-switch"
                    name="is_active"
                    label={formData.is_active ? 'Active' : 'Inactive'}
                    checked={formData.is_active}
                    onChange={handleChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                placeholder="Enter schedule description (optional)"
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Frequency</Form.Label>
                  <Form.Select
                    name="frequency"
                    value={formData.frequency}
                    onChange={handleChange}
                    required
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="annual">Annual</option>
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    Please select a frequency.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Count Method</Form.Label>
                  <Form.Select
                    name="method"
                    value={formData.method}
                    onChange={handleChange}
                    required
                  >
                    <option value="ABC">ABC Analysis</option>
                    <option value="random">Random Sampling</option>
                    <option value="location">By Location</option>
                    <option value="category">By Category</option>
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    Please select a count method.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button
                variant="outline-secondary"
                onClick={() => navigate('/cycle-counts/schedules')}
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
                    Saving...
                  </>
                ) : (
                  isEditMode ? 'Update Schedule' : 'Create Schedule'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CycleCountScheduleForm;
