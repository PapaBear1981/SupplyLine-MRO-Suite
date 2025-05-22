import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Tabs, Tab, Form, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import {
  fetchCycleCountAccuracyReport,
  fetchCycleCountDiscrepancyReport,
  fetchCycleCountPerformanceReport,
  fetchCycleCountCoverageReport
} from '../../store/reportSlice';
import CycleCountAccuracyReport from './cycleCount/CycleCountAccuracyReport';
import CycleCountDiscrepancyReport from './cycleCount/CycleCountDiscrepancyReport';
import CycleCountPerformanceReport from './cycleCount/CycleCountPerformanceReport';
import CycleCountCoverageReport from './cycleCount/CycleCountCoverageReport';

const CycleCountReports = () => {
  const dispatch = useDispatch();
  const { cycleCountReports } = useSelector((state) => state.reports);
  
  const [activeTab, setActiveTab] = useState('accuracy');
  const [timeframe, setTimeframe] = useState('month');
  const [location, setLocation] = useState('');
  const [category, setCategory] = useState('');
  const [discrepancyType, setDiscrepancyType] = useState('');
  const [days, setDays] = useState(90);
  
  useEffect(() => {
    // Load initial data for the active tab
    loadReportData();
  }, [activeTab]); // eslint-disable-line react-hooks/exhaustive-deps
  
  const loadReportData = () => {
    switch (activeTab) {
      case 'accuracy':
        dispatch(fetchCycleCountAccuracyReport({ timeframe, location, category }));
        break;
      case 'discrepancy':
        dispatch(fetchCycleCountDiscrepancyReport({ timeframe, type: discrepancyType, location, category }));
        break;
      case 'performance':
        dispatch(fetchCycleCountPerformanceReport({ timeframe }));
        break;
      case 'coverage':
        dispatch(fetchCycleCountCoverageReport({ days, location, category }));
        break;
      default:
        break;
    }
  };
  
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };
  
  const handleFilterSubmit = (e) => {
    e.preventDefault();
    loadReportData();
  };
  
  const renderFilters = () => {
    switch (activeTab) {
      case 'accuracy':
      case 'discrepancy':
        return (
          <Form onSubmit={handleFilterSubmit}>
            <Row className="mb-3">
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Timeframe</Form.Label>
                  <Form.Select
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                  >
                    <option value="week">Last 7 Days</option>
                    <option value="month">Last 30 Days</option>
                    <option value="quarter">Last 90 Days</option>
                    <option value="year">Last 365 Days</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Location</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Filter by location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Category</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Filter by category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  />
                </Form.Group>
              </Col>
              {activeTab === 'discrepancy' && (
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Discrepancy Type</Form.Label>
                    <Form.Select
                      value={discrepancyType}
                      onChange={(e) => setDiscrepancyType(e.target.value)}
                    >
                      <option value="">All Types</option>
                      <option value="quantity">Quantity</option>
                      <option value="location">Location</option>
                      <option value="condition">Condition</option>
                      <option value="missing">Missing</option>
                      <option value="extra">Extra</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              )}
              <Col md={activeTab === 'discrepancy' ? 12 : 3} className="d-flex align-items-end">
                <Button type="submit" variant="primary" className="mt-3">
                  Apply Filters
                </Button>
              </Col>
            </Row>
          </Form>
        );
      case 'performance':
        return (
          <Form onSubmit={handleFilterSubmit}>
            <Row className="mb-3">
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Timeframe</Form.Label>
                  <Form.Select
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                  >
                    <option value="week">Last 7 Days</option>
                    <option value="month">Last 30 Days</option>
                    <option value="quarter">Last 90 Days</option>
                    <option value="year">Last 365 Days</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4} className="d-flex align-items-end">
                <Button type="submit" variant="primary" className="mt-3">
                  Apply Filters
                </Button>
              </Col>
            </Row>
          </Form>
        );
      case 'coverage':
        return (
          <Form onSubmit={handleFilterSubmit}>
            <Row className="mb-3">
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Days Threshold</Form.Label>
                  <Form.Control
                    type="number"
                    min="1"
                    max="365"
                    value={days}
                    onChange={(e) => setDays(parseInt(e.target.value))}
                  />
                  <Form.Text className="text-muted">
                    Items not counted in this many days
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Location</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Filter by location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </Form.Group>
              </Col>
              <Col md={3}>
                <Form.Group>
                  <Form.Label>Category</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Filter by category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  />
                </Form.Group>
              </Col>
              <Col md={3} className="d-flex align-items-end">
                <Button type="submit" variant="primary" className="mt-3">
                  Apply Filters
                </Button>
              </Col>
            </Row>
          </Form>
        );
      default:
        return null;
    }
  };
  
  const renderReportContent = () => {
    switch (activeTab) {
      case 'accuracy':
        return (
          <CycleCountAccuracyReport
            data={cycleCountReports.accuracy.data}
            loading={cycleCountReports.accuracy.loading}
            error={cycleCountReports.accuracy.error}
          />
        );
      case 'discrepancy':
        return (
          <CycleCountDiscrepancyReport
            data={cycleCountReports.discrepancy.data}
            loading={cycleCountReports.discrepancy.loading}
            error={cycleCountReports.discrepancy.error}
          />
        );
      case 'performance':
        return (
          <CycleCountPerformanceReport
            data={cycleCountReports.performance.data}
            loading={cycleCountReports.performance.loading}
            error={cycleCountReports.performance.error}
          />
        );
      case 'coverage':
        return (
          <CycleCountCoverageReport
            data={cycleCountReports.coverage.data}
            loading={cycleCountReports.coverage.loading}
            error={cycleCountReports.coverage.error}
          />
        );
      default:
        return (
          <Alert variant="info">
            Select a report type to view cycle count reports.
          </Alert>
        );
    }
  };
  
  return (
    <Card>
      <Card.Header>
        <h5 className="mb-0">Cycle Count Reports</h5>
      </Card.Header>
      <Card.Body>
        <Tabs
          activeKey={activeTab}
          onSelect={handleTabChange}
          className="mb-4"
        >
          <Tab eventKey="accuracy" title="Inventory Accuracy">
            <div className="py-3">
              <p className="text-muted">
                This report shows inventory accuracy metrics based on cycle count results.
                It includes overall accuracy rate, accuracy by location, category, and trends over time.
              </p>
            </div>
          </Tab>
          <Tab eventKey="discrepancy" title="Discrepancies">
            <div className="py-3">
              <p className="text-muted">
                This report shows details about discrepancies found during cycle counts.
                It includes discrepancy types, locations, categories, and trends over time.
              </p>
            </div>
          </Tab>
          <Tab eventKey="performance" title="Performance">
            <div className="py-3">
              <p className="text-muted">
                This report shows cycle count performance metrics.
                It includes completion rates, average time to complete, counts by user, and counts over time.
              </p>
            </div>
          </Tab>
          <Tab eventKey="coverage" title="Coverage">
            <div className="py-3">
              <p className="text-muted">
                This report shows inventory coverage metrics based on cycle counts.
                It includes overall coverage, coverage by location and category, and items not counted recently.
              </p>
            </div>
          </Tab>
        </Tabs>
        
        {renderFilters()}
        
        <div className="mt-4">
          {renderReportContent()}
        </div>
      </Card.Body>
    </Card>
  );
};

export default CycleCountReports;
