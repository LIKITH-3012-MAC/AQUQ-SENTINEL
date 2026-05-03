/**
 * AquaSentinel AI - Risk Engine Interaction Controller
 */

const RiskEngine = {
    async useMyLocation() {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your neural interface.");
            return;
        }

        document.getElementById('risk-loader').style.display = 'block';
        document.getElementById('risk-result').style.display = 'none';

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;
                document.getElementById('location-search').value = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
                await this.analyze(latitude, longitude);
            },
            (error) => {
                document.getElementById('risk-loader').style.display = 'none';
                alert("Location access denied. Please enter coordinates manually.");
            }
        );
    },

    async analyze(manualLat = null, manualLon = null) {
        let lat, lon;

        if (manualLat !== null) {
            lat = manualLat;
            lon = manualLon;
        } else {
            const input = document.getElementById('location-search').value;
            if (!input) {
                alert("Please enter target coordinates.");
                return;
            }
            
            const parts = input.split(',').map(p => p.trim());
            if (parts.length !== 2 || isNaN(parts[0]) || isNaN(parts[1])) {
                alert("Format error. Please use: latitude, longitude");
                return;
            }
            lat = parseFloat(parts[0]);
            lon = parseFloat(parts[1]);
        }

        document.getElementById('risk-loader').style.display = 'block';
        document.getElementById('risk-result').style.display = 'none';

        try {
            const response = await API.request('/risk/calculate', 'POST', {
                latitude: lat,
                longitude: lon
            });

            this.displayResult(response);
        } catch (err) {
            console.error("Risk Analysis Failure:", err);
            alert("Neural link failed: " + err.message);
        } finally {
            document.getElementById('risk-loader').style.display = 'none';
        }
    },

    displayResult(data) {
        const resultDiv = document.getElementById('risk-result');
        const scoreVal = document.getElementById('risk-score-value');
        const levelTag = document.getElementById('risk-level-tag');
        const explanation = document.getElementById('risk-explanation');
        const action = document.getElementById('risk-action');

        // Safely parse risk score (supports both old 'score' and new 'risk_score' formats during deployment)
        const rawScore = data.risk_score !== undefined ? data.risk_score : data.score;
        if (rawScore !== undefined && rawScore !== null && Number.isFinite(Number(rawScore))) {
            scoreVal.textContent = Math.round(Number(rawScore));
        } else {
            scoreVal.textContent = "N/A";
        }

        // Safely parse risk level
        const level = data.risk_level || data.level || 'UNKNOWN';
        levelTag.textContent = level;
        levelTag.className = 'status-tag ' + (level === 'CRITICAL' || level === 'HIGH' ? 'critical' : 'success');

        // Safely parse explanations
        explanation.textContent = data.assessment || data.explanation || (data.signals_missing && data.signals_missing.length > 0 ? "Limited local intelligence available; only baseline risk could be computed." : "Assessment data unavailable.");
        action.textContent = data.recommended_action || "Continue routine monitoring. Refer to local authorities for immediate guidance.";

        // Safely parse components
        const components = data.components || {};
        const oldFactors = data.factors || {}; // Fallback for transition phase
        
        const renderFactor = (elementId, value) => {
            const el = document.getElementById(elementId);
            if (value !== undefined && value !== null && Number.isFinite(Number(value))) {
                el.textContent = Number(value).toFixed(1) + '%';
            } else {
                el.textContent = "Unavailable";
            }
        };

        renderFactor('factor-debris', components.debris_density !== undefined ? components.debris_density : oldFactors.debris);
        renderFactor('factor-thermal', components.thermal_stress !== undefined ? components.thermal_stress : oldFactors.bio_thermal);
        renderFactor('factor-bio', components.bio_stress !== undefined ? components.bio_stress : oldFactors.community_reports);
        renderFactor('factor-dynamic', components.dynamic_load !== undefined ? components.dynamic_load : oldFactors.dynamic_conditions);

        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }
};
