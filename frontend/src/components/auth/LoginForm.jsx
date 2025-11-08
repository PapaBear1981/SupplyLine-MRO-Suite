import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import { Eye, EyeSlash } from 'react-bootstrap-icons';
import { login } from '../../store/authSlice';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [validated, setValidated] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <Form noValidate validated={validated} onSubmit={handleSubmit}>
      {error && (
        <div className="login-alert login-alert-danger">
          {error.message || error.error || 'Login failed. Please try again.'}
        </div>
      )}

      <div className="login-form-group">
        <label htmlFor="formUsername" className="login-form-label">
          Employee Number
        </label>
        <div className="login-input-wrapper">
          <input
            id="formUsername"
            type="text"
            className={`login-form-control ${validated && !username ? 'is-invalid' : ''}`}
            placeholder="Enter your employee number"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
          />
        </div>
        {validated && !username && (
          <div className="invalid-feedback d-block" style={{ color: '#ff6b6b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Please provide your employee number.
          </div>
        )}
      </div>

      <div className="login-form-group">
        <label htmlFor="formPassword" className="login-form-label">
          Password
        </label>
        <div className="login-input-wrapper">
          <input
            id="formPassword"
            type={showPassword ? 'text' : 'password'}
            className={`login-form-control ${validated && !password ? 'is-invalid' : ''}`}
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            style={{ paddingRight: '3rem' }}
          />
          <button
            type="button"
            className="password-toggle-btn"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeSlash size={20} /> : <Eye size={20} />}
          </button>
        </div>
        {validated && !password && (
          <div className="invalid-feedback d-block" style={{ color: '#ff6b6b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Please provide a password.
          </div>
        )}
      </div>

      <div className="login-checkbox-wrapper">
        <input
          id="formRememberMe"
          type="checkbox"
          className="login-checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
        />
        <label htmlFor="formRememberMe" className="login-checkbox-label">
          Remember me
        </label>
      </div>

      <button
        type="submit"
        className="login-submit-btn"
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="login-spinner"></span>
            <span>Logging in...</span>
          </>
        ) : (
          'Login'
        )}
      </button>
    </Form>
  );
};

export default LoginForm;
