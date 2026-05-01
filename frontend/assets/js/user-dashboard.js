/**
 * AquaSentinel AI - User Dashboard Controller
 * NOTE: Dashboard logic is primarily in dashboard.html inline script.
 * This file provides supplementary utilities if needed.
 */

document.addEventListener('DOMContentLoaded', async () => {
  const user = AUTH.getCurrentUser();
  
  // Update user display elements if they exist
  if (user) {
    const nameEl = document.getElementById('userName');
    const firstNameEl = document.getElementById('userFirstName');
    if (nameEl) nameEl.textContent = user.full_name;
    if (firstNameEl) firstNameEl.textContent = user.full_name.split(' ')[0];
  }
});
