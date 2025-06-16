import { useState, useEffect } from 'react';
import { Modal, Button, Alert, ProgressBar } from 'react-bootstrap';
import { useDispatch } from 'react-redux';
import { logout } from '../../store/authSlice';

/**
 * Auto Logout Warning Modal Component
 * Shows a warning before automatic logout with countdown and extend session option
 */
const AutoLogoutWarning = ({ show, onHide, onExtend, warningMinutes = 5 }) => {
  const [timeLeft, setTimeLeft] = useState(warningMinutes * 60); // Convert to seconds
  const dispatch = useDispatch();

  useEffect(() => {
    if (!show) {
      setTimeLeft(warningMinutes * 60);
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          // Time's up, logout automatically
          dispatch(logout());
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [show, warningMinutes, dispatch]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleExtendSession = () => {
    onExtend();
    onHide();
  };

  const handleLogoutNow = () => {
    dispatch(logout());
  };

  const progressPercentage = ((warningMinutes * 60 - timeLeft) / (warningMinutes * 60)) * 100;

  return (
    <Modal 
      show={show} 
      onHide={onHide}
      backdrop="static"
      keyboard={false}
      centered
      size="md"
    >
      <Modal.Header>
        <Modal.Title className="text-warning">
          <i className="fas fa-exclamation-triangle me-2"></i>
          Session Timeout Warning
        </Modal.Title>
      </Modal.Header>
      
      <Modal.Body>
        <Alert variant="warning" className="mb-3">
          <strong>Your session will expire soon!</strong>
        </Alert>
        
        <p className="mb-3">
          You will be automatically logged out in <strong>{formatTime(timeLeft)}</strong> due to inactivity.
        </p>
        
        <div className="mb-3">
          <div className="d-flex justify-content-between mb-1">
            <small className="text-muted">Time remaining</small>
            <small className="text-muted">{formatTime(timeLeft)}</small>
          </div>
          <ProgressBar 
            variant={timeLeft < 60 ? 'danger' : timeLeft < 120 ? 'warning' : 'info'}
            now={progressPercentage}
            animated
          />
        </div>
        
        <p className="text-muted small mb-0">
          Click "Stay Logged In" to extend your session, or "Logout Now" to logout immediately.
        </p>
      </Modal.Body>
      
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={handleLogoutNow}>
          Logout Now
        </Button>
        <Button variant="primary" onClick={handleExtendSession}>
          Stay Logged In
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AutoLogoutWarning;
