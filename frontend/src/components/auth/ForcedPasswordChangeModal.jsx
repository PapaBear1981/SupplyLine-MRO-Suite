import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Modal, Form, Button, Alert } from 'react-bootstrap';
import PasswordStrengthMeter from '../common/PasswordStrengthMeter';
import api from '../../services/api';
import { fetchCurrentUser } from '../../store/authSlice';

/**
 * Non-dismissible modal for forced password changes
 * Shown when user logs in with a temporary password after admin reset
 */
const ForcedPasswordChangeModal = ({ show, employeeNumber, currentPassword, onPasswordChanged }) => {
  const dispatch = useDispatch();
  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: '',
  });
  const [passwordValid, setPasswordValid] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    setError(''); // Clear error when user types
  };

  const handlePasswordValidationChange = (isValid) => {
    setPasswordValid(isValid);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.newPassword !== formData.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    // Validate password strength
    if (!passwordValid) {
      setError('Password does not meet security requirements');
      return;
    }

    setLoading(true);

    try {
      // Call the forced password change endpoint
      const response = await api.post('/auth/change-password', {
        employee_number: employeeNumber,
        current_password: currentPassword,
        new_password: formData.newPassword,
      });

      // Password changed successfully
      // The backend returns user data and sets JWT cookies
      // Now fetch the current user to update the auth state
      await dispatch(fetchCurrentUser()).unwrap();

      if (onPasswordChanged) {
        onPasswordChanged(response.data);
      }
    } catch (err) {
      console.error('Failed to change password:', err);
      const errorMessage = err.response?.data?.error || 'Failed to change password. Please try again.';
      const errorDetails = err.response?.data?.details;

      if (errorDetails && Array.isArray(errorDetails)) {
        setError(`${errorMessage}\n${errorDetails.join('\n')}`);
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      show={show}
      backdrop="static"
      keyboard={false}
      centered
      size="md"
    >
      <Modal.Header className="bg-warning text-dark">
        <Modal.Title>
          <i className="bi bi-shield-exclamation me-2"></i>
          Password Change Required
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Alert variant="info" className="mb-4">
          <i className="bi bi-info-circle me-2"></i>
          Your password has been reset by an administrator. For security reasons, you must set a new password before continuing.
        </Alert>

        {error && (
          <Alert variant="danger" className="mb-3">
            {error.split('\n').map((line, index) => (
              <div key={index}>{line}</div>
            ))}
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>New Password</Form.Label>
            <Form.Control
              type="password"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleInputChange}
              required
              autoFocus
              disabled={loading}
            />
            <PasswordStrengthMeter
              password={formData.newPassword}
              onValidationChange={handlePasswordValidationChange}
            />
          </Form.Group>

          <Form.Group className="mb-4">
            <Form.Label>Confirm New Password</Form.Label>
            <Form.Control
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
              disabled={loading}
            />
            {formData.confirmPassword && formData.newPassword !== formData.confirmPassword && (
              <Form.Text className="text-danger">
                Passwords do not match
              </Form.Text>
            )}
          </Form.Group>

          <div className="d-grid">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={loading || !passwordValid || formData.newPassword !== formData.confirmPassword}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Changing Password...
                </>
              ) : (
                <>
                  <i className="bi bi-check-circle me-2"></i>
                  Set New Password
                </>
              )}
            </Button>
          </div>
        </Form>

        <div className="mt-3 text-muted small">
          <p className="mb-1"><strong>Password Requirements:</strong></p>
          <ul className="mb-0">
            <li>At least 8 characters long</li>
            <li>Contains uppercase and lowercase letters</li>
            <li>Contains at least one number</li>
            <li>Contains at least one special character</li>
            <li>Cannot match your last 5 passwords</li>
          </ul>
        </div>
      </Modal.Body>
    </Modal>
  );
};

export default ForcedPasswordChangeModal;

