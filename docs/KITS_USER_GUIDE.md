# Mobile Warehouse/Kits - User Guide

## Overview

The Mobile Warehouse (Kits) system allows you to manage mobile warehouses that follow aircraft to operating bases for maintenance operations. Each kit contains numbered boxes storing parts, tools, and consumables needed for aircraft maintenance.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating a New Kit](#creating-a-new-kit)
3. [Viewing Kit Details](#viewing-kit-details)
4. [Managing Kit Items](#managing-kit-items)
5. [Issuing Items](#issuing-items)
6. [Transferring Items](#transferring-items)
7. [Reordering Items](#reordering-items)
8. [Messaging](#messaging)
9. [Understanding Alerts](#understanding-alerts)
10. [Best Practices](#best-practices)

---

## Getting Started

### Accessing the Kits System

1. Log in to SupplyLine MRO Suite
2. Click **"Kits"** in the main navigation menu
3. You'll see the Kits Management dashboard

### Dashboard Overview

The dashboard shows:
- **All Kits**: Complete list of all kits
- **Active Kits**: Currently operational kits
- **Inactive Kits**: Kits not in use
- **Alerts**: Kits with pending issues

Each kit card displays:
- Kit name and aircraft type
- Status badge (Active/Inactive/Maintenance)
- Number of boxes
- Number of items
- Alert count

---

## Creating a New Kit

### Using the Kit Wizard

1. Click **"Create Kit"** button on the dashboard
2. Follow the 4-step wizard:

#### Step 1: Select Aircraft Type
- Choose the aircraft type this kit will support
- Options: Q400, RJ85, CL415 (or custom types added by admin)
- Click the aircraft card to select

#### Step 2: Enter Kit Details
- **Kit Name** (required): e.g., "Q400 Kit #1"
- **Description** (optional): Additional details about the kit
- Click **"Next"**

#### Step 3: Configure Boxes
- Review suggested boxes or customize
- Each box has:
  - **Box Number**: e.g., "Box1", "Box2", "Loose", "Floor"
  - **Box Type**: Expendable, Tooling, Consumable, Loose, or Floor
  - **Description**: Optional details
- Add or remove boxes as needed
- Click **"Next"**

#### Step 4: Review and Create
- Review all kit information
- Click **"Create Kit"** to finalize
- You'll be redirected to the new kit's detail page

### Duplicating an Existing Kit

1. Open any kit detail page
2. Click **"Duplicate"** button
3. Enter a new name for the duplicated kit
4. The new kit will have the same box configuration

---

## Viewing Kit Details

### Kit Detail Page

Click any kit card to view details:

#### Overview Tab
- Kit name, aircraft type, status
- Creation date and creator
- Description
- Statistics: boxes, items, transfers, pending reorders

#### Quick Actions
- **Issue Items**: Issue parts/tools from the kit
- **Transfer Items**: Move items between kits or warehouses
- **Request Reorder**: Request restocking
- **Send Message**: Communicate with stores personnel
- **View Analytics**: See usage statistics

#### Additional Tabs
- **Items**: View all items in the kit
- **Issuances**: History of issued items
- **Transfers**: Transfer history
- **Reorders**: Reorder requests
- **Messages**: Communication thread

---

## Managing Kit Items

### Viewing Items

1. Go to kit detail page
2. Click **"Items"** tab
3. Use filters to find specific items:
   - **Filter by Box**: Select specific box
   - **Filter by Type**: Tool, Chemical, or Expendable
   - **Filter by Status**: Available, Issued, Low Stock, Out of Stock

### Item Information

Each item shows:
- **Box Location**: Which box contains the item
- **Part Number**: Unique identifier
- **Serial/Lot Number**: If applicable
- **Description**: Item details
- **Type**: Tool, Chemical, or Expendable
- **Quantity**: Current stock level
- **Location**: Specific location within box
- **Status**: Current status with color coding

### Status Indicators

- 🟢 **Available**: Item in stock and ready
- 🟡 **Low Stock**: Below minimum level
- 🔴 **Out of Stock**: No quantity remaining
- 🔵 **Issued**: Currently issued to work order
- ⚪ **Transferred**: Moved to another location

---

## Issuing Items

### How to Issue Items from a Kit

1. Navigate to kit detail page
2. Click **"Issue Items"** button
3. In the issuance form:
   - Select the item to issue
   - Enter quantity
   - Enter work order number
   - Specify purpose
   - Add notes (optional)
4. Click **"Issue"**

### What Happens When You Issue

- Item quantity is reduced
- Issuance is recorded with timestamp
- If quantity falls below minimum, automatic reorder is triggered
- Audit log entry is created

### Viewing Issuance History

1. Go to kit detail page
2. Click **"Issuances"** tab
3. View complete history with:
   - Date and time
   - Item issued
   - Quantity
   - Work order
   - Issued by (user)
   - Purpose

---

## Transferring Items

### Types of Transfers

1. **Kit to Kit**: Move items between mobile kits
2. **Kit to Warehouse**: Return items to main warehouse
3. **Warehouse to Kit**: Stock items into kit

### Creating a Transfer

1. Click **"Transfer Items"** button
2. Select:
   - Source location (kit or warehouse)
   - Destination location (kit or warehouse)
   - Item to transfer
   - Quantity
3. Add notes (optional)
4. Click **"Create Transfer"**

### Transfer Status

- **Pending**: Transfer initiated, awaiting completion
- **Completed**: Transfer finished, inventory updated
- **Cancelled**: Transfer cancelled before completion

### Completing a Transfer

Materials department personnel can:
1. View pending transfers
2. Verify physical transfer
3. Click **"Complete Transfer"**
4. Inventory is automatically updated

---

## Reordering Items

### Automatic Reorders

The system automatically creates reorder requests when:
- Item quantity falls below minimum stock level
- Item is issued and stock becomes low
- Item is completely out of stock

### Manual Reorder Requests

To manually request a reorder:
1. Click **"Request Reorder"** button
2. Fill in:
   - Part number
   - Description
   - Quantity needed
   - Priority (Low, Medium, High, Urgent)
   - Notes
3. Click **"Submit Request"**

### Reorder Workflow

1. **Pending**: Request submitted, awaiting approval
2. **Approved**: Approved by materials manager
3. **Ordered**: Order placed with supplier
4. **Fulfilled**: Items received and added to kit

### Viewing Reorder Requests

1. Go to kit detail page
2. Click **"Reorders"** tab
3. View all requests with status and priority

---

## Messaging

### Sending Messages

1. Click **"Send Message"** button
2. Enter:
   - Subject
   - Message content
   - Recipient (optional - leave blank for broadcast)
   - Link to reorder request (optional)
3. Click **"Send"**

### Reading Messages

1. Click **"Messages"** tab or notification badge
2. View inbox with:
   - Unread messages highlighted
   - Message threads
   - Sender and date
3. Click message to read full content

### Replying to Messages

1. Open a message
2. Click **"Reply"** button
3. Type your response
4. Click **"Send Reply"**

### Message Threading

- Replies are grouped with original message
- View entire conversation thread
- Track communication history

---

## Understanding Alerts

### Alert Types

#### 🔴 High Severity (Red)
- **Out of Stock**: Item completely depleted
- **Critical Reorder**: Urgent restocking needed

#### 🟡 Medium Severity (Yellow)
- **Low Stock**: Below minimum level
- **Pending Reorder**: Awaiting approval/fulfillment

#### 🔵 Low Severity (Blue)
- **Unread Messages**: New communications
- **Informational**: General notifications

### Viewing Alerts

Alerts appear:
- On kit cards (alert count badge)
- On kit detail page (alert banner)
- In Alerts tab on dashboard

### Resolving Alerts

- **Low Stock**: Create reorder request or transfer items
- **Pending Reorder**: Follow up on request status
- **Unread Messages**: Read and respond to messages

---

## Best Practices

### Kit Organization

1. **Use Descriptive Names**: "Q400 Kit #1 - Vancouver Base"
2. **Keep Boxes Organized**: One type per box (expendable, tooling, consumable)
3. **Regular Inventory Checks**: Verify quantities periodically
4. **Update Locations**: Keep location information current

### Inventory Management

1. **Set Minimum Stock Levels**: Configure appropriate minimums for expendables
2. **Issue Promptly**: Record issuances immediately
3. **Complete Transfers**: Don't leave transfers pending
4. **Monitor Alerts**: Check alerts daily

### Communication

1. **Use Messages**: Communicate through the system for audit trail
2. **Link to Reorders**: Reference reorder requests in messages
3. **Be Specific**: Include part numbers and quantities
4. **Respond Promptly**: Reply to messages within 24 hours

### Maintenance

1. **Review Analytics**: Check usage patterns monthly
2. **Optimize Stock Levels**: Adjust minimums based on usage
3. **Clean Up**: Remove obsolete items
4. **Update Descriptions**: Keep information current

---

## Troubleshooting

### Common Issues

**Q: I can't create a kit**
- A: Ensure you have Materials department access
- Check that you've selected an aircraft type
- Verify kit name is unique

**Q: Items not showing in kit**
- A: Check filters - you may be filtering out items
- Verify items were added to correct box
- Refresh the page

**Q: Reorder not triggering automatically**
- A: Ensure minimum stock level is set for expendables
- Verify item quantity is below minimum
- Check that item status is not "issued" or "transferred"

**Q: Can't complete transfer**
- A: Only Materials department can complete transfers
- Verify transfer is in "pending" status
- Check that you have proper permissions

### Getting Help

- Click the help icon (?) throughout the application
- Contact your system administrator
- Refer to this user guide
- Check the FAQ section

---

## Keyboard Shortcuts

- **Ctrl/Cmd + K**: Quick search
- **Esc**: Close modals
- **Tab**: Navigate form fields
- **Enter**: Submit forms

---

## Glossary

- **Kit**: Mobile warehouse containing tools and parts
- **Box**: Container within a kit (numbered or named)
- **Expendable**: Consumable item that gets used up
- **Issuance**: Act of removing item from kit for use
- **Transfer**: Moving items between locations
- **Reorder**: Request to restock items
- **Aircraft Type**: Type of aircraft kit supports (Q400, RJ85, CL415)

---

## Support

For additional assistance:
- Email: support@supplyline-mro.com
- Phone: 1-800-MRO-HELP
- Documentation: https://docs.supplyline-mro.com

---

**Version**: 5.0.0  
**Last Updated**: 2025-10-12  
**Document**: User Guide - Mobile Warehouse/Kits System

