import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Row, Col, Card, Alert } from 'react-bootstrap';
import { FaChartPie, FaChartLine } from 'react-icons/fa';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { fetchOrderAnalytics } from '../../store/ordersSlice';

const CHART_COLORS = ['#0d6efd', '#6f42c1', '#20c997', '#ffc107', '#dc3545', '#0dcaf0'];

const AnalyticsTab = () => {
  const dispatch = useDispatch();
  const { analytics, analyticsLoading } = useSelector((state) => state.orders);

  useEffect(() => {
    dispatch(fetchOrderAnalytics());
  }, [dispatch]);

  if (analyticsLoading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <Alert variant="info">
        No analytics data available yet. Create some orders to see analytics!
      </Alert>
    );
  }

  // Prepare data for charts
  const statusData = analytics.status_breakdown
    ? analytics.status_breakdown.map(({ status, count }) => ({
        name: status.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
        value: count,
      }))
    : [];

  const typeData = analytics.type_breakdown
    ? analytics.type_breakdown.map(({ type, count }) => ({
        name: type.charAt(0).toUpperCase() + type.slice(1),
        value: count,
      }))
    : [];

  const priorityData = analytics.priority_breakdown
    ? analytics.priority_breakdown.map(({ priority, count }) => ({
        name: priority.charAt(0).toUpperCase() + priority.slice(1),
        count: count,
      }))
    : [];

  // Calculate total orders from status breakdown
  const totalOrders = statusData.reduce((sum, item) => sum + item.value, 0);

  return (
    <>
      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center border-primary">
            <Card.Body>
              <h2 className="text-primary mb-0">{totalOrders}</h2>
              <small className="text-muted">Total Orders</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-success">
            <Card.Body>
              <h2 className="text-success mb-0">{analytics.total_open || 0}</h2>
              <small className="text-muted">Open Orders</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-danger">
            <Card.Body>
              <h2 className="text-danger mb-0">{analytics.late_count || 0}</h2>
              <small className="text-muted">Late Orders</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center border-warning">
            <Card.Body>
              <h2 className="text-warning mb-0">{analytics.due_soon_count || 0}</h2>
              <small className="text-muted">Due Soon</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row>
        <Col md={6} className="mb-4">
          <Card>
            <Card.Header>
              <FaChartPie className="me-2" />
              Orders by Status
            </Card.Header>
            <Card.Body>
              {statusData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Alert variant="info" className="mb-0">No status data available</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} className="mb-4">
          <Card>
            <Card.Header>
              <FaChartPie className="me-2" />
              Orders by Type
            </Card.Header>
            <Card.Body>
              {typeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={typeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {typeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Alert variant="info" className="mb-0">No type data available</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={12} className="mb-4">
          <Card>
            <Card.Header>
              <FaChartLine className="me-2" />
              Orders by Priority
            </Card.Header>
            <Card.Body>
              {priorityData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={priorityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#0d6efd" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Alert variant="info" className="mb-0">No priority data available</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </>
  );
};

export default AnalyticsTab;

