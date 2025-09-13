
/**
 * DevDuck UI Renderer with VAPI Voice Integration
 * 
 * Manages the frontend interactions and communicates with the backend API.
 */

let Vapi;

try {
    const vapiModule = require('@vapi-ai/web');
    Vapi = vapiModule.default || vapiModule;
    console.log('VAPI module loaded via require:', typeof Vapi);
} catch (error) {
    console.warn('VAPI module not found via require:', error.message);
    console.log('Will attempt to use CDN version from window.Vapi');
}
class DevDuckUI {
    constructor() {
    this.apiBase = 'http://localhost:8001';
    this.vapiPublicKey = '' // redacted... JS can't use env vars
    this.vapiAssistantId = '' // redacted... JS can't use env vars
        this.isListening = false;
        this.vapi = null;
        this.isCallActive = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadHistory();
        this.updateStatus('Ready');
        this.initializeVapi();
    }

    initializeElements() {
        this.voiceBtn = document.getElementById('voice-call-btn');
        this.historyDropdown = document.getElementById('history-dropdown');
        this.statusElement = document.getElementById('status');
        
        console.log('Elements initialized:');
        console.log('  voiceBtn:', this.voiceBtn);
        console.log('  historyDropdown:', this.historyDropdown);
        console.log('  statusElement:', this.statusElement);
    }

    initializeVapi() {
        console.log('=== VAPI Initialization Debug ===');
        console.log('window.Vapi:', typeof window.Vapi);
        console.log('Imported Vapi:', typeof Vapi);
        console.log('window.vapiLoaded:', window.vapiLoaded);
        console.log('window keys containing "vapi":', Object.keys(window).filter(k => k.toLowerCase().includes('vapi')));
        console.log('window keys containing "Vapi":', Object.keys(window).filter(k => k.includes('Vapi')));
        
        const VapiClass = Vapi || window.Vapi;
        
        console.log('VapiClass found:', !!VapiClass);
        console.log('VapiClass type:', typeof VapiClass);
        
        if (!VapiClass) {
            console.log('VAPI not available, retrying...');
            this.vapiRetryCount = (this.vapiRetryCount || 0) + 1;
            console.log(`Retry attempt: ${this.vapiRetryCount}/15`);

            if (this.vapiRetryCount < 15) {
                setTimeout(() => this.initializeVapi(), 3000);
                return;
            } else {
                console.error('VAPI failed to load after multiple attempts');
                console.log('Attempting manual fallback initialization...');
                this.attemptFallbackInitialization();
                return;
            }
        }

        try {
            console.log('VAPI found, attempting initialization...');
            console.log('Public key: ', this.vapiPublicKey);

            this.vapi = new VapiClass(this.vapiPublicKey);

            console.log('VAPI instance created successfully:', this.vapi);
            console.log('VAPI instance methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(this.vapi)));
            
            this.vapi.on('call-start', () => {
                console.log('VAPI call started');
                this.isCallActive = true;
                this.updateVoiceButton();
                this.updateStatus('🎤 Connected to DevDuck - Speak now!');
            });

            this.vapi.on('call-end', () => {
                console.log('VAPI call ended');
                this.isCallActive = false;
                this.updateVoiceButton();
                this.updateStatus('Call ended');
                setTimeout(() => this.loadHistory(), 1000);
            });

            this.vapi.on('speech-start', () => {
                console.log('Assistant started speaking');
                this.updateStatus('🦆 DevDuck is speaking...');
            });

            this.vapi.on('speech-end', () => {
                console.log('Assistant stopped speaking');
                this.updateStatus('🎤 Your turn to speak');
            });

            this.vapi.on('message', (message) => {
                console.log('VAPI message:', message);
                if (message.type === 'transcript') {
                    console.log(`${message.role}: ${message.transcript}`);
                }
            });

            this.vapi.on('error', (error) => {
                console.error('VAPI error:', error);
                this.updateStatus(`Error: ${error.message}`);
                this.isCallActive = false;
                this.updateVoiceButton();
            });

            console.log('VAPI initialized successfully');
            this.updateStatus('🎤 Voice ready! Click "Talk to DevDuck"');
        } catch (error) {
            console.error('Failed to initialize VAPI:', error);
            console.error('Error stack:', error.stack);
            this.updateStatus('Voice feature unavailable - Initialization failed');
        }
    }

    attemptFallbackInitialization() {
        console.log('Attempting fallback VAPI initialization...');
        this.updateStatus('Attempting to load voice SDK...');
        
        const fallbackScript = document.createElement('script');
        fallbackScript.src = 'https://unpkg.com/@vapi-ai/web@latest/dist/index.js';
        fallbackScript.onload = () => {
            console.log('Fallback VAPI SDK loaded');
            setTimeout(() => this.initializeVapi(), 1000);
        };
        fallbackScript.onerror = () => {
            console.error('Fallback VAPI SDK failed to load');
            this.updateStatus('Voice feature unavailable - Cannot load SDK');
        };
        
        document.head.appendChild(fallbackScript);
    }    setupEventListeners() {
        if (this.voiceBtn) {
            this.voiceBtn.addEventListener('click', () => this.toggleVoiceCall());
            console.log('Voice button event listener added');
        } else {
            console.error('Voice button not found!');
        }
        
        if (this.historyDropdown) {
            this.historyDropdown.addEventListener('change', (e) => this.showHistoryItem(e.target.value));
        }
        
        setInterval(() => this.loadHistory(), 5000);
    }

    async toggleVoiceCall() {
        console.log('toggleVoiceCall called');
        console.log('this.vapi:', this.vapi);

        if (!this.vapi) {
            console.log('VAPI not available');
            this.updateStatus('Voice feature not available - VAPI not initialized');
            return;
        }

        try {
            if (this.isCallActive) {
                console.log('Stopping call...');
                await this.vapi.stop();
                this.updateStatus('Ending call...');
            } else {
                console.log('Starting call...');
                this.updateStatus('Starting voice call...');

                // Call backend to toggle listening ON
                try {
                    const response = await fetch(`${this.apiBase}/listening/toggle`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    if (!response.ok) {
                        throw new Error(`API error: ${response.status}`);
                    }
                    const data = await response.json();
                    this.isListening = data.isListening;
                    this.updateStatus(this.isListening ? 'Listening...' : 'Not listening');
                } catch (apiErr) {
                    console.error('Error toggling listening on backend:', apiErr);
                    this.updateStatus('Warning: Could not notify backend');
                }

                await this.vapi.start(this.vapiAssistantId);
            }
        } catch (error) {
            console.error('Voice call error:', error);
            this.updateStatus(`Call error: ${error.message}`);
            this.isCallActive = false;
            this.updateVoiceButton();
        }
    }

    updateVoiceButton() {
        if (!this.voiceBtn) return;
        
        if (this.isCallActive) {
            this.voiceBtn.textContent = '🔴 End Call';
            this.voiceBtn.classList.add('calling');
        } else {
            this.voiceBtn.textContent = '🎤 Talk to DevDuck';
            this.voiceBtn.classList.remove('calling');
        }
    }

    async toggleListening() {
        try {
            this.updateStatus('Toggling...');
            
            const response = await fetch(`${this.apiBase}/listening/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.isListening = data.isListening;
            
            this.updateToggleButton();
            this.updateStatus(this.isListening ? 'Listening...' : 'Stopped');
            
            setTimeout(() => this.loadHistory(), 500);
            
        } catch (error) {
            console.error('Error toggling listening:', error);
            this.updateStatus('Error: Could not connect to API');
        }
    }

    updateToggleButton() {
        if (this.isListening) {
            this.toggleBtn.textContent = 'Stop Listening';
            this.toggleBtn.classList.add('listening');
        } else {
            this.toggleBtn.textContent = 'Start Listening';
            this.toggleBtn.classList.remove('listening');
        }
    }

    async loadHistory() {
        try {
            const response = await fetch(`${this.apiBase}/history`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.populateHistoryDropdown(data.history || []);
            
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    populateHistoryDropdown(history) {
        this.historyDropdown.innerHTML = '<option value="">-- Select a conversation --</option>';
        
        if (history.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No history available';
            option.disabled = true;
            this.historyDropdown.appendChild(option);
            return;
        }

        history.forEach((item, index) => {
            const option = document.createElement('option');
            option.value = index;
            
            const time = new Date(item.time).toLocaleTimeString();
            const eventText = item.event || 'Event';
            option.textContent = `${time} - ${eventText}`;
            
            this.historyDropdown.appendChild(option);
        });
    }

    showHistoryItem(index) {
        if (!index) return;
        
        this.updateStatus(`Selected history item #${parseInt(index) + 1}`);
    }

    updateStatus(message) {
        this.statusElement.textContent = message;
        
        this.statusElement.classList.remove('listening', 'error');
        
        if (message.includes('Error')) {
            this.statusElement.classList.add('error');
        } else if (message.includes('Listening')) {
            this.statusElement.classList.add('listening');
        }
    }

    async checkServerStatus() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            return response.ok;
        } catch (error) {
            console.warn('Server health check failed:', error.message);
            return false;
        }
    }

    fetchCodeSnippet(filePath) {
        const url = `${this.apiBase}/get_code_snippet`;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: 'get_code_snippet',
                parameters: { file_path: filePath },
            }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error fetching code snippet: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    this.displayCodeSnippet(data.code_snippet);
                } else {
                    console.error('Failed to fetch code snippet:', data);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    displayCodeSnippet(codeSnippet) {
        const snippetElement = document.getElementById('code-snippet-display');
        snippetElement.textContent = codeSnippet;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, checking for VAPI...');
    console.log('window.Vapi:', typeof window.Vapi);
    console.log('Voice button element:', document.getElementById('voice-call-btn'));
    
    const app = new DevDuckUI();
    
    app.checkServerStatus().then(isOnline => {
        if (!isOnline) {
            app.updateStatus('Warning: API server not available');
        }
    }).catch(error => {
        console.error('Server check failed:', error);
        app.updateStatus('Warning: Could not check API server status');
    });
});
