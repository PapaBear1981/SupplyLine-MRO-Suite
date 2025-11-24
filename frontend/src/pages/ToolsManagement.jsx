import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Button, Alert, Tab, Nav, Row, Col } from 'react-bootstrap';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import ToolList from '../components/tools/ToolList';
import BulkImportTools from '../components/tools/BulkImportTools';
import ToolsDashboard from '../components/tools/ToolsDashboard';
import UserCheckouts from '../components/checkouts/UserCheckouts';
import AllCheckouts from '../components/checkouts/AllCheckouts';
import RecentTransactions from '../components/tools/RecentTransactions';
import CalibrationDueList from '../components/calibration/CalibrationDueList';
import CalibrationOverdueList from '../components/calibration/CalibrationOverdueList';
import CalibrationHistoryList from '../components/calibration/CalibrationHistoryList';
import CalibrationStandardsList from '../components/calibration/CalibrationStandardsList';
import { fetchTools } from '../store/toolsSlice';
import { fetchCheckouts, fetchUserCheckouts } from '../store/checkoutsSlice';
import useHotkeys from '../hooks/useHotkeys';

const ToolsManagement = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const isAdmin = user?.is_admin || user?.department === 'Materials';
  const unauthorized = location.state?.unauthorized;

  // Get tab from URL query parameter or default to 'tools'
  const tabParam = searchParams.get('tab');
  const [activeTab, setActiveTab] = useState(tabParam || 'tools');

  // Update active tab when URL query parameter changes
  useEffect(() => {
    const validTabs = ['tools', 'my-checkouts', 'all-checkouts', 'calibrations', 'transactions'];
    if (tabParam && validTabs.includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  // Sub-tab for calibrations
  const [calibrationTab, setCalibrationTab] = useState('due');

  // Handle tab selection - update both state and URL
  const handleTabSelect = (key) => {
    setActiveTab(key);
    setSearchParams({ tab: key }, { replace: true });
  };

  // Load data on mount
  useEffect(() => {
    // Fetch tools data
    dispatch(fetchTools());

    // Fetch checkout data based on user role
    if (isAdmin) {
      dispatch(fetchCheckouts()); // All checkouts for admin
    }
    dispatch(fetchUserCheckouts()); // User's own checkouts
  }, [dispatch, isAdmin]);

  // Page-specific hotkeys
  useHotkeys({
    'n': () => {
      if (isAdmin) {
        navigate('/tools/new');
      }
    }
  }, {
    enabled: isAdmin,
    deps: [navigate, isAdmin]
  });

  return (
    <div className="w-100">
      {/* Show unauthorized message if redirected from admin page */}
      {unauthorized && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Access Denied</Alert.Heading>
          <p>
            You do not have permission to access the Admin Dashboard. This area is restricted to administrators only.
          </p>
        </Alert>
      )}

      {/* Page Header */}
      <div className="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
        <h1 className="mb-0">
          <i className="bi bi-tools me-2"></i>
          Tool Management
        </h1>
        <div className="d-flex gap-2 flex-wrap">
          {isAdmin && <BulkImportTools />}
          {isAdmin && (
            <Button as={Link} to="/tools/new" variant="success" size="lg">
              <i className="bi bi-plus-circle me-2"></i>
              Add New Tool
            </Button>
          )}
        </div>
      </div>

      {/* Dashboard Cards */}
      <ToolsDashboard />

      {/* Tabs */}
      <Tab.Container id="tools-tabs" activeKey={activeTab} onSelect={handleTabSelect}>
        <Nav variant="tabs" className="mb-3">
          <Nav.Item>
            <Nav.Link eventKey="tools">
              <i className="bi bi-tools me-2"></i>
              Tools
            </Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey="my-checkouts">
              <i className="bi bi-person-check me-2"></i>
              My Checkouts
            </Nav.Link>
          </Nav.Item>
          {isAdmin && (
            <Nav.Item>
              <Nav.Link eventKey="all-checkouts">
                <i className="bi bi-box-arrow-right me-2"></i>
                All Checkouts
              </Nav.Link>
            </Nav.Item>
          )}
          {isAdmin && (
            <Nav.Item>
              <Nav.Link eventKey="calibrations">
                <i className="bi bi-sliders me-2"></i>
                Calibrations
              </Nav.Link>
            </Nav.Item>
          )}
          <Nav.Item>
            <Nav.Link eventKey="transactions">
              <i className="bi bi-clock-history me-2"></i>
              Recent Transactions
            </Nav.Link>
          </Nav.Item>
        </Nav>

        <Tab.Content>
          {/* Tools Tab */}
          <Tab.Pane eventKey="tools">
            <ToolList />
          </Tab.Pane>

          {/* My Checkouts Tab */}
          <Tab.Pane eventKey="my-checkouts">
            <UserCheckouts />
          </Tab.Pane>

          {/* All Checkouts Tab (Admin only) */}
          {isAdmin && (
            <Tab.Pane eventKey="all-checkouts">
              <AllCheckouts />
            </Tab.Pane>
          )}

          {/* Calibrations Tab (Admin only) */}
          {isAdmin && (
            <Tab.Pane eventKey="calibrations">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="mb-0">Calibration Management</h4>
                <Button
                  as={Link}
                  to="/calibration-standards/new"
                  variant="primary"
                >
                  <i className="bi bi-plus-circle me-2"></i>
                  Add Calibration Standard
                </Button>
              </div>

              <Tab.Container
                id="calibration-subtabs"
                activeKey={calibrationTab}
                onSelect={setCalibrationTab}
              >
                <Row>
                  <Col md={3} lg={2} className="mb-3">
                    <Nav variant="pills" className="flex-column">
                      <Nav.Item>
                        <Nav.Link eventKey="due">
                          <i className="bi bi-calendar-check me-2"></i>
                          Due Soon
                        </Nav.Link>
                      </Nav.Item>
                      <Nav.Item>
                        <Nav.Link eventKey="overdue">
                          <i className="bi bi-calendar-x me-2"></i>
                          Overdue
                        </Nav.Link>
                      </Nav.Item>
                      <Nav.Item>
                        <Nav.Link eventKey="history">
                          <i className="bi bi-clock-history me-2"></i>
                          History
                        </Nav.Link>
                      </Nav.Item>
                      <Nav.Item>
                        <Nav.Link eventKey="standards">
                          <i className="bi bi-rulers me-2"></i>
                          Standards
                        </Nav.Link>
                      </Nav.Item>
                    </Nav>
                  </Col>
                  <Col md={9} lg={10}>
                    <Tab.Content>
                      <Tab.Pane eventKey="due">
                        <CalibrationDueList />
                      </Tab.Pane>
                      <Tab.Pane eventKey="overdue">
                        <CalibrationOverdueList />
                      </Tab.Pane>
                      <Tab.Pane eventKey="history">
                        <CalibrationHistoryList />
                      </Tab.Pane>
                      <Tab.Pane eventKey="standards">
                        <CalibrationStandardsList />
                      </Tab.Pane>
                    </Tab.Content>
                  </Col>
                </Row>
              </Tab.Container>
            </Tab.Pane>
          )}

          {/* Recent Transactions Tab */}
          <Tab.Pane eventKey="transactions">
            <RecentTransactions />
          </Tab.Pane>
        </Tab.Content>
      </Tab.Container>
    </div>
  );
};

export default ToolsManagement;
