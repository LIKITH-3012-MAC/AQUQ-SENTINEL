const Profile = {
    async init() {
        await this.load();
    },

    async load() {
        try {
            const data = await API.request('/profile/me');
            if (data.success) {
                this.render(data);
                this.currentUserData = data;
            }
        } catch (err) {
            console.error("Profile load failure:", err);
            UI.showNotification("Critical Error: Intelligence sync failed.", "danger");
        }
    },

    render(data) {
        const { user, profile, stats, recent_reports, recent_activity } = data;

        // Header / Identity
        const nameEl = document.getElementById('display-name');
        const roleEl = document.getElementById('display-role');
        const bioEl = document.getElementById('display-bio');
        const avatarEl = document.getElementById('display-avatar');

        if (nameEl) nameEl.textContent = user.full_name || "Anonymous Operator";
        if (roleEl) {
            roleEl.textContent = (user.role || "USER").toUpperCase();
            roleEl.className = `status-tag ${user.role === 'admin' ? 'critical' : 'success'}`;
        }
        if (bioEl) bioEl.textContent = profile.bio || "No mission bio established in the Intelligence Matrix.";
        
        if (avatarEl) {
            if (profile.profile_image_url) {
                avatarEl.src = profile.profile_image_url.startsWith('http') ? profile.profile_image_url : (CONFIG.API_BASE_URL + profile.profile_image_url);
            } else {
                avatarEl.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.full_name)}&background=00f3ff&color=000&bold=true`;
            }
        }

        // Stats
        const reportsStat = document.getElementById('stat-reports');
        const impactStat = document.getElementById('stat-impact');
        const chatsStat = document.getElementById('stat-chats');
        const missionsStat = document.getElementById('stat-missions');

        if (reportsStat) reportsStat.textContent = stats.total_reports || "0";
        if (impactStat) impactStat.textContent = profile.impact_score || "0";
        if (chatsStat) chatsStat.textContent = stats.total_chat_queries || "0";
        if (missionsStat) missionsStat.textContent = stats.missions_joined || "0";

        // Completion
        const completion = profile.profile_completion_percent || 0;
        const compBar = document.getElementById('completion-bar');
        const compText = document.getElementById('completion-text');
        if (compBar) compBar.style.width = `${completion}%`;
        if (compText) compText.textContent = `${completion}%`;

        // Identity Matrix
        const emailEl = document.getElementById('display-email');
        const phoneEl = document.getElementById('display-phone');
        const locEl = document.getElementById('display-location');
        const regEl = document.getElementById('display-region');
        const orgEl = document.getElementById('display-org');
        const langEl = document.getElementById('display-language');
        const joinedEl = document.getElementById('display-joined');

        if (emailEl) emailEl.textContent = user.email || "Secure transmission only";
        if (phoneEl) phoneEl.textContent = profile.phone || "Secure line not established";
        if (locEl) {
            const locStr = (profile.district || profile.city) ? `${profile.district || profile.city}, ${profile.state || 'Unknown'}` : "Global Waters";
            locEl.textContent = locStr;
        }
        if (regEl) regEl.textContent = profile.preferred_region || "Global Tactical Sector";
        if (orgEl) {
            const orgStr = (profile.organization || profile.occupation) ? `${profile.occupation || ''} @ ${profile.organization || ''}` : "Independent Operator";
            orgEl.textContent = orgStr;
        }
        if (langEl) langEl.textContent = profile.preferred_language || "English (Default)";
        if (joinedEl) {
            const date = new Date(user.created_at);
            joinedEl.textContent = isNaN(date.getTime()) ? "Awaiting Timestamp" : date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
        }

        // Activity Timeline
        this.renderTimeline(recent_activity);
    },

    renderTimeline(activities) {
        const list = document.getElementById('activity-list');
        if (!list) return;

        if (!activities || activities.length === 0) {
            list.innerHTML = `<p style="color: var(--text-secondary); text-align: center; padding: 2rem; border: 1px dashed var(--border-color); border-radius: 12px; margin-top: 1rem;">No historical logs found in the operational timeline.</p>`;
            return;
        }

        list.innerHTML = '<div style="position: absolute; left: 15px; top: 0; bottom: 0; width: 1px; background: var(--border-color);"></div>' + 
            activities.map(act => `
            <div style="display: flex; gap: 1.5rem; position: relative; z-index: 1;">
                <div style="width: 30px; height: 30px; border-radius: 50%; background: var(--surface-color); border: 2px solid var(--accent-color); display: flex; align-items: center; justify-content: center; font-size: 0.8rem;">
                    <i class="${this.getEventIcon(act.event_type)}"></i>
                </div>
                <div style="flex: 1; padding-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 0.9rem; color: var(--accent-color);">${act.event_type.replace('_', ' ').toUpperCase()}</span>
                        <span style="font-size: 0.7rem; color: var(--text-secondary);">${new Date(act.created_at).toLocaleString()}</span>
                    </div>
                    <p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.3rem;">${act.description}</p>
                </div>
            </div>
        `).join('');
    },

    getEventIcon(type) {
        switch(type) {
            case 'profile_update': return 'fas fa-user-edit';
            case 'photo_upload': return 'fas fa-camera';
            case 'report_submitted': return 'fas fa-file-alt';
            case 'mission_joined': return 'fas fa-flag';
            default: return 'fas fa-circle-dot';
        }
    },

    openEdit() {
        const { user, profile } = this.currentUserData;
        document.getElementById('edit-name').value = user.full_name;
        document.getElementById('edit-phone').value = profile.phone || "";
        document.getElementById('edit-country').value = profile.country || "";
        document.getElementById('edit-state').value = profile.state || "";
        document.getElementById('edit-district').value = profile.district || profile.city || "";
        document.getElementById('edit-occupation').value = profile.occupation || "";
        document.getElementById('edit-organization').value = profile.organization || "";
        document.getElementById('edit-language').value = profile.preferred_language;
        document.getElementById('edit-region').value = profile.preferred_region || "";
        document.getElementById('edit-weather').value = profile.preferred_weather_unit || "metric";
        document.getElementById('edit-bio').value = profile.bio || "";
        
        document.getElementById('edit-modal').style.display = 'flex';
    },

    closeEdit() {
        document.getElementById('edit-modal').style.display = 'none';
    },

    async save(e) {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Synchronizing...';
        btn.disabled = true;

        const updateData = {
            full_name: document.getElementById('edit-name').value,
            phone: document.getElementById('edit-phone').value,
            country: document.getElementById('edit-country').value,
            state: document.getElementById('edit-state').value,
            district: document.getElementById('edit-district').value,
            city: document.getElementById('edit-district').value, // Use same for city for simplicity
            occupation: document.getElementById('edit-occupation').value,
            organization: document.getElementById('edit-organization').value,
            preferred_language: document.getElementById('edit-language').value,
            preferred_region: document.getElementById('edit-region').value,
            preferred_weather_unit: document.getElementById('edit-weather').value,
            bio: document.getElementById('edit-bio').value
        };

        try {
            const res = await API.request('/profile/me', 'PATCH', updateData);
            if (res.success) {
                UI.showNotification("Intelligence profile updated successfully.", "success");
                this.render(res);
                this.currentUserData = res;
                this.closeEdit();
            }
        } catch (err) {
            UI.showNotification("Update failed: Security sync error.", "danger");
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    async uploadPhoto(e) {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        UI.showNotification("Uploading profile identification...", "info");

        try {
            const result = await API.profile.uploadPhoto(formData);
            if (result.success) {
                UI.showNotification("Identification image synced.", "success");
                document.getElementById('display-avatar').src = result.url + "?t=" + Date.now();
                await this.load(); // Reload to update completion %
            } else {
                UI.showNotification(result.detail || "Upload failed.", "danger");
            }
        } catch (err) {
            UI.showNotification("Network error during upload.", "danger");
        }
    }
};

document.addEventListener('DOMContentLoaded', () => Profile.init());
