import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { fetchSecuritySettings, updateSessionTimeout, clearUpdateSuccess } from '../../store/securitySlice';

const SystemSettings = () => {
  const dispatch = useDispatch();
  const {
    sessionTimeoutMinutes,
    defaultTimeoutMinutes,
    minTimeoutMinutes,
    maxTimeoutMinutes,
    loading: securityLoading,
    error: securityError,
    saving: securitySaving,
    saveError: securitySaveError,
    updateSuccess,
    updatedAt,
    updatedBy,
    hasLoaded: securityLoaded,
  } = useSelector((state) => state.security);

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
  const [timeoutValue, setTimeoutValue] = useState(String(sessionTimeoutMinutes));
  const [securityValidationError, setSecurityValidationError] = useState('');

  const formattedUpdatedAt = useMemo(() => {
    if (!updatedAt) {
      return null;
    }

    try {
      return new Date(updatedAt).toLocaleString();
    } catch (_error) {
      return updatedAt;
    }
  }, [updatedAt]);

  useEffect(() => {
    if (!securityLoaded && !securityLoading) {
      dispatch(fetchSecuritySettings());
    }
  }, [dispatch, securityLoaded, securityLoading]);

  useEffect(() => {
    setTimeoutValue(String(sessionTimeoutMinutes));
  }, [sessionTimeoutMinutes]);

  useEffect(() => {
    let timer;
    if (updateSuccess) {
      timer = setTimeout(() => {
        dispatch(clearUpdateSuccess());
      }, 4000);
    }

    return () => {
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [dispatch, updateSuccess]);

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

  const handleSecuritySubmit = (e) => {
    e.preventDefault();

    if (securityLoading || !securityLoaded) {
      return;
    }

    const minutes = parseInt(timeoutValue, 10);
    if (Number.isNaN(minutes)) {
      setSecurityValidationError('Please enter a valid number of minutes.');
      return;
    }

    if (minutes < minTimeoutMinutes || minutes > maxTimeoutMinutes) {
      setSecurityValidationError(
        `Timeout must be between ${minTimeoutMinutes} and ${maxTimeoutMinutes} minutes.`,
      );
      return;
    }

    setSecurityValidationError('');
    dispatch(updateSessionTimeout(minutes));
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

            <h5 className="mb-3">Security Settings</h5>

            {securityLoading && !securityLoaded && (
              <Alert variant="info" className="mb-3">
                Loading security settings...
              </Alert>
            )}

            {securityError && !securityLoading && (
              <Alert variant="danger" className="mb-3">
                {securityError.error || securityError.message || 'Unable to load security settings.'}
              </Alert>
            )}

            {securitySaveError && (
              <Alert variant="danger" className="mb-3">
                {securitySaveError.error || securitySaveError.message || 'Failed to update security settings.'}
              </Alert>
            )}

            {securityValidationError && (
              <Alert variant="warning" className="mb-3">
                {securityValidationError}
              </Alert>
            )}

            {updateSuccess && (
              <Alert variant="success" className="mb-3">
                Session inactivity timeout updated successfully.
              </Alert>
            )}

            <Form.Group className="mb-3">
              <Form.Label>Session Inactivity Timeout (minutes)</Form.Label>
              <Form.Control
                type="number"
                value={timeoutValue}
                min={minTimeoutMinutes}
                max={maxTimeoutMinutes}
                onChange={(e) => {
                  setTimeoutValue(e.target.value);
                  if (securityValidationError) {
                    setSecurityValidationError('');
                  }
                }}
                disabled={securitySaving || securityLoading || !securityLoaded || !!securityError}
              />
              <Form.Text className="text-muted">
                Current effective timeout: {sessionTimeoutMinutes} minute
                {sessionTimeoutMinutes === 1 ? '' : 's'}. Allowed range: {minTimeoutMinutes}–
                {maxTimeoutMinutes} minutes. Default: {defaultTimeoutMinutes} minute
                {defaultTimeoutMinutes === 1 ? '' : 's'}.
              </Form.Text>
            </Form.Group>

            <div className="d-flex align-items-center mb-3">
              <Button
                variant="primary"
                type="button"
                onClick={handleSecuritySubmit}
                disabled={securitySaving || securityLoading || !securityLoaded || !!securityError}
              >
                {securitySaving ? 'Saving...' : 'Update Security Settings'}
              </Button>
              {securitySaving && (
                <Spinner animation="border" role="status" size="sm" className="ms-2">
                  <span className="visually-hidden">Saving...</span>
                </Spinner>
              )}
            </div>

            {formattedUpdatedAt && (
              <p className="text-muted small mb-0">
                Last updated {formattedUpdatedAt}
                {updatedBy?.name ? ` by ${updatedBy.name}` : ''}.
              </p>
            )}

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
