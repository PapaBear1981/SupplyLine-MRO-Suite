# Research Findings: Dependency and Infrastructure Hardening Sprint

## 1. Python Dependency Pinning Strategy

**Decision**: Implement dependency pinning using `pip-tools` to generate a fully resolved `requirements.txt` from a top-level `requirements.in`.

**Rationale**:
The current `backend/requirements.txt` only lists top-level dependencies, leading to non-reproducible builds and potential security drift in transitive dependencies. `pip-tools` enforces explicit pinning of all dependencies, improving build stability and security auditability (FR 4.2.1).

**Approach**:
1. Rename `backend/requirements.txt` to `backend/requirements.in`.
2. Install `pip-tools`.
3. Run `pip-compile backend/requirements.in` to generate the pinned `backend/requirements.txt`.
4. Install dependencies from the new `requirements.txt`.

## 2. Secure Configuration for Flask (Bandit B201 & B104)

**Decision**: Use environment variables and configuration classes to enforce secure defaults for debug mode and host binding.

**Rationale**:
Bandit findings B201 (debug=True) and B104 (0.0.0.0 bind) are critical security risks in production. The application must default to secure settings unless explicitly overridden for development.

**Approach**:
1. **B201 (Debug Mode)**: Ensure `app.config['DEBUG']` is set to `False` by default in `backend/config.py` and only enabled if a specific environment variable (e.g., `FLASK_ENV=development`) is present.
2. **B104 (Host Binding)**: Restrict the default host binding in `backend/app.py` or `backend/run.py` to `127.0.0.1` or the specific internal Docker network interface, only using `0.0.0.0` when explicitly required by the container orchestration (and only if network segmentation is in place).

## 3. Infrastructure Network Segmentation (FR 4.5.1)

**Decision**: Define a custom bridge network in `docker-compose.yml` and explicitly assign the `backend` and `frontend` services to it.

**Rationale**:
This isolates the application services from the default Docker bridge network, reducing the attack surface and aligning with the principle of least privilege (CIS Docker 4.3).

**Approach**:
1. Add a `networks` section to `docker-compose.yml` defining a custom network (e.g., `supplyline_net`).
2. Assign `backend` and `frontend` services to use `supplyline_net`.
3. Update service configurations to communicate using service names within this network.