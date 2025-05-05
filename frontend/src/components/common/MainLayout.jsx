import { useState } from 'react';
import { useSelector } from 'react-redux';
import { Container, Navbar, Nav, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import ProfileModal from '../profile/ProfileModal';

const MainLayout = ({ children }) => {
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const [showProfileModal, setShowProfileModal] = useState(false);

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container fluid>
          <Navbar.Brand as={Link} to="/">Tool Inventory System</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/tools">Tools</Nav.Link>
              <Nav.Link as={Link} to="/checkouts">Checkouts</Nav.Link>
              {user && (user.is_admin || user.department === 'Materials') && (
                <>
                  <Nav.Link as={Link} to="/checkouts/all">All Checkouts</Nav.Link>
                  <Nav.Link as={Link} to="/users">User Management</Nav.Link>
                  <Nav.Link as={Link} to="/reports">Reports</Nav.Link>
                </>
              )}
            </Nav>
            <Nav>
              {isAuthenticated ? (
                <Button
                  variant="outline-light"
                  className="d-flex align-items-center"
                  onClick={() => setShowProfileModal(true)}
                >
                  <span className="me-2">{user?.name || 'User'}</span>
                  <div className="avatar-circle-sm bg-primary text-white">
                    {user?.name?.charAt(0) || 'U'}
                  </div>
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
            <span>Tool Inventory System &copy; {new Date().getFullYear()}</span>
            <span>Version 1.2.0</span>
          </div>
        </Container>
      </footer>

      {/* Profile Modal */}
      <ProfileModal
        show={showProfileModal}
        onHide={() => setShowProfileModal(false)}
      />
    </div>
  );
};

export default MainLayout;
