import { useRef } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { Modal, Button, Card } from 'react-bootstrap';

/**
 * Component for displaying and printing a QR code
 *
 * @param {Object} props - Component props
 * @param {boolean} props.show - Whether to show the modal
 * @param {Function} props.onHide - Function to call when hiding the modal
 * @param {string} props.data - The data to encode in the QR code
 * @param {string} props.title - The title to display in the modal
 * @param {Object} props.itemDetails - Additional item details to display
 * @param {number} props.size - Size of the QR code (default: 256)
 */
const QRCodeGenerator = ({ show, onHide, data, title, itemDetails, size = 256 }) => {
  const qrCodeContainerRef = useRef(null);

  // Helper function to format item details
  const formatItemDetails = (details) => {
    return Object.entries(details || {}).map(([key, value]) =>
      `<p><strong>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${value || 'N/A'}</p>`
    ).join('');
  };

  // Handle print button click
  const handlePrint = () => {
    if (qrCodeContainerRef.current) {
      const printContent = `
        <html>
          <head>
            <title>${title || 'QR Code'}</title>
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
              .item-info {
                margin-top: 20px;
                font-size: 14px;
              }
              .item-info p {
                margin: 5px 0;
              }
              @media print {
                body {
                  margin: 0;
                  padding: 0;
                }
              }
            </style>
          </head>
          <body>
            <div class="qrcode-container">
              ${qrCodeContainerRef.current.innerHTML}
            </div>
            <div class="item-info">
              ${formatItemDetails(itemDetails)}
            </div>
          </body>
        </html>
      `;

      // Use iframe approach for better browser compatibility
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      document.body.appendChild(iframe);

      iframe.onload = () => {
        iframe.contentWindow.document.write(printContent);
        iframe.contentWindow.document.close();
        iframe.contentWindow.print();

        // Clean up after printing
        setTimeout(() => {
          document.body.removeChild(iframe);
        }, 1000);
      };

      iframe.src = 'about:blank';
    }
  };

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>{title || 'QR Code'}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Card className="text-center p-3" ref={qrCodeContainerRef}>
          <Card.Title>{title}</Card.Title>
          <div className="d-flex justify-content-center my-3">
            <QRCodeSVG value={data} size={size} />
          </div>
          <Card.Text>
            {itemDetails && Object.entries(itemDetails).map(([key, value]) => (
              <div key={key}>
                <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {value || 'N/A'}<br />
              </div>
            ))}
          </Card.Text>
        </Card>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        <Button variant="primary" onClick={handlePrint}>
          Print
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default QRCodeGenerator;
