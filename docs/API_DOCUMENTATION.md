# SupplyLine MRO Suite API Documentation

## Overview

The SupplyLine MRO Suite provides a comprehensive REST API for managing tools, chemicals, expendables, warehouses, kits, transfers, and barcode generation. All endpoints require JWT authentication unless otherwise noted.

## Base URL

```
http://localhost:5000/api
```

## Authentication

### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
    "username": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "username": "user@example.com",
        "role": "admin"
    }
}
```

### Using Authentication

Include the JWT token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Warehouses API

### List Warehouses
```http
GET /warehouses
```

**Query Parameters:**
- `include_inactive` (boolean): Include inactive warehouses
- `warehouse_type` (string): Filter by type (main/satellite)
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 50, max: 200)

### Create Warehouse
```http
POST /warehouses
```

**Request Body:**
```json
{
    "name": "Main Warehouse",
    "address": "123 Aviation Way",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98101",
    "country": "USA",
    "warehouse_type": "main"
}
```

### Get Warehouse
```http
GET /warehouses/:id
```

### Update Warehouse
```http
PUT /warehouses/:id
```

### Delete Warehouse
```http
DELETE /warehouses/:id
```

## Tools API

### List Tools
```http
GET /tools
```

**Query Parameters:**
- `warehouse_id` (integer): Filter by warehouse
- `kit_id` (integer): Filter by kit
- `category` (string): Filter by category
- `status` (string): Filter by status
- `page` (integer): Page number
- `per_page` (integer): Items per page

### Create Tool
```http
POST /tools
```

**Request Body:**
```json
{
    "tool_number": "T-12345",
    "serial_number": "SN-67890",
    "description": "Torque Wrench",
    "category": "Q400",
    "warehouse_id": 1,
    "location": "Shelf A-5",
    "calibration_date": "2025-01-15",
    "calibration_due_date": "2026-01-15"
}
```

### Get Tool
```http
GET /tools/:id
```

### Update Tool
```http
PUT /tools/:id
```

### Delete Tool
```http
DELETE /tools/:id
```

## Chemicals API

### List Chemicals
```http
GET /chemicals
```

**Query Parameters:**
- `warehouse_id` (integer): Filter by warehouse
- `kit_id` (integer): Filter by kit
- `status` (string): Filter by status
- `page` (integer): Page number
- `per_page` (integer): Items per page

### Create Chemical
```http
POST /chemicals
```

**Request Body:**
```json
{
    "part_number": "CHEM-001",
    "lot_number": "LOT-251106-0001",
    "manufacturer": "AeroSeal Inc",
    "quantity": 10,
    "unit": "gallons",
    "warehouse_id": 1,
    "location": "Cabinet B-3",
    "expiration_date": "2026-12-31"
}
```

### Get Chemical
```http
GET /chemicals/:id
```

### Update Chemical
```http
PUT /chemicals/:id
```

### Delete Chemical
```http
DELETE /chemicals/:id
```

### Issue Chemical (Partial)
```http
POST /chemicals/:id/issue
```

**Request Body:**
```json
{
    "quantity": 2.5,
    "destination": "Kit A",
    "work_order": "WO-12345",
    "notes": "Partial issuance for maintenance"
}
```

**Response:**
```json
{
    "message": "Chemical issued successfully",
    "parent_chemical": {
        "id": 1,
        "quantity": 7.5
    },
    "child_chemical": {
        "id": 2,
        "lot_number": "LOT-251106-0002",
        "quantity": 2.5,
        "parent_lot_number": "LOT-251106-0001"
    }
}
```

## Expendables API

### List Expendables
```http
GET /expendables
```

**Query Parameters:**
- `warehouse_id` (integer): Filter by warehouse
- `kit_id` (integer): Filter by kit
- `page` (integer): Page number
- `per_page` (integer): Items per page

### Create Expendable
```http
POST /expendables
```

**Request Body:**
```json
{
    "part_number": "EXP-001",
    "description": "AN3 Bolt Kit",
    "quantity": 100,
    "unit": "pieces",
    "lot_number": "LOT-251106-0001",
    "warehouse_id": 1,
    "location": "Bin A-5"
}
```

### Get Expendable
```http
GET /expendables/:id
```

### Update Expendable
```http
PUT /expendables/:id
```

### Delete Expendable
```http
DELETE /expendables/:id
```

## Kits API

### List Kits
```http
GET /kits
```

**Query Parameters:**
- `aircraft_type` (string): Filter by aircraft type
- `status` (string): Filter by status
- `page` (integer): Page number
- `per_page` (integer): Items per page

### Create Kit
```http
POST /kits
```

**Request Body:**
```json
{
    "name": "Q400 Kit #1",
    "aircraft_type": "Q400",
    "description": "Main maintenance kit for Q400",
    "boxes": [
        {
            "box_number": 1,
            "box_type": "expendable",
            "description": "Fasteners and consumables"
        },
        {
            "box_number": 2,
            "box_type": "tooling",
            "description": "Hand tools"
        }
    ]
}
```

### Get Kit
```http
GET /kits/:id
```

### Update Kit
```http
PUT /kits/:id
```

### Delete Kit
```http
DELETE /kits/:id
```

### Get Kit Items
```http
GET /kits/:id/items
```

**Query Parameters:**
- `box_id` (integer): Filter by box
- `item_type` (string): Filter by type (tool/chemical/expendable)
- `status` (string): Filter by status

### Add Expendable to Kit
```http
POST /kits/:id/expendables
```

**Request Body:**
```json
{
    "part_number": "EXP-003",
    "description": "Safety Wire",
    "quantity": 10,
    "unit": "feet",
    "box_id": 5,
    "location": "Box 3"
}
```

### Issue Items from Kit
```http
POST /kits/:id/issue
```

**Request Body:**
```json
{
    "items": [
        {
            "item_type": "chemical",
            "item_id": 1,
            "quantity": 2.5,
            "work_order": "WO-12345"
        },
        {
            "item_type": "expendable",
            "item_id": 5,
            "quantity": 10,
            "work_order": "WO-12345"
        }
    ],
    "issued_to": "John Smith",
    "notes": "Issued for hydraulic system repair"
}
```

## Transfers API

### Warehouse to Kit Transfer
```http
POST /transfers/warehouse-to-kit
```

**Request Body:**
```json
{
    "warehouse_id": 1,
    "kit_id": 5,
    "box_id": 12,
    "item_type": "tool",
    "item_id": 123,
    "quantity": 1,
    "notes": "Transferred for Q400 maintenance"
}
```

### Kit to Warehouse Transfer
```http
POST /transfers/kit-to-warehouse
```

**Request Body:**
```json
{
    "kit_id": 5,
    "warehouse_id": 1,
    "kit_item_id": 45,
    "notes": "Returned after maintenance completion"
}
```

### Kit to Kit Transfer
```http
POST /transfers/kit-to-kit
```

**Request Body:**
```json
{
    "from_kit_id": 5,
    "to_kit_id": 7,
    "from_box_id": 12,
    "to_box_id": 18,
    "kit_item_id": 45,
    "notes": "Transferred between kits"
}
```

### Warehouse to Warehouse Transfer
```http
POST /transfers/warehouse-to-warehouse
```

**Request Body:**
```json
{
    "from_warehouse_id": 1,
    "to_warehouse_id": 2,
    "item_type": "chemical",
    "item_id": 67,
    "quantity": 5,
    "notes": "Stock rebalancing"
}
```

### Complete Transfer
```http
POST /transfers/:id/complete
```

### Cancel Transfer
```http
POST /transfers/:id/cancel
```

## Barcode API

### Generate Tool Barcode
```http
GET /barcode/tool/:id
```

**Query Parameters:**
- `label_size` (string): Label size (4x6, 3x4, 2x4, 2x2) - default: 4x6
- `code_type` (string): Code type (barcode, qrcode) - default: barcode

**Response:** PDF file download

### Generate Chemical Barcode
```http
GET /barcode/chemical/:id
```

**Query Parameters:**
- `label_size` (string): Label size - default: 4x6
- `code_type` (string): Code type - default: barcode
- `is_transfer` (boolean): Transfer label - default: false
- `parent_lot_number` (string): Parent lot number (for transfers)
- `destination` (string): Destination name (for transfers)

**Response:** PDF file download

### Generate Expendable Barcode
```http
GET /barcode/expendable/:id
```

**Query Parameters:**
- `label_size` (string): Label size - default: 4x6
- `code_type` (string): Code type - default: barcode

**Response:** PDF file download

## Inventory Tracking API

### Get Transaction History
```http
GET /inventory/transactions/:item_type/:item_id
```

**Path Parameters:**
- `item_type` (string): Type (tool/chemical/expendable)
- `item_id` (integer): Item ID

**Response:**
```json
{
    "item_type": "chemical",
    "item_id": 1,
    "transactions": [
        {
            "id": 1,
            "transaction_type": "transfer",
            "from_location": "Warehouse A",
            "to_location": "Kit 5",
            "quantity": 2.5,
            "timestamp": "2025-11-06T10:00:00Z",
            "performed_by": "admin"
        }
    ]
}
```

### Get Item Detail with Transactions
```http
GET /inventory/detail/:item_type/:item_id
```

## Lot Number API

### Generate Lot Number
```http
GET /lot-numbers/generate
```

**Response:**
```json
{
    "lot_number": "LOT-251106-0001"
}
```

## Reorder API

### Create Reorder Request
```http
POST /kits/:kit_id/reorder
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

### List Reorder Requests
```http
GET /reorders
```

**Query Parameters:**
- `kit_id` (integer): Filter by kit
- `status` (string): Filter by status
- `priority` (string): Filter by priority

### Update Reorder Status
```http
PUT /reorders/:id
```

### Fulfill Reorder
```http
POST /reorders/:id/fulfill
```

## Error Responses

All endpoints return standard error responses:

```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {}
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Missing or invalid token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `409`: Conflict - Duplicate or conflicting data
- `500`: Internal Server Error - Server error

## Rate Limiting

API requests are rate-limited to:
- 100 requests per minute per user
- 1000 requests per hour per user

## Pagination

List endpoints support pagination:

**Request:**
```http
GET /tools?page=2&per_page=50
```

**Response:**
```json
{
    "tools": [...],
    "total": 150,
    "page": 2,
    "per_page": 50,
    "pages": 3
}
```

## See Also

- [Warehouse Management](WAREHOUSE_MANAGEMENT.md)
- [Expendables System](EXPENDABLES_SYSTEM.md)
- [Barcode System](BARCODE_SYSTEM.md)
- [Kits User Guide](KITS_USER_GUIDE.md)

