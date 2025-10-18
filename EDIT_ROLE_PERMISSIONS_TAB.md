# Edit Role Details - Permissions Tab Added

**Date:** 2025-10-17  
**Feature:** Added Permissions tab to Edit Role Details modal  
**Status:** ✅ Complete and Tested

---

## Summary

The "Edit Details" modal for roles now includes a **Permissions tab**, matching the functionality of the "Add New Role" modal. This allows administrators to edit both role details (name and description) AND permissions in a single unified interface.

---

## Changes Made

### 1. Updated `openEditDetailsForm` Function

**File:** `frontend/src/components/users/RolesManagementModal.jsx`

**Before:**
```javascript
const openEditDetailsForm = (role) => {
  setSelectedRole(role);
  setFormData({
    name: role.name,
    description: role.description || '',
    permissions: []  // ❌ Empty permissions
  });
  setShowEditDetailsForm(true);
};
```

**After:**
```javascript
const openEditDetailsForm = (role) => {
  setSelectedRole(role);
  
  // Fetch full role details with permissions
  dispatch(fetchRole(role.id))
    .unwrap()
    .then((roleData) => {
      setFormData({
        name: roleData.name,
        description: roleData.description || '',
        permissions: roleData.permissions ? roleData.permissions.map(p => p.id) : []  // ✅ Load permissions
      });
      setShowEditDetailsForm(true);
    })
    .catch(err => {
      console.error('Failed to fetch role details:', err);
    });
};
```

**Why:** The function now fetches the full role details including permissions from the backend, ensuring the Permissions tab shows the current state.

---

### 2. Updated Edit Role Details Modal Structure

**File:** `frontend/src/components/users/RolesManagementModal.jsx`

**Before:**
- Simple modal with name and description fields
- No tabs
- No permissions editing

**After:**
- Tabbed interface with two tabs:
  1. **Role Details** - Name and description fields
  2. **Permissions** - Full permission tree selector
- Modal size changed to `lg` for better visibility
- Title shows role name: "Edit Role: {role name}"

**Code Structure:**
```jsx
<Modal show={showEditDetailsForm} onHide={...} size="lg">
  <Modal.Header closeButton>
    <Modal.Title>Edit Role: {selectedRole?.name}</Modal.Title>
  </Modal.Header>
  <Form noValidate validated={validated} onSubmit={handleEditDetails}>
    <Modal.Body>
      {/* Warning for system roles */}
      {selectedRole?.is_system_role && (
        <Alert variant="warning">
          <FaExclamationTriangle className="me-2" />
          This is a system role. You cannot modify its name or description, but you can edit its permissions.
        </Alert>
      )}

      <Tabs defaultActiveKey="details" className="mb-3">
        {/* Role Details Tab */}
        <Tab eventKey="details" title="Role Details">
          <Form.Group className="mb-3">
            <Form.Label>Role Name *</Form.Label>
            <Form.Control
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              disabled={selectedRole?.is_system_role}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              disabled={selectedRole?.is_system_role}
            />
          </Form.Group>
        </Tab>

        {/* Permissions Tab */}
        <Tab eventKey="permissions" title="Permissions">
          <Alert variant="info">
            <FaInfoCircle className="me-2" />
            {selectedRole?.is_system_role 
              ? 'You can modify permissions for this system role to customize access levels.'
              : 'Select the permissions to assign to this role.'}
          </Alert>
          {Object.keys(permissionsByCategory).length > 0 ? (
            <PermissionTreeSelector
              permissionsByCategory={permissionsByCategory}
              selectedPermissions={formData.permissions}
              onChange={handlePermissionsChange}
            />
          ) : (
            <p className="text-muted">Loading permissions...</p>
          )}
        </Tab>
      </Tabs>
    </Modal.Body>
    <Modal.Footer>
      <Button variant="secondary" onClick={...}>Cancel</Button>
      <Button variant="primary" type="submit" disabled={loading}>
        Save Changes
      </Button>
    </Modal.Footer>
  </Form>
</Modal>
```

---

### 3. Updated `handleEditDetails` Function

**File:** `frontend/src/components/users/RolesManagementModal.jsx`

**Before:**
```javascript
const handleEditDetails = (e) => {
  // ... validation ...
  
  dispatch(updateRole({ 
    id: selectedRole.id, 
    roleData: {
      name: formData.name,
      description: formData.description  // ❌ Only name and description
    }
  }))
  // ...
};
```

**After:**
```javascript
const handleEditDetails = (e) => {
  // ... validation ...
  
  // Build the update payload - include both details and permissions
  const roleData = {
    name: formData.name,
    description: formData.description,
    permissions: formData.permissions  // ✅ Include permissions
  };

  dispatch(updateRole({ 
    id: selectedRole.id, 
    roleData
  }))
  // ...
};
```

**Why:** The function now saves both role details AND permissions in a single API call, providing a unified editing experience.

---

## User Experience

### For Regular Roles (Materials Manager, Maintenance User, Quality Inspector)

**Edit Details Button:**
1. Click "Edit Details" button
2. Modal opens with role name in title: "Edit Role: Materials Manager"
3. Two tabs available:
   - **Role Details** - Edit name and description
   - **Permissions** - Select/deselect permissions using the tree selector
4. Click "Save Changes" to update both details and permissions

**Benefits:**
- ✅ Edit everything in one place
- ✅ No need to use separate "Permissions" button
- ✅ See current permissions while editing details
- ✅ Consistent with "Add New Role" experience

### For System Roles (Administrator)

**Permissions Button Only:**
- System roles don't have "Edit Details" button (name/description cannot be changed)
- Only "Permissions" button is available
- Opens the dedicated permissions modal
- Shows info alert: "This is a system role. You can modify its permissions to customize access levels."

**Why Different:**
- System roles have protected name and description
- Tabbed interface would be confusing with disabled fields
- Dedicated permissions modal is clearer for this use case

---

## Technical Details

### API Calls

**When opening Edit Details modal:**
```
GET /roles/{role_id}
```
Returns full role details including permissions array.

**When saving changes:**
```
PUT /roles/{role_id}
```
Payload includes:
```json
{
  "name": "Materials Manager",
  "description": "Can manage tools, chemicals, and users",
  "permissions": [1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
}
```

### State Management

**Form Data Structure:**
```javascript
{
  name: 'Materials Manager',
  description: 'Can manage tools, chemicals, and users',
  permissions: [1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
}
```

**Permission IDs:**
- Array of permission IDs (integers)
- Managed by `PermissionTreeSelector` component
- Updated via `handlePermissionsChange` callback

---

## Testing Results

### ✅ Test 1: Edit Regular Role Details
- Opened "Edit Details" for Materials Manager
- Verified two tabs: "Role Details" and "Permissions"
- Switched between tabs successfully
- Both tabs displayed correct data

### ✅ Test 2: Permissions Tab Functionality
- Permissions tab shows all 26 permissions across 6 categories
- Current permissions are pre-selected (20 for Materials Manager)
- Permission tree selector works correctly
- Category collapse/expand works
- Select All / Deselect All buttons work

### ✅ Test 3: System Role Behavior
- Administrator only has "Permissions" button (no "Edit Details")
- Clicking "Permissions" opens dedicated permissions modal
- Shows correct info alert for system roles
- All 26 permissions are selected for Administrator

### ✅ Test 4: Dark Theme
- Both tabs display correctly in dark theme
- Permission tree selector uses dark theme colors
- No visual issues or light backgrounds

---

## Files Modified

1. **frontend/src/components/users/RolesManagementModal.jsx**
   - Updated `openEditDetailsForm` to fetch full role details
   - Updated Edit Role Details modal to use tabbed interface
   - Updated `handleEditDetails` to save permissions

---

## Benefits

### 1. **Unified Interface**
- Edit name, description, AND permissions in one place
- No need to switch between modals
- Consistent with "Add New Role" experience

### 2. **Better User Experience**
- See current permissions while editing details
- Make all changes at once
- Single "Save Changes" action

### 3. **Reduced Clicks**
- Before: Click "Edit Details" → Save → Click "Permissions" → Save (2 modals, 4 clicks)
- After: Click "Edit Details" → Switch tabs → Save (1 modal, 2 clicks)

### 4. **Consistency**
- "Add New Role" and "Edit Role" now have the same interface
- Users learn the pattern once

---

## Future Enhancements

### Potential Improvements:
1. **Validation:** Add validation to ensure at least one permission is selected
2. **Dirty State:** Show warning if user tries to close with unsaved changes
3. **Permission Diff:** Highlight which permissions changed
4. **Bulk Edit:** Allow editing multiple roles at once

---

## Conclusion

✅ **Feature Complete:** Edit Role Details modal now includes Permissions tab  
✅ **Tested:** All functionality verified in browser  
✅ **Dark Theme:** Fully compatible with dark theme  
✅ **User Experience:** Improved workflow with unified interface  
✅ **Backward Compatible:** System roles still use dedicated permissions modal

The Edit Role Details modal now provides a complete, unified interface for managing all aspects of a role, matching the functionality of the Add New Role modal and significantly improving the user experience.

