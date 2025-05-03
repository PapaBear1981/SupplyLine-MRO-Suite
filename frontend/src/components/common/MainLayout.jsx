import { useSelector, useDispatch } from 'react-redux';
import { Container, Navbar, Nav, NavDropdown, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../../store/authSlice';

const MainLayout = ({ children }) => {
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container fluid>
          <Navbar.Brand as={Link} to="/">Tool Inventory System</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
              <Nav.Link as={Link} to="/tools">Tools</Nav.Link>
              <Nav.Link as={Link} to="/checkouts">Checkouts</Nav.Link>
              {user && (user.is_admin || user.department === 'Materials') && (
                <Nav.Link as={Link} to="/checkouts/all">All Checkouts</Nav.Link>
              )}
              {user && user.is_admin && (
                <Nav.Link as={Link} to="/admin">Admin</Nav.Link>
              )}
            </Nav>
            <Nav>
              {isAuthenticated ? (
                <NavDropdown title={user?.name || 'User'} id="user-dropdown">
                  <NavDropdown.Item as={Link} to="/profile">Profile</NavDropdown.Item>
                  <NavDropdown.Item as={Link} to="/my-checkouts">My Checkouts</NavDropdown.Item>
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
                </NavDropdown>
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
            <span>Version 1.0.0</span>
          </div>
        </Container>
      </footer>
    </div>
  );
};

export default MainLayout;
