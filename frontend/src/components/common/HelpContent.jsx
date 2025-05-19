import { useState } from 'react';
import { Card, Button, Collapse } from 'react-bootstrap';
import './Help.css';

/**
 * A collapsible help content component that displays detailed help information.
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - The title of the help content
 * @param {React.ReactNode} props.children - The help content to display
 * @param {boolean} props.initialOpen - Whether the help content is initially open
 * @param {string} props.className - Additional CSS classes for the help content
 * @returns {React.ReactElement} - The collapsible help content
 */
const HelpContent = ({
  title = 'Help & Information',
  children,
  initialOpen = false,
  className = ''
}) => {
  const [open, setOpen] = useState(initialOpen);

  return (
    <Card className={`mb-3 help-section ${className}`}>
      <Card.Header className="d-flex justify-content-between align-items-center bg-light">
        <h5 className="mb-0">{title}</h5>
        <Button
          onClick={() => setOpen(!open)}
          variant="link"
          className="p-0 text-decoration-none"
          aria-expanded={open}
          aria-controls="help-content-collapse"
        >
          {open ? (
            <>
              <i className="bi bi-chevron-up me-1"></i>
              Hide
            </>
          ) : (
            <>
              <i className="bi bi-chevron-down me-1"></i>
              Show
            </>
          )}
        </Button>
      </Card.Header>
      <Collapse in={open}>
        <div id="help-content-collapse">
          <Card.Body>{children}</Card.Body>
        </div>
      </Collapse>
    </Card>
  );
};

export default HelpContent;
