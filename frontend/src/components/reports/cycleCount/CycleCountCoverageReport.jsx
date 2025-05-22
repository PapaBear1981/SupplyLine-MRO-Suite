import { Alert, Spinner, Card, Row, Col, Table, ProgressBar, Badge } from 'react-bootstrap';
import { Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const CycleCountCoverageReport = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading coverage report...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Report</Alert.Heading>
        <p>{error.message || 'An error occurred while loading the coverage report.'}</p>
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert variant="info">
        <Alert.Heading>No Data Available</Alert.Heading>
        <p>Apply filters and click "Apply Filters" to load the coverage report.</p>
      </Alert>
    );
  }

  // Prepare chart data for coverage by location
  const locationData = {
    labels: data.coverage_by_location.map(item => item.location),
    datasets: [
      {
        label: 'Coverage (%)',
        data: data.coverage_by_location.map(item => item.coverage_percentage),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }
    ]
  };

  // Prepare chart data for coverage by category
  const categoryData = {
    labels: data.coverage_by_category.map(item => item.category),
    datasets: [
      {
        label: 'Coverage (%)',
        data: data.coverage_by_category.map(item => item.coverage_percentage),
        backgroundColor: 'rgba(255, 159, 64, 0.5)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 1
      }
    ]
  };

  // Prepare chart data for overall coverage
  const overallData = {
    labels: ['Counted', 'Not Counted'],
    datasets: [
      {
        data: [
          data.overall_coverage.counted_items,
          data.overall_coverage.total_items - data.overall_coverage.counted_items
        ],
        backgroundColor: [
          'rgba(75, 192, 192, 0.5)',
          'rgba(255, 99, 132, 0.5)'
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1
      }
    ]
  };

  // Chart options
  const barOptions = {
    responsive: true,
    indexAxis: 'y',
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Coverage by Location',
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Coverage (%)'
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: 'Overall Coverage',
      },
    }
  };

  return (
    <div>
      <Row className="mb-4">
        <Col md={4}>
          <Card className="h-100">
            <Card.Body className="text-center">
              <h2 className="display-4 text-primary">
                {data.overall_coverage.coverage_percentage}%
              </h2>
              <p className="text-muted mb-0">Overall Coverage</p>
              <ProgressBar 
                now={data.overall_coverage.coverage_percentage} 
                variant={data.overall_coverage.coverage_percentage > 75 ? 'success' : data.overall_coverage.coverage_percentage > 50 ? 'warning' : 'danger'} 
                className="mt-2"
              />
              <div className="mt-3">
                <small className="text-muted">
                  {data.overall_coverage.counted_items} of {data.overall_coverage.total_items} items counted in the last {data.days_threshold} days
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={8}>
          <Card className="h-100">
            <Card.Body>
              <Pie data={overallData} options={pieOptions} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Coverage by Location</h6>
            </Card.Header>
            <Card.Body>
              <Bar data={locationData} options={barOptions} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Coverage by Category</h6>
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
                      text: 'Coverage by Category',
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
          <h6 className="mb-0">Items Not Counted in {data.days_threshold} Days</h6>
        </Card.Header>
        <Card.Body className="p-0">
          {data.uncounted_items.length === 0 ? (
            <Alert variant="success" className="m-3">
              All items have been counted within the specified timeframe.
            </Alert>
          ) : (
            <div className="table-responsive">
              <Table striped bordered hover className="mb-0">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Type</th>
                    <th>Location</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  {data.uncounted_items.map((item, index) => (
                    <tr key={index}>
                      <td>
                        {item.identifier} - {item.description}
                      </td>
                      <td>
                        <Badge bg={item.type === 'tool' ? 'primary' : 'info'}>
                          {item.type}
                        </Badge>
                      </td>
                      <td>{item.location}</td>
                      <td>{item.category}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {data.uncounted_items_count > data.uncounted_items.length && (
                <div className="p-3 text-center">
                  <small className="text-muted">
                    Showing {data.uncounted_items.length} of {data.uncounted_items_count} uncounted items
                  </small>
                </div>
              )}
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default CycleCountCoverageReport;
