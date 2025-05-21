import { useState } from 'react';
import { useSelector } from 'react-redux';
import { Container, Navbar, Nav, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import ProfileModal from '../profile/ProfileModal';
import { APP_VERSION } from '../../utils/version';
import { useHelp } from '../../context/HelpContext';
import TourGuide from './TourGuide';

const MainLayout = ({ children }) => {
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const { showHelp, showTooltips, setShowHelp, setShowTooltips } = useHelp();
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showTour, setShowTour] = useState(false);

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container fluid>
          <Navbar.Brand as={Link} to="/">SupplyLine MRO Suite</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
              <Nav.Link as={Link} to="/tools">Tools</Nav.Link>
              <Nav.Link as={Link} to="/checkouts">Checkouts</Nav.Link>
              {user && (
                <>
                  {/* Show these links to admins and Materials department users */}
                  {(user.is_admin || user.department === 'Materials') && (
                    <>
                      <Nav.Link as={Link} to="/checkouts/all">All Checkouts</Nav.Link>
                      <Nav.Link as={Link} to="/chemicals">Chemicals</Nav.Link>
                      <Nav.Link as={Link} to="/calibrations">Calibrations</Nav.Link>
                      <Nav.Link as={Link} to="/reports">Reports</Nav.Link>
                    </>
                  )}

                  {/* Only show Admin Dashboard to admin users */}
                  {user.is_admin === true && (
                    <Nav.Link as={Link} to="/admin/dashboard">Admin Dashboard</Nav.Link>
                  )}
                </>
              )}

              {/* Scanner button - available to all authenticated users */}
              {user && (
                <Nav.Link as={Link} to="/scanner" className="ms-2 btn btn-outline-light btn-sm">
                  <i className="bi bi-upc-scan me-1"></i> Scanner
                </Nav.Link>
              )}
            </Nav>
            <Nav>
              {/* Help Button */}
              {isAuthenticated && (
                <div className="d-flex me-3">
                  <OverlayTrigger
                    placement="bottom"
                    overlay={<Tooltip id="tooltip-help">Toggle help features</Tooltip>}
                    trigger={showTooltips ? ['hover', 'focus'] : []}
                  >
                    <Button
                      variant={showHelp ? "info" : "outline-info"}
                      className="me-2"
                      onClick={() => setShowHelp(!showHelp)}
                      aria-label={showHelp ? "Hide help features" : "Show help features"}
                    >
                      <i className="bi bi-question-circle"></i>
                    </Button>
                  </OverlayTrigger>
                  <OverlayTrigger
                    placement="bottom"
                    overlay={<Tooltip id="tooltip-tour">Start guided tour</Tooltip>}
                    trigger={showTooltips ? ['hover', 'focus'] : []}
                  >
                    <Button
                      variant="outline-info"
                      onClick={() => setShowTour(true)}
                      aria-label="Start guided tour"
                    >
                      <i className="bi bi-info-circle"></i>
                    </Button>
                  </OverlayTrigger>
                </div>
              )}

              {isAuthenticated ? (
                <Button
                  variant="outline-light"
                  className="d-flex align-items-center"
                  onClick={() => setShowProfileModal(true)}
                >
                  <span className="me-2">{user?.name || 'User'}</span>
                  {user?.avatar ? (
                    <img
                      src={user.avatar}
                      alt="User Avatar"
                      className="avatar-circle-sm"
                      style={{ objectFit: 'cover' }}
                    />
                  ) : (
                    <div className="avatar-circle-sm bg-primary text-white">
                      {user?.name?.charAt(0) || 'U'}
                    </div>
                  )}
                </Button>
              ) : (
                <>
                  <Button variant="outline-light" className="me-2" as={Link} to="/login">
                    Login
                  </Button>
                  <Button variant="light" as={Link} to="/register">
                    Register
                  </Button>
                </>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container fluid className="flex-grow-1 mb-4 px-4">
        {children}
      </Container>

      <footer className="bg-dark text-light py-3 mt-auto">
        <Container fluid>
          <div className="d-flex justify-content-between">
            <span>SupplyLine MRO Suite &copy; {new Date().getFullYear()}</span>
            <span>Version {APP_VERSION}</span>
          </div>
        </Container>
      </footer>

      {/* Profile Modal */}
      <ProfileModal
        show={showProfileModal}
        onHide={() => setShowProfileModal(false)}
      />

      {/* Tour Guide */}
      <TourGuide
        show={showTour}
        onClose={() => setShowTour(false)}
        title="SupplyLine MRO Suite Tour"
        steps={[
          {
            title: 'Welcome to SupplyLine MRO Suite',
            content: 'This guided tour will help you understand the key features of the application. Click Next to continue or Skip Tour to exit at any time.'
          },
          {
            title: 'Navigation',
            content: 'The navigation bar at the top provides access to all main sections of the application, including Tools, Checkouts, Chemicals, and more.'
          },
          {
            title: 'Tool Management',
            content: 'The Tools section allows you to view, search, and manage all tools in the inventory. You can checkout tools, view their details, and track their status.'
          },
          {
            title: 'Checkout System',
            content: 'The Checkouts section shows tools that are currently checked out to users. You can return tools, view checkout history, and manage your checkouts.'
          },
          {
            title: 'Help Features',
            content: 'Throughout the application, you\'ll find help icons (?) that provide contextual information about features. You can also toggle help features on/off using the help button in the navigation bar.'
          },
          {
            title: 'User Profile',
            content: 'Click on your name in the top-right corner to access your profile, change settings, or log out.'
          },
          {
            title: 'That\'s it!',
            content: 'You\'re now ready to use SupplyLine MRO Suite. If you need help at any time, look for the help icons or start this tour again from the navigation bar.'
          }
        ]}
      />
    </div>
  );
};

export default MainLayout;
