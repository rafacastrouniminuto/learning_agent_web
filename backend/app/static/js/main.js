// Living Lab UNIMINUTO - Main JavaScript

class LearningAgent {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.sidebarVisible = true;
        this.currentConversation = [];
        this.currentMode = 'learning_path'; // Default to learning path mode
        this.generatedLearningPath = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeSidebar();
        this.checkAuth();
    }

    initializeSidebar() {
        const toggle = document.querySelector('.sidebar-toggle');
        if (toggle) {
            if (this.sidebarVisible) {
                toggle.classList.add('sidebar-visible');
                toggle.innerHTML = '←';
                toggle.title = 'Ocultar menú';
            } else {
                toggle.classList.remove('sidebar-visible');
                toggle.innerHTML = '→';
                toggle.title = 'Mostrar menú';
            }
        }
    }

    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Register form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Chat form
        const chatForm = document.getElementById('chatForm');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => this.handleChatSubmit(e));
        }

        // Action cards
        const actionCards = document.querySelectorAll('.action-card');
        actionCards.forEach(card => {
            card.addEventListener('click', (e) => this.handleActionCard(e));
        });

        // Chat input auto-resize
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('input', () => this.autoResizeTextarea(chatInput));
        }
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('.content-area');
        const toggle = document.querySelector('.sidebar-toggle');
        
        this.sidebarVisible = !this.sidebarVisible;
        
        if (this.sidebarVisible) {
            sidebar.classList.remove('hidden');
            content.classList.remove('expanded');
            toggle.classList.add('sidebar-visible');
            toggle.innerHTML = '←';
            toggle.title = 'Ocultar menú';
        } else {
            sidebar.classList.add('hidden');
            content.classList.add('expanded');
            toggle.classList.remove('sidebar-visible');
            toggle.innerHTML = '→';
            toggle.title = 'Mostrar menú';
        }
    }

    async checkAuth() {
        if (!this.token) {
            // Si no está en login o register page, redirigir a login
            if (!window.location.pathname.includes('login') && !window.location.pathname.includes('register')) {
                window.location.href = '/login';
            }
            return false;
        }

        try {
            const response = await fetch('/auth/me', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Authentication failed');
            }

            const user = await response.json();
            this.updateUserInfo(user);
            return true;
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('access_token');
            if (!window.location.pathname.includes('login') && !window.location.pathname.includes('register')) {
                window.location.href = '/login';
            }
            return false;
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        this.setLoading(submitBtn, true);

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.get('email'),
                    password: formData.get('password')
                })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('access_token', data.access_token);
                this.token = data.access_token;
                window.location.href = '/dashboard';
            } else {
                this.showError(data.detail || 'Error al iniciar sesión');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('Error de conexión. Intenta nuevamente.');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        this.setLoading(submitBtn, true);

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.get('email'),
                    password: formData.get('password'),
                    first_name: formData.get('first_name'),
                    last_name: formData.get('last_name')
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showSuccess('Cuenta creada exitosamente. Por favor inicia sesión.');
                // Redirect to login after successful registration
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                this.showError(data.detail || 'Error al crear la cuenta');
            }
        } catch (error) {
            console.error('Register error:', error);
            this.showError('Error de conexión. Intenta nuevamente.');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    async handleChatSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addMessageToChat('user', message);
        input.value = '';
        this.autoResizeTextarea(input);

        // Show typing indicator
        const typingIndicator = this.addTypingIndicator();

        try {
            await this.sendChatMessage(message);
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessageToChat('assistant', 'Lo siento, ocurrió un error. Intenta nuevamente.');
        } finally {
            typingIndicator.remove();
        }
    }

    async sendChatMessage(message) {
        console.log('Sending chat message:', message);
        
        try {
            const response = await fetch('/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },            body: JSON.stringify({
                message: message,
                conversation_history: this.currentConversation,
                mode: this.currentMode
            })
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            if (!response.ok) {
                console.error('Chat request failed with status:', response.status);
                const errorText = await response.text();
                console.error('Error response:', errorText);
                throw new Error(`Chat request failed: ${response.status} - ${errorText}`);
            }

            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = '';
            let messageElement = this.addMessageToChat('assistant', '');

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) {
                        console.log('Stream reading completed');
                        break;
                    }

                    const chunk = decoder.decode(value, { stream: true });
                    console.log('Received chunk:', JSON.stringify(chunk));
                    
                    // Split by lines and process each potential SSE line
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.trim() === '') continue; // Skip empty lines
                        
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.slice(6); // Remove 'data: ' prefix
                                console.log('Parsing JSON:', jsonStr);
                                const data = JSON.parse(jsonStr);
                                console.log('Parsed data:', data);
                                
                                if (data.error) {
                                    console.error('Stream error:', data.error);
                                    messageElement.textContent = `Error: ${data.error}`;
                                    throw new Error(data.error);
                                }
                                
                                if (data.type === 'learning_path_generated') {
                                    console.log('Learning path generated:', data.learning_path);
                                    this.generatedLearningPath = data.learning_path;
                                    this.showGeneratePathButton(messageElement);
                                    continue;
                                }
                                
                                if (data.done) {
                                    console.log('Stream completed by server');
                                    // Update conversation history
                                    this.currentConversation.push(
                                        { role: 'user', content: message },
                                        { role: 'assistant', content: assistantMessage }
                                    );
                                    return; // Exit the function
                                }
                                
                                if (data.content) {
                                    assistantMessage += data.content;
                                    messageElement.textContent = assistantMessage;
                                    this.scrollChatToBottom();
                                }
                            } catch (parseError) {
                                console.error('Error parsing JSON:', parseError, 'Line:', line);
                                // Don't throw here, continue processing other lines
                            }
                        }
                    }
                }
            } finally {
                reader.releaseLock();
            }
        } catch (error) {
            console.error('sendChatMessage error:', error);
            throw error; // Re-throw to be handled by caller
        }
    }

    addMessageToChat(role, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${role}`;
        messageElement.textContent = content;
        
        messagesContainer.appendChild(messageElement);
        this.scrollChatToBottom();
        
        return messageElement;
    }

    addTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        const indicator = document.createElement('div');
        indicator.className = 'chat-message assistant';
        indicator.innerHTML = '<div class="loading"></div>';
        messagesContainer.appendChild(indicator);
        this.scrollChatToBottom();
        return indicator;
    }

    scrollChatToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    handleActionCard(e) {
        const card = e.currentTarget;
        const action = card.dataset.action;

        switch (action) {
            case 'generate-path':
                window.location.href = '/chat';
                break;
            case 'view-paths':
                window.location.href = '/learning-paths';
                break;
            case 'mcp-tools':
                window.location.href = '/mcp-tools';
                break;
            default:
                console.log('Unknown action:', action);
        }
    }

    updateUserInfo(user) {
        const userNameElement = document.getElementById('userName');
        if (userNameElement) {
            const displayName = user.first_name 
                ? `${user.first_name} ${user.last_name || ''}`.trim()
                : user.email;
            userNameElement.textContent = displayName;
        }
    }

    setLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<div class="loading"></div> Cargando...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || 'Enviar';
        }
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            maxWidth: '400px',
            backgroundColor: type === 'error' ? '#ef4444' : 
                           type === 'success' ? '#10b981' : '#3b82f6'
        });

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    logout() {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    }

    showGeneratePathButton(messageElement) {
        // Create a button to generate the learning path
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'generate-path-container';
        buttonContainer.style.marginTop = '15px';
        
        const generateButton = document.createElement('button');
        generateButton.className = 'btn btn-primary generate-path-btn';
        generateButton.innerHTML = '🚀 Generar Ruta de Aprendizaje';
        generateButton.onclick = () => this.generateLearningPath();
        
        buttonContainer.appendChild(generateButton);
        messageElement.appendChild(buttonContainer);
        
        this.scrollChatToBottom();
    }
    
    async generateLearningPath() {
        if (!this.generatedLearningPath) {
            alert('No hay ruta de aprendizaje disponible');
            return;
        }
        
        try {
            // Store the learning path in sessionStorage to pass to learning-paths page
            sessionStorage.setItem('generatedLearningPath', JSON.stringify(this.generatedLearningPath));
            
            // Show success message
            this.addMessageToChat('assistant', '✅ ¡Ruta de aprendizaje generada exitosamente! Puedes verla en la sección "Rutas de Aprendizaje".');
            
            // Disable the button
            const button = document.querySelector('.generate-path-btn');
            if (button) {
                button.disabled = true;
                button.innerHTML = '✅ Ruta Generada';
                button.classList.add('disabled');
            }
            
        } catch (error) {
            console.error('Error generating learning path:', error);
            this.addMessageToChat('assistant', 'Error al generar la ruta de aprendizaje. Intenta nuevamente.');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.learningAgent = new LearningAgent();
});
