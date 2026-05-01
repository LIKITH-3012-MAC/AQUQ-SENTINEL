/**
 * AquaSentinel AI - Tactical Reporting Flow Controller
 */

const ReportFlow = {
    currentStep: 1,
    data: {
        type: '',
        lat: 0,
        lon: 0,
        description: '',
        imageUrl: ''
    },

    selectType(type, el) {
        this.data.type = type;
        document.querySelectorAll('.issue-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        setTimeout(() => this.next(), 300);
    },

    getLocation() {
        if (!navigator.geolocation) return alert("GPS not available.");
        navigator.geolocation.getCurrentPosition(pos => {
            document.getElementById('rep-lat').value = pos.coords.latitude.toFixed(6);
            document.getElementById('rep-lon').value = pos.coords.longitude.toFixed(6);
            this.data.lat = pos.coords.latitude;
            this.data.lon = pos.coords.longitude;
        });
    },

    async handleFileUpload(input) {
        const file = input.files[0];
        if (!file) return;
        
        // Show local preview
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('file-preview').style.display = 'block';
            document.getElementById('preview-img').src = e.target.result;
        };
        reader.readAsDataURL(file);

        // Actual upload to Intelligence OS
        const formData = new FormData();
        formData.append('file', file);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/images/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await response.json();
            if (response.ok) {
                this.data.imageUrl = data.filename;
                UI.showToast("Evidence transmitted successfully.", "success");
            } else {
                throw new Error(data.detail || "Upload failed");
            }
        } catch (err) {
            UI.showToast("Telemetry failure: " + err.message, "error");
        }
    },

    next() {
        if (this.currentStep === 6) return;
        
        // Validation per step
        if (this.currentStep === 1 && !this.data.type) return alert("Select issue type first.");
        
        this.currentStep++;
        this.updateUI();

        if (this.currentStep === 5) this.runAIPreAnalysis();
        if (this.currentStep === 6) this.generateSummary();
    },

    prev() {
        if (this.currentStep === 1) return;
        this.currentStep--;
        this.updateUI();
    },

    updateUI() {
        document.querySelectorAll('.report-step').forEach(s => s.classList.remove('active'));
        document.getElementById(`step-${this.currentStep}`).classList.add('active');
        
        document.querySelectorAll('.step').forEach(s => {
            const stepNum = parseInt(s.dataset.step);
            s.classList.remove('active');
            if (stepNum <= this.currentStep) s.classList.add('active');
        });

        document.getElementById('prev-btn').style.visibility = this.currentStep === 1 ? 'hidden' : 'visible';
        document.getElementById('next-btn').style.display = this.currentStep === 6 ? 'none' : 'flex';
    },

    runAIPreAnalysis() {
        document.getElementById('ai-loading').style.display = 'block';
        document.getElementById('ai-result').style.display = 'none';

        setTimeout(() => {
            document.getElementById('ai-loading').style.display = 'none';
            document.getElementById('ai-result').style.display = 'block';
            
            // Mock AI results based on type
            const types = {
                'plastic_waste': { cat: 'Plastic Debris Cluster', urgency: 'MEDIUM', impact: 'High risk of microplastic degradation. Cleanup recommended within 7 days.' },
                'oil_spill': { cat: 'Petroleum Surface Slick', urgency: 'CRITICAL', impact: 'Severe toxicity to marine avifauna. Immediate containment required.' },
                'algae_bloom': { cat: 'Eutrophication Event', urgency: 'HIGH', impact: 'Hypoxic conditions detected. Fish kill risk imminent.' },
                'dead_fish': { cat: 'Mass Mortality Incident', urgency: 'CRITICAL', impact: 'Pathogen risk high. Immediate investigation by regional authorities needed.' }
            };

            const res = types[this.data.type] || types['plastic_waste'];
            document.getElementById('ai-category').textContent = res.cat;
            document.getElementById('ai-urgency').textContent = res.urgency;
            document.getElementById('ai-urgency').className = 'status-tag ' + (res.urgency === 'CRITICAL' ? 'critical' : 'success');
            document.getElementById('ai-impact').textContent = res.impact;
        }, 1500);
    },

    generateSummary() {
        this.data.lat = document.getElementById('rep-lat').value;
        this.data.lon = document.getElementById('rep-lon').value;
        this.data.description = document.getElementById('rep-desc').value;

        document.getElementById('summary-content').innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 1rem; font-size: 0.95rem;">
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:0.5rem;">
                    <span style="color:var(--text-secondary);">Issue:</span> <strong>${this.data.type.replace('_', ' ').toUpperCase()}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:0.5rem;">
                    <span style="color:var(--text-secondary);">Location:</span> <strong>${this.data.lat}, ${this.data.lon}</strong>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:0.5rem;">
                    <span style="color:var(--text-secondary);">Description:</span> <strong style="max-width:200px; text-align:right;">${this.data.description.substring(0, 50)}...</strong>
                </div>
                <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:0.5rem;">
                    <span style="color:var(--text-secondary);">Urgency:</span> <strong class="text-gradient">${document.getElementById('ai-urgency').textContent}</strong>
                </div>
            </div>
        `;
    },

    async submit() {
        try {
            const report = await API.request('/reports/create', 'POST', {
                title: `${this.data.type.replace('_', ' ')} Incident`,
                description: this.data.description,
                latitude: parseFloat(this.data.lat),
                longitude: parseFloat(this.data.lon),
                report_type: this.data.type,
                severity: document.getElementById('ai-urgency').textContent,
                image_url: this.data.imageUrl
            });

            alert("Mission Synchronized. Tracking ID: " + report.id);
            window.location.href = 'dashboard.html';
        } catch (err) {
            alert("Submission failed: " + err.message);
        }
    }
};
