import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Alert, Spinner, InputGroup } from 'react-bootstrap';
import { login } from '../../store/authSlice';
import { FaEye, FaEyeSlash } from 'react-icons/fa';

const LoginForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false
  });
  const [validated, setValidated] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [isLocked, setIsLocked] = useState(false);
  const [lockTimer, setLockTimer] = useState(0);

  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    // Basic form validation
    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    // Check if account is locked
    if (isLocked) {
      return;
    }

    setValidated(true);

    // Validate employee number format (alphanumeric only)
    const employeeNumberRegex = /^[A-Za-z0-9]+$/;
    if (!employeeNumberRegex.test(formData.username)) {
      setFormData({
        ...formData,
        password: '' // Clear password for security
      });
      return;
    }

    // Use the actual backend login API
    try {
      await dispatch(login({
        username: formData.username,
        password: formData.password,
        rememberMe: formData.rememberMe
      })).unwrap();

      // Reset login attempts on successful login
      setLoginAttempts(0);
    } catch (err) {
      console.error('Login failed:', err);

      // Increment login attempts
      const newAttempts = loginAttempts + 1;
      setLoginAttempts(newAttempts);

      // Lock account after 5 failed attempts
      if (newAttempts >= 5) {
        setIsLocked(true);
        setLockTimer(30); // Lock for 30 seconds
      }

      // Clear password field for security
      setFormData({
        ...formData,
        password: ''
      });
    }
  };

  // Handle account lockout timer
  useEffect(() => {
    let interval;
    if (isLocked && lockTimer > 0) {
      interval = setInterval(() => {
        setLockTimer((prevTimer) => {
          if (prevTimer <= 1) {
            setIsLocked(false);
            setLoginAttempts(0);
            clearInterval(interval);
            return 0;
          }
          return prevTimer - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isLocked, lockTimer]);

  return (
    <Form noValidate validated={validated} onSubmit={handleSubmit}>
      {error && <Alert variant="danger">{error.message || error.error || JSON.stringify(error)}</Alert>}

      {isLocked && (
        <Alert variant="warning">
          Too many failed login attempts. Please wait {lockTimer} seconds before trying again.
        </Alert>
      )}

      <Form.Group className="mb-3" controlId="formUsername">
        <Form.Label>Employee Number</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter employee number"
          name="username"
          value={formData.username}
          onChange={handleChange}
          required
          disabled={isLocked || loading}
          pattern="[A-Za-z0-9]+"
        />
        <Form.Control.Feedback type="invalid">
          Please provide a valid employee number (letters and numbers only).
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formPassword">
        <Form.Label>Password</Form.Label>
        <InputGroup>
          <Form.Control
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            disabled={isLocked || loading}
            minLength={8}
          />
          <Button
            variant="outline-secondary"
            onClick={togglePasswordVisibility}
            disabled={isLocked || loading}
          >
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </Button>
          <Form.Control.Feedback type="invalid">
            Please provide your password.
          </Form.Control.Feedback>
        </InputGroup>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formRememberMe">
        <Form.Check
          type="checkbox"
          label="Remember me"
          name="rememberMe"
          checked={formData.rememberMe}
          onChange={handleChange}
          disabled={isLocked || loading}
        />
      </Form.Group>

      <Button
        variant="primary"
        type="submit"
        disabled={isLocked || loading}
        className="w-100"
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
