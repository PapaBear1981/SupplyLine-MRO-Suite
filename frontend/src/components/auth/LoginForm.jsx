import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import { login } from '../../store/authSlice';

const LoginForm = () => {
  console.log('=== LOGIN FORM COMPONENT RENDERED ===');

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [validated, setValidated] = useState(false);

  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  console.log('Login form state:', { username, password: password ? '[HIDDEN]' : 'EMPTY', rememberMe, loading, error });

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('=== LOGIN FORM SUBMITTED ===');
    console.log('Username:', username);
    console.log('Password:', password ? '[HIDDEN]' : 'EMPTY');
    console.log('Remember Me:', rememberMe);

    // Simple validation
    if (!username || !password) {
      console.log('Missing username or password');
      return;
    }

    console.log('Validation passed, dispatching login action...');

    // Direct API call without Redux
    try {
      console.log('Making direct API call...');

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          employee_number: username,
          password: password,
          remember_me: rememberMe
        })
      });

      console.log('API response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Login API response:', data);

      // Store tokens in localStorage
      localStorage.setItem('supplyline_access_token', data.access_token);
      localStorage.setItem('supplyline_refresh_token', data.refresh_token);
      localStorage.setItem('supplyline_user_data', JSON.stringify(data.user));

      console.log('Tokens stored, redirecting to dashboard...');

      // Redirect to dashboard
      window.location.href = '/dashboard';

    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      {error && <Alert variant="danger">{error.message || error.error || JSON.stringify(error)}</Alert>}

      <Form.Group className="mb-3" controlId="formUsername">
        <Form.Label>Employee Number</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter employee number"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
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
        />
        <Form.Control.Feedback type="invalid">
          Please provide a password.
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formRememberMe">
        <Form.Check
          type="checkbox"
          label="Remember me"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
        />
      </Form.Group>

      <Button
        variant="primary"
        type="submit"
        disabled={loading}
      >
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
