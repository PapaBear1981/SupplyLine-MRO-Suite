import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Form, Alert, Spinner, Row, Col, Table, Button } from 'react-bootstrap';
import { fetchWasteAnalytics, fetchUniquePartNumbers } from '../../store/chemicalsSlice';
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

const ChemicalWasteAnalytics = () => {
  const dispatch = useDispatch();
  const {
    wasteAnalytics,
    wasteLoading,
    wasteError,
    uniquePartNumbers,
    uniquePartNumbersLoading,
    uniquePartNumbersError
  } = useSelector((state) => state.chemicals);

  const [timeframe, setTimeframe] = useState('month');
  const [selectedPartNumber, setSelectedPartNumber] = useState('');
  const [showPartNumberFilter, setShowPartNumberFilter] = useState(false);

  useEffect(() => {
    // Fetch unique part numbers for filtering
    dispatch(fetchUniquePartNumbers());
  }, [dispatch]);

  useEffect(() => {
    // Fetch waste analytics with optional part number filter
    const params = {
      timeframe: timeframe,
      part_number: selectedPartNumber || null
    };
    dispatch(fetchWasteAnalytics(params));
  }, [dispatch, timeframe, selectedPartNumber]);

  const handleTimeframeChange = (e) => {
    setTimeframe(e.target.value);
  };

  const handlePartNumberChange = (e) => {
    setSelectedPartNumber(e.target.value);
  };

  const handleClearFilter = () => {
    setSelectedPartNumber('');
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

    // Prepare data for location pie chart if available
    let locationPieData = null;
    if (wasteAnalytics.waste_by_location && wasteAnalytics.waste_by_location.length > 0) {
      locationPieData = {
        labels: wasteAnalytics.waste_by_location.map(item => item.location),
        datasets: [
          {
            label: 'Total Archived by Location',
            data: wasteAnalytics.waste_by_location.map(item => item.total),
            backgroundColor: [
              'rgba(75, 192, 192, 0.6)',
              'rgba(153, 102, 255, 0.6)',
              'rgba(255, 159, 64, 0.6)',
              'rgba(255, 99, 132, 0.6)',
              'rgba(54, 162, 235, 0.6)',
              'rgba(255, 206, 86, 0.6)',
              'rgba(199, 199, 199, 0.6)',
            ],
            borderColor: [
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(255, 159, 64, 1)',
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(199, 199, 199, 1)',
            ],
            borderWidth: 1,
          },
        ],
      };
    }

    // Prepare data for part number chart if available and not filtered
    let partNumberChartData = null;
    if (!selectedPartNumber && wasteAnalytics.waste_by_part_number && wasteAnalytics.waste_by_part_number.length > 0) {
      // Limit to top 10 part numbers by total count
      const topPartNumbers = [...wasteAnalytics.waste_by_part_number]
        .sort((a, b) => b.total - a.total)
        .slice(0, 10);

      partNumberChartData = {
        labels: topPartNumbers.map(item => item.part_number),
        datasets: [
          {
            label: 'Expired',
            data: topPartNumbers.map(item => item.expired),
            backgroundColor: 'rgba(255, 99, 132, 0.6)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
          },
          {
            label: 'Depleted',
            data: topPartNumbers.map(item => item.depleted),
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
          },
          {
            label: 'Other',
            data: topPartNumbers.map(item => item.other),
            backgroundColor: 'rgba(255, 206, 86, 0.6)',
            borderColor: 'rgba(255, 206, 86, 1)',
            borderWidth: 1,
          },
        ],
      };
    }

    return {
      categoryPieData,
      reasonPieData,
      timeSeriesData,
      locationPieData,
      partNumberChartData
    };
  };

  const chartData = wasteAnalytics ? prepareChartData() : null;

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <div className="d-flex justify-content-between align-items-center mb-2">
          <h4 className="mb-0">Chemical Waste Analytics</h4>
          <div className="d-flex gap-2">
            <Button
              variant="outline-secondary"
              size="sm"
              onClick={() => setShowPartNumberFilter(!showPartNumberFilter)}
            >
              {showPartNumberFilter ? 'Hide Filters' : 'Show Filters'}
            </Button>
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
        </div>

        {showPartNumberFilter && (
          <div className="mt-3 d-flex gap-2 align-items-center">
            <Form.Group className="flex-grow-1">
              <Form.Label>Filter by Part Number</Form.Label>
              <Form.Select
                value={selectedPartNumber}
                onChange={handlePartNumberChange}
                disabled={uniquePartNumbersLoading || wasteLoading}
              >
                <option value="">All Part Numbers</option>
                {uniquePartNumbers.map(partNumber => (
                  <option key={partNumber} value={partNumber}>{partNumber}</option>
                ))}
              </Form.Select>
            </Form.Group>
            {selectedPartNumber && (
              <Button
                variant="outline-secondary"
                onClick={handleClearFilter}
                className="mt-4"
              >
                Clear Filter
              </Button>
            )}
          </div>
        )}

        {selectedPartNumber && (
          <Alert variant="info" className="mt-2 mb-0">
            Showing waste analytics for part number: <strong>{selectedPartNumber}</strong>
          </Alert>
        )}
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

                <Row className="g-4 mb-4">
                  {chartData.locationPieData && (
                    <Col md={6}>
                      <h5>Locations</h5>
                      <div style={{ height: '300px' }}>
                        <Pie
                          data={chartData.locationPieData}
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: {
                                position: 'bottom',
                              },
                              title: {
                                display: true,
                                text: 'Chemicals by Location',
                              },
                            },
                          }}
                        />
                      </div>
                    </Col>
                  )}

                  {chartData.partNumberChartData && (
                    <Col md={chartData.locationPieData ? 6 : 12}>
                      <h5>Top Part Numbers</h5>
                      <div style={{ height: '300px' }}>
                        <Bar
                          data={chartData.partNumberChartData}
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: {
                                position: 'top',
                              },
                              title: {
                                display: true,
                                text: 'Top 10 Part Numbers by Waste',
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
                    </Col>
                  )}
                </Row>

                <Row className="g-4 mb-4">
                  <Col md={6}>
                    <h5>Waste Over Time (Stacked)</h5>
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
                  </Col>
                  <Col md={6}>
                    <h5>Waste Trends</h5>
                    <div style={{ height: '300px' }}>
                      <Line
                        data={{
                          labels: chartData.timeSeriesData.labels,
                          datasets: [
                            {
                              label: 'Expired',
                              data: chartData.timeSeriesData.datasets[0].data,
                              fill: false,
                              borderColor: 'rgba(255, 99, 132, 1)',
                              tension: 0.1,
                              pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                            },
                            {
                              label: 'Depleted',
                              data: chartData.timeSeriesData.datasets[1].data,
                              fill: false,
                              borderColor: 'rgba(54, 162, 235, 1)',
                              tension: 0.1,
                              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                            },
                            {
                              label: 'Other',
                              data: chartData.timeSeriesData.datasets[2].data,
                              fill: false,
                              borderColor: 'rgba(255, 206, 86, 1)',
                              tension: 0.1,
                              pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                            },
                          ],
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'top',
                            },
                            title: {
                              display: true,
                              text: 'Chemical Waste Trends',
                            },
                          },
                        }}
                      />
                    </div>
                  </Col>
                </Row>
              </>
            )}

            <div className="mt-4">
              <Row>
                <Col md={6}>
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
                </Col>
                <Col md={6}>
                  <h5>Waste by Location</h5>
                  <div className="table-responsive">
                    <Table hover bordered>
                      <thead className="bg-light">
                        <tr>
                          <th>Location</th>
                          <th>Total</th>
                          <th>Expired</th>
                          <th>Depleted</th>
                          <th>Other</th>
                        </tr>
                      </thead>
                      <tbody>
                        {wasteAnalytics.waste_by_location.map((location, index) => (
                          <tr key={index}>
                            <td>{location.location}</td>
                            <td>{location.total}</td>
                            <td>{location.expired}</td>
                            <td>{location.depleted}</td>
                            <td>{location.other}</td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                </Col>
              </Row>
            </div>

            {!selectedPartNumber && wasteAnalytics.waste_by_part_number && wasteAnalytics.waste_by_part_number.length > 0 && (
              <div className="mt-4">
                <h5>Waste by Part Number</h5>
                <div className="table-responsive">
                  <Table hover bordered>
                    <thead className="bg-light">
                      <tr>
                        <th>Part Number</th>
                        <th>Total</th>
                        <th>Expired</th>
                        <th>Depleted</th>
                        <th>Other</th>
                      </tr>
                    </thead>
                    <tbody>
                      {wasteAnalytics.waste_by_part_number.map((part, index) => (
                        <tr key={index}>
                          <td>{part.part_number}</td>
                          <td>{part.total}</td>
                          <td>{part.expired}</td>
                          <td>{part.depleted}</td>
                          <td>{part.other}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </div>
            )}

            {wasteAnalytics.shelf_life_analytics && wasteAnalytics.shelf_life_analytics.averages_by_part_number && wasteAnalytics.shelf_life_analytics.averages_by_part_number.length > 0 && (
              <div className="mt-4">
                <h5>Shelf Life Analytics by Part Number</h5>
                <div className="table-responsive">
                  <Table hover bordered>
                    <thead className="bg-light">
                      <tr>
                        <th>Part Number</th>
                        <th>Items</th>
                        <th>Avg. Shelf Life (days)</th>
                        <th>Avg. Used Life (days)</th>
                        <th>Avg. Usage %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {wasteAnalytics.shelf_life_analytics.averages_by_part_number.map((part, index) => (
                        <tr key={index}>
                          <td>{part.part_number}</td>
                          <td>{part.total_items}</td>
                          <td>{part.avg_shelf_life}</td>
                          <td>{part.avg_used_life}</td>
                          <td>{part.avg_usage_percentage}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </div>
            )}
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default ChemicalWasteAnalytics;
