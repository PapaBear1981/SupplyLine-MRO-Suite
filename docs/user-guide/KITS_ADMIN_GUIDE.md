# Mobile Warehouse (Kits) - Administrator Guide

**Version**: 1.0  
**Last Updated**: October 12, 2025  
**Audience**: System Administrators, Materials Department Managers

---

## Table of Contents

1. [Overview](#overview)
2. [System Configuration](#system-configuration)
3. [Aircraft Type Management](#aircraft-type-management)
4. [Kit Monitoring](#kit-monitoring)
5. [Reorder Approval Workflow](#reorder-approval-workflow)
6. [Transfer Management](#transfer-management)
7. [Reporting & Analytics](#reporting--analytics)
8. [User Management](#user-management)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

The Mobile Warehouse (Kits) system allows your organization to track mobile warehouses that follow aircraft to operating bases. As an administrator, you have full control over:

- **Aircraft Type Management**: Define and manage aircraft types (Q400, RJ85, CL415, etc.)
- **Kit Monitoring**: View all kits, their status, and health metrics
- **Approval Workflows**: Approve or reject reorder requests
- **Transfer Oversight**: Monitor and manage transfers between kits and warehouses
- **Analytics**: Access comprehensive reports and usage statistics
- **User Permissions**: Control who can create, edit, and manage kits

---

## System Configuration

### Access Requirements

**Admin Dashboard Access**:
- Navigate to: `/admin/dashboard`
- Required Role: `Administrator` or `Materials Department`
- Permissions: Full CRUD access to all kit operations

### Initial Setup Checklist

- [ ] Configure aircraft types for your fleet
- [ ] Set up user roles and permissions
- [ ] Create initial kit templates
- [ ] Configure reorder approval workflows
- [ ] Set up notification preferences
- [ ] Review default box types and configurations

---

## Aircraft Type Management

### Overview

Aircraft types define the categories of kits in your system. Each kit must be associated with an aircraft type.

### Accessing Aircraft Type Management

1. Navigate to **Admin Dashboard** (`/admin/dashboard`)
2. Scroll to **Aircraft Type Management** section
3. View existing types or click **Add Aircraft Type**

### Managing Aircraft Types

#### **Add New Aircraft Type**:

1. Click **Add Aircraft Type** button
2. Fill in the form:
   - **Name**: Aircraft model (e.g., "Q400", "RJ85", "CL415")
   - **Description**: Optional details about the aircraft
   - **Status**: Active (default)
3. Click **Save**

#### **Edit Aircraft Type**:

1. Find the aircraft type in the list
2. Click **Edit** button
3. Modify name or description
4. Click **Save Changes**

#### **Deactivate Aircraft Type**:

1. Find the aircraft type in the list
2. Click **Deactivate** button
3. Confirm the action

**Note**: Deactivating an aircraft type does NOT delete existing kits of that type. It only prevents new kits from being created with that type.

### Default Aircraft Types

The system comes pre-configured with:
- **Q400**: Bombardier Q400 turboprop
- **RJ85**: British Aerospace RJ85 regional jet
- **CL415**: Canadair CL-415 water bomber

---

## Kit Monitoring

### Admin Dashboard Widgets

The Admin Dashboard provides real-time kit monitoring through several widgets:

#### **1. Kit Statistics**

Shows:
- Total kits in system
- Active kits count
- Inactive kits count
- Kits in maintenance
- Kits with alerts
- Breakdown by aircraft type

**Actions**:
- Click on any stat to filter kits
- View detailed breakdown by aircraft type

#### **2. Pending Kit Transfers**

Displays:
- Transfers awaiting completion
- Source and destination locations
- Transfer details and quantities
- User who initiated transfer

**Actions**:
- Click **Review** to view transfer details
- Click **View All** to see complete transfer history

#### **3. Pending Reorder Approvals**

Shows:
- Reorder requests awaiting approval
- Priority levels (Urgent, High, Medium, Low)
- Requested quantities
- Requesting user

**Actions**:
- Click **Review** to approve/reject
- Urgent requests highlighted in red

#### **4. Kit Utilization Stats**

Interactive charts showing:
- Issuances by kit (bar chart)
- Transfers by type (pie chart)
- Activity over time (stacked bar chart)

**Features**:
- Time range selector (7/30/90 days)
- Drill-down to specific kits
- Export data for analysis

### Viewing All Kits

1. Navigate to **Kits** page (`/kits`)
2. Use tabs to filter:
   - **All Kits**: Complete list
   - **Active**: Currently in use
   - **Inactive**: Decommissioned or stored
   - **Alerts**: Kits requiring attention
3. Use search and filters:
   - Search by kit name
   - Filter by aircraft type
   - Sort by various criteria

### Kit Health Indicators

**Alert Badges**:
- 🔴 **Red**: Critical issues (out of stock, expired items)
- 🟡 **Yellow**: Warnings (low stock, expiring soon)
- 🔵 **Blue**: Informational (pending transfers, messages)

---

## Reorder Approval Workflow

### Overview

Mechanics and stores personnel can request reorders when kit items are low or depleted. As an administrator, you review and approve these requests.

### Approval Process

#### **Step 1: Review Request**

1. Navigate to **Admin Dashboard**
2. Find request in **Pending Reorder Approvals** widget
3. Click **Review** button

#### **Step 2: Evaluate Request**

Review the following:
- **Item Details**: Part number, description
- **Quantity Requested**: How many units needed
- **Priority**: Urgency level set by requester
- **Requesting User**: Who submitted the request
- **Kit Information**: Which kit needs the item
- **Current Stock**: Current quantity in kit
- **Notes**: Any additional context from requester

#### **Step 3: Take Action**

**Approve**:
1. Click **Approve** button
2. Request moves to "Approved" status
3. Procurement can now order the item

**Reject**:
1. Click **Reject** button
2. Provide reason for rejection
3. Requester is notified

**Request More Info**:
1. Use messaging system to contact requester
2. Ask for clarification or additional details

### Priority Levels

- **🔴 Urgent**: Aircraft grounded, immediate need
- **🟡 High**: Critical for upcoming maintenance
- **🔵 Medium**: Standard reorder
- **⚪ Low**: Stock replenishment, no urgency

**Best Practice**: Approve urgent requests within 1 hour, high priority within 4 hours.

### Bulk Approval

For multiple similar requests:
1. Navigate to **Reorder Requests** page
2. Use filters to find related requests
3. Select multiple requests (checkbox)
4. Click **Bulk Approve** button

---

## Transfer Management

### Overview

Transfers move items between kits and warehouses. Administrators can monitor all transfers and intervene if needed.

### Transfer Types

1. **Kit → Kit**: Moving items between mobile warehouses
2. **Kit → Warehouse**: Returning items to central warehouse
3. **Warehouse → Kit**: Restocking kits from warehouse

### Monitoring Transfers

#### **Pending Transfers**:

View in Admin Dashboard widget:
- Shows transfers awaiting completion
- Click **Review** to see details
- Monitor for stuck or delayed transfers

#### **Transfer History**:

1. Navigate to **Kit Reports** (`/kits/reports`)
2. Select **Transfer Report** tab
3. Filter by:
   - Date range
   - Source/destination
   - Status
   - User

### Completing Stuck Transfers

If a transfer is stuck in "Pending" status:

1. Navigate to transfer details
2. Verify items were physically moved
3. Click **Complete Transfer** button
4. Or click **Cancel Transfer** if not completed

### Transfer Validation

The system automatically validates:
- ✅ Sufficient quantity at source
- ✅ Valid source and destination
- ✅ User has permission
- ✅ Items exist in source location

---

## Reporting & Analytics

### Accessing Reports

Navigate to **Kit Reports** (`/kits/reports`)

### Available Reports

#### **1. Inventory Report**

Shows current inventory across all kits:
- Kit name and aircraft type
- Total items per kit
- Items by box type
- Stock health indicators
- Low stock warnings

**Filters**:
- Aircraft type
- Specific kit
- Stock status

**Export**: CSV, JSON

#### **2. Issuance Report**

Tracks items issued from kits:
- Issue date and time
- Item details
- Quantity issued
- Purpose and work order
- Issuing user

**Filters**:
- Date range
- Kit
- User
- Item type

**Export**: CSV, JSON

#### **3. Transfer Report**

Complete transfer history:
- Transfer date
- Source and destination
- Items transferred
- Quantities
- Status
- User

**Filters**:
- Date range
- Source/destination type
- Status
- User

**Export**: CSV, JSON

#### **4. Reorder Report**

Reorder request tracking:
- Request date
- Item details
- Quantity requested
- Priority
- Status (Pending, Approved, Fulfilled)
- Fulfillment date

**Filters**:
- Date range
- Status
- Priority
- Kit

**Export**: CSV, JSON

#### **5. Utilization Report**

Kit usage analytics:
- Issuances over time
- Transfer patterns
- Most-used kits
- Activity trends

**Features**:
- Interactive charts
- Time range selector
- Drill-down capabilities

### Exporting Data

All reports support export:
1. Apply desired filters
2. Click **Export CSV** or **Export JSON**
3. File downloads automatically
4. Open in Excel or analysis tool

---

## User Management

### Roles and Permissions

#### **Administrator**:
- Full access to all kit operations
- Manage aircraft types
- Approve reorder requests
- View all reports and analytics
- Manage user permissions

#### **Materials Department**:
- Create and manage kits
- Approve reorder requests
- View all kits and reports
- Manage transfers
- Cannot manage aircraft types

#### **Mechanic**:
- View assigned kits
- Issue items from kits
- Request reorders
- Create transfers
- Send messages
- Cannot approve requests

### Assigning Permissions

1. Navigate to **User Management** (if available)
2. Find user in list
3. Edit user roles
4. Assign appropriate department
5. Save changes

---

## Troubleshooting

### Common Issues

#### **Issue: Kit not appearing in list**

**Possible Causes**:
- Kit is inactive
- User doesn't have permission
- Aircraft type is deactivated

**Solution**:
1. Check kit status in admin view
2. Verify user permissions
3. Check aircraft type status

#### **Issue: Cannot approve reorder request**

**Possible Causes**:
- User lacks admin/materials role
- Request already processed
- System error

**Solution**:
1. Verify user role
2. Check request status
3. Refresh page and retry
4. Check browser console for errors

#### **Issue: Transfer stuck in pending**

**Possible Causes**:
- Physical transfer not completed
- System error during completion
- Network issue

**Solution**:
1. Verify physical transfer occurred
2. Manually complete or cancel transfer
3. Check system logs for errors

#### **Issue: Reports not loading**

**Possible Causes**:
- Large date range
- Too many kits
- Backend timeout

**Solution**:
1. Reduce date range
2. Filter by specific kit or aircraft type
3. Try exporting smaller chunks
4. Contact system administrator

### Getting Help

**Technical Support**:
- Email: support@supplyline-mro.com
- Phone: 1-800-SUPPLY-1
- Hours: 24/7 for critical issues

**Documentation**:
- User Guide: `docs/user-guide/KITS_USER_GUIDE.md`
- API Documentation: `backend/README.md`
- System Architecture: `docs/ARCHITECTURE.md`

---

## Best Practices

### Kit Management

1. **Regular Audits**: Review kit inventory monthly
2. **Deactivate Unused Kits**: Keep active list manageable
3. **Standardize Naming**: Use consistent naming conventions
4. **Monitor Alerts**: Check alert tab daily
5. **Review Utilization**: Analyze usage patterns quarterly

### Reorder Approvals

1. **Prioritize Urgent**: Approve urgent requests immediately
2. **Verify Quantities**: Ensure requested quantities are reasonable
3. **Check Stock Levels**: Review current inventory before approving
4. **Communicate**: Use messaging for clarifications
5. **Track Fulfillment**: Monitor approved requests to completion

### Transfer Management

1. **Monitor Pending**: Review pending transfers daily
2. **Complete Promptly**: Ensure transfers are completed within 24 hours
3. **Validate Physically**: Verify items were actually moved
4. **Document Issues**: Note any problems in transfer notes
5. **Audit Trail**: Review transfer history for patterns

### Reporting

1. **Regular Reviews**: Generate reports weekly
2. **Export Data**: Keep historical exports for trend analysis
3. **Share Insights**: Distribute reports to stakeholders
4. **Act on Data**: Use reports to drive improvements
5. **Archive Reports**: Maintain report archive for compliance

### Security

1. **Review Permissions**: Audit user permissions quarterly
2. **Monitor Activity**: Check for unusual patterns
3. **Secure Credentials**: Ensure users follow password policies
4. **Limit Admin Access**: Only grant admin to necessary users
5. **Log Review**: Periodically review system logs

---

## Appendix

### Quick Reference

**Admin Dashboard**: `/admin/dashboard`  
**Kits Management**: `/kits`  
**Kit Reports**: `/kits/reports`  
**Aircraft Types**: Admin Dashboard → Aircraft Type Management

### Keyboard Shortcuts

- `Ctrl + K`: Quick search
- `Ctrl + /`: Open help
- `Esc`: Close modals

### Support Resources

- **User Guide**: For end-user instructions
- **API Docs**: For integration and automation
- **Release Notes**: For new features and changes
- **Training Videos**: Available on company intranet

---

**Document Version**: 1.0  
**Last Updated**: October 12, 2025  
**Next Review**: January 12, 2026

