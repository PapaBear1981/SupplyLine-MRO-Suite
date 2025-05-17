import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Form, Button, Card, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { fetchToolById } from '../store/toolsSlice';
import { addCalibration, fetchCalibrationStandards } from '../store/calibrationSlice';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const ToolCalibrationForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { user } = useSelector((state) => state.auth);
  const { currentTool: selectedTool, loading: toolLoading } = useSelector((state) => state.tools);
  const { calibrationStandards, standardsLoading } = useSelector((state) => state.calibration);

  const [calibrationDate, setCalibrationDate] = useState(new Date());
  const [nextCalibrationDate, setNextCalibrationDate] = useState(null);
  const [calibrationNotes, setCalibrationNotes] = useState('');
  const [calibrationStatus, setCalibrationStatus] = useState('completed');
  const [selectedStandards, setSelectedStandards] = useState([]);
  const [certificateFile, setCertificateFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  // Check if user has permission to calibrate tools
  const hasPermission = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    if (id) {
      // Convert id to number if it's a string
      const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
      dispatch(fetchToolById(toolId));
      dispatch(fetchCalibrationStandards({ page: 1, limit: 100 }));
    }
  }, [dispatch, id]);

  useEffect(() => {
    // Calculate next calibration date based on tool's calibration frequency
    if (selectedTool?.calibration_frequency_days && calibrationDate) {
      const nextDate = new Date(calibrationDate);
      nextDate.setDate(nextDate.getDate() + selectedTool.calibration_frequency_days);
      setNextCalibrationDate(nextDate);
    }
  }, [selectedTool, calibrationDate]);

  const handleStandardChange = (e) => {
    const standardId = parseInt(e.target.value);
    const isChecked = e.target.checked;

    if (isChecked) {
      setSelectedStandards([...selectedStandards, standardId]);
    } else {
      setSelectedStandards(selectedStandards.filter(id => id !== standardId));
    }
  };

  const handleFileChange = (e) => {
    setCertificateFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Format dates for API - strip the timezone part to avoid offset issues
      const formattedCalibrationDate = calibrationDate.toISOString().split('T')[0];
      const formattedNextCalibrationDate = nextCalibrationDate ? nextCalibrationDate.toISOString().split('T')[0] : null;

      // Create calibration data
      const calibrationData = {
        calibration_date: formattedCalibrationDate,
        next_calibration_date: formattedNextCalibrationDate,
        calibration_notes: calibrationNotes,
        calibration_status: calibrationStatus,
        standard_ids: selectedStandards
      };

      // If there's a certificate file, handle file upload
      if (certificateFile) {
        // In a real implementation, you would upload the file to the server
        // and get back a file path to include in calibrationData
        // For now, we'll just include the file name
        calibrationData.calibration_certificate_file = certificateFile.name;
      }

      // Dispatch action to add calibration
      const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
      const resultAction = await dispatch(addCalibration({ toolId, calibrationData }));

      if (addCalibration.fulfilled.match(resultAction)) {
        setSuccess(true);
        // Reset form
        setCalibrationNotes('');
        setCalibrationStatus('completed');
        setSelectedStandards([]);
        setCertificateFile(null);

        // Navigate back to tool detail page after a delay
        setTimeout(() => {
          navigate(`/tools/${id}`);
        }, 2000);
      } else {
        setError(resultAction.error.message || 'Failed to add calibration record');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while adding calibration record');
    } finally {
      setLoading(false);
    }
  };

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Access Denied</Alert.Heading>
        <p>
          You do not have permission to calibrate tools.
          This feature is only available to administrators and Materials department personnel.
        </p>
      </Alert>
    );
  }

  if (toolLoading || standardsLoading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading...</p>
      </div>
    );
  }

  if (!selectedTool) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Tool Not Found</Alert.Heading>
        <p>The requested tool could not be found.</p>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <h1 className="mb-4">Calibrate Tool</h1>

      <Card className="mb-4">
        <Card.Header>
          <h4>Tool Information</h4>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <p><strong>Tool Number:</strong> {selectedTool.tool_number}</p>
              <p><strong>Serial Number:</strong> {selectedTool.serial_number}</p>
              <p><strong>Description:</strong> {selectedTool.description}</p>
            </Col>
            <Col md={6}>
              <p><strong>Location:</strong> {selectedTool.location}</p>
              <p><strong>Category:</strong> {selectedTool.category}</p>
              <p>
                <strong>Last Calibration:</strong> {selectedTool.last_calibration_date
                  ? new Date(selectedTool.last_calibration_date).toLocaleDateString()
                  : 'Never'}
              </p>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {error && (
        <Alert variant="danger">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {success && (
        <Alert variant="success">
          <Alert.Heading>Success</Alert.Heading>
          <p>Calibration record added successfully. Redirecting to tool detail page...</p>
        </Alert>
      )}

      <Card>
        <Card.Header>
          <h4>Calibration Information</h4>
        </Card.Header>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Calibration Date</Form.Label>
                  <DatePicker
                    selected={calibrationDate}
                    onChange={(date) => setCalibrationDate(date)}
                    className="form-control"
                    dateFormat="MM/dd/yyyy"
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Next Calibration Date</Form.Label>
                  <DatePicker
                    selected={nextCalibrationDate}
                    onChange={(date) => setNextCalibrationDate(date)}
                    className="form-control"
                    dateFormat="MM/dd/yyyy"
                    minDate={new Date()}
                  />
                  {selectedTool.calibration_frequency_days && (
                    <Form.Text className="text-muted">
                      Based on the tool's calibration frequency of {selectedTool.calibration_frequency_days} days
                    </Form.Text>
                  )}
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Calibration Status</Form.Label>
              <Form.Select
                value={calibrationStatus}
                onChange={(e) => setCalibrationStatus(e.target.value)}
                required
              >
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="in_progress">In Progress</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Calibration Notes</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={calibrationNotes}
                onChange={(e) => setCalibrationNotes(e.target.value)}
                placeholder="Enter calibration notes, observations, or special instructions"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Calibration Certificate</Form.Label>
              <Form.Control
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.jpg,.jpeg,.png"
              />
              <Form.Text className="text-muted">
                Upload calibration certificate (PDF, JPG, JPEG, PNG)
              </Form.Text>
            </Form.Group>

            {calibrationStandards?.length > 0 && (
              <Form.Group className="mb-3">
                <Form.Label>Calibration Standards Used</Form.Label>
                <div className="border p-3 rounded">
                  {calibrationStandards.map((standard) => (
                    <Form.Check
                      key={standard.id}
                      type="checkbox"
                      id={`standard-${standard.id}`}
                      label={`${standard.name} (${standard.standard_number})`}
                      value={standard.id}
                      onChange={handleStandardChange}
                      checked={selectedStandards.includes(standard.id)}
                      className="mb-2"
                    />
                  ))}
                </div>
              </Form.Group>
            )}

            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button
                variant="secondary"
                onClick={() => navigate(`/tools/${id}`)}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={loading}
              >
                {loading ? (
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
                  'Save Calibration'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default ToolCalibrationForm;
