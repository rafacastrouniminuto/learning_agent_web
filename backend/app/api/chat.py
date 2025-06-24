from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from ..core.database import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..services.openai_service import openai_service
from ..services.learning_path_service import learning_path_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    mode: str = "general"  # "general" or "learning_path"

class ChatResponse(BaseModel):
    response: str
    conversation_id: str = None

class LearningPathGeneratedResponse(BaseModel):
    success: bool
    learning_path: Optional[Dict[str, Any]] = None
    message: str

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Stream chat response from OpenAI"""
    
    print(f"🔍 DEBUG - Chat request from user {current_user.email}: {request.message}")
    print(f"🔍 DEBUG - Chat mode: {request.mode}")
    print(f"🔍 DEBUG - Conversation history length: {len(request.conversation_history)}")
    
    async def generate():
        try:
            print("Starting OpenAI stream...")
            chunk_count = 0
            generated_learning_path = None
            
            # Usar el servicio específico para rutas de aprendizaje si está en modo learning_path
            if request.mode == "learning_path":
                print("Using learning path mode")
                async for content, learning_path_json in openai_service.chat_completion_stream_learning_path(
                    request.message, 
                    [msg.dict() for msg in request.conversation_history],
                    user_id=str(current_user.id)
                ):
                    if learning_path_json:
                        # Se generó una ruta de aprendizaje
                        generated_learning_path = learning_path_json
                        formatted_path = learning_path_service.format_learning_path_for_display(learning_path_json)
                        
                        # Enviar la ruta de aprendizaje como evento especial
                        path_data = json.dumps({
                            "type": "learning_path_generated",
                            "learning_path": formatted_path,
                            "done": False
                        })
                        yield f"data: {path_data}\n\n"
                    elif content:
                        chunk_count += 1
                        print(f"Chunk {chunk_count}: {repr(content)}")
                        
                        # Formato normal de streaming
                        data = json.dumps({"content": content, "done": False})
                        yield f"data: {data}\n\n"
            else:
                # Modo general - usar el prompt original
                system_message = {
                    "role": "system",
                    "content": """Eres un agente conversacional experto del Living Lab de UNIMINUTO especializado en crear rutas de aprendizaje personalizadas. 

Tu objetivo es:
1. Entender las necesidades de aprendizaje del usuario
2. Evaluar su nivel de conocimiento actual
3. Identificar sus objetivos de aprendizaje
4. Crear rutas de aprendizaje personalizadas

Características:
- Eres amigable y profesional
- Haces preguntas relevantes para entender mejor al usuario
- Ofreces contenido educativo de calidad del ecosistema UNIMINUTO
- Adaptas las recomendaciones según el perfil del usuario

Responde siempre en español y mantén un tono académico pero accesible."""
                }
                
                # Build conversation messages
                messages = [system_message]
                messages.extend([msg.dict() for msg in request.conversation_history])
                messages.append({"role": "user", "content": request.message})
                
                async for chunk in openai_service.chat_completion_stream(messages):
                    chunk_count += 1
                    print(f"Chunk {chunk_count}: {repr(chunk)}")
                    
                    # Format as Server-Sent Events
                    data = json.dumps({"content": chunk, "done": False})
                    yield f"data: {data}\n\n"
            
            print(f"Stream completed successfully. Total chunks: {chunk_count}")
            # Send completion signal
            data = json.dumps({"content": "", "done": True})
            yield f"data: {data}\n\n"
            
        except Exception as e:
            print(f"Stream error: {str(e)}")
            import traceback
            traceback.print_exc()
            error_data = json.dumps({"error": str(e), "done": True})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Send chat message and get response (non-streaming)"""
    
    # Prepare system message
    system_message = {
        "role": "system",
        "content": """Eres un agente conversacional experto del Living Lab de UNIMINUTO especializado en crear rutas de aprendizaje personalizadas."""
    }
    
    # Build conversation messages
    messages = [system_message]
    messages.extend([msg.dict() for msg in request.conversation_history])
    messages.append({"role": "user", "content": request.message})
    
    try:
        response = await openai_service.chat_completion(messages)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_connection(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify authentication and basic connectivity"""
    return {"status": "ok", "user": current_user.email, "message": "Chat connection is working"}
