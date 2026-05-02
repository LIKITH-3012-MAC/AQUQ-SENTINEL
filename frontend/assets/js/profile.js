/**
 * AquaSentinel AI - Profile Controller
 */

const Profile = {
    data: null,

    async init() {
        UI.showToast("Fetching mission profile...", "info");
        try {
            this.data = await API.profile.get();
            this.render();
        } catch (err) {
            UI.showToast("Failed to load profile: " + err.message, "error");
        }
    },

    render() {
        if (!this.data) return;
        const { user, profile, stats, recent_reports } = this.data;

        // Header
        document.getElementById('display-name').textContent = user.full_name;
        document.getElementById('display-role').textContent = user.role.toUpperCase();
        document.getElementById('display-bio').textContent = profile.bio || "Marine monitoring enthusiast and protector of the oceans.";
        document.getElementById('display-avatar').src = profile.profile_image_url || `https://ui-avatars.com/api/?name=${user.full_name.replace(' ', '+')}&background=00f3ff&color=000&bold=true`;

        // Stats
        document.getElementById('stat-reports').textContent = stats.total_reports;
        document.getElementById('stat-chats').textContent = stats.total_chat_queries;
        document.getElementById('stat-missions').textContent = stats.missions_joined;

        // Info
        document.getElementById('display-email').textContent = user.email;
        document.getElementById('display-phone').textContent = profile.phone || "Not set";
        document.getElementById('display-location').textContent = (profile.city || profile.state) ? `${profile.city || ''}, ${profile.state || ''}` : "Not set";
        document.getElementById('display-region').textContent = profile.preferred_region || "Global";
        document.getElementById('display-language').textContent = profile.preferred_language || "English";
        document.getElementById('display-joined').textContent = new Date(user.created_at).toLocaleDateString();

        // Activity
        const activityList = document.getElementById('activity-list');
        if (recent_reports && recent_reports.length > 0) {
            activityList.innerHTML = recent_reports.map(r => `
                <div class="glass-card" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background: rgba(255,255,255,0.02);">
                    <div>
                        <div style="font-weight: 700; font-size: 0.85rem;">${r.title}</div>
                        <div style="font-size: 0.7rem; color: var(--text-secondary);">${new Date(r.created_at).toLocaleDateString()} | ${r.status}</div>
                    </div>
                    <a href="dashboard.html" class="btn btn-outline" style="padding: 0.3rem 0.8rem; font-size: 0.6rem;">Track</a>
                </div>
            `).join('');
        }

        // Populate Edit Form
        document.getElementById('edit-name').value = user.full_name;
        document.getElementById('edit-phone').value = profile.phone || '';
        document.getElementById('edit-state').value = profile.state || '';
        document.getElementById('edit-city').value = profile.city || '';
        document.getElementById('edit-language').value = profile.preferred_language || 'English';
        document.getElementById('edit-region').value = profile.preferred_region || '';
        document.getElementById('edit-bio').value = profile.bio || '';
    },

    openEdit() {
        document.getElementById('edit-modal').style.display = 'flex';
    },

    closeEdit() {
        document.getElementById('edit-modal').style.display = 'none';
    },

    async save(e) {
        e.preventDefault();
        UI.showToast("Synchronizing profile with DB...", "info");

        const updateData = {
            full_name: document.getElementById('edit-name').value,
            phone: document.getElementById('edit-phone').value,
            state: document.getElementById('edit-state').value,
            city: document.getElementById('edit-city').value,
            preferred_language: document.getElementById('edit-language').value,
            preferred_region: document.getElementById('edit-region').value,
            bio: document.getElementById('edit-bio').value
        };

        try {
            const res = await API.profile.update(updateData);
            if (res.success) {
                this.data = res;
                this.render();
                this.closeEdit();
                UI.showToast("Neural profile updated successfully.", "success");
            }
        } catch (err) {
            UI.showToast("Sync failure: " + err.message, "error");
        }
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => Profile.init());
