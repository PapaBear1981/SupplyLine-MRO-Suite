import { OverlayTrigger, Tooltip as BSTooltip } from 'react-bootstrap';

/**
 * A reusable tooltip component that wraps any element with a Bootstrap tooltip.
 *
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - The element to wrap with a tooltip
 * @param {string} props.text - The tooltip text to display
 * @param {string} props.placement - The placement of the tooltip (top, bottom, left, right)
 * @param {string} props.delay - Delay in ms before showing the tooltip
 * @param {string} props.className - Additional CSS classes for the wrapper
 * @returns {React.ReactElement} - The wrapped element with a tooltip
 */
const Tooltip = ({
  children,
  text,
  placement = 'top',
  delay = 200,
  className = ''
}) => {
  if (!text) return children;

  return (
    <OverlayTrigger
      placement={placement}
      delay={{ show: delay, hide: 0 }}
      overlay={
        <BSTooltip id={`tooltip-${text.substring(0, 10).replace(/[^\w-]/g, '-')}-${Math.random().toString(36).substr(2, 5)}`}>
          {text}
        </BSTooltip>
      }
    >
      <span
        className={className}
        style={{ display: 'inline-block' }}
        tabIndex={0}
        aria-label={text}
      >
        {children}
      </span>
    </OverlayTrigger>
  );
};

export default Tooltip;
