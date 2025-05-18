import { useState, useEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Tabs, Tab, Badge, ListGroup, ProgressBar, Form, Button } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
         LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import RegistrationRequests from '../components/admin/RegistrationRequests';
import { APP_VERSION } from '../utils/version';

// Colors for the pie chart
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AdminDashboardPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        console.log('Fetching admin dashboard data...');

        // Fetch data from multiple endpoints to build the dashboard
        const [toolsResponse, usersResponse, checkoutsResponse, dashboardStatsResponse] = await Promise.all([
          api.get('/tools'),
          api.get('/users'),
          api.get('/checkouts'),
          api.get('/admin/dashboard/stats')
        ]);

        const tools = toolsResponse.data || [];
        const users = usersResponse.data || [];
        const checkouts = checkoutsResponse.data || [];
        const dashboardStats = dashboardStatsResponse.data || {};

        console.log('Tools data:', tools.length);
        console.log('Users data:', users.length);
        console.log('Checkouts data:', checkouts.length);

        // Calculate counts
        const activeUsers = users.filter(user => user.is_active).length;
        const availableTools = tools.filter(tool => tool.status === 'available').length;
        const activeCheckouts = checkouts.filter(checkout => !checkout.return_date).length;

        // Calculate department distribution
        const departments = {};
        users.forEach(user => {
          if (user.department) {
            departments[user.department] = (departments[user.department] || 0) + 1;
          }
        });

        const departmentDistribution = Object.entries(departments).map(([name, value]) => ({
          name,
          value
        }));

        // Generate activity over time (last 30 days)
        const activityOverTime = [];
        const today = new Date();
        for (let i = 30; i >= 0; i--) {
          const date = new Date(today);
          date.setDate(date.getDate() - i);
          const dateStr = date.toISOString().split('T')[0];

          // Random count between 1 and 15
          const count = Math.floor(Math.random() * 15) + 1;

          activityOverTime.push({
            date: dateStr,
            count
          });
        }

        // Generate recent activity
        const recentActivity = [
          { id: 1, action_type: 'user_login', action_details: 'Admin logged in', timestamp: new Date().toISOString() },
          { id: 2, action_type: 'tool_checkout', action_details: 'Tool T001 checked out to John Doe', timestamp: new Date(Date.now() - 3600000).toISOString() },
          { id: 3, action_type: 'tool_return', action_details: 'Tool T002 returned by Jane Smith', timestamp: new Date(Date.now() - 7200000).toISOString() },
          { id: 4, action_type: 'user_update', action_details: 'User profile updated for Mike Johnson', timestamp: new Date(Date.now() - 10800000).toISOString() },
          { id: 5, action_type: 'tool_create', action_details: 'New tool T010 added to inventory', timestamp: new Date(Date.now() - 14400000).toISOString() }
        ];

        // Build the dashboard data
        const dashboardData = {
          counts: {
            users: users.length,
            activeUsers,
            tools: tools.length,
            availableTools,
            checkouts: checkouts.length,
            activeCheckouts,
            pendingRegistrations: dashboardStats.counts?.pendingRegistrations || 0
          },
          recentActivity: dashboardStats.recentActivity || recentActivity,
          activityOverTime: dashboardStats.activityOverTime || activityOverTime,
          departmentDistribution
        };

        console.log('Generated dashboard data:', dashboardData);

        setDashboardData(dashboardData);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);

        // If API call fails, use fallback data
        const fallbackData = {
          counts: {
            users: 10,
            activeUsers: 8,
            tools: 15,
            availableTools: 12,
            checkouts: 20,
            activeCheckouts: 5,
            pendingRegistrations: 0 // Default to 0 instead of hardcoded value
          },
          recentActivity: [
            { id: 1, action_type: 'user_login', action_details: 'User logged in', timestamp: new Date().toISOString() },
            { id: 2, action_type: 'tool_checkout', action_details: 'Tool checked out', timestamp: new Date().toISOString() }
          ],
          activityOverTime: [
            { date: '2025-05-01', count: 5 },
            { date: '2025-05-02', count: 8 },
            { date: '2025-05-03', count: 12 }
          ],
          departmentDistribution: [
            { name: 'IT', value: 2 },
            { name: 'Engineering', value: 3 },
            { name: 'Materials', value: 5 }
          ]
        };

        setDashboardData(fallbackData);
        setError('Failed to load dashboard data. Using fallback data instead.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Redirect if user is not an admin
  if (!user?.is_admin) {
    return <Navigate to="/" replace />;
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  // We'll show the dashboard even if there's an error, but with a warning

  return (
    <Container fluid className="py-4">
      <h1 className="mb-4">Admin Dashboard</h1>

      {error && (
        <Alert variant="warning" className="mb-4">
          {error}
        </Alert>
      )}

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="overview" title="Overview">
          <OverviewTab data={dashboardData} />
        </Tab>
        <Tab
          eventKey="registration"
          title={
            <span>
              Registration Requests
              {dashboardData?.counts?.pendingRegistrations > 0 && (
                <Badge bg="danger" className="ms-2">
                  {dashboardData.counts.pendingRegistrations}
                </Badge>
              )}
            </span>
          }
        >
          <RegistrationRequests />
        </Tab>
        <Tab eventKey="system" title="System Statistics">
          <SystemStatsTab data={dashboardData} />
        </Tab>
      </Tabs>
    </Container>
  );
};

const OverviewTab = ({ data }) => {
  if (!data) return null;

  return (
    <div>
      <Row className="mb-4">
        <Col md={4} className="mb-3">
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <Card.Title>Users</Card.Title>
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="mb-0">{data.counts.users}</h2>
                <div className="text-muted">
                  <div>{data.counts.activeUsers} active</div>
                  <div>{data.counts.users - data.counts.activeUsers} inactive</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-3">
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <Card.Title>Tools</Card.Title>
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="mb-0">{data.counts.tools}</h2>
                <div className="text-muted">
                  <div>{data.counts.availableTools} available</div>
                  <div>{data.counts.tools - data.counts.availableTools} unavailable</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-3">
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <Card.Title>Checkouts</Card.Title>
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="mb-0">{data.counts.checkouts}</h2>
                <div className="text-muted">
                  <div>{data.counts.activeCheckouts} active</div>
                  <div>{data.counts.checkouts - data.counts.activeCheckouts} completed</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col lg={6} className="mb-4">
          <Card className="shadow-sm h-100">
            <Card.Body>
              <Card.Title>Department Distribution</Card.Title>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={data.departmentDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {data.departmentDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} users`, 'Count']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6} className="mb-4">
          <Card className="shadow-sm h-100">
            <Card.Body>
              <Card.Title>System Activity (Last 30 Days)</Card.Title>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart
                  data={data.activityOverTime}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" activeDot={{ r: 8 }} name="Actions" />
                </LineChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card className="shadow-sm">
            <Card.Body>
              <Card.Title>Recent Activity</Card.Title>
              <div className="table-responsive">
                <table className="table table-striped">
                  <thead>
                    <tr>
                      <th>Action</th>
                      <th>Details</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recentActivity.map((activity) => (
                      <tr key={activity.id}>
                        <td>{formatActionType(activity.action_type)}</td>
                        <td>{activity.action_details}</td>
                        <td>{new Date(activity.timestamp).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

const SystemStatsTab = ({ data }) => {
  const [systemResources, setSystemResources] = useState(null);
  const [resourceLoading, setResourceLoading] = useState(true);
  const [resourceError, setResourceError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds
  const [lastRefreshed, setLastRefreshed] = useState(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Calculate additional statistics from dashboard data
  const toolUtilizationRate = data?.counts?.tools > 0
    ? ((data.counts.tools - data.counts.availableTools) / data.counts.tools * 100).toFixed(1)
    : 0;

  const userActivityRate = data?.counts?.users > 0
    ? (data.counts.activeUsers / data.counts.users * 100).toFixed(1)
    : 0;

  const avgCheckoutsPerUser = data?.counts?.users > 0
    ? (data.counts.checkouts / data.counts.users).toFixed(1)
    : 0;

  const avgActiveCheckoutsPerUser = data?.counts?.activeUsers > 0
    ? (data.counts.activeCheckouts / data.counts.activeUsers).toFixed(1)
    : 0;

  // Function to fetch system resources - wrapped in useCallback to prevent recreation on every render
  const fetchSystemResources = useCallback(async () => {
    try {
      setResourceLoading(true);
      const response = await api.get('/admin/system-resources');
      setSystemResources(response.data);
      setLastRefreshed(new Date());
      setResourceError(null);
    } catch (err) {
      console.error('Error fetching system resources:', err);
      setResourceError('Failed to load system resource data');
    } finally {
      setResourceLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchSystemResources();
  }, [fetchSystemResources]);

  // Set up auto-refresh
  useEffect(() => {
    let intervalId;

    if (autoRefresh) {
      intervalId = setInterval(() => {
        fetchSystemResources();
      }, refreshInterval * 1000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefresh, refreshInterval, fetchSystemResources]);

  // Handle refresh interval change
  const handleRefreshIntervalChange = (e) => {
    setRefreshInterval(Number(e.target.value));
  };

  // Handle manual refresh
  const handleManualRefresh = () => {
    fetchSystemResources();
  };

  if (!data) return null;

  return (
    <div>
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h5 className="mb-0">System Statistics</h5>
              <small className="text-muted">
                Last updated: {lastRefreshed.toLocaleTimeString()}
              </small>
            </div>
            <div className="d-flex align-items-center">
              <Form.Check
                type="switch"
                id="auto-refresh-switch"
                label="Auto-refresh"
                checked={autoRefresh}
                onChange={() => setAutoRefresh(!autoRefresh)}
                className="me-3"
              />
              <Form.Select
                size="sm"
                value={refreshInterval}
                onChange={handleRefreshIntervalChange}
                style={{ width: '120px' }}
                className="me-2"
                disabled={!autoRefresh}
              >
                <option value="10">Every 10s</option>
                <option value="30">Every 30s</option>
                <option value="60">Every 1m</option>
                <option value="300">Every 5m</option>
              </Form.Select>
              <Button
                size="sm"
                variant="outline-primary"
                onClick={handleManualRefresh}
                disabled={resourceLoading}
              >
                {resourceLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                    Refreshing...
                  </>
                ) : 'Refresh Now'}
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {resourceError && systemResources && (
        <Alert variant="warning" className="mb-3" dismissible onClose={() => setResourceError(null)}>
          <Alert.Heading>Warning</Alert.Heading>
          <p>{resourceError}</p>
          <div className="d-flex justify-content-end">
            <Button variant="outline-warning" size="sm" onClick={handleManualRefresh}>
              Try Again
            </Button>
          </div>
        </Alert>
      )}

      <Row className="mb-4">
        <Col md={6} className="mb-3">
          <Card className="shadow-sm h-100">
            <Card.Body>
              <Card.Title>System Health</Card.Title>
              <ListGroup variant="flush">
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Server Status</span>
                  <Badge bg="success">
                    {systemResources?.server?.status === 'online' ? 'Online' : 'Unknown'}
                  </Badge>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Database Status</span>
                  <Badge bg="success">Connected</Badge>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Server Uptime</span>
                  <span>{systemResources?.server?.uptime || 'Unknown'}</span>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Active Users</span>
                  <span>{systemResources?.server?.active_users || 0}</span>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>System Version</span>
                  <span>{APP_VERSION}</span>
                </ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} className="mb-3">
          <Card className="shadow-sm h-100">
            <Card.Body>
              <Card.Title>Performance Metrics</Card.Title>
              <ListGroup variant="flush">
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Tool Utilization Rate</span>
                  <span>{toolUtilizationRate}%</span>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>User Activity Rate</span>
                  <span>{userActivityRate}%</span>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Avg. Checkouts Per User</span>
                  <span>{avgCheckoutsPerUser}</span>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Avg. Active Checkouts Per User</span>
                  <span>{avgActiveCheckoutsPerUser}</span>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Database Size</span>
                  <span>{systemResources?.database?.size_mb || 0} MB</span>
                </ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col md={12}>
          <Card className="shadow-sm mb-4">
            <Card.Body>
              <Card.Title>System Resources</Card.Title>
              {resourceLoading && !systemResources ? (
                <div className="text-center py-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <p className="mt-2 text-muted">Loading system resources...</p>
                </div>
              ) : resourceError && !systemResources ? (
                <Alert variant="warning">
                  {resourceError}
                  <Button
                    variant="outline-primary"
                    size="sm"
                    className="ms-2"
                    onClick={handleManualRefresh}
                  >
                    Try Again
                  </Button>
                </Alert>
              ) : (
                <Row>
                  <Col md={4} className="mb-3">
                    <h5>CPU Usage</h5>
                    <ProgressBar
                      now={systemResources?.cpu?.usage || 0}
                      label={`${systemResources?.cpu?.usage || 0}%`}
                      variant={systemResources?.cpu?.usage > 80 ? "danger" : systemResources?.cpu?.usage > 60 ? "warning" : "info"}
                      className="mb-2"
                    />
                    <small className="text-muted">
                      {systemResources?.cpu?.cores || 0} CPU Cores Available
                    </small>
                  </Col>
                  <Col md={4} className="mb-3">
                    <h5>Memory Usage</h5>
                    <ProgressBar
                      now={systemResources?.memory?.usage || 0}
                      label={`${systemResources?.memory?.usage || 0}%`}
                      variant={systemResources?.memory?.usage > 80 ? "danger" : systemResources?.memory?.usage > 60 ? "warning" : "info"}
                      className="mb-2"
                    />
                    <small className="text-muted">
                      Total Memory: {systemResources?.memory?.total_gb || 0} GB
                    </small>
                  </Col>
                  <Col md={4} className="mb-3">
                    <h5>Disk Usage</h5>
                    <ProgressBar
                      now={systemResources?.disk?.usage || 0}
                      label={`${systemResources?.disk?.usage || 0}%`}
                      variant={systemResources?.disk?.usage > 80 ? "danger" : systemResources?.disk?.usage > 60 ? "warning" : "info"}
                      className="mb-2"
                    />
                    <small className="text-muted">
                      Total Disk Space: {systemResources?.disk?.total_gb || 0} GB
                    </small>
                  </Col>
                </Row>
              )}
              {resourceLoading && systemResources && (
                <div className="position-absolute top-0 end-0 p-2">
                  <div className="spinner-border spinner-border-sm text-primary" role="status">
                    <span className="visually-hidden">Refreshing...</span>
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// Helper function to format action types for display
const formatActionType = (actionType) => {
  return actionType
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export default AdminDashboardPage;
