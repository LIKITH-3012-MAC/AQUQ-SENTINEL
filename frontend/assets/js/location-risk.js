document.getElementById('searchForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const lat = parseFloat(document.getElementById('lat').value);
  const lon = parseFloat(document.getElementById('lon').value);
  const date = new Date().toISOString().split('T')[0];

  document.getElementById('loading').style.display = 'block';
  document.getElementById('results').style.display = 'none';

  try {
    // 1. Fetch NASA/Wave Data
    const nasaRes = await API.get(`/api/nasa/ocean-summary?lat=${lat}&lon=${lon}&date=${date}`);
    const waveRes = await API.get(`/api/waves/conditions?lat=${lat}&lon=${lon}&date=${date}`);
    
    const nasaData = await nasaRes.json();
    const waveData = await waveRes.json();

    // 2. Evaluate Risk
    const riskRes = await API.post('/api/risk/evaluate', {
      latitude: lat,
      longitude: lon,
      debris_density_score: 45, // Mock initial debris
      chlorophyll_value: nasaData.chlorophyll_value,
      algae_indicator: nasaData.algae_indicator,
      wave_height_m: waveData.wave_height_m,
      wave_direction_deg: waveData.wave_direction_deg,
      sensitive_zone_distance_km: 15.0,
      ecosystem_degradation_score: 30
    });

    const riskData = await riskRes.json();

    // 3. Display Results
    document.getElementById('chlValue').textContent = nasaData.chlorophyll_value;
    document.getElementById('waveHeight').textContent = waveData.wave_height_m;
    
    const badge = document.getElementById('riskBadge');
    badge.textContent = riskData.risk_level;
    badge.className = `badge badge-${riskData.risk_level.toLowerCase()}`;
    
    const progress = document.getElementById('riskProgress');
    progress.style.width = `${riskData.risk_score}%`;
    if (riskData.risk_level === 'CRITICAL') progress.style.backgroundColor = 'var(--risk-critical)';
    else if (riskData.risk_level === 'HIGH') progress.style.backgroundColor = 'var(--risk-high)';
    else if (riskData.risk_level === 'MEDIUM') progress.style.backgroundColor = 'var(--risk-medium)';
    else progress.style.backgroundColor = 'var(--risk-low)';

    document.getElementById('recommendation').textContent = riskData.recommendation;
    
    const reasonsList = document.getElementById('reasons');
    reasonsList.innerHTML = JSON.parse(riskData.reasons_json).map(r => `<li>${r}</li>`).join('');

    document.getElementById('loading').style.display = 'none';
    document.getElementById('results').style.display = 'grid';

  } catch (err) {
    console.error(err);
    alert('Failed to analyze location. Please try again.');
    document.getElementById('loading').style.display = 'none';
  }
});
