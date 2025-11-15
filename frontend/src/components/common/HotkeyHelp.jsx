import { Modal, Badge, Row, Col, Button } from 'react-bootstrap';
import PropTypes from 'prop-types';
import { useSelector } from 'react-redux';
import { getHotkeysByCategory, formatHotkeyForDisplay } from '../../utils/hotkeyConfig';
import './HotkeyHelp.css';

const HotkeyHelp = ({ show, onHide }) => {
  const { user } = useSelector((state) => state.auth);
  const hotkeysByCategory = getHotkeysByCategory();

  // Filter out admin hotkeys if user is not admin
  const filteredHotkeys = Object.entries(hotkeysByCategory).reduce((acc, [category, hotkeys]) => {
    const filtered = hotkeys.filter(hotkey => {
      if (hotkey.requiresAdmin) {
        return user?.role === 'admin' || user?.isAdmin;
      }
      return true;
    });

    if (filtered.length > 0) {
      acc[category] = filtered;
    }

    return acc;
  }, {});

  return (
    <Modal
      show={show}
      onHide={onHide}
      size="lg"
      centered
      className="hotkey-help-modal"
    >
      <Modal.Header closeButton>
        <Modal.Title>
          ⌨️ Keyboard Shortcuts
        </Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <p className="text-muted mb-4">
          Speed up your workflow with these keyboard shortcuts. Press{' '}
          <kbd>{formatHotkeyForDisplay('mod+/')}</kbd> anytime to view this help.
        </p>

        {Object.entries(filteredHotkeys).map(([category, hotkeys]) => (
          <div key={category} className="hotkey-category mb-4">
            <h5 className="hotkey-category-title">{category}</h5>
            <Row className="g-2">
              {hotkeys.map((hotkey) => (
                <Col key={hotkey.name} xs={12} md={6}>
                  <div className="hotkey-item">
                    <div className="hotkey-keys">
                      <kbd className="hotkey-badge">
                        {formatHotkeyForDisplay(hotkey.key)}
                      </kbd>
                    </div>
                    <div className="hotkey-description">
                      {hotkey.description}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </div>
        ))}

        <div className="hotkey-tips mt-4 pt-3 border-top">
          <h6 className="mb-3">Tips:</h6>
          <ul className="small text-muted mb-0">
            <li>
              Most shortcuts work globally, but some only work on specific pages
            </li>
            <li>
              Single-key shortcuts (like <kbd>/</kbd> or <kbd>n</kbd>) are disabled while typing
            </li>
            <li>
              You can disable hotkeys in your profile settings
            </li>
            <li>
              Press <kbd>Esc</kbd> to close most modals and dialogs
            </li>
          </ul>
        </div>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

HotkeyHelp.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired
};

export default HotkeyHelp;
