import { useEffect, useRef, useState } from 'react';
import { Card, Form } from 'react-bootstrap';
import JsBarcode from 'jsbarcode';
import { QRCodeSVG } from 'qrcode.react';
import { FaTools } from 'react-icons/fa';
import PropTypes from 'prop-types';

/**
 * Standardized barcode/QR code display component
 * Ensures consistent formatting across all barcode types
 *
 * @param {Object} props - Component props
 * @param {string} props.type - Type of code: 'barcode' or 'qrcode'
 * @param {string} props.barcodeData - The data string to encode in the barcode
 * @param {string} props.qrUrl - The URL to encode in the QR code (for type='qrcode')
 * @param {string} props.title - The title to display (e.g., "TOOL-001 - S/N: 12345")
 * @param {Array} props.fields - Array of field objects {label, value} to display
 * @param {Object} props.specialStyling - Optional special styling (for transfers, warnings, etc.)
 * @param {boolean} props.specialStyling.isTransfer - Whether this is a transfer barcode
 * @param {boolean} props.specialStyling.isWarning - Whether to show warning styling
 * @param {string} props.specialStyling.warningText - Warning text to display
 * @param {Object} props.containerRef - Ref to attach to the container for printing
 * @param {Function} props.onLabelSizeChange - Callback when label size changes
 */
const StandardBarcode = ({
  type = 'barcode',
  barcodeData,
  qrUrl,
  title,
  fields = [],
  specialStyling = {},
  containerRef,
  onLabelSizeChange
}) => {
  const barcodeRef = useRef(null);
  const [labelSize, setLabelSize] = useState('4x6');

  // Handle label size change
  const handleLabelSizeChange = (e) => {
    const newSize = e.target.value;
    setLabelSize(newSize);
    if (onLabelSizeChange) {
      onLabelSizeChange(newSize);
    }
  };

  // Generate barcode when data changes
  useEffect(() => {
    if (type === 'barcode' && barcodeData && barcodeRef.current) {
      try {
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
      } catch (error) {
        console.error('Error generating barcode:', error);
      }
    }
  }, [type, barcodeData]);

  const { isTransfer, isWarning, warningText } = specialStyling;

  return (
    <>
      {/* Label Size Selector */}
      <div className="mb-3">
        <Form.Group>
          <Form.Label style={{ fontWeight: '600', color: 'var(--bs-body-color)' }}>
            Label Size for Printing:
          </Form.Label>
          <Form.Select
            value={labelSize}
            onChange={handleLabelSizeChange}
            style={{ maxWidth: '300px' }}
          >
            <option value="4x6">4" × 6" (Standard Shipping Label)</option>
            <option value="3x4">3" × 4" (Medium Label)</option>
            <option value="2x4">2" × 4" (Small Label)</option>
            <option value="2x2">2" × 2" (Compact Label)</option>
          </Form.Select>
          <Form.Text className="text-muted">
            Select the size of your label stickers for optimized printing
          </Form.Text>
        </Form.Group>
      </div>

      {/* Barcode Display Card */}
      <Card
        className="text-center p-3"
        ref={containerRef}
        style={{
          border: isWarning ? '2px solid var(--bs-warning)' : undefined,
          boxShadow: isWarning ? '0 0 10px rgba(255, 193, 7, 0.3)' : undefined
        }}
      >
        {/* Logo Header */}
        <div
          className="d-flex align-items-center justify-content-center mb-2"
          style={{
            fontSize: '1.2rem',
            fontWeight: 'bold',
            color: 'var(--bs-primary)',
            paddingBottom: '10px',
            borderBottom: '2px solid var(--bs-primary)'
          }}
        >
          <FaTools className="me-2" />
          <span>SupplyLine MRO Suite</span>
        </div>

        {/* Warning Badge (for transfers or special cases) */}
        {isWarning && warningText && (
          <div
            className="mb-3 p-2"
            style={{
              backgroundColor: 'var(--bs-warning)',
              color: '#000',
              fontWeight: 'bold',
              borderRadius: '4px',
              fontSize: '0.9rem'
            }}
          >
            ⚠️ {warningText}
          </div>
        )}

        {/* Title */}
        {title && (
          <Card.Title className="mb-3" style={{ fontSize: '1.1rem', fontWeight: '600', color: 'var(--bs-body-color)' }}>
            {title}
          </Card.Title>
        )}

        {/* Barcode or QR Code */}
        <div className="d-flex justify-content-center my-3">
          {type === 'barcode' ? (
            <svg ref={barcodeRef}></svg>
          ) : (
            <QRCodeSVG value={qrUrl || ''} size={256} />
          )}
        </div>

        {/* QR Code Helper Text */}
        {type === 'qrcode' && (
          <Card.Text style={{ fontSize: '12px', color: 'var(--bs-secondary-color)', marginBottom: '20px' }}>
            Scan this QR code to view detailed information
          </Card.Text>
        )}

        {/* Information Fields */}
        {fields && fields.length > 0 && (
          <div
            className="mt-3"
            style={{
              textAlign: 'left',
              fontSize: '0.9rem',
              lineHeight: '1.8'
            }}
          >
            {fields.map((field, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  padding: '8px 0',
                  borderBottom: index < fields.length - 1 ? '1px solid var(--bs-border-color)' : 'none'
                }}
              >
                <div style={{
                  fontWeight: '600',
                  color: 'var(--bs-secondary-color)',
                  minWidth: '180px',
                  flexShrink: 0
                }}>
                  {field.label}:
                </div>
                <div style={{
                  color: 'var(--bs-body-color)',
                  flex: 1,
                  wordBreak: 'break-word'
                }}>
                  {field.value}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Transfer-specific styling */}
        {isTransfer && (
          <div
            className="mt-3 p-2"
            style={{
              backgroundColor: 'var(--bs-warning-bg-subtle)',
              border: '1px solid var(--bs-warning)',
              borderRadius: '4px',
              fontSize: '0.85rem',
              color: 'var(--bs-warning-text-emphasis)'
            }}
          >
            <strong>Note:</strong> This is a partial transfer. The parent lot has been split.
          </div>
        )}
      </Card>
    </>
  );
};

StandardBarcode.propTypes = {
  type: PropTypes.oneOf(['barcode', 'qrcode']),
  barcodeData: PropTypes.string,
  qrUrl: PropTypes.string,
  title: PropTypes.string,
  fields: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired
    })
  ),
  specialStyling: PropTypes.shape({
    isTransfer: PropTypes.bool,
    isWarning: PropTypes.bool,
    warningText: PropTypes.string
  }),
  containerRef: PropTypes.object,
  onLabelSizeChange: PropTypes.func
};

export default StandardBarcode;

