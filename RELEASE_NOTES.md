# SupplyLine MRO Suite Release Notes

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
