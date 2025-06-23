import { useState, useEffect } from 'react';
import { Modal, Button, Alert, Form, Tab, Tabs, Table, Badge, ProgressBar } from 'react-bootstrap';
import FileUpload from './FileUpload';

const BulkImportModal = ({
  show,
  onHide,
  title,
  importType, // 'tools' or 'chemicals'
  onImport,
  onDownloadTemplate,
  loading = false
}) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [selectedFile, setSelectedFile] = useState(null);
  const [skipDuplicates, setSkipDuplicates] = useState(true);
  const [validationResults, setValidationResults] = useState(null);
  const [importResults, setImportResults] = useState(null);
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState('');

  // Reset state when modal is closed
  useEffect(() => {
    if (!show) {
      setActiveTab('upload');
      setSelectedFile(null);
      setValidationResults(null);
      setImportResults(null);
      setError('');
    }
  }, [show]);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setValidationResults(null);
    setImportResults(null);
    setError('');
  };

  const handleValidate = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setValidating(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('type', importType);

      const response = await fetch('/api/bulk-import/validate', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Validation failed');
      }

      setValidationResults(data);
      setActiveTab('preview');
    } catch (err) {
      setError(err.message || 'Failed to validate file');
    } finally {
      setValidating(false);
    }
  };

  const handleImport = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('skip_duplicates', skipDuplicates.toString());

      const result = await onImport(formData);
      setImportResults(result);
      setActiveTab('results');
    } catch (err) {
      setError(err.message || 'Import failed');
    }
  };

  const handleDownloadTemplate = () => {
    if (onDownloadTemplate) {
      onDownloadTemplate();
    }
  };

  const renderUploadTab = () => (
    <div>
      <div className="mb-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h6 className="mb-0">Step 1: Download Template</h6>
          <Button
            variant="outline-primary"
            size="sm"
            onClick={handleDownloadTemplate}
          >
            <i className="bi bi-download me-2"></i>
            Download Template
          </Button>
        </div>
        <p className="text-muted small">
          Download the CSV template to see the required format and column headers.
        </p>
      </div>

      <div className="mb-4">
        <h6 className="mb-3">Step 2: Upload Your File</h6>
        <FileUpload
          onFileSelect={handleFileSelect}
          acceptedTypes=".csv"
          title="Upload CSV File"
          description="Select your CSV file with the data to import"
          disabled={loading || validating}
        />
      </div>

      <div className="mb-4">
        <h6 className="mb-3">Step 3: Import Options</h6>
        <Form.Check
          type="checkbox"
          id="skip-duplicates"
          label="Skip duplicate entries"
          checked={skipDuplicates}
          onChange={(e) => setSkipDuplicates(e.target.checked)}
          disabled={loading || validating}
        />
        <Form.Text className="text-muted">
          When enabled, duplicate entries will be skipped instead of causing errors.
        </Form.Text>
      </div>

      {error && (
        <Alert variant="danger">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
        </Alert>
      )}

      <div className="d-flex justify-content-between">
        <Button
          variant="outline-secondary"
          onClick={handleValidate}
          disabled={!selectedFile || validating || loading}
        >
          {validating ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Validating...
            </>
          ) : (
            <>
              <i className="bi bi-check-circle me-2"></i>
              Validate File
            </>
          )}
        </Button>
        <Button
          variant="primary"
          onClick={handleImport}
          disabled={!selectedFile || loading || validating}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Importing...
            </>
          ) : (
            <>
              <i className="bi bi-upload me-2"></i>
              Import Now
            </>
          )}
        </Button>
      </div>
    </div>
  );

  const renderPreviewTab = () => {
    if (!validationResults) return null;

    return (
      <div>
        <div className="mb-4">
          <h6>Validation Results</h6>
          <div className="row">
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-success">{validationResults.valid_rows}</div>
                <div className="text-muted small">Valid Rows</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-danger">{validationResults.invalid_rows}</div>
                <div className="text-muted small">Invalid Rows</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-warning">{validationResults.duplicate_rows}</div>
                <div className="text-muted small">Duplicates</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-info">{validationResults.sample_data?.length || 0}</div>
                <div className="text-muted small">Preview Rows</div>
              </div>
            </div>
          </div>
        </div>

        {validationResults.errors && validationResults.errors.length > 0 && (
          <Alert variant="danger">
            <h6>Validation Errors:</h6>
            <ul className="mb-0">
              {validationResults.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </Alert>
        )}

        {validationResults.sample_data && validationResults.sample_data.length > 0 && (
          <div>
            <h6>Data Preview (First 10 rows)</h6>
            <div className="table-responsive">
              <Table striped bordered hover size="sm">
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Status</th>
                    <th>Data</th>
                  </tr>
                </thead>
                <tbody>
                  {validationResults.sample_data.map((row, index) => (
                    <tr key={index}>
                      <td>{row.row}</td>
                      <td>
                        {row.valid ? (
                          row.is_duplicate ? (
                            <Badge bg="warning">Duplicate</Badge>
                          ) : (
                            <Badge bg="success">Valid</Badge>
                          )
                        ) : (
                          <Badge bg="danger">Invalid</Badge>
                        )}
                      </td>
                      <td>
                        {row.valid ? (
                          <small className="text-muted">
                            {JSON.stringify(row.data, null, 2).substring(0, 100)}...
                          </small>
                        ) : (
                          <small className="text-danger">{row.error}</small>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </div>
        )}

        <div className="d-flex justify-content-between mt-4">
          <Button
            variant="outline-secondary"
            onClick={() => setActiveTab('upload')}
          >
            <i className="bi bi-arrow-left me-2"></i>
            Back to Upload
          </Button>
          <Button
            variant="primary"
            onClick={handleImport}
            disabled={loading || validationResults.valid_rows === 0}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Importing...
              </>
            ) : (
              <>
                <i className="bi bi-upload me-2"></i>
                Import {validationResults.valid_rows} Valid Rows
              </>
            )}
          </Button>
        </div>
      </div>
    );
  };

  const renderResultsTab = () => {
    if (!importResults) return null;

    return (
      <div>
        <div className="mb-4">
          <h6>Import Results</h6>
          <div className="row">
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-success">{importResults.success_count}</div>
                <div className="text-muted small">Imported</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-danger">{importResults.error_count}</div>
                <div className="text-muted small">Errors</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-warning">{importResults.skipped_count}</div>
                <div className="text-muted small">Skipped</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-center">
                <div className="h4 text-info">{importResults.warning_count}</div>
                <div className="text-muted small">Warnings</div>
              </div>
            </div>
          </div>
        </div>

        {importResults.message && (
          <Alert variant={importResults.error_count > 0 ? 'warning' : 'success'}>
            {importResults.message}
          </Alert>
        )}

        {importResults.errors && importResults.errors.length > 0 && (
          <div className="mb-3">
            <h6>Errors:</h6>
            <div className="table-responsive">
              <Table striped bordered hover size="sm">
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {importResults.errors.slice(0, 10).map((error, index) => (
                    <tr key={index}>
                      <td>{error.row}</td>
                      <td className="text-danger">{error.error}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
            {importResults.errors.length > 10 && (
              <small className="text-muted">
                Showing first 10 errors. Total: {importResults.errors.length}
              </small>
            )}
          </div>
        )}

        <div className="d-flex justify-content-end mt-4">
          <Button variant="primary" onClick={onHide}>
            Close
          </Button>
        </div>
      </div>
    );
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Tabs activeKey={activeTab} onSelect={setActiveTab} className="mb-4">
          <Tab eventKey="upload" title="Upload" disabled={loading}>
            {renderUploadTab()}
          </Tab>
          <Tab eventKey="preview" title="Preview" disabled={!validationResults || loading}>
            {renderPreviewTab()}
          </Tab>
          <Tab eventKey="results" title="Results" disabled={!importResults}>
            {renderResultsTab()}
          </Tab>
        </Tabs>
      </Modal.Body>
    </Modal>
  );
};

export default BulkImportModal;
