const AUTH = {
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
  },

  isLoggedIn() {
    return !!localStorage.getItem('token');
  },

  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  checkAuth() {
    const path = window.location.pathname;
    const isAuthPage = path.includes('login.html') || path.includes('register.html') || path === '/' || path.includes('index.html');
    
    if (!this.isLoggedIn() && !isAuthPage) {
      window.location.href = 'login.html';
    }
  },

  checkAdmin() {
    const user = this.getUser();
    if (!user || user.role !== 'admin') {
      window.location.href = 'dashboard.html';
    }
  }
};

// Auto check auth on load
document.addEventListener('DOMContentLoaded', () => {
  AUTH.checkAuth();
});
