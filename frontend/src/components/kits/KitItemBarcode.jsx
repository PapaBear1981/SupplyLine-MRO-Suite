import React, { useState, useRef, useEffect } from 'react';
import { Modal, Button, Tabs, Tab, Alert } from 'react-bootstrap';
import StandardBarcode from '../common/StandardBarcode';
import {
  generateChemicalBarcodeData,
  generateToolBarcodeData,
  generateExpendableBarcodeData,
  getChemicalBarcodeFields,
  getToolBarcodeFields,
  getExpendableBarcodeFields
} from '../../utils/barcodeFormatter';
import { generatePrintCSS } from '../../utils/labelSizeConfig';
import api from '../../services/api';

/**
 * KitItemBarcode - Universal barcode modal for kit items (tools, chemicals, expendables)
 * Reuses existing barcode infrastructure for consistency
 */
const KitItemBarcode = ({ show, onHide, item }) => {
  const [barcodeData, setBarcodeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [labelSize, setLabelSize] = useState('4x6');
  const barcodeContainerRef = useRef(null);
  const qrCodeContainerRef = useRef(null);

  // Fetch barcode data when modal opens
  useEffect(() => {
    const fetchBarcodeData = async () => {
      if (show && item) {
        setLoading(true);
        setError(null);
        try {
          let response;

          // Use item_id (the underlying entity ID) instead of id (the kit-item row ID)
          const entityId = item.item_id ?? item.id;

          // Determine item type and fetch appropriate barcode data
          if (item.item_type === 'tool' || item.source === 'item') {
            // For tools, use the tool barcode endpoint with the underlying entity ID
            response = await api.get(`/tools/${entityId}/barcode`);
          } else if (item.item_type === 'chemical') {
            // For chemicals, use the chemical barcode endpoint with the underlying entity ID
            response = await api.get(`/chemicals/${entityId}/barcode`);
          } else if (item.item_type === 'expendable' || item.source === 'expendable') {
            // For expendables, use the expendable barcode endpoint with the underlying entity ID
            response = await api.get(`/expendables/${entityId}/barcode`);
          } else {
            throw new Error('Unknown item type');
          }
          
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
  }, [show, item]);

  // Handle label size change
  const handleLabelSizeChange = (newSize) => {
    setLabelSize(newSize);
  };

  // Generic print function for both barcode and QR code
  const handlePrint = (type, containerRef) => {
    if (!containerRef.current || !barcodeData || !item) return;

    const printWindow = window.open('', '_blank', 'noopener,noreferrer');
    if (!printWindow) {
      alert('Pop-up blocked. Please allow pop-ups to print labels.');
      return;
    }
    try { printWindow.opener = null; } catch { /* ignore */ }
    const typeCapitalized = type.charAt(0).toUpperCase() + type.slice(1);

    // Generate CSS for selected label size
    const printCSS = generatePrintCSS(labelSize, false);

    // The containerRef already contains the complete barcode card with logo, title, code, and fields
    // We just need to wrap it in the print CSS
    printWindow.document.write(`
      <html>
        <head>
          <title>Kit Item ${typeCapitalized} - ${item.part_number || item.tool_number}</title>
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

  if (!item) return null;

  // Prepare data for StandardBarcode component
  const completeItemData = barcodeData ? {
    ...item,
    ...barcodeData,
    created_at: barcodeData.created_at || item.created_at
  } : item;

  // Generate barcode string
  let barcodeString = '';
  if (barcodeData) {
    barcodeString = barcodeData.barcode_data;
  } else if (item.item_type === 'tool' || item.source === 'item') {
    barcodeString = generateToolBarcodeData(item);
  } else if (item.item_type === 'expendable' || item.source === 'expendable') {
    barcodeString = generateExpendableBarcodeData(item);
  } else {
    barcodeString = generateChemicalBarcodeData(item);
  }

  // Get fields based on item type
  let fields = [];
  if (barcodeData) {
    if (item.item_type === 'tool' || item.source === 'item') {
      fields = getToolBarcodeFields(completeItemData, barcodeData.calibration);
    } else if (item.item_type === 'expendable' || item.source === 'expendable') {
      fields = getExpendableBarcodeFields(completeItemData);
    } else {
      fields = getChemicalBarcodeFields(completeItemData);
    }
  }

  // Generate title
  let title = '';
  if (item.item_type === 'tool' || item.source === 'item') {
    title = barcodeData
      ? `${item.part_number || item.tool_number} - ${barcodeData.lot_number ? `LOT: ${barcodeData.lot_number}` : `S/N: ${item.serial_number}`}`
      : `${item.part_number || item.tool_number}`;
  } else if (item.item_type === 'expendable' || item.source === 'expendable') {
    title = barcodeData
      ? `${item.part_number} - ${barcodeData.lot_number ? `LOT: ${barcodeData.lot_number}` : `S/N: ${item.serial_number}`}`
      : `${item.part_number}`;
  } else {
    title = `${item.part_number} - ${item.lot_number}`;
  }

  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Kit Item Barcode</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && (
          <div className="text-center py-4">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-2">Loading barcode data...</p>
          </div>
        )}

        {error && (
          <Alert variant="danger">{error}</Alert>
        )}

        {!loading && !error && barcodeData && (
          <Tabs defaultActiveKey="barcode" id="kit-item-code-tabs" className="mb-3">
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

export default KitItemBarcode;

