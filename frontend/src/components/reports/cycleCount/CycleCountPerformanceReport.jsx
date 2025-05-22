import { Card, Table, Row, Col, Alert, ProgressBar } from 'react-bootstrap';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const CycleCountPerformanceReport = ({ data }) => {
  if (!data) {
    return (
      <Alert variant="info">
        No performance data available for the selected time period.
      </Alert>
    );
  }

  const { batches, summary, user_performance, trends } = data;

  // Chart data for batch completion trends
  const trendChartData = {
    labels: trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Batches Created',
        data: trends.map(t => t.batches_created),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.1,
      },
      {
        label: 'Batches Completed',
        data: trends.map(t => t.batches_completed),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        tension: 0.1,
      },
    ],
  };

  const trendChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Batch Creation and Completion Trends',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  // Chart data for user performance
  const topUsers = user_performance.slice(0, 10);
  const userChartData = {
    labels: topUsers.map(u => u.name),
    datasets: [
      {
        label: 'Counts Performed',
        data: topUsers.map(u => u.counts_performed),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
    ],
  };

  const userChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Top 10 Performers by Count Volume',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'pending': return 'warning';
      case 'failed': return 'danger';
      case 'archived': return 'dark';
      default:
        console.warn(`Unknown status: ${status}`);
        return 'secondary';
    }
  };

  const formatDate = (dateString) => {
    return dateString ? new Date(dateString).toLocaleDateString() : 'N/A';
  };

  return (
    <div>
      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-primary">{summary.total_batches}</h3>
              <p className="mb-0">Total Batches</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-success">{summary.completed_batches}</h3>
              <p className="mb-0">Completed Batches</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-info">{summary.average_completion_time_days}</h3>
              <p className="mb-0">Avg. Completion (Days)</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-warning">
                {summary.total_batches > 0 ?
                  Math.round((summary.completed_batches / summary.total_batches) * 100) : 0}%
              </h3>
              <p className="mb-0">Completion Rate</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        {trends.length > 0 && (
          <Col md={8}>
            <Card>
              <Card.Header>
                <h5>Batch Performance Trends</h5>
              </Card.Header>
              <Card.Body>
                <Line data={trendChartData} options={trendChartOptions} />
              </Card.Body>
            </Card>
          </Col>
        )}

        {user_performance.length > 0 && (
          <Col md={4}>
            <Card>
              <Card.Header>
                <h5>User Performance</h5>
              </Card.Header>
              <Card.Body>
                <Bar data={userChartData} options={userChartOptions} />
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {/* Batch Details Table */}
      {batches.length > 0 && (
        <Card className="mb-4">
          <Card.Header>
            <h5>Batch Performance Details</h5>
          </Card.Header>
          <Card.Body>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Batch Name</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                  <th>Completion Time</th>
                  <th>Created By</th>
                </tr>
              </thead>
              <tbody>
                {batches.slice(0, 20).map((batch, index) => (
                  <tr key={index}>
                    <td>
                      <strong>{batch.name}</strong>
                      <br />
                      <small className="text-muted">ID: {batch.id}</small>
                    </td>
                    <td>
                      <span className={`badge bg-${getStatusColor(batch.status)}`}>
                        {batch.status.charAt(0).toUpperCase() + batch.status.slice(1).replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      <div>
                        <ProgressBar
                          now={batch.completion_rate}
                          label={`${batch.completion_rate}%`}
                          variant={batch.completion_rate === 100 ? 'success' :
                                  batch.completion_rate >= 50 ? 'primary' : 'warning'}
                        />
                        <small className="text-muted">
                          {batch.counted_items}/{batch.total_items} items
                        </small>
                      </div>
                    </td>
                    <td>{formatDate(batch.start_date)}</td>
                    <td>{formatDate(batch.end_date)}</td>
                    <td>
                      {batch.completion_time_days ?
                        `${batch.completion_time_days} days` :
                        'In Progress'}
                    </td>
                    <td>{batch.created_by}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
            {batches.length > 20 && (
              <Alert variant="info" className="mt-3">
                Showing first 20 batches. Total: {batches.length}
              </Alert>
            )}
          </Card.Body>
        </Card>
      )}

      {/* User Performance Table */}
      {user_performance.length > 0 && (
        <Card>
          <Card.Header>
            <h5>User Performance Details</h5>
          </Card.Header>
          <Card.Body>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>User</th>
                  <th>Counts Performed</th>
                  <th>Accurate Counts</th>
                  <th>Accuracy Rate</th>
                  <th>Performance Rating</th>
                </tr>
              </thead>
              <tbody>
                {user_performance.map((user, index) => (
                  <tr key={index}>
                    <td>
                      <strong>{user.name}</strong>
                      <br />
                      <small className="text-muted">ID: {user.user_id}</small>
                    </td>
                    <td>{user.counts_performed}</td>
                    <td>{user.accurate_counts}</td>
                    <td>
                      <span className={`badge ${
                        user.accuracy_rate >= 95 ? 'bg-success' :
                        user.accuracy_rate >= 85 ? 'bg-warning' :
                        'bg-danger'
                      }`}>
                        {user.accuracy_rate}%
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${
                        user.accuracy_rate >= 95 && user.counts_performed >= 10 ? 'bg-success' :
                        user.accuracy_rate >= 85 && user.counts_performed >= 5 ? 'bg-primary' :
                        'bg-secondary'
                      }`}>
                        {user.accuracy_rate >= 95 && user.counts_performed >= 10 ? 'Excellent' :
                         user.accuracy_rate >= 85 && user.counts_performed >= 5 ? 'Good' :
                         'Developing'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default CycleCountPerformanceReport;
