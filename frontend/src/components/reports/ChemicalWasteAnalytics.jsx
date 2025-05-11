import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Form, Alert, Spinner, Row, Col, Table } from 'react-bootstrap';
import { fetchWasteAnalytics } from '../../store/chemicalsSlice';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ChemicalWasteAnalytics = () => {
  const dispatch = useDispatch();
  const { wasteAnalytics, wasteLoading, wasteError } = useSelector((state) => state.chemicals);
  const [timeframe, setTimeframe] = useState('month');

  useEffect(() => {
    dispatch(fetchWasteAnalytics(timeframe));
  }, [dispatch, timeframe]);

  const handleTimeframeChange = (e) => {
    setTimeframe(e.target.value);
  };

  // Prepare data for charts
  const prepareChartData = () => {
    if (!wasteAnalytics) return null;

    // Prepare data for category pie chart
    const categoryPieData = {
      labels: wasteAnalytics.waste_by_category.map(item => item.category),
      datasets: [
        {
          label: 'Total Archived',
          data: wasteAnalytics.waste_by_category.map(item => item.total),
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(199, 199, 199, 0.6)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(199, 199, 199, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };

    // Prepare data for reason pie chart
    const reasonPieData = {
      labels: ['Expired', 'Depleted', 'Other'],
      datasets: [
        {
          label: 'Archive Reasons',
          data: [
            wasteAnalytics.expired_count,
            wasteAnalytics.depleted_count,
            wasteAnalytics.other_count,
          ],
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };

    // Prepare data for time series chart
    const timeSeriesData = {
      labels: wasteAnalytics.waste_over_time.map(item => item.month),
      datasets: [
        {
          label: 'Expired',
          data: wasteAnalytics.waste_over_time.map(item => item.expired),
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1,
        },
        {
          label: 'Depleted',
          data: wasteAnalytics.waste_over_time.map(item => item.depleted),
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
        },
        {
          label: 'Other',
          data: wasteAnalytics.waste_over_time.map(item => item.other),
          backgroundColor: 'rgba(255, 206, 86, 0.6)',
          borderColor: 'rgba(255, 206, 86, 1)',
          borderWidth: 1,
        },
      ],
    };

    return {
      categoryPieData,
      reasonPieData,
      timeSeriesData,
    };
  };

  const chartData = wasteAnalytics ? prepareChartData() : null;

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <div className="d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Chemical Waste Analytics</h4>
          <Form.Select
            value={timeframe}
            onChange={handleTimeframeChange}
            style={{ width: 'auto' }}
            disabled={wasteLoading}
          >
            <option value="week">Last 7 Days</option>
            <option value="month">Last 30 Days</option>
            <option value="quarter">Last 90 Days</option>
            <option value="year">Last Year</option>
            <option value="all">All Time</option>
          </Form.Select>
        </div>
      </Card.Header>
      <Card.Body>
        {wasteError && <Alert variant="danger">{wasteError.message}</Alert>}

        {wasteLoading ? (
          <div className="text-center p-5">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
            <p className="mt-3">Loading waste analytics...</p>
          </div>
        ) : !wasteAnalytics ? (
          <Alert variant="info">No waste analytics data available.</Alert>
        ) : (
          <>
            <div className="mb-4">
              <h5>Summary</h5>
              <Row className="g-4 mb-4">
                <Col md={4}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{wasteAnalytics.total_archived}</h3>
                      <p className="mb-0">Total Archived Chemicals</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card className="text-center h-100 text-danger">
                    <Card.Body>
                      <h3>{wasteAnalytics.expired_count}</h3>
                      <p className="mb-0">Expired Chemicals</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card className="text-center h-100 text-primary">
                    <Card.Body>
                      <h3>{wasteAnalytics.depleted_count}</h3>
                      <p className="mb-0">Depleted Chemicals</p>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </div>

            {chartData && (
              <>
                <Row className="g-4 mb-4">
                  <Col md={6}>
                    <h5>Archive Reasons</h5>
                    <div style={{ height: '300px' }}>
                      <Pie
                        data={chartData.reasonPieData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'bottom',
                            },
                            title: {
                              display: true,
                              text: 'Chemicals by Archive Reason',
                            },
                          },
                        }}
                      />
                    </div>
                  </Col>
                  <Col md={6}>
                    <h5>Categories</h5>
                    <div style={{ height: '300px' }}>
                      <Pie
                        data={chartData.categoryPieData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'bottom',
                            },
                            title: {
                              display: true,
                              text: 'Chemicals by Category',
                            },
                          },
                        }}
                      />
                    </div>
                  </Col>
                </Row>

                <div className="mb-4">
                  <h5>Waste Over Time</h5>
                  <div style={{ height: '300px' }}>
                    <Bar
                      data={chartData.timeSeriesData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top',
                          },
                          title: {
                            display: true,
                            text: 'Chemical Waste Over Time',
                          },
                        },
                        scales: {
                          x: {
                            stacked: true,
                          },
                          y: {
                            stacked: true,
                          },
                        },
                      }}
                    />
                  </div>
                </div>
              </>
            )}

            <div className="mt-4">
              <h5>Waste by Category</h5>
              <div className="table-responsive">
                <Table hover bordered>
                  <thead className="bg-light">
                    <tr>
                      <th>Category</th>
                      <th>Total</th>
                      <th>Expired</th>
                      <th>Depleted</th>
                      <th>Other</th>
                    </tr>
                  </thead>
                  <tbody>
                    {wasteAnalytics.waste_by_category.map((category, index) => (
                      <tr key={index}>
                        <td>{category.category}</td>
                        <td>{category.total}</td>
                        <td>{category.expired}</td>
                        <td>{category.depleted}</td>
                        <td>{category.other}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </div>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default ChemicalWasteAnalytics;
