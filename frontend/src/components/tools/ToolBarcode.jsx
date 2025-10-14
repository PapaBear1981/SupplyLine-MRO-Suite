import { useEffect, useRef, useState } from 'react';
import { Modal, Button, Card, Tabs, Tab, Spinner, Alert } from 'react-bootstrap';
import JsBarcode from 'jsbarcode';
import { QRCodeSVG } from 'qrcode.react';
import api from '../../services/api';

/**
 * Component for displaying and printing a tool barcode and QR code
 *
 * @param {Object} props - Component props
 * @param {boolean} props.show - Whether to show the modal
 * @param {Function} props.onHide - Function to call when hiding the modal
 * @param {Object} props.tool - The tool data to generate barcode/QR code for
 */
const ToolBarcode = ({ show, onHide, tool }) => {
  const barcodeRef = useRef(null);
  const barcodeContainerRef = useRef(null);
  const qrCodeContainerRef = useRef(null);

  const [barcodeData, setBarcodeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  // Generate barcode when barcode data is available
  useEffect(() => {
    if (barcodeData && barcodeRef.current) {
      // Generate barcode
      JsBarcode(barcodeRef.current, barcodeData.barcode_data, {
        format: "CODE128",
        lineColor: "#000",
        width: 2,
        height: 100,
        displayValue: true,
        fontSize: 16,
        margin: 10,
        textMargin: 10
      });
    }
  }, [barcodeData]);

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  // HTML escape function to prevent XSS in print templates
  const escapeHtml = (str) => {
    if (str === null || str === undefined) return '';
    return String(str).replace(/[&<>"']/g, (char) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[char]));
  };

  // Generic print function to handle both barcode and QR code printing
  const handlePrint = (type, containerRef) => {
    if (containerRef.current && barcodeData) {
      const printWindow = window.open('', '_blank');
      const typeCapitalized = type.charAt(0).toUpperCase() + type.slice(1);

      // Prepare calibration info HTML
      let calibrationInfoHTML = '';
      if (barcodeData.requires_calibration && barcodeData.calibration) {
        const calDate = formatDate(barcodeData.calibration.calibration_date);
        const nextDate = formatDate(barcodeData.calibration.next_calibration_date);

        calibrationInfoHTML = `
          <div class="calibration-info">
            <h3 style="margin-top: 20px; margin-bottom: 10px; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">Calibration Information</h3>
            <p><strong>Last Calibration:</strong> <span style="color: #27ae60; font-weight: bold;">${calDate}</span></p>
            <p><strong>Next Due Date:</strong> <span style="color: #e74c3c; font-weight: bold;">${nextDate}</span></p>
            <p><strong>Status:</strong> ${barcodeData.calibration.calibration_status}</p>
          </div>
        `;
      } else if (barcodeData.requires_calibration) {
        calibrationInfoHTML = `
          <div class="calibration-info">
            <h3 style="margin-top: 20px; margin-bottom: 10px; color: #e74c3c; border-bottom: 2px solid #e74c3c; padding-bottom: 5px;">⚠️ Calibration Required</h3>
            <p style="color: #e74c3c;"><strong>No calibration records on file</strong></p>
          </div>
        `;
      }

      printWindow.document.write(`
        <html>
          <head>
            <title>Tool ${typeCapitalized} - ${tool.tool_number}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f8f9fa;
              }
              .label-container {
                background: white;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 20px;
                max-width: 400px;
                margin: 0 auto;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
              }
              .code-container {
                text-align: center;
                margin-bottom: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
              }
              .tool-info {
                margin-top: 20px;
                font-size: 14px;
                line-height: 1.6;
              }
              .tool-info p {
                margin: 8px 0;
                padding: 5px 0;
                border-bottom: 1px solid #eee;
              }
              .tool-info p:last-child {
                border-bottom: none;
              }
              .calibration-info {
                margin-top: 15px;
                padding: 15px;
                background: #fff3cd;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
              }
              .calibration-info p {
                margin: 5px 0;
                border-bottom: none;
              }
              h3 {
                font-size: 16px;
                margin: 0 0 10px 0;
              }
              button {
                margin-top: 20px;
                padding: 10px 20px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
              }
              button:hover {
                background: #0056b3;
              }
              @media print {
                body {
                  margin: 0;
                  padding: 10px;
                  background: white;
                }
                .label-container {
                  border: 2px solid #333;
                  box-shadow: none;
                }
                button {
                  display: none;
                }
              }
            </style>
          </head>
          <body>
            <div class="label-container">
              <div class="code-container">
                ${containerRef.current.innerHTML}
              </div>
              <div class="tool-info">
                <p><strong>Tool Number:</strong> ${escapeHtml(tool.tool_number)}</p>
                ${barcodeData.lot_number
                  ? `<p><strong>Lot Number:</strong> ${escapeHtml(barcodeData.lot_number)}</p>`
                  : `<p><strong>Serial Number:</strong> ${escapeHtml(tool.serial_number)}</p>`}
                <p><strong>Description:</strong> ${escapeHtml(tool.description || 'N/A')}</p>
                <p><strong>Category:</strong> ${escapeHtml(tool.category || 'N/A')}</p>
                <p><strong>Location:</strong> ${escapeHtml(tool.location || 'N/A')}</p>
              </div>
              ${calibrationInfoHTML}
            </div>
            <div style="text-align: center;">
              <button onclick="window.print(); window.close();">Print Label</button>
            </div>
          </body>
        </html>
      `);

      printWindow.document.close();
    }
  };

  // Handle print button click for barcode
  const handlePrintBarcode = () => handlePrint('barcode', barcodeContainerRef);

  // Handle print button click for QR code
  const handlePrintQRCode = () => handlePrint('qr code', qrCodeContainerRef);

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
              <Card className="text-center p-3" ref={barcodeContainerRef}>
                <Card.Title>
                  {tool.tool_number} - {barcodeData.lot_number ? `LOT: ${barcodeData.lot_number}` : `S/N: ${tool.serial_number}`}
                </Card.Title>
                <div className="d-flex justify-content-center my-3">
                  <svg ref={barcodeRef}></svg>
                </div>
                <Card.Text>
                  <strong>Description:</strong> {tool.description || 'N/A'}<br />
                  <strong>Category:</strong> {tool.category || 'N/A'}<br />
                  <strong>Location:</strong> {tool.location || 'N/A'}
                  {barcodeData.lot_number && (
                    <>
                      <br />
                      <strong>Lot Number:</strong> <span style={{ fontFamily: 'monospace', color: '#f57c00' }}>LOT: {barcodeData.lot_number}</span>
                    </>
                  )}
                  {!barcodeData.lot_number && tool.serial_number && (
                    <>
                      <br />
                      <strong>Serial Number:</strong> <span style={{ fontFamily: 'monospace', color: '#1976d2' }}>S/N: {tool.serial_number}</span>
                    </>
                  )}
                </Card.Text>

                {barcodeData.requires_calibration && barcodeData.calibration && (
                  <div className="mt-3 p-3" style={{ backgroundColor: '#fff3cd', borderRadius: '8px', borderLeft: '4px solid #ffc107' }}>
                    <h6 style={{ marginBottom: '10px', color: '#856404' }}>📅 Calibration Information</h6>
                    <div style={{ fontSize: '14px', textAlign: 'left' }}>
                      <p style={{ margin: '5px 0' }}>
                        <strong>Last Calibration:</strong> <span style={{ color: '#27ae60' }}>{formatDate(barcodeData.calibration.calibration_date)}</span>
                      </p>
                      <p style={{ margin: '5px 0' }}>
                        <strong>Next Due Date:</strong> <span style={{ color: '#e74c3c' }}>{formatDate(barcodeData.calibration.next_calibration_date)}</span>
                      </p>
                    </div>
                  </div>
                )}

                {barcodeData.requires_calibration && !barcodeData.calibration && (
                  <Alert variant="warning" className="mt-3">
                    <strong>⚠️ Calibration Required</strong><br />
                    No calibration records on file
                  </Alert>
                )}

                <Button variant="primary" onClick={handlePrintBarcode} className="mt-3">
                  Print Barcode Label
                </Button>
              </Card>
            </Tab>

            <Tab eventKey="qrcode" title="QR Code">
              <Card className="text-center p-3" ref={qrCodeContainerRef}>
                <Card.Title>
                  {tool.tool_number} - {barcodeData.lot_number ? `LOT: ${barcodeData.lot_number}` : `S/N: ${tool.serial_number}`}
                </Card.Title>
                <div className="d-flex justify-content-center my-3">
                  <QRCodeSVG value={barcodeData.qr_url} size={256} />
                </div>
                <Card.Text style={{ fontSize: '12px', color: '#666' }}>
                  Scan this QR code to view tool details and calibration certificate
                </Card.Text>
                <Card.Text>
                  <strong>Description:</strong> {tool.description || 'N/A'}<br />
                  <strong>Category:</strong> {tool.category || 'N/A'}<br />
                  <strong>Location:</strong> {tool.location || 'N/A'}
                  {barcodeData.lot_number && (
                    <>
                      <br />
                      <strong>Lot Number:</strong> <span style={{ fontFamily: 'monospace', color: '#f57c00' }}>LOT: {barcodeData.lot_number}</span>
                    </>
                  )}
                  {!barcodeData.lot_number && tool.serial_number && (
                    <>
                      <br />
                      <strong>Serial Number:</strong> <span style={{ fontFamily: 'monospace', color: '#1976d2' }}>S/N: {tool.serial_number}</span>
                    </>
                  )}
                </Card.Text>

                {barcodeData.requires_calibration && barcodeData.calibration && (
                  <div className="mt-3 p-3" style={{ backgroundColor: '#d4edda', borderRadius: '8px', borderLeft: '4px solid #28a745' }}>
                    <h6 style={{ marginBottom: '10px', color: '#155724' }}>📅 Calibration Information</h6>
                    <div style={{ fontSize: '14px', textAlign: 'left' }}>
                      <p style={{ margin: '5px 0' }}>
                        <strong>Last Calibration:</strong> <span style={{ color: '#27ae60' }}>{formatDate(barcodeData.calibration.calibration_date)}</span>
                      </p>
                      <p style={{ margin: '5px 0' }}>
                        <strong>Next Due Date:</strong> <span style={{ color: '#e74c3c' }}>{formatDate(barcodeData.calibration.next_calibration_date)}</span>
                      </p>
                      {barcodeData.calibration.has_certificate && (
                        <p style={{ margin: '5px 0' }}>
                          <strong>Certificate:</strong> <span style={{ color: '#007bff' }}>✓ Available via QR scan</span>
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {barcodeData.requires_calibration && !barcodeData.calibration && (
                  <Alert variant="warning" className="mt-3">
                    <strong>⚠️ Calibration Required</strong><br />
                    No calibration records on file
                  </Alert>
                )}

                <Button variant="primary" onClick={handlePrintQRCode} className="mt-3">
                  Print QR Code Label
                </Button>
              </Card>
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
