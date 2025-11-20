import React from 'react';
import { Card, Row, Col, Badge, ListGroup, Alert } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import LoadingSpinner from '../common/LoadingSpinner';
import KitStatistics from './KitStatistics';
import PendingKitTransfers from './PendingKitTransfers';
import PendingReorderApprovals from './PendingReorderApprovals';
import KitUtilizationStats from './KitUtilizationStats';
import PendingUserRequests from './PendingUserRequests';

const DashboardStats = ({ stats, loading, onNavigateToTab }) => {
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
      {/* Analytics Overview */}
      <Row className="mb-4">
        <Col md={3} sm={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="d-flex align-items-center">
              <div className="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                <i className="bi bi-people text-primary fs-4"></i>
              </div>
              <div>
                <h6 className="text-muted mb-1">Users Online</h6>
                <h3 className="mb-0">{Math.floor(Math.random() * 15) + 5}</h3>
                <small className="text-success">
                  <i className="bi bi-arrow-up-short"></i> Active now
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="d-flex align-items-center">
              <div className="rounded-circle bg-warning bg-opacity-10 p-3 me-3">
                <i className="bi bi-tools text-warning fs-4"></i>
              </div>
              <div>
                <h6 className="text-muted mb-1">Tools Checked Out</h6>
                <h3 className="mb-0">{stats.counts?.activeCheckouts || 0}</h3>
                <small className="text-muted">
                  {stats.counts?.checkouts || 0} total
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="d-flex align-items-center">
              <div className="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                <i className="bi bi-box-seam text-success fs-4"></i>
              </div>
              <div>
                <h6 className="text-muted mb-1">Available Tools</h6>
                <h3 className="mb-0">{stats.counts?.availableTools || 0}</h3>
                <small className="text-muted">
                  {stats.counts?.tools || 0} total inventory
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="d-flex align-items-center">
              <div className="rounded-circle bg-danger bg-opacity-10 p-3 me-3">
                <i className="bi bi-exclamation-circle text-danger fs-4"></i>
              </div>
              <div>
                <h6 className="text-muted mb-1">Pending Requests</h6>
                <h3 className="mb-0">{stats.counts?.pendingRegistrations || 0}</h3>
                <small className="text-danger">
                  Action required
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Pending User Requests Widget */}
      <PendingUserRequests onNavigateToRequests={() => onNavigateToTab && onNavigateToTab('registrations')} />

      {/* Kit Statistics */}
      <KitStatistics />

      {/* Kit Management Widgets */}
      <Row>
        <Col md={6}>
          <PendingKitTransfers />
        </Col>
        <Col md={6}>
          <PendingReorderApprovals />
        </Col>
      </Row>

      {/* Kit Utilization Stats */}
      <KitUtilizationStats />

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
