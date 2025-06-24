"""
Servicio de Accesibilidad para Discapacidad Visual
Integrado con Model Context Protocol (MCP)
"""

import json
import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear servidor MCP para herramientas de accesibilidad
accessibility_server = FastMCP("Accessibility Tools")

class AccessibilityService:
    """Servicio que proporciona herramientas de accesibilidad para discapacidad visual"""
    
    def __init__(self):
        self.contrast_modes = {
            "normal": {"background": "#ffffff", "text": "#333333"},
            "high": {"background": "#000000", "text": "#ffffff"},
            "yellow_black": {"background": "#ffff00", "text": "#000000"},
            "blue_white": {"background": "#0000ff", "text": "#ffffff"}
        }
        
        self.font_sizes = ["small", "medium", "large", "extra-large"]
        self.current_settings = {
            "contrast_mode": "normal",
            "font_size": "medium",
            "screen_reader_enabled": False,
            "voice_navigation_enabled": False,
            "audio_descriptions_enabled": False
        }

    def get_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración actual de accesibilidad"""
        return self.current_settings.copy()

    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza la configuración de accesibilidad"""
        for key, value in settings.items():
            if key in self.current_settings:
                self.current_settings[key] = value
        return self.current_settings.copy()

# Herramientas MCP para Accesibilidad

@accessibility_server.tool()
def get_accessibility_settings() -> dict:
    """
    Obtiene la configuración actual de accesibilidad para discapacidad visual.
    
    Returns:
        dict: Configuración actual
    """
    try:
        service = AccessibilityService()
        settings = service.get_settings()
        
        logger.info("Configuración de accesibilidad obtenida exitosamente")
        return {
            "status": "success",
            "data": settings,
            "message": "Configuración de accesibilidad obtenida"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración de accesibilidad: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@accessibility_server.tool()
def set_contrast_mode(mode: str) -> dict:
    """
    Establece el modo de contraste para usuarios con discapacidad visual.
    
    Args:
        mode: Modo de contraste ('normal', 'high', 'yellow_black', 'blue_white')
    
    Returns:
        dict: Resultado de la operación
    """
    try:
        service = AccessibilityService()
        
        if mode not in service.contrast_modes:
            available_modes = list(service.contrast_modes.keys())
            return {
                "status": "error",
                "message": f"Modo de contraste inválido. Modos disponibles: {available_modes}"
            }
        
        settings = service.update_settings({"contrast_mode": mode})
        contrast_config = service.contrast_modes[mode]
        
        logger.info(f"Modo de contraste cambiado a: {mode}")
        return {
            "status": "success",
            "data": {
                "mode": mode,
                "colors": contrast_config,
                "settings": settings
            },
            "message": f"Modo de contraste cambiado a: {mode}"
        }
        
    except Exception as e:
        logger.error(f"Error cambiando modo de contraste: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@accessibility_server.tool()
def set_font_size(size: str) -> dict:
    """
    Establece el tamaño de fuente para mejorar la legibilidad.
    
    Args:
        size: Tamaño de fuente ('small', 'medium', 'large', 'extra-large')
    
    Returns:
        dict: Resultado de la operación
    """
    try:
        service = AccessibilityService()
        
        if size not in service.font_sizes:
            return {
                "status": "error",
                "message": f"Tamaño de fuente inválido. Tamaños disponibles: {service.font_sizes}"
            }
        
        settings = service.update_settings({"font_size": size})
        
        font_scale = {
            "small": "0.8em",
            "medium": "1em",
            "large": "1.2em",
            "extra-large": "1.5em"
        }
        
        logger.info(f"Tamaño de fuente cambiado a: {size}")
        return {
            "status": "success",
            "data": {
                "size": size,
                "scale": font_scale[size],
                "settings": settings
            },
            "message": f"Tamaño de fuente cambiado a: {size}"
        }
        
    except Exception as e:
        logger.error(f"Error cambiando tamaño de fuente: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@accessibility_server.tool()
def toggle_screen_reader_support(enabled: bool) -> dict:
    """
    Activa o desactiva el soporte para lectores de pantalla.
    
    Args:
        enabled: True para activar, False para desactivar
    
    Returns:
        dict: Resultado de la operación
    """
    try:
        service = AccessibilityService()
        settings = service.update_settings({"screen_reader_enabled": enabled})
        
        status = "activado" if enabled else "desactivado"
        logger.info(f"Soporte para lector de pantalla {status}")
        
        return {
            "status": "success",
            "data": {
                "enabled": enabled,
                "settings": settings,
                "aria_features": {
                    "live_regions": enabled,
                    "landmarks": enabled,
                    "descriptions": enabled,
                    "labels": enabled
                }
            },
            "message": f"Soporte para lector de pantalla {status}"
        }
        
    except Exception as e:
        logger.error(f"Error configurando lector de pantalla: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@accessibility_server.tool()
def get_keyboard_shortcuts() -> dict:
    """
    Obtiene la lista de atajos de teclado disponibles para navegación.
    
    Returns:
        dict: Lista de atajos de teclado
    """
    try:
        shortcuts = {
            "navigation": {
                "Tab": "Navegar al siguiente elemento",
                "Shift+Tab": "Navegar al elemento anterior",
                "Enter": "Activar elemento seleccionado",
                "Space": "Activar botón o checkbox",
                "Arrow Keys": "Navegar entre opciones de menú"
            },
            "application": {
                "Alt+1": "Ir al Dashboard",
                "Alt+2": "Ir al Chat",
                "Alt+3": "Ir a Rutas de Aprendizaje",
                "Alt+4": "Ir a Herramientas MCP",
                "Alt+M": "Abrir/cerrar menú lateral",
                "Alt+S": "Buscar",
                "Ctrl+/": "Mostrar ayuda de atajos"
            },
            "accessibility": {
                "Alt+C": "Cambiar modo de contraste",
                "Alt+F": "Cambiar tamaño de fuente",
                "Alt+R": "Activar/desactivar lector de pantalla",
                "Alt+V": "Activar/desactivar navegación por voz"
            }
        }
        
        logger.info("Lista de atajos de teclado obtenida")
        return {
            "status": "success",
            "data": shortcuts,
            "message": "Atajos de teclado disponibles"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo atajos de teclado: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@accessibility_server.tool()
def generate_audio_description(content_type: str, content_data: str) -> dict:
    """
    Genera descripción de audio para contenido multimedia o visual.
    
    Args:
        content_type: Tipo de contenido ('image', 'video', 'chart', 'diagram')
        content_data: Datos o descripción del contenido
    
    Returns:
        dict: Descripción de audio generada
    """
    try:
        descriptions = {
            "image": f"Imagen: {content_data}. Descripción detallada disponible para lectores de pantalla.",
            "video": f"Video: {content_data}. Descripción de audio activada para narrar contenido visual.",
            "chart": f"Gráfico: {content_data}. Datos tabulares disponibles como alternativa accesible.",
            "diagram": f"Diagrama: {content_data}. Descripción estructural y navegación por elementos disponible."
        }
        
        if content_type not in descriptions:
            return {
                "status": "error",
                "message": f"Tipo de contenido no soportado: {content_type}"
            }
        
        description = descriptions[content_type]
        
        logger.info(f"Descripción de audio generada para {content_type}")
        return {
            "status": "success",
            "data": {
                "content_type": content_type,
                "description": description,
                "accessibility_features": {
                    "screen_reader_text": description,
                    "audio_cues": True,
                    "alternative_format": True
                }
            },
            "message": "Descripción de audio generada exitosamente"
        }
        
    except Exception as e:
        logger.error(f"Error generando descripción de audio: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

@accessibility_server.tool()
def configure_voice_navigation(command: str, action: str = "") -> dict:
    """
    Configura comandos de navegación por voz para usuarios con discapacidad visual.
    
    Args:
        command: Comando de voz a configurar
        action: Acción asociada al comando (opcional para consultas)
    
    Returns:
        dict: Resultado de la configuración
    """
    try:
        voice_commands = {
            "ir dashboard": "/dashboard",
            "ir chat": "/chat",
            "ir rutas": "/learning-paths",
            "ir herramientas": "/mcp-tools",
            "abrir menú": "toggle_sidebar",
            "cerrar menú": "close_sidebar",
            "siguiente": "next_element",
            "anterior": "previous_element",
            "activar": "click_element",
            "buscar": "focus_search",
            "ayuda": "show_help",
            "leer página": "read_all",
            "parar lectura": "stop_reading"
        }
        
        if not action:  # Solo consulta
            return {
                "status": "success",
                "data": {
                    "available_commands": voice_commands,
                    "usage": "Use comandos de voz naturales en español",
                    "examples": [
                        "Decir 'ir dashboard' para navegar al dashboard",
                        "Decir 'leer página' para que se lea todo el contenido",
                        "Decir 'siguiente' para ir al siguiente elemento"
                    ]
                },
                "message": "Comandos de voz disponibles"
            }
        
        if command in voice_commands:
            logger.info(f"Comando de voz configurado: {command} -> {action}")
            return {
                "status": "success",
                "data": {
                    "command": command,
                    "action": action,
                    "default_action": voice_commands[command]
                },
                "message": f"Comando de voz '{command}' configurado"
            }
        else:
            return {
                "status": "error",
                "message": f"Comando de voz no reconocido: {command}"
            }
        
    except Exception as e:
        logger.error(f"Error configurando navegación por voz: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

# Instancia global del servicio
accessibility_service = AccessibilityService()
