/**
 * AquaSentinel UI - Global Theme & UX Controller
 */

const UI = {
    init() {
        this.loadTheme();
        this.setupNavigation();
        this.initAIAssistant();
    },

    loadTheme() {
        const savedTheme = localStorage.getItem('aquasentinel_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeToggleIcon(savedTheme);
    },

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('aquasentinel_theme', newTheme);
        this.updateThemeToggleIcon(newTheme);

        // Sync with backend if user is logged in
        if (localStorage.getItem('token')) {
            this.syncThemeWithBackend(newTheme);
        }
    },

    updateThemeToggleIcon(theme) {
        const icon = document.querySelector('.theme-toggle i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    },

    async syncThemeWithBackend(theme) {
        try {
            await API.request('/auth/preferences', 'PATCH', { theme });
        } catch (err) {
            console.error("Failed to sync theme preferences", err);
        }
    },

    setupNavigation() {
        const path = window.location.pathname;
        document.querySelectorAll('.nav-links a').forEach(link => {
            if (path.includes(link.getAttribute('href'))) {
                link.classList.add('active');
            }
        });
    },

    initAIAssistant() {
        const trigger = document.getElementById('ai-copilot-trigger');
        if (trigger) {
            trigger.addEventListener('click', () => this.toggleAICopilot());
        }
    },

    toggleAICopilot() {
        const widget = document.getElementById('copilot-widget');
        if (widget) {
            widget.classList.toggle('active');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => UI.init());
