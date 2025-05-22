import { Alert, Spinner, Card, Row, Col, Table, Badge } from 'react-bootstrap';
import { Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
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
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const CycleCountDiscrepancyReport = ({ data, loading, error }) => {
  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Loading discrepancy report...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error Loading Report</Alert.Heading>
        <p>{error.message || 'An error occurred while loading the discrepancy report.'}</p>
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert variant="info">
        <Alert.Heading>No Data Available</Alert.Heading>
        <p>Apply filters and click "Apply Filters" to load the discrepancy report.</p>
      </Alert>
    );
  }

  // Prepare chart data for discrepancy trend
  const trendData = {
    labels: data.discrepancy_trend.map(item => item.date),
    datasets: [
      {
        label: 'Discrepancies',
        data: data.discrepancy_trend.map(item => item.count),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.1
      }
    ]
  };

  // Prepare chart data for discrepancy by type
  const typeData = {
    labels: data.discrepancy_by_type.map(item => item.type),
    datasets: [
      {
        label: 'Discrepancies by Type',
        data: data.discrepancy_by_type.map(item => item.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(153, 102, 255, 0.5)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
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
        text: 'Discrepancy Trend Over Time',
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

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: 'Discrepancies by Type',
      },
    }
  };

  // Helper function to get badge variant based on discrepancy type
  const getDiscrepancyBadgeVariant = (type) => {
    switch (type) {
      case 'quantity':
        return 'warning';
      case 'location':
        return 'info';
      case 'condition':
        return 'secondary';
      case 'missing':
        return 'danger';
      case 'extra':
        return 'success';
      default:
        return 'primary';
    }
  };

  return (
    <div>
      <Row className="mb-4">
        <Col md={4}>
          <Card className="h-100">
            <Card.Body className="text-center">
              <h2 className="display-4 text-danger">{data.total_discrepancies}</h2>
              <p className="text-muted mb-0">Total Discrepancies</p>
              <div className="mt-3">
                {data.discrepancy_by_type.map((item, index) => (
                  <Badge 
                    key={index} 
                    bg={getDiscrepancyBadgeVariant(item.type)}
                    className="me-2 mb-2"
                  >
                    {item.type}: {item.count}
                  </Badge>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={8}>
          <Card className="h-100">
            <Card.Body>
              <Line data={trendData} options={lineOptions} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Discrepancies by Type</h6>
            </Card.Header>
            <Card.Body>
              <Pie data={typeData} options={pieOptions} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6 className="mb-0">Discrepancies by Location</h6>
            </Card.Header>
            <Card.Body>
              <div className="table-responsive">
                <Table striped bordered hover className="mb-0">
                  <thead>
                    <tr>
                      <th>Location</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.discrepancy_by_location.map((item, index) => (
                      <tr key={index}>
                        <td>{item.location}</td>
                        <td>{item.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card>
        <Card.Header>
          <h6 className="mb-0">Discrepancy Details</h6>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="table-responsive">
            <Table striped bordered hover className="mb-0">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Type</th>
                  <th>Expected</th>
                  <th>Actual</th>
                  <th>Discrepancy Type</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {data.discrepancies.slice(0, 10).map((item, index) => (
                  <tr key={index}>
                    <td>
                      {item.item_type === 'tool' ? (
                        <span>
                          {item.item_details.tool_number} - {item.item_details.description}
                        </span>
                      ) : (
                        <span>
                          {item.item_details.part_number} - {item.item_details.description}
                        </span>
                      )}
                    </td>
                    <td>{item.item_type}</td>
                    <td>
                      {item.discrepancy_type === 'quantity' ? (
                        <span>{item.expected_quantity}</span>
                      ) : item.discrepancy_type === 'location' ? (
                        <span>{item.expected_location}</span>
                      ) : (
                        <span>-</span>
                      )}
                    </td>
                    <td>
                      {item.discrepancy_type === 'quantity' ? (
                        <span>{item.actual_quantity}</span>
                      ) : item.discrepancy_type === 'location' ? (
                        <span>{item.actual_location}</span>
                      ) : (
                        <span>-</span>
                      )}
                    </td>
                    <td>
                      <Badge bg={getDiscrepancyBadgeVariant(item.discrepancy_type)}>
                        {item.discrepancy_type}
                      </Badge>
                    </td>
                    <td>{new Date(item.counted_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
          {data.discrepancies.length > 10 && (
            <div className="p-3 text-center">
              <small className="text-muted">
                Showing 10 of {data.discrepancies.length} discrepancies
              </small>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default CycleCountDiscrepancyReport;
