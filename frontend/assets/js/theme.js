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



    toggleAICopilot() {
        const widget = document.getElementById('copilot-widget');
        if (widget) {
            widget.classList.toggle('active');
            if (widget.classList.contains('active')) {
                document.getElementById('chat-input').focus();
                this.loadChatHistory();
                this.renderSuggestionChips();
            }
        }
    },

    async loadChatHistory() {
        const sessionId = this.getChatSessionId();
        const box = document.getElementById('chat-box');
        if (box.children.length > 1) return; // Already loaded (initial message exists)

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

    async sendMessage(predefinedMsg = null) {
        const input = document.getElementById('chat-input');
        const langSelect = document.getElementById('chat-lang-select');
        const msg = predefinedMsg || input.value.trim();
        
        if (!msg) return;

        this.appendMessage('user', msg);
        if (!predefinedMsg) input.value = '';

        this.showTypingIndicator();

        try {
            const data = await API.chatbot.query({
                message: msg,
                session_id: this.getChatSessionId(),
                language: langSelect ? langSelect.value : 'English',
                location: 'Sector 7'
            });
            
            this.hideTypingIndicator();

            if (data.success) {
                this.appendMessage('ai', data.answer);
            } else {
                this.appendMessage('ai', "⚠️ Error: " + (data.error || "Intelligence OS offline."));
            }
        } catch (err) {
            this.hideTypingIndicator();
            this.appendMessage('ai', "🚨 Critical: Connection to Command Base lost.");
        }
    },

    showTypingIndicator() {
        const box = document.getElementById('chat-box');
        const indicator = document.createElement('div');
        indicator.id = 'ai-typing';
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span style="margin-left: 0.5rem">AquaSentinel is analyzing...</span>
        `;
        box.appendChild(indicator);
        box.scrollTop = box.scrollHeight;
    },

    hideTypingIndicator() {
        const indicator = document.getElementById('ai-typing');
        if (indicator) indicator.remove();
    },

    renderSuggestionChips() {
        const widget = document.getElementById('copilot-widget');
        let container = document.querySelector('.suggestion-container');
        
        if (!container) {
            container = document.createElement('div');
            container.className = 'suggestion-container';
            const footer = widget.querySelector('div[style*="border-top"]');
            widget.insertBefore(container, footer);
        }

        const chips = ["Check local ocean risk", "Explain map layers", "Report marine issue", "Show latest alerts"];
        container.innerHTML = chips.map(c => `<div class="suggestion-chip" onclick="UI.sendMessage('${c}')">${c}</div>`).join('');
    },

    appendMessage(role, text) {
        const box = document.getElementById('chat-box');
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ' + role;
        
        if (role === 'ai') {
            msgDiv.innerHTML = this.formatAIResponse(text);
        } else {
            msgDiv.textContent = text;
        }
        
        box.appendChild(msgDiv);
        box.scrollTop = box.scrollHeight;
    },

    formatAIResponse(text) {
        // Handle bolding first
        let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Split by lines to detect structure
        const lines = formatted.split('\n');
        let html = '';
        let listOpen = false;

        lines.forEach((line, index) => {
            const trimmed = line.trim();
            if (!trimmed) return;

            // Heading Detection (Ends with emoji or starts with one, or uses markdown #)
            if ((index === 0 && (trimmed.includes('👋') || trimmed.includes('Hello'))) || trimmed.startsWith('###')) {
                const cleanHeading = trimmed.replace(/###/g, '').trim();
                html += `<span class="ai-greeting">${cleanHeading}</span>`;
            } 
            // Section Detection (Starts with Emoji + Label or Markdown Heading)
            else if (/^([📊📍📝✅⚠️🤖🛠️ℹ️])/.test(trimmed) || trimmed.startsWith('##')) {
                if (listOpen) { html += '</ul>'; listOpen = false; }
                const cleanLine = trimmed.replace(/##/g, '').trim();
                const parts = cleanLine.split(':');
                if (parts.length > 1) {
                    html += `<div class="ai-section">
                                <div class="ai-section-label">${parts[0]}</div>
                                <div style="font-size: 0.9rem">${parts.slice(1).join(':')}</div>
                             </div>`;
                } else {
                    html += `<div class="ai-section"><div style="font-size: 0.9rem">${cleanLine}</div></div>`;
                }
            }
            // Bullet Points
            else if (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*')) {
                if (!listOpen) { html += '<ul class="ai-list">'; listOpen = true; }
                html += `<li class="ai-list-item">${trimmed.replace(/^[-•*]/, '').trim()}</li>`;
            }
            // Normal text
            else {
                if (listOpen) { html += '</ul>'; listOpen = false; }
                html += `<span class="ai-summary">${trimmed}</span>`;
            }
        });

        if (listOpen) html += '</ul>';
        
        return html || formatted;
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
