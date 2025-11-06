# Barcode & Label System Documentation

## Overview

The SupplyLine MRO Suite features a professional PDF-based barcode and label system designed for high-quality printing of inventory labels. The system supports multiple label sizes, both 1D barcodes and 2D QR codes, and is optimized for both standard PDF printing and future Zebra printer compatibility.

## Key Features

- **Professional PDF Generation**: WeasyPrint-powered PDF creation with magazine-quality typography
- **Vector Graphics**: SVG-based barcodes and QR codes for crisp printing at any resolution
- **Multiple Label Sizes**: 4x6, 3x4, 2x4, and 2x2 inch labels with responsive content scaling
- **Unified API**: Consistent endpoint pattern for all item types (tools, chemicals, expendables, kit items)
- **Automatic Printing**: Barcode modals appear automatically after transfers and partial issuances
- **Future-Ready**: Designed for Zebra printer compatibility while supporting standard PDF printing

## Architecture

### Backend Components

#### 1. Routes (`backend/routes_barcode.py`)
Unified API endpoints for generating barcode labels:

```python
GET /api/barcode/tool/<tool_id>
GET /api/barcode/chemical/<chemical_id>
GET /api/barcode/expendable/<expendable_id>
```

**Query Parameters:**
- `label_size`: Label size (4x6, 3x4, 2x4, 2x2) - default: 4x6
- `code_type`: Code type (barcode, qrcode) - default: barcode

**Chemical-Specific Parameters:**
- `is_transfer`: Whether this is a transfer label - default: false
- `parent_lot_number`: Parent lot number (for transfers)
- `destination`: Destination name (for transfers)

#### 2. Label PDF Service (`backend/utils/label_pdf_service.py`)
Core service for generating PDF labels:

```python
def generate_tool_label_pdf(tool, label_size='4x6', code_type='barcode')
def generate_chemical_label_pdf(chemical, label_size='4x6', code_type='barcode', ...)
def generate_expendable_label_pdf(expendable, label_size='4x6', code_type='barcode')
```

**Features:**
- Jinja2 template rendering
- WeasyPrint PDF generation
- SVG barcode/QR code embedding
- Responsive content scaling based on label size

#### 3. Label Configuration (`backend/utils/label_config.py`)
Defines label sizes and dimensions:

```python
LABEL_SIZES = {
    '4x6': {'width': 4, 'height': 6, 'unit': 'in'},
    '3x4': {'width': 3, 'height': 4, 'unit': 'in'},
    '2x4': {'width': 2, 'height': 4, 'unit': 'in'},
    '2x2': {'width': 2, 'height': 2, 'unit': 'in'}
}
```

#### 4. Barcode Service (`backend/utils/barcode_service.py`)
Generates barcode and QR code SVG graphics:

```python
def generate_barcode_svg(data, barcode_type='code128')
def generate_qrcode_svg(data, scale=10)
```

**Supported Barcode Types:**
- Code128 (default)
- Code39
- EAN13
- UPC-A

#### 5. HTML Templates (`backend/templates/labels/`)
Jinja2 templates for label layouts:

- `base_label.html`: Base template with common styling
- Tool-specific layouts
- Chemical-specific layouts
- Expendable-specific layouts

### Frontend Components

#### 1. Barcode Service (`frontend/src/utils/barcodeService.js`)
Centralized service for generating barcode PDFs:

```javascript
export const generateToolBarcode = async (toolId, labelSize = '4x6', codeType = 'barcode')
export const generateChemicalBarcode = async (chemicalId, labelSize = '4x6', codeType = 'barcode', options = {})
export const generateExpendableBarcode = async (expendableId, labelSize = '4x6', codeType = 'barcode')
```

**Features:**
- Automatic PDF download
- Print dialog opening
- Error handling
- Loading states

#### 2. Barcode Components

**ToolBarcode.jsx**
```jsx
<ToolBarcode
  tool={tool}
  show={showModal}
  onHide={() => setShowModal(false)}
/>
```

**ChemicalBarcode.jsx**
```jsx
<ChemicalBarcode
  chemical={chemical}
  show={showModal}
  onHide={() => setShowModal(false)}
  isTransfer={false}
  parentLotNumber=""
  destination=""
/>
```

**ExpendableBarcode.jsx**
```jsx
<ExpendableBarcode
  expendable={expendable}
  show={showModal}
  onHide={() => setShowModal(false)}
/>
```

**KitItemBarcode.jsx**
```jsx
<KitItemBarcode
  item={item}
  show={showModal}
  onHide={() => setShowModal(false)}
/>
```

## Label Sizes

### 4x6 Inch (Default)
- **Use Case**: Standard shipping labels, detailed item information
- **Content**: Full item details, large barcode/QR code, calibration info
- **Recommended For**: Tools, chemicals with extensive information

### 3x4 Inch
- **Use Case**: Medium-sized labels for boxes and containers
- **Content**: Essential item details, medium barcode/QR code
- **Recommended For**: Kit boxes, chemical containers

### 2x4 Inch
- **Use Case**: Compact labels for smaller items
- **Content**: Key item details, compact barcode/QR code
- **Recommended For**: Small tools, expendables

### 2x2 Inch
- **Use Case**: Minimal labels for very small items
- **Content**: Item identifier, small barcode/QR code
- **Recommended For**: Small parts, fasteners, minimal labeling needs

## Usage Examples

### Backend API Usage

#### Generate Tool Label
```bash
GET /api/barcode/tool/123?label_size=4x6&code_type=barcode
```

#### Generate Chemical Transfer Label
```bash
GET /api/barcode/chemical/456?label_size=3x4&code_type=qrcode&is_transfer=true&parent_lot_number=LOT-251106-0001&destination=Kit%20A
```

#### Generate Expendable Label
```bash
GET /api/barcode/expendable/789?label_size=2x4&code_type=barcode
```

### Frontend Component Usage

#### Tool Barcode Modal
```javascript
import { useState } from 'react';
import ToolBarcode from './components/tools/ToolBarcode';

function ToolDetail({ tool }) {
  const [showBarcode, setShowBarcode] = useState(false);
  
  return (
    <>
      <button onClick={() => setShowBarcode(true)}>
        Print Barcode
      </button>
      
      <ToolBarcode
        tool={tool}
        show={showBarcode}
        onHide={() => setShowBarcode(false)}
      />
    </>
  );
}
```

#### Automatic Barcode After Transfer
```javascript
// After successful transfer
const handleTransferComplete = (transferredItem) => {
  setTransferredItem(transferredItem);
  setShowBarcodeModal(true);
};
```

## Barcode Content

### Tool Labels
- Tool Number
- Serial Number
- Description
- Category
- Location
- Calibration Date (if applicable)
- Calibration Due Date (if applicable)
- Barcode/QR Code

### Chemical Labels
- Part Number
- Lot Number
- Manufacturer
- Quantity and Unit
- Expiration Date
- Location
- Parent Lot Number (for child lots)
- Destination (for transfers)
- Barcode/QR Code

### Expendable Labels
- Part Number
- Lot/Serial Number
- Description
- Quantity and Unit
- Location
- Barcode/QR Code

## QR Code Landing Pages

QR codes link to mobile-friendly landing pages with detailed item information:

### Tool Landing Page
- Tool details
- Current location
- Calibration information
- Calibration certificate download
- Checkout history

### Chemical Landing Page
- Chemical details
- Lot information
- Expiration date
- Parent lot lineage
- Usage history

## Printing Workflow

### Standard PDF Printing

1. **Generate Label**: Click "Print Barcode" button
2. **Select Options**: Choose label size and code type
3. **Generate PDF**: System generates PDF label
4. **Print Dialog**: Browser print dialog opens automatically
5. **Print**: Select printer and print settings
6. **Apply Label**: Apply printed label to item

### Future Zebra Printer Support

The system is designed to support Zebra printers in future releases:

- ZPL (Zebra Programming Language) template generation
- Direct printer communication
- Label queue management
- Batch printing support

## Best Practices

### Label Size Selection
- **4x6**: Use for items requiring detailed information (tools with calibration, chemicals)
- **3x4**: Use for medium-sized items (kit boxes, chemical containers)
- **2x4**: Use for smaller items (small tools, expendables)
- **2x2**: Use for minimal labeling needs (small parts, fasteners)

### Barcode vs QR Code
- **Barcode**: Use for simple item identification, faster scanning
- **QR Code**: Use when linking to landing pages, more data capacity

### Print Quality
- Use high-quality label stock
- Ensure printer is set to highest quality
- Verify barcode scannability after printing
- Test QR codes with mobile devices

### Label Placement
- Place labels on flat, clean surfaces
- Avoid curved or textured surfaces
- Ensure labels are visible and accessible
- Protect labels from chemicals and abrasion

## Troubleshooting

### PDF Generation Issues
- **Error**: "Failed to generate PDF"
  - **Solution**: Check WeasyPrint installation, verify template files exist

### Barcode Scanning Issues
- **Error**: Barcode won't scan
  - **Solution**: Increase label size, use higher print quality, clean scanner lens

### QR Code Issues
- **Error**: QR code won't scan
  - **Solution**: Increase QR code size, ensure good lighting, use QR code reader app

### Print Quality Issues
- **Error**: Blurry or pixelated labels
  - **Solution**: Use vector graphics (SVG), increase printer DPI, use quality label stock

## API Reference

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference including:
- Request/response formats
- Error codes
- Authentication requirements
- Rate limiting

