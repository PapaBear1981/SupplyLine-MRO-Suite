# Testing Guide - SupplyLine MRO Suite

Comprehensive testing documentation for the SupplyLine MRO Suite backend.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Test Fixtures](#test-fixtures)
- [Coverage Reports](#coverage-reports)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The test suite consists of **31 test files** with **500+ test functions** covering:

- ✅ **Authentication & Authorization** - JWT, RBAC, password security
- ✅ **Performance Testing** - Bulk operations, query optimization, benchmarking
- ✅ **Security Testing** - CORS, file uploads, injection attacks, cryptography
- ✅ **API Endpoints** - All major routes and business logic
- ✅ **Data Models** - Database integrity, relationships, constraints
- ✅ **Messaging System** - Channels, real-time features, attachments
- ✅ **Bulk Operations** - CSV imports, data validation, error handling
- ✅ **Calibration Workflows** - Due dates, certificates, notifications
- ✅ **Reports & Analytics** - Inventory reports, usage analytics, exports
- ✅ **Concurrency** - Race conditions, data integrity, deadlocks

### Test Statistics

```
Total Test Files: 31
Total Tests: 500+
Total Lines of Test Code: ~10,000+
Average Test Execution Time: ~2-5 minutes (full suite)
```

---

## Test Structure

```
backend/
├── tests/
│   ├── conftest.py                      # Global fixtures and configuration
│   │
│   ├── test_auth.py                     # Authentication tests
│   ├── test_auth_security.py            # Auth security edge cases
│   ├── test_authorization.py            # RBAC and permissions
│   │
│   ├── test_security_extended.py        # ⭐ Advanced security tests
│   ├── test_security_assessment.py      # Security compliance
│   ├── test_input_validation.py         # Input sanitization
│   ├── test_rate_limiting.py            # Rate limiting & throttling
│   │
│   ├── test_performance.py              # ⭐ Performance benchmarks
│   ├── test_concurrency_integrity.py    # ⭐ Concurrency & data integrity
│   │
│   ├── test_models.py                   # Core data models
│   ├── test_models_kits.py              # Kit system models
│   ├── test_models_messaging.py         # Messaging models
│   │
│   ├── test_routes.py                   # Main API routes
│   ├── test_routes_*.py                 # Specific route modules (9 files)
│   │
│   ├── test_messaging_extended.py       # ⭐ Complete messaging tests
│   ├── test_bulk_import.py              # ⭐ Bulk CSV import tests
│   ├── test_calibration_workflows.py    # ⭐ Calibration management
│   ├── test_reports_analytics.py        # ⭐ Reports & analytics
│   │
│   ├── test_kit_workflows.py            # Kit operations
│   ├── test_unified_requests.py         # Unified request system
│   │
│   └── test_issue_*.py                  # Security issue tests (5 files)
│
└── pytest.ini                           # Pytest configuration
```

⭐ = New comprehensive test files

---

## Running Tests

### Quick Start

```bash
# Navigate to backend directory
cd backend

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run fast tests only (exclude slow tests)
pytest tests/ -m "not slow"
```

### Run by Category

```bash
# Performance tests
pytest -m performance

# Security tests
pytest -m security

# Concurrency tests
pytest -m concurrency

# API tests
pytest -m api

# Model tests
pytest -m models

# Authentication tests
pytest -m auth

# Bulk operation tests
pytest -m bulk

# Messaging tests
pytest -m messaging

# Calibration tests
pytest -m calibration

# Reports and analytics
pytest -m reports -m analytics
```

### Run Specific Test Files

```bash
# Single file
pytest tests/test_performance.py -v

# Multiple files
pytest tests/test_security_extended.py tests/test_concurrency_integrity.py -v

# Specific test class
pytest tests/test_performance.py::TestBulkOperations -v

# Specific test function
pytest tests/test_security_extended.py::TestCORSPolicy::test_cors_headers_present -v
```

### Advanced Options

```bash
# Show slowest 10 tests
pytest --durations=10

# Show slowest 20 tests
pytest --durations=20

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Verbose output with print statements
pytest -v -s

# Quiet mode (minimal output)
pytest -q
```

---

## Test Categories

### 1. Performance Tests (`test_performance.py`)

**Purpose**: Ensure system performs efficiently under load

**Tests Include**:
- Bulk chemical creation (100 items in < 5s)
- Bulk tool creation (100 items in < 5s)
- Large audit log queries (500 items in < 1s)
- Inventory transaction queries (500 items in < 1s)
- Kit item eager loading (no N+1 queries)
- Pagination performance (1000 items in < 0.5s)
- API response times (200 items in < 2s)

**Run**: `pytest -m performance -v`

**Thresholds**:
- Bulk operations: < 5 seconds for 100 items
- Database queries: < 1 second for 500 records
- API endpoints: < 2 seconds for 200 items
- Pagination: < 0.5 seconds per page

### 2. Security Tests (`test_security_extended.py`)

**Purpose**: Validate security controls and prevent vulnerabilities

**Tests Include**:
- CORS policy enforcement
- Security headers (X-Frame-Options, CSP, etc.)
- File upload attacks (path traversal, null bytes, polyglots)
- JWT security (tampering, algorithm substitution)
- Password timing attack resistance
- SQL/NoSQL injection protection
- Mass assignment prevention
- Information disclosure prevention
- Session security (fixation, token invalidation)

**Run**: `pytest -m security -v`

**Key Areas**:
- **File Security**: Path traversal, MIME validation, size limits
- **Cryptography**: JWT signature verification, strong hashing
- **API Security**: Injection protection, rate limiting
- **Information Leakage**: Error messages, user enumeration

### 3. Messaging Tests (`test_messaging_extended.py`)

**Purpose**: Validate complete messaging system functionality

**Tests Include**:
- Channel creation (department, private, group)
- Channel member management (add/remove)
- Message CRUD operations
- Message pagination (large conversations)
- Reactions (add/remove emojis)
- Typing indicators
- User presence tracking
- Message search (channel and global)
- Message attachments (upload/download)

**Run**: `pytest -m messaging -v`

### 4. Bulk Import Tests (`test_bulk_import.py`)

**Purpose**: Ensure bulk data import is robust and secure

**Tests Include**:
- CSV chemical import (valid data)
- CSV tool import
- Validation error handling
- Duplicate detection
- Large dataset imports (100-1000 items)
- Invalid CSV format rejection
- Special character handling
- Transaction rollback on errors
- Import performance (500 items < 30s)
- SQL injection protection
- CSV formula injection protection

**Run**: `pytest -m bulk -v`

### 5. Calibration Tests (`test_calibration_workflows.py`)

**Purpose**: Validate tool calibration management

**Tests Include**:
- Calibration record creation
- Tool status updates on calibration
- Failed calibration handling
- Calibration history retrieval
- Certificate uploads
- Due date tracking
- Overdue tool identification
- Calibration reminders
- Expired calibration prevention

**Run**: `pytest -m calibration -v`

### 6. Reports & Analytics (`test_reports_analytics.py`)

**Purpose**: Validate reporting and analytics functionality

**Tests Include**:
- Inventory reports (tools, chemicals)
- Low stock reports
- Expiring items reports
- Tool usage analytics
- Chemical consumption analytics
- User activity analytics
- Warehouse utilization
- Trend analysis (30-day patterns)
- Report exports (CSV, Excel, PDF)
- Report generation performance (500 items < 5s)

**Run**: `pytest -m reports -m analytics -v`

### 7. Concurrency & Integrity (`test_concurrency_integrity.py`)

**Purpose**: Ensure data integrity under concurrent access

**Tests Include**:
- Concurrent chemical quantity updates
- Concurrent tool checkout prevention
- Race condition handling
- Transaction isolation
- Inventory consistency validation
- Unique constraint enforcement
- Foreign key constraint validation
- NOT NULL constraint enforcement
- Transaction rollback on errors
- Deadlock prevention
- Atomic operations

**Run**: `pytest -m concurrency -v`

---

## Writing Tests

### Test File Template

```python
"""
Module description

Tests for:
- Feature 1
- Feature 2
- Feature 3
"""

import pytest
from models import YourModel

@pytest.mark.your_marker
@pytest.mark.integration
class TestYourFeature:
    """Test your feature description"""

    def test_basic_operation(self, client, db_session, auth_headers):
        """Test basic operation works correctly"""
        # Arrange
        data = {"field": "value"}

        # Act
        response = client.post("/api/endpoint",
                             headers=auth_headers,
                             json=data)

        # Assert
        assert response.status_code == 201
        result = response.get_json()
        assert result["field"] == "value"

    def test_error_handling(self, client, auth_headers):
        """Test error handling for invalid input"""
        # Arrange
        invalid_data = {"field": None}

        # Act
        response = client.post("/api/endpoint",
                             headers=auth_headers,
                             json=invalid_data)

        # Assert
        assert response.status_code == 400
        error = response.get_json()
        assert "error" in error
```

### Best Practices

1. **Use Descriptive Names**
   ```python
   # Good
   def test_user_cannot_access_admin_endpoint(self, ...):

   # Bad
   def test_endpoint(self, ...):
   ```

2. **Follow AAA Pattern** (Arrange, Act, Assert)
   ```python
   def test_create_chemical(self, client, db_session):
       # Arrange - Set up test data
       data = {"part_number": "TEST001", ...}

       # Act - Perform the action
       response = client.post("/api/chemicals", json=data)

       # Assert - Verify the outcome
       assert response.status_code == 201
   ```

3. **Use Appropriate Markers**
   ```python
   @pytest.mark.performance  # For performance tests
   @pytest.mark.slow         # For tests taking > 1 second
   @pytest.mark.integration  # For integration tests
   @pytest.mark.unit         # For unit tests
   @pytest.mark.security     # For security tests
   ```

4. **Clean Up Resources**
   ```python
   def test_with_cleanup(self, db_session):
       # Create test data
       item = create_test_item()

       try:
           # Test logic
           assert item is not None
       finally:
           # Cleanup happens automatically via db_session fixture
           pass
   ```

5. **Test Edge Cases**
   ```python
   def test_empty_list(self, ...):
       """Test behavior with empty list"""

   def test_null_value(self, ...):
       """Test behavior with null value"""

   def test_maximum_length(self, ...):
       """Test behavior at maximum allowed length"""
   ```

---

## Test Fixtures

### Available Fixtures (from `conftest.py`)

```python
# Application Fixtures
app                    # Flask test application (session scope)
client                 # Test client for making requests
db_session            # Clean database session per test

# User Fixtures
admin_user            # Admin user (ADMIN001)
test_user             # Regular user (USER001)
regular_user          # Alias for test_user
materials_user        # Materials department user
test_user_2           # Second test user (EMP002)

# Authentication Fixtures
auth_headers          # Admin auth headers
user_auth_headers     # Regular user auth headers
auth_headers_materials        # Materials user auth headers
auth_headers_return_manager   # Return manager auth headers
auth_headers_requests_user    # Request submitter auth headers
jwt_manager          # JWT token manager

# Domain Fixtures
test_warehouse       # Test warehouse
sample_tool          # Sample tool for testing
sample_chemical      # Sample chemical for testing
test_channel         # Test messaging channel
test_kit             # Test kit with aircraft type
sample_data          # Comprehensive sample data set

# Utility Fixtures
test_utils           # Test utility functions
```

### Using Fixtures

```python
def test_with_fixtures(self, client, admin_user, auth_headers, test_warehouse):
    """Example test using multiple fixtures"""
    # client - for making HTTP requests
    # admin_user - authenticated admin user object
    # auth_headers - headers with admin JWT token
    # test_warehouse - pre-created warehouse

    response = client.get("/api/tools", headers=auth_headers)
    assert response.status_code == 200
```

### Creating Custom Fixtures

```python
# In conftest.py or test file
@pytest.fixture
def custom_fixture(db_session, admin_user):
    """Create custom test data"""
    # Setup
    data = create_custom_data()
    yield data
    # Teardown (if needed)
    # cleanup_custom_data(data)
```

---

## Coverage Reports

### Generate Coverage Report

```bash
# HTML coverage report
pytest tests/ --cov=. --cov-report=html

# Terminal coverage report
pytest tests/ --cov=. --cov-report=term

# XML coverage report (for CI/CD)
pytest tests/ --cov=. --cov-report=xml

# Combined reports
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### View HTML Coverage Report

```bash
# Generate report
pytest tests/ --cov=. --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Thresholds

Current coverage targets:
- **Overall**: > 80%
- **Critical paths**: > 90%
- **Security code**: 100%

---

## CI/CD Integration

### GitHub Actions Workflow

Tests run automatically on:
- Every push to main branch
- Every pull request
- Manual workflow dispatch

See `.github/workflows/test.yml` for configuration.

### Local Pre-Commit

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Tests run before each commit
git commit -m "Your changes"  # Tests run automatically
```

---

## Best Practices

### 1. Test Independence

Each test should be independent and not rely on other tests:

```python
# Good - Creates its own data
def test_create_tool(self, db_session):
    tool = Tool(tool_number="TEST001", ...)
    db_session.add(tool)
    db_session.commit()
    assert tool.id is not None

# Bad - Depends on data from another test
def test_update_tool(self, db_session):
    tool = Tool.query.first()  # Assumes tool exists
    tool.description = "Updated"
```

### 2. Test One Thing

Each test should verify one specific behavior:

```python
# Good
def test_create_returns_201(self, client):
    """Test that create endpoint returns 201"""
    response = client.post("/api/tools", json=data)
    assert response.status_code == 201

def test_create_returns_tool_data(self, client):
    """Test that create endpoint returns tool data"""
    response = client.post("/api/tools", json=data)
    result = response.get_json()
    assert result["tool_number"] == data["tool_number"]

# Bad - Tests multiple things
def test_create_tool(self, client):
    response = client.post("/api/tools", json=data)
    assert response.status_code == 201
    assert "tool_number" in response.get_json()
    assert Tool.query.count() == 1
```

### 3. Meaningful Assertions

Use specific assertions that clearly indicate what failed:

```python
# Good
assert response.status_code == 201, f"Expected 201, got {response.status_code}"
assert chemical.quantity == 100.0, f"Expected 100.0, got {chemical.quantity}"

# Better - Pytest provides good error messages
assert response.status_code == 201
assert chemical.quantity == 100.0
```

### 4. Performance Test Thresholds

Always document and enforce performance thresholds:

```python
import time

def test_bulk_operation_performance(self):
    """Test bulk operation completes within threshold"""
    start = time.time()

    # Perform operation
    create_100_items()

    elapsed = time.time() - start
    assert elapsed < 5.0, f"Operation took {elapsed:.2f}s, expected < 5s"
```

### 5. Security Test Coverage

Ensure security tests cover all attack vectors:

```python
@pytest.mark.security
class TestInputValidation:
    """Test all input validation"""

    def test_sql_injection_protection(self):
        """Test SQL injection is prevented"""

    def test_xss_protection(self):
        """Test XSS is prevented"""

    def test_command_injection_protection(self):
        """Test command injection is prevented"""
```

---

## Troubleshooting

### Common Issues

#### 1. Database Lock Errors

**Problem**: SQLite database is locked during concurrent tests

**Solution**: Tests use `db_session` fixture which handles cleanup

```python
def test_example(self, db_session):  # Use db_session, not app
    # Test code here
    pass
```

#### 2. Foreign Key Constraint Failures

**Problem**: Cannot create records due to missing foreign keys

**Solution**: Use appropriate fixtures or create dependencies first

```python
def test_with_dependencies(self, db_session, test_warehouse):
    # test_warehouse is created first
    chemical = Chemical(
        warehouse_id=test_warehouse.id,  # Valid FK
        ...
    )
```

#### 3. Authentication Failures

**Problem**: 401 Unauthorized errors in tests

**Solution**: Use auth header fixtures

```python
def test_protected_endpoint(self, client, auth_headers):
    # auth_headers contains valid JWT token
    response = client.get("/api/admin/users", headers=auth_headers)
    assert response.status_code == 200
```

#### 4. Slow Tests

**Problem**: Test suite takes too long

**Solution**: Mark slow tests and exclude them during development

```python
@pytest.mark.slow
def test_large_dataset(self):
    # Slow test code
    pass

# Run fast tests only
# pytest -m "not slow"
```

#### 5. Import Errors

**Problem**: Cannot import modules

**Solution**: Ensure you're in the backend directory

```bash
cd backend
pytest tests/
```

### Debug Mode

Run tests with debugging enabled:

```bash
# Show print statements
pytest -v -s

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Show local variables on failure
pytest -l
```

---

## Quick Reference

### Common Commands

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov

# Run specific category
pytest -m performance

# Run specific file
pytest tests/test_performance.py

# Exclude slow tests
pytest -m "not slow"

# Stop on first failure
pytest -x

# Verbose output
pytest -v

# Show print statements
pytest -s

# Parallel execution
pytest -n auto
```

### Test Markers

```
performance    - Performance and benchmarking tests
security       - Security vulnerability tests
concurrency    - Concurrent operation tests
bulk           - Bulk operation tests
messaging      - Messaging system tests
files          - File operation tests
reports        - Report generation tests
calibration    - Calibration workflow tests
analytics      - Analytics tests
slow           - Tests taking > 1 second
integration    - Integration tests
unit           - Unit tests
auth           - Authentication tests
api            - API endpoint tests
models         - Database model tests
```

### Performance Thresholds

```
Bulk operations:      < 5s for 100 items
Database queries:     < 1s for 500 records
API endpoints:        < 2s for 200 items
Pagination:           < 0.5s per page
Report generation:    < 5s for 500 items
Import operations:    < 30s for 500 items
```

---

## Contributing

When adding new tests:

1. ✅ Use appropriate test markers
2. ✅ Follow AAA pattern (Arrange, Act, Assert)
3. ✅ Add docstrings describing what is tested
4. ✅ Use existing fixtures when possible
5. ✅ Ensure tests are independent
6. ✅ Test both success and failure cases
7. ✅ Add performance thresholds for performance tests
8. ✅ Update this documentation if adding new test categories

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing Documentation](https://flask.palletsprojects.com/en/latest/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Last Updated**: 2024-01-XX
**Test Suite Version**: 2.0
**Total Tests**: 500+
