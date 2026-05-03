# PROJECT KNOWLEDGE DESIGN REPORT

## Files Created
1. `backend/app/knowledge/project_metadata.json`: Core identity, mission, and purpose.
2. `backend/app/knowledge/project_features.json`: Detailed descriptions of modules (Dashboard, Map, Risk Intelligence, etc.).
3. `backend/app/knowledge/page_context.json`: Page-by-page breakdown of what each HTML view achieves and who can access it.
4. `backend/app/knowledge/role_capabilities.json`: Permissions and workflows for Users vs Admins.
5. `backend/app/knowledge/workflow_knowledge.json`: Data flow from reporting to alerts, and AI to action.
6. `backend/app/knowledge/ai_module_knowledge.json`: Deep dive into Simulated vs Real models, Debris Detection, and Ecosystem metrics.
7. `backend/app/knowledge/faq_knowledge.json`: Common Q&A mapping for the chatbot.

## Metadata Categories
The knowledge base is broken down into structured, machine-readable JSON elements covering: Identity, Features, Context, Roles, Workflows, AI Architecture, and FAQs.

## Page Mappings
I will inject contextual UI components (such as an "About this Page" tooltip or inline meta-cards) into:
- `login.html`, `register.html`: Clarifying what users unlock upon entry.
- `dashboard.html`: Explaining metrics and command center roles.
- `map.html`: Explaining layers, hotspots, and debris lines.
- `profile.html`: Explaining data privacy and activity impact.
- `report.html`: Explaining how civilian reports feed the AI.
- `admin.html`: Explaining the simulation engine.
- `location-risk.html`: Explaining the weather-integrated dynamic load and thermal stress.
- `ai-intelligence.html`: Explaining inference models and ecosystem signals.

## Chatbot Integration Strategy
The backend chatbot service (`backend/app/services/chatbot_service.py` or `copilot.py`) will be updated to load these JSON files into memory. When a user asks "What is this project?" or "How does the map work?", the chatbot will parse the intent, inject the relevant JSON knowledge into its system prompt, and return a highly accurate, role-aware, hallucination-free answer based purely on the actual architecture of AquaSentinel.
