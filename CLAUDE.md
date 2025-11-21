# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SupplyLine MRO Suite is a full-stack MRO (Maintenance, Repair, and Operations) management system with:
- **Backend:** Flask 3.1 + SQLAlchemy ORM (Python 3.12)
- **Frontend:** React 19 + Redux Toolkit + Vite
- **Database:** SQLite (default) or PostgreSQL
- **Auth:** JWT tokens (Flask-JWT-Extended)
- **Real-time:** Flask-SocketIO for WebSockets

## Common Commands

### Backend (from `/backend`)
```bash
# Development server
python app.py                              # Starts on localhost:5000

# Testing
python -m pytest tests/ -v                 # Run all tests
python -m pytest tests/test_auth.py -v     # Single test file
python -m pytest tests/test_auth.py::test_login -v  # Single test

# Linting
ruff check .                               # Check code
ruff check . --fix                         # Auto-fix issues
pyright                                    # Type checking
```

### Frontend (from `/frontend`)
```bash
# Development
npm run dev                                # Starts on localhost:5173 (proxies /api to :5000)

# Testing
npm run test:run                           # Unit tests (Vitest)
npm run test:e2e                           # E2E tests (Playwright)
npm run test:e2e:headed                    # E2E with visible browser

# Build & Lint
npm run build                              # Production build
npm run lint                               # ESLint check
```

### Docker (from root)
```bash
docker-compose up -d                       # Start both services
docker-compose up -d --build               # Rebuild after changes
docker-compose down -v                     # Stop and remove volumes
```

## Architecture

### Backend Structure
- **`app.py`** - Flask app factory with `create_app()`
- **`models.py`** - SQLAlchemy models (User, Tool, Chemical, etc.)
- **`routes_*.py`** - Feature-specific API routes (28 route modules)
- **`auth.py`** - JWT token utilities
- **`conftest.py`** - Pytest fixtures (app, client, test models)

Routes follow REST pattern: `routes_auth.py`, `routes_tools.py`, `routes_chemicals.py`, `routes_kits.py`, etc.

### Frontend Structure
- **`src/components/`** - React components organized by feature
- **`src/store/`** - Redux Toolkit slices (authSlice, toolsSlice, chemicalsSlice, etc.)
- **`src/services/`** - Axios-based API service layer
- **`src/pages/`** - Page-level components

Pattern: Components → Redux thunks → Services → Backend API

### Authentication Flow
1. Login returns access + refresh tokens
2. Access token sent in Authorization header
3. Protected routes use `@jwt_required()` decorator
4. Refresh token endpoint for token renewal

## Testing

### Backend (Pytest)
- **Location:** `backend/tests/`
- **Markers:** `@pytest.mark.auth`, `@pytest.mark.slow`, `@pytest.mark.integration`
- **Fixtures:** `app`, `client`, various model fixtures in `conftest.py`

### Frontend
- **Unit tests:** `frontend/src/tests/` (Vitest + Testing Library)
- **E2E tests:** `frontend/tests/e2e/` (Playwright)
- **Global setup:** `tests/e2e/global-setup.js`

## Code Quality

### Backend
- **Linter:** Ruff (configured in `pyproject.toml`)
- **Type Checker:** Pyright (configured in `pyrightconfig.json`)
- **Line Length:** 127 characters
- **Python Target:** 3.12

### Frontend
- **Linter:** ESLint 9 with flat config (`eslint.config.js`)
- **React Hooks:** Enforced via eslint-plugin-react-hooks
- **Disabled:** `no-useless-catch` (intentional pattern in services)

## Key Patterns

### API Endpoints
All backend routes prefixed with `/api/`:
- `/api/auth/login`, `/api/auth/logout`, `/api/auth/refresh`
- `/api/tools/`, `/api/chemicals/`, `/api/kits/`, `/api/users/`

### State Management
Redux slices with async thunks for API calls. Components use `useSelector`/`useDispatch`.

### Database Models
SQLAlchemy ORM with relationships. Key models: User, Tool, Chemical, Kit, Checkout, Issuance.

### Environment Variables
- `FLASK_ENV`, `FLASK_DEBUG` - Flask environment
- `SECRET_KEY`, `JWT_SECRET_KEY` - Security keys
- `VITE_API_URL` - Frontend API base URL
- `PUBLIC_URL` - QR code base URL for external devices

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to master:
1. Backend: Ruff linting
2. Backend: Pyright type checking
3. Frontend: ESLint validation
4. Docker: Hadolint on Dockerfiles

## Default Test Credentials

- Admin: `ADMIN001` / `admin123`
- Materials: `MAT001` / `materials123`
- Maintenance: `MAINT001` / `maintenance123`

## PR Testing Workflow

When pulling a PR for testing, always follow these steps:
1. Checkout the PR: `gh pr checkout <PR_NUMBER>`
2. Review the changes: `gh pr diff <PR_NUMBER>`
3. Rebuild Docker containers: `docker-compose up -d --build`
4. **Run any database migrations** in `backend/migrations/`:
   ```bash
   docker exec supplyline-mro-backend python migrations/<migration_file>.py
   ```
5. Verify containers are healthy: `docker-compose ps`

**Important:** Always check for new migration files in the PR and run them to ensure the database schema is up to date. Migrations are idempotent and safe to run multiple times.

**Important:** When adding new features, keep in mind that the application is FORBIDDEN from including any kind of cost information.  Never include a cost field of any kind. 