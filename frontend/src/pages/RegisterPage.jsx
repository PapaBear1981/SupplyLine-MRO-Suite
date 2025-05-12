import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Alert } from 'react-bootstrap';
import RegisterForm from '../components/auth/RegisterForm';
import { clearError } from '../store/authSlice';

const RegisterPage = () => {
  const { isAuthenticated, registrationSuccess } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  useEffect(() => {
    // If user is already authenticated, redirect to dashboard
    if (isAuthenticated) {
      navigate('/');
    }

    // Clear any errors when component unmounts
    return () => {
      dispatch(clearError());
    };
  }, [isAuthenticated, navigate, dispatch]);

  return (
    <Container fluid>
      <Row className="justify-content-center py-5">
        <Col lg={6} md={8} sm={12}>
          {registrationSuccess ? (
            <Card className="shadow">
              <Card.Header className="bg-success text-white text-center py-3">
                <h3 className="mb-0">Registration Submitted</h3>
              </Card.Header>
              <Card.Body className="p-4">
                <Alert variant="success">
                  <Alert.Heading>Registration Request Submitted Successfully!</Alert.Heading>
                  <p>
                    {registrationSuccess}
                  </p>
                  <p>
                    Your registration request has been submitted and is pending administrator approval.
                    You will not be able to log in until an administrator approves your request.
                  </p>
                  <hr />
                  <p className="mb-0">
                    You can now <Link to="/login" className="fw-bold">return to the login page</Link>.
                  </p>
                </Alert>
              </Card.Body>
            </Card>
          ) : (
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
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default RegisterPage;
