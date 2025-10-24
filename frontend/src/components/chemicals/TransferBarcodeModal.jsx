import { useRef, useState } from 'react';
import { Modal, Button, Badge } from 'react-bootstrap';
import { FaTools, FaPrint, FaDownload } from 'react-icons/fa';
import jsPDF from 'jspdf';
import StandardBarcode from '../common/StandardBarcode';
import {
  generateChemicalBarcodeData,
  getChemicalBarcodeFields
} from '../../utils/barcodeFormatter';
import {
  generatePrintCSS
} from '../../utils/labelSizeConfig';

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
  const barcodeContainerRef = useRef(null);
  const [labelSize, setLabelSize] = useState('4x6');

  // Handle label size change
  const handleLabelSizeChange = (newSize) => {
    setLabelSize(newSize);
  };

  // Handle print button click
  const handlePrint = () => {
    if (!barcodeContainerRef.current || !chemical) return;

    const printWindow = window.open('', '_blank');

    // Generate CSS for selected label size (with transfer styling)
    const printCSS = generatePrintCSS(labelSize, true);

    // The containerRef already contains the complete barcode card with logo, title, code, and fields
    // We just need to wrap it in the print CSS
    printWindow.document.write(`
      <html>
        <head>
          <title>Chemical Transfer Label - ${chemical.part_number}</title>
          <style>
            ${printCSS}
          </style>
        </head>
        <body>
          ${barcodeContainerRef.current.innerHTML}
          <div style="text-align: center; margin-top: 10px;">
            <button onclick="window.print(); window.close();">Print Label</button>
          </div>
        </body>
      </html>
    `);

    printWindow.document.close();
  };

  // Handle download as PDF
  const handleDownloadPDF = () => {
    if (!chemical || !barcodeContainerRef.current) return;

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

    // Get barcode SVG from the container
    const svgElement = barcodeContainerRef.current.querySelector('svg');
    if (svgElement) {
      const svgData = new XMLSerializer().serializeToString(svgElement);
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

        // Get fields for transfer barcode
        const fields = getChemicalBarcodeFields(chemical, {
          isTransfer: true,
          transferData: {
            quantity: chemical.quantity,
            unit: chemical.unit,
            parent_lot_number: parentLotNumber,
            destination: destinationName,
            transfer_date: transferDate || new Date()
          }
        });

        // Add chemical info
        doc.setFontSize(9);
        doc.setTextColor(0, 0, 0);
        let yPos = 70;

        fields.forEach(field => {
          doc.text(`${field.label}: ${field.value}`, 10, yPos);
          yPos += 6;
        });

        // Add note
        yPos += 4;
        doc.setFillColor(255, 243, 205);
        doc.rect(5, yPos - 4, 90, 10, 'F');
        doc.setFontSize(8);
        doc.text('Note: This is a partial transfer. The parent lot has been split.', 10, yPos + 2);

        // Save PDF
        doc.save(`transfer-label-${chemical.lot_number}.pdf`);
      };

      img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
    }
  };

  if (!chemical) return null;

  const barcodeData = generateChemicalBarcodeData(chemical);
  const fields = getChemicalBarcodeFields(chemical, {
    isTransfer: true,
    transferData: {
      quantity: chemical.quantity,
      unit: chemical.unit,
      parent_lot_number: parentLotNumber,
      destination: destinationName,
      transfer_date: transferDate || new Date()
    }
  });
  const title = `${chemical.part_number} - ${chemical.lot_number}`;

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

        <StandardBarcode
          type="barcode"
          barcodeData={barcodeData}
          title={title}
          fields={fields}
          specialStyling={{
            isTransfer: true,
            isWarning: true,
            warningText: "PARTIAL TRANSFER - NEW LOT NUMBER"
          }}
          containerRef={barcodeContainerRef}
          onLabelSizeChange={handleLabelSizeChange}
        />
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

