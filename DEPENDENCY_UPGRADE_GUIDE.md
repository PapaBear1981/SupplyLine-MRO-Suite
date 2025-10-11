# Dependency Upgrade Guide - Issue #413

This document provides guidance for upgrading dependencies to address security vulnerabilities identified in issue #413.

## Overview

Multiple dependencies have been updated to their latest secure versions to address known vulnerabilities:

| Package | Old Version | New Version | Severity | Notes |
|---------|-------------|-------------|----------|-------|
| Flask | 2.2.3 | 3.1.0 | High | Security patches, bug fixes |
| Werkzeug | 2.2.3 | 3.1.3 | Critical | Fixes CVE-2023-25577, CVE-2023-46136 |
| SQLAlchemy | 1.4.46 | 2.0.36 | High | **Major version upgrade** |
| Flask-SQLAlchemy | 2.5.1 | 3.1.1 | Medium | Compatibility with SQLAlchemy 2.x |
| Flask-Session | 0.4.0 | 0.8.0 | Medium | Security improvements |
| Flask-CORS | 4.0.0 | 5.0.0 | Medium | Better security defaults |
| PyJWT | 2.8.0 | 2.10.1 | High | Security patches |
| gunicorn | 20.1.0 | 23.0.0 | High | Security and performance |
| python-json-logger | 2.0.7 | 3.2.1 | Low | Compatibility |
| psutil | 5.9.5 | 6.1.1 | Low | Bug fixes |
| psycopg2-binary | 2.9.7 | 2.9.10 | Medium | Security patches |
| reportlab | 4.0.4 | 4.2.5 | Medium | Security patches |
| openpyxl | 3.1.2 | 3.1.5 | Medium | Security patches |

## Upgrade Process

### 1. Backup Current Environment

```bash
# Backup current requirements
cp backend/requirements.txt backend/requirements.txt.backup

# Backup database (if using SQLite)
cp database/tools.db database/tools.db.backup

# Or backup PostgreSQL
pg_dump your_database > backup.sql
```

### 2. Update Dependencies

```bash
cd backend
pip install -r requirements.txt --upgrade
```

### 3. Test the Application

```bash
# Run test suite
python -m pytest tests/ -v

# Test critical functionality
# - User authentication
# - Database operations
# - API endpoints
# - File uploads
```

## Breaking Changes and Migration Notes

### SQLAlchemy 1.4 → 2.0 (Major Version Upgrade)

This is the most significant change. SQLAlchemy 2.0 includes breaking changes.

#### Key Changes:

1. **Query API Changes**
   - Old style: `User.query.filter_by(id=1).first()`
   - New style: `db.session.execute(select(User).filter_by(id=1)).scalar_one_or_none()`
   - **Good news**: The legacy query API is still supported in 2.0 for backward compatibility

2. **Session Handling**
   - The application currently uses Flask-SQLAlchemy which handles session management
   - No immediate changes required, but be aware of new patterns

3. **Type Annotations**
   - SQLAlchemy 2.0 has better type hint support
   - Consider adding type hints to models in future updates

#### Migration Strategy:

**Option 1: Gradual Migration (Recommended)**
- SQLAlchemy 2.0 supports the 1.x query API for backward compatibility
- Current code should work without changes
- Gradually migrate to 2.0 style queries over time

**Option 2: Immediate Migration**
- Update all queries to use the new select() API
- More work upfront but cleaner code
- See SQLAlchemy 2.0 migration guide: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html

### Flask 2.x → 3.x

Minor changes, mostly backward compatible:

1. **Deprecated Features Removed**
   - Check for any deprecation warnings in logs
   - Update any deprecated function calls

2. **Extension Compatibility**
   - All Flask extensions have been updated to compatible versions
   - No action required

### Werkzeug 2.x → 3.x

1. **Security Fixes**
   - CVE-2023-25577: DoS vulnerability fixed
   - CVE-2023-46136: Path traversal vulnerability fixed

2. **API Changes**
   - Mostly backward compatible
   - Check for deprecation warnings

## Testing Checklist

After upgrading, verify the following functionality:

- [ ] Application starts without errors
- [ ] User authentication works (login/logout)
- [ ] Password reset functionality works
- [ ] Database queries execute correctly
- [ ] API endpoints respond correctly
- [ ] File uploads work
- [ ] Reports generate correctly
- [ ] Excel import/export works
- [ ] PDF generation works
- [ ] All tests pass

## Rollback Procedure

If issues occur after upgrade:

```bash
# Restore old requirements
cp backend/requirements.txt.backup backend/requirements.txt

# Reinstall old versions
pip install -r backend/requirements.txt --force-reinstall

# Restore database if needed
cp database/tools.db.backup database/tools.db
# Or for PostgreSQL:
psql your_database < backup.sql
```

## Known Issues and Workarounds

### Issue: SQLAlchemy 2.0 Query Deprecation Warnings

**Symptom**: Deprecation warnings in logs about legacy query API

**Solution**: These are warnings, not errors. The code will continue to work. Plan to migrate queries gradually.

### Issue: Type Checking Errors with SQLAlchemy 2.0

**Symptom**: MyPy or other type checkers report errors

**Solution**: Update type hints or configure type checker to use SQLAlchemy 2.0 stubs

## Performance Improvements

The upgraded dependencies include several performance improvements:

1. **SQLAlchemy 2.0**: Faster query execution, better connection pooling
2. **gunicorn 23.0**: Improved worker management, better performance
3. **Flask 3.1**: Faster request handling

## Security Improvements

1. **Werkzeug 3.1.3**: Fixes critical DoS and path traversal vulnerabilities
2. **PyJWT 2.10.1**: Fixes JWT validation bypass issues
3. **All packages**: Latest security patches applied

## Continuous Monitoring

After upgrade, monitor for:

1. **Error Logs**: Check application logs for new errors
2. **Performance**: Monitor response times and resource usage
3. **Security Alerts**: Subscribe to security advisories for dependencies

## Automated Dependency Management

Consider implementing:

1. **Dependabot**: Automated dependency updates via GitHub
2. **Safety**: Regular security scans of dependencies
3. **pip-audit**: Audit dependencies for known vulnerabilities

### Setup Dependabot

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

### Setup Safety Checks

```bash
pip install safety
safety check -r backend/requirements.txt
```

## Support and Resources

- SQLAlchemy 2.0 Migration Guide: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html
- Flask 3.x Changelog: https://flask.palletsprojects.com/en/3.0.x/changes/
- Werkzeug 3.x Changelog: https://werkzeug.palletsprojects.com/en/3.0.x/changes/

## Questions?

If you encounter issues during the upgrade:

1. Check the error logs for specific error messages
2. Review the migration guides linked above
3. Test in a development environment first
4. Create a GitHub issue with details if problems persist

