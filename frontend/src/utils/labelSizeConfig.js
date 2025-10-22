/**
 * Label Size Configuration Utility
 * Defines layouts, field priorities, and styling for different label sizes
 */

/**
 * Label size configurations
 * Each size defines:
 * - dimensions: Physical dimensions in inches
 * - maxFields: Maximum number of fields to display
 * - priorityFields: Which fields to prioritize (by index or label pattern)
 * - barcodeHeight: Height of barcode in pixels
 * - qrSize: Size of QR code in pixels
 * - fontSize: Font sizes for different elements
 * - margins: Print margins
 */
export const LABEL_SIZES = {
  '4x6': {
    name: '4" × 6" (Standard Shipping Label)',
    dimensions: { width: 4, height: 6 },
    maxFields: 12, // Show all fields
    priorityFields: 'all',
    barcodeHeight: 80,
    qrSize: 200,
    fontSize: {
      logo: '16px',
      title: '14px',
      fieldLabel: '11px',
      fieldValue: '11px',
      warning: '12px',
      note: '10px'
    },
    margins: {
      page: '0.1in',
      content: '10px'
    },
    labelWidth: '4in',
    labelHeight: '6in'
  },
  '3x4': {
    name: '3" × 4" (Medium Label)',
    dimensions: { width: 3, height: 4 },
    maxFields: 8, // Show top 8 fields
    priorityFields: [
      'Part Number',
      'Tool Number',
      'Lot Number',
      'Serial Number',
      'Description',
      'Location',
      'Expiration Date',
      'Created Date'
    ],
    barcodeHeight: 60,
    qrSize: 150,
    fontSize: {
      logo: '13px',
      title: '12px',
      fieldLabel: '9px',
      fieldValue: '9px',
      warning: '10px',
      note: '8px'
    },
    margins: {
      page: '0.05in',
      content: '8px'
    },
    labelWidth: '3in',
    labelHeight: '4in'
  },
  '2x4': {
    name: '2" × 4" (Small Label)',
    dimensions: { width: 2, height: 4 },
    maxFields: 5, // Show top 5 critical fields
    priorityFields: [
      'Part Number',
      'Tool Number',
      'Lot Number',
      'Serial Number',
      'Description'
    ],
    barcodeHeight: 50,
    qrSize: 120,
    fontSize: {
      logo: '11px',
      title: '10px',
      fieldLabel: '8px',
      fieldValue: '8px',
      warning: '9px',
      note: '7px'
    },
    margins: {
      page: '0.05in',
      content: '6px'
    },
    labelWidth: '2in',
    labelHeight: '4in'
  },
  '2x2': {
    name: '2" × 2" (Compact Label)',
    dimensions: { width: 2, height: 2 },
    maxFields: 2, // Show only 2 most critical fields
    priorityFields: [
      'Part Number',
      'Tool Number',
      'Lot Number',
      'Serial Number'
    ],
    barcodeHeight: 35,
    qrSize: 140, // Larger QR code for better scanning on small labels
    fontSize: {
      logo: '9px',
      title: '8px',
      fieldLabel: '7px',
      fieldValue: '7px',
      warning: '8px',
      note: '6px'
    },
    margins: {
      page: '0.05in',
      content: '3px'
    },
    labelWidth: '2in',
    labelHeight: '2in',
    hideTitle: false, // Show title for identification
    hideLogo: true // Hide logo to save space for QR code
  }
};

/**
 * Filter fields based on label size configuration
 * @param {Array} fields - All available fields
 * @param {string} labelSize - Selected label size (e.g., '4x6')
 * @returns {Array} Filtered fields based on priority and max count
 */
export const filterFieldsForLabelSize = (fields, labelSize) => {
  const config = LABEL_SIZES[labelSize];
  if (!config) return fields;

  // If showing all fields, return as-is
  if (config.priorityFields === 'all') {
    return fields;
  }

  // Filter based on priority fields
  const priorityLabels = config.priorityFields;
  const priorityFields = [];
  const otherFields = [];

  fields.forEach(field => {
    const isPriority = priorityLabels.some(label => 
      field.label.includes(label) || label.includes(field.label)
    );
    if (isPriority) {
      priorityFields.push(field);
    } else {
      otherFields.push(field);
    }
  });

  // Combine priority fields first, then others up to maxFields
  const result = [...priorityFields, ...otherFields].slice(0, config.maxFields);
  return result;
};

/**
 * Generate print CSS for a specific label size
 * @param {string} labelSize - Selected label size
 * @param {boolean} isTransfer - Whether this is a transfer label
 * @returns {string} CSS string for print media
 */
export const generatePrintCSS = (labelSize, isTransfer = false) => {
  const config = LABEL_SIZES[labelSize];
  if (!config) return '';

  return `
    @page {
      size: ${config.labelWidth} ${config.labelHeight};
      margin: ${config.margins.page};
    }

    body {
      margin: 0;
      padding: 0;
      width: ${config.labelWidth};
      height: ${config.labelHeight};
      font-family: Arial, sans-serif;
    }

    .label-container {
      width: 100%;
      height: 100%;
      padding: ${config.margins.content};
      box-sizing: border-box;
      display: flex;
      flex-direction: column;
    }

    .logo-header {
      text-align: center;
      font-size: ${config.fontSize.logo};
      font-weight: bold;
      color: #0066ff;
      margin-bottom: ${labelSize === '2x2' ? '4px' : '8px'};
      padding-bottom: ${labelSize === '2x2' ? '3px' : '6px'};
      border-bottom: 2px solid #0066ff;
      display: ${config.hideLogo ? 'none' : 'flex'};
      align-items: center;
      justify-content: center;
    }

    .title {
      text-align: center;
      font-size: ${config.fontSize.title};
      font-weight: 600;
      margin-bottom: ${labelSize === '2x2' ? '4px' : '8px'};
      display: ${config.hideTitle ? 'none' : 'block'};
    }

    .warning-badge {
      text-align: center;
      background-color: #ffc107;
      color: #000;
      padding: ${labelSize === '2x2' ? '3px' : '6px'};
      font-weight: bold;
      font-size: ${config.fontSize.warning};
      margin-bottom: ${labelSize === '2x2' ? '4px' : '8px'};
      border-radius: 3px;
      display: ${isTransfer ? 'block' : 'none'};
    }

    .code-container {
      text-align: center;
      margin: ${labelSize === '2x2' ? '4px 0' : '8px 0'};
      flex-shrink: 0;
    }

    .code-container svg {
      max-width: 100%;
      height: auto;
    }

    .info-fields {
      font-size: ${config.fontSize.fieldLabel};
      margin-top: ${labelSize === '2x2' ? '4px' : '8px'};
      flex-grow: 1;
      overflow: hidden;
    }

    .field-row {
      display: flex;
      padding: ${labelSize === '2x2' ? '2px 0' : '4px 0'};
      border-bottom: 1px solid #e0e0e0;
      line-height: 1.3;
    }

    .field-row:last-child {
      border-bottom: none;
    }

    .field-label {
      font-weight: 600;
      color: #555;
      min-width: ${labelSize === '2x2' ? '60px' : labelSize === '2x4' ? '80px' : '120px'};
      flex-shrink: 0;
      font-size: ${config.fontSize.fieldLabel};
    }

    .field-value {
      color: #333;
      flex: 1;
      word-break: break-word;
      font-size: ${config.fontSize.fieldValue};
    }

    .transfer-note {
      margin-top: ${labelSize === '2x2' ? '4px' : '8px'};
      padding: ${labelSize === '2x2' ? '3px' : '6px'};
      background-color: #fff3cd;
      border: 1px solid #ffc107;
      border-radius: 3px;
      font-size: ${config.fontSize.note};
      color: #856404;
      display: ${isTransfer ? 'block' : 'none'};
    }

    button {
      display: none !important;
    }

    /* Hide elements that shouldn't print */
    @media print {
      .no-print {
        display: none !important;
      }
    }
  `;
};

/**
 * Get barcode configuration for a specific label size
 * @param {string} labelSize - Selected label size
 * @returns {Object} JsBarcode configuration object
 */
export const getBarcodeConfig = (labelSize) => {
  const config = LABEL_SIZES[labelSize];
  if (!config) {
    return {
      format: "CODE128",
      lineColor: "#000",
      width: 2,
      height: 80,
      displayValue: true,
      fontSize: 14,
      margin: 10,
      textMargin: 8
    };
  }

  // Adjust bar width based on label size to ensure barcode fits
  let barWidth;
  switch (labelSize) {
    case '2x2':
      barWidth = 1;
      break;
    case '2x4':
      barWidth = 1.2;
      break;
    case '3x4':
      barWidth = 1.5;
      break;
    case '4x6':
    default:
      barWidth = 2;
      break;
  }

  return {
    format: "CODE128",
    lineColor: "#000",
    width: barWidth,
    height: config.barcodeHeight,
    displayValue: true,
    fontSize: parseInt(config.fontSize.fieldValue),
    margin: labelSize === '2x2' ? 3 : labelSize === '2x4' ? 5 : 8,
    textMargin: labelSize === '2x2' ? 2 : labelSize === '2x4' ? 4 : 6
  };
};

/**
 * Get QR code size for a specific label size
 * @param {string} labelSize - Selected label size
 * @returns {number} QR code size in pixels
 */
export const getQRCodeSize = (labelSize) => {
  const config = LABEL_SIZES[labelSize];
  return config ? config.qrSize : 200;
};

