# Cycle Count User Guide

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Creating Schedules](#creating-schedules)
4. [Managing Batches](#managing-batches)
5. [Performing Counts](#performing-counts)
6. [Managing Discrepancies](#managing-discrepancies)
7. [Reports and Analytics](#reports-and-analytics)
8. [Mobile Interface](#mobile-interface)
9. [Troubleshooting](#troubleshooting)

## Overview

### What is Cycle Counting?
Cycle counting is a systematic approach to inventory management that involves counting a subset of inventory items on a regular basis rather than conducting a full physical inventory. This method helps maintain accurate inventory records while minimizing business disruption.

### Benefits of Cycle Counting
- **Improved Accuracy**: Regular counting helps identify and correct inventory discrepancies quickly
- **Reduced Downtime**: No need to shut down operations for full inventory counts
- **Better Control**: Continuous monitoring of inventory levels and locations
- **Cost Effective**: Reduces labor costs compared to full physical inventories
- **Data-Driven Decisions**: Analytics help optimize inventory management strategies

### Workflow Overview
1. **Schedule Creation**: Define when and how counts will be performed
2. **Batch Generation**: Create specific counting tasks based on the schedule
3. **Item Assignment**: Assign counting tasks to team members
4. **Count Execution**: Perform physical counts using mobile or desktop interface
5. **Discrepancy Review**: Identify and resolve counting discrepancies
6. **Adjustment Approval**: Apply necessary inventory adjustments
7. **Reporting**: Generate reports and analyze counting performance

## Getting Started

### Prerequisites
- Active user account with cycle count permissions
- Basic understanding of your inventory system
- Access to physical inventory locations

### Accessing Cycle Count Features
1. Log in to the SupplyLine MRO Suite
2. Navigate to the **Cycle Count** section from the main menu
3. The dashboard will display current schedules, active batches, and analytics

### User Permissions
Different user roles have different access levels:
- **Admin**: Full access to all cycle count features
- **Manager**: Can create schedules and approve adjustments
- **Counter**: Can perform counts and view assigned items
- **Viewer**: Read-only access to reports and analytics

## Creating Schedules

### Schedule Types
The system supports several counting methods:

#### ABC Analysis
- **A Items**: High-value items counted frequently (e.g., monthly)
- **B Items**: Medium-value items counted regularly (e.g., quarterly)
- **C Items**: Low-value items counted less frequently (e.g., annually)

#### Random Sampling
- Items selected randomly from the entire inventory
- Useful for general accuracy verification
- Configurable sample size and frequency

#### Location-Based
- Count all items in specific locations
- Ideal for organized storage areas
- Helps verify location accuracy

#### Category-Based
- Count items by category or type
- Useful for specialized inventory groups
- Allows focused counting efforts

### Creating a New Schedule

1. **Navigate to Schedules**
   - Click "Create Schedule" on the dashboard
   - Fill in the schedule details

2. **Basic Information**
   - **Name**: Descriptive name for the schedule
   - **Description**: Optional detailed description
   - **Frequency**: How often counts should occur
     - Daily, Weekly, Monthly, Quarterly, Annual

3. **Counting Method**
   - Select the appropriate method for your needs
   - Configure method-specific parameters

4. **Advanced Settings**
   - **Item Types**: Choose tools, chemicals, or both
   - **Categories**: Limit to specific categories if needed
   - **Locations**: Restrict to certain locations

5. **Save and Activate**
   - Review all settings
   - Save the schedule
   - Activate when ready to begin counting

### Schedule Management
- **Edit**: Modify schedule parameters as needed
- **Deactivate**: Temporarily stop batch generation
- **Archive**: Permanently disable old schedules
- **Clone**: Create similar schedules quickly

## Managing Batches

### What is a Batch?
A batch is a specific set of items to be counted during a defined time period. Batches are generated automatically based on schedules or can be created manually.

### Batch Lifecycle
1. **Draft**: Batch created but not yet active
2. **Active**: Counting is in progress
3. **Review**: Counting complete, pending review
4. **Completed**: All discrepancies resolved
5. **Archived**: Historical batch for reference

### Creating a Manual Batch

1. **Start New Batch**
   - Click "Create Batch" on the dashboard
   - Select the parent schedule

2. **Batch Details**
   - **Name**: Unique identifier for the batch
   - **Start Date**: When counting should begin
   - **End Date**: Counting deadline
   - **Notes**: Additional instructions or context

3. **Generate Items**
   - **Item Selection**: Choose generation method
   - **Sample Size**: Number of items to include
   - **Filters**: Apply category or location filters
   - **Preview**: Review items before finalizing

4. **Assign Counters**
   - **Auto-Assignment**: Distribute items evenly
   - **Manual Assignment**: Assign specific items to users
   - **Workload Balancing**: Consider user availability

### Batch Monitoring
- **Progress Tracking**: View completion percentages
- **Real-time Updates**: Monitor counting activity
- **Deadline Alerts**: Receive notifications for overdue batches
- **Performance Metrics**: Track counting efficiency

## Performing Counts

### Desktop Interface

#### Finding Your Assignments
1. Navigate to "My Assignments" or "Active Batches"
2. Select the batch you want to work on
3. View your assigned items list

#### Counting Process
1. **Locate Item**: Find the physical item using provided information
2. **Verify Details**: Confirm item identity and location
3. **Count Quantity**: Record actual quantity found
4. **Check Condition**: Note any condition issues
5. **Update Location**: Correct location if different
6. **Add Notes**: Include relevant observations
7. **Submit Count**: Save the count result

#### Handling Special Situations
- **Item Not Found**: Mark as missing and add notes
- **Extra Items**: Record unexpected items found
- **Damaged Items**: Note condition and take photos if possible
- **Location Changes**: Update item location in system

### Barcode Scanning
The system supports barcode scanning for faster, more accurate counting:

1. **Enable Scanner**: Click the barcode scan button
2. **Scan Item**: Point camera at barcode or QR code
3. **Auto-Population**: System fills in item details
4. **Verify and Submit**: Confirm details and submit count

### Quality Control
- **Double-Check**: Verify counts before submitting
- **Photo Documentation**: Take photos of discrepancies
- **Supervisor Review**: Flag items for additional review
- **Audit Trail**: All actions are logged for accountability

## Managing Discrepancies

### Types of Discrepancies
- **Quantity Variance**: Actual count differs from expected
- **Location Mismatch**: Item found in different location
- **Condition Issues**: Item condition differs from records
- **Missing Items**: Expected items not found
- **Extra Items**: Unexpected items discovered

### Discrepancy Resolution Process

#### 1. Initial Review
- Review all flagged discrepancies
- Verify counting accuracy
- Check for data entry errors

#### 2. Investigation
- **Recount**: Perform additional counts if needed
- **Research**: Check recent transactions
- **Documentation**: Gather supporting evidence

#### 3. Root Cause Analysis
- **Process Issues**: Identify procedural problems
- **System Errors**: Check for software issues
- **Training Needs**: Identify knowledge gaps

#### 4. Adjustment Approval
- **Manager Review**: Supervisor approves adjustments
- **Documentation**: Record justification for changes
- **System Update**: Apply approved adjustments

### Adjustment Types
- **Quantity Adjustments**: Correct inventory quantities
- **Location Updates**: Move items to correct locations
- **Status Changes**: Update item status or condition
- **Data Corrections**: Fix item information

## Reports and Analytics

### Available Reports

#### Summary Reports
- **Batch Summary**: Overview of batch completion and accuracy
- **Schedule Performance**: Analysis of schedule effectiveness
- **User Performance**: Individual counter productivity metrics
- **Discrepancy Analysis**: Trends in counting discrepancies

#### Detailed Reports
- **Item-Level Results**: Complete counting details for each item
- **Adjustment History**: Record of all inventory adjustments
- **Accuracy Trends**: Historical accuracy performance
- **Coverage Analysis**: Inventory coverage by location/category

#### Export Options
- **PDF Reports**: Professional formatted reports
- **Excel Export**: Detailed data for further analysis
- **CSV Files**: Raw data for custom reporting
- **Scheduled Reports**: Automatic report generation

### Analytics Dashboard

#### Key Performance Indicators (KPIs)
- **Counting Accuracy**: Percentage of items counted correctly
- **Completion Rate**: Percentage of batches completed on time
- **Discrepancy Rate**: Frequency of counting discrepancies
- **Productivity Metrics**: Items counted per hour/day

#### Trend Analysis
- **Historical Performance**: Track improvements over time
- **Seasonal Patterns**: Identify recurring trends
- **Category Analysis**: Compare performance by item type
- **Location Analysis**: Identify problem areas

#### Predictive Analytics
- **Accuracy Forecasting**: Predict future counting accuracy
- **Resource Planning**: Estimate counting resource needs
- **Risk Assessment**: Identify high-risk inventory areas

## Mobile Interface

### Mobile Features
The mobile interface is optimized for on-the-go counting:

#### Touch-Friendly Design
- Large buttons and text for easy interaction
- Swipe gestures for navigation
- Responsive layout for all screen sizes

#### Camera Integration
- **Barcode Scanning**: Built-in barcode reader
- **Photo Capture**: Document discrepancies with photos
- **QR Code Support**: Scan QR codes for quick item lookup

#### Offline Capability
- **Local Storage**: Work without internet connection
- **Sync When Connected**: Automatic data synchronization
- **Conflict Resolution**: Handle data conflicts gracefully

### Mobile Workflow
1. **Login**: Access mobile interface through web browser
2. **Select Batch**: Choose active counting batch
3. **Scan/Select Items**: Use barcode scanner or manual selection
4. **Enter Counts**: Input quantity and condition information
5. **Submit Results**: Save counts locally or sync immediately
6. **Review Progress**: Check completion status

### Mobile Best Practices
- **Battery Management**: Keep device charged during counting
- **Network Connectivity**: Sync regularly when connected
- **Data Backup**: Ensure counts are saved before closing app
- **Screen Protection**: Use screen protectors in industrial environments

## Troubleshooting

### Common Issues

#### Login Problems
- **Forgot Password**: Use password reset feature
- **Account Locked**: Contact administrator
- **Permission Denied**: Verify user role and permissions

#### Counting Issues
- **Barcode Won't Scan**: Clean barcode, adjust lighting
- **Item Not Found**: Check item number, verify location
- **System Slow**: Check network connection, clear browser cache

#### Data Problems
- **Missing Assignments**: Refresh page, check batch status
- **Count Not Saving**: Verify network connection, try again
- **Discrepancy Errors**: Double-check entered values

### Getting Help
- **User Manual**: Refer to this guide for detailed instructions
- **Help Desk**: Contact IT support for technical issues
- **Training**: Request additional training if needed
- **Feedback**: Report bugs or suggest improvements

### Best Practices
- **Regular Training**: Stay updated on new features
- **Data Accuracy**: Double-check all entries
- **Timely Completion**: Complete counts within deadlines
- **Communication**: Report issues promptly
- **Documentation**: Keep detailed notes for discrepancies

## Appendix

### Keyboard Shortcuts
- **Ctrl+S**: Save current count
- **Ctrl+N**: Start new count
- **Ctrl+F**: Search items
- **Esc**: Cancel current operation

### System Requirements
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+
- **Mobile**: iOS 12+, Android 8+
- **Network**: Stable internet connection recommended
- **Camera**: Required for barcode scanning

### Data Retention
- **Active Data**: Kept indefinitely
- **Completed Batches**: Archived after 2 years
- **Audit Logs**: Retained for 7 years
- **Reports**: Available for 5 years

---

*For technical support or additional training, please contact your system administrator.*
