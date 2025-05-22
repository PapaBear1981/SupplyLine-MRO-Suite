import { Alert, Spinner, Card, Row, Col, Table, ProgressBar } from 'react-bootstrap';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
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

const CycleCountPerformanceReport = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading performance report...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Report</Alert.Heading>
        <p>{error.message || 'An error occurred while loading the performance report.'}</p>
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert variant="info">
        <Alert.Heading>No Data Available</Alert.Heading>
        <p>Apply filters and click "Apply Filters" to load the performance report.</p>
      </Alert>
    );
  }

  // Prepare chart data for counts by day
  const countsByDayData = {
    labels: data.counts_by_day.map(item => item.date),
    datasets: [
      {
        label: 'Counts',
        data: data.counts_by_day.map(item => item.count),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }
    ]
  };

  // Prepare chart data for counts by user
  const countsByUserData = {
    labels: data.counts_by_user.map(item => item.user_name),
    datasets: [
      {
        label: 'Counts',
        data: data.counts_by_user.map(item => item.count),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }
    ]
  };

  // Chart options
  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Counts by Day',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Count'
        }
      }
    }
  };

  const barOptions = {
    responsive: true,
    indexAxis: 'y',
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Counts by User',
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Count'
        }
      }
    }
  };

  return (
    <div>
      <Row className="mb-4">
        <Col md={4}>
          <Card className="h-100">
            <Card.Body className="text-center">
              <h2 className="display-4 text-primary">
                {data.completion_rate.completion_percentage}%
              </h2>
              <p className="text-muted mb-0">Batch Completion Rate</p>
              <ProgressBar 
                now={data.completion_rate.completion_percentage} 
                variant={data.completion_rate.completion_percentage > 75 ? 'success' : data.completion_rate.completion_percentage > 50 ? 'warning' : 'danger'} 
                className="mt-2"
              />
              <div className="mt-3">
                <small className="text-muted">
                  {data.completion_rate.completed_batches} of {data.completion_rate.total_batches} batches completed
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100">
            <Card.Body className="text-center">
              <h2 className="display-4 text-info">
                {data.average_completion_time.toFixed(1)}
              </h2>
              <p className="text-muted mb-0">Average Completion Time (hours)</p>
              <div className="mt-3">
                <small className="text-muted">
                  Average time to complete a batch
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100">
            <Card.Body className="text-center">
              <h2 className="display-4 text-success">
                {data.counts_by_user.reduce((sum, user) => sum + user.count, 0)}
              </h2>
              <p className="text-muted mb-0">Total Items Counted</p>
              <div className="mt-3">
                <small className="text-muted">
                  By {data.counts_by_user.length} users
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={7}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Counts by Day</h6>
            </Card.Header>
            <Card.Body>
              <Line data={countsByDayData} options={lineOptions} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={5}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Counts by User</h6>
            </Card.Header>
            <Card.Body>
              <Bar data={countsByUserData} options={barOptions} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Batch Status</h6>
            </Card.Header>
            <Card.Body>
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Count</th>
                    <th>Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Completed</td>
                    <td>{data.completion_rate.completed_batches}</td>
                    <td>
                      {(data.completion_rate.completed_batches / data.completion_rate.total_batches * 100).toFixed(1)}%
                      <ProgressBar 
                        now={data.completion_rate.completed_batches / data.completion_rate.total_batches * 100} 
                        variant="success" 
                        className="mt-1"
                        style={{ height: '5px' }}
                      />
                    </td>
                  </tr>
                  <tr>
                    <td>In Progress</td>
                    <td>{data.completion_rate.in_progress_batches}</td>
                    <td>
                      {(data.completion_rate.in_progress_batches / data.completion_rate.total_batches * 100).toFixed(1)}%
                      <ProgressBar 
                        now={data.completion_rate.in_progress_batches / data.completion_rate.total_batches * 100} 
                        variant="warning" 
                        className="mt-1"
                        style={{ height: '5px' }}
                      />
                    </td>
                  </tr>
                  <tr>
                    <td>Pending</td>
                    <td>{data.completion_rate.pending_batches}</td>
                    <td>
                      {(data.completion_rate.pending_batches / data.completion_rate.total_batches * 100).toFixed(1)}%
                      <ProgressBar 
                        now={data.completion_rate.pending_batches / data.completion_rate.total_batches * 100} 
                        variant="danger" 
                        className="mt-1"
                        style={{ height: '5px' }}
                      />
                    </td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">User Performance</h6>
            </Card.Header>
            <Card.Body className="p-0">
              <div className="table-responsive">
                <Table striped bordered hover className="mb-0">
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Items Counted</th>
                      <th>Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.counts_by_user.map((user, index) => {
                      const totalCounts = data.counts_by_user.reduce((sum, u) => sum + u.count, 0);
                      const percentage = (user.count / totalCounts * 100).toFixed(1);
                      
                      return (
                        <tr key={index}>
                          <td>{user.user_name}</td>
                          <td>{user.count}</td>
                          <td>
                            {percentage}%
                            <ProgressBar 
                              now={percentage} 
                              variant="info" 
                              className="mt-1"
                              style={{ height: '5px' }}
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CycleCountPerformanceReport;
