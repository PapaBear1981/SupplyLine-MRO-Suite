import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import { login } from '../../store/authSlice';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validated, setValidated] = useState(false);

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, error } = useSelector((state) => state.auth);

  // Get the redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    // Use the actual backend login API
    try {
      await dispatch(login({ username, password })).unwrap();
      console.log('Login successful!');
      // Navigate to the intended page after successful login
      navigate(from, { replace: true });
    } catch (err) {
      console.error('Login failed:', err);
      // Don't clear the form on error - let the user see the error and try again
      // The error will be displayed via the Redux state
    }
  };

  return (
    <Form noValidate validated={validated} onSubmit={handleSubmit}>
      {error && <Alert variant="danger" className="alert-danger error-message">{error.message || error.error || JSON.stringify(error)}</Alert>}

      <Form.Group className="mb-3" controlId="formUsername">
        <Form.Label>Employee Number</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter employee number"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          data-testid="employee-number-input"
        />
        <Form.Control.Feedback type="invalid">
          Please provide your employee number.
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formPassword">
        <Form.Label>Password</Form.Label>
        <Form.Control
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          data-testid="password-input"
        />
        <Form.Control.Feedback type="invalid">
          Please provide a password.
        </Form.Control.Feedback>
      </Form.Group>

      <Button variant="primary" type="submit" disabled={loading} data-testid="login-button">
        {loading ? (
          <>
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />
            <span className="ms-2">Logging in...</span>
          </>
        ) : (
          'Login'
        )}
      </Button>
    </Form>
  );
};

export default LoginForm;
