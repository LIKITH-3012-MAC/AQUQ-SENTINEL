document.addEventListener('DOMContentLoaded', async () => {
  // Check Admin Role
  AUTH.checkAdmin();

  // Load Overview Metrics
  const loadMetrics = async () => {
    const response = await API.get('/api/admin/overview');
    if (response.ok) {
      const data = await response.json();
      document.getElementById('totalUsers').textContent = data.total_users;
      document.getElementById('totalAssessments').textContent = data.total_assessments;
      document.getElementById('criticalAlerts').textContent = data.critical_alerts;
      document.getElementById('apiHealth').textContent = data.api_health;
    }
  };

  // Load Recent Predictions
  const loadPredictions = async () => {
    const response = await API.get('/api/alerts'); // For demo, use alerts queue
    if (response.ok) {
      const alerts = await response.json();
      const body = document.getElementById('predictionsTableBody');
      
      if (alerts.length > 0) {
        body.innerHTML = alerts.map(alert => `
          <tr>
            <td>${alert.latitude.toFixed(2)}, ${alert.longitude.toFixed(2)}</td>
            <td>User#${alert.id}</td>
            <td><span class="badge badge-${alert.risk_level.toLowerCase()}">${alert.risk_level}</span></td>
            <td>82/100</td>
            <td>${alert.status}</td>
            <td>
              <button class="btn btn-outline btn-sm" onclick="verifyAlert(${alert.id})">Verify</button>
            </td>
          </tr>
        `).join('');
      } else {
        body.innerHTML = '<tr><td colspan="6" class="text-center">No recent predictions found.</td></tr>';
      }
    }
  };

  // API Traffic Chart
  const ctx = document.getElementById('apiTrafficChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['NASA GIBS', 'NASA CMR', 'NASA Ocean', 'Copernicus'],
      datasets: [{
        label: 'API Requests Today',
        data: [120, 85, 45, 60],
        backgroundColor: [
          'rgba(100, 255, 218, 0.6)',
          'rgba(0, 112, 243, 0.6)',
          'rgba(0, 198, 255, 0.6)',
          'rgba(16, 185, 129, 0.6)'
        ],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#8892b0' } },
        x: { grid: { display: false }, ticks: { color: '#8892b0' } }
      }
    }
  });

  loadMetrics();
  loadPredictions();
});

window.verifyAlert = async (id) => {
  const response = await API.put(`/api/alerts/${id}/verify`, {});
  if (response.ok) {
    alert('Alert verified successfully.');
    location.reload();
  }
};
