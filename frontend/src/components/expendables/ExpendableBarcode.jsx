import { useState } from 'react';
import { Modal, Button, Form, Tabs, Tab, Alert, Spinner } from 'react-bootstrap';
import { FaPrint, FaDownload } from 'react-icons/fa';
import {
  generateExpendableLabel,
  printPdfLabel,
  downloadPdfLabel,
  LABEL_SIZES,
  CODE_TYPES,
} from '../../utils/barcodeService';

/**
 * Component for displaying and printing an expendable barcode and QR code
 *
 * @param {Object} props - Component props
 * @param {boolean} props.show - Whether to show the modal
 * @param {Function} props.onHide - Function to call when hiding the modal
 * @param {Object} props.expendable - The expendable data to generate barcode/QR code for
 */
const ExpendableBarcode = ({ show, onHide, expendable }) => {
  const [labelSize, setLabelSize] = useState('4x6');
  const [codeType, setCodeType] = useState('barcode');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle print button click
  const handlePrint = async () => {
    if (!expendable) return;

    setLoading(true);
    setError(null);

    try {
      const pdfBlob = await generateExpendableLabel(
        expendable.id,
        labelSize,
        codeType
      );
      printPdfLabel(pdfBlob, `expendable-${expendable.part_number}-label.pdf`);
    } catch (err) {
      console.error('Error printing label:', err);
      setError('Failed to generate label. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle download button click
  const handleDownload = async () => {
    if (!expendable) return;

    setLoading(true);
    setError(null);

    try {
      const pdfBlob = await generateExpendableLabel(
        expendable.id,
        labelSize,
        codeType
      );
      downloadPdfLabel(pdfBlob, `expendable-${expendable.part_number}-label.pdf`);
    } catch (err) {
      console.error('Error downloading label:', err);
      setError('Failed to generate label. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!expendable) return null;

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Expendable Barcode Label</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <div className="mb-4">
          <h5 className="mb-3">Label Configuration</h5>

          {/* Label Size Selection */}
          <Form.Group className="mb-3">
            <Form.Label>Label Size</Form.Label>
            <Form.Select
              value={labelSize}
              onChange={(e) => setLabelSize(e.target.value)}
              disabled={loading}
            >
              {Object.values(LABEL_SIZES).map((size) => (
                <option key={size.id} value={size.id}>
                  {size.name} - {size.description}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

          {/* Code Type Selection */}
          <Form.Group className="mb-3">
            <Form.Label>Code Type</Form.Label>
            <Tabs
              activeKey={codeType}
              onSelect={(k) => setCodeType(k)}
              className="mb-3"
            >
              {Object.values(CODE_TYPES).map((type) => (
                <Tab
                  key={type.id}
                  eventKey={type.id}
                  title={type.name}
                  disabled={loading}
                >
                  <p className="text-muted small">{type.description}</p>
                </Tab>
              ))}
            </Tabs>
          </Form.Group>

          {/* Item Information */}
          <div className="border rounded p-3 item-info-section">
            <h6 className="mb-2">Item Information</h6>
            <div className="row">
              <div className="col-md-6">
                <strong>Part Number:</strong> {expendable.part_number}
              </div>
              <div className="col-md-6">
                <strong>Serial/Lot:</strong> {expendable.serial_number || expendable.lot_number || 'N/A'}
              </div>
              <div className="col-12 mt-2">
                <strong>Description:</strong> {expendable.description || 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide} disabled={loading}>
          Close
        </Button>
        <Button
          variant="info"
          onClick={handleDownload}
          disabled={loading}
        >
          {loading ? (
            <>
              <Spinner animation="border" size="sm" className="me-2" />
              Generating...
            </>
          ) : (
            <>
              <FaDownload className="me-2" />
              Download PDF
            </>
          )}
        </Button>
        <Button
          variant="primary"
          onClick={handlePrint}
          disabled={loading}
        >
          {loading ? (
            <>
              <Spinner animation="border" size="sm" className="me-2" />
              Generating...
            </>
          ) : (
            <>
              <FaPrint className="me-2" />
              Print Label
            </>
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ExpendableBarcode;

