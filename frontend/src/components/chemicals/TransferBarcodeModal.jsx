import { useState } from 'react';
import { Modal, Button, Form, Tabs, Tab, Alert, Spinner, Badge } from 'react-bootstrap';
import { FaPrint, FaDownload } from 'react-icons/fa';
import {
  generateChemicalLabel,
  printPdfLabel,
  downloadPdfLabel,
  LABEL_SIZES,
  CODE_TYPES,
} from '../../utils/barcodeService';

/**
 * Component for displaying and printing a chemical transfer barcode
 * Shows the new child lot number with parent lot reference
 *
 * @param {Object} props - Component props
 * @param {boolean} props.show - Whether to show the modal
 * @param {Function} props.onHide - Function to call when hiding the modal
 * @param {Object} props.chemical - The child chemical data (with new lot number)
 * @param {string} props.parentLotNumber - The parent lot number
 * @param {string} props.destinationName - Name of destination (warehouse or kit)
 * @param {string} props.transferDate - Date of transfer
 */
const TransferBarcodeModal = ({ show, onHide, chemical, parentLotNumber, destinationName, transferDate }) => {
  const [labelSize, setLabelSize] = useState('4x6');
  const [codeType, setCodeType] = useState('barcode');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle print button click
  const handlePrint = async () => {
    if (!chemical) return;

    setLoading(true);
    setError(null);

    try {
      const transferData = {
        parent_lot_number: parentLotNumber,
        destination: destinationName,
        transfer_date: transferDate,
      };

      const pdfBlob = await generateChemicalLabel(
        chemical.id,
        labelSize,
        codeType,
        true, // isTransfer
        transferData
      );
      printPdfLabel(pdfBlob, `transfer-${chemical.lot_number}-label.pdf`);
    } catch (err) {
      console.error('Error printing transfer label:', err);
      setError('Failed to generate transfer label. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle download button click
  const handleDownload = async () => {
    if (!chemical) return;

    setLoading(true);
    setError(null);

    try {
      const transferData = {
        parent_lot_number: parentLotNumber,
        destination: destinationName,
        transfer_date: transferDate,
      };

      const pdfBlob = await generateChemicalLabel(
        chemical.id,
        labelSize,
        codeType,
        true, // isTransfer
        transferData
      );
      downloadPdfLabel(pdfBlob, `transfer-${chemical.lot_number}-label.pdf`);
    } catch (err) {
      console.error('Error downloading transfer label:', err);
      setError('Failed to generate transfer label. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!chemical) return null;

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton className="bg-warning">
        <Modal.Title>
          Transfer Label - New Lot Created
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <div className="text-center mb-3">
          <Badge bg="warning" className="px-3 py-2">
            ⚠️ Partial Transfer - New Lot Created
          </Badge>
        </div>

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

          {/* Transfer Information */}
          <div className="border rounded p-3 item-info-section">
            <h6 className="mb-2">Transfer Information</h6>
            <div className="row">
              <div className="col-md-6">
                <strong>New Lot:</strong> {chemical.lot_number}
              </div>
              <div className="col-md-6">
                <strong>Parent Lot:</strong> {parentLotNumber || 'N/A'}
              </div>
              <div className="col-md-6 mt-2">
                <strong>Part Number:</strong> {chemical.part_number}
              </div>
              <div className="col-md-6 mt-2">
                <strong>Destination:</strong> {destinationName || 'N/A'}
              </div>
              <div className="col-12 mt-2">
                <strong>Quantity:</strong> {chemical.quantity} {chemical.unit}
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

export default TransferBarcodeModal;

