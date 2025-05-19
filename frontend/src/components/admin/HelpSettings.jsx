import { useState } from 'react';
import { Card, Form, Button, Alert } from 'react-bootstrap';
import { useHelp } from '../../context/HelpContext';

/**
 * Component for managing help and tooltip settings in the admin dashboard
 */
const HelpSettings = () => {
  const { showHelp, showTooltips, savePreferences } = useHelp();
  const [localShowHelp, setLocalShowHelp] = useState(showHelp);
  const [localShowTooltips, setLocalShowTooltips] = useState(showTooltips);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    savePreferences(localShowHelp, localShowTooltips);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Help & Tooltip Settings</h5>
      </Card.Header>
      <Card.Body>
        {saved && (
          <Alert variant="success" className="mb-3">
            Settings saved successfully!
          </Alert>
        )}
        
        <Form>
          <Form.Group className="mb-3">
            <Form.Check 
              type="switch"
              id="show-help"
              label="Show contextual help throughout the application"
              checked={localShowHelp}
              onChange={(e) => setLocalShowHelp(e.target.checked)}
            />
            <Form.Text className="text-muted">
              When enabled, help icons and collapsible help sections will be displayed throughout the application.
            </Form.Text>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Check 
              type="switch"
              id="show-tooltips"
              label="Show tooltips on hover"
              checked={localShowTooltips}
              onChange={(e) => setLocalShowTooltips(e.target.checked)}
            />
            <Form.Text className="text-muted">
              When enabled, tooltips will be displayed when hovering over buttons, icons, and other UI elements.
            </Form.Text>
          </Form.Group>
          
          <Button variant="primary" onClick={handleSave}>
            Save Settings
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default HelpSettings;
