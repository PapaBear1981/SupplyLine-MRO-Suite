import { useRef, useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import StandardBarcode from '../common/StandardBarcode';
import {
  generateChemicalBarcodeData,
  getChemicalBarcodeFields
} from '../../utils/barcodeFormatter';
import {
  generatePrintCSS
} from '../../utils/labelSizeConfig';

/**
 * Component for displaying and printing a chemical barcode
 *
 * @param {Object} props - Component props
 * @param {boolean} props.show - Whether to show the modal
 * @param {Function} props.onHide - Function to call when hiding the modal
 * @param {Object} props.chemical - The chemical data to generate barcode for
 */
const ChemicalBarcode = ({ show, onHide, chemical }) => {
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

    // Generate CSS for selected label size
    const printCSS = generatePrintCSS(labelSize, false);

    // The containerRef already contains the complete barcode card with logo, title, code, and fields
    // We just need to wrap it in the print CSS
    printWindow.document.write(`
      <html>
        <head>
          <title>Chemical Label - ${chemical.part_number}</title>
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

  if (!chemical) return null;

  const barcodeData = generateChemicalBarcodeData(chemical);
  const fields = getChemicalBarcodeFields(chemical);
  const title = `${chemical.part_number} - ${chemical.lot_number}`;

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Chemical Barcode</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <StandardBarcode
          type="barcode"
          barcodeData={barcodeData}
          title={title}
          fields={fields}
          containerRef={barcodeContainerRef}
          onLabelSizeChange={handleLabelSizeChange}
        />
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
