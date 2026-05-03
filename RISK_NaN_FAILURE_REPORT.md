# RISK NaN FAILURE REPORT

## Visible Issue
The Regional Risk Intelligence card on the frontend rendered `NaN` for the Risk Score, `--%` for components, and empty or fallback text for the Threat Assessment and Recommended Action.

## Broken Files
1. `frontend/assets/js/location-risk.js` (Lacked defensive parsing for undefined fields).
2. `backend/app/routes/risk.py` (Lacked strict `None` safety when extracting `temperature` and `wind_speed` from the weather dictionary).

## Actual Payload Problem
During the deployment transition window, the frontend attempted to read `data.risk_score` and `data.components`, but the backend was returning the old schema (`data.score`, `data.factors`). Passing `undefined` to `Math.round()` forced a `NaN` result. Additionally, if the OpenWeather API returned a dictionary where `temp` was explicitly `None`, the backend Python code (`temp > 28.0`) crashed with a `TypeError`, returning a 500 error that aborted the DOM update entirely, leaving raw `--` placeholders on screen.

## Root Cause
1. **Schema Mismatch During Propagation**: Frontend JS hit a backend that hadn't finished propagating the new JSON schema structure.
2. **Missing Null-Safety**: `dict.get("temperature", 25.0)` fails to use the default `25.0` if the `"temperature"` key exists but is explicitly set to `None`.
3. **Fragile DOM Rendering**: The UI rendered `NaN` because it implicitly trusted the backend payload shape and numeric validity.

## Exact Fix Needed
1. Modify `location-risk.js` to support BOTH old and new payload shapes (`data.risk_score || data.score`).
2. Add strict `Number.isFinite()` checks in JS before rendering.
3. Fallback to `"Unavailable"` instead of `NaN` or leaving `--`.
4. Modify `risk.py` to cast `weather_data.get(...)` strictly to `float` and default it properly if it is `None`.
