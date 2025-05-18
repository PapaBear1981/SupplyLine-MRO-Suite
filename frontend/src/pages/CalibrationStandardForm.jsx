import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import {
  addCalibrationStandard,
  fetchCalibrationStandard,
  updateCalibrationStandard
} from '../store/calibrationSlice';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const CalibrationStandardForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { user } = useSelector((state) => state.auth);
  const { currentCalibrationStandard, standardsLoading } = useSelector((state) => state.calibration);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [standardNumber, setStandardNumber] = useState('');
  const [certificationDate, setCertificationDate] = useState(new Date());
  const [expirationDate, setExpirationDate] = useState(new Date(new Date().setFullYear(new Date().getFullYear() + 1)));
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  // Check if user has permission to manage calibration standards
  const hasPermission = user?.is_admin || user?.department === 'Materials';

  // Check if we're editing an existing standard
  const isEditing = !!id;

  useEffect(() => {
    if (isEditing) {
      dispatch(fetchCalibrationStandard(id));
    }
  }, [dispatch, id, isEditing]);

  useEffect(() => {
    if (isEditing && currentCalibrationStandard) {
      setName(currentCalibrationStandard.name || '');
      setDescription(currentCalibrationStandard.description || '');
      setStandardNumber(currentCalibrationStandard.standard_number || '');

      if (currentCalibrationStandard.certification_date) {
        setCertificationDate(new Date(currentCalibrationStandard.certification_date));
      }

      if (currentCalibrationStandard.expiration_date) {
        setExpirationDate(new Date(currentCalibrationStandard.expiration_date));
      }
    }
  }, [currentCalibrationStandard, isEditing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Format dates for API - use ISO string without timezone information
      const formattedCertificationDate = certificationDate.toISOString().split('T')[0] + 'T00:00:00';
      const formattedExpirationDate = expirationDate.toISOString().split('T')[0] + 'T00:00:00';

      // Create standard data
      const standardData = {
        name,
        description,
        standard_number: standardNumber,
        certification_date: formattedCertificationDate,
        expiration_date: formattedExpirationDate
      };

      let resultAction;

      if (isEditing) {
        // Update existing standard
        resultAction = await dispatch(updateCalibrationStandard({
          id,
          standardData
        }));
      } else {
        // Add new standard
        resultAction = await dispatch(addCalibrationStandard(standardData));
      }

      if (
        (isEditing && updateCalibrationStandard.fulfilled.match(resultAction)) ||
        (!isEditing && addCalibrationStandard.fulfilled.match(resultAction))
      ) {
        setSuccess(true);

        // Navigate back to calibration standards page after a delay
        setTimeout(() => {
          navigate('/calibrations');
        }, 2000);
      } else {
        setError(resultAction.error.message || `Failed to ${isEditing ? 'update' : 'add'} calibration standard`);
      }
    } catch (err) {
      setError(err.message || `An error occurred while ${isEditing ? 'updating' : 'adding'} calibration standard`);
    } finally {
      setLoading(false);
    }
  };

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Access Denied</Alert.Heading>
        <p>
          You do not have permission to manage calibration standards.
          This feature is only available to administrators and Materials department personnel.
        </p>
      </Alert>
    );
  }

  if (isEditing && standardsLoading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading...</p>
      </div>
    );
  }

  if (isEditing && !currentCalibrationStandard && !standardsLoading) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Standard Not Found</Alert.Heading>
        <p>The requested calibration standard could not be found.</p>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <h1 className="mb-4">{isEditing ? 'Edit' : 'Add'} Calibration Standard</h1>

      {error && (
        <Alert variant="danger">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {success && (
        <Alert variant="success">
          <Alert.Heading>Success</Alert.Heading>
          <p>
            Calibration standard {isEditing ? 'updated' : 'added'} successfully.
            Redirecting to calibration standards page...
          </p>
        </Alert>
      )}

      <Card>
        <Card.Header>
          <h4>Standard Information</h4>
        </Card.Header>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter standard name"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Standard Number</Form.Label>
              <Form.Control
                type="text"
                value={standardNumber}
                onChange={(e) => setStandardNumber(e.target.value)}
                placeholder="Enter standard number or identifier"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter standard description"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Certification Date</Form.Label>
              <DatePicker
                selected={certificationDate}
                onChange={(date) => setCertificationDate(date)}
                className="form-control"
                dateFormat="MM/dd/yyyy"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Expiration Date</Form.Label>
              <DatePicker
                selected={expirationDate}
                onChange={(date) => setExpirationDate(date)}
                className="form-control"
                dateFormat="MM/dd/yyyy"
                minDate={new Date()}
                required
              />
            </Form.Group>

            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button
                variant="secondary"
                onClick={() => navigate('/calibrations')}
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
                  `${isEditing ? 'Update' : 'Save'} Standard`
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CalibrationStandardForm;
