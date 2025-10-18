import { useEffect, useRef } from 'react';
import { Modal, Button, Card, Row, Col, Badge } from 'react-bootstrap';
import JsBarcode from 'jsbarcode';
import { FaTools, FaPrint, FaDownload } from 'react-icons/fa';
import jsPDF from 'jspdf';

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
      
      const transferDateFormatted = transferDate 
        ? new Date(transferDate).toLocaleDateString()
        : new Date().toLocaleDateString();
      
      printWindow.document.write(`
        <html>
          <head>
            <title>Chemical Transfer Label - ${chemical.part_number}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
              }
              .logo-header {
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                color: #0066ff;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 3px solid #0066ff;
              }
              .transfer-badge {
                text-align: center;
                background-color: #ffc107;
                color: #000;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 15px;
                border-radius: 4px;
              }
              .barcode-container {
                text-align: center;
                margin-bottom: 20px;
                border: 2px solid #ddd;
                padding: 15px;
                border-radius: 8px;
              }
              .chemical-info {
                margin-top: 20px;
                font-size: 13px;
                line-height: 1.6;
              }
              .chemical-info p {
                margin: 8px 0;
                padding: 5px;
                border-bottom: 1px solid #eee;
              }
              .parent-lot {
                background-color: #fff3cd;
                padding: 10px;
                margin: 15px 0;
                border-left: 4px solid #ffc107;
                font-weight: bold;
              }
              .destination-info {
                background-color: #d1ecf1;
                padding: 10px;
                margin: 15px 0;
                border-left: 4px solid #0dcaf0;
              }
              @media print {
                body {
                  margin: 0;
                  padding: 10px;
                }
                button {
                  display: none;
                }
              }
            </style>
          </head>
          <body>
            <div class="logo-header">🔧 SupplyLine MRO Suite</div>
            <div class="transfer-badge">⚠️ PARTIAL TRANSFER - NEW LOT NUMBER</div>
            <div class="barcode-container">
              ${barcodeContainerRef.current.innerHTML}
            </div>
            <div class="chemical-info">
              <p><strong>Part Number:</strong> ${chemical.part_number}</p>
              <p><strong>New Lot Number:</strong> ${chemical.lot_number}</p>
              <p><strong>Description:</strong> ${chemical.description || 'N/A'}</p>
              <p><strong>Manufacturer:</strong> ${chemical.manufacturer || 'N/A'}</p>
              <p><strong>Quantity:</strong> ${chemical.quantity} ${chemical.unit}</p>
              ${chemical.expiration_date ? 
                `<p><strong>Expiration Date:</strong> ${new Date(chemical.expiration_date).toLocaleDateString()}</p>` : ''}
            </div>
            <div class="parent-lot">
              <p style="margin: 0;"><strong>⬆️ Parent Lot Number:</strong> ${parentLotNumber}</p>
            </div>
            <div class="destination-info">
              <p style="margin: 0;"><strong>📍 Destination:</strong> ${destinationName}</p>
              <p style="margin: 5px 0 0 0;"><strong>📅 Transfer Date:</strong> ${transferDateFormatted}</p>
            </div>
            <button onclick="window.print(); window.close();" style="
              background-color: #0066ff;
              color: white;
              border: none;
              padding: 10px 20px;
              font-size: 16px;
              cursor: pointer;
              border-radius: 4px;
              margin-top: 20px;
              width: 100%;
            ">Print Label</button>
          </body>
        </html>
      `);
      
      printWindow.document.close();
    }
  };

  // Handle download as PDF
  const handleDownloadPDF = () => {
    if (!chemical) return;

    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: [100, 150] // Label size: 100mm x 150mm
    });

    // Add header
    doc.setFontSize(14);
    doc.setTextColor(0, 102, 255);
    doc.text('SupplyLine MRO Suite', 50, 10, { align: 'center' });
    
    // Add transfer badge
    doc.setFillColor(255, 193, 7);
    doc.rect(5, 15, 90, 10, 'F');
    doc.setFontSize(10);
    doc.setTextColor(0, 0, 0);
    doc.text('PARTIAL TRANSFER - NEW LOT NUMBER', 50, 21, { align: 'center' });

    // Add barcode (convert SVG to image)
    if (barcodeRef.current) {
      const svgData = new XMLSerializer().serializeToString(barcodeRef.current);
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        const imgData = canvas.toDataURL('image/png');
        
        // Add barcode image to PDF
        doc.addImage(imgData, 'PNG', 10, 30, 80, 30);
        
        // Add chemical info
        doc.setFontSize(9);
        doc.setTextColor(0, 0, 0);
        let yPos = 70;
        
        doc.text(`Part Number: ${chemical.part_number}`, 10, yPos);
        yPos += 6;
        doc.text(`New Lot Number: ${chemical.lot_number}`, 10, yPos);
        yPos += 6;
        doc.text(`Description: ${chemical.description || 'N/A'}`, 10, yPos);
        yPos += 6;
        doc.text(`Manufacturer: ${chemical.manufacturer || 'N/A'}`, 10, yPos);
        yPos += 6;
        doc.text(`Quantity: ${chemical.quantity} ${chemical.unit}`, 10, yPos);
        yPos += 6;
        
        if (chemical.expiration_date) {
          doc.text(`Expiration: ${new Date(chemical.expiration_date).toLocaleDateString()}`, 10, yPos);
          yPos += 6;
        }
        
        // Add parent lot info
        yPos += 4;
        doc.setFillColor(255, 243, 205);
        doc.rect(5, yPos - 4, 90, 10, 'F');
        doc.setFontSize(10);
        doc.setFont(undefined, 'bold');
        doc.text(`Parent Lot: ${parentLotNumber}`, 10, yPos + 2);
        
        // Add destination info
        yPos += 14;
        doc.setFillColor(209, 236, 241);
        doc.rect(5, yPos - 4, 90, 14, 'F');
        doc.setFont(undefined, 'normal');
        doc.setFontSize(9);
        doc.text(`Destination: ${destinationName}`, 10, yPos + 2);
        doc.text(`Transfer Date: ${transferDate ? new Date(transferDate).toLocaleDateString() : new Date().toLocaleDateString()}`, 10, yPos + 8);
        
        // Save PDF
        doc.save(`transfer-label-${chemical.lot_number}.pdf`);
      };
      
      img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
    }
  };

  if (!chemical) return null;

  const transferDateFormatted = transferDate 
    ? new Date(transferDate).toLocaleDateString()
    : new Date().toLocaleDateString();

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton className="bg-warning">
        <Modal.Title>
          <FaTools className="me-2" />
          Transfer Label - New Lot Created
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="text-center mb-3">
          <Badge bg="warning" className="px-3 py-2">
            ⚠️ Partial Transfer - New Lot Created
          </Badge>
        </div>

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
            <strong>Quantity:</strong> {chemical.quantity} {chemical.unit}<br />
            {chemical.expiration_date && (
              <><strong>Expires:</strong> {new Date(chemical.expiration_date).toLocaleDateString()}<br /></>
            )}
            <strong>Parent Lot:</strong> {parentLotNumber}<br />
            <strong>Destination:</strong> {destinationName}<br />
            <strong>Transfer Date:</strong> {transferDateFormatted}
          </Card.Text>
        </Card>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
        <Button variant="info" onClick={handleDownloadPDF}>
          <FaDownload className="me-2" />
          Download PDF
        </Button>
        <Button variant="primary" onClick={handlePrint}>
          <FaPrint className="me-2" />
          Print Label
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default TransferBarcodeModal;

