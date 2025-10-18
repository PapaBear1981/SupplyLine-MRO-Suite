import { useEffect, useRef } from 'react';
import { Modal, Button, Card } from 'react-bootstrap';
import JsBarcode from 'jsbarcode';
import { FaTools } from 'react-icons/fa';

/**
 * Component for displaying and printing a chemical barcode
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.show - Whether to show the modal
 * @param {Function} props.onHide - Function to call when hiding the modal
 * @param {Object} props.chemical - The chemical data to generate barcode for
 */
const ChemicalBarcode = ({ show, onHide, chemical }) => {
  const barcodeRef = useRef(null);
  const barcodeContainerRef = useRef(null);

  // Generate barcode when chemical data changes or modal is shown
  useEffect(() => {
    if (show && chemical && barcodeRef.current) {
      // Create barcode data string: part_number-lot_number-expiration_date
      const expirationDate = chemical.expiration_date 
        ? new Date(chemical.expiration_date).toISOString().split('T')[0].replace(/-/g, '')
        : 'NOEXP';
      
      const barcodeData = `${chemical.part_number}-${chemical.lot_number}-${expirationDate}`;
      
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
  }, [show, chemical]);

  // Handle print button click
  const handlePrint = () => {
    if (barcodeContainerRef.current) {
      const printWindow = window.open('', '_blank');
      
      printWindow.document.write(`
        <html>
          <head>
            <title>Chemical Barcode - ${chemical.part_number}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
              }
              .logo-header {
                text-align: center;
                font-size: 16px;
                font-weight: bold;
                color: #0066ff;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #0066ff;
              }
              .barcode-container {
                text-align: center;
                margin-bottom: 20px;
              }
              .chemical-info {
                margin-top: 20px;
                font-size: 14px;
              }
              .chemical-info p {
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
            <div class="logo-header">🔧 SupplyLine MRO Suite</div>
            <div class="barcode-container">
              ${barcodeContainerRef.current.innerHTML}
            </div>
            <div class="chemical-info">
              <p><strong>Part Number:</strong> ${chemical.part_number}</p>
              <p><strong>Lot Number:</strong> ${chemical.lot_number}</p>
              <p><strong>Description:</strong> ${chemical.description || 'N/A'}</p>
              <p><strong>Manufacturer:</strong> ${chemical.manufacturer || 'N/A'}</p>
              ${chemical.expiration_date ? 
                `<p><strong>Expiration Date:</strong> ${new Date(chemical.expiration_date).toLocaleDateString()}</p>` : ''}
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
        <Modal.Title>Chemical Barcode</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {chemical && (
          <Card className="text-center p-3" ref={barcodeContainerRef}>
            <div className="d-flex align-items-center justify-content-center mb-2" style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#0066ff' }}>
              <FaTools className="me-2" />
              <span>SupplyLine MRO Suite</span>
            </div>
            <Card.Title>{chemical.part_number} - {chemical.lot_number}</Card.Title>
            <div className="d-flex justify-content-center my-3">
              <svg ref={barcodeRef}></svg>
            </div>
            <Card.Text>
              <strong>Description:</strong> {chemical.description || 'N/A'}<br />
              <strong>Manufacturer:</strong> {chemical.manufacturer || 'N/A'}<br />
              {chemical.expiration_date && (
                <><strong>Expires:</strong> {new Date(chemical.expiration_date).toLocaleDateString()}</>
              )}
            </Card.Text>
          </Card>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        <Button variant="primary" onClick={handlePrint}>
          <i className="bi bi-printer me-2"></i>
          Print Barcode
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ChemicalBarcode;
