/**
 * AquaSentinel AI - Admin Control Tower Controller
 * Uses the standardized API layer from api.js
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Check Admin Role
  AUTH.requireAuth();
  if (localStorage.getItem('role') !== 'admin') {
    window.location.href = 'dashboard.html';
    return;
  }

  // Load Overview Metrics
  const loadMetrics = async () => {
    try {
      const data = await API.request('/admin/overview');
      const el = (id) => document.getElementById(id);
      if (el('totalUsers')) el('totalUsers').textContent = data.total_users;
      if (el('totalAssessments')) el('totalAssessments').textContent = data.total_assessments;
      if (el('criticalAlerts')) el('criticalAlerts').textContent = data.critical_alerts;
      if (el('apiHealth')) el('apiHealth').textContent = data.api_health;
    } catch (err) {
      console.error("Failed to load admin metrics:", err);
    }
  };

  // Load Recent Predictions
  const loadPredictions = async () => {
    try {
      const alerts = await API.request('/alerts');
      const body = document.getElementById('predictionsTableBody');
      if (!body) return;
      
      if (alerts.length > 0) {
        body.innerHTML = alerts.map(alert => `
          <tr>
            <td>${alert.latitude.toFixed(2)}, ${alert.longitude.toFixed(2)}</td>
            <td>Alert#${alert.id}</td>
            <td><span class="status-tag ${alert.severity === 'CRITICAL' ? 'critical' : ''}">${alert.severity}</span></td>
            <td>${alert.status}</td>
            <td>
              <button class="btn btn-outline btn-sm" onclick="verifyAlert(${alert.id})">Verify</button>
            </td>
          </tr>
        `).join('');
      } else {
        body.innerHTML = '<tr><td colspan="5" class="text-center">No recent predictions found.</td></tr>';
      }
    } catch (err) {
      console.error("Failed to load predictions:", err);
    }
  };

  // API Traffic Chart
  const chartCanvas = document.getElementById('apiTrafficChart');
  if (chartCanvas && typeof Chart !== 'undefined') {
    const ctx = chartCanvas.getContext('2d');
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
  }

  loadMetrics();
  loadPredictions();
});

window.verifyAlert = async (id) => {
  try {
    await API.request(`/alerts/${id}/verify`, 'PUT');
    alert('Alert verified successfully.');
    location.reload();
  } catch (err) {
    alert('Failed to verify: ' + err.message);
  }
};
