const AUTH = {
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${CONFIG.API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      
      // Get user role
      const userResponse = await API.get('/api/auth/me');
      if (userResponse.ok) {
        const user = await userResponse.json();
        localStorage.setItem('user', JSON.stringify(user));
        return { success: true, user };
      }
    }
    return { success: false };
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
  },

  isLoggedIn() {
    return !!localStorage.getItem('token');
  },

  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  checkAuth() {
    if (!this.isLoggedIn() && !window.location.pathname.includes('login.html') && !window.location.pathname.includes('register.html') && window.location.pathname !== '/' && !window.location.pathname.includes('index.html')) {
      window.location.href = '/login.html';
    }
  },

  checkAdmin() {
    const user = this.getUser();
    if (!user || user.role !== 'admin') {
      window.location.href = '/user-dashboard.html';
    }
  }
};

// Auto check auth on load
document.addEventListener('DOMContentLoaded', () => {
  AUTH.checkAuth();
});
