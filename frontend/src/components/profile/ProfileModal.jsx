import { useSelector, useDispatch } from 'react-redux';
import { Modal, Button, Form, ListGroup } from 'react-bootstrap';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { logout } from '../../store/authSlice';
import { toggleTheme } from '../../store/themeSlice';
import { useHotkeyContext } from '../../context/HotkeyContext';

const ProfileModal = ({ show, onHide, onShowTour, onToggleHelp, onShowCustomize, showHelp }) => {
  const { user } = useSelector((state) => state.auth);
  const { theme } = useSelector((state) => state.theme);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { preferences, setHotkeysEnabled, toggleHelpModal } = useHotkeyContext();

  const handleLogout = () => {
    dispatch(logout());
    onHide();
    navigate('/login');
  };

  const handleThemeToggle = () => {
    dispatch(toggleTheme());
  };

  const handleHelpToggle = () => {
    if (onToggleHelp) {
      onToggleHelp();
    }
  };

  const handleTourClick = () => {
    if (onShowTour) {
      onShowTour();
      onHide();
    }
  };

  const handleCustomizeClick = () => {
    // Call the global function exposed by UserDashboardPage
    if (window.openDashboardCustomizer) {
      window.openDashboardCustomizer();
      onHide();
    } else if (onShowCustomize) {
      onShowCustomize();
      onHide();
    }
  };

  // Check if we're on the dashboard page
  const isOnDashboard = location.pathname === '/dashboard';

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>User Profile</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="text-center mb-4">
          <div className="user-avatar mb-3">
            {/* User avatar or initials */}
            {user?.avatar ? (
              <img
                src={user.avatar}
                alt="User Avatar"
                className="avatar-circle"
                style={{ objectFit: 'cover' }}
              />
            ) : (
              <div className="avatar-circle bg-primary text-white">
                {user?.name?.charAt(0) || 'U'}
              </div>
            )}
          </div>
          <h5 className="mb-1">{user?.name || 'User'}</h5>
          <p className="text-muted mb-0">
            {user?.is_admin
              ? 'Administrator'
              : user?.department === 'Materials'
                ? 'Materials (Tool Manager)'
                : user?.department || 'Regular User'}
          </p>
        </div>

        <ListGroup className="mb-4">
          <ListGroup.Item action as={Link} to="/profile" onClick={onHide}>
            <i className="bi bi-person me-2"></i> View Profile
          </ListGroup.Item>
          <ListGroup.Item action as={Link} to="/my-checkouts" onClick={onHide}>
            <i className="bi bi-tools me-2"></i> My Checkouts
          </ListGroup.Item>
        </ListGroup>

        <div className="mb-4">
          <h6 className="mb-3">Preferences</h6>
          <Form>
            <Form.Check
              type="switch"
              id="theme-switch"
              label={`Theme: ${theme === 'light' ? 'Light' : 'Dark'}`}
              checked={theme === 'dark'}
              onChange={handleThemeToggle}
              className="mb-2"
            />
            <Form.Check
              type="switch"
              id="hotkeys-switch"
              label={`Keyboard Shortcuts: ${preferences.enabled ? 'Enabled' : 'Disabled'}`}
              checked={preferences.enabled}
              onChange={(e) => setHotkeysEnabled(e.target.checked)}
            />
          </Form>
        </div>

        <div className="mb-3">
          <h6 className="mb-3">Application Settings</h6>
          <div className="d-grid gap-2">
            {isOnDashboard && (
              <Button
                variant="outline-primary"
                onClick={handleCustomizeClick}
              >
                <i className="bi bi-sliders me-2"></i>
                Customize Dashboard
              </Button>
            )}
            <Button
              variant="outline-secondary"
              onClick={() => {
                toggleHelpModal();
                onHide();
              }}
              disabled={!preferences.enabled}
            >
              <i className="bi bi-keyboard me-2"></i>
              View Keyboard Shortcuts
            </Button>
            {onToggleHelp && (
              <Button
                variant={showHelp ? "info" : "outline-info"}
                onClick={handleHelpToggle}
              >
                <i className="bi bi-question-circle me-2"></i>
                {showHelp ? 'Hide Help Features' : 'Show Help Features'}
              </Button>
            )}
            {onShowTour && (
              <Button
                variant="outline-info"
                onClick={handleTourClick}
              >
                <i className="bi bi-info-circle me-2"></i>
                Start Guided Tour
              </Button>
            )}
          </div>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide}>
          Close
        </Button>
        <Button variant="danger" onClick={handleLogout}>
          Logout
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ProfileModal;
