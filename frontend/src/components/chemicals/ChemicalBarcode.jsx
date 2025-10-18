import { useRef, useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import StandardBarcode from '../common/StandardBarcode';
import {
  generateChemicalBarcodeData,
  getChemicalBarcodeFields
} from '../../utils/barcodeFormatter';
import {
  filterFieldsForLabelSize,
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

    // Get all fields and filter based on label size
    const allFields = getChemicalBarcodeFields(chemical);
    const fields = filterFieldsForLabelSize(allFields, labelSize);

    // Build field rows HTML
    const fieldsHTML = fields.map(field =>
      `<div class="field-row">
        <div class="field-label">${field.label}:</div>
        <div class="field-value">${field.value}</div>
      </div>`
    ).join('');

    // Generate CSS for selected label size
    const printCSS = generatePrintCSS(labelSize, false);

    printWindow.document.write(`
      <html>
        <head>
          <title>Chemical Label - ${chemical.part_number}</title>
          <style>
            ${printCSS}
          </style>
        </head>
        <body>
          <div class="label-container">
            <div class="logo-header">🔧 SupplyLine MRO Suite</div>
            <div class="title">${chemical.part_number} - ${chemical.lot_number}</div>
            <div class="code-container">
              ${barcodeContainerRef.current.innerHTML}
            </div>
            <div class="info-fields">
              ${fieldsHTML}
            </div>
          </div>
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
