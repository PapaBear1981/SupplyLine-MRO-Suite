# Expendables System Documentation

## Overview

The Expendables System in SupplyLine MRO Suite provides a streamlined way to manage consumable items that are stored directly within mobile kits without the overhead of warehouse management. This system is designed for items that are consumed during maintenance operations and need to be tracked at the kit level.

## Key Features

- **Kit-Only Storage**: Add consumables directly to kits without warehouse management
- **Full CRUD Operations**: Complete create, read, update, delete functionality
- **Lot/Serial Tracking**: Mutually exclusive lot or serial number validation
- **Auto-Complete Transfers**: Immediate feedback for warehouse-to-kit transfers
- **Integrated Workflow**: Seamless integration with kit transfers and reorder systems
- **Barcode Printing**: Professional PDF labels for all expendables

## What Are Expendables?

Expendables are consumable items that:
- Are used up during maintenance operations
- Don't require individual serial number tracking (though optional)
- Are stored directly in kits for immediate use
- Don't need warehouse-level inventory management
- Are typically low-cost, high-volume items

### Examples of Expendables
- Fasteners (bolts, nuts, screws, washers)
- O-rings and seals
- Safety wire
- Cleaning supplies
- Disposable gloves
- Shop towels
- Zip ties
- Tape (duct tape, masking tape, etc.)
- Lubricants (small quantities)
- Consumable abrasives

## Expendable Model

### Expendable Properties

```python
{
    "id": 1,
    "part_number": "EXP-001",
    "description": "AN3 Bolt Kit - Assorted Lengths",
    "quantity": 100,
    "unit": "pieces",
    "lot_number": "LOT-251106-0001",  # Optional, mutually exclusive with serial_number
    "serial_number": None,  # Optional, mutually exclusive with lot_number
    "warehouse_id": 1,  # Optional, for warehouse-stored expendables
    "location": "Bin A-5",
    "notes": "Assorted AN3 bolts for general use",
    "created_at": "2025-11-06T10:00:00Z",
    "updated_at": "2025-11-06T10:00:00Z"
}
```

### Validation Rules

1. **Lot/Serial Exclusivity**: An expendable can have EITHER a lot number OR a serial number, never both
2. **Quantity Required**: Quantity must be specified and greater than 0
3. **Unit Required**: Unit of measurement must be specified
4. **Part Number Required**: Part number is required and should be unique per lot/serial

## API Endpoints

### List Expendables
```http
GET /api/expendables
```

**Query Parameters:**
- `warehouse_id`: Filter by warehouse
- `kit_id`: Filter by kit (via KitItem relationship)
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 50, max: 200)

**Response:**
```json
{
    "expendables": [
        {
            "id": 1,
            "part_number": "EXP-001",
            "description": "AN3 Bolt Kit",
            "quantity": 100,
            "unit": "pieces",
            "lot_number": "LOT-251106-0001",
            "warehouse_id": 1,
            "location": "Bin A-5"
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 50,
    "pages": 1
}
```

### Create Expendable
```http
POST /api/expendables
```

**Request Body:**
```json
{
    "part_number": "EXP-002",
    "description": "O-Ring Kit - Various Sizes",
    "quantity": 50,
    "unit": "pieces",
    "lot_number": "LOT-251106-0002",
    "warehouse_id": 1,
    "location": "Cabinet B-3",
    "notes": "Assorted O-rings for hydraulic systems"
}
```

**Required Fields:**
- `part_number`: Part number
- `description`: Item description
- `quantity`: Quantity (must be > 0)
- `unit`: Unit of measurement

**Optional Fields:**
- `lot_number`: Lot number (mutually exclusive with serial_number)
- `serial_number`: Serial number (mutually exclusive with lot_number)
- `warehouse_id`: Warehouse ID (for warehouse storage)
- `location`: Location within warehouse or kit
- `notes`: Additional notes

**Response:**
```json
{
    "message": "Expendable created successfully",
    "expendable": {
        "id": 2,
        "part_number": "EXP-002",
        "description": "O-Ring Kit - Various Sizes",
        "quantity": 50,
        "unit": "pieces"
    }
}
```

### Get Expendable Details
```http
GET /api/expendables/:id
```

**Response:**
```json
{
    "id": 1,
    "part_number": "EXP-001",
    "description": "AN3 Bolt Kit - Assorted Lengths",
    "quantity": 100,
    "unit": "pieces",
    "lot_number": "LOT-251106-0001",
    "serial_number": null,
    "warehouse_id": 1,
    "location": "Bin A-5",
    "notes": "Assorted AN3 bolts for general use",
    "created_at": "2025-11-06T10:00:00Z",
    "updated_at": "2025-11-06T10:00:00Z"
}
```

### Update Expendable
```http
PUT /api/expendables/:id
```

**Request Body:**
```json
{
    "quantity": 75,
    "location": "Bin A-6",
    "notes": "Updated location after reorganization"
}
```

**Updatable Fields:**
- `description`: Item description
- `quantity`: Quantity
- `unit`: Unit of measurement
- `lot_number`: Lot number
- `serial_number`: Serial number
- `warehouse_id`: Warehouse ID
- `location`: Location
- `notes`: Notes

**Response:**
```json
{
    "message": "Expendable updated successfully",
    "expendable": {
        "id": 1,
        "quantity": 75,
        "location": "Bin A-6"
    }
}
```

### Delete Expendable
```http
DELETE /api/expendables/:id
```

**Response:**
```json
{
    "message": "Expendable deleted successfully"
}
```

**Note:** Expendables are hard-deleted if not referenced by any kit items. If referenced, they are marked as inactive.

## Kit Integration

### Adding Expendables to Kits

Expendables can be added to kits in two ways:

#### 1. Direct Addition (Kit-Only Expendables)
Create expendable directly in kit without warehouse storage:

```http
POST /api/kits/:kit_id/expendables
```

**Request Body:**
```json
{
    "part_number": "EXP-003",
    "description": "Safety Wire - 0.032 inch",
    "quantity": 10,
    "unit": "feet",
    "box_id": 5,
    "location": "Box 3"
}
```

#### 2. Transfer from Warehouse
Transfer existing expendable from warehouse to kit:

```http
POST /api/transfers/warehouse-to-kit
```

**Request Body:**
```json
{
    "warehouse_id": 1,
    "kit_id": 5,
    "box_id": 12,
    "item_type": "expendable",
    "item_id": 1,
    "quantity": 25,
    "notes": "Transferred for Q400 maintenance"
}
```

### Issuing Expendables from Kits

```http
POST /api/kits/:kit_id/issue
```

**Request Body:**
```json
{
    "items": [
        {
            "item_type": "expendable",
            "item_id": 1,
            "quantity": 5,
            "work_order": "WO-12345"
        }
    ],
    "issued_to": "John Smith",
    "notes": "Issued for hydraulic system repair"
}
```

### Reordering Expendables

When expendables run low, create a reorder request:

```http
POST /api/kits/:kit_id/reorder
```

**Request Body:**
```json
{
    "item_type": "expendable",
    "item_id": 1,
    "quantity_requested": 50,
    "priority": "high",
    "notes": "Running low on AN3 bolts"
}
```

## Barcode Printing

### Generate Expendable Barcode Label

```http
GET /api/barcode/expendable/:id?label_size=4x6&code_type=barcode
```

**Label Sizes:**
- `4x6`: Standard shipping label (default)
- `3x4`: Medium label
- `2x4`: Compact label
- `2x2`: Minimal label

**Code Types:**
- `barcode`: 1D barcode (Code128)
- `qrcode`: 2D QR code

**Label Content:**
- Part Number
- Description
- Lot/Serial Number
- Quantity and Unit
- Location
- Barcode/QR Code

### Automatic Barcode Printing

Barcode modals appear automatically after:
- Creating new expendable
- Transferring expendable to kit
- Receiving reorder fulfillment

## Workflow Examples

### Example 1: Add Expendable Directly to Kit

1. **Create Expendable in Kit**:
   ```http
   POST /api/kits/5/expendables
   {
       "part_number": "EXP-004",
       "description": "Zip Ties - 8 inch",
       "quantity": 100,
       "unit": "pieces",
       "box_id": 3
   }
   ```

2. **Print Barcode**: Automatic barcode modal appears

3. **Apply Label**: Print and apply label to container

### Example 2: Transfer Expendable from Warehouse

1. **Create Expendable in Warehouse**:
   ```http
   POST /api/expendables
   {
       "part_number": "EXP-005",
       "description": "Shop Towels",
       "quantity": 200,
       "unit": "pieces",
       "warehouse_id": 1,
       "location": "Shelf C-2"
   }
   ```

2. **Transfer to Kit**:
   ```http
   POST /api/transfers/warehouse-to-kit
   {
       "warehouse_id": 1,
       "kit_id": 5,
       "box_id": 4,
       "item_type": "expendable",
       "item_id": 5,
       "quantity": 50
   }
   ```

3. **Print Transfer Label**: Automatic barcode modal appears

### Example 3: Issue and Reorder

1. **Issue Expendable**:
   ```http
   POST /api/kits/5/issue
   {
       "items": [
           {
               "item_type": "expendable",
               "item_id": 4,
               "quantity": 75
           }
       ],
       "issued_to": "Maintenance Team A"
   }
   ```

2. **Automatic Reorder Trigger**: System checks if quantity below threshold

3. **Create Reorder Request**:
   ```http
   POST /api/kits/5/reorder
   {
       "item_type": "expendable",
       "item_id": 4,
       "quantity_requested": 100,
       "priority": "medium"
   }
   ```

4. **Fulfill Reorder**: Materials department fulfills request

5. **Update Quantity**: Expendable quantity automatically updated

## Best Practices

### Part Numbering
- Use consistent part number format (e.g., EXP-XXX)
- Include manufacturer part number in description
- Group similar items with sequential numbers

### Quantity Management
- Set appropriate minimum stock levels
- Monitor usage patterns
- Reorder before running out
- Use realistic quantities for kit storage

### Lot Number Tracking
- Use lot numbers for items with expiration dates
- Track lot numbers for quality control
- Use auto-generated lot numbers (LOT-YYMMDD-XXXX)

### Location Tracking
- Specify exact location within kit (box number, compartment)
- Update location when reorganizing
- Use consistent location naming

### Barcode Labels
- Print labels immediately after creation
- Apply labels to containers, not individual items
- Use appropriate label size for container
- Protect labels from damage

## Troubleshooting

### Common Issues

**Issue**: Cannot create expendable with both lot and serial number
- **Solution**: Choose either lot number OR serial number, not both

**Issue**: Transfer fails with "Insufficient quantity"
- **Solution**: Verify available quantity in source location

**Issue**: Reorder request not triggering automatically
- **Solution**: Check minimum stock level settings

**Issue**: Barcode won't scan
- **Solution**: Increase label size, use higher print quality

## See Also

- [Kits User Guide](KITS_USER_GUIDE.md) - Mobile warehouse/kits management
- [Warehouse Management](WAREHOUSE_MANAGEMENT.md) - Warehouse operations
- [Barcode System](BARCODE_SYSTEM.md) - Barcode and label printing
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference

