# Warehouse Management Documentation

## Overview

The Warehouse Management system in SupplyLine MRO Suite provides comprehensive tracking and management of physical warehouse locations. Warehouses serve as the primary storage locations for tools, chemicals, and expendables before they are transferred to mobile kits for field operations.

## Key Features

- **Multiple Warehouse Support**: Create and manage multiple warehouse locations
- **Address Management**: Track complete address information for each warehouse
- **Warehouse Types**: Classify warehouses as main or satellite locations
- **Inventory Tracking**: Track tools, chemicals, and expendables by warehouse
- **Transfer Management**: Complete audit trail for all warehouse transfers
- **Location Hierarchy**: Warehouses → Kits → Boxes for organized inventory

## Warehouse Model

### Warehouse Properties

```python
{
    "id": 1,
    "name": "Main Warehouse - Building A",
    "address": "123 Aviation Way",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98101",
    "country": "USA",
    "warehouse_type": "main",  # main or satellite
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "created_by": "admin",
    "tools_count": 150,
    "chemicals_count": 75,
    "expendables_count": 200
}
```

### Warehouse Types

#### Main Warehouse
- **Purpose**: Primary storage facility
- **Characteristics**: Large inventory, central location, full stock
- **Use Case**: Main distribution center, primary inventory storage

#### Satellite Warehouse
- **Purpose**: Secondary storage facility
- **Characteristics**: Smaller inventory, remote location, specific stock
- **Use Case**: Remote sites, specialized storage, overflow storage

## API Endpoints

### List Warehouses
```http
GET /api/warehouses
```

**Query Parameters:**
- `include_inactive`: Include inactive warehouses (default: false)
- `warehouse_type`: Filter by type (main/satellite)
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 50, max: 200)

**Response:**
```json
{
    "warehouses": [
        {
            "id": 1,
            "name": "Main Warehouse",
            "warehouse_type": "main",
            "is_active": true,
            "tools_count": 150,
            "chemicals_count": 75,
            "expendables_count": 200
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 50,
    "pages": 1
}
```

### Create Warehouse
```http
POST /api/warehouses
```

**Request Body:**
```json
{
    "name": "Satellite Warehouse - Hangar 5",
    "address": "456 Runway Drive",
    "city": "Portland",
    "state": "OR",
    "zip_code": "97201",
    "country": "USA",
    "warehouse_type": "satellite"
}
```

**Required Fields:**
- `name`: Warehouse name (must be unique)

**Optional Fields:**
- `address`: Street address
- `city`: City
- `state`: State/Province
- `zip_code`: Postal code
- `country`: Country (default: "USA")
- `warehouse_type`: Type (default: "satellite")

**Response:**
```json
{
    "message": "Warehouse created successfully",
    "warehouse": {
        "id": 2,
        "name": "Satellite Warehouse - Hangar 5",
        "warehouse_type": "satellite",
        "is_active": true
    }
}
```

### Get Warehouse Details
```http
GET /api/warehouses/:id
```

**Response:**
```json
{
    "id": 1,
    "name": "Main Warehouse",
    "address": "123 Aviation Way",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98101",
    "country": "USA",
    "warehouse_type": "main",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "created_by": "admin",
    "tools_count": 150,
    "chemicals_count": 75,
    "expendables_count": 200
}
```

### Update Warehouse
```http
PUT /api/warehouses/:id
```

**Request Body:**
```json
{
    "name": "Main Warehouse - Updated",
    "address": "789 New Address",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98102",
    "warehouse_type": "main",
    "is_active": true
}
```

**Updatable Fields:**
- `name`: Warehouse name
- `address`: Street address
- `city`: City
- `state`: State/Province
- `zip_code`: Postal code
- `country`: Country
- `warehouse_type`: Type (main/satellite)
- `is_active`: Active status

**Response:**
```json
{
    "message": "Warehouse updated successfully",
    "warehouse": {
        "id": 1,
        "name": "Main Warehouse - Updated",
        "is_active": true
    }
}
```

### Delete Warehouse
```http
DELETE /api/warehouses/:id
```

**Response:**
```json
{
    "message": "Warehouse deactivated successfully"
}
```

**Note:** Warehouses are soft-deleted (marked as inactive) to preserve historical data.

## Warehouse Transfers

### Transfer Types

#### 1. Warehouse to Kit
Transfer items from warehouse to mobile kit for field operations.

```http
POST /api/transfers/warehouse-to-kit
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

#### 2. Kit to Warehouse
Return items from kit back to warehouse.

```http
POST /api/transfers/kit-to-warehouse
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

#### 3. Warehouse to Warehouse
Transfer items between warehouses.

```http
POST /api/transfers/warehouse-to-warehouse
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

### Transfer Workflow

1. **Initiate Transfer**: Create transfer request via API
2. **Validation**: System validates item availability and permissions
3. **Update Inventory**: Item location updated in database
4. **Create Audit Record**: Transfer record created for audit trail
5. **Record Transaction**: Transaction logged for inventory tracking
6. **Auto-Complete**: Warehouse transfers auto-complete immediately
7. **Barcode Printing**: Optional barcode label generation for transferred items

### Transfer Status

- **completed**: Transfer successfully completed
- **pending**: Transfer initiated but not yet completed (kit-to-kit only)
- **cancelled**: Transfer cancelled before completion

## Inventory Management

### Adding Items to Warehouse

#### Tools
```http
POST /api/tools
```

**Request Body:**
```json
{
    "tool_number": "T-12345",
    "serial_number": "SN-67890",
    "description": "Torque Wrench",
    "warehouse_id": 1,
    "location": "Shelf A-5"
}
```

#### Chemicals
```http
POST /api/chemicals
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
    "location": "Cabinet B-3"
}
```

#### Expendables
```http
POST /api/expendables
```

**Request Body:**
```json
{
    "part_number": "EXP-001",
    "description": "Fastener Kit",
    "quantity": 100,
    "unit": "pieces",
    "warehouse_id": 1,
    "location": "Bin C-7"
}
```

### Viewing Warehouse Inventory

#### Get All Tools in Warehouse
```http
GET /api/tools?warehouse_id=1
```

#### Get All Chemicals in Warehouse
```http
GET /api/chemicals?warehouse_id=1
```

#### Get All Expendables in Warehouse
```http
GET /api/expendables?warehouse_id=1
```

## Best Practices

### Warehouse Organization

1. **Naming Convention**: Use descriptive names (e.g., "Main Warehouse - Building A")
2. **Address Accuracy**: Maintain accurate address information for shipping and logistics
3. **Type Classification**: Properly classify warehouses as main or satellite
4. **Active Status**: Keep inactive warehouses for historical data, don't delete

### Inventory Management

1. **Location Tracking**: Always specify location within warehouse (shelf, bin, cabinet)
2. **Regular Audits**: Conduct regular physical inventory audits
3. **Transfer Documentation**: Include detailed notes for all transfers
4. **Barcode Labels**: Print and apply barcode labels for all items

### Transfer Management

1. **Validation**: Verify item availability before initiating transfers
2. **Documentation**: Include clear notes explaining transfer purpose
3. **Audit Trail**: Review transfer history regularly for compliance
4. **Auto-Completion**: Leverage auto-complete for warehouse transfers

## Security & Permissions

### Admin-Only Operations
- Create warehouse
- Update warehouse
- Delete (deactivate) warehouse

### Materials Department Operations
- View warehouses
- Transfer items between warehouses
- Transfer items to/from kits
- View inventory

### Maintenance Department Operations
- View warehouses (read-only)
- View inventory (read-only)

## Reporting

### Warehouse Inventory Report
```http
GET /api/warehouses/:id/inventory-report
```

**Response:**
```json
{
    "warehouse": {
        "id": 1,
        "name": "Main Warehouse"
    },
    "inventory": {
        "tools": 150,
        "chemicals": 75,
        "expendables": 200,
        "total_items": 425
    },
    "by_category": {
        "tools": {
            "Q400": 50,
            "RJ85": 40,
            "General": 60
        },
        "chemicals": {
            "Sealant": 30,
            "Paint": 25,
            "Adhesive": 20
        }
    }
}
```

### Transfer History Report
```http
GET /api/warehouses/:id/transfer-history
```

**Query Parameters:**
- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)
- `transfer_type`: Filter by type (warehouse-to-kit, kit-to-warehouse, warehouse-to-warehouse)

## Troubleshooting

### Common Issues

**Issue**: Cannot create warehouse with duplicate name
- **Solution**: Warehouse names must be unique. Choose a different name.

**Issue**: Cannot delete warehouse with inventory
- **Solution**: Transfer all items out of warehouse before deletion, or use deactivation instead.

**Issue**: Transfer fails with "Item not found"
- **Solution**: Verify item exists and is in the source warehouse.

**Issue**: Permission denied when creating warehouse
- **Solution**: Only admin users can create warehouses. Contact your administrator.

## See Also

- [Kits User Guide](KITS_USER_GUIDE.md) - Mobile warehouse/kits management
- [Barcode System](BARCODE_SYSTEM.md) - Barcode and label printing
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference

