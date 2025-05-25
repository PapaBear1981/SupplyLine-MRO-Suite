import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import { register } from '../../store/authSlice';
import PasswordStrengthMeter from '../common/PasswordStrengthMeter';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    employee_number: '',
    password: '',
    confirmPassword: '',
    department: '',
  });
  const [validated, setValidated] = useState(false);
  const [passwordValid, setPasswordValid] = useState(false);
  const { showTooltips } = useHelp();

  const dispatch = useDispatch();
  const { loading, error } = useSelector((state) => state.auth);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    if (form.checkValidity() === false ||
        formData.password !== formData.confirmPassword ||
        !passwordValid) {
      e.stopPropagation();
      setValidated(true);
      return;
    }

    setValidated(true);

    // Remove confirmPassword before sending to API
    const { confirmPassword, ...userData } = formData;
    dispatch(register(userData));
  };

  const handlePasswordValidationChange = (isValid) => {
    setPasswordValid(isValid);
  };

  return (
    <Form noValidate validated={validated} onSubmit={handleSubmit}>
      {error && <Alert variant="danger">{error.message}</Alert>}

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
        />
        <Form.Control.Feedback type="invalid">
          Please provide your name.
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
        />
        <Form.Control.Feedback type="invalid">
          Please provide your employee number.
        </Form.Control.Feedback>
      </Form.Group>
      <Form.Group className="mb-3" controlId="formDepartment">
        <Tooltip text={showTooltips ? "Select your work department - this determines your access permissions" : null} placement="right">
          <Form.Label>Department</Form.Label>
        </Tooltip>
        <Form.Select
          name="department"
          value={formData.department}
          onChange={handleChange}
          required
          aria-describedby="department-help"
        >
          <option value="">Select Department</option>
          <option value="Engineering">Engineering</option>
          <option value="Maintenance">Maintenance</option>
          <option value="Production">Production</option>
          <option value="Quality">Quality</option>
          <option value="Materials">Materials</option>
        </Form.Select>
        <Form.Control.Feedback type="invalid">
          Please select a department.
        </Form.Control.Feedback>
        <Form.Text id="department-help" className="text-muted">
          Materials department users have additional tool management permissions.
        </Form.Text>
      </Form.Group>

      <Form.Group className="mb-3" controlId="formPassword">
        <Form.Label>Password</Form.Label>
        <Form.Control
          type="password"
          placeholder="Password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
          isInvalid={validated && !passwordValid}
        />
        <Form.Control.Feedback type="invalid">
          Please provide a valid password that meets all requirements.
        </Form.Control.Feedback>
        <PasswordStrengthMeter
          password={formData.password}
          onValidationChange={handlePasswordValidationChange}
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formConfirmPassword">
        <Form.Label>Confirm Password</Form.Label>
        <Form.Control
          type="password"
          placeholder="Confirm Password"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          isInvalid={validated && formData.password !== formData.confirmPassword}
        />
        <Form.Control.Feedback type="invalid">
          Passwords do not match.
        </Form.Control.Feedback>
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
