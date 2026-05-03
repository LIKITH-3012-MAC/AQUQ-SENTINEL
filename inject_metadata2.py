import os
import re

files_metadata = {
    "register.html": "<strong>Sentinel Registration.</strong> Create an account to join the network. As an authenticated user, you can report marine debris, receive real-time alerts, and track your civilian impact.",
    "report.html": "<strong>Tactical Issue Report.</strong> Submit evidence of marine debris. Your report feeds directly into the PostgreSQL database, appears on the Global Map, and helps train our AI models.",
    "index.html": "<strong>AquaSentinel Portal.</strong> This is the public gateway to the Advanced Marine Debris & Regional Risk Intelligence Platform."
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
        
        card_html = card_template.format(content=content)
        
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
