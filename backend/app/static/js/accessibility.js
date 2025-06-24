/**
 * Módulo de Accesibilidad para Discapacidad Visual
 * Living Lab UNIMINUTO - Learning Agent Web
 */

class AccessibilityManager {
    constructor() {
        this.settings = {
            contrastMode: 'normal',
            fontSize: 'medium',
            screenReaderEnabled: false,
            voiceNavigationEnabled: false,
            audioDescriptionsEnabled: false
        };
        
        this.voiceCommands = new Map();
        this.speechSynthesis = window.speechSynthesis;
        this.recognition = null;
        this.isListening = false;
        
        this.init();
    }

    /**
     * Inicializa el módulo de accesibilidad
     */
    init() {
        this.loadSettings();
        this.initializeVoices();
        this.createAccessibilityPanel();
        this.setupKeyboardNavigation();
        this.setupVoiceNavigation();
        this.setupSkipLinks();
        this.setupLiveRegion();
        this.applyStoredSettings();
        
        console.log('🔧 Módulo de accesibilidad inicializado');
    }

    /**
     * Inicializa las voces de síntesis de voz con mejor detección
     */
    initializeVoices() {
        if (!this.speechSynthesis) {
            console.warn('⚠️ Síntesis de voz no disponible en este navegador');
            return;
        }

        const loadVoices = () => {
            const voices = this.speechSynthesis.getVoices();
            
            if (voices.length === 0) {
                console.warn('⚠️ No hay voces disponibles en este navegador');
                return;
            }

            // Analizar voces disponibles
            console.log('📋 Análisis de voces disponibles:');
            console.table(voices.map(voice => ({
                name: voice.name,
                lang: voice.lang,
                localService: voice.localService,
                default: voice.default
            })));

            // Clasificar voces en español
            const spanishVoices = voices.filter(voice => {
                const lang = voice.lang.toLowerCase();
                const name = voice.name.toLowerCase();
                return lang.startsWith('es') || 
                       name.includes('spanish') || 
                       name.includes('español') ||
                       name.includes('castilian') ||
                       name.includes('castellano');
            });

            const nativeSpanishVoices = spanishVoices.filter(voice => voice.localService);
            const onlineSpanishVoices = spanishVoices.filter(voice => !voice.localService);

            console.log('🗣️ Voces en español encontradas:');
            console.log('  - Nativas/Locales:', nativeSpanishVoices.length);
            console.log('  - En línea/Cloud:', onlineSpanishVoices.length);
            console.log('  - Total:', spanishVoices.length);

            if (nativeSpanishVoices.length > 0) {
                console.log('✅ Voces nativas en español:', nativeSpanishVoices.map(v => `${v.name} (${v.lang})`));
            }

            if (onlineSpanishVoices.length > 0) {
                console.log('🌐 Voces en línea en español:', onlineSpanishVoices.map(v => `${v.name} (${v.lang})`));
            }

            if (spanishVoices.length === 0) {
                console.warn('⚠️ NO se encontraron voces en español');
                console.log('Voces disponibles:', voices.map(v => `${v.name} (${v.lang})`));
                
                // Mostrar advertencia al usuario
                this.showVoiceWarning();
            } else {
                console.log('✅ Síntesis de voz en español configurada correctamente');
            }
        };

        // Cargar voces inmediatamente si están disponibles
        loadVoices();
        
        // También escuchar el evento de cambio de voces (para algunos navegadores)
        if (this.speechSynthesis.addEventListener) {
            this.speechSynthesis.addEventListener('voiceschanged', loadVoices);
        } else {
            // Fallback para navegadores antiguos
            this.speechSynthesis.onvoiceschanged = loadVoices;
        }

        // Verificar periódicamente si las voces han cargado (fallback)
        let checkCount = 0;
        const checkVoices = setInterval(() => {
            if (this.speechSynthesis.getVoices().length > 0 || checkCount >= 10) {
                clearInterval(checkVoices);
                if (checkCount >= 10) {
                    console.warn('⚠️ Timeout esperando carga de voces');
                }
            }
            checkCount++;
        }, 500);
    }

    /**
     * Carga configuraciones guardadas
     */
    loadSettings() {
        const stored = localStorage.getItem('accessibility-settings');
        if (stored) {
            this.settings = { ...this.settings, ...JSON.parse(stored) };
        }
    }

    /**
     * Guarda configuraciones
     */
    saveSettings() {
        localStorage.setItem('accessibility-settings', JSON.stringify(this.settings));
        this.announceToScreenReader('Configuración de accesibilidad guardada');
    }

    /**
     * Crea el panel de accesibilidad
     */
    createAccessibilityPanel() {
        // Skip links
        const skipLinks = document.createElement('a');
        skipLinks.href = '#main-content';
        skipLinks.className = 'skip-links';
        skipLinks.textContent = 'Saltar al contenido principal (Alt+S)';
        skipLinks.setAttribute('accesskey', 's');
        document.body.insertBefore(skipLinks, document.body.firstChild);

        // Botón flotante
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'accessibility-toggle';
        toggleBtn.innerHTML = '<i class="fas fa-universal-access" aria-hidden="true"></i>';
        toggleBtn.setAttribute('aria-label', 'Abrir panel de accesibilidad');
        toggleBtn.setAttribute('title', 'Panel de Accesibilidad (Alt+A)');
        toggleBtn.addEventListener('click', () => this.togglePanel());
        
        // Panel principal
        const panel = document.createElement('div');
        panel.className = 'accessibility-panel';
        panel.id = 'accessibility-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-labelledby', 'accessibility-title');
        panel.setAttribute('aria-hidden', 'true');
        
        panel.innerHTML = `
            <h3 id="accessibility-title">
                <i class="fas fa-universal-access" aria-hidden="true"></i>
                Configuración de Accesibilidad
            </h3>
            
            <div class="accessibility-controls">
                <!-- Contraste -->
                <div class="control-group">
                    <label for="contrast-controls">Modo de Contraste:</label>
                    <div class="control-buttons" id="contrast-controls" role="radiogroup" aria-labelledby="contrast-label">
                        <button class="accessibility-btn" data-contrast="normal" role="radio" aria-checked="true">
                            Normal
                        </button>
                        <button class="accessibility-btn" data-contrast="high" role="radio" aria-checked="false">
                            Alto Contraste
                        </button>
                        <button class="accessibility-btn" data-contrast="yellow-black" role="radio" aria-checked="false">
                            Amarillo/Negro
                        </button>
                        <button class="accessibility-btn" data-contrast="blue-white" role="radio" aria-checked="false">
                            Azul/Blanco
                        </button>
                    </div>
                </div>

                <!-- Tamaño de fuente -->
                <div class="control-group">
                    <label for="font-controls">Tamaño de Texto:</label>
                    <div class="control-buttons" id="font-controls" role="radiogroup">
                        <button class="accessibility-btn" data-font="small" role="radio" aria-checked="false">
                            Pequeño
                        </button>
                        <button class="accessibility-btn" data-font="medium" role="radio" aria-checked="true">
                            Normal
                        </button>
                        <button class="accessibility-btn" data-font="large" role="radio" aria-checked="false">
                            Grande
                        </button>
                        <button class="accessibility-btn" data-font="extra-large" role="radio" aria-checked="false">
                            Muy Grande
                        </button>
                    </div>
                </div>

                <!-- Herramientas -->
                <div class="control-group">
                    <label>Herramientas de Asistencia:</label>
                    <div class="control-buttons">
                        <button class="accessibility-btn" id="screen-reader-btn" aria-pressed="false">
                            <i class="fas fa-volume-up" aria-hidden="true"></i>
                            Lector de Pantalla
                        </button>
                        <button class="accessibility-btn" id="voice-nav-btn" aria-pressed="false">
                            <i class="fas fa-microphone" aria-hidden="true"></i>
                            Navegación por Voz
                        </button>
                        <button class="accessibility-btn" id="keyboard-help-btn">
                            <i class="fas fa-keyboard" aria-hidden="true"></i>
                            Atajos de Teclado
                        </button>
                    </div>
                </div>

                <!-- Acciones -->
                <div class="control-group">
                    <div class="control-buttons">
                        <button class="accessibility-btn" id="reset-btn">
                            <i class="fas fa-undo" aria-hidden="true"></i>
                            Restablecer
                        </button>
                        <button class="accessibility-btn" id="close-panel-btn">
                            <i class="fas fa-times" aria-hidden="true"></i>
                            Cerrar Panel
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(toggleBtn);
        document.body.appendChild(panel);

        this.setupPanelEvents();
    }

    /**
     * Configura eventos del panel
     */
    setupPanelEvents() {
        // Contraste
        document.querySelectorAll('[data-contrast]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.target.dataset.contrast;
                this.setContrastMode(mode);
            });
        });

        // Tamaño de fuente
        document.querySelectorAll('[data-font]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const size = e.target.dataset.font;
                this.setFontSize(size);
            });
        });

        // Screen reader
        document.getElementById('screen-reader-btn').addEventListener('click', () => {
            this.toggleScreenReader();
        });

        // Navegación por voz
        document.getElementById('voice-nav-btn').addEventListener('click', () => {
            this.toggleVoiceNavigation();
        });

        // Ayuda de teclado
        document.getElementById('keyboard-help-btn').addEventListener('click', () => {
            this.showKeyboardHelp();
        });

        // Restablecer
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetSettings();
        });

        // Cerrar panel
        document.getElementById('close-panel-btn').addEventListener('click', () => {
            this.togglePanel();
        });

        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const panel = document.getElementById('accessibility-panel');
                if (panel.classList.contains('open')) {
                    this.togglePanel();
                }
            }
        });
    }

    /**
     * Alterna la visibilidad del panel
     */
    togglePanel() {
        const panel = document.getElementById('accessibility-panel');
        const isOpen = panel.classList.toggle('open');
        
        panel.setAttribute('aria-hidden', !isOpen);
        
        if (isOpen) {
            panel.querySelector('button').focus();
            this.announceToScreenReader('Panel de accesibilidad abierto');
        } else {
            document.querySelector('.accessibility-toggle').focus();
            this.announceToScreenReader('Panel de accesibilidad cerrado');
        }
    }

    /**
     * Establece el modo de contraste
     */
    setContrastMode(mode) {
        // Remover clases existentes
        document.body.classList.remove('contrast-normal', 'contrast-high', 'contrast-yellow-black', 'contrast-blue-white');
        
        // Aplicar nueva clase
        document.body.classList.add(`contrast-${mode}`);
        
        // Actualizar configuración
        this.settings.contrastMode = mode;
        this.saveSettings();
        
        // Actualizar botones
        document.querySelectorAll('[data-contrast]').forEach(btn => {
            const isActive = btn.dataset.contrast === mode;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-checked', isActive);
        });
        
        this.showAccessibilityFeedback(`Modo de contraste: ${this.getContrastLabel(mode)}`);
        this.announceToScreenReader(`Modo de contraste cambiado a ${this.getContrastLabel(mode)}`);
    }

    /**
     * Establece el tamaño de fuente
     */
    setFontSize(size) {
        // Remover clases existentes
        document.body.classList.remove('font-small', 'font-medium', 'font-large', 'font-extra-large');
        
        // Aplicar nueva clase
        document.body.classList.add(`font-${size}`);
        
        // Actualizar configuración
        this.settings.fontSize = size;
        this.saveSettings();
        
        // Actualizar botones
        document.querySelectorAll('[data-font]').forEach(btn => {
            const isActive = btn.dataset.font === size;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-checked', isActive);
        });
        
        this.showAccessibilityFeedback(`Tamaño de texto: ${this.getFontSizeLabel(size)}`);
        this.announceToScreenReader(`Tamaño de texto cambiado a ${this.getFontSizeLabel(size)}`);
    }

    /**
     * Alterna el lector de pantalla
     */
    toggleScreenReader() {
        this.settings.screenReaderEnabled = !this.settings.screenReaderEnabled;
        this.saveSettings();
        
        const btn = document.getElementById('screen-reader-btn');
        btn.classList.toggle('active', this.settings.screenReaderEnabled);
        btn.setAttribute('aria-pressed', this.settings.screenReaderEnabled);
        
        if (this.settings.screenReaderEnabled) {
            this.enableScreenReaderFeatures();
            this.announceToScreenReader('Lector de pantalla activado. Las páginas se leerán automáticamente.');
        } else {
            this.disableScreenReaderFeatures();
            this.announceToScreenReader('Lector de pantalla desactivado');
        }
    }

    /**
     * Alterna la navegación por voz
     */
    toggleVoiceNavigation() {
        this.settings.voiceNavigationEnabled = !this.settings.voiceNavigationEnabled;
        this.saveSettings();
        
        const btn = document.getElementById('voice-nav-btn');
        btn.classList.toggle('active', this.settings.voiceNavigationEnabled);
        btn.setAttribute('aria-pressed', this.settings.voiceNavigationEnabled);
        
        if (this.settings.voiceNavigationEnabled) {
            this.startVoiceRecognition();
            this.announceToScreenReader('Navegación por voz activada. Diga comandos como "ir dashboard" o "abrir menú"');
        } else {
            this.stopVoiceRecognition();
            this.announceToScreenReader('Navegación por voz desactivada');
        }
    }

    /**
     * Configura navegación por teclado
     */
    setupKeyboardNavigation() {
        // Atajos globales
        document.addEventListener('keydown', (e) => {
            if (e.altKey) {
                switch(e.key) {
                    case 'a':
                    case 'A':
                        e.preventDefault();
                        this.togglePanel();
                        break;
                    case '1':
                        e.preventDefault();
                        this.navigateTo('/dashboard');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateTo('/chat');
                        break;
                    case '3':
                        e.preventDefault();
                        this.navigateTo('/learning-paths');
                        break;
                    case '4':
                        e.preventDefault();
                        this.navigateTo('/mcp-tools');
                        break;
                    case 'm':
                    case 'M':
                        e.preventDefault();
                        this.toggleSidebar();
                        break;
                    case 'c':
                    case 'C':
                        e.preventDefault();
                        this.cycleContrastMode();
                        break;
                    case 'f':
                    case 'F':
                        e.preventDefault();
                        this.cycleFontSize();
                        break;
                    case 'r':
                    case 'R':
                        e.preventDefault();
                        this.toggleScreenReader();
                        break;
                    case 'v':
                    case 'V':
                        e.preventDefault();
                        this.toggleVoiceNavigation();
                        break;
                    case '/':
                        e.preventDefault();
                        this.showKeyboardHelp();
                        break;
                }
            }
        });

        // Mejorar foco visible
        document.addEventListener('focusin', (e) => {
            e.target.classList.add('keyboard-navigation');
        });

        document.addEventListener('focusout', (e) => {
            e.target.classList.remove('keyboard-navigation');
        });
    }

    /**
     * Configura navegación por voz
     */
    setupVoiceNavigation() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Reconocimiento de voz no soportado en este navegador');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        this.recognition.lang = 'es-ES';

        this.recognition.onresult = (event) => {
            const command = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
            this.processVoiceCommand(command);
        };

        this.recognition.onerror = (event) => {
            console.error('Error en reconocimiento de voz:', event.error);
            if (event.error === 'not-allowed') {
                this.announceToScreenReader('Permiso de micrófono denegado. Active el micrófono para usar navegación por voz.');
            }
        };

        // Comandos de voz
        this.voiceCommands = new Map([
            ['ir dashboard', () => this.navigateTo('/dashboard')],
            ['ir chat', () => this.navigateTo('/chat')],
            ['ir rutas', () => this.navigateTo('/learning-paths')],
            ['ir herramientas', () => this.navigateTo('/mcp-tools')],
            ['abrir menú', () => this.toggleSidebar()],
            ['cerrar menú', () => this.closeSidebar()],
            ['siguiente', () => this.focusNext()],
            ['anterior', () => this.focusPrevious()],
            ['activar', () => this.clickFocused()],
            ['buscar', () => this.focusSearch()],
            ['ayuda', () => this.showKeyboardHelp()],
            ['leer página', () => this.readPage()],
            ['parar lectura', () => this.stopReading()],
            ['contraste alto', () => this.setContrastMode('high')],
            ['contraste normal', () => this.setContrastMode('normal')],
            ['texto grande', () => this.setFontSize('large')],
            ['texto normal', () => this.setFontSize('medium')]
        ]);
    }

    /**
     * Procesa comandos de voz
     */
    processVoiceCommand(command) {
        console.log('Comando de voz recibido:', command);
        
        // Buscar comando exacto
        if (this.voiceCommands.has(command)) {
            this.voiceCommands.get(command)();
            this.announceToScreenReader(`Comando ejecutado: ${command}`);
            return;
        }

        // Buscar comandos parciales
        for (const [key, action] of this.voiceCommands) {
            if (command.includes(key) || key.includes(command)) {
                action();
                this.announceToScreenReader(`Comando ejecutado: ${key}`);
                return;
            }
        }

        this.announceToScreenReader(`Comando no reconocido: ${command}. Diga "ayuda" para ver comandos disponibles.`);
    }

    /**
     * Inicia reconocimiento de voz
     */
    startVoiceRecognition() {
        if (this.recognition && !this.isListening) {
            try {
                this.recognition.start();
                this.isListening = true;
                this.showAccessibilityFeedback('Navegación por voz activada - Escuchando...');
            } catch (error) {
                console.error('Error iniciando reconocimiento de voz:', error);
            }
        }
    }

    /**
     * Detiene reconocimiento de voz
     */
    stopVoiceRecognition() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            this.showAccessibilityFeedback('Navegación por voz desactivada');
        }
    }

    /**
     * Configura skip links
     */
    setupSkipLinks() {
        // Marcar contenido principal
        const mainContent = document.querySelector('main') || document.querySelector('.content-area');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }
    }

    /**
     * Configura región live para screen readers
     */
    setupLiveRegion() {
        const liveRegion = document.createElement('div');
        liveRegion.className = 'live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.id = 'accessibility-live-region';
        document.body.appendChild(liveRegion);
    }

    /**
     * Anuncia mensajes a screen readers
     */
    announceToScreenReader(message) {
        const liveRegion = document.getElementById('accessibility-live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            
            // Limpiar después de 1 segundo
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }

        // También usar síntesis de voz si está habilitada
        if (this.settings.screenReaderEnabled && this.speechSynthesis) {
            this.speak(message);
        }
    }

    /**
     * Síntesis de voz mejorada con mejor detección de idioma español
     */
    speak(text) {
        if (!this.speechSynthesis) {
            console.warn('⚠️ Síntesis de voz no disponible en este navegador');
            return;
        }

        // Cancelar cualquier speech anterior
        this.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Configurar parámetros de voz
        utterance.rate = 0.8;  // Reducir velocidad para mejor comprensión
        utterance.pitch = 1;
        utterance.volume = 1;
        
        // Obtener voces disponibles
        const voices = this.speechSynthesis.getVoices();
        
        // Estrategia de selección de voz en español más robusta
        let selectedVoice = null;
        
        // 1. Buscar voces nativas específicas de español
        const nativeSpanishVoices = voices.filter(voice => {
            const lang = voice.lang.toLowerCase();
            const name = voice.name.toLowerCase();
            return (
                // Códigos de idioma específicos
                lang === 'es-es' || lang === 'es-mx' || lang === 'es-ar' || 
                lang === 'es-co' || lang === 'es-pe' || lang === 'es-ve' ||
                lang === 'es-cl' || lang === 'es-uy' || lang === 'es-ec' ||
                // Nombres que incluyen "español" o "castilian"
                name.includes('español') || name.includes('castilian') ||
                name.includes('castellano') || name.includes('spain') ||
                name.includes('mexico') || name.includes('argentina') ||
                name.includes('colombia')
            ) && voice.localService; // Preferir voces locales/nativas
        });
        
        // 2. Si no hay nativas, buscar cualquier voz que empiece con 'es'
        const anySpanishVoices = voices.filter(voice => 
            voice.lang.toLowerCase().startsWith('es')
        );
        
        // 3. Como último recurso, buscar por nombre
        const nameBasedSpanishVoices = voices.filter(voice => {
            const name = voice.name.toLowerCase();
            return name.includes('spanish') || name.includes('español') ||
                   name.includes('maria') || name.includes('jorge') ||
                   name.includes('carmen') || name.includes('diego');
        });
        
        // Seleccionar la mejor voz disponible
        if (nativeSpanishVoices.length > 0) {
            selectedVoice = nativeSpanishVoices[0];
            utterance.lang = selectedVoice.lang;
            console.log('🗣️ Usando voz nativa en español:', selectedVoice.name, selectedVoice.lang);
        } else if (anySpanishVoices.length > 0) {
            selectedVoice = anySpanishVoices[0];
            utterance.lang = selectedVoice.lang;
            console.log('🗣️ Usando voz en español:', selectedVoice.name, selectedVoice.lang);
        } else if (nameBasedSpanishVoices.length > 0) {
            selectedVoice = nameBasedSpanishVoices[0];
            utterance.lang = 'es-ES'; // Forzar idioma español
            console.log('🗣️ Usando voz con nombre español:', selectedVoice.name, 'forzando idioma es-ES');
        } else {
            // Sin voces en español, forzar configuración de idioma
            utterance.lang = 'es-ES';
            console.warn('⚠️ Sin voces en español disponibles. Forzando idioma es-ES con voz por defecto');
            console.log('Voces disponibles:', voices.map(v => `${v.name} (${v.lang})`));
        }
        
        // Asignar voz seleccionada
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
        
        // Eventos para depuración
        utterance.onstart = () => {
            console.log('🎤 Iniciando síntesis de voz:', {
                text: text.substring(0, 50) + '...',
                voice: selectedVoice ? selectedVoice.name : 'por defecto',
                lang: utterance.lang
            });
        };
        
        utterance.onerror = (event) => {
            console.error('❌ Error en síntesis de voz:', event.error);
        };
        
        utterance.onend = () => {
            console.log('✅ Síntesis de voz completada');
        };
        
        // Ejecutar síntesis
        try {
            this.speechSynthesis.speak(utterance);
        } catch (error) {
            console.error('❌ Error al ejecutar síntesis de voz:', error);
        }
    }

    /**
     * Aplica configuraciones guardadas
     */
    applyStoredSettings() {
        this.setContrastMode(this.settings.contrastMode);
        this.setFontSize(this.settings.fontSize);
        
        if (this.settings.screenReaderEnabled) {
            this.toggleScreenReader();
        }
        
        if (this.settings.voiceNavigationEnabled) {
            this.toggleVoiceNavigation();
        }
    }

    /**
     * Muestra feedback de accesibilidad
     */
    showAccessibilityFeedback(message) {
        let indicator = document.querySelector('.accessibility-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'accessibility-indicator';
            document.body.appendChild(indicator);
        }
        
        indicator.textContent = message;
        indicator.classList.add('show');
        
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 3000);
    }

    /**
     * Funciones de utilidad
     */
    getContrastLabel(mode) {
        const labels = {
            'normal': 'Normal',
            'high': 'Alto Contraste',
            'yellow-black': 'Amarillo sobre Negro',
            'blue-white': 'Azul sobre Blanco'
        };
        return labels[mode] || mode;
    }

    getFontSizeLabel(size) {
        const labels = {
            'small': 'Pequeño',
            'medium': 'Normal',
            'large': 'Grande',
            'extra-large': 'Muy Grande'
        };
        return labels[size] || size;
    }

    navigateTo(path) {
        window.location.href = path;
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
    }

    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.add('collapsed');
        }
    }

    focusNext() {
        const focusable = this.getFocusableElements();
        const current = document.activeElement;
        const currentIndex = Array.from(focusable).indexOf(current);
        const nextIndex = (currentIndex + 1) % focusable.length;
        focusable[nextIndex].focus();
    }

    focusPrevious() {
        const focusable = this.getFocusableElements();
        const current = document.activeElement;
        const currentIndex = Array.from(focusable).indexOf(current);
        const prevIndex = currentIndex === 0 ? focusable.length - 1 : currentIndex - 1;
        focusable[prevIndex].focus();
    }

    getFocusableElements() {
        return document.querySelectorAll(
            'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
    }

    clickFocused() {
        const focused = document.activeElement;
        if (focused && (focused.tagName === 'BUTTON' || focused.tagName === 'A')) {
            focused.click();
        }
    }

    focusSearch() {
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="buscar"], input[placeholder*="Buscar"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    readPage() {
        if (this.speechSynthesis) {
            const content = document.querySelector('main, .content-area');
            if (content) {
                const text = content.textContent || content.innerText;
                this.speak(text);
            }
        }
    }

    stopReading() {
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
        }
    }

    cycleContrastMode() {
        const modes = ['normal', 'high', 'yellow-black', 'blue-white'];
        const currentIndex = modes.indexOf(this.settings.contrastMode);
        const nextIndex = (currentIndex + 1) % modes.length;
        this.setContrastMode(modes[nextIndex]);
    }

    cycleFontSize() {
        const sizes = ['small', 'medium', 'large', 'extra-large'];
        const currentIndex = sizes.indexOf(this.settings.fontSize);
        const nextIndex = (currentIndex + 1) % sizes.length;
        this.setFontSize(sizes[nextIndex]);
    }

    showKeyboardHelp() {
        const helpContent = `
            <h3>Atajos de Teclado Disponibles</h3>
            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 10px; font-size: 0.9em;">
                <strong>Navegación:</strong>
                <span>Tab / Shift+Tab - Navegar elementos</span>
                <strong>Alt + 1:</strong>
                <span>Ir al Dashboard</span>
                <strong>Alt + 2:</strong>
                <span>Ir al Chat</span>
                <strong>Alt + 3:</strong>
                <span>Ir a Rutas de Aprendizaje</span>
                <strong>Alt + 4:</strong>
                <span>Ir a Herramientas MCP</span>
                <strong>Alt + A:</strong>
                <span>Abrir Panel de Accesibilidad</span>
                <strong>Alt + C:</strong>
                <span>Cambiar Modo de Contraste</span>
                <strong>Alt + F:</strong>
                <span>Cambiar Tamaño de Fuente</span>
                <strong>Alt + R:</strong>
                <span>Activar/Desactivar Lector de Pantalla</span>
                <strong>Alt + V:</strong>
                <span>Activar/Desactivar Navegación por Voz</span>
                <strong>Alt + M:</strong>
                <span>Abrir/Cerrar Menú Lateral</span>
                <strong>Escape:</strong>
                <span>Cerrar Panel Actual</span>
            </div>
        `;
        
        this.showModal('Ayuda de Teclado', helpContent);
    }

    showModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'accessibility-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'modal-title');
        modal.setAttribute('aria-modal', 'true');
        
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modal-title">${title}</h2>
                    <button class="modal-close" aria-label="Cerrar modal">×</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    <button class="accessibility-btn modal-close">Cerrar</button>
                </div>
            </div>
        `;
        
        // Estilos inline para el modal
        const style = document.createElement('style');
        style.textContent = `
            .accessibility-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 2000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
            }
            .modal-content {
                background: white;
                border-radius: 8px;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                position: relative;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            .modal-header {
                padding: 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-body {
                padding: 20px;
            }
            .modal-footer {
                padding: 20px;
                border-top: 1px solid #eee;
                text-align: right;
            }
            .modal-close {
                background: none;
                border: none;
                font-size: 1.5em;
                cursor: pointer;
                padding: 5px;
                color: #666;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(modal);
        
        // Event listeners
        modal.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                document.body.removeChild(modal);
                document.head.removeChild(style);
            });
        });
        
        // Cerrar con escape
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.head.removeChild(style);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        // Focus inicial
        modal.querySelector('.modal-close').focus();
    }

    resetSettings() {
        this.settings = {
            contrastMode: 'normal',
            fontSize: 'medium',
            screenReaderEnabled: false,
            voiceNavigationEnabled: false,
            audioDescriptionsEnabled: false
        };
        
        localStorage.removeItem('accessibility-settings');
        this.applyStoredSettings();
        this.announceToScreenReader('Configuración de accesibilidad restablecida');
        this.showAccessibilityFeedback('Configuración restablecida');
    }

    /**
     * Muestra advertencia visible cuando no hay voces en español
     */
    showVoiceWarning() {
        // Crear o actualizar el mensaje de advertencia
        let warningElement = document.getElementById('voice-warning');
        
        if (!warningElement) {
            warningElement = document.createElement('div');
            warningElement.id = 'voice-warning';
            warningElement.className = 'voice-warning';
            warningElement.setAttribute('role', 'alert');
            warningElement.setAttribute('aria-live', 'polite');
            
            // Insertar al inicio del body
            document.body.insertBefore(warningElement, document.body.firstChild);
        }
        
        warningElement.innerHTML = `
            <div class="warning-content">
                <i class="fas fa-exclamation-triangle" aria-hidden="true"></i>
                <div>
                    <strong>Advertencia de Accesibilidad:</strong>
                    <p>No se encontraron voces en español en este dispositivo. 
                    La síntesis de voz podría sonar con acento inglés.</p>
                    <p><small>Para mejorar la experiencia, instale voces en español en la configuración del sistema.</small></p>
                </div>
                <button class="close-warning" onclick="this.parentElement.parentElement.remove()" aria-label="Cerrar advertencia">
                    <i class="fas fa-times" aria-hidden="true"></i>
                </button>
            </div>
        `;
        
        // Auto-ocultar después de 10 segundos
        setTimeout(() => {
            if (warningElement && warningElement.parentNode) {
                warningElement.remove();
            }
        }, 10000);
        
        // También anunciar a lectores de pantalla
        this.announceToScreenReader('Advertencia: No se encontraron voces en español. La síntesis de voz podría sonar con acento inglés.');
    }

    enableScreenReaderFeatures() {
        // Mejorar descripciones ARIA
        document.querySelectorAll('img:not([alt])').forEach(img => {
            img.setAttribute('alt', 'Imagen sin descripción');
        });
        
        // Anunciar cambios de página
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    const newContent = Array.from(mutation.addedNodes)
                        .filter(node => node.nodeType === Node.ELEMENT_NODE)
                        .map(node => node.textContent?.trim())
                        .filter(text => text && text.length > 10)
                        .join(' ');
                    
                    if (newContent) {
                        this.announceToScreenReader(`Nuevo contenido cargado: ${newContent.substring(0, 100)}...`);
                    }
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        this.screenReaderObserver = observer;
    }

    disableScreenReaderFeatures() {
        if (this.screenReaderObserver) {
            this.screenReaderObserver.disconnect();
            this.screenReaderObserver = null;
        }
        
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityManager = new AccessibilityManager();
});

// Exportar para uso global
window.AccessibilityManager = AccessibilityManager;
