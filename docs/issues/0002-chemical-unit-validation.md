# Bug: Chemical creation rejects valid unit selections

## Summary
Creating a new chemical fails for several units. Selecting "Liter (l)" in the **Add New Chemical** form produces an HTTP 400 error. The UI submits the abbreviated unit value (`l`), but the backend validation schema only accepts the long-form string (`liter`).

## Steps to Reproduce
1. Sign in to the application as an administrator.
2. Navigate to **Chemicals → Add New Chemical**.
3. Fill in all required fields with valid data.
4. Choose **Liter (l)** from the unit dropdown.
5. Submit the form.

## Expected Result
The chemical should be created successfully using the unit selected in the UI.

## Actual Result
The request returns HTTP 400 with a validation error stating the unit must be one of the accepted values. The backend accepts `liter`, while the frontend sends `l`.

## Impact
Administrators cannot add chemicals that use affected units (e.g., liters), blocking inventory entry for those measurements.

## Notes
* Screenshot: [Chemical creation error](browser:/invocations/ksdyxyxk/artifacts/artifacts/chemical_create_result.png)
* This mismatch likely affects additional units where the abbreviation differs from the long-form value the backend expects.
