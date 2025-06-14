import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Card, Row, Col, Button, Badge, Spinner, Alert, Table } from 'react-bootstrap';
import { fetchToolById } from '../store/toolsSlice';
import { fetchCalibrationStandard } from '../store/calibrationSlice';
import api from '../services/api';

const CalibrationDetailPage = () => {
  const { id, calibrationId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { user } = useSelector((state) => state.auth);
  const { currentTool: selectedTool, loading: toolLoading } = useSelector((state) => state.tools);

  const [calibration, setCalibration] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user has permission to view calibration details
  const hasPermission = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch tool data
        if (id) {
          // Convert id to number if it's a string
          const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
          dispatch(fetchToolById(toolId));
        }

        // Fetch calibration data
        if (calibrationId) {
          // Convert ids to numbers if they're strings
          const toolId = typeof id === 'string' ? parseInt(id, 10) : id;
          const calId = typeof calibrationId === 'string' ? parseInt(calibrationId, 10) : calibrationId;

          try {
            const response = await api.get(`/tools/${toolId}/calibrations/${calId}`);
            setCalibration(response.data);

            // Fetch calibration standards if any
            if (response.data.standards && response.data.standards.length > 0) {
              response.data.standards.forEach(standard => {
                dispatch(fetchCalibrationStandard(standard.id));
              });
            }
            setError(null);
          } catch (error) {
            console.error('Error fetching calibration details:', error);
            setError('Failed to load calibration details. Please try again later.');
          }
        }
      } catch (err) {
        console.error('Error fetching calibration details:', err);
        setError('Failed to load calibration details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [dispatch, id, calibrationId]);

  if (!hasPermission) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Access Denied</Alert.Heading>
        <p>
          You do not have permission to view calibration details.
          This feature is only available to administrators and Materials department personnel.
        </p>
      </Alert>
    );
  }

  if (loading || toolLoading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading calibration details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error</Alert.Heading>
        <p>{error}</p>
      </Alert>
    );
  }

  if (!calibration) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Calibration Not Found</Alert.Heading>
        <p>The requested calibration record could not be found.</p>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Calibration Details</h1>
        <div>
          <Button
            as={Link}
            to={`/tools/${id}`}
            variant="secondary"
          >
            Back to Tool
          </Button>
        </div>
      </div>

      <Row>
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>
              <h4>Tool Information</h4>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Tool Number:</Col>
                <Col sm={8}>{selectedTool?.tool_number}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Serial Number:</Col>
                <Col sm={8}>{selectedTool?.serial_number}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Description:</Col>
                <Col sm={8}>{selectedTool?.description || 'N/A'}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Location:</Col>
                <Col sm={8}>{selectedTool?.location}</Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>
              <h4>Calibration Information</h4>
            </Card.Header>
            <Card.Body>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Calibration Date:</Col>
                <Col sm={8}>{new Date(calibration.calibration_date).toLocaleDateString()}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Next Due Date:</Col>
                <Col sm={8}>
                  {calibration.next_calibration_date
                    ? new Date(calibration.next_calibration_date).toLocaleDateString()
                    : 'Not scheduled'}
                </Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Performed By:</Col>
                <Col sm={8}>{calibration.performed_by_name}</Col>
              </Row>
              <Row className="mb-3">
                <Col sm={4} className="fw-bold">Status:</Col>
                <Col sm={8}>
                  <Badge bg={
                    calibration.calibration_status === 'pass' ? 'success' :
                    calibration.calibration_status === 'fail' ? 'danger' : 'warning'
                  }>
                    {calibration.calibration_status === 'pass' ? 'Pass' :
                     calibration.calibration_status === 'fail' ? 'Fail' : 'Limited'}
                  </Badge>
                </Col>
              </Row>
              {calibration.calibration_notes && (
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Notes:</Col>
                  <Col sm={8}>{calibration.calibration_notes}</Col>
                </Row>
              )}
              {calibration.calibration_certificate_file && (
                <Row className="mb-3">
                  <Col sm={4} className="fw-bold">Certificate:</Col>
                  <Col sm={8}>
                    <a href={`/api/calibrations/${calibration.id}/certificate`} target="_blank" rel="noopener noreferrer">
                      View Certificate
                    </a>
                  </Col>
                </Row>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {calibration.standards && calibration.standards.length > 0 && (
        <Card>
          <Card.Header>
            <h4>Calibration Standards Used</h4>
          </Card.Header>
          <Card.Body>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Standard Number</th>
                  <th>Certification Date</th>
                  <th>Expiration Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {calibration.standards.map((standard) => (
                  <tr key={standard.id}>
                    <td>{standard.name}</td>
                    <td>{standard.standard_number}</td>
                    <td>{new Date(standard.certification_date).toLocaleDateString()}</td>
                    <td>{new Date(standard.expiration_date).toLocaleDateString()}</td>
                    <td>
                      <Badge bg={
                        standard.is_expired ? 'danger' :
                        standard.is_expiring_soon ? 'warning' : 'success'
                      }>
                        {standard.is_expired ? 'Expired' :
                         standard.is_expiring_soon ? 'Expiring Soon' : 'Valid'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default CalibrationDetailPage;
