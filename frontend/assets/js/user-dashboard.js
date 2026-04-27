document.addEventListener('DOMContentLoaded', async () => {
  const user = AUTH.getUser();
  if (user) {
    document.getElementById('userName').textContent = user.name;
    document.getElementById('userFirstName').textContent = user.name.split(' ')[0];
  }

  // Initialize Map
  const map = L.map('map').setView([12.9716, 77.5946], 5); // Default to some location
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // Load Alerts
  const loadAlerts = async () => {
    const response = await API.get('/api/alerts/user');
    if (response.ok) {
      const alerts = await response.json();
      const list = document.getElementById('alertsList');
      document.getElementById('activeAlerts').textContent = alerts.length;
      
      if (alerts.length > 0) {
        list.innerHTML = alerts.map(alert => `
          <div class="alert-item ${alert.risk_level}">
            <strong>${alert.title}</strong>
            <p style="font-size: 0.8rem; margin-top: 0.25rem;">${alert.message}</p>
            <small class="text-muted">${new Date(alert.created_at).toLocaleDateString()}</small>
          </div>
        `).join('');
      }
    }
  };

  // Initialize Debris Chart
  const ctx = document.getElementById('debrisChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Debris Density Score',
        data: [45, 52, 48, 70, 65, 82],
        borderColor: '#64ffda',
        backgroundColor: 'rgba(100, 255, 218, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { 
          beginAtZero: true,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#8892b0' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#8892b0' }
        }
      }
    }
  });

  loadAlerts();
});
