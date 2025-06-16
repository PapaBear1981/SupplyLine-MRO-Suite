import { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import AuthService from '../../services/authService';

const SystemSettings = () => {
  const [settings, setSettings] = useState({
    companyName: 'SupplyLine MRO Suite',
    defaultDepartment: 'Maintenance',
    toolCheckoutDuration: 7,
    enableNotifications: true,
    enableAuditLogging: true,
    enableUserActivity: true,
    enableChemicalAlerts: true,
    enableToolCalibrationAlerts: true,
    chemicalExpiryThreshold: 30,
    calibrationDueThreshold: 14,
    // Auto logout settings
    autoLogoutTimeout: 30,
    enableAutoLogout: true,
    logoutOnWindowClose: true,
    showLogoutWarning: true,
    logoutWarningMinutes: 5
  });

  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load settings on component mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await AuthService.getSystemSettings();

      // Convert settings from grouped format to flat format
      const flatSettings = {};
      Object.values(response).flat().forEach(setting => {
        flatSettings[setting.key] = setting.value;
      });

      // Merge with default settings
      setSettings(prevSettings => ({
        ...prevSettings,
        ...flatSettings
      }));
    } catch (err) {
      console.error('Failed to load settings:', err);
      setError('Failed to load settings. Using defaults.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? Number(value) : value)
    });
    setSaved(false);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Convert settings to the format expected by the backend
      const settingsToSave = {
        company_name: {
          value: settings.companyName,
          value_type: 'string',
          description: 'Company name displayed in the application',
          category: 'general'
        },
        default_department: {
          value: settings.defaultDepartment,
          value_type: 'string',
          description: 'Default department for new users',
          category: 'general'
        },
        tool_checkout_duration: {
          value: settings.toolCheckoutDuration,
          value_type: 'integer',
          description: 'Default tool checkout duration in days',
          category: 'tools'
        },
        auto_logout_timeout: {
          value: settings.autoLogoutTimeout,
          value_type: 'integer',
          description: 'Auto logout timeout in minutes',
          category: 'security'
        },
        enable_auto_logout: {
          value: settings.enableAutoLogout,
          value_type: 'boolean',
          description: 'Enable automatic logout on inactivity',
          category: 'security'
        },
        logout_on_window_close: {
          value: settings.logoutOnWindowClose,
          value_type: 'boolean',
          description: 'Automatically logout when browser window is closed',
          category: 'security'
        },
        show_logout_warning: {
          value: settings.showLogoutWarning,
          value_type: 'boolean',
          description: 'Show warning before automatic logout',
          category: 'security'
        },
        logout_warning_minutes: {
          value: settings.logoutWarningMinutes,
          value_type: 'integer',
          description: 'Minutes before logout to show warning',
          category: 'security'
        },
        enable_notifications: {
          value: settings.enableNotifications,
          value_type: 'boolean',
          description: 'Enable system notifications',
          category: 'notifications'
        },
        enable_audit_logging: {
          value: settings.enableAuditLogging,
          value_type: 'boolean',
          description: 'Enable audit logging',
          category: 'security'
        },
        enable_user_activity: {
          value: settings.enableUserActivity,
          value_type: 'boolean',
          description: 'Track user activity',
          category: 'security'
        },
        enable_chemical_alerts: {
          value: settings.enableChemicalAlerts,
          value_type: 'boolean',
          description: 'Enable chemical expiry alerts',
          category: 'chemicals'
        },
        enable_tool_calibration_alerts: {
          value: settings.enableToolCalibrationAlerts,
          value_type: 'boolean',
          description: 'Enable tool calibration alerts',
          category: 'tools'
        },
        chemical_expiry_threshold: {
          value: settings.chemicalExpiryThreshold,
          value_type: 'integer',
          description: 'Days before chemical expiry to show alerts',
          category: 'chemicals'
        },
        calibration_due_threshold: {
          value: settings.calibrationDueThreshold,
          value_type: 'integer',
          description: 'Days before calibration due to show alerts',
          category: 'tools'
        }
      };

      await AuthService.updateSystemSettings(settingsToSave);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
      setError('Failed to save settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3 className="mb-4">System Settings</h3>

      {saved && (
        <Alert variant="success" className="mb-4">
          Settings saved successfully!
        </Alert>
      )}

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}

      <Card>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <h5 className="mb-3">General Settings</h5>
            
            <Form.Group className="mb-3">
              <Form.Label>Company Name</Form.Label>
              <Form.Control
                type="text"
                name="companyName"
                value={settings.companyName}
                onChange={handleChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Default Department</Form.Label>
              <Form.Control
                type="text"
                name="defaultDepartment"
                value={settings.defaultDepartment}
                onChange={handleChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Default Tool Checkout Duration (days)</Form.Label>
              <Form.Control
                type="number"
                name="toolCheckoutDuration"
                value={settings.toolCheckoutDuration}
                onChange={handleChange}
                min="1"
                max="365"
              />
            </Form.Group>
            
            <hr className="my-4" />
            
            <h5 className="mb-3">Notifications & Alerts</h5>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="enableNotifications"
                name="enableNotifications"
                label="Enable System Notifications"
                checked={settings.enableNotifications}
                onChange={handleChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="enableChemicalAlerts"
                name="enableChemicalAlerts"
                label="Enable Chemical Expiry Alerts"
                checked={settings.enableChemicalAlerts}
                onChange={handleChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Chemical Expiry Alert Threshold (days)</Form.Label>
              <Form.Control
                type="number"
                name="chemicalExpiryThreshold"
                value={settings.chemicalExpiryThreshold}
                onChange={handleChange}
                min="1"
                max="90"
                disabled={!settings.enableChemicalAlerts}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="enableToolCalibrationAlerts"
                name="enableToolCalibrationAlerts"
                label="Enable Tool Calibration Due Alerts"
                checked={settings.enableToolCalibrationAlerts}
                onChange={handleChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Calibration Due Alert Threshold (days)</Form.Label>
              <Form.Control
                type="number"
                name="calibrationDueThreshold"
                value={settings.calibrationDueThreshold}
                onChange={handleChange}
                min="1"
                max="90"
                disabled={!settings.enableToolCalibrationAlerts}
              />
            </Form.Group>
              </Col>

              <Col md={6}>
                <h5 className="mb-3">Security Settings</h5>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    id="enableAutoLogout"
                    name="enableAutoLogout"
                    label="Enable Auto Logout"
                    checked={settings.enableAutoLogout}
                    onChange={handleChange}
                  />
                  <Form.Text className="text-muted">
                    Automatically log users out after a period of inactivity
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Auto Logout Timeout (minutes)</Form.Label>
                  <Form.Control
                    type="number"
                    name="autoLogoutTimeout"
                    value={settings.autoLogoutTimeout}
                    onChange={handleChange}
                    min="5"
                    max="480"
                    disabled={!settings.enableAutoLogout}
                  />
                  <Form.Text className="text-muted">
                    Time in minutes before automatic logout (5-480 minutes)
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    id="showLogoutWarning"
                    name="showLogoutWarning"
                    label="Show Logout Warning"
                    checked={settings.showLogoutWarning}
                    onChange={handleChange}
                    disabled={!settings.enableAutoLogout}
                  />
                  <Form.Text className="text-muted">
                    Show warning before automatic logout
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Warning Time (minutes before logout)</Form.Label>
                  <Form.Control
                    type="number"
                    name="logoutWarningMinutes"
                    value={settings.logoutWarningMinutes}
                    onChange={handleChange}
                    min="1"
                    max="30"
                    disabled={!settings.enableAutoLogout || !settings.showLogoutWarning}
                  />
                  <Form.Text className="text-muted">
                    Minutes before logout to show warning (1-30 minutes)
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Check
                    type="switch"
                    id="logoutOnWindowClose"
                    name="logoutOnWindowClose"
                    label="Logout on Window Close"
                    checked={settings.logoutOnWindowClose}
                    onChange={handleChange}
                  />
                  <Form.Text className="text-muted">
                    Automatically logout when browser window is closed
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <hr className="my-4" />

            <h5 className="mb-3">System Logging</h5>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="enableAuditLogging"
                name="enableAuditLogging"
                label="Enable Audit Logging"
                checked={settings.enableAuditLogging}
                onChange={handleChange}
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="enableUserActivity"
                name="enableUserActivity"
                label="Track User Activity"
                checked={settings.enableUserActivity}
                onChange={handleChange}
              />
            </Form.Group>
            
            <div className="d-grid gap-2 d-md-flex justify-content-md-end">
              <Button variant="primary" type="submit" disabled={loading}>
                {loading ? 'Saving...' : 'Save Settings'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default SystemSettings;
