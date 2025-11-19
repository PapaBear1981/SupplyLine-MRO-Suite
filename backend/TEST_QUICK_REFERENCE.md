# Test Quick Reference Guide

## 🚀 Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov

# Run fast tests only
pytest -m "not slow"
```

---

## 📋 Common Commands

### Basic Test Execution

```bash
# All tests with verbose output
pytest tests/ -v

# Specific test file
pytest tests/test_performance.py

# Specific test class
pytest tests/test_performance.py::TestBulkOperations

# Specific test function
pytest tests/test_performance.py::TestBulkOperations::test_bulk_chemical_creation

# Stop on first failure
pytest -x

# Stop after 3 failures
pytest --maxfail=3
```

### By Category/Marker

```bash
pytest -m performance      # Performance tests
pytest -m security         # Security tests
pytest -m concurrency      # Concurrency tests
pytest -m bulk             # Bulk import tests
pytest -m messaging        # Messaging tests
pytest -m calibration      # Calibration tests
pytest -m reports          # Report tests
pytest -m analytics        # Analytics tests
pytest -m "not slow"       # Exclude slow tests
pytest -m "security and not slow"  # Combine markers
```

### Coverage Reports

```bash
# Terminal coverage report
pytest --cov --cov-report=term

# HTML coverage report
pytest --cov --cov-report=html
# Then open: htmlcov/index.html

# XML coverage (for CI/CD)
pytest --cov --cov-report=xml

# All formats at once
pytest --cov --cov-report=html --cov-report=term --cov-report=xml
```

### Performance & Debugging

```bash
# Show 10 slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0

# Verbose with print statements
pytest -v -s

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Show local variables on failure
pytest -l

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

### Re-running Tests

```bash
# Run only failed tests from last run
pytest --lf

# Run failed first, then others
pytest --ff

# Repeat tests N times (stress testing)
pytest --count=100

# Run with timeout (10 seconds per test)
pytest --timeout=10
```

---

## 🏷️ Test Markers

| Marker | Description | Example |
|--------|-------------|---------|
| `performance` | Performance benchmarks | `pytest -m performance` |
| `security` | Security tests | `pytest -m security` |
| `concurrency` | Concurrency tests | `pytest -m concurrency` |
| `bulk` | Bulk operations | `pytest -m bulk` |
| `messaging` | Messaging system | `pytest -m messaging` |
| `files` | File operations | `pytest -m files` |
| `reports` | Report generation | `pytest -m reports` |
| `calibration` | Calibration workflows | `pytest -m calibration` |
| `analytics` | Analytics | `pytest -m analytics` |
| `slow` | Tests taking > 1s | `pytest -m "not slow"` |
| `integration` | Integration tests | `pytest -m integration` |
| `unit` | Unit tests | `pytest -m unit` |
| `auth` | Authentication | `pytest -m auth` |
| `api` | API endpoints | `pytest -m api` |
| `models` | Database models | `pytest -m models` |

---

## 📊 Test Files

| File | Focus | Tests | Marker |
|------|-------|-------|--------|
| `test_performance.py` | Performance benchmarks | 19 | `performance` |
| `test_security_extended.py` | Advanced security | 35+ | `security` |
| `test_messaging_extended.py` | Messaging system | 25+ | `messaging` |
| `test_bulk_import.py` | CSV imports | 20+ | `bulk` |
| `test_calibration_workflows.py` | Calibration | 15+ | `calibration` |
| `test_reports_analytics.py` | Reports & analytics | 20+ | `reports`, `analytics` |
| `test_concurrency_integrity.py` | Concurrency | 15+ | `concurrency` |
| `test_auth.py` | Authentication | 40+ | `auth` |
| `test_routes*.py` | API endpoints | 180+ | `api` |
| `test_models*.py` | Data models | 60+ | `models` |

---

## 🔧 Common Test Fixtures

```python
# Application
app                    # Flask test app
client                 # Test client
db_session            # Clean DB session

# Users
admin_user            # Admin (ADMIN001)
test_user             # Regular user (USER001)
materials_user        # Materials dept user

# Auth
auth_headers          # Admin headers
user_auth_headers     # User headers

# Domain
test_warehouse        # Test warehouse
sample_tool           # Sample tool
sample_chemical       # Sample chemical
test_channel          # Test channel
test_kit              # Test kit
```

---

## 📈 Performance Thresholds

```
Bulk operations:      < 5s for 100 items
Database queries:     < 1s for 500 records
API endpoints:        < 2s for 200 items
Pagination:           < 0.5s per page
Report generation:    < 5s for 500 items
Import operations:    < 30s for 500 items
```

---

## 🐛 Troubleshooting

### Database Locked
```python
# ❌ Wrong
def test(app):
    ...

# ✅ Correct
def test(db_session):
    ...
```

### Need Authentication
```python
# ❌ Wrong
def test(client):
    response = client.get("/api/admin/users")

# ✅ Correct
def test(client, auth_headers):
    response = client.get("/api/admin/users", headers=auth_headers)
```

### Missing Dependencies
```python
# ❌ Wrong
chemical = Chemical(warehouse_id=1, ...)

# ✅ Correct
def test(db_session, test_warehouse):
    chemical = Chemical(warehouse_id=test_warehouse.id, ...)
```

---

## 🔍 Finding Tests

```bash
# List all tests
pytest --collect-only

# List tests with keywords
pytest --collect-only -k "user"

# List tests in specific marker
pytest --collect-only -m performance

# Count tests
pytest --collect-only -q | wc -l
```

---

## 📝 Writing New Tests

### Template

```python
@pytest.mark.your_marker
class TestYourFeature:
    """Test your feature"""

    def test_success_case(self, client, auth_headers):
        """Test successful operation"""
        # Arrange
        data = {"field": "value"}

        # Act
        response = client.post("/api/endpoint",
                              headers=auth_headers,
                              json=data)

        # Assert
        assert response.status_code == 201

    def test_error_case(self, client, auth_headers):
        """Test error handling"""
        # Arrange
        invalid_data = {"field": None}

        # Act
        response = client.post("/api/endpoint",
                              headers=auth_headers,
                              json=invalid_data)

        # Assert
        assert response.status_code == 400
```

---

## 🎯 Test Development Workflow

```bash
# 1. Write test
vim tests/test_my_feature.py

# 2. Run just your test
pytest tests/test_my_feature.py -v

# 3. Fix until passing
pytest tests/test_my_feature.py -v

# 4. Run related tests
pytest -k "my_feature" -v

# 5. Run fast suite
pytest -m "not slow" -v

# 6. Run full suite with coverage
pytest --cov --cov-report=term
```

---

## 🚦 CI/CD Integration

### GitHub Actions
Tests run automatically on:
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### Local Pre-Commit
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Skip hooks (if needed)
git commit --no-verify
```

---

## 📦 Dependencies

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Key packages:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-xdist` - Parallel execution
- `pytest-timeout` - Timeout handling
- `pytest-mock` - Mocking support
- `pytest-benchmark` - Performance benchmarking

---

## 💡 Tips & Tricks

### Speed Up Tests
```bash
# Run in parallel (4 workers)
pytest -n 4

# Auto-detect CPU cores
pytest -n auto

# Skip coverage for faster runs
pytest tests/ --no-cov
```

### Filter by Name
```bash
# All tests with "user" in name
pytest -k "user"

# All tests with "create" or "update"
pytest -k "create or update"

# Exclude tests with "delete"
pytest -k "not delete"
```

### Custom Output
```bash
# Minimal output
pytest -q

# Only show failed tests
pytest -v --tb=short

# No output capture (see prints)
pytest -s

# JUnit XML output
pytest --junit-xml=results.xml
```

### Watch Mode (with pytest-watch)
```bash
# Install
pip install pytest-watch

# Watch for changes and auto-run tests
ptw
```

---

## 📚 Full Documentation

See [TESTING.md](./TESTING.md) for comprehensive documentation.

---

**Quick Tip**: Run `pytest -h` to see all available options!
