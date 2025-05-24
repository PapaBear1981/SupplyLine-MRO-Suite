import { useEffect, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Row, Col, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { Line, Bar, Pie } from 'react-chartjs-2';
import CycleCountExportImport from './CycleCountExportImport';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { fetchCycleCountAnalytics } from '../../store/cycleCountSlice';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const CycleCountAdvancedAnalytics = () => {
  const dispatch = useDispatch();
  const { data: analytics, loading, error } = useSelector((state) => state.cycleCount.analytics);

  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    dispatch(fetchCycleCountAnalytics(dateRange));
  }, [dispatch, dateRange]);

  const handleDateRangeChange = (field, value) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Chart configurations - memoized for performance (must be at top level)
  const accuracyTrendData = useMemo(() => ({
    labels: analytics?.accuracy_trends?.map(trend => new Date(trend.date).toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Accuracy Rate (%)',
        data: analytics?.accuracy_trends?.map(trend => trend.accuracy_rate) || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        tension: 0.1,
      },
    ],
  }), [analytics?.accuracy_trends]);

  const discrepancyTypeData = useMemo(() => ({
    labels: analytics?.discrepancy_types?.map(type => type.type) || [],
    datasets: [
      {
        data: analytics?.discrepancy_types?.map(type => type.count) || [],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(236, 72, 153, 0.8)',
        ],
      },
    ],
  }), [analytics?.discrepancy_types]);

  const userPerformanceData = useMemo(() => ({
    labels: analytics?.user_performance?.map(user => `User ${user.user_id}`) || [],
    datasets: [
      {
        label: 'Accuracy Rate (%)',
        data: analytics?.user_performance?.map(user => user.accuracy_rate) || [],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
      },
    ],
  }), [analytics?.user_performance]);

  const batchTrendData = useMemo(() => ({
    labels: analytics?.batch_trends?.map(trend => new Date(trend.date).toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Batches Created',
        data: analytics?.batch_trends?.map(trend => trend.batches_created) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.1,
      },
      {
        label: 'Batches Completed',
        data: analytics?.batch_trends?.map(trend => trend.batches_completed) || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        tension: 0.1,
      },
    ],
  }), [analytics?.batch_trends]);

  const chartOptions = useMemo(() => ({
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }), []);

  const refreshAnalytics = () => {
    dispatch(fetchCycleCountAnalytics(dateRange));
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading analytics...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        Error loading analytics: {error.error || 'Unknown error'}
      </Alert>
    );
  }

  if (!analytics) {
    return (
      <Alert variant="info">
        No analytics data available for the selected date range.
      </Alert>
    );
  }

  return (
    <div>
      {/* Date Range Controls */}
      <Card className="mb-4">
        <Card.Header>
          <h5>Analytics Date Range</h5>
        </Card.Header>
        <Card.Body>
          <Row className="align-items-end">
            <Col md={4}>
              <Form.Group>
                <Form.Label>Start Date</Form.Label>
                <Form.Control
                  type="date"
                  value={dateRange.start_date}
                  onChange={(e) => handleDateRangeChange('start_date', e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group>
                <Form.Label>End Date</Form.Label>
                <Form.Control
                  type="date"
                  value={dateRange.end_date}
                  onChange={(e) => handleDateRangeChange('end_date', e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Button variant="primary" onClick={refreshAnalytics}>
                Refresh Analytics
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Export/Import Results */}
      <CycleCountExportImport
        mode="results"
        onImportSuccess={() => {
          // Refresh analytics after successful import
          dispatch(fetchCycleCountAnalytics(dateRange));
        }}
      />

      {/* Coverage Metrics */}
      <Row className="mb-4">
        <Col md={6}>
          <Card className="h-100">
            <Card.Header>
              <h5>Tool Coverage</h5>
            </Card.Header>
            <Card.Body className="text-center">
              <h2 className="text-primary">
                {analytics.coverage?.tools?.coverage_rate || 0}%
              </h2>
              <p className="text-muted">
                {analytics.coverage?.tools?.counted || 0} of {analytics.coverage?.tools?.total || 0} tools counted
              </p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="h-100">
            <Card.Header>
              <h5>Chemical Coverage</h5>
            </Card.Header>
            <Card.Body className="text-center">
              <h2 className="text-success">
                {analytics.coverage?.chemicals?.coverage_rate || 0}%
              </h2>
              <p className="text-muted">
                {analytics.coverage?.chemicals?.counted || 0} of {analytics.coverage?.chemicals?.total || 0} chemicals counted
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        <Col md={8}>
          <Card>
            <Card.Header>
              <h5>Accuracy Trends</h5>
            </Card.Header>
            <Card.Body>
              {analytics.accuracy_trends?.length > 0 ? (
                <Line data={accuracyTrendData} options={chartOptions} />
              ) : (
                <Alert variant="info">No accuracy trend data available</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card>
            <Card.Header>
              <h5>Discrepancy Types</h5>
            </Card.Header>
            <Card.Body>
              {analytics.discrepancy_types?.length > 0 ? (
                <Pie data={discrepancyTypeData} />
              ) : (
                <Alert variant="info">No discrepancy data available</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5>User Performance</h5>
            </Card.Header>
            <Card.Body>
              {analytics.user_performance?.length > 0 ? (
                <Bar data={userPerformanceData} options={chartOptions} />
              ) : (
                <Alert variant="info">No user performance data available</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5>Batch Completion Trends</h5>
            </Card.Header>
            <Card.Body>
              {analytics.batch_trends?.length > 0 ? (
                <Line data={batchTrendData} options={chartOptions} />
              ) : (
                <Alert variant="info">No batch trend data available</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CycleCountAdvancedAnalytics;
