import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Form, Alert, Spinner, Row, Col, Table } from 'react-bootstrap';
import { fetchUniquePartNumbers, fetchPartNumberAnalytics } from '../../store/chemicalsSlice';
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

const PartNumberAnalytics = () => {
  const dispatch = useDispatch();
  const { 
    uniquePartNumbers, 
    uniquePartNumbersLoading, 
    uniquePartNumbersError,
    partNumberAnalytics,
    partNumberLoading,
    partNumberError
  } = useSelector((state) => state.chemicals);
  
  const [selectedPartNumber, setSelectedPartNumber] = useState('');

  useEffect(() => {
    dispatch(fetchUniquePartNumbers());
  }, [dispatch]);

  useEffect(() => {
    if (selectedPartNumber) {
      dispatch(fetchPartNumberAnalytics(selectedPartNumber));
    }
  }, [dispatch, selectedPartNumber]);

  const handlePartNumberChange = (e) => {
    setSelectedPartNumber(e.target.value);
  };

  const prepareChartData = () => {
    if (!partNumberAnalytics) return null;

    // Usage by location chart data
    const locationLabels = partNumberAnalytics.usage_stats.by_location.map(item => item.location);
    const locationData = partNumberAnalytics.usage_stats.by_location.map(item => item.quantity);
    
    const locationChartData = {
      labels: locationLabels,
      datasets: [
        {
          label: 'Usage by Location',
          data: locationData,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }
      ]
    };

    // Usage over time chart data
    const timeLabels = partNumberAnalytics.usage_stats.over_time.map(item => item.month);
    const timeData = partNumberAnalytics.usage_stats.over_time.map(item => item.quantity);
    
    const timeChartData = {
      labels: timeLabels,
      datasets: [
        {
          label: 'Usage Over Time',
          data: timeData,
          fill: false,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          tension: 0.1
        }
      ]
    };

    // Waste statistics pie chart
    const wasteLabels = ['Expired', 'Depleted', 'Other'];
    const wasteData = [
      partNumberAnalytics.waste_stats.expired_count,
      partNumberAnalytics.waste_stats.depleted_count,
      partNumberAnalytics.waste_stats.other_archived_count
    ];
    
    const wastePieData = {
      labels: wasteLabels,
      datasets: [
        {
          data: wasteData,
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)'
          ],
          borderWidth: 1
        }
      ]
    };

    return {
      locationChartData,
      timeChartData,
      wastePieData
    };
  };

  const chartData = partNumberAnalytics ? prepareChartData() : null;

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-light">
        <div className="d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Part Number Analytics</h4>
          <Form.Select
            value={selectedPartNumber}
            onChange={handlePartNumberChange}
            style={{ width: 'auto' }}
            disabled={uniquePartNumbersLoading}
          >
            <option value="">Select a Part Number</option>
            {uniquePartNumbers.map(partNumber => (
              <option key={partNumber} value={partNumber}>{partNumber}</option>
            ))}
          </Form.Select>
        </div>
      </Card.Header>
      <Card.Body>
        {uniquePartNumbersError && (
          <Alert variant="danger">{uniquePartNumbersError.message}</Alert>
        )}
        
        {uniquePartNumbersLoading ? (
          <div className="text-center p-5">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading part numbers...</span>
            </Spinner>
            <p className="mt-3">Loading part numbers...</p>
          </div>
        ) : !selectedPartNumber ? (
          <Alert variant="info">Please select a part number to view analytics.</Alert>
        ) : partNumberError ? (
          <Alert variant="danger">{partNumberError.message}</Alert>
        ) : partNumberLoading ? (
          <div className="text-center p-5">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading analytics...</span>
            </Spinner>
            <p className="mt-3">Loading analytics for {selectedPartNumber}...</p>
          </div>
        ) : !partNumberAnalytics ? (
          <Alert variant="info">No analytics data available for {selectedPartNumber}.</Alert>
        ) : (
          <>
            <div className="mb-4">
              <h5>Summary for Part Number: {partNumberAnalytics.part_number}</h5>
              <Row className="g-4 mb-4">
                <Col md={3}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{partNumberAnalytics.inventory_stats.current_inventory}</h3>
                      <p className="mb-0">Current Inventory</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{partNumberAnalytics.usage_stats.total_issued}</h3>
                      <p className="mb-0">Total Issued</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center h-100 text-danger">
                    <Card.Body>
                      <h3>{partNumberAnalytics.waste_stats.expired_count}</h3>
                      <p className="mb-0">Expired Items</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center h-100 text-warning">
                    <Card.Body>
                      <h3>{partNumberAnalytics.waste_stats.waste_percentage}%</h3>
                      <p className="mb-0">Waste Percentage</p>
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
                    <h5>Waste Distribution</h5>
                    <div style={{ height: '300px' }}>
                      <Pie
                        data={chartData.wastePieData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'bottom',
                            },
                            title: {
                              display: true,
                              text: 'Waste Distribution',
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
              </>
            )}

            <div className="mt-4">
              <h5>Shelf Life Analytics</h5>
              <Row className="g-4 mb-4">
                <Col md={4}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{partNumberAnalytics.shelf_life_stats.avg_shelf_life_days} days</h3>
                      <p className="mb-0">Average Shelf Life</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{partNumberAnalytics.shelf_life_stats.avg_used_life_days} days</h3>
                      <p className="mb-0">Average Used Life</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card className="text-center h-100">
                    <Card.Body>
                      <h3>{partNumberAnalytics.shelf_life_stats.avg_usage_percentage}%</h3>
                      <p className="mb-0">Average Usage Percentage</p>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </div>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default PartNumberAnalytics;
