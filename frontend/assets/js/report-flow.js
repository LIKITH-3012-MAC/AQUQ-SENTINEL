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
        
        // Store file for later upload
        this.selectedFile = file;

        // Show local preview
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('file-preview').style.display = 'block';
            document.getElementById('preview-img').src = e.target.result;
        };
        reader.readAsDataURL(file);

        UI.showToast("Evidence captured and staged for transmission.", "info");
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

    async runAIPreAnalysis() {
        document.getElementById('ai-loading').style.display = 'block';
        document.getElementById('ai-result').style.display = 'none';

        try {
            this.data.lat = document.getElementById('rep-lat').value || 0;
            this.data.lon = document.getElementById('rep-lon').value || 0;
            this.data.description = document.getElementById('rep-desc').value || "Manual report";

            const analysis = await API.reports.analyze({
                title: "Pre-Analysis",
                description: this.data.description,
                latitude: parseFloat(this.data.lat),
                longitude: parseFloat(this.data.lon),
                report_type: this.data.type,
                severity: "Medium" // Initial guess
            });

            document.getElementById('ai-loading').style.display = 'none';
            document.getElementById('ai-result').style.display = 'block';
            
            document.getElementById('ai-category').textContent = analysis.suggested_category;
            document.getElementById('ai-urgency').textContent = analysis.urgency.toUpperCase();
            document.getElementById('ai-conf').textContent = analysis.confidence + "%";
            document.getElementById('ai-impact').textContent = analysis.possible_impact;
            document.getElementById('ai-suggestion').innerHTML = `<strong>Intelligence Suggestion:</strong> ${analysis.recommended_action}`;
            
            const urgencyClass = analysis.urgency === 'Extreme' || analysis.urgency === 'High' ? 'critical' : 'success';
            document.getElementById('ai-urgency').className = 'status-tag ' + urgencyClass;
            
            // Store results for submission
            this.aiAnalysis = analysis;
        } catch (err) {
            console.error("AI Analysis failed", err);
            document.getElementById('ai-loading').innerHTML = `<p style="color:var(--danger);">AI Telemetry Failure: ${err.message}</p>`;
        }
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
            const report = await API.reports.create({
                title: `${this.data.type.replace('_', ' ')} Incident`,
                description: this.data.description,
                latitude: parseFloat(this.data.lat),
                longitude: parseFloat(this.data.lon),
                report_type: this.data.type,
                severity: this.aiAnalysis ? this.aiAnalysis.urgency : "Medium",
                image_url: "" // Will be updated by binary upload
            });

            if (this.selectedFile) {
                UI.showToast("Uploading evidence...", "info");
                const formData = new FormData();
                formData.append('file', this.selectedFile);
                await API.reports.uploadImage(report.id, formData);
            }

            UI.showToast("Mission Synchronized. ID: " + report.tracking_id, "success");
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 2000);
        } catch (err) {
            UI.showToast("Submission failed: " + err.message, "error");
        }
    }
};
