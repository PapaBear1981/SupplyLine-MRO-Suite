import { useState, useEffect } from 'react';
import { Table, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Tooltip from '../common/Tooltip';
import HelpIcon from '../common/HelpIcon';
import HelpContent from '../common/HelpContent';
import { useHelp } from '../../context/HelpContext';

const CalibrationDueList = () => {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);
  const { showTooltips, showHelp } = useHelp();

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

  // Always render the timeframe selector
  const renderTimeframeSelector = () => (
    <div className="mb-3">
      <div className="d-flex align-items-center mb-3">
        <div className="d-flex align-items-center">
          <span className="me-2">Show tools due for calibration in the next:</span>
          {showHelp && (
            <HelpIcon
              title="Timeframe Selection"
              content="Select a timeframe to view tools that will need calibration within that period. This helps you plan and prioritize calibration tasks."
              size="sm"
            />
          )}
        </div>
        <div className="btn-group ms-2">
          <Tooltip text="Show tools due in the next 7 days" placement="top" show={showTooltips}>
            <Button
              variant={days === 7 ? 'primary' : 'outline-primary'}
              onClick={() => setDays(7)}
              size="sm"
            >
              7 Days
            </Button>
          </Tooltip>
          <Tooltip text="Show tools due in the next 30 days" placement="top" show={showTooltips}>
            <Button
              variant={days === 30 ? 'primary' : 'outline-primary'}
              onClick={() => setDays(30)}
              size="sm"
            >
              30 Days
            </Button>
          </Tooltip>
          <Tooltip text="Show tools due in the next 90 days" placement="top" show={showTooltips}>
            <Button
              variant={days === 90 ? 'primary' : 'outline-primary'}
              onClick={() => setDays(90)}
              size="sm"
            >
              90 Days
            </Button>
          </Tooltip>
        </div>
      </div>
    </div>
  );

  return (
    <div>
      {showHelp && (
        <HelpContent title="Tools Due for Calibration" initialOpen={false}>
          <p>This page shows all tools that are due for calibration within the selected timeframe.</p>
          <ul>
            <li><strong>Timeframe Selection:</strong> Use the buttons at the top to change the timeframe (7, 30, or 90 days).</li>
            <li><strong>Days Remaining:</strong> The number of days until calibration is due. Color-coded by urgency:
              <ul>
                <li>Red: 7 days or less</li>
                <li>Yellow: 8-14 days</li>
                <li>Blue: More than 14 days</li>
              </ul>
            </li>
            <li><strong>Actions:</strong>
              <ul>
                <li>"View Tool" - View detailed information about the tool</li>
                <li>"Calibrate" - Perform and record a new calibration for the tool</li>
              </ul>
            </li>
          </ul>
        </HelpContent>
      )}

      {renderTimeframeSelector()}

      {tools.length === 0 ? (
        <Alert variant="info">
          <Alert.Heading>No Calibrations Due</Alert.Heading>
          <p>There are no tools due for calibration in the next {days} days.</p>
        </Alert>
      ) : (

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
                    <Tooltip text={showTooltips ? "View tool details" : null} placement="top">
                      <Button
                        as={Link}
                        to={`/tools/${tool.id}`}
                        variant="info"
                        size="sm"
                      >
                        View Tool
                      </Button>
                    </Tooltip>
                    <Tooltip text={showTooltips ? "Perform calibration on this tool" : null} placement="top">
                      <Button
                        as={Link}
                        to={`/tools/${tool.id}/calibrations/new`}
                        variant="primary"
                        size="sm"
                      >
                        Calibrate
                      </Button>
                    </Tooltip>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>
      )}
    </div>
  );
};

export default CalibrationDueList;
