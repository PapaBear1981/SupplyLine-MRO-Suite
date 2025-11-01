# Security Notes

This document tracks known security issues and their mitigation strategies.

## Known Vulnerabilities

### Frontend Dependencies

#### xlsx (SheetJS) - High Severity
- **Package**: `xlsx@0.18.5`
- **Vulnerabilities**:
  - Prototype Pollution (GHSA-4r6h-8v6p-xvw6)
  - Regular Expression Denial of Service - ReDoS (GHSA-5pgg-2g8v-p4x9)
- **Status**: No fix available as of 2025-10-26
- **Usage**: Used in `CalibrationReports.jsx` for exporting calibration data to Excel format
- **Mitigation**:
  - Library is only used for **client-side export** functionality
  - No user-provided data is parsed by xlsx (only application-generated data is exported)
  - The prototype pollution and ReDoS vulnerabilities require malicious Excel files to be **imported**, which we do not do
  - We only use xlsx to **export** data, not import/parse untrusted files
  - Risk is minimal as the attack vector (importing malicious Excel files) is not present in our application
- **Recommendation**: Monitor for updates to xlsx or consider alternative libraries when available
- **Alternative Options**:
  - Backend-only Excel generation using `openpyxl` (Python) - already implemented for some reports
  - Consider migrating all Excel exports to backend using `openpyxl@3.1.5` which has no known vulnerabilities

## Security Best Practices Implemented

### Bandit Static Analysis
All Bandit security issues have been addressed:

1. **B104 - Hardcoded bind to all interfaces**: Documented with `#nosec` - intentional for Docker/development
2. **B113 - Requests without timeout**: Fixed by adding 10-second timeouts to all HTTP requests
3. **B108 - Hardcoded /tmp directory**: Fixed by using `tempfile.gettempdir()` for cross-platform compatibility

### Session Management
- Implemented an inactivity auto-logout that defaults to **30 minutes** and is enforced on both the backend session validator and the frontend client.
- Administrators can adjust the timeout from **Admin Dashboard → System Settings → Security Settings**. Updates are persisted to the database, immediately applied to new requests, and recorded in the audit log for traceability.

### npm Audit
- **Vite vulnerability**: Fixed by running `npm audit fix`
- **xlsx vulnerability**: Documented above with mitigation strategy

## Security Scanning

This project uses automated security scanning:
- **Bandit**: Python static analysis security testing
- **npm audit**: JavaScript dependency vulnerability scanning
- **GitHub Dependabot**: Automated dependency updates for security patches

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainers directly rather than opening a public issue.

