import { Button, ButtonGroup, Spinner } from 'react-bootstrap';

const ExportControls = ({ onExport, loading, disabled }) => {
  return (
    <ButtonGroup>
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
    </ButtonGroup>
  );
};

export default ExportControls;
