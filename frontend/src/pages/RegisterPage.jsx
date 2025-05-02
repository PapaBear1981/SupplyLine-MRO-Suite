import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Row, Col, Card } from 'react-bootstrap';
import RegisterForm from '../components/auth/RegisterForm';

const RegisterPage = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  const navigate = useNavigate();

  useEffect(() => {
    // If user is already authenticated, redirect to dashboard
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Container fluid>
      <Row className="justify-content-center py-5">
        <Col lg={6} md={8} sm={12}>
          <Card className="shadow">
            <Card.Header className="bg-primary text-white text-center py-3">
              <h3 className="mb-0">Register New Account</h3>
            </Card.Header>
            <Card.Body className="p-4">
              <RegisterForm />
              <div className="mt-4 text-center">
                <p className="mb-0">
                  Already have an account?{' '}
                  <Link to="/login" className="fw-bold">Login here</Link>
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default RegisterPage;
