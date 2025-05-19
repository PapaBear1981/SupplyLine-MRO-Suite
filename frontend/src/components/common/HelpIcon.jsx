import { useState } from 'react';
import { OverlayTrigger, Popover, Button } from 'react-bootstrap';

/**
 * A help icon component that displays detailed help content in a popover when clicked.
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - The title of the help content
 * @param {React.ReactNode} props.content - The help content to display
 * @param {string} props.placement - The placement of the popover (top, bottom, left, right)
 * @param {string} props.variant - The variant of the help icon (primary, secondary, etc.)
 * @param {string} props.size - The size of the help icon (sm, md, lg)
 * @param {string} props.className - Additional CSS classes for the help icon
 * @returns {React.ReactElement} - The help icon with a popover
 */
const HelpIcon = ({
  title,
  content,
  placement = 'right',
  variant = 'outline-info',
  size = 'sm',
  className = ''
}) => {
  const [show, setShow] = useState(false);

  const popover = (
    <Popover id={`popover-${title?.replace(/\s/g, '-') || 'help'}`} className="help-popover">
      {title && <Popover.Header as="h3">{title}</Popover.Header>}
      <Popover.Body>
        {content}
      </Popover.Body>
    </Popover>
  );

  return (
    <OverlayTrigger
      trigger="click"
      placement={placement}
      overlay={popover}
      show={show}
      onToggle={(nextShow) => setShow(nextShow)}
      rootClose
    >
      <Button 
        variant={variant} 
        size={size} 
        className={`rounded-circle help-icon ${className}`}
        style={{ width: size === 'sm' ? '24px' : size === 'lg' ? '36px' : '30px', height: size === 'sm' ? '24px' : size === 'lg' ? '36px' : '30px', padding: 0 }}
        aria-label="Help"
      >
        <i className="bi bi-question"></i>
      </Button>
    </OverlayTrigger>
  );
};

export default HelpIcon;
