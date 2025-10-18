import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { FaTools } from 'react-icons/fa';
import LoginForm from '../components/auth/LoginForm';
import ForcedPasswordChangeModal from '../components/auth/ForcedPasswordChangeModal';
import { clearPasswordChangeRequired } from '../store/authSlice';
import './LoginPage.css';

const LoginPage = () => {
  const { isAuthenticated, user, passwordChangeRequired, passwordChangeData } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPasswordChangeModal, setShowPasswordChangeModal] = useState(false);

  // Get the redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || '/';

  // Handle password change required state
  useEffect(() => {
    if (passwordChangeRequired && passwordChangeData) {
      setShowPasswordChangeModal(true);
    }
  }, [passwordChangeRequired, passwordChangeData]);

  useEffect(() => {
    // Only redirect if user is authenticated AND we have user data
    // This prevents redirect loops during initial auth check
    if (isAuthenticated && user) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, user, navigate, from]);

  const handlePasswordChanged = () => {
    // Password was successfully changed
    // The backend returns user data and sets cookies
    setShowPasswordChangeModal(false);
    dispatch(clearPasswordChangeRequired());

    // Redirect to dashboard
    navigate('/dashboard', { replace: true });
  };

  return (
    <>
      <div className="login-page-wrapper">
        <div className="login-container">
          <div className="login-card">
            <div className="login-card-header">
              <div className="login-logo">
                <FaTools className="login-logo-icon" />
              </div>
              <h1 className="login-card-title">SupplyLine MRO Suite</h1>
              <p className="login-card-subtitle">Tool Inventory Management System</p>
            </div>
            <div className="login-card-body">
              <LoginForm />
              <div className="login-register-link">
                <p>
                  Don't have an account?{' '}
                  <Link to="/register">Register here</Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Forced Password Change Modal */}
      {passwordChangeData && (
        <ForcedPasswordChangeModal
          show={showPasswordChangeModal}
          employeeNumber={passwordChangeData.employeeNumber}
          currentPassword={passwordChangeData.password}
          onPasswordChanged={handlePasswordChanged}
        />
      )}
    </>
  );
};

export default LoginPage;
