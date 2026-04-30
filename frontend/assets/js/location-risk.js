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

        scoreVal.textContent = Math.round(data.score);
        levelTag.textContent = data.level;
        levelTag.className = 'status-tag ' + (data.level === 'CRITICAL' || data.level === 'HIGH' ? 'critical' : 'success');
        explanation.textContent = data.explanation;
        action.textContent = data.recommended_action;

        // Factors
        if (data.factors) {
            document.getElementById('factor-debris').textContent = (data.factors.debris || 0).toFixed(1) + '%';
            document.getElementById('factor-thermal').textContent = (data.factors.bio_thermal || 0).toFixed(1) + '%';
            document.getElementById('factor-bio').textContent = (data.factors.community_reports || 0).toFixed(1) + '%';
            document.getElementById('factor-dynamic').textContent = (data.factors.dynamic_conditions || 0).toFixed(1) + '%';
        }

        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }
};
