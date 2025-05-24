import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, Form, Alert, Spinner, Modal, Row, Col, ButtonGroup, Dropdown } from 'react-bootstrap';
import {
  exportCycleCountBatch,
  exportCycleCountSchedule,
  exportCycleCountResults,
  importCycleCountResults,
  importCycleCountSchedules,
  importCycleCountBatches
} from '../../store/cycleCountSlice';

const CycleCountExportImport = ({
  batchId,
  batchName,
  scheduleId,
  scheduleName,
  mode = 'batch', // 'batch', 'schedule', 'results'
  onImportSuccess
}) => {
  const dispatch = useDispatch();
  const { loading: exportLoading, error: exportError } = useSelector((state) => state.cycleCount.export);
  const { loading: importLoading, error: importError, result: importResult } = useSelector((state) => state.cycleCount.import);

  const [showImportModal, setShowImportModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [importType, setImportType] = useState('results'); // 'results', 'schedules', 'batches'
  const [exportFilters, setExportFilters] = useState({
    start_date: '',
    end_date: '',
    discrepancies_only: false
  });

  const handleExport = (format = 'csv') => {
    if (mode === 'batch' && batchId) {
      dispatch(exportCycleCountBatch({ batchId, format }));
    } else if (mode === 'schedule' && scheduleId) {
      dispatch(exportCycleCountSchedule({ scheduleId, format }));
    } else if (mode === 'results') {
      dispatch(exportCycleCountResults({ filters: exportFilters, format }));
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
  };

  const handleImport = () => {
    if (!selectedFile) {
      return;
    }

    let importAction;
    if (importType === 'results' && batchId) {
      importAction = importCycleCountResults({ batchId, file: selectedFile });
    } else if (importType === 'schedules') {
      importAction = importCycleCountSchedules({ file: selectedFile });
    } else if (importType === 'batches') {
      importAction = importCycleCountBatches({ file: selectedFile });
    } else {
      return;
    }

    dispatch(importAction)
      .unwrap()
      .then(() => {
        setShowImportModal(false);
        setSelectedFile(null);
        if (onImportSuccess) {
          onImportSuccess();
        }
      })
      .catch(() => {
        // Error is handled by Redux state
      });
  };

  const closeImportModal = () => {
    setShowImportModal(false);
    setSelectedFile(null);
  };

  const getTitle = () => {
    if (mode === 'batch' && batchName) return `Export/Import for ${batchName}`;
    if (mode === 'schedule' && scheduleName) return `Export/Import for ${scheduleName}`;
    if (mode === 'results') return 'Export/Import Cycle Count Results';
    return 'Export/Import Cycle Count Data';
  };

  return (
    <div>
      <Card>
        <Card.Header>
          <h5>{getTitle()}</h5>
        </Card.Header>
        <Card.Body>
          {exportError && (
            <Alert variant="danger" className="mb-3">
              Export Error: {exportError.error || 'Unknown error'}
            </Alert>
          )}

          {/* Export Section */}
          <Row className="mb-4">
            <Col>
              <h6>Export Data</h6>

              {mode === 'results' && (
                <Row className="mb-3">
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>Start Date</Form.Label>
                      <Form.Control
                        type="date"
                        value={exportFilters.start_date}
                        onChange={(e) => setExportFilters(prev => ({ ...prev, start_date: e.target.value }))}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>End Date</Form.Label>
                      <Form.Control
                        type="date"
                        value={exportFilters.end_date}
                        onChange={(e) => setExportFilters(prev => ({ ...prev, end_date: e.target.value }))}
                      />
                    </Form.Group>
                  </Col>
                </Row>
              )}

              {mode === 'results' && (
                <Form.Check
                  type="checkbox"
                  label="Export discrepancies only"
                  checked={exportFilters.discrepancies_only}
                  onChange={(e) => setExportFilters(prev => ({ ...prev, discrepancies_only: e.target.checked }))}
                  className="mb-3"
                />
              )}

              <ButtonGroup>
                <Button
                  variant="outline-primary"
                  onClick={() => handleExport('csv')}
                  disabled={exportLoading}
                >
                  {exportLoading ? (
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
                      <i className="bi bi-filetype-csv me-2"></i>
                      Export CSV
                    </>
                  )}
                </Button>

                <Button
                  variant="outline-primary"
                  onClick={() => handleExport('excel')}
                  disabled={exportLoading}
                >
                  {exportLoading ? (
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
                      <i className="bi bi-filetype-xlsx me-2"></i>
                      Export Excel
                    </>
                  )}
                </Button>
              </ButtonGroup>
            </Col>
          </Row>

          {/* Import Section */}
          <Row>
            <Col>
              <h6>Import Data</h6>
              <Dropdown className="mb-3">
                <Dropdown.Toggle variant="outline-secondary" id="import-type-dropdown">
                  Import {importType === 'results' ? 'Count Results' : importType === 'schedules' ? 'Schedules' : 'Batches'}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  {mode === 'batch' && (
                    <Dropdown.Item onClick={() => setImportType('results')}>
                      Count Results
                    </Dropdown.Item>
                  )}
                  <Dropdown.Item onClick={() => setImportType('schedules')}>
                    Schedules
                  </Dropdown.Item>
                  <Dropdown.Item onClick={() => setImportType('batches')}>
                    Batches
                  </Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>

              <Button
                variant="outline-success"
                onClick={() => setShowImportModal(true)}
              >
                <i className="bi bi-upload me-2"></i>
                Import {importType === 'results' ? 'Count Results' : importType === 'schedules' ? 'Schedules' : 'Batches'}
              </Button>
            </Col>
          </Row>

          <div className="text-muted mt-3">
            <small>
              <strong>Export:</strong> Download data in CSV or Excel format for offline use.<br />
              <strong>Import:</strong> Upload data from CSV files to create or update records.
            </small>
          </div>
        </Card.Body>
      </Card>

      {/* Import Modal */}
      <Modal show={showImportModal} onHide={closeImportModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            Import {importType === 'results' ? 'Count Results' : importType === 'schedules' ? 'Schedules' : 'Batches'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {importError && (
            <Alert variant="danger">
              Import Error: {importError.error || 'Unknown error'}
            </Alert>
          )}

          {importResult && (
            <Alert variant="success">
              <strong>Import Successful!</strong><br />
              Imported {importResult.imported_count} {importType}.
              {importResult.errors && importResult.errors.length > 0 && (
                <div className="mt-2">
                  <strong>Errors:</strong>
                  <ul className="mb-0 mt-1">
                    {importResult.errors.slice(0, 5).map((error, index) => (
                      <li key={index}><small>{error}</small></li>
                    ))}
                    {importResult.errors.length > 5 && (
                      <li><small>... and {importResult.errors.length - 5} more errors</small></li>
                    )}
                  </ul>
                </div>
              )}
            </Alert>
          )}

          <Form.Group className="mb-3">
            <Form.Label>Select CSV File</Form.Label>
            <Form.Control
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
            />
            <Form.Text className="text-muted">
              Upload a CSV file with {importType} data.
            </Form.Text>
          </Form.Group>

          <Alert variant="info">
            <strong>CSV Format Requirements for {importType}:</strong>
            {importType === 'results' && (
              <ul className="mb-0 mt-2">
                <li><strong>Item ID:</strong> Required - Must match exported item IDs</li>
                <li><strong>Actual Quantity:</strong> Required - Counted quantity</li>
                <li><strong>Actual Location:</strong> Optional - Where item was found</li>
                <li><strong>Condition:</strong> Optional - Item condition</li>
                <li><strong>Notes:</strong> Optional - Additional notes</li>
              </ul>
            )}
            {importType === 'schedules' && (
              <ul className="mb-0 mt-2">
                <li><strong>Schedule Name:</strong> Required - Unique schedule name</li>
                <li><strong>Description:</strong> Optional - Schedule description</li>
                <li><strong>Frequency:</strong> Required - daily, weekly, monthly, quarterly, yearly</li>
                <li><strong>Method:</strong> Required - ABC, random, location, category</li>
                <li><strong>Active:</strong> Optional - Yes/No (default: Yes)</li>
              </ul>
            )}
            {importType === 'batches' && (
              <ul className="mb-0 mt-2">
                <li><strong>Batch Name:</strong> Required - Unique batch name</li>
                <li><strong>Description:</strong> Optional - Batch description</li>
                <li><strong>Schedule Name:</strong> Optional - Associated schedule name</li>
                <li><strong>Status:</strong> Optional - pending, in_progress, completed, cancelled</li>
                <li><strong>Start Date:</strong> Optional - YYYY-MM-DD or YYYY-MM-DD HH:MM:SS</li>
                <li><strong>End Date:</strong> Optional - YYYY-MM-DD or YYYY-MM-DD HH:MM:SS</li>
              </ul>
            )}
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeImportModal}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleImport}
            disabled={!selectedFile || importLoading}
          >
            {importLoading ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Importing...
              </>
            ) : (
              'Import Results'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default CycleCountExportImport;
