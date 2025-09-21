# Bug: Add Tool endpoint rejects JWT-authenticated admins (403 Forbidden)

## Summary
Submitting the **Add New Tool** form as an authenticated admin user fails with a 403 Forbidden response. The backend endpoint for creating tools only trusts Flask session flags (e.g., `session['is_admin']`) instead of the administrator claims embedded in the JWT that the React frontend uses.

## Steps to Reproduce
1. Sign in to the web app as an administrator (e.g., `ADMIN001`).
2. Navigate to **Tools → Add New Tool**.
3. Fill in all required fields with valid data.
4. Submit the form.

## Expected Result
The tool should be created successfully and appear in the tool inventory list.

## Actual Result
The UI displays a red banner stating the tool creation failed, and the network response is HTTP 403 Forbidden because the backend rejects the request when the Flask session is missing the `is_admin` flag.

## Impact
Administrators cannot add new tools through the UI even though they are authenticated, blocking a core workflow without manual database intervention.

## Notes
* Screenshot: [Add Tool failure](browser:/invocations/noqxenji/artifacts/artifacts/tool_created_success.png)
* Related observation: the existing tool list works if a tool is seeded directly in the database.
