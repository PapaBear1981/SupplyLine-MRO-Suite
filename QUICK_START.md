# Quick Start Guide - User Management Refactoring

## Overview
This guide will help you quickly get started with testing the new Roles and Departments management features.

## Prerequisites
- Backend server running
- Frontend development server running
- Admin user credentials

## Starting the Application

### Backend
```bash
cd SupplyLine-MRO-Suite/backend
# Activate virtual environment if needed
python app.py
```

### Frontend
```bash
cd SupplyLine-MRO-Suite/frontend
npm start
```

## Quick Test Flow

### 1. Access User Management (30 seconds)
1. Log in as an administrator
2. Navigate to User Management page
3. Look for the button group in the top-right:
   - **"Add New User"** (unchanged)
   - **"Roles"** (renamed from "Create Role")
   - **"Departments"** (renamed from "Create Department")

### 2. Test Departments Management (2 minutes)

#### Quick Test:
1. Click **"Departments"** button
2. You should see a modal with a table of all departments
3. Try the search box - type "Materials"
4. Click **"Add New Department"**
5. Create a test department:
   - Name: "Test Department"
   - Description: "This is a test"
6. Click **"Add Department"**
7. Find your new department in the list
8. Click the **edit** button (pencil icon)
9. Change the description
10. Click **"Save Changes"**
11. Click the **deactivate** button (toggle icon)
12. Notice the department becomes inactive (grayed out)
13. Click the **activate** button to restore it
14. Click the **delete** button (trash icon)
15. Read the warning and click **"Delete Permanently"**
16. Verify the department is gone

### 3. Test Roles Management (3 minutes)

#### Quick Test:
1. Click **"Roles"** button
2. You should see a modal with a table of all roles
3. Notice the system roles have a "System Role" badge
4. Try the search box - type "Admin"
5. Click **"Add New Role"**
6. On the "Role Details" tab:
   - Name: "Test Role"
   - Description: "This is a test role"
7. Switch to the "Permissions" tab
8. Expand the "User Management" category
9. Select a few permissions (e.g., user.view, user.create)
10. Notice the permission count updates
11. Click **"Add Role"**
12. Find your new role in the list
13. Click the **"Permissions"** button (shield icon)
14. Add more permissions from different categories
15. Click **"Save Permissions"**
16. Notice the permission count updates in the table
17. Click the **edit** button (pencil icon)
18. Change the description
19. Click **"Save Changes"**
20. Click the **delete** button (trash icon)
21. Confirm deletion

### 4. Test System Role Protection (1 minute)

1. In the Roles modal, find "Administrator" role
2. Notice it has a "System Role" badge
3. Try to click the **edit** button - it should be there but...
4. Click the **"Permissions"** button - this SHOULD work
5. Modify some permissions
6. Click **"Save Permissions"** - this SHOULD work
7. Try to click the **delete** button - it should be disabled/hidden

## Visual Checklist

### Departments Modal Should Have:
- ✅ Search box at the top
- ✅ "Add New Department" button
- ✅ Table with columns: Name, Description, Status, Actions
- ✅ Active/Inactive badges
- ✅ Three action buttons per row: Edit, Toggle Active, Delete
- ✅ Smooth animations on hover
- ✅ Confirmation dialog for delete

### Roles Modal Should Have:
- ✅ Search box at the top
- ✅ "Add New Role" button
- ✅ Table with columns: Role Name, Description, Permissions, Type, Actions
- ✅ Permission count badges
- ✅ System Role badges for system roles
- ✅ Three action buttons: Permissions, Edit, Delete
- ✅ Edit and Delete disabled for system roles
- ✅ Permissions button enabled for all roles

### Permission Tree Should Have:
- ✅ Categories that expand/collapse
- ✅ Category icons showing selection state (all/partial/none)
- ✅ "Select All" / "Deselect All" per category
- ✅ Individual permission checkboxes
- ✅ Permission descriptions
- ✅ Total count at the bottom
- ✅ Global "Clear All" and "Select All" buttons

## Common Issues and Solutions

### Issue: Buttons not showing
**Solution**: Make sure you're logged in as a user with `user.manage` and `role.manage` permissions

### Issue: Modal not opening
**Solution**: Check browser console for errors. Make sure backend is running.

### Issue: Changes not saving
**Solution**: Check network tab for failed requests. Verify backend is running and accessible.

### Issue: Permission tree not loading
**Solution**: Verify the `/api/permissions/categories` endpoint is working. Check backend logs.

### Issue: Can't delete system roles
**Solution**: This is expected behavior. System roles are protected from deletion.

### Issue: Styling looks broken
**Solution**: Make sure all CSS files are loaded. Check browser console for 404 errors.

## API Endpoints to Verify

### Departments
```bash
# Get all departments (including inactive)
GET http://localhost:5000/api/departments?include_inactive=true

# Create department
POST http://localhost:5000/api/departments
Body: {"name": "Test", "description": "Test dept"}

# Update department
PUT http://localhost:5000/api/departments/1
Body: {"name": "Updated", "description": "Updated desc"}

# Soft delete (deactivate)
DELETE http://localhost:5000/api/departments/1

# Hard delete (permanent)
DELETE http://localhost:5000/api/departments/1/hard-delete
```

### Roles
```bash
# Get all roles
GET http://localhost:5000/api/roles

# Get role with permissions
GET http://localhost:5000/api/roles/1

# Create role
POST http://localhost:5000/api/roles
Body: {"name": "Test", "description": "Test role", "permissions": [1, 2, 3]}

# Update role (including permissions)
PUT http://localhost:5000/api/roles/1
Body: {"permissions": [1, 2, 3, 4, 5]}

# Delete role
DELETE http://localhost:5000/api/roles/1
```

### Permissions
```bash
# Get all permissions
GET http://localhost:5000/api/permissions

# Get permissions by category
GET http://localhost:5000/api/permissions/categories
```

## Files Changed

### Backend
- `backend/routes_departments.py` - Added hard delete endpoint
- `backend/routes_rbac.py` - Modified to allow permission updates for system roles

### Frontend
- `frontend/src/components/users/UserManagement.jsx` - Updated to use new modals
- `frontend/src/components/users/RolesManagementModal.jsx` - NEW
- `frontend/src/components/users/RolesManagementModal.css` - NEW
- `frontend/src/components/users/DepartmentsManagementModal.jsx` - NEW
- `frontend/src/components/users/DepartmentsManagementModal.css` - NEW
- `frontend/src/components/rbac/PermissionTreeSelector.jsx` - NEW
- `frontend/src/components/rbac/PermissionTreeSelector.css` - NEW
- `frontend/src/store/departmentsSlice.js` - Added hard delete action

## Next Steps

1. Run through the Quick Test Flow above
2. Review the detailed [TESTING_GUIDE.md](./TESTING_GUIDE.md)
3. Check the [VISUAL_CHANGES_GUIDE.md](./VISUAL_CHANGES_GUIDE.md) for UI details
4. Read the [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) for technical details

## Support

If you encounter any issues:
1. Check browser console for errors
2. Check backend logs for errors
3. Verify all files are saved and servers are restarted
4. Review the testing guide for expected behavior
5. Report bugs using the template in TESTING_GUIDE.md

## Success Indicators

You'll know everything is working when:
- ✅ Both modals open without errors
- ✅ All CRUD operations work smoothly
- ✅ Permission tree displays and functions correctly
- ✅ System roles are protected appropriately
- ✅ Animations are smooth
- ✅ No console errors
- ✅ Changes persist after refresh

Happy testing! 🚀

