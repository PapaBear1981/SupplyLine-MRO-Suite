import { Button, ButtonGroup, Spinner } from 'react-bootstrap';
import Tooltip from '../common/Tooltip';
import { useHelp } from '../../context/HelpContext';

const ExportControls = ({ onExport, loading, disabled }) => {
  const { showTooltips } = useHelp();
  return (
    <ButtonGroup>
      <Tooltip text="Export report as PDF document" placement="top" show={showTooltips}>
        <Button
          variant="outline-primary"
          onClick={() => onExport('pdf')}
          disabled={disabled || loading}
        >
          {loading ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-2"
              />
              Exporting...
            </>
          ) : (
            <>
              <i className="bi bi-file-earmark-pdf me-2"></i>
              Export PDF
            </>
          )}
        </Button>
      </Tooltip>
      <Tooltip text="Export report as Excel spreadsheet" placement="top" show={showTooltips}>
        <Button
          variant="outline-success"
          onClick={() => onExport('excel')}
          disabled={disabled || loading}
        >
          {loading ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
                className="me-2"
              />
              Exporting...
            </>
          ) : (
            <>
              <i className="bi bi-file-earmark-excel me-2"></i>
              Export Excel
            </>
          )}
        </Button>
      </Tooltip>
    </ButtonGroup>
  );
};

export default ExportControls;
