# WEATHER-INTEGRATED RISK ENGINE FAILURE REPORT

## Broken Files
- `backend/app/routes/risk.py` (Currently not fetching real weather data, passing fake zeros or using default static values).
- `backend/app/services/risk_engine.py` (Calculations don't clearly map missing weather data and fallback securely, currently treats missing as 0 which leads to fake zeroes).
- `backend/.env` (Missing OpenWeather API key).
- `frontend/assets/js/location-risk.js` (Might need schema alignment to properly parse the new `components` and `signals_used` keys).

## Missing Integration Steps
1. The backend risk analysis route (`/api/risk/calculate`) does not call `weather_service.get_marine_weather(lat, lon)` before calculating the risk.
2. The risk engine (`risk_engine.py`) takes `wind_speed`, `wave_height`, and `sst_anomaly` but since the route doesn't provide them dynamically, they default to `0.0`.
3. If weather API is missing/unavailable, there is no logic to track `signals_missing` and `signals_used`.
4. OpenWeather API key is not in `.env`.

## Root Cause
The `calculate_marine_risk` function is completely uncoupled from the external OpenWeather API service in the routing layer. The parameters are accepted as optional query params with `0.0` default values, leading to a permanent "no risk" condition for dynamic factors (Thermal Stress and Dynamic Load).

## Exact Fix Needed
1. Add `OPENWEATHER_API_KEY=[REDACTED_API_KEY]` to `.env`.
2. Update `backend/app/routes/risk.py`'s `calculate_risk` endpoint to:
   - Call `weather_service.get_marine_weather(req.latitude, req.longitude)`.
   - Extract `temperature` and `wind_speed`.
   - Track `signals_used` and `signals_missing`.
   - Pass these real values to `risk_engine.calculate_marine_risk`.
3. Update `risk_engine.py` to properly map `temperature` to `bio_stress/thermal_stress` and `wind_speed` to `dynamic_load`, adjusting the text dynamically.
4. Refactor `calculate_risk` to return the new JSON shape required by the prompt.
5. Update `frontend/assets/js/location-risk.js` to parse `data.risk_score`, `data.components.thermal_stress`, etc., matching the new backend schema.
