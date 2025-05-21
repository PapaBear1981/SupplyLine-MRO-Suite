import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Card, Row, Col, Nav, Tab, Alert, Button } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import CalibrationDueList from '../components/calibration/CalibrationDueList';
import CalibrationOverdueList from '../components/calibration/CalibrationOverdueList';
import CalibrationHistoryList from '../components/calibration/CalibrationHistoryList';
import CalibrationStandardsList from '../components/calibration/CalibrationStandardsList';

const CalibrationManagement = () => {
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const tabParam = queryParams.get('tab');
  const [activeTab, setActiveTab] = useState(tabParam || 'due');

  // Update active tab when URL query parameter changes
  useEffect(() => {
    if (tabParam && ['due', 'overdue', 'history', 'standards'].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  if (!isAdmin) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Access Denied</Alert.Heading>
        <p>
          You do not have permission to access the calibration management page.
          This feature is only available to administrators and Materials department personnel.
        </p>
      </Alert>
    );
  }

  return (
    <div className="w-100">
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">Calibration Management</h1>
        <div>
          <Button
            as={Link}
            to="/calibration-standards/new"
            variant="outline-primary"
            className="me-2"
          >
            <i className="bi bi-plus-circle me-2"></i>
            Add Calibration Standard
          </Button>
        </div>
      </div>

      <Tab.Container id="calibration-tabs" activeKey={activeTab} onSelect={setActiveTab}>
        <Row>
          <Col md={3} lg={2} className="mb-4">
            <Card>
              <Card.Header>
                <h5 className="mb-0">Navigation</h5>
              </Card.Header>
              <Card.Body className="p-0">
                <Nav variant="pills" className="flex-column">
                  <Nav.Item>
                    <Nav.Link eventKey="due" className="rounded-0">
                      <i className="bi bi-calendar-check me-2"></i>
                      Due Soon
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="overdue" className="rounded-0">
                      <i className="bi bi-calendar-x me-2"></i>
                      Overdue
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="history" className="rounded-0">
                      <i className="bi bi-clock-history me-2"></i>
                      Calibration History
                    </Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="standards" className="rounded-0">
                      <i className="bi bi-rulers me-2"></i>
                      Calibration Standards
                    </Nav.Link>
                  </Nav.Item>
                </Nav>
              </Card.Body>
            </Card>
          </Col>
          <Col md={9} lg={10}>
            <Tab.Content>
              <Tab.Pane eventKey="due">
                <Card>
                  <Card.Header>
                    <h4>Tools Due for Calibration</h4>
                  </Card.Header>
                  <Card.Body>
                    <CalibrationDueList />
                  </Card.Body>
                </Card>
              </Tab.Pane>
              <Tab.Pane eventKey="overdue">
                <Card>
                  <Card.Header>
                    <h4>Overdue Calibrations</h4>
                  </Card.Header>
                  <Card.Body>
                    <CalibrationOverdueList />
                  </Card.Body>
                </Card>
              </Tab.Pane>
              <Tab.Pane eventKey="history">
                <Card>
                  <Card.Header>
                    <h4>Calibration History</h4>
                  </Card.Header>
                  <Card.Body>
                    <CalibrationHistoryList />
                  </Card.Body>
                </Card>
              </Tab.Pane>
              <Tab.Pane eventKey="standards">
                <Card>
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    <h4>Calibration Standards</h4>
                    <Button
                      as={Link}
                      to="/calibration-standards/new"
                      variant="primary"
                      size="sm"
                    >
                      <i className="bi bi-plus-circle me-2"></i>
                      Add Standard
                    </Button>
                  </Card.Header>
                  <Card.Body>
                    <CalibrationStandardsList />
                  </Card.Body>
                </Card>
              </Tab.Pane>
            </Tab.Content>
          </Col>
        </Row>
      </Tab.Container>
    </div>
  );
};

export default CalibrationManagement;
