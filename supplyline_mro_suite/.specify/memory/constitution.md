<!--
Sync Impact Report
Version change: 1.1.0 → 1.2.0
Modified principles:
- None
Added principles:
- VI. High-Fidelity User Experience
Added sections:
- Security & Compliance Requirements
- Workflow & Quality Gates
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md
- ✅ .specify/templates/tasks-template.md
Follow-up TODOs:
- None
-->

# SupplyLine MRO Suite Constitution

## Core Principles

### I. Zero-Trust Security Enforcement
- MUST configure and load all secrets via environment variables per `SECURITY_SETUP.md` before running any service; hardcoded secrets are prohibited.
- MUST preserve rate limiting, password lifecycle rules, and token handling introduced in v4.1.0 when modifying auth, and document deviations in `SECURITY_IMPROVEMENTS.md`.
- MUST sanitize logs and user-facing errors as described in `ENHANCED_ERROR_HANDLING_IMPLEMENTATION.md`, ensuring sensitive payloads never leave controlled boundaries.

Rationale: The suite manages operational tooling data and must maintain the hardened security posture that underpins its AWS-ready deployment.

### II. Test-Orchestrated Delivery
- MUST author and gate changes with failing tests first: backend `pytest` and `flake8`, frontend `npm run lint`, and UI `npx playwright test` align to the repository guidelines.
- MUST keep tests deterministic, seeded via `backend/create_mock_data.py`, and update fixtures instead of duplicating test scaffolding.
- MUST verify security and regression coverage locally before requesting review and attach evidence when introducing new flows.

Rationale: Automated tests are the enforcement mechanism for the suite’s security and UX guarantees.

### III. Independently Shippable Stories
- MUST define specs and plans so each user story delivers standalone value, as enforced by the `/speckit.plan` and `/speckit.tasks` workflows.
- MUST structure tasks so story-aligned work can be developed, tested, and deployed without hidden dependencies.
- MUST stop after each story to validate acceptance criteria and update documentation under `specs/` before starting the next increment.

Rationale: Independent increments keep releases reviewable and reduce cross-team blocking in the MRO environment.

### IV. Observable and Auditable Operations
- MUST instrument backend and frontend updates with structured logging and error handling consistent with `ENHANCED_ERROR_HANDLING_IMPLEMENTATION.md`.
- MUST ensure deployment artifacts (`docker-compose.yml`, `start_dev_servers.sh`) reflect new telemetry endpoints or configuration flags.
- MUST record operational changes in `docs/` or `RELEASE_NOTES.md` so field teams can trace behavior.

Rationale: The platform supports regulated operations and must remain diagnosable in production and staging.

### V. Coordinated Change Propagation
- MUST propagate API, schema, or configuration changes across `backend/`, `frontend/`, `migrations/`, and automation scripts in lockstep.
- MUST update supporting guides (`README.md`, `DEPLOYMENT.md`, `SECURITY_SETUP.md`) and version markers when behavior changes.
- MUST track cross-service versioning via `CHANGELOG.md`, `VERSION.md`, and `RELEASE_NOTES.md`, aligning release notes with actual code.

Rationale: Ensuring every surface reflects the same contract prevents integration drift and field outages.

### VI. High-Fidelity User Experience
- MUST adhere to a maximum First Contentful Paint (FCP) of 1.5 seconds and Time to Interactive (TTI) of 3.0 seconds for all primary application routes.
- MUST ensure all user interactions (clicks, form submissions) provide immediate visual feedback to prevent perceived latency.
- MUST use the established React component library and design tokens defined in `frontend/src/styles/` to maintain visual consistency across the suite.

Rationale: The MRO Suite is a mission-critical tool; performance and predictable UX are essential for operational efficiency.

## Security & Compliance Requirements

- Environment setup MUST follow `SECURITY_SETUP.md`; changes that introduce new secrets MUST document defaults in `backend/config.py` and update deployment manifests, including `docker-compose.yml` and cloud task definitions referenced in `DEPLOYMENT.md`.
- Database schema adjustments MUST run through `migrations/` with up-to-date artefacts in `database/` and scripts under `scripts/`; ad-hoc SQL in production is forbidden.
- Any feature handling personally identifiable maintenance data MUST confirm logging redaction and review `SECURITY_AUDIT_REPORT.md` implications before merge.
- AWS-facing automation under `scripts/` and `aws/` directories MUST be reviewed for least privilege and align with `SECURITY_IMPROVEMENTS.md`.

## Workflow & Quality Gates

- `/speckit.plan` outputs MUST satisfy the Constitution Check by confirming security impact, test plan, and change propagation before implementation begins.
- Research and specs MUST document independent user stories, acceptance criteria, and measurable success metrics per `.specify/templates/spec-template.md`.
- Before opening a PR, contributors MUST run `pytest`, `flake8`, `npm run lint`, `npm run build`, and `npx playwright test`; implementation is not complete until every test passes and the outcomes are recorded in the PR checklist or summary.
- Release preparation MUST update `CHANGELOG.md`, `RELEASE_NOTES.md`, and any affected `docs/` quickstarts in the same change set.

## Governance

- This constitution supersedes conflicting process guides; reviewers MUST flag violations before merge.
- Amendments require approval from backend, frontend, and security leads, documented in `CHANGELOG.md`, with accompanying template updates committed together.
- Versioning follows semantic rules: MAJOR for rewritten principles or removals, MINOR for new enforceable sections, PATCH for clarifications.
- Compliance reviews occur quarterly; release managers MUST confirm `SECURITY_AUDIT_REPORT.md` and operational guides remain accurate prior to tagging a release.

**Version**: 1.2.0 | **Ratified**: 2025-10-12 | **Last Amended**: 2025-10-15
