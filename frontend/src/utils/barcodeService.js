/**
 * Barcode Service
 * 
 * Unified service for generating and printing professional PDF barcode labels.
 * Handles all item types (tools, chemicals, expendables, kit items) with
 * support for multiple label sizes and code types.
 */

import api from '../services/api';

/**
 * Label size options
 */
export const LABEL_SIZES = {
  '4x6': {
    id: '4x6',
    name: '4" × 6" (Standard Shipping Label)',
    description: 'Full-size label with all fields',
  },
  '3x4': {
    id: '3x4',
    name: '3" × 4" (Medium Label)',
    description: 'Medium label with priority fields',
  },
  '2x4': {
    id: '2x4',
    name: '2" × 4" (Small Label)',
    description: 'Small label with essential fields',
  },
  '2x2': {
    id: '2x2',
    name: '2" × 2" (Compact Label)',
    description: 'Compact label with minimal fields',
  },
};

/**
 * Code type options
 */
export const CODE_TYPES = {
  barcode: {
    id: 'barcode',
    name: '1D Barcode',
    description: 'Standard linear barcode (CODE128)',
  },
  qrcode: {
    id: 'qrcode',
    name: 'QR Code',
    description: '2D QR code for URLs and detailed data',
  },
};

/**
 * Generate a PDF label for a tool
 * 
 * @param {number} toolId - Tool ID
 * @param {string} labelSize - Label size (4x6, 3x4, 2x4, 2x2)
 * @param {string} codeType - Code type (barcode, qrcode)
 * @returns {Promise<Blob>} PDF blob
 */
export async function generateToolLabel(toolId, labelSize = '4x6', codeType = 'barcode') {
  try {
    const response = await api.get(`/barcode/tool/${toolId}`, {
      params: { label_size: labelSize, code_type: codeType },
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error generating tool label:', error);
    throw new Error('Failed to generate tool label');
  }
}

/**
 * Generate a PDF label for a chemical
 * 
 * @param {number} chemicalId - Chemical ID
 * @param {string} labelSize - Label size (4x6, 3x4, 2x4, 2x2)
 * @param {string} codeType - Code type (barcode, qrcode)
 * @param {boolean} isTransfer - Whether this is a transfer label
 * @param {Object} transferData - Transfer metadata (optional)
 * @returns {Promise<Blob>} PDF blob
 */
export async function generateChemicalLabel(
  chemicalId,
  labelSize = '4x6',
  codeType = 'barcode',
  isTransfer = false,
  transferData = null
) {
  try {
    const params = {
      label_size: labelSize,
      code_type: codeType,
      is_transfer: isTransfer,
    };

    if (isTransfer && transferData) {
      if (transferData.parent_lot_number) {
        params.parent_lot_number = transferData.parent_lot_number;
      }
      if (transferData.destination) {
        params.destination = transferData.destination;
      }
    }

    const response = await api.get(`/barcode/chemical/${chemicalId}`, {
      params,
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error generating chemical label:', error);
    throw new Error('Failed to generate chemical label');
  }
}

/**
 * Generate a PDF label for an expendable
 *
 * @param {number} expendableId - Expendable ID
 * @param {string} labelSize - Label size (4x6, 3x4, 2x4, 2x2)
 * @param {string} codeType - Code type (barcode, qrcode)
 * @returns {Promise<Blob>} PDF blob
 */
export async function generateExpendableLabel(
  expendableId,
  labelSize = '4x6',
  codeType = 'barcode'
) {
  try {
    const response = await api.get(`/barcode/expendable/${expendableId}`, {
      params: { label_size: labelSize, code_type: codeType },
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error generating expendable label:', error);
    throw new Error('Failed to generate expendable label');
  }
}

/**
 * Generate a PDF label for a kit item
 *
 * @param {number} itemId - Item ID (the underlying entity ID)
 * @param {string} itemType - Item type (tool, chemical, expendable)
 * @param {string} labelSize - Label size (4x6, 3x4, 2x4, 2x2)
 * @param {string} codeType - Code type (barcode, qrcode)
 * @returns {Promise<Blob>} PDF blob
 */
export async function generateKitItemLabel(
  itemId,
  itemType,
  labelSize = '4x6',
  codeType = 'barcode'
) {
  try {
    // Route to the appropriate endpoint based on item type
    let endpoint;
    switch (itemType) {
      case 'tool':
        endpoint = `/barcode/tool/${itemId}`;
        break;
      case 'chemical':
        endpoint = `/barcode/chemical/${itemId}`;
        break;
      case 'expendable':
        endpoint = `/barcode/expendable/${itemId}`;
        break;
      default:
        throw new Error(`Unknown item type: ${itemType}`);
    }

    const response = await api.get(endpoint, {
      params: {
        label_size: labelSize,
        code_type: codeType,
      },
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error generating kit item label:', error);
    throw new Error('Failed to generate kit item label');
  }
}

/**
 * Open a PDF blob in a new window for printing
 * 
 * @param {Blob} pdfBlob - PDF blob to print
 * @param {string} filename - Optional filename for the PDF
 */
export function printPdfLabel(pdfBlob, filename = 'label.pdf') {
  try {
    // Create object URL from blob
    const url = URL.createObjectURL(pdfBlob);

    // Open in new window
    const printWindow = window.open(url, '_blank');

    if (printWindow) {
      // Wait for PDF to load, then trigger print dialog
      printWindow.onload = () => {
        printWindow.print();
      };

      // Clean up object URL after a delay
      setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 60000); // 1 minute
    } else {
      // Fallback: download the PDF if popup was blocked
      downloadPdfLabel(pdfBlob, filename);
    }
  } catch (error) {
    console.error('Error printing PDF label:', error);
    throw new Error('Failed to print label');
  }
}

/**
 * Download a PDF blob as a file
 * 
 * @param {Blob} pdfBlob - PDF blob to download
 * @param {string} filename - Filename for the download
 */
export function downloadPdfLabel(pdfBlob, filename = 'label.pdf') {
  try {
    // Create object URL from blob
    const url = URL.createObjectURL(pdfBlob);

    // Create temporary download link
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);

    // Trigger download
    link.click();

    // Clean up
    document.body.removeChild(link);
    setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 100);
  } catch (error) {
    console.error('Error downloading PDF label:', error);
    throw new Error('Failed to download label');
  }
}

/**
 * Generate and print a label in one step
 * 
 * @param {string} itemType - Item type (tool, chemical, expendable, kit_item)
 * @param {Object} params - Parameters for label generation
 * @returns {Promise<void>}
 */
export async function generateAndPrintLabel(itemType, params) {
  try {
    let pdfBlob;
    let filename;

    switch (itemType) {
      case 'tool':
        pdfBlob = await generateToolLabel(
          params.toolId,
          params.labelSize,
          params.codeType
        );
        filename = `tool-${params.toolId}-label.pdf`;
        break;

      case 'chemical':
        pdfBlob = await generateChemicalLabel(
          params.chemicalId,
          params.labelSize,
          params.codeType,
          params.isTransfer,
          params.transferData
        );
        filename = params.isTransfer
          ? `transfer-${params.chemicalId}-label.pdf`
          : `chemical-${params.chemicalId}-label.pdf`;
        break;

      case 'expendable':
        pdfBlob = await generateExpendableLabel(
          params.expendableId,
          params.labelSize,
          params.codeType
        );
        filename = `expendable-${params.expendableId}-label.pdf`;
        break;

      case 'kit_item':
        pdfBlob = await generateKitItemLabel(
          params.kitId,
          params.itemId,
          params.itemItemType,
          params.labelSize,
          params.codeType
        );
        filename = `kit-${params.kitId}-item-${params.itemId}-label.pdf`;
        break;

      default:
        throw new Error(`Unknown item type: ${itemType}`);
    }

    printPdfLabel(pdfBlob, filename);
  } catch (error) {
    console.error('Error generating and printing label:', error);
    throw error;
  }
}

/**
 * Get available label sizes from the backend
 *
 * @returns {Promise<Object>} Label sizes configuration
 */
export async function getLabelSizes() {
  try {
    const response = await api.get('/barcode/label-sizes');
    return response.data;
  } catch (error) {
    console.error('Error fetching label sizes:', error);
    // Return default sizes if API call fails
    return LABEL_SIZES;
  }
}

