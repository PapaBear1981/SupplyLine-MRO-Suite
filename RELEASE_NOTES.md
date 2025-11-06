# SupplyLine MRO Suite Release Notes

## Version 5.1.0 - Barcode System Refactoring & Inventory Enhancements (2025-11-06)

### 🚀 MAJOR IMPROVEMENTS RELEASE

This release introduces a professional PDF-based barcode system, kit-only expendables management, child lot tracking for partial chemical issuances, and numerous UI/UX improvements. The barcode system has been completely refactored to use WeasyPrint for magazine-quality labels with support for multiple label sizes.

### 🏷️ Professional PDF-Based Barcode System

#### New Barcode Infrastructure
- **WeasyPrint Integration**: High-quality PDF generation from HTML/CSS templates
- **Vector Graphics**: SVG-based barcodes (python-barcode) and QR codes (segno) for crisp printing at any resolution
- **Multiple Label Sizes**: 4x6, 3x4, 2x4, 2x2 inches with responsive content scaling
- **Professional Design**: Magazine-quality typography and layout optimized for printing
- **Future-Ready**: Designed for Zebra printer compatibility while supporting standard PDF printing

#### Unified Barcode API
- **GET /api/barcode/tool/:id** - Generate tool label PDF
  - Query params: `label_size` (4x6, 3x4, 2x4, 2x2), `code_type` (barcode, qrcode)
- **GET /api/barcode/chemical/:id** - Generate chemical label PDF
  - Additional params: `is_transfer`, `parent_lot_number`, `destination`
- **GET /api/barcode/expendable/:id** - Generate expendable label PDF
  - Query params: `label_size`, `code_type`

#### Frontend Barcode Components
- **Centralized Barcode Service** (`barcodeService.js`): Single service for all barcode PDF generation
- **Updated Components**: ChemicalBarcode, ToolBarcode, ExpendableBarcode, KitItemBarcode
- **Automatic Printing**: Barcode modals appear after transfers and partial issuances

### 📦 Kit-Only Expendables System

#### New Expendable Model
- **Direct Kit Storage**: Add consumables directly to kits without warehouse management overhead
- **Lot/Serial Validation**: Mutually exclusive lot or serial number tracking
- **Full CRUD Operations**: Complete REST API for expendable management

#### Expendables API Endpoints
- **GET /api/expendables** - List all expendables with pagination
- **POST /api/expendables** - Create new expendable
- **GET /api/expendables/:id** - Get expendable details
- **PUT /api/expendables/:id** - Update expendable
- **DELETE /api/expendables/:id** - Delete expendable

#### Integration Features
- **Auto-Complete Transfers**: Warehouse-to-kit transfers complete immediately
- **Kit Transfer Integration**: Seamless integration with kit transfer system
- **Reorder Support**: Full integration with reorder request workflow
- **Barcode Printing**: Professional PDF labels for all expendables

### 🧬 Child Lot Tracking & Lineage

#### Automatic Child Lot Creation
- **Partial Issuance Detection**: Automatically creates child lots for partial chemical issuances
- **Parent-Child Lineage**: Complete tracking with `parent_lot_number` field
- **Lot Sequence Counter**: Track number of child lots created from each parent
- **Immediate Barcode Printing**: Automatic barcode modal for new child lots

#### Lot Number Auto-Generation
- **Format**: LOT-YYMMDD-XXXX (e.g., LOT-251106-0001)
- **Atomic Generation**: Row-level locking ensures uniqueness
- **Daily Sequence**: Automatic counter reset each day
- **API Endpoint**: GET /api/lot-numbers/generate

#### Inventory Transaction Tracking
- **Complete Audit Trail**: Full transaction history for all lot splits and transfers
- **API Endpoints**:
  - GET /api/inventory/transactions/:item_type/:item_id - Get transaction history
  - GET /api/inventory/detail/:item_type/:item_id - Get item details with transactions

### 📊 UI/UX Improvements

#### Sortable Tables
- **All Active Checkouts**: Sort by tool number, serial, description, user, dates
- **Kit Items**: Sort by box, part number, description, type, quantity, location, status
- **Visual Indicators**: Clear sort direction indicators (ascending/descending)

#### Dark Mode Enhancements
- **Fixed Table Headers**: Proper hover effect in dark mode (#2d3139 background)
- **Theme Consistency**: Removed hardcoded `bg-light` classes
- **Flash Prevention**: Inline script applies theme immediately on page load
- **Announcements Card**: Better theme compatibility with `fw-semibold` for unread items

#### Tool Location Display
- **Correct Location**: Tools now show warehouse OR kit location (never both)
- **Kit Display**: Kit name in warehouse column, box number in location column
- **Pagination Support**: Efficient handling of large tool datasets

### 🔧 Technical Improvements

#### Backend Code Quality
- **Ruff Migration**: Migrated from flake8 to Ruff for 10x faster linting
- **Auto-Fixed Issues**: Thousands of linting issues resolved (imports, quotes, whitespace)
- **Modern Python**: Includes pyupgrade and bugbear rules for best practices
- **Configuration**: Centralized in `pyproject.toml`

#### Enhanced Transfer Logic
- **Expendable Distinction**: Better handling of KitExpendable vs KitItem
- **Kit-to-Kit Transfers**: Remain pending until manually completed
- **Warehouse Transfers**: Auto-complete for immediate feedback
- **Improved Validation**: Better validation for expendable transfers

#### Reorder Fulfillment
- **Modify Existing**: Update existing expendables instead of creating duplicates
- **Status Updates**: Automatic status update to 'available' when quantity restored
- **Partial Fulfillment**: Better handling of partial reorder fulfillments

### 🐛 Critical Bug Fixes

#### Chemical Inventory Tracking
- **Child Lot Quantities**: Fixed quantities not updating after issuance
- **Child Lot Status**: Fixed status not updating when fully consumed (set to "issued")
- **Parent Lot Status**: Fixed status not updating when depleted or low stock
- **Reorder Status**: Fixed automatic reorder status updates

#### Transfer System
- **Expendable Validation**: Fixed transfer validation for expendables
- **Auto-Completion**: Fixed kit-to-kit transfers auto-completing incorrectly
- **Duplicate Prevention**: Fixed reorder fulfillment creating duplicate expendables

#### Tool Location
- **Dual Location Bug**: Fixed tools showing in both warehouse and kit
- **Location Display**: Fixed incorrect location information for tools in kits
- **Pagination**: Fixed pagination issues with large tool datasets

#### Frontend Fixes
- **E2E Tests**: Updated navigation tests to use Promise.all and expect /dashboard
- **JavaScript Errors**: Fixed sorting logic reference errors in KitItemsList
- **Theme Issues**: Fixed announcements card theme compatibility

### 📦 Dependency Updates

#### Backend Dependencies
- **WeasyPrint**: Added for professional PDF generation
- **segno**: Added for QR code generation (SVG format)
- **python-barcode**: Added for 1D barcode generation (SVG format)
- **Ruff**: Replaced flake8 for faster, modern linting

#### Frontend Dependencies
- **React 19**: Updated to latest React version
- **All Dependencies**: Updated to latest secure versions

### 🗑️ Removed Components

#### Deprecated Features
- **StandardBarcode.jsx**: Removed (replaced by PDF-based system)
- **labelSizeConfig.js**: Removed (replaced by backend label_config.py)
- **flake8**: Removed (replaced by Ruff)
- **.flake8**: Removed configuration file

### 📋 Migration Guide

#### Upgrading from v5.0.0

1. **Update Dependencies**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

2. **No Database Changes Required**:
   - All new features use existing database schema
   - No migrations needed

3. **Test Barcode Printing**:
   - Verify PDF generation works correctly
   - Test all label sizes (4x6, 3x4, 2x4, 2x2)
   - Test both barcode and QR code types

4. **Review Expendables System**:
   - Familiarize with new expendables workflow
   - Test expendable creation and transfers
   - Verify barcode printing for expendables

5. **Verify Child Lot Creation**:
   - Test partial chemical issuances
   - Verify child lot creation and barcode printing
   - Check lot lineage tracking

#### Breaking Changes
- **None**: This release is fully backward compatible
- All existing functionality continues to work
- New features are additive only

#### Configuration Changes
- **No Changes Required**: All configuration remains the same
- Existing environment variables continue to work

### 🎯 Testing Recommendations

#### Barcode System
- [ ] Generate tool labels in all sizes (4x6, 3x4, 2x4, 2x2)
- [ ] Generate chemical labels with transfer information
- [ ] Generate expendable labels
- [ ] Test QR code generation and scanning
- [ ] Verify PDF print quality

#### Expendables System
- [ ] Create new expendables directly in kits
- [ ] Transfer expendables from warehouse to kit
- [ ] Update expendable quantities
- [ ] Delete expendables
- [ ] Print expendable barcodes

#### Child Lot Tracking
- [ ] Issue partial chemical quantities
- [ ] Verify child lot creation
- [ ] Check automatic barcode printing
- [ ] Verify lot lineage tracking
- [ ] Test transaction history

#### UI/UX
- [ ] Test table sorting in All Active Checkouts
- [ ] Test table sorting in Kit Items
- [ ] Verify dark mode theme consistency
- [ ] Check tool location display accuracy
- [ ] Test pagination with large datasets

### 📝 Known Issues

- None reported

### 🙏 Acknowledgments

This release includes contributions from automated testing, code quality improvements, and user feedback. Special thanks to all users who reported issues and provided valuable feedback.

---

## Version 5.0.0 - Mobile Warehouse/Kits System (2025-10-12)

### 🚀 MAJOR FEATURE RELEASE

This release introduces the Mobile Warehouse (Kits) system, enabling tracking and management of mobile warehouses that follow aircraft to operating bases for maintenance operations.

See [CHANGELOG.md](CHANGELOG.md) for complete details.

---

## Version 4.0.0 - AWS Production Beta (2025-06-22)

### 🚀 MAJOR RELEASE - BREAKING CHANGES

This is a major architectural release that migrates the SupplyLine MRO Suite to AWS cloud infrastructure with significant security and scalability improvements. This release includes breaking changes and requires a fresh deployment.

### 🏗️ Infrastructure & Architecture Changes

#### AWS Cloud Migration
- **Complete AWS Infrastructure**: Migrated from Google Cloud to AWS using CloudFormation Infrastructure as Code
- **Container Orchestration**: Deployed on Amazon ECS Fargate for scalable container management
- **Database Migration**: Moved to Amazon RDS PostgreSQL for production-grade database management
- **CDN & Static Assets**: Frontend deployed to S3 with CloudFront CDN for global performance
- **Load Balancing**: Application Load Balancer with health checks and auto-scaling
- **Container Registry**: Amazon ECR for secure Docker image management

#### Security Infrastructure
- **AWS Secrets Manager**: Secure management of database passwords and JWT secrets
- **IAM Roles & Policies**: Least-privilege access controls for all AWS resources
- **VPC Security**: Private subnets with NAT Gateway for secure backend communication
- **SSL/TLS**: End-to-end encryption with AWS Certificate Manager
- **Security Groups**: Network-level security controls

### 🔐 Authentication System Overhaul

#### JWT-Based Authentication (BREAKING CHANGE)
- **Replaced Session-Based Auth**: Complete migration from Flask sessions to JWT tokens
- **Access Tokens**: Short-lived tokens (15 minutes) for API access
- **Refresh Tokens**: Long-lived tokens (7 days) for seamless user experience
- **CSRF Protection**: Enhanced CSRF protection using JWT token secrets
- **Token Revocation**: Secure token invalidation and refresh mechanisms

#### Security Enhancements
- **Password Security**: Improved password hashing and validation
- **Account Lockout**: Progressive lockout policy for failed login attempts
- **Audit Logging**: Comprehensive security event logging
- **Permission System**: Granular role-based access control

### 🛠️ Development & Deployment

#### DevOps Improvements
- **GitHub Actions CI/CD**: Automated testing and deployment pipeline
- **Docker Optimization**: Multi-stage builds and security hardening
- **Infrastructure as Code**: Complete AWS infrastructure defined in CloudFormation
- **Automated Deployments**: One-command deployment to AWS
- **Health Monitoring**: Application health checks and monitoring

#### Testing & Quality
- **Playwright Testing**: End-to-end browser testing integration
- **Security Testing**: Automated security vulnerability scanning
- **Database Testing**: PostgreSQL integration testing
- **Cross-Platform Testing**: Chrome and Firefox browser compatibility

### 🔧 Technical Improvements

#### Backend Enhancements
- **PyJWT Integration**: Added PyJWT 2.8.0 for secure token management
- **Database Optimization**: PostgreSQL-specific optimizations and migrations
- **API Security**: Enhanced API endpoint security and validation
- **Error Handling**: Improved error handling and logging

#### Frontend Updates
- **Token Management**: Client-side JWT token handling and refresh
- **API Integration**: Updated API calls for JWT authentication
- **Security Headers**: Enhanced security headers and CSRF protection
- **Performance**: Optimized for CDN delivery and caching

### 🚨 Security Fixes

#### Critical Vulnerabilities Resolved
- **Issue #363**: Fixed authentication bypass vulnerability
- **Issue #364**: Resolved privilege escalation security flaw
- **Admin Security**: Enhanced admin account creation and password reset security
- **Secure Key Generation**: Automated secure key generation for production

### 📋 Migration Guide

#### For Existing Installations
1. **Data Backup**: Export all data before migration
2. **AWS Setup**: Configure AWS account and credentials
3. **Infrastructure Deployment**: Deploy CloudFormation stacks
4. **Database Migration**: Migrate data to RDS PostgreSQL
5. **DNS Update**: Update DNS to point to new AWS infrastructure
6. **User Re-authentication**: All users must log in again due to JWT migration

#### Breaking Changes
- **Authentication**: Session-based authentication no longer supported
- **Database**: SQLite no longer supported in production (PostgreSQL required)
- **Environment Variables**: New environment variables required for AWS deployment
- **API Endpoints**: Some API responses changed due to JWT implementation

### 🎯 Beta Testing Focus Areas

This AWS production beta release focuses on:
- **Infrastructure Stability**: AWS resource provisioning and scaling
- **Authentication Flow**: JWT token management and user experience
- **Database Performance**: PostgreSQL performance under load
- **Security Validation**: End-to-end security testing
- **Deployment Process**: CloudFormation and CI/CD pipeline validation

### 📚 Documentation Updates

- **AWS Deployment Guide**: Comprehensive AWS deployment instructions
- **Security Documentation**: Updated security implementation details
- **API Documentation**: JWT authentication API reference
- **Migration Guide**: Step-by-step migration instructions

### ⚠️ Known Issues

- **First-Time Setup**: Initial AWS deployment may take 15-20 minutes
- **Database Migration**: Large datasets may require extended migration time
- **DNS Propagation**: DNS changes may take up to 24 hours to propagate globally

### 🔄 Upgrade Path

**From 3.x to 4.0.0:**
1. Complete data backup
2. Deploy new AWS infrastructure
3. Migrate database to PostgreSQL
4. Update DNS configuration
5. Test authentication and core functionality
6. Train users on any UI changes

---

## Version 3.5.4 (Previous)

### Bug Fixes
- Fixed issue #4: Add New Tool functionality not working
  - Tools can now be successfully added through the UI
  - Added success message when a tool is created
  - Improved error handling for tool creation
  - Fixed backend API to return complete tool data

## Version 3.5.2 (Current)

### Features
- Added calibration management for tools
- Improved chemical inventory tracking
- Enhanced reporting capabilities

### Bug Fixes
- Fixed issue with checkout history not displaying correctly
- Resolved authentication issues for some user roles
- Improved error handling for network failures

## Version 3.5.1

### Features
- Added barcode generation for chemicals
- Implemented expiration date tracking for chemicals
- Added reorder notifications for low stock items

### Bug Fixes
- Fixed search functionality in tools list
- Resolved issue with user permissions for tool checkout
- Fixed date formatting in reports

## Version 3.5.0

### Major Features
- Complete UI redesign with improved user experience
- Added chemical inventory management
- Implemented tool service history tracking
- Added comprehensive reporting system
- Improved user management with role-based permissions

### Bug Fixes
- Multiple performance improvements
- Enhanced security for user authentication
- Fixed various UI inconsistencies
