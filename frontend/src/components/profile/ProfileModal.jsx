import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Modal, Button, Form, ListGroup } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../../store/authSlice';
import { toggleTheme } from '../../store/themeSlice';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';

const ProfileModal = ({ show, onHide }) => {
  const { user } = useSelector((state) => state.auth);
  const { theme } = useSelector((state) => state.theme);
  const { showTooltips } = useHelp();
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    onHide();
    navigate('/login');
  };

  const handleThemeToggle = () => {
    dispatch(toggleTheme());
  };

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
            <Tooltip text={showTooltips ? "Switch between light and dark theme modes" : null} placement="right">
              <Form.Check
                type="switch"
                id="theme-switch"
                label={`Theme: ${theme === 'light' ? 'Light' : 'Dark'}`}
                checked={theme === 'dark'}
                onChange={handleThemeToggle}
              />
            </Tooltip>
          </Form>
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
