# Testing Guide for User Management Refactoring

## Prerequisites
1. Ensure the backend server is running
2. Ensure the frontend development server is running
3. Log in as a user with `user.manage` and `role.manage` permissions (Administrator role recommended)

## Test Scenarios

### 1. Departments Management

#### 1.1 Opening the Departments Modal
- [ ] Navigate to User Management page
- [ ] Click the "Departments" button
- [ ] Verify the Departments Management modal opens
- [ ] Verify all existing departments are displayed
- [ ] Verify both active and inactive departments are shown

#### 1.2 Search Functionality
- [ ] Type in the search box
- [ ] Verify departments are filtered in real-time
- [ ] Verify search works for both name and description
- [ ] Clear the search and verify all departments reappear

#### 1.3 Create Department
- [ ] Click "Add New Department" button
- [ ] Verify the create form modal opens
- [ ] Try submitting without a name - should show validation error
- [ ] Enter a department name and description
- [ ] Click "Add Department"
- [ ] Verify success message or modal closes
- [ ] Verify new department appears in the list
- [ ] Try creating a department with a duplicate name - should show error

#### 1.4 Edit Department
- [ ] Click the edit (pencil) button on a department
- [ ] Verify the edit form modal opens with current values
- [ ] Modify the name and/or description
- [ ] Click "Save Changes"
- [ ] Verify the department is updated in the list
- [ ] Try changing to a duplicate name - should show error

#### 1.5 Deactivate Department (Soft Delete)
- [ ] Click the deactivate (toggle off) button on an active department
- [ ] Verify the department's status changes to "Inactive"
- [ ] Verify the department row appears grayed out
- [ ] Verify the button changes to activate (toggle on)

#### 1.6 Activate Department
- [ ] Click the activate (toggle on) button on an inactive department
- [ ] Verify the department's status changes to "Active"
- [ ] Verify the department row appears normal
- [ ] Verify the button changes to deactivate (toggle off)

#### 1.7 Hard Delete Department
- [ ] Click the delete (trash) button on a department
- [ ] Verify a confirmation modal appears
- [ ] Verify the warning message is displayed
- [ ] Click "Cancel" - modal should close without deleting
- [ ] Click delete again and click "Delete Permanently"
- [ ] Verify the department is removed from the list
- [ ] Refresh the page and verify the department is gone

### 2. Roles Management

#### 2.1 Opening the Roles Modal
- [ ] Navigate to User Management page
- [ ] Click the "Roles" button
- [ ] Verify the Roles Management modal opens
- [ ] Verify all existing roles are displayed
- [ ] Verify system roles are marked with a "System Role" badge

#### 2.2 Search Functionality
- [ ] Type in the search box
- [ ] Verify roles are filtered in real-time
- [ ] Verify search works for both name and description
- [ ] Clear the search and verify all roles reappear

#### 2.3 Create Role
- [ ] Click "Add New Role" button
- [ ] Verify the create form modal opens with tabs
- [ ] On "Role Details" tab:
  - [ ] Try submitting without a name - should show validation error
  - [ ] Enter a role name and description
- [ ] Switch to "Permissions" tab:
  - [ ] Verify permission tree is displayed
  - [ ] Verify permissions are grouped by category
  - [ ] Expand/collapse categories
  - [ ] Select individual permissions
  - [ ] Use "Select All" for a category
  - [ ] Use "Deselect All" for a category
  - [ ] Verify permission count updates
- [ ] Click "Add Role"
- [ ] Verify new role appears in the list with correct permission count
- [ ] Try creating a role with a duplicate name - should show error

#### 2.4 Edit Role Details (Non-System Roles)
- [ ] Click the edit (pencil) button on a non-system role
- [ ] Verify the edit form modal opens with current values
- [ ] Modify the name and/or description
- [ ] Click "Save Changes"
- [ ] Verify the role is updated in the list
- [ ] Try editing a system role's details - button should be disabled or show error

#### 2.5 Edit Role Permissions (All Roles)
- [ ] Click the "Permissions" button on any role (including system roles)
- [ ] Verify the permission tree modal opens
- [ ] Verify current permissions are pre-selected
- [ ] For system roles, verify info message is displayed
- [ ] Modify permissions:
  - [ ] Deselect some permissions
  - [ ] Select new permissions
  - [ ] Use category select all/deselect all
  - [ ] Verify total count updates
- [ ] Click "Save Permissions"
- [ ] Verify the role's permission count updates in the list
- [ ] Re-open permissions and verify changes were saved

#### 2.6 Permission Tree Functionality
- [ ] Test expanding/collapsing categories
- [ ] Test category icons (checkmark, minus, empty)
- [ ] Test "Select All" button (global)
- [ ] Test "Clear All" button (global)
- [ ] Test individual permission checkboxes
- [ ] Verify permission descriptions are displayed
- [ ] Verify smooth animations

#### 2.7 Delete Role (Non-System Roles)
- [ ] Click the delete (trash) button on a non-system role
- [ ] Verify a confirmation modal appears
- [ ] Verify the warning message is displayed
- [ ] Click "Cancel" - modal should close without deleting
- [ ] Click delete again and click "Delete Role"
- [ ] Verify the role is removed from the list
- [ ] Try deleting a system role - button should be disabled

#### 2.8 System Role Protection
- [ ] Verify system roles (Administrator, Materials Manager, Maintenance User) have:
  - [ ] "System Role" badge
  - [ ] Disabled or hidden edit details button
  - [ ] Disabled or hidden delete button
  - [ ] Enabled permissions button
- [ ] Try to edit system role details - should show error or be disabled
- [ ] Try to delete system role - should show error or be disabled
- [ ] Verify you CAN edit system role permissions

### 3. Integration Tests

#### 3.1 User Assignment
- [ ] Create a new role with specific permissions
- [ ] Assign the role to a user
- [ ] Verify the user has the correct permissions
- [ ] Edit the role's permissions
- [ ] Verify the user's permissions update accordingly

#### 3.2 Department Assignment
- [ ] Create a new department
- [ ] Create or edit a user and assign them to the new department
- [ ] Verify the department appears in the user's profile
- [ ] Deactivate the department
- [ ] Verify the department still appears for existing users
- [ ] Try to assign a new user to an inactive department

#### 3.3 Audit Logging
- [ ] Perform various operations (create, edit, delete)
- [ ] Check the audit log (if accessible)
- [ ] Verify all operations are logged with:
  - [ ] Action type
  - [ ] Timestamp
  - [ ] User who performed the action
  - [ ] Details of the change

### 4. Error Handling

#### 4.1 Network Errors
- [ ] Disconnect from the network
- [ ] Try to perform operations
- [ ] Verify appropriate error messages are displayed
- [ ] Reconnect and verify operations work again

#### 4.2 Permission Errors
- [ ] Log in as a user without `user.manage` or `role.manage` permissions
- [ ] Verify the Roles and Departments buttons are hidden or disabled
- [ ] Try to access the endpoints directly (if possible)
- [ ] Verify 403 Forbidden errors are returned

#### 4.3 Validation Errors
- [ ] Try to create/edit with empty required fields
- [ ] Try to create duplicates
- [ ] Verify validation messages are clear and helpful

### 5. UI/UX Tests

#### 5.1 Responsive Design
- [ ] Resize browser window to mobile size
- [ ] Verify modals are responsive
- [ ] Verify tables are scrollable
- [ ] Verify buttons are accessible
- [ ] Test on actual mobile device if possible

#### 5.2 Animations and Transitions
- [ ] Verify smooth modal open/close animations
- [ ] Verify hover effects on buttons and rows
- [ ] Verify category expand/collapse animations
- [ ] Verify no janky or broken animations

#### 5.3 Accessibility
- [ ] Tab through the interface
- [ ] Verify all interactive elements are keyboard accessible
- [ ] Verify focus indicators are visible
- [ ] Test with screen reader if possible

#### 5.4 Loading States
- [ ] Verify loading spinners appear during operations
- [ ] Verify buttons are disabled during loading
- [ ] Verify no double-submissions are possible

### 6. Performance Tests

#### 6.1 Large Data Sets
- [ ] Create many departments (20+)
- [ ] Create many roles (20+)
- [ ] Verify search still works quickly
- [ ] Verify scrolling is smooth
- [ ] Verify no lag in UI interactions

#### 6.2 Permission Tree Performance
- [ ] Open permission tree with all 26 permissions
- [ ] Expand all categories
- [ ] Select/deselect rapidly
- [ ] Verify no lag or freezing

## Bug Reporting Template

If you find any issues, please report them with the following information:

```
**Issue Title**: [Brief description]

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Screenshots**:
[If applicable]

**Browser/Environment**:
- Browser: [e.g., Chrome 120]
- OS: [e.g., Windows 11]
- Screen Size: [e.g., 1920x1080]

**Console Errors**:
[Any errors from browser console]
```

## Success Criteria

All tests should pass with:
- ✅ No console errors
- ✅ Smooth animations
- ✅ Correct data persistence
- ✅ Proper error handling
- ✅ Responsive design working
- ✅ All CRUD operations functional
- ✅ Permission system working correctly
- ✅ Audit logging working

