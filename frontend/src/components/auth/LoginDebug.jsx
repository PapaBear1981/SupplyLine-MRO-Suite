import { useState } from 'react';
import { Button, Form, Alert, Card, Row, Col } from 'react-bootstrap';
import axios from 'axios';

const LoginDebug = () => {
  const [username, setUsername] = useState('ADMIN001');
  const [password, setPassword] = useState('admin123');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleDirectLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('Attempting direct login with:', { employee_number: username, password });

      const response = await axios.post('/api/auth/login', {
        employee_number: username,
        password
      }, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Login response:', response.data);
      setResult(response.data);

      // Check auth status
      setTimeout(async () => {
        try {
          const statusResponse = await axios.get('/api/auth/status', {
            withCredentials: true
          });
          console.log('Auth status:', statusResponse.data);
          setResult(prev => ({ ...prev, authStatus: statusResponse.data }));
        } catch (statusError) {
          console.error('Error checking auth status:', statusError);
          setError(statusError.message);
        }
      }, 1000);
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      console.log('Attempting logout');

      const response = await axios.post('/api/auth/logout', {}, {
        withCredentials: true
      });

      console.log('Logout response:', response.data);
      setResult({ message: 'Logged out successfully' });

      // Check auth status after logout
      setTimeout(async () => {
        try {
          const statusResponse = await axios.get('/api/auth/status', {
            withCredentials: true
          });
          console.log('Auth status after logout:', statusResponse.data);
          setResult(prev => ({ ...prev, authStatus: statusResponse.data }));
        } catch (statusError) {
          console.error('Error checking auth status:', statusError);
          setError(statusError.message);
        }
      }, 1000);
    } catch (err) {
      console.error('Logout error:', err);
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  const checkAuthStatus = async () => {
    setLoading(true);
    setError(null);

    try {
      const statusResponse = await axios.get('/api/auth/status', {
        withCredentials: true
      });
      console.log('Current auth status:', statusResponse.data);
      setResult({ authStatus: statusResponse.data });
    } catch (err) {
      console.error('Error checking auth status:', err);
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mt-4">
      <Card.Header className="bg-warning">
        <h4>Debug Login</h4>
      </Card.Header>
      <Card.Body>
        <Form onSubmit={handleDirectLogin}>
          <Form.Group className="mb-3">
            <Form.Label>Employee Number</Form.Label>
            <Form.Control
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </Form.Group>

          <Row className="mb-3">
            <Col>
              <Button
                variant="warning"
                type="submit"
                disabled={loading}
                className="w-100"
              >
                {loading ? 'Testing Login...' : 'Test Direct Login'}
              </Button>
            </Col>
            <Col>
              <Button
                variant="danger"
                onClick={handleLogout}
                disabled={loading}
                className="w-100"
              >
                Logout
              </Button>
            </Col>
            <Col>
              <Button
                variant="info"
                onClick={checkAuthStatus}
                disabled={loading}
                className="w-100"
              >
                Check Status
              </Button>
            </Col>
          </Row>
        </Form>

        {error && (
          <Alert variant="danger" className="mt-3">
            <strong>Error:</strong> {error}
          </Alert>
        )}

        {result && (
          <div className="mt-3">
            <h5>Result:</h5>
            <pre className="bg-light p-3 rounded">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default LoginDebug;
