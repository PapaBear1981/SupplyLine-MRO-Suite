import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import { createTool, clearError, clearSuccessMessage } from '../../store/toolsSlice';
import LotNumberInput from '../common/LotNumberInput';
import api from '../../services/api';

const NewToolForm = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error, successMessage } = useSelector((state) => state.tools);

  // Local state for form submission status
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState(null);

  // Warehouse state
  const [warehouses, setWarehouses] = useState([]);
  const [loadingWarehouses, setLoadingWarehouses] = useState(false);

  const [toolData, setToolData] = useState({
    tool_number: '',
    serial_number: '',
    lot_number: '',
    description: '',
    condition: 'New',
    location: '',
    category: 'General',
    warehouse_id: '',  // Required field
    requires_calibration: false,
    calibration_frequency_days: ''
  });
  const [validated, setValidated] = useState(false);

  // Fetch warehouses on mount
  useEffect(() => {
    const fetchWarehouses = async () => {
      setLoadingWarehouses(true);
      try {
        const response = await api.get('/warehouses');
        // Backend returns array directly, not wrapped in {warehouses: [...]}
        setWarehouses(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        console.error('Failed to fetch warehouses:', err);
        setLocalError('Failed to load warehouses. Please refresh the page.');
      } finally {
        setLoadingWarehouses(false);
      }
    };

    fetchWarehouses();
  }, []);

  // Clear error and success messages when component unmounts
  useEffect(() => {
    return () => {
      dispatch(clearError());
      dispatch(clearSuccessMessage());
    };
  }, [dispatch]);

  // Effect to handle successful tool creation
  useEffect(() => {
    if (successMessage && isSubmitting) {
      // Wait a moment to show the success message before navigating
      const timer = setTimeout(() => {
        navigate('/tools');
      }, 1500);

      return () => clearTimeout(timer);
    }
  }, [successMessage, isSubmitting, navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setToolData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    setLocalError(null);
    dispatch(clearError()); // Clear any previous Redux errors

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);
    setIsSubmitting(true);

    // Log the data being sent
    console.log('Submitting tool data:', toolData);

    // Create a copy of the data to ensure we're sending the right fields
    const toolDataToSend = {
      ...toolData,
      // Convert calibration_frequency_days to a number if it's provided
      calibration_frequency_days: toolData.requires_calibration && toolData.calibration_frequency_days
        ? parseInt(toolData.calibration_frequency_days, 10)
        : null
    };

    dispatch(createTool(toolDataToSend))
      .unwrap()
      .then((result) => {
        console.log('Tool created successfully:', result);
        // Success is handled by the useEffect that watches for successMessage
      })
      .catch((err) => {
        console.error('Failed to create tool:', err);
        // Extract error message from various possible formats
        const errorMessage = err.error || err.message || 'Failed to create tool. Please try again.';
        setLocalError(errorMessage);
        dispatch(clearError()); // Clear Redux error to avoid duplicate display
        setIsSubmitting(false);
      });
  };

  return (
    <Card className="shadow-sm">
      <Card.Header>
        <h4>Add New Tool</h4>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error.error || error.message || 'An error occurred'}</Alert>}
        {localError && <Alert variant="danger">{localError}</Alert>}
        {successMessage && <Alert variant="success">{successMessage}</Alert>}

        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Tool Number*</Form.Label>
            <Form.Control
              type="text"
              name="tool_number"
              value={toolData.tool_number}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Tool number is required
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              You can create multiple tools with the same tool number as long as they have different serial numbers.
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Serial Number*</Form.Label>
            <Form.Control
              type="text"
              name="serial_number"
              value={toolData.serial_number}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Serial number is required
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              Serial number must be unique for tools with the same tool number.
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Warehouse*</Form.Label>
            <Form.Select
              name="warehouse_id"
              value={toolData.warehouse_id}
              onChange={handleChange}
              required
              disabled={loadingWarehouses}
            >
              <option value="">
                {loadingWarehouses ? 'Loading warehouses...' : 'Select a warehouse...'}
              </option>
              {warehouses.map(warehouse => (
                <option key={warehouse.id} value={warehouse.id}>
                  {warehouse.name} - {warehouse.city}, {warehouse.state}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Warehouse is required
            </Form.Control.Feedback>
            <Form.Text className="text-muted">
              All tools must be created in a warehouse before they can be transferred to kits.
            </Form.Text>
          </Form.Group>

          <LotNumberInput
            value={toolData.lot_number}
            onChange={(value) => setToolData(prev => ({ ...prev, lot_number: value }))}
            disabled={loading || isSubmitting}
            required={false}
            label="Lot Number (Optional)"
            helpText="For consumable tools, you can track by lot number instead of serial number. Leave blank for standard tools."
            showAutoGenerate={true}
          />

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              value={toolData.description}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Condition</Form.Label>
            <Form.Select
              name="condition"
              value={toolData.condition}
              onChange={handleChange}
            >
              <option value="New">New</option>
              <option value="Good">Good</option>
              <option value="Fair">Fair</option>
              <option value="Poor">Poor</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Location</Form.Label>
            <Form.Control
              type="text"
              name="location"
              value={toolData.location}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Category</Form.Label>
            <Form.Select
              name="category"
              value={toolData.category}
              onChange={handleChange}
            >
              <option value="General">General</option>
              <option value="Q400">Q400</option>
              <option value="CL415">CL415</option>
              <option value="RJ85">RJ85</option>
              <option value="Engine">Engine</option>
              <option value="Floor">Floor</option>
              <option value="CNC">CNC</option>
              <option value="Sheetmetal">Sheetmetal</option>
            </Form.Select>
          </Form.Group>

          <hr className="my-4" />
          <h5 className="mb-3">Calibration Information</h5>

          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              id="requires-calibration"
              label="This tool requires calibration"
              name="requires_calibration"
              checked={toolData.requires_calibration}
              onChange={handleChange}
            />
          </Form.Group>

          {toolData.requires_calibration && (
            <Form.Group className="mb-3">
              <Form.Label>Calibration Frequency (Days)</Form.Label>
              <Form.Control
                type="number"
                name="calibration_frequency_days"
                value={toolData.calibration_frequency_days}
                onChange={handleChange}
                min="1"
                max="3650"
                placeholder="Enter number of days between calibrations"
              />
              <Form.Text className="text-muted">
                Enter the number of days between required calibrations (e.g., 90, 180, 365).
              </Form.Text>
            </Form.Group>
          )}

          <div className="d-flex justify-content-end gap-2">
            <Button
              variant="secondary"
              onClick={() => navigate('/tools')}
              disabled={loading || isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={loading || isSubmitting}
            >
              {loading || isSubmitting ? (
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
                'Save Tool'
              )}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default NewToolForm;
