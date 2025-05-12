import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Tabs, Tab, Badge } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
         LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import api from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import RegistrationRequests from '../components/admin/RegistrationRequests';

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
        // Use the health endpoint instead of the admin dashboard stats endpoint
        const response = await api.get('/health');
        console.log('Health response:', response);

        // Create mock dashboard data for testing
        const mockData = {
          counts: {
            users: 10,
            activeUsers: 8,
            tools: 50,
            availableTools: 40,
            checkouts: 20,
            activeCheckouts: 5,
            pendingRegistrations: 3
          },
          recentActivity: [
            {
              id: 1,
              action_type: 'user_login',
              action_details: 'User 1 (Admin) logged in',
              timestamp: new Date().toISOString()
            }
          ],
          activityOverTime: [
            { date: '2025-05-01', count: 5 },
            { date: '2025-05-02', count: 8 },
            { date: '2025-05-03', count: 12 },
            { date: '2025-05-04', count: 7 },
            { date: '2025-05-05', count: 10 }
          ],
          departmentDistribution: [
            { name: 'IT', value: 2 },
            { name: 'Materials', value: 3 },
            { name: 'Maintenance', value: 5 }
          ]
        };

        setDashboardData(mockData);
        setError(null);
      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.');
        console.error('Error fetching dashboard data:', err);
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

  if (error) {
    return (
      <Container className="py-4">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      <h1 className="mb-4">Admin Dashboard</h1>

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
  if (!data) return null;

  return (
    <div>
      <Row>
        <Col>
          <Card className="shadow-sm mb-4">
            <Card.Body>
              <Card.Title>System Statistics</Card.Title>
              <p>This tab can be expanded with additional system statistics and metrics.</p>
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
