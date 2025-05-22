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

const CycleCountAccuracyReport = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading accuracy report...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Report</Alert.Heading>
        <p>{error.message || 'An error occurred while loading the accuracy report.'}</p>
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert variant="info">
        <Alert.Heading>No Data Available</Alert.Heading>
        <p>Apply filters and click "Apply Filters" to load the accuracy report.</p>
      </Alert>
    );
  }

  // Prepare chart data for accuracy trend
  const trendData = {
    labels: data.accuracy_trend.map(item => item.date),
    datasets: [
      {
        label: 'Accuracy Rate (%)',
        data: data.accuracy_trend.map(item => item.accuracy),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }
    ]
  };

  // Prepare chart data for accuracy by location
  const locationData = {
    labels: data.accuracy_by_location.map(item => item.location),
    datasets: [
      {
        label: 'Accuracy Rate (%)',
        data: data.accuracy_by_location.map(item => item.accuracy),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }
    ]
  };

  // Prepare chart data for accuracy by category
  const categoryData = {
    labels: data.accuracy_by_category.map(item => item.category),
    datasets: [
      {
        label: 'Accuracy Rate (%)',
        data: data.accuracy_by_category.map(item => item.accuracy),
        backgroundColor: 'rgba(255, 159, 64, 0.5)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 1
      }
    ]
  };

  // Chart options
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Inventory Accuracy Trend',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Accuracy (%)'
        }
      }
    }
  };

  const barOptions = {
    ...options,
    indexAxis: 'y',
    plugins: {
      ...options.plugins,
      title: {
        display: true,
        text: 'Accuracy by Location',
      },
    }
  };

  return (
    <div>
      <Row className="mb-4">
        <Col md={4}>
          <Card className="h-100">
            <Card.Body className="text-center">
              <h2 className="display-4 text-primary">{data.overall_accuracy}%</h2>
              <p className="text-muted mb-0">Overall Accuracy Rate</p>
              <ProgressBar 
                now={data.overall_accuracy} 
                variant={data.overall_accuracy > 90 ? 'success' : data.overall_accuracy > 70 ? 'warning' : 'danger'} 
                className="mt-2"
              />
              <div className="mt-3">
                <small className="text-muted">
                  Based on {data.total_counts} total counts
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={8}>
          <Card className="h-100">
            <Card.Body>
              <Line data={trendData} options={options} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Accuracy by Location</h6>
            </Card.Header>
            <Card.Body>
              <Bar data={locationData} options={barOptions} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Accuracy by Category</h6>
            </Card.Header>
            <Card.Body>
              <Bar 
                data={categoryData} 
                options={{
                  ...barOptions,
                  plugins: {
                    ...barOptions.plugins,
                    title: {
                      display: true,
                      text: 'Accuracy by Category',
                    },
                  }
                }} 
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Header>
          <h6 className="mb-0">Detailed Accuracy Data</h6>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table striped bordered hover className="mb-0">
              <thead>
                <tr>
                  <th>Location</th>
                  <th>Total Counts</th>
                  <th>Accurate Counts</th>
                  <th>Accuracy Rate</th>
                </tr>
              </thead>
              <tbody>
                {data.accuracy_by_location.map((item, index) => (
                  <tr key={index}>
                    <td>{item.location}</td>
                    <td>{item.total}</td>
                    <td>{item.accurate}</td>
                    <td>
                      {item.accuracy}%
                      <ProgressBar 
                        now={item.accuracy} 
                        variant={item.accuracy > 90 ? 'success' : item.accuracy > 70 ? 'warning' : 'danger'} 
                        className="mt-1"
                        style={{ height: '5px' }}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CycleCountAccuracyReport;
