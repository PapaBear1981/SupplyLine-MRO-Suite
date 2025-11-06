/**
 * Centralized barcode formatting utilities
 * Ensures consistent data formatting across all barcode displays
 */

/**
 * Format a value for display, returning "N/A" if the value is null, undefined, or empty
 * @param {*} value - The value to format
 * @param {string} defaultValue - The default value to return if value is missing (default: "N/A")
 * @returns {string} - Formatted value or default
 */
export const formatValue = (value, defaultValue = "N/A") => {
  if (value === null || value === undefined || value === "") {
    return defaultValue;
  }
  return String(value);
};

/**
 * Format a date for display
 * @param {string|Date} date - The date to format
 * @param {string} format - The format type: "short" (MM/DD/YYYY) or "long" (Month DD, YYYY)
 * @returns {string} - Formatted date or "N/A"
 */
export const formatDate = (date, format = "short") => {
  if (!date) {
    return "N/A";
  }

  try {
    const dateObj = typeof date === "string" ? new Date(date) : date;
    
    if (isNaN(dateObj.getTime())) {
      return "N/A";
    }

    if (format === "long") {
      return dateObj.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    }

    // Short format: MM/DD/YYYY
    return dateObj.toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
  } catch (error) {
    console.error("Error formatting date:", error);
    return "N/A";
  }
};

/**
 * Format a boolean value for display
 * @param {boolean} value - The boolean value
 * @param {string} trueText - Text to display for true (default: "Yes")
 * @param {string} falseText - Text to display for false (default: "No")
 * @returns {string} - Formatted boolean or "N/A"
 */
export const formatBoolean = (value, trueText = "Yes", falseText = "No") => {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return value ? trueText : falseText;
};

/**
 * Format quantity with unit
 * @param {number} quantity - The quantity value
 * @param {string} unit - The unit of measurement
 * @returns {string} - Formatted quantity with unit or "N/A"
 */
export const formatQuantity = (quantity, unit) => {
  if (quantity === null || quantity === undefined) {
    return "N/A";
  }
  if (!unit) {
    return String(quantity);
  }
  return `${quantity} ${unit}`;
};

/**
 * Get standard chemical barcode fields in correct order
 * @param {Object} chemical - The chemical object
 * @param {Object} options - Additional options (isTransfer, transferData)
 * @returns {Array} - Array of field objects {label, value}
 */
export const getChemicalBarcodeFields = (chemical, options = {}) => {
  const { isTransfer = false, transferData = {} } = options;

  const fields = [
    { label: "Part Number", value: formatValue(chemical.part_number) },
    { label: "Lot Number", value: formatValue(chemical.lot_number) },
    { label: "Description", value: formatValue(chemical.description) },
    { label: "Location", value: formatValue(chemical.location) },
    { label: "Manufacturer", value: formatValue(chemical.manufacturer) },
    { label: "Expiration Date", value: formatDate(chemical.expiration_date) },
    { label: "Status", value: formatValue(chemical.status) },
    { label: "Created Date", value: formatDate(chemical.created_at) },
  ];

  // Add transfer-specific fields if this is a transfer barcode
  if (isTransfer) {
    fields.push(
      { label: "Quantity", value: formatQuantity(transferData.quantity, transferData.unit) },
      { label: "Parent Lot", value: formatValue(transferData.parent_lot_number) },
      { label: "Destination", value: formatValue(transferData.destination) },
      { label: "Transfer Date", value: formatDate(transferData.transfer_date) }
    );
  }

  return fields;
};

/**
 * Get standard tool barcode fields in correct order
 * @param {Object} tool - The tool object
 * @param {Object} calibration - The calibration object (optional)
 * @returns {Array} - Array of field objects {label, value}
 */
export const getToolBarcodeFields = (tool, calibration = null) => {
  const fields = [
    { label: "Tool Number", value: formatValue(tool.tool_number) },
    { label: "Serial Number", value: formatValue(tool.serial_number) },
    { label: "Lot Number", value: formatValue(tool.lot_number) },
    { label: "Description", value: formatValue(tool.description) },
    { label: "Location", value: formatValue(tool.location) },
    { label: "Category", value: formatValue(tool.category) },
    { label: "Condition", value: formatValue(tool.condition) },
    { label: "Status", value: formatValue(tool.status) },
    { label: "Created Date", value: formatDate(tool.created_at) },
  ];

  // Add calibration fields
  fields.push(
    { label: "Requires Calibration", value: formatBoolean(tool.requires_calibration) }
  );

  if (tool.requires_calibration) {
    fields.push(
      { label: "Last Calibration", value: formatDate(calibration?.calibration_date || tool.last_calibration_date) },
      { label: "Next Calibration Due", value: formatDate(calibration?.next_calibration_date || tool.next_calibration_date) },
      { label: "Calibration Status", value: formatValue(calibration?.calibration_status) }
    );
  } else {
    fields.push(
      { label: "Last Calibration", value: "N/A" },
      { label: "Next Calibration Due", value: "N/A" },
      { label: "Calibration Status", value: "N/A" }
    );
  }

  return fields;
};

/**
 * Generate barcode data string for chemicals
 * @param {Object} chemical - The chemical object
 * @returns {string} - Barcode data string
 */
export const generateChemicalBarcodeData = (chemical) => {
  const partNumber = chemical.part_number || "";
  const lotNumber = chemical.lot_number || "";
  const expirationDate = chemical.expiration_date
    ? new Date(chemical.expiration_date).toISOString().slice(0, 10).replace(/-/g, "")
    : "NOEXP";

  return `${partNumber}-${lotNumber}-${expirationDate}`;
};

/**
 * Generate barcode data string for tools
 * @param {Object} tool - The tool object
 * @returns {string} - Barcode data string
 */
export const generateToolBarcodeData = (tool) => {
  const toolNumber = tool.tool_number || "";

  if (tool.lot_number) {
    return `${toolNumber}-LOT-${tool.lot_number}`;
  } else {
    return `${toolNumber}-${tool.serial_number || ""}`;
  }
};

/**
 * Get standard expendable barcode fields in correct order
 * @param {Object} expendable - The expendable object
 * @returns {Array} - Array of field objects {label, value}
 */
export const getExpendableBarcodeFields = (expendable) => {
  const fields = [
    { label: "Part Number", value: formatValue(expendable.part_number) },
    { label: "Serial Number", value: formatValue(expendable.serial_number) },
    { label: "Lot Number", value: formatValue(expendable.lot_number) },
    { label: "Description", value: formatValue(expendable.description) },
    { label: "Manufacturer", value: formatValue(expendable.manufacturer) },
    { label: "Quantity", value: formatQuantity(expendable.quantity, expendable.unit) },
    { label: "Status", value: formatValue(expendable.status) },
    { label: "Created Date", value: formatDate(expendable.created_at) },
  ];

  return fields;
};

/**
 * Generate barcode data string for expendables
 * @param {Object} expendable - The expendable object
 * @returns {string} - Barcode data string
 */
export const generateExpendableBarcodeData = (expendable) => {
  const partNumber = expendable.part_number || "";

  if (expendable.lot_number) {
    return `${partNumber}-LOT-${expendable.lot_number}`;
  } else {
    return `${partNumber}-SN-${expendable.serial_number || ""}`;
  }
};
