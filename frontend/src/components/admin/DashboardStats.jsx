import React from 'react';
import { Card, Row, Col, Badge, ListGroup, Alert } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import LoadingSpinner from '../common/LoadingSpinner';

const DashboardStats = ({ stats, loading }) => {
  if (loading) {
    return <LoadingSpinner />;
  }

  if (!stats) {
    return (
      <Alert variant="info">
        Dashboard statistics are not available. Please try again later.
      </Alert>
    );
  }

  // Format activity data for chart
  const activityData = stats.activityOverTime || [];
  
  // Format department data for pie chart
  const departmentData = stats.departmentDistribution || [];
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="dashboard-stats mb-4">
      <Card className="mb-4">
        <Card.Header as="h5">System Overview</Card.Header>
        <Card.Body>
          <Row>
            <Col md={3} sm={6} className="mb-3">
              <div className="stat-card">
                <h3>{stats.counts?.users || 0}</h3>
                <p>Total Users</p>
                <Badge bg="info">{stats.counts?.activeUsers || 0} Active</Badge>
              </div>
            </Col>
            <Col md={3} sm={6} className="mb-3">
              <div className="stat-card">
                <h3>{stats.counts?.tools || 0}</h3>
                <p>Total Tools</p>
                <Badge bg="success">{stats.counts?.availableTools || 0} Available</Badge>
              </div>
            </Col>
            <Col md={3} sm={6} className="mb-3">
              <div className="stat-card">
                <h3>{stats.counts?.checkouts || 0}</h3>
                <p>Total Checkouts</p>
                <Badge bg="warning">{stats.counts?.activeCheckouts || 0} Active</Badge>
              </div>
            </Col>
            <Col md={3} sm={6} className="mb-3">
              <div className="stat-card">
                <h3>{stats.counts?.pendingRegistrations || 0}</h3>
                <p>Pending Registrations</p>
                <Badge bg="danger">Require Approval</Badge>
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Row>
        <Col md={7}>
          <Card className="mb-4">
            <Card.Header as="h5">Activity Over Time (Last 30 Days)</Card.Header>
            <Card.Body>
              {activityData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={activityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" name="Activities" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Alert variant="info">No activity data available for the last 30 days.</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col md={5}>
          <Card className="mb-4">
            <Card.Header as="h5">Department Distribution</Card.Header>
            <Card.Body>
              {departmentData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={departmentData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                      nameKey="department"
                      label={({ department, count }) => `${department}: ${count}`}
                    >
                      {departmentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Alert variant="info">No department data available.</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Header as="h5">Recent Activity</Card.Header>
        <Card.Body>
          <ListGroup variant="flush">
            {stats.recentActivity && stats.recentActivity.length > 0 ? (
              stats.recentActivity.map((activity, index) => (
                <ListGroup.Item key={index} className="d-flex justify-content-between align-items-start">
                  <div className="ms-2 me-auto">
                    <div className="fw-bold">{activity.action_type}</div>
                    {activity.action_details}
                  </div>
                  <Badge bg="primary" pill>
                    {new Date(activity.timestamp).toLocaleString()}
                  </Badge>
                </ListGroup.Item>
              ))
            ) : (
              <Alert variant="info">No recent activity available.</Alert>
            )}
          </ListGroup>
        </Card.Body>
      </Card>
    </div>
  );
};

export default DashboardStats;
