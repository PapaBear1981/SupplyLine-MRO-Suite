import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Alert, Spinner, InputGroup, ProgressBar } from 'react-bootstrap';
import { register } from '../../store/authSlice';
import { FaEye, FaEyeSlash, FaCheck, FaTimes } from 'react-icons/fa';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    employee_number: '',
    password: '',
    confirmPassword: '',
    department: '',
  });
  const [validated, setValidated] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [passwordFeedback, setPasswordFeedback] = useState([]);

  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Check password strength when password field changes
    if (name === 'password') {
      checkPasswordStrength(value);
    }
  };

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Toggle confirm password visibility
  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  // Check password strength
  const checkPasswordStrength = (password) => {
    const feedback = [];
    let strength = 0;

    // Check length
    if (password.length >= 8) {
      feedback.push({ valid: true, text: 'At least 8 characters' });
      strength += 25;
    } else {
      feedback.push({ valid: false, text: 'At least 8 characters' });
    }

    // Check for uppercase letters
    if (/[A-Z]/.test(password)) {
      feedback.push({ valid: true, text: 'Contains uppercase letter' });
      strength += 25;
    } else {
      feedback.push({ valid: false, text: 'Contains uppercase letter' });
    }

    // Check for numbers
    if (/[0-9]/.test(password)) {
      feedback.push({ valid: true, text: 'Contains number' });
      strength += 25;
    } else {
      feedback.push({ valid: false, text: 'Contains number' });
    }

    // Check for special characters
    if (/[^A-Za-z0-9]/.test(password)) {
      feedback.push({ valid: true, text: 'Contains special character' });
      strength += 25;
    } else {
      feedback.push({ valid: false, text: 'Contains special character' });
    }

    setPasswordStrength(strength);
    setPasswordFeedback(feedback);
  };

  // Get password strength color
  const getPasswordStrengthColor = () => {
    if (passwordStrength < 50) return 'danger';
    if (passwordStrength < 75) return 'warning';
    return 'success';
  };

  // Validate form before submission
  const validateForm = () => {
    // Check if all required fields are filled
    if (!formData.name || !formData.employee_number || !formData.department ||
        !formData.password || !formData.confirmPassword) {
      return false;
    }

    // Check if passwords match
    if (formData.password !== formData.confirmPassword) {
      return false;
    }

    // Check if password is strong enough
    if (passwordStrength < 75) {
      return false;
    }

    // Check if employee number is valid (alphanumeric only)
    const employeeNumberRegex = /^[A-Za-z0-9]+$/;
    if (!employeeNumberRegex.test(formData.employee_number)) {
      return false;
    }

    // Check if name is valid
    const nameRegex = /^[A-Za-z0-9\s\-\'\.]+$/;
    if (!nameRegex.test(formData.name)) {
      return false;
    }

    return true;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false || !validateForm()) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    // Remove confirmPassword before sending to API
    const { confirmPassword, ...userData } = formData;
    dispatch(register(userData));
  };

  return (
    <Form noValidate validated={validated} onSubmit={handleSubmit}>
      {error && <Alert variant="danger">{error.message || error.error || JSON.stringify(error)}</Alert>}

      <Alert variant="info" className="mb-3">
        <Alert.Heading>Registration Approval Required</Alert.Heading>
        <p>
          All new account registrations require administrator approval. After submitting your registration,
          an administrator will review your request and approve or deny it. You will not be able to log in
          until your registration is approved.
        </p>
      </Alert>

      <Form.Group className="mb-3" controlId="formName">
        <Form.Label>Full Name</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter your full name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          pattern="[A-Za-z0-9\s\-\'\.]+$"
          disabled={loading}
        />
        <Form.Control.Feedback type="invalid">
          Please provide a valid name (letters, numbers, spaces, hyphens, apostrophes, and periods only).
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formEmployeeNumber">
        <Form.Label>Employee Number</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter employee number"
          name="employee_number"
          value={formData.employee_number}
          onChange={handleChange}
          required
          pattern="[A-Za-z0-9]+"
          disabled={loading}
        />
        <Form.Control.Feedback type="invalid">
          Please provide a valid employee number (letters and numbers only).
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formDepartment">
        <Form.Label>Department</Form.Label>
        <Form.Select
          name="department"
          value={formData.department}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="">Select Department</option>
          <option value="Engineering">Engineering</option>
          <option value="Maintenance">Maintenance</option>
          <option value="Production">Production</option>
          <option value="Quality">Quality</option>
          <option value="Materials">Materials</option>
          <option value="IT">IT</option>
        </Form.Select>
        <Form.Control.Feedback type="invalid">
          Please select a department.
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
            minLength={8}
            isInvalid={validated && passwordStrength < 75}
            disabled={loading}
          />
          <Button
            variant="outline-secondary"
            onClick={togglePasswordVisibility}
            disabled={loading}
          >
            {showPassword ? <FaEyeSlash /> : <FaEye />}
          </Button>
          <Form.Control.Feedback type="invalid">
            Password must meet all strength requirements.
          </Form.Control.Feedback>
        </InputGroup>

        {formData.password && (
          <div className="mt-2">
            <ProgressBar
              variant={getPasswordStrengthColor()}
              now={passwordStrength}
              className="mb-2"
            />
            <div className="password-requirements">
              {passwordFeedback.map((item, index) => (
                <div key={index} className={`d-flex align-items-center ${item.valid ? 'text-success' : 'text-danger'}`}>
                  {item.valid ? <FaCheck className="me-1" /> : <FaTimes className="me-1" />}
                  <small>{item.text}</small>
                </div>
              ))}
            </div>
          </div>
        )}
      </Form.Group>

      <Form.Group className="mb-3" controlId="formConfirmPassword">
        <Form.Label>Confirm Password</Form.Label>
        <InputGroup>
          <Form.Control
            type={showConfirmPassword ? "text" : "password"}
            placeholder="Confirm Password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            isInvalid={validated && formData.password !== formData.confirmPassword}
            disabled={loading}
          />
          <Button
            variant="outline-secondary"
            onClick={toggleConfirmPasswordVisibility}
            disabled={loading}
          >
            {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
          </Button>
          <Form.Control.Feedback type="invalid">
            Passwords do not match.
          </Form.Control.Feedback>
        </InputGroup>
      </Form.Group>

      <Button
        variant="primary"
        type="submit"
        disabled={loading}
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
            <span className="ms-2">Registering...</span>
          </>
        ) : (
          'Register'
        )}
      </Button>
    </Form>
  );
};

export default RegisterForm;
