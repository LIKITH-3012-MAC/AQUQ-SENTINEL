import re

with open("backend/app/services/chatbot_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "def get_system_prompt(self, user_role=\"user\", language=\"en\"):" in line:
        new_lines.append("""        import os
        import json
        knowledge_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "project_knowledge.json")
        project_context = ""
        if os.path.exists(knowledge_path):
            try:
                with open(knowledge_path, "r", encoding="utf-8") as fk:
                    project_context = f"\\n\\n[SYSTEM PROJECT KNOWLEDGE BASE]\\n{json.dumps(json.load(fk))}\\n\\nIMPORTANT RULE: Use the above structured metadata to answer questions about what AquaSentinel is, pages, risk, and AI modules. Be highly accurate to this data."
            except Exception:
                pass
""")

final_text = "".join(new_lines)
final_text = re.sub(r'(\"en\":.*?)(?=\",)', r'\1.{project_context}', final_text)
final_text = re.sub(r'(\"te\":.*?)(?=\",)', r'\1.{project_context}', final_text)
final_text = re.sub(r'(\"hi\":.*?)(?=\",)', r'\1.{project_context}', final_text)
final_text = re.sub(r'(\"ta\":.*?)(?=\",)', r'\1.{project_context}', final_text)
final_text = re.sub(r'(\"kn\":.*?)(?=\",)', r'\1.{project_context}', final_text)
final_text = re.sub(r'(\"ml\":.*?)(?=\")', r'\1.{project_context}', final_text)

with open("backend/app/services/chatbot_service.py", "w", encoding="utf-8") as f:
    f.write(final_text)

print("Patched successfully")
