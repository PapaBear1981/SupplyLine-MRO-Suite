# PowerShell script to run tests with required environment variables
# This ensures tests can run with the new security requirements

# Set test environment variables
$env:FLASK_ENV = "testing"
$env:SECRET_KEY = "test-secret-key-do-not-use-in-production"
$env:JWT_SECRET_KEY = "test-jwt-secret-key-do-not-use-in-production"

# Run pytest with all arguments passed to this script
if ($args.Count -eq 0) {
    # No arguments, run all tests
    python -m pytest -v
} else {
    # Run with provided arguments
    python -m pytest @args
}

# Exit with pytest's exit code
exit $LASTEXITCODE

