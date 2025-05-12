import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Form, Alert, Spinner, Row, Col, Table, Button } from 'react-bootstrap';
import { fetchUniquePartNumbers, fetchUsageAnalytics } from '../../store/chemicalsSlice';
import { Bar, Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const ChemicalUsageAnalytics = () => {
  const dispatch = useDispatch();
  const {
    uniquePartNumbers,
    usageAnalytics: usageData,
    usageLoading,
    usageError
  } = useSelector((state) => state.chemicals);

  const [selectedPartNumber, setSelectedPartNumber] = useState('');
  const [timeframe, setTimeframe] = useState('month');

  // Fetch unique part numbers on component mount
  useEffect(() => {
    dispatch(fetchUniquePartNumbers());
  }, [dispatch]);

  // Fetch usage data when part number or timeframe changes
  useEffect(() => {
    if (selectedPartNumber) {
      dispatch(fetchUsageAnalytics({ part_number: selectedPartNumber, timeframe }));
    }
  }, [dispatch, selectedPartNumber, timeframe]);

  // Prepare chart data
  const prepareChartData = () => {
    if (!usageData) return null;

    // Prepare data for location bar chart
    const locationChartData = {
      labels: usageData.usage_stats.by_location.map(item => item.location),
      datasets: [
        {
          label: 'Quantity Used',
          data: usageData.usage_stats.by_location.map(item => item.quantity),
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
        },
      ],
    };

    // Prepare data for user bar chart
    const userChartData = {
      labels: usageData.usage_stats.by_user.map(item => item.user),
      datasets: [
        {
          label: 'Quantity Used',
          data: usageData.usage_stats.by_user.map(item => item.quantity),
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
      ],
    };

    // Prepare data for usage over time line chart
    const timeChartData = {
      labels: usageData.usage_stats.over_time.map(item => item.month),
      datasets: [
        {
          label: 'Usage Over Time',
          data: usageData.usage_stats.over_time.map(item => item.quantity),
          fill: false,
          backgroundColor: 'rgba(153, 102, 255, 0.6)',
          borderColor: 'rgba(153, 102, 255, 1)',
          tension: 0.1,
        },
      ],
    };

    // Prepare data for inventory status pie chart
    const inventoryPieData = {
      labels: ['Current Inventory', 'Total Issued'],
      datasets: [
        {
          data: [usageData.inventory_stats.current_inventory, usageData.usage_stats.total_issued],
          backgroundColor: [
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 99, 132, 0.6)',
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };

    return {
      locationChartData,
      userChartData,
      timeChartData,
      inventoryPieData
    };
  };

  const chartData = usageData ? prepareChartData() : null;

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-light">
        <h4 className="mb-0">Chemical Usage Analytics</h4>
      </Card.Header>
      <Card.Body>
        <Row className="mb-4">
          <Col md={6}>
            <Form.Group>
              <Form.Label>Part Number</Form.Label>
              <Form.Select
                value={selectedPartNumber}
                onChange={(e) => setSelectedPartNumber(e.target.value)}
              >
                <option value="">Select a part number</option>
                {uniquePartNumbers.map((part) => (
                  <option key={part} value={part}>
                    {part}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group>
              <Form.Label>Timeframe</Form.Label>
              <Form.Select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
              >
                <option value="week">Last Week</option>
                <option value="month">Last Month</option>
                <option value="quarter">Last Quarter</option>
                <option value="year">Last Year</option>
                <option value="all">All Time</option>
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>

        {usageError && <Alert variant="danger">{usageError}</Alert>}

        {!selectedPartNumber ? (
          <Alert variant="info">Please select a part number to view usage analytics.</Alert>
        ) : usageLoading ? (
          <div className="text-center p-5">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
            <p className="mt-3">Loading usage analytics...</p>
          </div>
        ) : !usageData ? (
          <Alert variant="info">No usage analytics data available for the selected part number.</Alert>
        ) : (
          <>
            <div className="mb-4">
              <h5>Summary</h5>
              <Row className="g-4 mb-4">
                <Col md={3}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{usageData.inventory_stats.total_count}</h3>
                      <p className="mb-0">Total Items</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{usageData.inventory_stats.active_count}</h3>
                      <p className="mb-0">Active Items</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{usageData.inventory_stats.current_inventory.toFixed(2)}</h3>
                      <p className="mb-0">Current Inventory</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{usageData.usage_stats.total_issued.toFixed(2)}</h3>
                      <p className="mb-0">Total Issued</p>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              <Row className="g-4 mb-4">
                <Col md={4}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{usageData.usage_stats.avg_monthly_usage.toFixed(2)}</h3>
                      <p className="mb-0">Avg. Monthly Usage</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={8}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>
                        {usageData.usage_stats.projected_depletion_days
                          ? `${usageData.usage_stats.projected_depletion_days} days`
                          : 'N/A'}
                      </h3>
                      <p className="mb-0">Projected Depletion Time</p>
                      {usageData.usage_stats.projected_depletion_days && (
                        <small className="text-muted">
                          Estimated depletion date: {
                            new Date(Date.now() + (usageData.usage_stats.projected_depletion_days * 24 * 60 * 60 * 1000))
                              .toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
                          }
                        </small>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </div>

            {chartData && (
              <>
                <Row className="g-4 mb-4">
                  <Col md={6}>
                    <h5>Usage by Location</h5>
                    <div style={{ height: '300px' }}>
                      <Bar
                        data={chartData.locationChartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: false,
                            },
                            title: {
                              display: true,
                              text: 'Chemical Usage by Location',
                            },
                          },
                        }}
                      />
                    </div>
                  </Col>
                  <Col md={6}>
                    <h5>Inventory Status</h5>
                    <div style={{ height: '300px' }}>
                      <Pie
                        data={chartData.inventoryPieData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'bottom',
                            },
                            title: {
                              display: true,
                              text: 'Inventory vs. Usage',
                            },
                          },
                        }}
                      />
                    </div>
                  </Col>
                </Row>

                <Row className="g-4 mb-4">
                  <Col md={12}>
                    <h5>Usage Over Time</h5>
                    <div style={{ height: '300px' }}>
                      <Line
                        data={chartData.timeChartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: false,
                            },
                            title: {
                              display: true,
                              text: 'Chemical Usage Over Time',
                            },
                          },
                        }}
                      />
                    </div>
                  </Col>
                </Row>

                <Row className="g-4 mb-4">
                  <Col md={12}>
                    <h5>Usage by User</h5>
                    <div style={{ height: '300px' }}>
                      <Bar
                        data={chartData.userChartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: false,
                            },
                            title: {
                              display: true,
                              text: 'Chemical Usage by User',
                            },
                          },
                        }}
                      />
                    </div>
                  </Col>
                </Row>

                {usageData.efficiency_stats && usageData.efficiency_stats.usage_efficiency_data && usageData.efficiency_stats.usage_efficiency_data.length > 0 && (
                  <div className="mt-4">
                    <h5>Usage Efficiency Data</h5>
                    <div className="table-responsive">
                      <Table hover bordered>
                        <thead className="bg-light">
                          <tr>
                            <th>Lot Number</th>
                            <th>Original Quantity</th>
                            <th>Total Issued</th>
                            <th>Days to Deplete</th>
                            <th>Daily Usage Rate</th>
                          </tr>
                        </thead>
                        <tbody>
                          {usageData.efficiency_stats.usage_efficiency_data.map((item, index) => (
                            <tr key={index}>
                              <td>{item.lot_number}</td>
                              <td>{item.original_quantity.toFixed(2)}</td>
                              <td>{item.total_issued.toFixed(2)}</td>
                              <td>{item.days_to_deplete || 'N/A'}</td>
                              <td>{item.daily_usage_rate.toFixed(4)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default ChemicalUsageAnalytics;
