import { useEffect, useRef, useState } from 'react';
import { Modal, Button, Tabs, Tab, Spinner, Alert } from 'react-bootstrap';
import api from '../../services/api';
import StandardBarcode from '../common/StandardBarcode';
import {
  generateToolBarcodeData,
  getToolBarcodeFields
} from '../../utils/barcodeFormatter';
import {
  generatePrintCSS
} from '../../utils/labelSizeConfig';

/**
 * Component for displaying and printing a tool barcode and QR code
 *
 * @param {Object} props - Component props
 * @param {boolean} props.show - Whether to show the modal
 * @param {Function} props.onHide - Function to call when hiding the modal
 * @param {Object} props.tool - The tool data to generate barcode/QR code for
 */
const ToolBarcode = ({ show, onHide, tool }) => {
  const barcodeContainerRef = useRef(null);
  const qrCodeContainerRef = useRef(null);

  const [barcodeData, setBarcodeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [labelSize, setLabelSize] = useState('4x6');

  // Fetch barcode data including calibration information
  useEffect(() => {
    const fetchBarcodeData = async () => {
      if (show && tool) {
        setLoading(true);
        setError(null);
        try {
          const response = await api.get(`/tools/${tool.id}/barcode`);
          setBarcodeData(response.data);
        } catch (err) {
          console.error('Error fetching barcode data:', err);
          setError('Failed to load barcode data');
        } finally {
          setLoading(false);
        }
      }
    };

    fetchBarcodeData();
  }, [show, tool]);

  // Handle label size change
  const handleLabelSizeChange = (newSize) => {
    setLabelSize(newSize);
  };

  // Generic print function to handle both barcode and QR code printing
  const handlePrint = (type, containerRef) => {
    if (!containerRef.current || !barcodeData || !tool) return;

    const printWindow = window.open('', '_blank');
    const typeCapitalized = type.charAt(0).toUpperCase() + type.slice(1);

    // Generate CSS for selected label size
    const printCSS = generatePrintCSS(labelSize, false);

    // The containerRef already contains the complete barcode card with logo, title, code, and fields
    // We just need to wrap it in the print CSS
    printWindow.document.write(`
      <html>
        <head>
          <title>Tool ${typeCapitalized} - ${tool.tool_number}</title>
          <style>
            ${printCSS}
          </style>
        </head>
        <body>
          ${containerRef.current.innerHTML}
          <div style="text-align: center; margin-top: 10px;">
            <button onclick="window.print(); window.close();">Print Label</button>
          </div>
        </body>
      </html>
    `);

    printWindow.document.close();
  };

  // Handle print button click for barcode
  const handlePrintBarcode = () => handlePrint('barcode', barcodeContainerRef);

  // Handle print button click for QR code
  const handlePrintQRCode = () => handlePrint('qr code', qrCodeContainerRef);

  if (!tool) return null;

  // Prepare data for StandardBarcode component
  const completeToolData = barcodeData ? {
    ...tool,
    ...barcodeData,
    created_at: barcodeData.created_at || tool.created_at
  } : tool;

  const barcodeString = barcodeData ? barcodeData.barcode_data : generateToolBarcodeData(tool);
  const fields = barcodeData ? getToolBarcodeFields(completeToolData, barcodeData.calibration) : [];
  const title = barcodeData
    ? `${tool.tool_number} - ${barcodeData.lot_number ? `LOT: ${barcodeData.lot_number}` : `S/N: ${tool.serial_number}`}`
    : `${tool.tool_number}`;

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Tool Identification</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && (
          <div className="text-center p-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
            <p className="mt-2">Loading barcode data...</p>
          </div>
        )}

        {error && (
          <Alert variant="danger">
            {error}
          </Alert>
        )}

        {!loading && !error && barcodeData && (
          <Tabs defaultActiveKey="barcode" id="tool-code-tabs" className="mb-3">
            <Tab eventKey="barcode" title="Barcode">
              <StandardBarcode
                type="barcode"
                barcodeData={barcodeString}
                title={title}
                fields={fields}
                containerRef={barcodeContainerRef}
                onLabelSizeChange={handleLabelSizeChange}
              />
              <div className="text-center mt-3">
                <Button variant="primary" onClick={handlePrintBarcode}>
                  <i className="bi bi-printer me-2"></i>
                  Print Barcode Label
                </Button>
              </div>
            </Tab>

            <Tab eventKey="qrcode" title="QR Code">
              <StandardBarcode
                type="qrcode"
                qrUrl={barcodeData.qr_url}
                title={title}
                fields={fields}
                containerRef={qrCodeContainerRef}
                onLabelSizeChange={handleLabelSizeChange}
              />
              <div className="text-center mt-3">
                <Button variant="primary" onClick={handlePrintQRCode}>
                  <i className="bi bi-printer me-2"></i>
                  Print QR Code Label
                </Button>
              </div>
            </Tab>
          </Tabs>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ToolBarcode;
