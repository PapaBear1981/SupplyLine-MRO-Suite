# PowerShell script to run tests with required environment variables
# This ensures tests can run with the new security requirements

# Set test environment variables
$env:FLASK_ENV = "testing"
$env:SECRET_KEY = "test-secret-key-do-not-use-in-production"
$env:JWT_SECRET_KEY = "test-jwt-secret-key-do-not-use-in-production"

# Run pytest
python -m pytest tests/test_issue_410_secret_keys.py -v

# Exit with pytest's exit code
exit $LASTEXITCODE

