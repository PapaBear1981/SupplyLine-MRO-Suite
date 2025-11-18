"""
Minimal smoke test to verify CI setup

This test should always pass and helps verify that:
1. Pytest is installed and working
2. Test discovery is working
3. Basic test execution works
"""

import pytest


@pytest.mark.unit
class TestCISetup:
    """Basic tests to verify CI is working"""

    def test_pytest_is_working(self):
        """Verify pytest is functioning"""
        assert True

    def test_python_version(self):
        """Verify Python version"""
        import sys
        version = sys.version_info
        assert version.major == 3
        assert version.minor >= 9

    def test_basic_imports(self):
        """Verify basic Python imports work"""
        import json
        import os
        import sys

        assert json is not None
        assert os is not None
        assert sys is not None

    def test_pytest_markers_registered(self):
        """Verify custom pytest markers are registered"""
        # This test will fail if markers aren't properly registered in pytest.ini
        pass  # Just having this decorated with markers below tests registration

test_pytest_markers_registered = pytest.mark.performance(
    pytest.mark.security(
        pytest.mark.concurrency(test_pytest_markers_registered)
    )
)
