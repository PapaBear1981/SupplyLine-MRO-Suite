import { useState, useEffect } from 'react';
import { Table, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const CalibrationDueList = () => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    const fetchDueCalibrations = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/calibrations/due?days=${days}`);
        setTools(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching calibrations due:', err);
        setError('Failed to load tools due for calibration. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDueCalibrations();
  }, [days]);

  if (loading) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" role="status" />
        <span className="ms-2">Loading calibration data...</span>
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

  if (tools.length === 0) {
    return (
      <Alert variant="info">
        <Alert.Heading>No Calibrations Due</Alert.Heading>
        <p>There are no tools due for calibration in the next {days} days.</p>
      </Alert>
    );
  }

  return (
    <div>
      <div className="mb-3">
        <div className="d-flex align-items-center mb-3">
          <span className="me-2">Showing tools due for calibration in the next:</span>
          <div className="btn-group">
            <Button
              variant={days === 7 ? 'primary' : 'outline-primary'}
              onClick={() => setDays(7)}
              size="sm"
            >
              7 Days
            </Button>
            <Button
              variant={days === 30 ? 'primary' : 'outline-primary'}
              onClick={() => setDays(30)}
              size="sm"
            >
              30 Days
            </Button>
            <Button
              variant={days === 90 ? 'primary' : 'outline-primary'}
              onClick={() => setDays(90)}
              size="sm"
            >
              90 Days
            </Button>
          </div>
        </div>
      </div>

      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>Tool Number</th>
            <th>Serial Number</th>
            <th>Description</th>
            <th>Last Calibration</th>
            <th>Next Calibration</th>
            <th>Days Remaining</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tools.map((tool) => {
            const nextDate = new Date(tool.next_calibration_date);
            const today = new Date();
            const daysRemaining = Math.ceil((nextDate - today) / (1000 * 60 * 60 * 24));
            
            return (
              <tr key={tool.id}>
                <td>{tool.tool_number}</td>
                <td>{tool.serial_number}</td>
                <td>{tool.description || 'N/A'}</td>
                <td>
                  {tool.last_calibration_date
                    ? new Date(tool.last_calibration_date).toLocaleDateString()
                    : 'Never'}
                </td>
                <td>{new Date(tool.next_calibration_date).toLocaleDateString()}</td>
                <td>
                  <Badge bg={daysRemaining <= 7 ? 'danger' : daysRemaining <= 14 ? 'warning' : 'info'}>
                    {daysRemaining} days
                  </Badge>
                </td>
                <td>
                  <div className="d-flex gap-2">
                    <Button
                      as={Link}
                      to={`/tools/${tool.id}`}
                      variant="info"
                      size="sm"
                    >
                      View Tool
                    </Button>
                    <Button
                      as={Link}
                      to={`/tools/${tool.id}/calibrations/new`}
                      variant="primary"
                      size="sm"
                    >
                      Calibrate
                    </Button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    </div>
  );
};

export default CalibrationDueList;
