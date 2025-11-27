import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { Row } from 'react-bootstrap';
import api from '../../services/api';
import StatCard from '../common/StatCard';

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

  return (
    <div className="mb-4">
      <Row className="g-3">
        <StatCard
          title="Total Tools"
          value={totalTools}
          icon="tools"
          bgColor="bg-primary-static"
        />
        <StatCard
          title="Available"
          value={availableTools}
          icon="check-circle"
          bgColor="bg-success-static"
        />
        <StatCard
          title="Checked Out"
          value={checkedOutTools}
          icon="person-fill"
          bgColor="bg-info-static"
        />
        <StatCard
          title="Maintenance"
          value={maintenanceTools}
          icon="wrench"
          bgColor="bg-warning-static"
          textColor="text-dark"
        />
        <StatCard
          title="Overdue Checkouts"
          value={overdueCheckouts}
          icon="exclamation-triangle"
          bgColor="bg-danger-static"
        />
        <StatCard
          title="Overdue Calibrations"
          value={calibrationStats.overdue}
          icon="calendar-x"
          bgColor="bg-danger-static"
          loading={loading}
        />
      </Row>
    </div>
  );
};

export default ToolsDashboard;
