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

const CycleCountCoverageReport = ({ data }) => {
  if (!data) {
    return (
      <Alert variant="info">
        No coverage data available for the selected time period.
      </Alert>
    );
  }

  const { summary, uncounted_items, by_location, trends } = data;

  // Chart data for coverage trends
  const trendChartData = {
    labels: trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Items Counted',
        data: trends.map(t => t.items_counted),
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
        text: 'Coverage Trends Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  // Chart data for location coverage
  const locationChartData = {
    labels: by_location.map(l => l.location),
    datasets: [
      {
        label: 'Coverage Rate (%)',
        data: by_location.map(l => l.coverage_rate),
        backgroundColor: by_location.map(l => 
          l.coverage_rate >= 80 ? 'rgba(34, 197, 94, 0.8)' :
          l.coverage_rate >= 50 ? 'rgba(251, 191, 36, 0.8)' :
          'rgba(239, 68, 68, 0.8)'
        ),
        borderColor: by_location.map(l => 
          l.coverage_rate >= 80 ? 'rgb(34, 197, 94)' :
          l.coverage_rate >= 50 ? 'rgb(251, 191, 36)' :
          'rgb(239, 68, 68)'
        ),
        borderWidth: 1,
      },
    ],
  };

  const locationChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Coverage Rate by Location',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      },
    },
  };

  const formatDate = (dateString) => {
    return dateString ? new Date(dateString).toLocaleDateString() : 'Never';
  };

  const getDaysSinceLastCount = (dateString) => {
    if (!dateString) return 'Never';
    const lastCount = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - lastCount);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return `${diffDays} days ago`;
  };

  return (
    <div>
      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-primary">{summary.total_inventory}</h3>
              <p className="mb-0">Total Inventory</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-success">{summary.counted_items}</h3>
              <p className="mb-0">Items Counted</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-warning">{summary.uncounted_items}</h3>
              <p className="mb-0">Items Not Counted</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className={`${summary.coverage_rate >= 80 ? 'text-success' : summary.coverage_rate >= 50 ? 'text-warning' : 'text-danger'}`}>
                {summary.coverage_rate}%
              </h3>
              <p className="mb-0">Coverage Rate</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Overall Coverage Progress */}
      <Card className="mb-4">
        <Card.Header>
          <h5>Overall Coverage Progress</h5>
        </Card.Header>
        <Card.Body>
          <ProgressBar 
            now={summary.coverage_rate} 
            label={`${summary.coverage_rate}%`}
            variant={summary.coverage_rate >= 80 ? 'success' : 
                    summary.coverage_rate >= 50 ? 'warning' : 'danger'}
            style={{ height: '30px', fontSize: '16px' }}
          />
          <div className="mt-2 text-center">
            <small className="text-muted">
              {summary.counted_items} of {summary.total_inventory} items counted
            </small>
          </div>
        </Card.Body>
      </Card>

      {/* Charts */}
      <Row className="mb-4">
        {trends.length > 0 && (
          <Col md={8}>
            <Card>
              <Card.Header>
                <h5>Coverage Trends</h5>
              </Card.Header>
              <Card.Body>
                <Line data={trendChartData} options={trendChartOptions} />
              </Card.Body>
            </Card>
          </Col>
        )}
        
        {by_location.length > 0 && (
          <Col md={4}>
            <Card>
              <Card.Header>
                <h5>Coverage by Location</h5>
              </Card.Header>
              <Card.Body>
                <Bar data={locationChartData} options={locationChartOptions} />
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {/* Location Coverage Details */}
      {by_location.length > 0 && (
        <Card className="mb-4">
          <Card.Header>
            <h5>Location Coverage Details</h5>
          </Card.Header>
          <Card.Body>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Location</th>
                  <th>Total Items</th>
                  <th>Counted Items</th>
                  <th>Coverage Rate</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {by_location.map((location, index) => (
                  <tr key={index}>
                    <td>{location.location}</td>
                    <td>{location.total_items}</td>
                    <td>{location.counted_items}</td>
                    <td>
                      <div>
                        <ProgressBar 
                          now={location.coverage_rate} 
                          label={`${location.coverage_rate}%`}
                          variant={location.coverage_rate >= 80 ? 'success' : 
                                  location.coverage_rate >= 50 ? 'warning' : 'danger'}
                          style={{ height: '20px' }}
                        />
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${
                        location.coverage_rate >= 80 ? 'bg-success' :
                        location.coverage_rate >= 50 ? 'bg-warning' :
                        'bg-danger'
                      }`}>
                        {location.coverage_rate >= 80 ? 'Good' :
                         location.coverage_rate >= 50 ? 'Fair' :
                         'Poor'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      )}

      {/* Uncounted Items */}
      {uncounted_items.length > 0 && (
        <Card>
          <Card.Header>
            <h5>Items Requiring Attention (Not Recently Counted)</h5>
          </Card.Header>
          <Card.Body>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Item Number</th>
                  <th>Serial Number</th>
                  <th>Description</th>
                  <th>Location</th>
                  <th>Category</th>
                  <th>Last Counted</th>
                  <th>Priority</th>
                </tr>
              </thead>
              <tbody>
                {uncounted_items.map((item, index) => {
                  const daysSince = item.last_counted ? 
                    Math.ceil((new Date() - new Date(item.last_counted)) / (1000 * 60 * 60 * 24)) : 
                    999;
                  
                  return (
                    <tr key={index}>
                      <td>
                        <strong>{item.number}</strong>
                      </td>
                      <td>{item.serial_number}</td>
                      <td>
                        <small>{item.description}</small>
                      </td>
                      <td>{item.location}</td>
                      <td>
                        <span className="badge bg-secondary">
                          {item.category}
                        </span>
                      </td>
                      <td>
                        <div>
                          {formatDate(item.last_counted)}
                          <br />
                          <small className="text-muted">
                            {getDaysSinceLastCount(item.last_counted)}
                          </small>
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${
                          daysSince > 365 || !item.last_counted ? 'bg-danger' :
                          daysSince > 180 ? 'bg-warning' :
                          'bg-info'
                        }`}>
                          {daysSince > 365 || !item.last_counted ? 'High' :
                           daysSince > 180 ? 'Medium' :
                           'Low'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
            {uncounted_items.length >= 50 && (
              <Alert variant="info" className="mt-3">
                Showing first 50 items. Consider filtering by location or category for more specific results.
              </Alert>
            )}
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default CycleCountCoverageReport;
