# Page Access Permissions System

**Date:** 2025-10-17  
**Feature:** Page-level access control using RBAC permissions  
**Status:** ✅ Complete and Tested

---

## Overview

The SupplyLine MRO Suite now includes a comprehensive **page access permission system** that controls which pages users can access based on their assigned roles and permissions.

### Key Features

- ✅ **14 new page access permissions** added to the Permission system
- ✅ **Permission-based routing** - Users without permission see "Access Denied" page
- ✅ **Dynamic navigation** - Menu items only show for pages user can access
- ✅ **Dashboard always accessible** - All authenticated users can access /dashboard
- ✅ **Role-based defaults** - Each role has appropriate page permissions pre-configured

---

## Page Access Permissions

### Permission List

| Permission Name | Description | Page(s) Protected |
|----------------|-------------|-------------------|
| `page.tools` | Access Tools page | /tools, /tools/new, /tools/:id, /tools/:id/edit |
| `page.orders` | Access Orders page | /orders |
| `page.checkouts` | Access Checkouts page | /checkouts, /checkouts/all, /checkout/:id |
| `page.my_checkouts` | Access My Checkouts page | /my-checkouts |
| `page.kits` | Access Kits page | /kits, /kits/new, /kits/:id, /kits/:id/edit, /kits/reports, /kits/mobile |
| `page.chemicals` | Access Chemicals page | /chemicals, /chemicals/new, /chemicals/:id, /chemicals/:id/edit, /chemicals/:id/issue |
| `page.calibrations` | Access Calibrations page | /calibrations, /tools/:id/calibrations/new, /calibration-standards, etc. |
| `page.reports` | Access Reports page | /reports |
| `page.scanner` | Access Scanner page | /scanner |
| `page.warehouses` | Access Warehouses page | /warehouses |
| `page.admin_dashboard` | Access Admin Dashboard | /admin/dashboard |
| `page.aircraft_types` | Access Aircraft Types Management | /admin/aircraft-types |
| `page.profile` | Access Profile page | /profile |

**Note:** The main dashboard (`/dashboard`) is accessible to ALL authenticated users and does not require a specific permission.

---

## Role Assignments

### Administrator Role
**Page Permissions:** ALL (14 permissions)

- ✅ Tools
- ✅ Orders
- ✅ Checkouts
- ✅ My Checkouts
- ✅ Kits
- ✅ Chemicals
- ✅ Calibrations
- ✅ Reports
- ✅ Scanner
- ✅ Warehouses
- ✅ Admin Dashboard
- ✅ Aircraft Types
- ✅ Profile

**Navigation:** Sees all menu items

---

### Materials Manager Role
**Page Permissions:** 11 permissions (everything except admin-specific pages)

- ✅ Tools
- ✅ Orders
- ✅ Checkouts
- ✅ My Checkouts
- ✅ Kits
- ✅ Chemicals
- ✅ Calibrations
- ✅ Reports
- ✅ Scanner
- ✅ Warehouses
- ✅ Profile
- ❌ Admin Dashboard
- ❌ Aircraft Types

**Navigation:** Sees most menu items except admin-specific pages

---

### Maintenance User Role (RESTRICTED)
**Page Permissions:** 3 permissions (minimal access)

- ❌ Tools
- ❌ Orders
- ❌ Checkouts
- ✅ My Checkouts (can see their own checkouts)
- ✅ Kits (primary work area)
- ❌ Chemicals
- ❌ Calibrations
- ❌ Reports
- ❌ Scanner
- ❌ Warehouses
- ❌ Admin Dashboard
- ❌ Aircraft Types
- ✅ Profile

**Navigation:** Only sees Dashboard, Kits, and Profile menu items

**Use Case:** This role is designed for maintenance technicians who only need to:
1. View their dashboard
2. Work with kits
3. See their own checkouts
4. Access their profile

---

### Quality Inspector Role
**Page Permissions:** 7 permissions

- ✅ Tools
- ✅ Checkouts
- ✅ My Checkouts
- ❌ Orders
- ❌ Kits
- ❌ Chemicals
- ✅ Calibrations
- ✅ Reports
- ✅ Scanner
- ❌ Warehouses
- ❌ Admin Dashboard
- ❌ Aircraft Types
- ✅ Profile

**Navigation:** Sees Tools, Checkouts, Calibrations, Reports, Scanner, and Profile

---

## Technical Implementation

### 1. Backend Migration

**File:** `backend/migrations/add_page_access_permissions.py`

- Creates 14 new permissions in the "Page Access" category
- Assigns permissions to all 4 default roles
- Can be run multiple times safely (checks for existing permissions)

**Run Migration:**
```bash
cd backend
source venv/bin/activate
python migrations/add_page_access_permissions.py
```

---

### 2. Frontend Route Protection

**File:** `frontend/src/components/auth/ProtectedRoute.jsx`

**New Components:**
- `ProtectedRoute` - Enhanced with `requirePermission` prop
- `PermissionRoute` - Specialized component for permission-based routes
- `hasPermission()` - Helper function to check if user has a permission

**Usage:**
```jsx
// Old way (no permission check)
<Route path="/tools" element={
  <ProtectedRoute>
    <MainLayout><ToolsManagement /></MainLayout>
  </ProtectedRoute>
} />

// New way (with permission check)
<Route path="/tools" element={
  <PermissionRoute permission="page.tools">
    <MainLayout><ToolsManagement /></MainLayout>
  </PermissionRoute>
} />
```

**Access Denied Behavior:**
- Shows user-friendly "Access Denied" alert
- Displays required permission name
- Provides "Return to Dashboard" button
- Does NOT redirect (user stays on same URL)

---

### 3. Dynamic Navigation

**File:** `frontend/src/components/common/MainLayout.jsx`

**Changes:**
- Imports `hasPermission` helper function
- Each navigation link wrapped in permission check
- Menu items only render if user has permission

**Example:**
```jsx
{hasPermission(user, 'page.tools') && (
  <Nav.Link as={Link} to="/tools">Tools</Nav.Link>
)}
```

**Result:**
- Maintenance User sees: Dashboard, Kits
- Materials Manager sees: Dashboard, Tools, Checkouts, Kits, Chemicals, Calibrations, Warehouses, Scanner, Reports
- Administrator sees: All menu items

---

### 4. Permission Checking Logic

**Admin Bypass:**
```javascript
const hasPermission = (user, permissionName) => {
  if (!user) return false;
  
  // Admins have all permissions
  if (user.is_admin) return true;
  
  // Check if user has the specific permission
  const permissions = user.permissions || [];
  return permissions.includes(permissionName);
};
```

**Key Points:**
- Admins (`is_admin: true`) automatically have ALL permissions
- Non-admin users must have the specific permission in their `permissions` array
- Permissions come from user's assigned roles

---

## User Experience

### For Maintenance User (Restricted Role)

**Login Experience:**
1. User logs in
2. Redirected to `/dashboard`
3. Navigation shows: **Dashboard | Kits**
4. Can access:
   - `/dashboard` - Main dashboard
   - `/kits` - Kits management
   - `/my-checkouts` - Their own checkouts
   - `/profile` - Their profile

**If they try to access restricted page:**
1. Type `/tools` in browser
2. See "Access Denied" page
3. Message: "You do not have permission to access this page. Required permission: page.tools"
4. Click "Return to Dashboard" button

---

### For Materials Manager

**Login Experience:**
1. User logs in
2. Redirected to `/dashboard`
3. Navigation shows: **Dashboard | Tools | Checkouts | Kits | Chemicals | Calibrations | Warehouses | Scanner | Reports**
4. Can access all pages except admin pages

---

### For Administrator

**Login Experience:**
1. User logs in
2. Redirected to `/dashboard`
3. Navigation shows: **All menu items including Admin Dashboard**
4. Can access ALL pages (permission checks bypassed)

---

## Managing Page Permissions

### Via Roles Management Modal

1. Navigate to **Admin Dashboard** → **User Management** tab
2. Click **"Roles"** button
3. Select a role and click **"Edit Details"** or **"Permissions"**
4. Switch to **"Permissions"** tab
5. Expand **"Page Access"** category
6. Check/uncheck page permissions as needed
7. Click **"Save Changes"**

**Example: Give Maintenance User access to Tools page**
1. Edit "Maintenance User" role
2. Go to Permissions tab
3. Expand "Page Access" category
4. Check `page.tools` - "Access Tools page"
5. Save
6. Maintenance Users will now see "Tools" in navigation

---

## Database Schema

### Permissions Table

```sql
-- Example page access permissions
INSERT INTO permissions (name, description, category) VALUES
('page.tools', 'Access Tools page', 'Page Access'),
('page.checkouts', 'Access Checkouts page', 'Page Access'),
('page.kits', 'Access Kits page', 'Page Access'),
...
```

### Role-Permission Relationships

```sql
-- Example: Maintenance User role permissions
SELECT p.name, p.description 
FROM permissions p
JOIN role_permissions rp ON p.id = rp.permission_id
JOIN roles r ON rp.role_id = r.id
WHERE r.name = 'Maintenance User' AND p.category = 'Page Access';

-- Results:
-- page.kits | Access Kits page
-- page.my_checkouts | Access My Checkouts page
-- page.profile | Access Profile page
```

---

## Testing

### Test Scenarios

**✅ Test 1: Maintenance User Restricted Access**
1. Login as Maintenance User
2. Verify navigation only shows: Dashboard, Kits
3. Try accessing `/tools` directly
4. Verify "Access Denied" page appears
5. Click "Return to Dashboard"
6. Verify redirected to `/dashboard`

**✅ Test 2: Materials Manager Access**
1. Login as Materials Manager
2. Verify navigation shows most pages (except admin)
3. Access `/tools`, `/chemicals`, `/kits` successfully
4. Try accessing `/admin/dashboard`
5. Verify "Access Denied" page appears

**✅ Test 3: Administrator Full Access**
1. Login as Administrator
2. Verify navigation shows ALL pages
3. Access any page successfully
4. Verify no "Access Denied" pages

**✅ Test 4: Permission Changes**
1. Login as Administrator
2. Edit Maintenance User role
3. Add `page.tools` permission
4. Logout and login as Maintenance User
5. Verify "Tools" now appears in navigation
6. Verify can access `/tools` page

---

## Benefits

### 1. **Granular Access Control**
- Control access at the page level
- Different roles see different pages
- Easy to customize per organization

### 2. **Improved Security**
- Users can't access pages they shouldn't see
- Navigation doesn't show inaccessible pages
- Clear "Access Denied" messages

### 3. **Better User Experience**
- Simplified navigation for restricted users
- No confusion about which pages they can access
- Clear feedback when access is denied

### 4. **Flexible Configuration**
- Administrators can easily modify page access
- No code changes required
- Changes take effect immediately

---

## Future Enhancements

### Potential Improvements

1. **Page Groups:** Group related pages under single permission
2. **Conditional Access:** Time-based or location-based access
3. **Audit Logging:** Track when users are denied access
4. **Custom Redirect:** Redirect to different page based on role
5. **Permission Inheritance:** Child pages inherit parent page permissions

---

## Conclusion

✅ **Feature Complete:** Page access permission system fully implemented  
✅ **Tested:** All roles and permissions verified  
✅ **User-Friendly:** Clear navigation and access denied messages  
✅ **Flexible:** Easy to modify permissions via Roles Management  
✅ **Secure:** Users can only access pages they have permission for

The page access permission system provides fine-grained control over which pages users can access, improving both security and user experience by showing only relevant navigation items and preventing unauthorized access to restricted pages.

