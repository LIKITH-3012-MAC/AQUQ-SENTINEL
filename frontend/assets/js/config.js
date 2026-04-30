/**
 * AquaSentinel AI - Global Configuration
 */

const CONFIG = {
    // API_BASE_URL: "https://aquq-sentinel.onrender.com", // Production
    API_BASE_URL: "http://localhost:8000", // Development
    VERSION: "4.0.0-PROD",
    SYSTEM_NAME: "AquaSentinel Intelligence OS"
};

// Auto-switch to production if on vercel
if (window.location.hostname.includes('vercel.app')) {
    CONFIG.API_BASE_URL = "https://aquq-sentinel.onrender.com";
}
