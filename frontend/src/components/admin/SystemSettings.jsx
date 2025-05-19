import { useState } from 'react';
import { Card, Form, Button, Alert } from 'react-bootstrap';

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
    calibrationDueThreshold: 14
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value
    });
    setSaved(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real implementation, this would save to the backend
    console.log('Saving settings:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div>
      <h3 className="mb-4">System Settings</h3>
      
      {saved && (
        <Alert variant="success" className="mb-4">
          Settings saved successfully!
        </Alert>
      )}
      
      <Card>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
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
              <Button variant="primary" type="submit">
                Save Settings
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default SystemSettings;
