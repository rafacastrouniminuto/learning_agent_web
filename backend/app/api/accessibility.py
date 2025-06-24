"""
API de Accesibilidad para Discapacidad Visual
Living Lab UNIMINUTO - Learning Agent Web
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import logging

from ..services.accessibility_service import accessibility_service, accessibility_server

# Configurar logging
logger = logging.getLogger(__name__)

# Router para accesibilidad
accessibility_router = APIRouter(prefix="/accessibility", tags=["accessibility"])

# Modelos Pydantic
class AccessibilitySettings(BaseModel):
    contrast_mode: Optional[str] = None
    font_size: Optional[str] = None
    screen_reader_enabled: Optional[bool] = None
    voice_navigation_enabled: Optional[bool] = None
    audio_descriptions_enabled: Optional[bool] = None

class ContrastModeRequest(BaseModel):
    mode: str

class FontSizeRequest(BaseModel):
    size: str

class ScreenReaderRequest(BaseModel):
    enabled: bool

class AudioDescriptionRequest(BaseModel):
    content_type: str
    content_data: str

class VoiceCommandRequest(BaseModel):
    command: str
    action: Optional[str] = ""

@accessibility_router.get("/settings")
async def get_accessibility_settings():
    """
    Obtiene la configuración actual de accesibilidad
    """
    try:
        settings = accessibility_service.get_settings()
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": settings,
                "message": "Configuración de accesibilidad obtenida exitosamente"
            }
        )
    except Exception as e:
        logger.error(f"Error obteniendo configuración de accesibilidad: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.post("/settings")
async def update_accessibility_settings(settings: AccessibilitySettings):
    """
    Actualiza la configuración de accesibilidad
    """
    try:
        settings_dict = settings.dict(exclude_none=True)
        updated_settings = accessibility_service.update_settings(settings_dict)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": updated_settings,
                "message": "Configuración de accesibilidad actualizada exitosamente"
            }
        )
    except Exception as e:
        logger.error(f"Error actualizando configuración de accesibilidad: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.post("/contrast-mode")
async def set_contrast_mode(request: ContrastModeRequest):
    """
    Establece el modo de contraste
    """
    try:
        # Usar la herramienta MCP directamente
        result = await accessibility_server.call_tool("set_contrast_mode", {"mode": request.mode})
        result_data = json.loads(result)
        
        if result_data["status"] == "error":
            raise HTTPException(status_code=400, detail=result_data["message"])
        
        return JSONResponse(
            status_code=200,
            content=result_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estableciendo modo de contraste: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.post("/font-size")
async def set_font_size(request: FontSizeRequest):
    """
    Establece el tamaño de fuente
    """
    try:
        # Usar la herramienta MCP directamente
        result = await accessibility_server.call_tool("set_font_size", {"size": request.size})
        result_data = json.loads(result)
        
        if result_data["status"] == "error":
            raise HTTPException(status_code=400, detail=result_data["message"])
        
        return JSONResponse(
            status_code=200,
            content=result_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estableciendo tamaño de fuente: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.post("/screen-reader")
async def toggle_screen_reader(request: ScreenReaderRequest):
    """
    Activa o desactiva el soporte para lectores de pantalla
    """
    try:
        # Usar la herramienta MCP directamente
        result = await accessibility_server.call_tool("toggle_screen_reader_support", {"enabled": request.enabled})
        result_data = json.loads(result)
        
        if result_data["status"] == "error":
            raise HTTPException(status_code=400, detail=result_data["message"])
        
        return JSONResponse(
            status_code=200,
            content=result_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configurando lector de pantalla: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.get("/keyboard-shortcuts")
async def get_keyboard_shortcuts():
    """
    Obtiene la lista de atajos de teclado disponibles
    """
    try:
        # Usar la herramienta MCP directamente
        result = await accessibility_server.call_tool("get_keyboard_shortcuts", {})
        result_data = json.loads(result)
        
        if result_data["status"] == "error":
            raise HTTPException(status_code=400, detail=result_data["message"])
        
        return JSONResponse(
            status_code=200,
            content=result_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo atajos de teclado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.post("/audio-description")
async def generate_audio_description(request: AudioDescriptionRequest):
    """
    Genera descripción de audio para contenido multimedia
    """
    try:
        # Usar la herramienta MCP directamente
        result = await accessibility_server.call_tool(
            "generate_audio_description", 
            {
                "content_type": request.content_type,
                "content_data": request.content_data
            }
        )
        result_data = json.loads(result)
        
        if result_data["status"] == "error":
            raise HTTPException(status_code=400, detail=result_data["message"])
        
        return JSONResponse(
            status_code=200,
            content=result_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando descripción de audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.get("/voice-commands")
async def get_voice_commands():
    """
    Obtiene los comandos de voz disponibles
    """
    try:
        # Usar la herramienta MCP directamente
        result = await accessibility_server.call_tool("configure_voice_navigation", {"command": ""})
        result_data = json.loads(result)
        
        if result_data["status"] == "error":
            raise HTTPException(status_code=400, detail=result_data["message"])
        
        return JSONResponse(
            status_code=200,
            content=result_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo comandos de voz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.post("/voice-command")
async def configure_voice_command(request: VoiceCommandRequest):
    """
    Configura un comando de navegación por voz
    """
    try:
        # Usar la herramienta MCP directamente
        result = await accessibility_server.call_tool(
            "configure_voice_navigation", 
            {
                "command": request.command,
                "action": request.action
            }
        )
        result_data = json.loads(result)
        
        if result_data["status"] == "error":
            raise HTTPException(status_code=400, detail=result_data["message"])
        
        return JSONResponse(
            status_code=200,
            content=result_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configurando comando de voz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.get("/test")
async def test_accessibility_features():
    """
    Endpoint de prueba para verificar funcionalidades de accesibilidad
    """
    try:
        # Probar todas las herramientas MCP
        tests = []
        
        # Test 1: Obtener configuración
        try:
            result = await accessibility_server.call_tool("get_accessibility_settings", {})
            tests.append({
                "test": "get_accessibility_settings",
                "status": "success",
                "result": json.loads(result)
            })
        except Exception as e:
            tests.append({
                "test": "get_accessibility_settings",
                "status": "error",
                "error": str(e)
            })
        
        # Test 2: Cambiar contraste
        try:
            result = await accessibility_server.call_tool("set_contrast_mode", {"mode": "high"})
            tests.append({
                "test": "set_contrast_mode",
                "status": "success",
                "result": json.loads(result)
            })
        except Exception as e:
            tests.append({
                "test": "set_contrast_mode",
                "status": "error",
                "error": str(e)
            })
        
        # Test 3: Atajos de teclado
        try:
            result = await accessibility_server.call_tool("get_keyboard_shortcuts", {})
            tests.append({
                "test": "get_keyboard_shortcuts",
                "status": "success",
                "result": json.loads(result)
            })
        except Exception as e:
            tests.append({
                "test": "get_keyboard_shortcuts",
                "status": "error",
                "error": str(e)
            })
        
        # Test 4: Descripción de audio
        try:
            result = await accessibility_server.call_tool(
                "generate_audio_description", 
                {
                    "content_type": "image",
                    "content_data": "Logo de Living Lab UNIMINUTO"
                }
            )
            tests.append({
                "test": "generate_audio_description",
                "status": "success",
                "result": json.loads(result)
            })
        except Exception as e:
            tests.append({
                "test": "generate_audio_description",
                "status": "error",
                "error": str(e)
            })
        
        # Test 5: Comandos de voz
        try:
            result = await accessibility_server.call_tool("configure_voice_navigation", {"command": "ir dashboard"})
            tests.append({
                "test": "configure_voice_navigation",
                "status": "success",
                "result": json.loads(result)
            })
        except Exception as e:
            tests.append({
                "test": "configure_voice_navigation",
                "status": "error",
                "error": str(e)
            })
        
        success_count = len([t for t in tests if t["status"] == "success"])
        total_count = len(tests)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": f"Pruebas de accesibilidad completadas: {success_count}/{total_count} exitosas",
                "summary": {
                    "total_tests": total_count,
                    "successful": success_count,
                    "failed": total_count - success_count
                },
                "tests": tests
            }
        )
        
    except Exception as e:
        logger.error(f"Error ejecutando pruebas de accesibilidad: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@accessibility_router.get("/health")
async def accessibility_health_check():
    """
    Verificación de salud del módulo de accesibilidad
    """
    try:
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "message": "Módulo de accesibilidad funcionando correctamente",
                "features": {
                    "contrast_modes": ["normal", "high", "yellow_black", "blue_white"],
                    "font_sizes": ["small", "medium", "large", "extra-large"],
                    "screen_reader_support": True,
                    "voice_navigation": True,
                    "keyboard_shortcuts": True,
                    "audio_descriptions": True
                },
                "mcp_server": "accessibility_server",
                "tools_available": [
                    "get_accessibility_settings",
                    "set_contrast_mode",
                    "set_font_size",
                    "toggle_screen_reader_support",
                    "get_keyboard_shortcuts",
                    "generate_audio_description",
                    "configure_voice_navigation"
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error en verificación de salud de accesibilidad: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
