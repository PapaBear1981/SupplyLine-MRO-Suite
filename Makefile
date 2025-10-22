PYTHON ?= python3
PIP ?= pip
K6 ?= k6

.PHONY: lint unit property contract security e2e k6-smoke k6-stress k6-soak mutate cov db-migrate db-restore install

install:
	$(PIP) install -r requirements-dev.txt

lint:
	flake8 src tests

unit:
	pytest -m unit

property:
	pytest -m property

contract:
	pytest -m contract

security:
	bandit -r src -c .bandit
	pip-audit -r requirements-dev.txt --severity-level high
	command -v gitleaks >/dev/null 2>&1 || { echo 'gitleaks not installed; see README for setup'; exit 1; }
	gitleaks detect --no-git -c .gitleaks.toml

e2e:
	pytest tests/e2e --maxfail=1

k6-smoke:
	K6_DRY_RUN=1 $(K6) run qa/k6/checkin_smoke.js

k6-stress:
	K6_DRY_RUN=1 $(K6) run qa/k6/checkin_stress.js

k6-soak:
	K6_DRY_RUN=1 $(K6) run qa/k6/checkin_soak.js

mutate:
	mutmut run
	python - <<'PY'
import re
import subprocess

output = subprocess.check_output(['mutmut', 'results']).decode()
match_survived = re.search(r'(\d+) mutants survived', output)
match_killed = re.search(r'(\d+) mutants killed', output)
match_total = re.search(r'(\d+) total', output)
survived = int(match_survived.group(1)) if match_survived else 0
killed = int(match_killed.group(1)) if match_killed else 0
if match_total:
    total = int(match_total.group(1))
else:
    total = killed + survived
score = 0.0 if total == 0 else (killed / total) * 100
print(f"Mutation score: {score:.2f}% (killed={killed}, survived={survived}, total={total})")
if score < 60:
    raise SystemExit('Mutation score below threshold (60%)')
PY

cov:
	pytest --cov
	coverage json
	python - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path('coverage.json').read_text())
line = summary['totals']['percent_covered']
branch = summary['totals'].get('branch_coverage', 0)
print(f"Line coverage: {line:.2f}%")
print(f"Branch coverage: {branch:.2f}%")
if line < 85:
    raise SystemExit('Line coverage below 85% threshold')
if branch < 70:
    raise SystemExit('Branch coverage below 70% threshold')
PY

db-migrate:
	pytest tests/db/test_migrations.py

db-restore:
	pytest tests/db/test_backup_restore.py
