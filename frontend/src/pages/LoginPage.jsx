import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Container, Row, Col, Card } from 'react-bootstrap';
import LoginForm from '../components/auth/LoginForm';

const LoginPage = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  const location = useLocation();

  // Get the redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || '/';

  useEffect(() => {
    // If user is already authenticated, redirect to the intended page
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  return (
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
  );
};

export default LoginPage;
