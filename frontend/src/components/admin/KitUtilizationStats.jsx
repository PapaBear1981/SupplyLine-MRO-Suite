import { useState, useEffect } from 'react';
import { Card, Row, Col, Alert, Form } from 'react-bootstrap';
import { FaChartLine } from 'react-icons/fa';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import api from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';

const KitUtilizationStats = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [utilizationData, setUtilizationData] = useState(null);
  const [timeRange, setTimeRange] = useState(30); // days

  useEffect(() => {
    const fetchUtilizationData = async () => {
      try {
        setLoading(true);
        const response = await api.get('/kits/analytics/utilization', {
          params: { days: timeRange }
        });
        setUtilizationData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching kit utilization:', err);
        // Don't show error if endpoint doesn't exist yet
        if (err.response?.status !== 404) {
          setError('Failed to load utilization data');
        }
        setUtilizationData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUtilizationData();
  }, [timeRange]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];
  const RADIAN = Math.PI / 180;

  const renderTransferLabel = ({
    cx,
    cy,
    midAngle,
    outerRadius,
    percent,
    name
  }) => {
    const radius = outerRadius + 18;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="#2c3e50"
        fontSize={12}
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
      >
        {`${name}: ${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  if (loading) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaChartLine className="me-2" />
          Kit Utilization Statistics
        </Card.Header>
        <Card.Body>
          <LoadingSpinner />
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-4">
        <Card.Header as="h5">
          <FaChartLine className="me-2" />
          Kit Utilization Statistics
        </Card.Header>
        <Card.Body>
          <Alert variant="danger">{error}</Alert>
        </Card.Body>
      </Card>
    );
  }

  // Mock data if API doesn't return data yet
  const mockData = {
    issuancesByKit: [
      { name: 'Kit A', value: 45 },
      { name: 'Kit B', value: 32 },
      { name: 'Kit C', value: 28 },
      { name: 'Kit D', value: 15 },
      { name: 'Kit E', value: 10 }
    ],
    transfersByType: [
      { name: 'Kit to Kit', value: 25 },
      { name: 'Kit to Warehouse', value: 18 },
      { name: 'Warehouse to Kit', value: 22 }
    ],
    activityOverTime: [
      { date: 'Week 1', issuances: 12, transfers: 8 },
      { date: 'Week 2', issuances: 15, transfers: 10 },
      { date: 'Week 3', issuances: 18, transfers: 12 },
      { date: 'Week 4', issuances: 14, transfers: 9 }
    ]
  };

  const data = utilizationData || mockData;

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">
          <FaChartLine className="me-2" />
          Kit Utilization Statistics
        </h5>
        <Form.Select
          size="sm"
          style={{ width: 'auto' }}
          value={timeRange}
          onChange={(e) => setTimeRange(parseInt(e.target.value))}
        >
          <option value={7}>Last 7 Days</option>
          <option value={30}>Last 30 Days</option>
          <option value={90}>Last 90 Days</option>
        </Form.Select>
      </Card.Header>
      <Card.Body>
        <Row>
          {/* Issuances by Kit */}
          <Col md={6} className="mb-4">
            <h6 className="mb-3">Issuances by Kit</h6>
            {data.issuancesByKit && data.issuancesByKit.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={data.issuancesByKit}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8" name="Issuances" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Alert variant="info">No issuance data available</Alert>
            )}
          </Col>

          {/* Transfers by Type */}
          <Col md={6} className="mb-4">
            <h6 className="mb-3">Transfers by Type</h6>
            {data.transfersByType && data.transfersByType.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart margin={{ top: 8, right: 16, bottom: 8, left: 16 }}>
                  <Pie
                    data={data.transfersByType}
                    cx="50%"
                    cy="50%"
                    labelLine
                    label={renderTransferLabel}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {data.transfersByType.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Alert variant="info">No transfer data available</Alert>
            )}
          </Col>
        </Row>

        {/* Activity Over Time */}
        <Row>
          <Col>
            <h6 className="mb-3">Activity Over Time</h6>
            {data.activityOverTime && data.activityOverTime.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={data.activityOverTime}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="issuances" fill="#8884d8" name="Issuances" />
                  <Bar dataKey="transfers" fill="#82ca9d" name="Transfers" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Alert variant="info">No activity data available</Alert>
            )}
          </Col>
        </Row>

        {/* Summary Stats */}
        {data.summary && (
          <Row className="mt-4">
            <Col md={3} sm={6} className="mb-2">
              <div className="text-center p-2 border rounded">
                <h4 className="mb-0">{data.summary.totalIssuances || 0}</h4>
                <small className="text-muted">Total Issuances</small>
              </div>
            </Col>
            <Col md={3} sm={6} className="mb-2">
              <div className="text-center p-2 border rounded">
                <h4 className="mb-0">{data.summary.totalTransfers || 0}</h4>
                <small className="text-muted">Total Transfers</small>
              </div>
            </Col>
            <Col md={3} sm={6} className="mb-2">
              <div className="text-center p-2 border rounded">
                <h4 className="mb-0">{data.summary.activeKits || 0}</h4>
                <small className="text-muted">Active Kits</small>
              </div>
            </Col>
            <Col md={3} sm={6} className="mb-2">
              <div className="text-center p-2 border rounded">
                <h4 className="mb-0">{data.summary.avgUtilization || 0}%</h4>
                <small className="text-muted">Avg Utilization</small>
              </div>
            </Col>
          </Row>
        )}

        {!utilizationData && (
          <Alert variant="info" className="mt-3 mb-0">
            <small>
              <strong>Note:</strong> Displaying sample data. Connect to backend API for real-time statistics.
            </small>
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default KitUtilizationStats;

