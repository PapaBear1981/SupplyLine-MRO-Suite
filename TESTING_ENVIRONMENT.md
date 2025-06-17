# Testing Environment Configuration

This document describes the environment variables required for running the comprehensive testing suite.

## Required Environment Variables

### Admin Credentials

For security reasons, admin credentials are loaded from environment variables rather than being hard-coded in the test scripts.

```bash
# Admin user credentials for testing
export SL_ADMIN_EMP_NUM="ADMIN001"
export SL_ADMIN_PWD="admin123"

# Admin password for reset script
export ADMIN_INIT_PASSWORD="admin123"

# Application secret key (for production use a secure random key)
export SECRET_KEY="your-secure-secret-key-here"
```

### Setting Environment Variables

#### Linux/macOS
```bash
# Set for current session
export SL_ADMIN_EMP_NUM="ADMIN001"
export SL_ADMIN_PWD="admin123"
export ADMIN_INIT_PASSWORD="admin123"

# Or create a .env file and source it
echo 'export SL_ADMIN_EMP_NUM="ADMIN001"' >> .env
echo 'export SL_ADMIN_PWD="admin123"' >> .env
echo 'export ADMIN_INIT_PASSWORD="admin123"' >> .env
source .env
```

#### Windows
```cmd
# Command Prompt
set SL_ADMIN_EMP_NUM=ADMIN001
set SL_ADMIN_PWD=admin123
set ADMIN_INIT_PASSWORD=admin123

# PowerShell
$env:SL_ADMIN_EMP_NUM="ADMIN001"
$env:SL_ADMIN_PWD="admin123"
$env:ADMIN_INIT_PASSWORD="admin123"
```

## Running Tests

Once environment variables are set, you can run the test suites:

```bash
# Security Testing
python security_tests.py

# Performance Testing  
python performance_tests.py

# Functionality Testing
python functionality_tests.py

# Database Security Testing
python database_security_tests.py

# Reset admin password (requires ADMIN_INIT_PASSWORD)
cd backend
python reset_admin_password.py
```

## Production Considerations

### Secret Key
In production, use a cryptographically secure secret key:

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set it as environment variable
export SECRET_KEY="your-generated-secure-key"
```

### Admin Password
In production, use a strong password and rotate it regularly:

```bash
# Use a strong password
export ADMIN_INIT_PASSWORD="your-strong-password-here"
```

### CI/CD Integration

For continuous integration, set these variables in your CI/CD system:

#### GitHub Actions
```yaml
env:
  SL_ADMIN_EMP_NUM: ${{ secrets.SL_ADMIN_EMP_NUM }}
  SL_ADMIN_PWD: ${{ secrets.SL_ADMIN_PWD }}
  ADMIN_INIT_PASSWORD: ${{ secrets.ADMIN_INIT_PASSWORD }}
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

#### Docker
```dockerfile
ENV SL_ADMIN_EMP_NUM=ADMIN001
ENV SL_ADMIN_PWD=admin123
ENV ADMIN_INIT_PASSWORD=admin123
ENV SECRET_KEY=your-secure-key
```

## Security Notes

1. **Never commit credentials to version control**
2. **Use different credentials for different environments**
3. **Rotate passwords regularly**
4. **Use secrets management in production**
5. **Limit access to environment variables**

## Troubleshooting

### Missing Environment Variables
If you see errors like "ADMIN_INIT_PASSWORD environment variable must be set", ensure all required variables are exported in your current shell session.

### Test Failures
If tests fail with authentication errors, verify:
1. Environment variables are set correctly
2. Admin user exists in the database
3. Backend server is running on localhost:5000

### Default Values
The test scripts include fallback values for development:
- `SL_ADMIN_EMP_NUM` defaults to "ADMIN001"
- `SL_ADMIN_PWD` defaults to "admin123"

However, the admin reset script requires `ADMIN_INIT_PASSWORD` to be explicitly set for security.
