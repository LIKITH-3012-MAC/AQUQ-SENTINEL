/**
 * AquaSentinel AI - Standardized API Interaction Layer
 */

// Fallback for CONFIG if config.js fails to load
if (typeof CONFIG === 'undefined') {
    window.CONFIG = {
        API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://127.0.0.1:8001'
            : 'https://aquq-sentinel-1.onrender.com',
        VERSION: "4.0.0-PROD-FALLBACK",
        SYSTEM_NAME: "AquaSentinel Intelligence OS"
    };
}

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
                const isAuthFlow = endpoint.includes('/auth/') && !endpoint.includes('/auth/me');
                if (response.status === 401 && !isAuthFlow) {
                    console.warn("Session Expired. Terminating interface.");
                    if (typeof AUTH !== 'undefined') {
                        AUTH.logout();
                    } else {
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        localStorage.removeItem('role');
                        window.location.href = 'login.html';
                    }
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
        create: (data) => API.request('/reports/create', 'POST', data),
        analyze: (data) => API.request('/reports/analyze', 'POST', data),
        get: (id) => API.request(`/reports/${id}`),
        history: (id) => API.request(`/reports/${id}/history`),
        uploadImage: (id, formData) => fetch(`${CONFIG.API_BASE_URL}/api/reports/${id}/image`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        }).then(r => r.json())
    },

    dashboard: {
        summary: () => API.request('/dashboard/summary')
    },

    health: {
        getScore: (lat, lon) => API.request(`/health/score?lat=${lat}&lon=${lon}`),
        calculate: (data) => API.request('/health/calculate', 'POST', data)
    },

    hyperlocal: {
        getIntelligence: (lat, lon, radius = 50) => API.request(`/hyperlocal/intelligence?lat=${lat}&lon=${lon}&radius=${radius}`)
    },

    weather: {
        getMarine: (lat, lon) => API.request(`/weather/marine?lat=${lat}&lon=${lon}`),
        getByCity: (place) => API.request(`/weather/current?place=${place}`)
    },

    predictions: {
        getHotspots: (lat, lon, hours = 24) => API.request(`/predictions/hotspots?lat=${lat}&lon=${lon}&hours=${hours}`)
    },

    missions: {
        list: () => API.request('/missions'),
        create: (reportId) => API.request(`/missions/${reportId}/create`, 'POST'),
        accept: (missionId) => API.request(`/missions/${missionId}/accept`, 'POST'),
        updateProgress: (missionId, data) => API.request(`/missions/${missionId}/progress`, 'PATCH', data)
    },

    profile: {
        get: () => API.request('/profile/me'),
        update: (data) => API.request('/profile/me', 'PATCH', data),
        uploadPhoto: (formData) => fetch(`${CONFIG.API_BASE_URL}/api/profile/me/photo`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        }).then(r => r.json())
    },

    simulation: {
        create: (data) => API.request('/admin/simulations/', 'POST', data),
        list: () => API.request('/admin/simulations/'),
        reset: () => API.request('/admin/simulations/reset', 'POST'),
        delete: (id) => API.request(`/admin/simulations/${id}`, 'DELETE')
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
    },

    // AI Marine Debris Intelligence Layer
    aiDetection: {
        detectFromImage: (formData) => fetch(`${CONFIG.API_BASE_URL}/api/ai/detect/image`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        }).then(r => r.json()),
        simulate: (data) => API.request('/ai/detect/simulate', 'POST', data),
        getResults: (params = '') => API.request(`/ai/detect/results${params ? '?' + params : ''}`),
        getDetail: (id) => API.request(`/ai/detect/results/${id}`),
        getEvidence: (id) => API.request(`/ai/detect/evidence/${id}`),
        getDashboard: () => API.request('/ai/detect/dashboard'),
        getMapOverlays: () => API.request('/ai/detect/map/overlays'),
        getEcosystem: (params = '') => API.request(`/ai/detect/ecosystem${params ? '?' + params : ''}`),
        ingestTile: (data) => API.request('/ai/detect/tiles/ingest', 'POST', data)
    }
};
