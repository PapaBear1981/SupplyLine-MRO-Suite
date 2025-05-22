import { Card, Table, Row, Col, Alert, Badge } from 'react-bootstrap';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

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

const CycleCountDiscrepancyReport = ({ data }) => {
  if (!data) {
    return (
      <Alert variant="info">
        No discrepancy data available for the selected time period.
      </Alert>
    );
  }

  const { discrepancies, summary, trends } = data;

  // Chart data for discrepancy trends
  const trendChartData = {
    labels: trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Discrepancies Found',
        data: trends.map(t => t.discrepancy_count),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
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
        text: 'Discrepancy Trends Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  // Chart data for discrepancy types
  const typeChartData = {
    labels: summary.by_type.map(t => t.type.charAt(0).toUpperCase() + t.type.slice(1)),
    datasets: [
      {
        data: summary.by_type.map(t => t.count),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(147, 51, 234, 0.8)',
        ],
        borderColor: [
          'rgb(239, 68, 68)',
          'rgb(251, 191, 36)',
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(147, 51, 234)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const typeChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: 'Discrepancies by Type',
      },
    },
  };

  const getDiscrepancyTypeColor = (type) => {
    switch (type) {
      case 'quantity': return 'danger';
      case 'location': return 'warning';
      case 'condition': return 'info';
      case 'missing': return 'dark';
      case 'extra': return 'success';
      default: return 'secondary';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString() + ' ' + 
           new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div>
      {/* Summary Cards */}
      <Row className="mb-4">
        <Col md={6}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-danger">{summary.total_discrepancies}</h3>
              <p className="mb-0">Total Discrepancies</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card className="text-center">
            <Card.Body>
              <h3 className="text-primary">{summary.by_type.length}</h3>
              <p className="mb-0">Discrepancy Types</p>
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
                <h5>Discrepancy Trends</h5>
              </Card.Header>
              <Card.Body>
                <Line data={trendChartData} options={trendChartOptions} />
              </Card.Body>
            </Card>
          </Col>
        )}
        
        {summary.by_type.length > 0 && (
          <Col md={4}>
            <Card>
              <Card.Header>
                <h5>Types Breakdown</h5>
              </Card.Header>
              <Card.Body>
                <Doughnut data={typeChartData} options={typeChartOptions} />
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {/* Discrepancy Details Table */}
      {discrepancies.length > 0 && (
        <Card>
          <Card.Header>
            <h5>Discrepancy Details</h5>
          </Card.Header>
          <Card.Body>
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Type</th>
                  <th>Expected</th>
                  <th>Actual</th>
                  <th>Location</th>
                  <th>Counted By</th>
                  <th>Date</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {discrepancies.slice(0, 50).map((discrepancy, index) => (
                  <tr key={index}>
                    <td>
                      <div>
                        <strong>{discrepancy.item_details.number || 'N/A'}</strong>
                        <br />
                        <small className="text-muted">
                          {discrepancy.item_details.description || 'No description'}
                        </small>
                      </div>
                    </td>
                    <td>
                      <Badge bg={getDiscrepancyTypeColor(discrepancy.discrepancy_type)}>
                        {discrepancy.discrepancy_type?.charAt(0).toUpperCase() + 
                         discrepancy.discrepancy_type?.slice(1) || 'Unknown'}
                      </Badge>
                    </td>
                    <td>
                      <div>
                        <div>Qty: {discrepancy.expected_quantity || 'N/A'}</div>
                        <small className="text-muted">
                          Loc: {discrepancy.expected_location || 'N/A'}
                        </small>
                      </div>
                    </td>
                    <td>
                      <div>
                        <div>Qty: {discrepancy.actual_quantity || 'N/A'}</div>
                        <small className="text-muted">
                          Loc: {discrepancy.actual_location || 'N/A'}
                        </small>
                      </div>
                    </td>
                    <td>{discrepancy.expected_location || 'Unknown'}</td>
                    <td>{discrepancy.counted_by}</td>
                    <td>
                      <small>{formatDate(discrepancy.counted_at)}</small>
                    </td>
                    <td>
                      <small>
                        {discrepancy.discrepancy_notes || discrepancy.notes || 'No notes'}
                      </small>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
            {discrepancies.length > 50 && (
              <Alert variant="info" className="mt-3">
                Showing first 50 discrepancies. Total: {discrepancies.length}
              </Alert>
            )}
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default CycleCountDiscrepancyReport;
