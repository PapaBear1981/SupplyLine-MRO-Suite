# SupplyLine MRO Suite Documentation

## Documentation Index

This directory contains comprehensive documentation for the SupplyLine MRO Suite v5.1.0.

### Getting Started

- **[README.md](../README.md)** - Main project overview, features, and quick start guide
- **[CHANGELOG.md](../CHANGELOG.md)** - Complete version history and change log
- **[RELEASE_NOTES.md](../RELEASE_NOTES.md)** - Detailed release notes with migration guides

### User Guides

- **[KITS_USER_GUIDE.md](KITS_USER_GUIDE.md)** - Complete guide to using the mobile warehouse/kits system
  - Creating and managing kits
  - Adding and organizing items
  - Issuing items from kits
  - Transferring items between kits and warehouses
  - Managing expendables
  - Barcode printing
  - Reordering workflow
  - Messaging system

### System Documentation

#### Barcode & Label System (v5.1.0+)
- **[BARCODE_SYSTEM.md](BARCODE_SYSTEM.md)** - Professional PDF-based barcode system
  - Architecture and components
  - Label sizes (4x6, 3x4, 2x4, 2x2 inches)
  - Barcode vs QR code usage
  - API endpoints
  - Frontend components
  - Printing workflow
  - Best practices

#### Warehouse Management (v5.1.0+)
- **[WAREHOUSE_MANAGEMENT.md](WAREHOUSE_MANAGEMENT.md)** - Warehouse operations and management
  - Creating and managing warehouses
  - Warehouse types (main/satellite)
  - Inventory tracking
  - Transfer workflows
  - API endpoints
  - Best practices

#### Expendables System (v5.1.0+)
- **[EXPENDABLES_SYSTEM.md](EXPENDABLES_SYSTEM.md)** - Kit-only expendables management
  - What are expendables
  - Adding expendables to kits
  - Direct addition vs warehouse transfer
  - Issuing and reordering
  - Barcode printing
  - API endpoints
  - Workflow examples

### API Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete REST API reference
  - Authentication
  - Warehouses API
  - Tools API
  - Chemicals API
  - Expendables API
  - Kits API
  - Transfers API
  - Barcode API
  - Inventory Tracking API
  - Lot Number API
  - Reorder API
  - Error responses
  - Rate limiting
  - Pagination

### Security & Deployment

- **[SECURITY_SETUP.md](../SECURITY_SETUP.md)** - Security configuration and best practices
- **[SECURITY_COMPLIANCE.md](../SECURITY_COMPLIANCE.md)** - Compliance and audit requirements
- **[DEPLOYMENT.md](../DEPLOYMENT.md)** - Deployment guide for production environments

## What's New in v5.1.0

### 🏷️ Professional PDF-Based Barcode System
- WeasyPrint integration for magazine-quality labels
- SVG vector graphics for crisp printing
- 4 label sizes: 4x6, 3x4, 2x4, 2x2 inches
- Support for both 1D barcodes and 2D QR codes
- Automatic barcode printing after transfers
- Mobile-friendly QR code landing pages

### 📦 Kit-Only Expendables System
- Add consumables directly to kits
- Full CRUD operations via REST API
- Lot/serial number tracking
- Auto-complete warehouse transfers
- Integrated reorder workflow
- Professional barcode labels

### 🧬 Child Lot Tracking & Lineage
- Automatic child lot creation for partial issuances
- Parent-child lot lineage tracking
- Auto-generated lot numbers (LOT-YYMMDD-XXXX)
- Complete transaction audit trail
- Immediate barcode printing for child lots

### 📊 UI/UX Improvements
- Sortable tables in All Active Checkouts and Kit Items
- Fixed dark mode theme consistency
- Improved tool location display
- Better pagination for large datasets
- Enhanced flash message prevention

### 🔧 Technical Improvements
- Migrated from flake8 to Ruff for faster linting
- Enhanced transfer logic for expendables
- Improved reorder fulfillment
- React 19 frontend updates
- Better error handling and validation

## Quick Navigation

### For End Users
1. Start with [KITS_USER_GUIDE.md](KITS_USER_GUIDE.md) to learn how to use the system
2. Review [BARCODE_SYSTEM.md](BARCODE_SYSTEM.md) for barcode printing instructions
3. Check [EXPENDABLES_SYSTEM.md](EXPENDABLES_SYSTEM.md) for managing consumables

### For Administrators
1. Review [WAREHOUSE_MANAGEMENT.md](WAREHOUSE_MANAGEMENT.md) for warehouse setup
2. Check [SECURITY_SETUP.md](../SECURITY_SETUP.md) for security configuration
3. See [DEPLOYMENT.md](../DEPLOYMENT.md) for production deployment

### For Developers
1. Start with [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API reference
2. Review [CHANGELOG.md](../CHANGELOG.md) for technical changes
3. Check [README.md](../README.md) for development setup

## Documentation Standards

All documentation follows these standards:
- **Markdown Format**: All docs use GitHub-flavored Markdown
- **Version Tags**: Features tagged with version introduced (e.g., v5.1.0+)
- **Code Examples**: Practical examples with request/response samples
- **Cross-References**: Links to related documentation
- **Screenshots**: Visual guides where applicable (coming soon)

## Contributing to Documentation

When updating documentation:
1. Keep examples practical and tested
2. Include version tags for new features
3. Update cross-references when adding new docs
4. Follow existing formatting conventions
5. Test all code examples before committing

## Support

For questions or issues:
- Check the relevant documentation first
- Review [CHANGELOG.md](../CHANGELOG.md) for recent changes
- See [RELEASE_NOTES.md](../RELEASE_NOTES.md) for migration guides
- Contact your system administrator

## Version History

- **v5.1.0** (2025-11-06) - Barcode system refactoring, expendables, child lot tracking
- **v5.0.0** (2025-10-12) - Mobile warehouse/kits system
- **v4.0.0** (2025-06-22) - AWS production beta
- **v3.0.0** (2025-05-15) - Chemical management enhancements
- **v2.0.0** (2025-04-01) - Tool calibration system
- **v1.0.0** (2025-03-01) - Initial release

## License

Copyright © 2025 SupplyLine MRO Suite. All rights reserved.

