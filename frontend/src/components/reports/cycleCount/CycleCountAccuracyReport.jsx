import { Card, Table, Row, Col, Alert } from 'react-bootstrap';
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

const CycleCountAccuracyReport = ({ data }) => {
  if (!data) {
    return (
      <Alert variant="info">
        No accuracy data available for the selected time period.
      </Alert>
    );
  }

  const {
    summary = { total_counts: 0, accurate_counts: 0, discrepancy_counts: 0, accuracy_rate: 0 },
    by_location = [],
    trends = [],
  } = data ?? {};

  // Chart data for accuracy trends
  const trendChartData = {
    labels: trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Accuracy Rate (%)',
        data: trends.map(t => t.accuracy_rate),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
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
        text: 'Accuracy Rate Trends Over Time',
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

  // Chart data for location accuracy
  const locationChartData = {
    labels: by_location.map(l => l.location),
    datasets: [
      {
        label: 'Accuracy Rate (%)',
        data: by_location.map(l => l.accuracy_rate),
        backgroundColor: by_location.map(l =>
          l.accuracy_rate >= 95 ? 'rgba(34, 197, 94, 0.8)' :
          l.accuracy_rate >= 85 ? 'rgba(251, 191, 36, 0.8)' :
          'rgba(239, 68, 68, 0.8)'
        ),
        borderColor: by_location.map(l =>
          l.accuracy_rate >= 95 ? 'rgb(34, 197, 94)' :
          l.accuracy_rate >= 85 ? 'rgb(251, 191, 36)' :
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
        text: 'Accuracy Rate by Location',
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

  return (
    <div>
      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-primary">{summary.total_counts}</h3>
              <p className="mb-0">Total Counts</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-success">{summary.accurate_counts}</h3>
              <p className="mb-0">Accurate Counts</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-warning">{summary.discrepancy_counts}</h3>
              <p className="mb-0">Discrepancies</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h3 className={`${summary.accuracy_rate >= 95 ? 'text-success' : summary.accuracy_rate >= 85 ? 'text-warning' : 'text-danger'}`}>
                {summary.accuracy_rate}%
              </h3>
              <p className="mb-0">Overall Accuracy</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      {trends.length > 0 && (
        <Card className="mb-4">
          <Card.Header>
            <h5>Accuracy Trends</h5>
          </Card.Header>
          <Card.Body>
            <Line data={trendChartData} options={trendChartOptions} />
          </Card.Body>
        </Card>
      )}

      {by_location.length > 0 && (
        <Card className="mb-4">
          <Card.Header>
            <h5>Accuracy by Location</h5>
          </Card.Header>
          <Card.Body>
            <Bar data={locationChartData} options={locationChartOptions} />
          </Card.Body>
        </Card>
      )}

      {/* Location Details Table */}
      {by_location.length > 0 && (
        <Card>
          <Card.Header>
            <h5>Location Accuracy Details</h5>
          </Card.Header>
          <Card.Body>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Location</th>
                  <th>Total Counts</th>
                  <th>Accurate Counts</th>
                  <th>Accuracy Rate</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {by_location.map((location) => (
                  <tr key={location.location || Math.random()}>
                    <td>{location.location}</td>
                    <td>{location.total_counts}</td>
                    <td>{location.accurate_counts}</td>
                    <td>{location.accuracy_rate}%</td>
                    <td>
                      <span className={`badge ${
                        location.accuracy_rate >= 95 ? 'bg-success' :
                        location.accuracy_rate >= 85 ? 'bg-warning' :
                        'bg-danger'
                      }`}>
                        {location.accuracy_rate >= 95 ? 'Excellent' :
                         location.accuracy_rate >= 85 ? 'Good' :
                         'Needs Improvement'}
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

export default CycleCountAccuracyReport;
