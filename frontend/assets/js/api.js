/**
 * AquaSentinel AI - Standardized API Interaction Layer
 */

const API = {
    async request(endpoint, method = 'GET', body = null) {
        const token = localStorage.getItem('token');
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
        const url = endpoint.startsWith('http') ? endpoint : `${CONFIG.API_BASE_URL}/api/${cleanEndpoint}`;
        
        console.log(`[NETWORK] Attempting ${method} -> ${url}`);

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
            
            // Check if response is JSON
            const contentType = response.headers.get("content-type");
            let data;
            if (contentType && contentType.includes("application/json")) {
                data = await response.json();
            } else {
                const text = await response.text();
                throw new Error(`Server returned non-JSON response: ${text.substring(0, 100)}`);
            }

            if (!response.ok) {
                if (response.status === 401) {
                    console.warn("Session Expired. Terminating interface.");
                    AUTH.logout();
                }
                throw new Error(data.detail || data.message || 'Command failed');
            }

            return data;
        } catch (err) {
            console.error(`[CRITICAL] API Request Failure [${endpoint}]:`, err);
            throw err;
        }
    },

    // Resource Specific Methods
    auth: {
        register: (data) => API.request('/auth/register', 'POST', data),
        login: (data) => API.request('/auth/login', 'POST', data),
        me: () => API.request('/auth/me', 'GET'),
        logout: () => API.request('/auth/logout', 'POST'),
        forgotPasswordQuestion: (email) => API.request('/auth/forgot-password/question', 'POST', { email }),
        verifyAnswer: (data) => API.request('/auth/forgot-password/verify', 'POST', data),
        resetPassword: (data) => API.request('/auth/forgot-password/reset', 'POST', data),
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
