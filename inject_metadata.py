import os
import re

files_metadata = {
    "login.html": "<strong>Authentication Gateway.</strong> Log in to access the AquaSentinel Command Base, view the Global Intelligence Map, and submit marine debris reports. Different roles (User, Admin) unlock specific operational capabilities.",
    "dashboard.html": "<strong>Command Base.</strong> This dashboard provides a high-level summary of marine intelligence, tracking total reports, active ecosystem alerts, and critical risks. It acts as the central hub for the AquaSentinel project.",
    "map.html": "<strong>Global Intelligence Map.</strong> Visualizes spatial data including user reports, AI debris detections, and simulated environmental incidents. Use this to pinpoint hotspots and analyze geospatial risk distribution.",
    "profile.html": "<strong>Sentinel Profile.</strong> Manage your user identity, adjust interface preferences, and track your civilian impact score. Your data powers the community reporting matrix of AquaSentinel.",
    "admin.html": "<strong>Admin Tower & Simulation Engine.</strong> Restricted access. Administrators can broadcast tactical drills, generate simulated debris spills, and monitor system-wide alerts to verify platform readiness.",
    "location-risk.html": "<strong>Regional Risk Intelligence.</strong> Computes real-time risk scores (0-100) using live OpenWeather data. It maps temperature to Thermal Stress and wind to Dynamic Load, fusing them into a dynamic ecosystem threat assessment.",
    "ai-intelligence.html": "<strong>AI Marine Debris Intelligence.</strong> Upload imagery for deep-learning classification of debris types (e.g., Plastics, Ghost Nets). This module operates in both Simulated and Real inference modes to extract ecosystem signals."
}

card_template = """
                <!-- AQUASENTINEL PROJECT METADATA KNOWLEDGE LAYER -->
                <div class="glass-card project-knowledge-layer" style="margin-bottom: 2rem; border-left: 4px solid var(--accent-color); padding: 1.5rem;">
                    <div style="display: flex; align-items: flex-start; gap: 1rem;">
                        <div style="font-size: 1.5rem;">ℹ️</div>
                        <div>
                            <h4 style="color: var(--accent-color); margin-bottom: 0.3rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">About This Module</h4>
                            <p style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.5;">{content}</p>
                        </div>
                    </div>
                </div>
"""

frontend_dir = "frontend"

for filename, content in files_metadata.items():
    filepath = os.path.join(frontend_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
            
        if "PROJECT METADATA KNOWLEDGE LAYER" in html:
            continue
            
        # Try to inject after the opening <div class="container" style="margin-top: ..."> or similar
        # Fallback to injecting right after <div class="container">
        
        card_html = card_template.format(content=content)
        
        # We will look for <div class="container" (with or without extra classes/styles)
        # and inject inside it.
        match = re.search(r'(<div[^>]*class="[^"]*container[^"]*"[^>]*>)', html)
        if match:
            insertion_point = match.end()
            new_html = html[:insertion_point] + card_html + html[insertion_point:]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"Injected into {filename}")
        else:
            print(f"Could not find container in {filename}")
            
print("Done")
