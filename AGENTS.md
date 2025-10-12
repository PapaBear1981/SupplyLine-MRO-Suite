# Repository Guidelines

## Project Structure & Module Organization
- `backend/` contains the Flask API, SQLAlchemy models, migrations, and reusable fixtures under `backend/tests/`.
- `frontend/` is a Vite-powered React 19 app with Playwright suites in `frontend/tests/e2e/`.
- `database/` stores local SQLite state; `migrations/` and `scripts/` supply schema upgrades and automation.
- `docs/` and the `SECURITY_*.md` set capture architecture and compliance decisions—consult them before touching auth or deployment flows.
- Root utilities (`docker-compose.yml`, `start_dev_servers.sh`) keep services in sync; update them alongside runtime changes.

## Build, Test, and Development Commands
- Backend: `python -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt` prepares dependencies; start with `python backend/run.py`.
- Frontend: run `npm install` then `npm run dev` inside `frontend/` for the Vite dev server; `npm run build` produces optimized assets.
- Full stack: `./start_dev_servers.sh` (or the PowerShell variant) opens both services; `docker-compose up --build` mirrors production container settings.

## Coding Style & Naming Conventions
- Python modules follow PEP 8 with 4-space indentation; keep files snake_case and favor explicit imports over wildcards.
- React components use PascalCase filenames, hooks and utilities stay camelCase, and 2-space indentation is enforced via `npm run lint`.
- Re-run `eslint` and `pytest` before opening a PR to catch formatting or type issues introduced by new APIs.

## Testing Guidelines
- Execute `pytest` from `backend/`; respect the existing markers (`unit`, `integration`, `auth`, etc.) defined in `backend/pytest.ini` to scope runs (`pytest -m "not slow"`).
- Seed data helpers in `backend/create_mock_data.py` and fixtures in `backend/tests` should be reused rather than duplicated.
- UI smoke tests live in Playwright suites; run `npx playwright test` (from `frontend/`) before shipping UX or routing changes and attach the HTML report when relevant.

## Commit & Pull Request Guidelines
- Follow the existing Git history: imperative, sentence-case subjects (e.g., `Fix admin dashboard loading issue`) with optional hyphenated detail.
- Keep commits scoped and security-conscious; reference any related `SECURITY_*` doc updates when secrets, auth, or rate limiting change.
- Pull requests should summarize motivation, list the commands/tests executed, link tickets, and include screenshots or API samples for user-facing updates.

## Security & Configuration Tips
- Never hardcode sensitive values; load secrets through environment variables defined in `SECURITY_SETUP.md` and `DEPLOYMENT.md`.
- When adding new configuration keys, document defaults in `backend/config.py` and update deployment artifacts (`docker-compose.yml`, ECS task defs) together.
- Logs default to sanitized payloads—double-check new handlers and ensure personally identifiable information stays redacted.
