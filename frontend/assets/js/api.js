/**
 * AquaSentinel AI - Centralized API Service
 * Handles all futuristic command center data orchestration
 */

const API_BASE_URL = "https://aquasentinel-backend.onrender.com";

const API = {
    async request(endpoint, method = "GET", data = null) {
        const token = localStorage.getItem("token");
        const headers = {
            "Content-Type": "application/json",
        };
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const options = {
            method,
            headers,
        };
        if (data) options.body = JSON.stringify(data);

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            if (response.status === 401) {
                localStorage.removeItem("token");
                window.location.href = "login.html";
                return;
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    auth: {
        login: (credentials) => API.request("/auth/login", "POST", credentials),
        register: (data) => API.request("/auth/register", "POST", data),
        me: () => API.request("/auth/me"),
    },

    dashboard: {
        summary: () => API.request("/dashboard/summary"),
        health: () => API.request("/dashboard/health"),
    },

    reports: {
        create: (data) => API.request("/reports/create", "POST", data),
        list: () => API.request("/reports"),
        updateStatus: (id, status) => API.request(`/reports/${id}/status`, "PATCH", { status }),
        delete: (id) => API.request(`/reports/${id}`, "DELETE"),
    },

    satellite: {
        data: (lat, lon, param) => API.request(`/satellite/nasa?lat=${lat}&lon=${lon}&parameter=${param}`),
        layers: () => API.request("/satellite/layers"),
    },

    weather: {
        marine: (lat, lon) => API.request(`/weather/marine?lat=${lat}&lon=${lon}`),
    },

    ocean: {
        copernicus: (lat, lon) => API.request(`/ocean/copernicus?lat=${lat}&lon=${lon}`),
    },

    risk: {
        calculate: (data) => API.request("/risk/calculate", "POST", data),
        history: () => API.request("/risk/history"),
    },

    debris: {
        detect: (reportId, imagePath) => API.request("/debris/detect", "POST", { report_id: reportId, image_path: imagePath }),
    },

    chatbot: {
        query: (msg, lang) => API.request(`/chatbot/query?message=${encodeURIComponent(msg)}&language=${lang}`, "POST"),
        history: () => API.request("/chatbot/history"),
    },

    simulation: {
        pollution: (lat, lon, type, vol) => API.request(`/simulation/pollution?lat=${lat}&lon=${lon}&spill_type=${type}&volume=${vol}`, "POST"),
    }
};
