import React, { useState, useEffect } from 'react';
import { Modal, Button, Form, Alert, Spinner, Card } from 'react-bootstrap';
import { FaDatabase, FaCheck, FaTimes, FaSync, FaCloud, FaWifi } from 'react-icons/fa';
import supabaseService from '../services/supabase.js';
import syncService from '../services/syncService.js';

const SupabaseConfig = ({ show, onHide, onConfigured }) => {
  const [config, setConfig] = useState({ url: '', key: '' });
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);

  useEffect(() => {
    if (show) {
      loadCurrentConfig();
      updateSyncStatus();
    }
  }, [show]);

  useEffect(() => {
    // Listen for sync events
    const handleSyncComplete = (event) => {
      setSyncStatus({
        type: 'success',
        message: `Sync completed at ${new Date(event.detail.timestamp).toLocaleTimeString()}`
      });
    };

    const handleSyncError = (event) => {
      setSyncStatus({
        type: 'error',
        message: `Sync failed: ${event.detail.error}`
      });
    };

    window.addEventListener('syncComplete', handleSyncComplete);
    window.addEventListener('syncError', handleSyncError);

    return () => {
      window.removeEventListener('syncComplete', handleSyncComplete);
      window.removeEventListener('syncError', handleSyncError);
    };
  }, []);

  const loadCurrentConfig = async () => {
    try {
      const currentConfig = supabaseService.getConfig();
      setConfig(currentConfig);
      
      if (currentConfig.url && currentConfig.key) {
        setConnectionStatus(supabaseService.isReady() ? 'connected' : 'disconnected');
      }
    } catch (error) {
      console.error('Failed to load current config:', error);
    }
  };

  const updateSyncStatus = () => {
    const status = syncService.getStatus();
    setSyncStatus({
      type: 'info',
      message: `Online: ${status.isOnline ? 'Yes' : 'No'} | Last sync: ${
        status.lastSyncTime ? new Date(status.lastSyncTime).toLocaleString() : 'Never'
      } | Queue: ${status.queueLength} items`
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setConfig(prev => ({ ...prev, [name]: value }));
    setError('');
    setSuccess('');
  };

  const testConnection = async () => {
    if (!config.url || !config.key) {
      setError('Please enter both URL and API key');
      return;
    }

    setTesting(true);
    setError('');
    setConnectionStatus(null);

    try {
      await supabaseService.configure(config.url, config.key);
      const isConnected = await supabaseService.testConnection();
      
      if (isConnected) {
        setConnectionStatus('connected');
        setSuccess('Connection successful!');
      } else {
        setConnectionStatus('failed');
        setError('Connection test failed. Please check your URL and API key.');
      }
    } catch (error) {
      setConnectionStatus('failed');
      setError(`Connection failed: ${error.message}`);
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!config.url || !config.key) {
      setError('Please enter both URL and API key');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await supabaseService.configure(config.url, config.key);
      const isConnected = await supabaseService.testConnection();
      
      if (isConnected) {
        // Initialize sync service
        await syncService.initialize();
        
        setSuccess('Configuration saved successfully!');
        setTimeout(() => {
          onConfigured && onConfigured();
          onHide();
        }, 1500);
      } else {
        setError('Configuration saved but connection test failed. Please verify your settings.');
      }
    } catch (error) {
      setError(`Failed to save configuration: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleForceSync = async () => {
    try {
      setLoading(true);
      await syncService.forceSync();
      setSuccess('Manual sync completed successfully!');
      updateSyncStatus();
    } catch (error) {
      setError(`Sync failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <FaCheck className="text-success" />;
      case 'failed':
        return <FaTimes className="text-danger" />;
      default:
        return <FaDatabase className="text-muted" />;
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>
          <FaCloud className="me-2" />
          Supabase Configuration
        </Modal.Title>
      </Modal.Header>
      
      <Modal.Body>
        <div className="mb-4">
          <Card className="border-0 bg-light">
            <Card.Body className="py-2">
              <div className="d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center">
                  {getConnectionIcon()}
                  <span className="ms-2">
                    Connection Status: {
                      connectionStatus === 'connected' ? 'Connected' :
                      connectionStatus === 'failed' ? 'Failed' : 'Not tested'
                    }
                  </span>
                </div>
                <div className="d-flex align-items-center">
                  <FaWifi className={`me-2 ${navigator.onLine ? 'text-success' : 'text-danger'}`} />
                  <span>{navigator.onLine ? 'Online' : 'Offline'}</span>
                </div>
              </div>
            </Card.Body>
          </Card>
        </div>

        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
        
        {syncStatus && (
          <Alert variant={syncStatus.type === 'error' ? 'warning' : 'info'}>
            <FaSync className="me-2" />
            {syncStatus.message}
          </Alert>
        )}

        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Supabase URL</Form.Label>
            <Form.Control
              type="url"
              name="url"
              value={config.url}
              onChange={handleInputChange}
              placeholder="https://your-project.supabase.co"
              disabled={loading || testing}
            />
            <Form.Text className="text-muted">
              Your Supabase project URL (found in project settings)
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Supabase API Key</Form.Label>
            <Form.Control
              type="password"
              name="key"
              value={config.key}
              onChange={handleInputChange}
              placeholder="Your anon/public API key"
              disabled={loading || testing}
            />
            <Form.Text className="text-muted">
              Your Supabase anon/public API key (found in project settings)
            </Form.Text>
          </Form.Group>

          <div className="d-flex gap-2 mb-3">
            <Button
              variant="outline-primary"
              onClick={testConnection}
              disabled={loading || testing || !config.url || !config.key}
            >
              {testing ? (
                <>
                  <Spinner size="sm" className="me-2" />
                  Testing...
                </>
              ) : (
                <>
                  <FaDatabase className="me-2" />
                  Test Connection
                </>
              )}
            </Button>

            {supabaseService.isReady() && (
              <Button
                variant="outline-secondary"
                onClick={handleForceSync}
                disabled={loading || !navigator.onLine}
              >
                <FaSync className="me-2" />
                Force Sync
              </Button>
            )}
          </div>
        </Form>

        <Card className="border-0 bg-light">
          <Card.Body className="py-2">
            <h6 className="mb-2">Configuration Help</h6>
            <ul className="mb-0 small">
              <li>Get your Supabase URL and API key from your project settings</li>
              <li>Use the "anon" or "public" API key, not the service role key</li>
              <li>The app will sync data automatically when online</li>
              <li>Data is stored locally for offline access</li>
            </ul>
          </Card.Body>
        </Card>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onHide} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={loading || testing || !config.url || !config.key}
        >
          {loading ? (
            <>
              <Spinner size="sm" className="me-2" />
              Saving...
            </>
          ) : (
            'Save Configuration'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default SupabaseConfig;
