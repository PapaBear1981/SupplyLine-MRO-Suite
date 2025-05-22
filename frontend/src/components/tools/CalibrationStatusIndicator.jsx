import { Badge, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCheckCircle, 
  faExclamationTriangle, 
  faClock, 
  faTimesCircle,
  faCertificate
} from '@fortawesome/free-solid-svg-icons';

const CalibrationStatusIndicator = ({ tool, showText = true, size = 'sm' }) => {
  if (!tool.requires_calibration) {
    const tooltip = (
      <Tooltip>
        This tool does not require calibration
      </Tooltip>
    );

    return (
      <OverlayTrigger placement="top" overlay={tooltip}>
        <Badge bg="secondary" className={`calibration-status-badge ${size}`}>
          <FontAwesomeIcon icon={faTimesCircle} className={showText ? "me-1" : ""} />
          {showText && "N/A"}
        </Badge>
      </OverlayTrigger>
    );
  }

  const getStatusInfo = () => {
    const now = new Date();
    const nextCalDate = tool.next_calibration_date ? new Date(tool.next_calibration_date) : null;
    const lastCalDate = tool.last_calibration_date ? new Date(tool.last_calibration_date) : null;

    switch (tool.calibration_status) {
      case 'current':
        return {
          variant: 'success',
          icon: faCheckCircle,
          text: 'Current',
          tooltip: `Calibration is current. ${nextCalDate ? `Next due: ${nextCalDate.toLocaleDateString()}` : ''}`
        };
      
      case 'due_soon':
        const daysUntilDue = nextCalDate ? Math.ceil((nextCalDate - now) / (1000 * 60 * 60 * 24)) : null;
        return {
          variant: 'warning',
          icon: faClock,
          text: daysUntilDue ? `Due in ${daysUntilDue}d` : 'Due Soon',
          tooltip: `Calibration due soon. ${nextCalDate ? `Due date: ${nextCalDate.toLocaleDateString()}` : ''}`
        };
      
      case 'overdue':
        const daysOverdue = nextCalDate ? Math.ceil((now - nextCalDate) / (1000 * 60 * 60 * 24)) : null;
        return {
          variant: 'danger',
          icon: faExclamationTriangle,
          text: daysOverdue ? `${daysOverdue}d overdue` : 'Overdue',
          tooltip: `Calibration is overdue! ${nextCalDate ? `Was due: ${nextCalDate.toLocaleDateString()}` : ''}`
        };
      
      case 'never_calibrated':
        return {
          variant: 'warning',
          icon: faCertificate,
          text: 'Never Cal.',
          tooltip: 'This tool has never been calibrated and requires initial calibration'
        };
      
      default:
        return {
          variant: 'secondary',
          icon: faTimesCircle,
          text: 'Unknown',
          tooltip: 'Calibration status unknown'
        };
    }
  };

  const statusInfo = getStatusInfo();

  const tooltip = (
    <Tooltip>
      {statusInfo.tooltip}
      {tool.last_calibration_date && (
        <div className="mt-1">
          Last calibrated: {new Date(tool.last_calibration_date).toLocaleDateString()}
        </div>
      )}
    </Tooltip>
  );

  return (
    <OverlayTrigger placement="top" overlay={tooltip}>
      <Badge 
        bg={statusInfo.variant} 
        className={`calibration-status-badge ${size} ${statusInfo.variant === 'danger' ? 'pulse' : ''}`}
      >
        <FontAwesomeIcon icon={statusInfo.icon} className={showText ? "me-1" : ""} />
        {showText && statusInfo.text}
      </Badge>
    </OverlayTrigger>
  );
};

export default CalibrationStatusIndicator;
