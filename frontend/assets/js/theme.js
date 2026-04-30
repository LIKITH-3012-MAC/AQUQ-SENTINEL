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
            if (widget.classList.contains('active')) {
                document.getElementById('chat-input').focus();
                this.loadChatHistory();
            }
        }
    },

    async loadChatHistory() {
        const sessionId = this.getChatSessionId();
        const box = document.getElementById('chat-box');
        if (box.children.length > 0) return; // Already loaded

        try {
            const history = await API.chatbot.history(sessionId);
            history.forEach(msg => {
                this.appendMessage('user', msg.user_message);
                this.appendMessage('ai', msg.bot_response);
            });
        } catch (err) {
            console.error("History fail", err);
        }
    },

    getChatSessionId() {
        let sid = localStorage.getItem('aquasentinel_chat_session');
        if (!sid) {
            sid = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('aquasentinel_chat_session', sid);
        }
        return sid;
    },

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const langSelect = document.getElementById('chat-lang-select');
        const msg = input.value.trim();
        
        if (!msg) return;

        this.appendMessage('user', msg);
        input.value = '';

        const typingId = 'typing-' + Date.now();
        this.appendMessage('ai', '...', typingId);

        try {
            const data = await API.chatbot.query({
                message: msg,
                session_id: this.getChatSessionId(),
                language: langSelect ? langSelect.value : 'English',
                location: 'Sector 7'
            });
            
            if (data.success) {
                document.getElementById(typingId).textContent = data.answer;
            } else {
                document.getElementById(typingId).textContent = "Error: " + (data.error || "Intelligence OS offline.");
            }
        } catch (err) {
            document.getElementById(typingId).textContent = "Critical: Connection to Command Base lost.";
        }
    },

    appendMessage(role, text, id = null) {
        const box = document.getElementById('chat-box');
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ' + role;
        msgDiv.style.cssText = role === 'user' 
            ? 'background: var(--accent-gradient); color: #000; padding: 0.8rem 1.2rem; border-radius: 18px 18px 0 18px; font-size: 0.85rem; align-self: flex-end; max-width: 85%; font-weight: 600; margin-bottom: 0.5rem;'
            : 'background: rgba(255,255,255,0.05); padding: 0.8rem 1.2rem; border-radius: 18px 18px 18px 0; font-size: 0.85rem; align-self: flex-start; max-width: 85%; border-left: 3px solid var(--accent-color); margin-bottom: 0.5rem;';
        
        if (id) msgDiv.id = id;
        msgDiv.textContent = text;
        box.appendChild(msgDiv);
        box.scrollTop = box.scrollHeight;
    },

    initAIAssistant() {
        const trigger = document.getElementById('ai-copilot-trigger');
        const input = document.getElementById('chat-input');
        const sendBtn = document.querySelector('.copilot-widget button');

        if (trigger) trigger.addEventListener('click', () => this.toggleAICopilot());
        if (sendBtn) sendBtn.addEventListener('click', () => this.sendMessage());
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => UI.init());
