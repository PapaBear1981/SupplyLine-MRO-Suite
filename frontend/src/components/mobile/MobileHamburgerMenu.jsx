import { Offcanvas, Nav, Button, Dropdown } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { logout } from '../../store/authSlice';
import { useViewPreference } from '../../utils/deviceDetection';
import { APP_VERSION } from '../../utils/version';

const MobileHamburgerMenu = ({ show, onHide, user }) => {
  const dispatch = useDispatch();
  const { viewPreference, setPreference } = useViewPreference();

  const handleLogout = () => {
    dispatch(logout());
    onHide();
  };

  const handleViewPreferenceChange = (preference) => {
    setPreference(preference);
    // Force page reload to apply new layout
    window.location.reload();
  };

  return (
    <Offcanvas show={show} onHide={onHide} placement="start" className="mobile-menu">
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Menu</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <Nav className="flex-column">
          {/* Primary Navigation */}
          <Nav.Link as={Link} to="/dashboard" onClick={onHide}>
            <i className="bi bi-house me-2"></i>
            Dashboard
          </Nav.Link>
          
          <Nav.Link as={Link} to="/tools" onClick={onHide}>
            <i className="bi bi-tools me-2"></i>
            Tools
          </Nav.Link>
          
          <Nav.Link as={Link} to="/checkouts" onClick={onHide}>
            <i className="bi bi-clipboard-check me-2"></i>
            My Checkouts
          </Nav.Link>

          {/* Admin and Materials specific links */}
          {user && (user.is_admin || user.department === 'Materials') && (
            <>
              <hr />
              <h6 className="text-muted px-3">Management</h6>
              
              <Nav.Link as={Link} to="/checkouts/all" onClick={onHide}>
                <i className="bi bi-list-check me-2"></i>
                All Checkouts
              </Nav.Link>
              
              <Nav.Link as={Link} to="/chemicals" onClick={onHide}>
                <i className="bi bi-flask me-2"></i>
                Chemicals
              </Nav.Link>
              
              <Nav.Link as={Link} to="/calibrations" onClick={onHide}>
                <i className="bi bi-speedometer2 me-2"></i>
                Calibrations
              </Nav.Link>
              
              <Nav.Link as={Link} to="/cycle-counts" onClick={onHide}>
                <i className="bi bi-arrow-repeat me-2"></i>
                Cycle Counts
              </Nav.Link>
              
              <Nav.Link as={Link} to="/reports" onClick={onHide}>
                <i className="bi bi-graph-up me-2"></i>
                Reports
              </Nav.Link>
            </>
          )}

          {/* Admin only links */}
          {user?.is_admin && (
            <>
              <hr />
              <h6 className="text-muted px-3">Administration</h6>
              
              <Nav.Link as={Link} to="/admin/dashboard" onClick={onHide}>
                <i className="bi bi-gear me-2"></i>
                Admin Dashboard
              </Nav.Link>
            </>
          )}

          <hr />
          
          {/* Settings */}
          <h6 className="text-muted px-3">Settings</h6>
          
          <div className="px-3 mb-3">
            <label className="form-label small">View Preference</label>
            <Dropdown>
              <Dropdown.Toggle variant="outline-secondary" size="sm" className="w-100">
                {viewPreference === 'auto' ? 'Auto' : 
                 viewPreference === 'mobile' ? 'Mobile' : 'Desktop'}
              </Dropdown.Toggle>
              <Dropdown.Menu className="w-100">
                <Dropdown.Item onClick={() => handleViewPreferenceChange('auto')}>
                  Auto (Recommended)
                </Dropdown.Item>
                <Dropdown.Item onClick={() => handleViewPreferenceChange('mobile')}>
                  Always Mobile
                </Dropdown.Item>
                <Dropdown.Item onClick={() => handleViewPreferenceChange('desktop')}>
                  Always Desktop
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </div>

          <Nav.Link as={Link} to="/profile" onClick={onHide}>
            <i className="bi bi-person me-2"></i>
            Profile Settings
          </Nav.Link>

          <hr />
          
          <Button variant="outline-danger" onClick={handleLogout} className="mx-3">
            <i className="bi bi-box-arrow-right me-2"></i>
            Logout
          </Button>
        </Nav>

        <div className="mt-auto pt-4">
          <small className="text-muted px-3">
            SupplyLine MRO Suite v{APP_VERSION}
          </small>
        </div>
      </Offcanvas.Body>
    </Offcanvas>
  );
};

export default MobileHamburgerMenu;
