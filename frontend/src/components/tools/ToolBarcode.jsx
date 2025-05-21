import { useEffect, useRef } from 'react';
import { Modal, Button, Card, Tabs, Tab } from 'react-bootstrap';
import JsBarcode from 'jsbarcode';
import { QRCodeSVG } from 'qrcode.react';

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

  // Generate barcode when tool data changes or modal is shown
  useEffect(() => {
    if (show && tool && barcodeRef.current) {
      // Create barcode data string: tool_number-serial_number
      const barcodeData = `${tool.tool_number}-${tool.serial_number}`;
      
      // Generate barcode
      JsBarcode(barcodeRef.current, barcodeData, {
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
  }, [show, tool]);

  // Create QR code data
  const qrCodeData = tool ? JSON.stringify({
    id: tool.id,
    tool_number: tool.tool_number,
    serial_number: tool.serial_number,
    description: tool.description,
    category: tool.category,
    location: tool.location,
    status: tool.status
  }) : '';

  // Handle print button click for barcode
  const handlePrintBarcode = () => {
    if (barcodeContainerRef.current) {
      const printWindow = window.open('', '_blank');
      
      printWindow.document.write(`
        <html>
          <head>
            <title>Tool Barcode - ${tool.tool_number}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
              }
              .barcode-container {
                text-align: center;
                margin-bottom: 20px;
              }
              .tool-info {
                margin-top: 20px;
                font-size: 14px;
              }
              .tool-info p {
                margin: 5px 0;
              }
              @media print {
                body {
                  margin: 0;
                  padding: 0;
                }
                button {
                  display: none;
                }
              }
            </style>
          </head>
          <body>
            <div class="barcode-container">
              ${barcodeContainerRef.current.innerHTML}
            </div>
            <div class="tool-info">
              <p><strong>Tool Number:</strong> ${tool.tool_number}</p>
              <p><strong>Serial Number:</strong> ${tool.serial_number}</p>
              <p><strong>Description:</strong> ${tool.description || 'N/A'}</p>
              <p><strong>Category:</strong> ${tool.category || 'N/A'}</p>
              <p><strong>Location:</strong> ${tool.location || 'N/A'}</p>
            </div>
            <button onclick="window.print(); window.close();">Print</button>
          </body>
        </html>
      `);
      
      printWindow.document.close();
    }
  };

  // Handle print button click for QR code
  const handlePrintQRCode = () => {
    if (qrCodeContainerRef.current) {
      const printWindow = window.open('', '_blank');
      
      printWindow.document.write(`
        <html>
          <head>
            <title>Tool QR Code - ${tool.tool_number}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
              }
              .qrcode-container {
                text-align: center;
                margin-bottom: 20px;
              }
              .tool-info {
                margin-top: 20px;
                font-size: 14px;
              }
              .tool-info p {
                margin: 5px 0;
              }
              @media print {
                body {
                  margin: 0;
                  padding: 0;
                }
                button {
                  display: none;
                }
              }
            </style>
          </head>
          <body>
            <div class="qrcode-container">
              ${qrCodeContainerRef.current.innerHTML}
            </div>
            <div class="tool-info">
              <p><strong>Tool Number:</strong> ${tool.tool_number}</p>
              <p><strong>Serial Number:</strong> ${tool.serial_number}</p>
              <p><strong>Description:</strong> ${tool.description || 'N/A'}</p>
              <p><strong>Category:</strong> ${tool.category || 'N/A'}</p>
              <p><strong>Location:</strong> ${tool.location || 'N/A'}</p>
            </div>
            <button onclick="window.print(); window.close();">Print</button>
          </body>
        </html>
      `);
      
      printWindow.document.close();
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Tool Identification</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Tabs defaultActiveKey="barcode" id="tool-code-tabs" className="mb-3">
          <Tab eventKey="barcode" title="Barcode">
            {tool && (
              <Card className="text-center p-3" ref={barcodeContainerRef}>
                <Card.Title>{tool.tool_number} - {tool.serial_number}</Card.Title>
                <div className="d-flex justify-content-center my-3">
                  <svg ref={barcodeRef}></svg>
                </div>
                <Card.Text>
                  <strong>Description:</strong> {tool.description || 'N/A'}<br />
                  <strong>Category:</strong> {tool.category || 'N/A'}<br />
                  <strong>Location:</strong> {tool.location || 'N/A'}
                </Card.Text>
                <Button variant="primary" onClick={handlePrintBarcode} className="mt-2">
                  Print Barcode
                </Button>
              </Card>
            )}
          </Tab>
          <Tab eventKey="qrcode" title="QR Code">
            {tool && (
              <Card className="text-center p-3" ref={qrCodeContainerRef}>
                <Card.Title>{tool.tool_number} - {tool.serial_number}</Card.Title>
                <div className="d-flex justify-content-center my-3">
                  <QRCodeSVG value={qrCodeData} size={256} />
                </div>
                <Card.Text>
                  <strong>Description:</strong> {tool.description || 'N/A'}<br />
                  <strong>Category:</strong> {tool.category || 'N/A'}<br />
                  <strong>Location:</strong> {tool.location || 'N/A'}
                </Card.Text>
                <Button variant="primary" onClick={handlePrintQRCode} className="mt-2">
                  Print QR Code
                </Button>
              </Card>
            )}
          </Tab>
        </Tabs>
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
