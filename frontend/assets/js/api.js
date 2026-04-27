const API = {
  async fetch(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      if (!window.location.pathname.includes('login.html')) {
        window.location.href = '/login.html';
      }
    }

    return response;
  },

  async get(endpoint) {
    return this.fetch(endpoint, { method: 'GET' });
  },

  async post(endpoint, body) {
    return this.fetch(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  async put(endpoint, body) {
    return this.fetch(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  },

  async delete(endpoint) {
    return this.fetch(endpoint, { method: 'DELETE' });
  },

  async upload(endpoint, formData) {
    const token = localStorage.getItem('token');
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });
  }
};
