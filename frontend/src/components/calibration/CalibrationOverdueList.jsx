import { useState, useEffect } from 'react';
import { Table, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const CalibrationOverdueList = () => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOverdueCalibrations = async () => {
      try {
        setLoading(true);
        const response = await api.get('/calibrations/overdue');
        setTools(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching overdue calibrations:', err);
        setError('Failed to load tools with overdue calibrations. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchOverdueCalibrations();
  }, []);

  if (loading) {
    return (
      <div className="text-center my-4">
        <Spinner animation="border" role="status" />
        <span className="ms-2">Loading overdue calibration data...</span>
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
      <Alert variant="success">
        <Alert.Heading>No Overdue Calibrations</Alert.Heading>
        <p>There are no tools with overdue calibrations.</p>
      </Alert>
    );
  }

  return (
    <div>
      <Alert variant="danger">
        <Alert.Heading>Attention Required</Alert.Heading>
        <p>
          The following tools have overdue calibrations and should not be used until they have been
          recalibrated.
        </p>
      </Alert>

      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>Tool Number</th>
            <th>Serial Number</th>
            <th>Description</th>
            <th>Last Calibration</th>
            <th>Due Date</th>
            <th>Days Overdue</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tools.map((tool) => {
            const dueDate = new Date(tool.next_calibration_date);
            const today = new Date();
            const daysOverdue = Math.ceil((today - dueDate) / (1000 * 60 * 60 * 24));
            
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
                  <Badge bg="danger">
                    {daysOverdue} days
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
                      variant="danger"
                      size="sm"
                    >
                      Calibrate Now
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

export default CalibrationOverdueList;
