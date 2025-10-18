import { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Container, Row, Col, Card } from 'react-bootstrap';
import LoginForm from '../components/auth/LoginForm';
import ForcedPasswordChangeModal from '../components/auth/ForcedPasswordChangeModal';
import { clearPasswordChangeRequired } from '../store/authSlice';

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
      <Container fluid>
        <Row className="justify-content-center py-5">
          <Col lg={4} md={6} sm={10}>
            <Card className="shadow">
              <Card.Header className="bg-primary text-white text-center py-3">
                <h3 className="mb-0">Login to Tool Inventory System</h3>
              </Card.Header>
              <Card.Body className="p-4">
                <LoginForm />
                <div className="mt-4 text-center">
                  <p className="mb-0">
                    Don't have an account?{' '}
                    <Link to="/register" className="fw-bold">Register here</Link>
                  </p>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

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
