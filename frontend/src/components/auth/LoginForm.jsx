import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import { login } from '../../store/authSlice';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validated, setValidated] = useState(false);
  const { showTooltips } = useHelp();

  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

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
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <Form noValidate validated={validated} onSubmit={handleSubmit}>
      {error && <Alert variant="danger">{error.message || error.error || JSON.stringify(error)}</Alert>}

      <Form.Group className="mb-3" controlId="formUsername">
        <Tooltip text="Enter your unique employee identification number" placement="right" show={showTooltips}>
          <Form.Label>Employee Number</Form.Label>
        </Tooltip>
        <Form.Control
          type="text"
          placeholder="Enter employee number"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          aria-describedby="username-help"
        />
        <Form.Control.Feedback type="invalid">
          Please provide your employee number.
        </Form.Control.Feedback>
        <Form.Text id="username-help" className="text-muted">
          Use the employee number provided by your administrator.
        </Form.Text>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formPassword">
        <Tooltip text="Enter your account password" placement="right" show={showTooltips}>
          <Form.Label>Password</Form.Label>
        </Tooltip>
        <Form.Control
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          aria-describedby="password-help"
        />
        <Form.Control.Feedback type="invalid">
          Please provide a password.
        </Form.Control.Feedback>
        <Form.Text id="password-help" className="text-muted">
          Contact your administrator if you've forgotten your password.
        </Form.Text>
      </Form.Group>

      <Button variant="primary" type="submit" disabled={loading}>
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
