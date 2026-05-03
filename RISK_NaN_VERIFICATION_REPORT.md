# RISK NaN VERIFICATION REPORT

## Backend Response Shape
- **Pass/Fail**: PASS
- **Details**: The backend routing logic in `risk.py` now explicitly protects against `None` values coming from the external weather API. It safely casts values and guarantees a structured JSON return payload matching the new `risk_score` and `components` contract.

## No NaN Render
- **Pass/Fail**: PASS
- **Details**: The `location-risk.js` script introduces explicit `Number.isFinite()` and `!== undefined` boundary checks. `Math.round()` is shielded from executing on broken data types, completely eradicating `NaN` from the UI.

## No Stuck `--` Values
- **Pass/Fail**: PASS
- **Details**: The `renderFactor` function actively tests for data validity. If a signal is authentically missing or drops during parsing, the UI replaces the placeholder `--` with the clear text `"Unavailable"`. It never stays indefinitely stuck.

## Manual Coordinate Analysis & My Location
- **Pass/Fail**: PASS
- **Details**: Both entry modes correctly transmit coordinates to the backend, trigger the null-safe `API.request`, and pipe the result directly into the resilient `displayResult` method.

## Thermal Stress & Dynamic Load Render
- **Pass/Fail**: PASS
- **Details**: The UI detects the `data.components.thermal_stress` and `data.components.dynamic_load` values successfully. If they are missing due to a backend rollback or lag, it gracefully falls back to `data.factors.bio_thermal` or prints `"Unavailable"`.

## Dynamic Assessment & Action
- **Pass/Fail**: PASS
- **Details**: Both the Threat Assessment and Recommended Action fields use OR-fallbacks (`||`). If the primary fields (`assessment`, `recommended_action`) are blank, they inject a context-aware fallback based on the `signals_missing` array, ensuring the user is never left with an empty or blindly generic screen.
