/**
 * AquaSentinel AI - Authentication Controller
 */

const AUTH = {
    async login(email, password) {
        try {
            const data = await API.auth.login({ email, password });
            if (data.success) {
                this.setSession(data);
                this.redirectByRole(data.role);
                return data;
            }
        } catch (err) {
            throw err;
        }
    },

    async register(userData) {
        try {
            const data = await API.auth.register(userData);
            if (data.success) {
                this.setSession(data);
                this.redirectByRole(data.role);
                return data;
            }
        } catch (err) {
            throw err;
        }
    },

    setSession(data) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('role', data.role);
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('role');
        window.location.href = 'login.html';
    },

    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    getToken() {
        return localStorage.getItem('token');
    },

    isAuthenticated() {
        return !!this.getToken();
    },

    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'login.html';
        }
    },

    redirectByRole(role) {
        if (role === 'admin') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'dashboard.html';
        }
    },

    checkAuthState() {
        const path = window.location.pathname;
        const publicPages = ['/', '/index.html', '/login.html', '/register.html'];
        
        const isPublic = publicPages.some(p => path.endsWith(p));
        
        if (!this.isAuthenticated() && !isPublic) {
            this.logout();
        } else if (this.isAuthenticated() && (path.endsWith('login.html') || path.endsWith('register.html'))) {
            this.redirectByRole(localStorage.getItem('role'));
        }
    }
};

// Initialize auth check
document.addEventListener('DOMContentLoaded', () => AUTH.checkAuthState());
