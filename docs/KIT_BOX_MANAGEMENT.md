# Kit Box Management Feature

## Overview
This feature allows administrators and Materials department users to add, edit, and remove boxes from kits after they have been created.

## Features

### 1. **Add Boxes**
- Add new boxes to existing kits
- Specify box number, type, and description
- Box numbers must be unique within a kit
- Supported box types:
  - Expendable
  - Tooling
  - Consumable
  - Loose
  - Floor

### 2. **Edit Boxes**
- Update box number, type, or description
- Box number uniqueness is validated on update
- Cannot change box number to one that already exists in the kit

### 3. **Delete Boxes**
- Remove boxes from kits
- **Safety Check**: Cannot delete boxes that contain items
- Must remove all items from a box before deletion
- Confirmation dialog prevents accidental deletion

## User Interface

### Accessing Box Management
1. Navigate to a kit's detail page
2. Click the "Edit" button
3. Select the "Manage Boxes" tab

### Box Manager Interface
- **Table View**: Shows all boxes with:
  - Box number
  - Box type (color-coded badge)
  - Description
  - Item count
  - Action buttons (Edit/Delete)

- **Add Box Button**: Opens modal to create new box
- **Edit Button**: Opens modal to modify existing box
- **Delete Button**: 
  - Disabled if box contains items
  - Shows confirmation dialog before deletion

### Modal Forms
- **Add/Edit Modal**:
  - Box Number field (required, unique)
  - Box Type dropdown (required)
  - Description field (optional)
  - Form validation with helpful feedback

- **Delete Confirmation Modal**:
  - Shows box details
  - Displays item count warning
  - Prevents deletion if items exist

## API Endpoints

### Get Kit Boxes
```
GET /api/kits/{kit_id}/boxes
```
Returns all boxes for a specific kit.

### Add Box
```
POST /api/kits/{kit_id}/boxes
Content-Type: application/json

{
  "box_number": "Box4",
  "box_type": "expendable",
  "description": "Additional expendables"
}
```

### Update Box
```
PUT /api/kits/{kit_id}/boxes/{box_id}
Content-Type: application/json

{
  "box_number": "Box4A",
  "box_type": "tooling",
  "description": "Updated description"
}
```

### Delete Box
```
DELETE /api/kits/{kit_id}/boxes/{box_id}
```
Returns error if box contains items.

## Validation Rules

1. **Box Number**:
   - Required field
   - Must be unique within the kit
   - Can be any string (e.g., "Box1", "Loose", "Floor")

2. **Box Type**:
   - Required field
   - Must be one of: expendable, tooling, consumable, loose, floor

3. **Description**:
   - Optional field
   - Maximum 255 characters

4. **Deletion**:
   - Box must have 0 items
   - Cannot delete if `item_count > 0`

## Permissions
- **Required Role**: Admin or Materials department
- **Read Access**: All authenticated users can view boxes
- **Write Access**: Only Admin and Materials can add/edit/delete boxes

## Technical Implementation

### Frontend Components
- **KitBoxManager.jsx**: Main component for box management
  - Handles CRUD operations
  - Manages modals and forms
  - Displays box list with actions

### Redux Actions
- `fetchKitBoxes`: Load boxes for a kit
- `addKitBox`: Create new box
- `updateKitBox`: Modify existing box
- `deleteKitBox`: Remove box (if empty)

### Backend Routes
- All routes in `backend/routes_kits.py`
- Protected with `@materials_required` decorator
- Validates box uniqueness and item count

### Database Model
```python
class KitBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kits.id'))
    box_number = db.Column(db.String(20), nullable=False)
    box_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    
    # Unique constraint on kit_id + box_number
    __table_args__ = (
        db.UniqueConstraint('kit_id', 'box_number'),
    )
```

## User Workflow Examples

### Example 1: Adding a New Box
1. Navigate to kit detail page
2. Click "Edit" button
3. Select "Manage Boxes" tab
4. Click "Add Box" button
5. Fill in form:
   - Box Number: "Box6"
   - Box Type: "Expendable"
   - Description: "Emergency supplies"
6. Click "Add Box"
7. Success toast appears
8. New box appears in table

### Example 2: Editing a Box
1. In the box manager, click "Edit" button on a box
2. Modify fields as needed
3. Click "Update Box"
4. Changes are saved and reflected immediately

### Example 3: Deleting an Empty Box
1. Click "Delete" button on a box with 0 items
2. Confirmation dialog appears
3. Review box details
4. Click "Delete Box"
5. Box is removed from the list

### Example 4: Attempting to Delete Box with Items
1. Click "Delete" button on a box with items
2. Button is disabled with tooltip: "Cannot delete box with items"
3. User must first remove all items from the box
4. Then deletion becomes available

## Error Handling

### Common Errors
1. **Duplicate Box Number**:
   - Error: "Box 'Box1' already exists in this kit"
   - Solution: Choose a different box number

2. **Box Contains Items**:
   - Error: "Cannot delete box with 5 items. Remove items first."
   - Solution: Transfer or remove all items before deletion

3. **Invalid Box Type**:
   - Error: "Box type is required"
   - Solution: Select a valid box type from dropdown

## Best Practices

1. **Naming Convention**:
   - Use consistent naming (e.g., Box1, Box2, Box3)
   - Use descriptive names for special boxes (e.g., "Loose", "Floor")

2. **Box Types**:
   - Choose appropriate type for contents
   - Helps with organization and reporting

3. **Descriptions**:
   - Add meaningful descriptions
   - Helps users understand box contents

4. **Before Deletion**:
   - Always verify box is empty
   - Consider transferring items to another box
   - Check if box is referenced in documentation

## Future Enhancements

Potential improvements:
- Bulk box operations
- Box templates for common configurations
- Drag-and-drop box reordering
- Box capacity tracking
- Visual box layout designer
- Box barcode generation
- Box location tracking within warehouse

