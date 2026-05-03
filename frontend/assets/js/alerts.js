/**
 * AquaSentinel Intelligence OS - Global Alert System Controller
 * Handles real-time premium notifications across all HTML pages.
 */

const GlobalAlerts = {
    audioPath: 'assets/audio/high_frequency_alert.mp3',
    displayedAlerts: new Set(JSON.parse(localStorage.getItem('displayed_alerts') || '[]')),
    pollInterval: null,
    isSoundEnabled: false,

    init() {
        console.log("[SYSTEM] Initializing Global Alert Intelligence Grid...");
        
        // 1. Create Container
        this.createContainer();

        // 2. Setup Interaction Listener (to enable audio due to browser policies)
        document.addEventListener('click', () => {
            this.isSoundEnabled = true;
        }, { once: true });

        // 3. Initial Check
        this.checkActiveAlerts();

        // 4. Start Polling (every 30 seconds for background updates)
        this.pollInterval = setInterval(() => this.checkActiveAlerts(), 30000);
    },

    createContainer() {
        if (document.getElementById('global-alert-container')) return;
        const container = document.createElement('div');
        container.id = 'global-alert-container';
        container.className = 'global-alert-container';
        document.body.appendChild(container);
    },

    async checkActiveAlerts() {
        // Only check if logged in
        if (!localStorage.getItem('token')) return;

        try {
            // We'll use the user alerts endpoint
            const alerts = await API.request('/alerts/user');
            
            if (alerts && Array.isArray(alerts)) {
                // Find first new active alert
                const newAlert = alerts.find(a => a.status === 'active' && !this.displayedAlerts.has(a.id));
                
                if (newAlert) {
                    this.showPremiumAlert(newAlert);
                }
            }
        } catch (err) {
            console.warn("[INTEL] Alert polling synchronization issue:", err);
        }
    },

    showPremiumAlert(alert) {
        const container = document.getElementById('global-alert-container');
        if (!container) return;

        // Mark as displayed
        this.displayedAlerts.add(alert.id);
        localStorage.setItem('displayed_alerts', JSON.stringify(Array.from(this.displayedAlerts)));

        // Determine severity class and icon
        let severityClass = 'info';
        let icon = 'fa-info-circle';
        
        const sev = alert.severity.toLowerCase();
        if (sev === 'critical' || sev === 'high') {
            severityClass = 'high';
            icon = 'fa-triangle-exclamation';
        } else if (sev === 'medium' || sev === 'warning') {
            severityClass = 'medium';
            icon = 'fa-radiation';
        }

        const card = document.createElement('div');
        card.className = `premium-alert-card ${severityClass}`;
        card.innerHTML = `
            <div class="shimmer-sweep"></div>
            <div class="alert-header">
                <div class="alert-icon-node">
                    <div class="ripple"></div>
                    <i class="fas ${icon}"></i>
                </div>
                <div class="alert-content">
                    <h4 class="alert-title">${alert.title}</h4>
                    <p class="alert-message">${alert.message}</p>
                </div>
            </div>
            <div class="alert-chips">
                <span class="alert-chip"><i class="fas fa-shield-virus"></i> ${alert.severity}</span>
                <span class="alert-chip"><i class="fas fa-location-dot"></i> ${alert.latitude.toFixed(3)}, ${alert.longitude.toFixed(3)}</span>
                ${alert.is_simulated ? '<span class="alert-chip" style="color: #ff3366; border-color: rgba(255,51,102,0.3); background: rgba(255,51,102,0.05);">[SIMULATED]</span>' : ''}
            </div>
            <div class="alert-timer-edge"></div>
        `;

        container.appendChild(card);

        // 1. Play Sound
        this.playSound();

        // 2. Trigger Vibration
        this.triggerVibration();

        // 3. Lifecycle Management (5 seconds)
        setTimeout(() => {
            card.classList.add('exit');
            setTimeout(() => card.remove(), 600);
        }, 5000);
    },

    playSound() {
        if (!this.isSoundEnabled) return;
        const audio = new Audio(this.audioPath);
        audio.volume = 0.5;
        audio.play().catch(e => console.warn("Audio autoplay blocked by browser intelligence."));
    },

    triggerVibration() {
        if ("vibrate" in navigator) {
            // Pattern: 200ms on, 100ms off, 200ms on
            navigator.vibrate([200, 100, 200]);
        }
    }
};

// Initialize if on a relevant page
document.addEventListener('DOMContentLoaded', () => {
    // List of pages to show alerts on (or just all pages if preferred)
    GlobalAlerts.init();
});
