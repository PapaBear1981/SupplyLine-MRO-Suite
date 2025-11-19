# Makefile for SupplyLine MRO Suite Backend
# Convenience commands for development and testing

.PHONY: help install test test-fast test-slow test-security test-performance test-coverage clean lint format check

help: ## Show this help message
	@echo "SupplyLine MRO Suite - Backend Test Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies including test dependencies
	pip install -r requirements.txt
	pip install -r requirements-test.txt

install-dev: ## Install development dependencies
	pip install -r requirements-test.txt
	pre-commit install

test: ## Run all tests
	pytest tests/ -v

test-fast: ## Run fast tests only (exclude slow tests)
	pytest tests/ -m "not slow" -v

test-slow: ## Run slow tests only
	pytest tests/ -m slow -v

test-security: ## Run security tests only
	pytest tests/ -m security -v

test-performance: ## Run performance tests with timing info
	pytest tests/ -m performance -v --durations=10

test-concurrency: ## Run concurrency tests
	pytest tests/ -m concurrency -v

test-bulk: ## Run bulk import tests
	pytest tests/ -m bulk -v

test-messaging: ## Run messaging tests
	pytest tests/ -m messaging -v

test-calibration: ## Run calibration tests
	pytest tests/ -m calibration -v

test-reports: ## Run reports and analytics tests
	pytest tests/ -m "reports or analytics" -v

test-api: ## Run API endpoint tests
	pytest tests/ -m api -v

test-models: ## Run model tests
	pytest tests/ -m models -v

test-auth: ## Run authentication tests
	pytest tests/ -m auth -v

test-coverage: ## Run all tests with coverage report
	pytest tests/ --cov=. --cov-report=html --cov-report=term
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

test-coverage-xml: ## Generate XML coverage report for CI/CD
	pytest tests/ --cov=. --cov-report=xml --cov-report=term

test-parallel: ## Run tests in parallel (requires pytest-xdist)
	pytest tests/ -n auto -v

test-failed: ## Re-run only failed tests from last run
	pytest tests/ --lf -v

test-debug: ## Run tests with debugging enabled
	pytest tests/ -v -s --pdb

test-one: ## Run a specific test file (usage: make test-one FILE=test_performance.py)
	pytest tests/$(FILE) -v

test-watch: ## Watch for changes and auto-run tests (requires pytest-watch)
	ptw

lint: ## Run code linting
	flake8 tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 tests/ --count --max-complexity=10 --max-line-length=120 --statistics

format: ## Format code with Black and isort
	black tests/
	isort tests/

check: ## Run format and lint checks
	black --check tests/
	isort --check tests/
	flake8 tests/ --max-line-length=120

security-scan: ## Run security scans
	bandit -r . -ll --exclude tests,venv,env,.venv
	safety check

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage.json
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

report: ## Generate and open coverage report
	pytest tests/ --cov=. --cov-report=html
	@echo "Opening coverage report..."
	@python -m webbrowser htmlcov/index.html || open htmlcov/index.html || xdg-open htmlcov/index.html

ci-test: ## Run tests as they would run in CI
	pytest tests/ -m "not slow" --cov=. --cov-report=xml --cov-report=term

benchmark: ## Run performance benchmarks
	pytest tests/ -m performance --durations=20 -v

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

setup: install-dev ## Complete development setup
	@echo "✓ Development environment setup complete!"
	@echo ""
	@echo "Run 'make test' to verify everything works."

stats: ## Show test statistics
	@echo "Test Statistics:"
	@echo "================"
	@echo -n "Total test files: "
	@find tests -name "test_*.py" | wc -l
	@echo -n "Total test functions: "
	@grep -r "def test_" tests/ | wc -l
	@echo -n "Total test classes: "
	@grep -r "^class Test" tests/ | wc -l
	@echo ""
	@echo "Test Markers:"
	@echo "============="
	@pytest --markers | grep "^@pytest.mark" || echo "No custom markers found"

.DEFAULT_GOAL := help
