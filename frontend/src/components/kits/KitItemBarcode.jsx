import React, { useState } from 'react';
import { Modal, Button, Form, Tabs, Tab, Alert, Spinner } from 'react-bootstrap';
import { FaPrint, FaDownload } from 'react-icons/fa';
import {
  generateKitItemLabel,
  printPdfLabel,
  downloadPdfLabel,
  LABEL_SIZES,
  CODE_TYPES,
} from '../../utils/barcodeService';

/**
 * KitItemBarcode - Universal barcode modal for kit items (tools, chemicals, expendables)
 * Reuses existing barcode infrastructure for consistency
 */
const KitItemBarcode = ({ show, onHide, item }) => {
  const [labelSize, setLabelSize] = useState('4x6');
  const [codeType, setCodeType] = useState('barcode');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Determine item type for API call
  const getItemType = () => {
    if (item.item_type === 'tool' || item.source === 'item') {
      return 'tool';
    } else if (item.item_type === 'chemical') {
      return 'chemical';
    } else if (item.item_type === 'expendable' || item.source === 'expendable') {
      return 'expendable';
    }
    return null;
  };

  // Get the underlying entity ID (not the kit-item row ID)
  const getEntityId = () => {
    return item.item_id ?? item.id;
  };

  // Handle print button click
  const handlePrint = async () => {
    if (!item) return;

    const itemType = getItemType();
    const entityId = getEntityId();

    if (!itemType || !entityId) {
      setError('Unable to determine item type or ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const pdfBlob = await generateKitItemLabel(
        entityId,
        itemType,
        labelSize,
        codeType
      );
      const filename = `kit-item-${item.part_number || item.tool_number}-label.pdf`;
      printPdfLabel(pdfBlob, filename);
    } catch (err) {
      console.error('Error printing label:', err);
      setError('Failed to generate label. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle download button click
  const handleDownload = async () => {
    if (!item) return;

    const itemType = getItemType();
    const entityId = getEntityId();

    if (!itemType || !entityId) {
      setError('Unable to determine item type or ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const pdfBlob = await generateKitItemLabel(
        entityId,
        itemType,
        labelSize,
        codeType
      );
      const filename = `kit-item-${item.part_number || item.tool_number}-label.pdf`;
      downloadPdfLabel(pdfBlob, filename);
    } catch (err) {
      console.error('Error downloading label:', err);
      setError('Failed to generate label. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!item) return null;

  // Get display information
  const itemIdentifier = item.part_number || item.tool_number || 'Unknown';
  const serialOrLot = item.serial_number || item.lot_number || 'N/A';
  const itemTypeDisplay = (item.item_type || item.source || 'Unknown').toUpperCase();

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Kit Item Barcode Label</Modal.Title>
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
                <strong>Type:</strong> {itemTypeDisplay}
              </div>
              <div className="col-md-6">
                <strong>Identifier:</strong> {itemIdentifier}
              </div>
              <div className="col-md-6 mt-2">
                <strong>Serial/Lot:</strong> {serialOrLot}
              </div>
              <div className="col-md-6 mt-2">
                <strong>Location:</strong> {item.location || 'N/A'}
              </div>
              {item.description && (
                <div className="col-12 mt-2">
                  <strong>Description:</strong> {item.description}
                </div>
              )}
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

export default KitItemBarcode;

