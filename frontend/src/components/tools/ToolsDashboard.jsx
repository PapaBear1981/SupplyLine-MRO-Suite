import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { Card, Row, Col, Spinner } from 'react-bootstrap';
import api from '../../services/api';

const ToolsDashboard = () => {
  const { tools } = useSelector((state) => state.tools);
  const { checkouts } = useSelector((state) => state.checkouts);
  const [calibrationStats, setCalibrationStats] = useState({ due: 0, overdue: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCalibrationStats = async () => {
      try {
        // Fetch calibration statistics
        const [dueResponse, overdueResponse] = await Promise.all([
          api.get('/calibrations/due'),
          api.get('/calibrations/overdue')
        ]);

        setCalibrationStats({
          due: dueResponse.data?.length || 0,
          overdue: overdueResponse.data?.length || 0
        });
      } catch (err) {
        console.error('Error fetching calibration stats:', err);
        // Don't show error to user, just use 0 values
      } finally {
        setLoading(false);
      }
    };

    fetchCalibrationStats();
  }, []);

  // Calculate tool statistics
  const totalTools = tools.length;
  const availableTools = tools.filter(t => t.status === 'available').length;
  const checkedOutTools = tools.filter(t => t.status === 'checked_out').length;
  const maintenanceTools = tools.filter(t => t.status === 'maintenance').length;

  // Calculate overdue checkouts
  const activeCheckouts = checkouts.filter(c => !c.return_date);
  const overdueCheckouts = activeCheckouts.filter(c =>
    c.expected_return_date && new Date(c.expected_return_date) < new Date()
  ).length;

  const StatCard = ({ title, value, icon, bgColor, textColor = 'text-white' }) => (
    <Col xs={12} sm={6} md={4} lg={2}>
      <Card className={`${bgColor} ${textColor} shadow-sm h-100`}>
        <Card.Body className="d-flex flex-column justify-content-between">
          <div className="d-flex justify-content-between align-items-start mb-2">
            <div>
              <h6 className="mb-0 text-uppercase small">{title}</h6>
            </div>
            <i className={`bi bi-${icon} fs-3 opacity-50`}></i>
          </div>
          <div>
            <h2 className="mb-0 fw-bold">
              {loading && (title.includes('Calibration') || title.includes('Overdue')) ? (
                <Spinner animation="border" size="sm" />
              ) : (
                value
              )}
            </h2>
          </div>
        </Card.Body>
      </Card>
    </Col>
  );

  return (
    <div className="mb-4">
      <Row className="g-3">
        <StatCard
          title="Total Tools"
          value={totalTools}
          icon="tools"
          bgColor="bg-primary"
        />
        <StatCard
          title="Available"
          value={availableTools}
          icon="check-circle"
          bgColor="bg-success"
        />
        <StatCard
          title="Checked Out"
          value={checkedOutTools}
          icon="person-fill"
          bgColor="bg-info"
        />
        <StatCard
          title="Maintenance"
          value={maintenanceTools}
          icon="wrench"
          bgColor="bg-warning"
          textColor="text-dark"
        />
        <StatCard
          title="Overdue Checkouts"
          value={overdueCheckouts}
          icon="exclamation-triangle"
          bgColor="bg-danger"
        />
        <StatCard
          title="Overdue Calibrations"
          value={calibrationStats.overdue}
          icon="calendar-x"
          bgColor="bg-danger"
        />
      </Row>
    </div>
  );
};

export default ToolsDashboard;
