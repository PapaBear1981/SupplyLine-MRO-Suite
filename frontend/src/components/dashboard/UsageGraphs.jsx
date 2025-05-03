import { useState, useEffect } from 'react';
import { Card, Row, Col, Form, Alert, Table, Badge } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
         LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { useSelector } from 'react-redux';
import api from '../../services/api';

// Colors for the pie chart
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

// Default data structure
const defaultData = {
  checkoutsByDepartment: [],
  checkoutsByDay: [],
  toolUsageByCategory: [],
  mostFrequentlyCheckedOut: [],
  overallStats: {
    totalCheckouts: 0,
    totalReturns: 0,
    currentlyCheckedOut: 0,
    averageDuration: 0,
    overdueCount: 0
  }
};

const UsageGraphs = () => {
  const [timeframe, setTimeframe] = useState('week');
  const [data, setData] = useState(defaultData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';

  // Fetch data based on the timeframe
  useEffect(() => {
    if (isAdmin) {
      fetchUsageData(timeframe);
    }
  }, [timeframe, isAdmin]);

  const fetchUsageData = async (timeframe) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/analytics/usage?timeframe=${timeframe}`);
      setData(response.data);
    } catch (err) {
      console.error('Error fetching usage data:', err);
      setError('Failed to load usage analytics data');
      // Fall back to empty data structure
      setData(defaultData);
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin) {
    return null; // Only show graphs to admins and Materials department
  }

  if (loading) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Usage Analytics</h4>
          <Form.Select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            style={{ width: 'auto' }}
            disabled
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </Form.Select>
        </Card.Header>
        <Card.Body className="text-center p-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3">Loading analytics data...</p>
        </Card.Body>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Usage Analytics</h4>
          <Form.Select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </Form.Select>
        </Card.Header>
        <Card.Body>
          <Alert variant="warning">
            {error}
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  // Check if we have data to display
  const hasData = data.checkoutsByDepartment?.length > 0 ||
                  data.checkoutsByDay?.length > 0 ||
                  data.toolUsageByCategory?.length > 0 ||
                  data.mostFrequentlyCheckedOut?.length > 0 ||
                  (data.overallStats &&
                   (data.overallStats.totalCheckouts > 0 ||
                    data.overallStats.totalReturns > 0 ||
                    data.overallStats.currentlyCheckedOut > 0));

  if (!hasData) {
    return (
      <Card className="shadow-sm mb-4">
        <Card.Header className="bg-light d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Usage Analytics</h4>
          <Form.Select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </Form.Select>
        </Card.Header>
        <Card.Body>
          <Alert variant="info">
            No usage data available for the selected time period.
          </Alert>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light d-flex justify-content-between align-items-center">
        <h4 className="mb-0">Usage Analytics</h4>
        <Form.Select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
          style={{ width: 'auto' }}
        >
          <option value="week">Last Week</option>
          <option value="month">Last Month</option>
          <option value="quarter">Last Quarter</option>
          <option value="year">Last Year</option>
        </Form.Select>
      </Card.Header>
      <Card.Body>
        {/* Overall Stats Section */}
        <Row className="mb-4">
          <Col>
            <h5 className="text-center mb-3">Overall Statistics</h5>
            <Row className="text-center">
              <Col xs={6} md={2} className="mb-3">
                <Card className="h-100 border-0 shadow-sm">
                  <Card.Body>
                    <h3 className="text-primary">{data.overallStats.totalCheckouts}</h3>
                    <div className="text-muted small">Total Checkouts</div>
                  </Card.Body>
                </Card>
              </Col>
              <Col xs={6} md={2} className="mb-3">
                <Card className="h-100 border-0 shadow-sm">
                  <Card.Body>
                    <h3 className="text-success">{data.overallStats.totalReturns}</h3>
                    <div className="text-muted small">Total Returns</div>
                  </Card.Body>
                </Card>
              </Col>
              <Col xs={6} md={3} className="mb-3">
                <Card className="h-100 border-0 shadow-sm">
                  <Card.Body>
                    <h3 className="text-info">{data.overallStats.currentlyCheckedOut}</h3>
                    <div className="text-muted small">Currently Checked Out</div>
                  </Card.Body>
                </Card>
              </Col>
              <Col xs={6} md={2} className="mb-3">
                <Card className="h-100 border-0 shadow-sm">
                  <Card.Body>
                    <h3 className="text-secondary">{data.overallStats.averageDuration}</h3>
                    <div className="text-muted small">Avg. Days Checked Out</div>
                  </Card.Body>
                </Card>
              </Col>
              <Col xs={6} md={3} className="mb-3">
                <Card className="h-100 border-0 shadow-sm">
                  <Card.Body>
                    <h3 className={data.overallStats.overdueCount > 0 ? "text-danger" : "text-success"}>
                      {data.overallStats.overdueCount}
                    </h3>
                    <div className="text-muted small">Overdue Checkouts</div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Col>
        </Row>

        {/* Charts Section */}
        <Row>
          <Col lg={6} className="mb-4">
            <h5 className="text-center mb-3">Checkouts by Department</h5>
            {data.checkoutsByDepartment?.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={data.checkoutsByDepartment}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {data.checkoutsByDepartment.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} checkouts`, 'Count']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-muted p-5">No department data available</div>
            )}
          </Col>
          <Col lg={6} className="mb-4">
            <h5 className="text-center mb-3">Tool Usage by Category</h5>
            {data.toolUsageByCategory?.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={data.toolUsageByCategory}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="checkouts" fill="#8884d8" name="Checkouts" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-muted p-5">No category data available</div>
            )}
          </Col>
        </Row>

        <Row>
          <Col lg={7} className="mb-4">
            <h5 className="text-center mb-3">Checkouts and Returns by Day</h5>
            {data.checkoutsByDay?.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart
                  data={data.checkoutsByDay}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="checkouts" stroke="#8884d8" activeDot={{ r: 8 }} name="Checkouts" />
                  <Line type="monotone" dataKey="returns" stroke="#82ca9d" name="Returns" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-muted p-5">No daily data available</div>
            )}
          </Col>

          <Col lg={5} className="mb-4">
            <h5 className="text-center mb-3">Most Frequently Checked Out Tools</h5>
            {data.mostFrequentlyCheckedOut?.length > 0 ? (
              <div className="table-responsive">
                <Table hover size="sm" className="border">
                  <thead className="bg-light">
                    <tr>
                      <th>Tool Number</th>
                      <th>Description</th>
                      <th className="text-center">Checkouts</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.mostFrequentlyCheckedOut.map((tool) => (
                      <tr key={tool.id}>
                        <td>{tool.tool_number}</td>
                        <td>{tool.description}</td>
                        <td className="text-center">
                          <Badge bg="primary" pill>{tool.checkouts}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            ) : (
              <div className="text-center text-muted p-5">No tool usage data available</div>
            )}
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};

export default UsageGraphs;
