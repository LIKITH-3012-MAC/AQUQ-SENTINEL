/**
 * AquaSentinel AI - Global Configuration
 */

const CONFIG = {
    // Development default
    API_BASE_URL: "http://127.0.0.1:8000",
    VERSION: "4.0.0-PROD",
    SYSTEM_NAME: "AquaSentinel Intelligence OS"
};

// Auto-switch to ONE CENTRAL Render API in production
if (window.location.hostname !== '127.0.0.1' && window.location.hostname !== 'localhost') {
    CONFIG.API_BASE_URL = "https://aquq-sentinel-1.onrender.com";
}
