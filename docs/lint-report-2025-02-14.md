# Lint Report — 2025-02-14

## Backend (`flake8`)
- Command: `flake8 .`
- Status: **Failed** — thousands of violations recorded.
- Key patterns observed:
  - Extensive `E501` (line too long) hits across migrations, routes, tests, and utilities.
  - Numerous whitespace issues (`W293`, `W391`, `W291`) in helper scripts such as `add_lot_lineage_fields.py`.
  - A handful of logic findings including unused variables (`F841`) in `tests/test_authorization.py` and `verify_e2e_endpoints.py`.
- Full output captured in [`backend-flake8-report.txt`](./backend-flake8-report.txt).

## Frontend (`eslint`)
- Command: `npm run lint` (a subsequent `npx eslint .` stored the output).
- Status: **Failed** — 8 errors and 15 warnings.
- Notable issues:
  - `no-unused-vars` violations in `DatabaseManagement.jsx`, `TransferBarcodeModal.jsx`, and multiple Playwright specs.
  - React hook dependency warnings (`react-hooks/exhaustive-deps`) across several components.
  - Fast refresh export warnings from files that mix components with utility exports.
- Full output captured in [`frontend-eslint-report.txt`](./frontend-eslint-report.txt).

## Tooling Notes
- `npm` emitted `Unknown env config "http-proxy"` warnings during install and lint runs.
- `npm install` reported 2 vulnerabilities (1 moderate, 1 high) in the audited dependency tree.
- Attempting to use the deprecated core `unix` formatter (`npx eslint . -f unix`) failed; it now requires installing `eslint-formatter-unix` explicitly.
