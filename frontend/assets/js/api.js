/**
 * AquaSentinel AI - Standardized API Interaction Layer
 */

const API = {
    async request(endpoint, method = 'GET', body = null) {
        const token = localStorage.getItem('token');
        const url = endpoint.startsWith('http') ? endpoint : `${CONFIG.API_BASE_URL}${endpoint.startsWith('/') ? endpoint : '/api' + endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const options = {
            method,
            headers
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(url, options);
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    console.warn("Session Expired. Terminating interface.");
                    AUTH.logout();
                }
                throw new Error(data.detail || 'Command failed');
            }

            return data;
        } catch (err) {
            console.error(`API Request Error [${endpoint}]:`, err);
            throw err;
        }
    },

    // Resource Specific Methods
    auth: {
        register: (data) => API.request('/auth/register', 'POST', data),
        login: (data) => API.request('/auth/login', 'POST', data),
        me: () => API.request('/auth/me', 'GET'),
        logout: () => API.request('/auth/logout', 'POST'),
        updatePrefs: (data) => API.request('/auth/preferences', 'PATCH', data)
    },

    reports: {
        list: () => API.request('/reports'),
        create: (data) => API.request('/reports', 'POST', data),
        get: (id) => API.request(`/reports/${id}`)
    },

    dashboard: {
        summary: () => API.request('/dashboard/summary')
    },

    chatbot: {
        query: (data) => API.request('/chatbot/message', 'POST', {
            message: data.message,
            session_id: data.session_id || 'default',
            language: data.language || 'English',
            location: data.location || 'Global',
            role: localStorage.getItem('role') || 'user'
        }),
        history: (sessionId) => API.request(`/chatbot/history?session_id=${sessionId}`),
        sessions: () => API.request('/chatbot/sessions')
    }
};
