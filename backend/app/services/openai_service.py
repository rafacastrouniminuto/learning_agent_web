import asyncio
import re
from typing import AsyncGenerator, Dict, Any, Optional, Tuple, List
import openai
import json
from sqlalchemy.orm import Session
from ..core.config import settings
from .prompts import get_system_prompt, get_conversation_prompt
from .learning_path_service import learning_path_service
from .mcp_service import mcp_service_instance, MCP_AVAILABLE, search_learning_modules, get_available_thematic_axes, create_personalized_learning_path, get_user_learning_profile
from ..models.learning_path import LearningPath

class OpenAIService:
    def __init__(self):
        print(f"Initializing OpenAI with API key: {settings.openai_api_key[:10]}..." if settings.openai_api_key else "No API key found")
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.mcp_service = mcp_service_instance["server"]
        print(f"✅ OpenAI Service: MCP integration enabled ({'official' if MCP_AVAILABLE else 'custom'})")
    
    def get_mcp_tools_as_functions(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenAI function calling format"""
        functions = []
        
        # Define function schemas for OpenAI
        function_schemas = {
            "search_learning_modules": {
                "name": "search_learning_modules",
                "description": "Search for learning modules by topic, difficulty, and thematic axis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic to search for"},
                        "difficulty": {"type": "string", "enum": ["all", "principiante", "intermedio", "avanzado"], "description": "Difficulty level"},
                        "eje_tematico": {"type": "string", "description": "Thematic axis"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 10}
                    }
                }
            },
            "get_available_thematic_axes": {
                "name": "get_available_thematic_axes",
                "description": "Get all available thematic axes from the learning modules",
                "parameters": {"type": "object", "properties": {}}
            },
            "create_personalized_learning_path": {
                "name": "create_personalized_learning_path",
                "description": "Create a personalized learning path based on user profile and goals",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_profile": {"type": "object", "description": "User's learning profile"},
                        "learning_goals": {"type": "array", "items": {"type": "string"}, "description": "Learning goals"},
                        "time_constraints": {"type": "string", "description": "Time constraints", "default": "flexible"},
                        "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Focus areas"}
                    },
                    "required": ["user_profile", "learning_goals"]
                }
            }
        }
        
        # Include all available function schemas
        for schema_name in function_schemas:
            functions.append(function_schemas[schema_name])
        
        return functions
    
    async def handle_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OpenAI function calls by routing to MCP tools"""
        try:
            if MCP_AVAILABLE:
                # Call FastMCP functions directly
                if function_name == "search_learning_modules":
                    result = search_learning_modules(**arguments)
                elif function_name == "get_available_thematic_axes":
                    result = get_available_thematic_axes()
                elif function_name == "create_personalized_learning_path":
                    result = create_personalized_learning_path(**arguments)
                elif function_name == "get_user_learning_profile":
                    result = get_user_learning_profile(**arguments)
                else:
                    return {"error": f"Function '{function_name}' not found"}
            else:
                # Fallback to custom service
                result = await self.mcp_service.call_tool(function_name, **arguments)
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"error": str(e)}
    
    def prepare_learning_path_messages(
        self, 
        user_message: str, 
        conversation_history: list = None,
        iteration_count: int = 0
    ) -> list[Dict[str, str]]:
        """
        Prepara los mensajes para el chat de rutas de aprendizaje con gestión inteligente de tokens
        """
        conversation_history = conversation_history or []
        
        # Determinar si usar versión compacta basado en solicitud del usuario
        use_compact = False
        max_modules_in_prompt = None
        
        # Detectar si solicita muchos ejes
        user_msg_lower = user_message.lower()
        if any(num in user_msg_lower for num in ['13', '15', '20', '30', 'todos', 'completa']):
            use_compact = True
            max_modules_in_prompt = 20
            print(f"🔍 DEBUG - Detected large request, using compact mode")
        
        # Obtener contexto de módulos con gestión de tokens
        modules_context = learning_path_service.get_modules_context(
            max_modules=max_modules_in_prompt, 
            compact=use_compact
        )
        
        print(f"🔍 DEBUG - Context length: {len(modules_context)} chars, compact: {use_compact}")
        print(f"🔍 DEBUG - Context preview (first 300 chars):")
        print(modules_context[:300])
        print(f"🔍 DEBUG - Context preview (last 300 chars):")
        print(modules_context[-300:])
        
        # Sistema prompt con contexto optimizado
        system_message = {
            "role": "system",
            "content": get_system_prompt(modules_context)
        }
        
        print(f"🔍 DEBUG - Final system prompt length: {len(system_message['content'])}")
        print(f"🔍 DEBUG - System prompt preview:")
        print(system_message['content'][:500] + "..." if len(system_message['content']) > 500 else system_message['content'])
        
        # Construir historial de conversación (limitar para ahorrar tokens)
        messages = [system_message]
        
        # Solo incluir los últimos 2 intercambios para ahorrar tokens en solicitudes grandes
        recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
        
        # Agregar historial previo
        for msg in recent_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Agregar mensaje actual del usuario
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        return messages
    
    async def chat_completion_stream_learning_path(
        self, 
        user_message: str,
        conversation_history: list = None,
        iteration_count: int = 0,
        model: str = None,
        user_id: str = None
    ) -> AsyncGenerator[Tuple[str, Optional[Dict[str, Any]]], None]:
        """
        Genera streaming chat completion específico para rutas de aprendizaje
        Retorna tuplas de (content, learning_path_json)
        """
        try:
            print(f"🔍 Debug - Preparing messages for user: {user_id}")
            print(f"🔍 Debug - User message: {user_message}")
            print(f"🔍 Debug - Conversation history length: {len(conversation_history or [])}")
            
            messages = self.prepare_learning_path_messages(
                user_message, conversation_history, iteration_count
            )
            
            print(f"🔍 Debug - Total messages prepared: {len(messages)}")
            print(f"🔍 Debug - System message length: {len(messages[0]['content']) if messages else 0}")
            
            model = model or settings.openai_model
            print(f"Making OpenAI learning path request with model: {model} (user_id: {user_id})")
            
            # Add a simple validation
            if not user_message.strip():
                yield "❌ Error: Mensaje vacío", None
                return
            
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=settings.openai_max_tokens,
                temperature=0.7,
                stream=True
            )
            
            full_response = ""
            chunk_count = 0
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    chunk_count += 1
                    yield content, None
            
            print(f"🔍 Debug - Stream completed. Total chunks: {chunk_count}, Response length: {len(full_response)}")
            print(f"🔍 Debug - Full response: {full_response[:300]}...")
            
            # Verificar estado del learning_path_service
            print(f"📊 CSV modules loaded: {len(learning_path_service.modules_data) if hasattr(learning_path_service, 'modules_data') else 'No modules_data'}")
            if hasattr(learning_path_service, 'modules_data') and learning_path_service.modules_data:
                print(f"📋 First module: {learning_path_service.modules_data[0]}")
            
            # Al final del stream, buscar patrones GENERATE_PATH
            learning_path_json = None
            
            # Buscar diferentes patrones de generación
            if "GENERATE_PATH_COUNT:" in full_response:
                print("🎯 Found GENERATE_PATH_COUNT pattern!")
                count_match = re.search(r'GENERATE_PATH_COUNT:\s*(\d+|ALL)', full_response)
                if count_match:
                    print(f"🎯 Count match: {count_match.group(1)}")
                    learning_path_json = self._generate_path_from_csv(full_response)
                else:
                    print("❌ No count match found")
                        
            elif "GENERATE_PATH_IDS:" in full_response:
                learning_path_json = self._generate_path_from_csv(full_response)
                    
            elif "GENERATE_PATH_CATEGORY:" in full_response:
                learning_path_json = self._generate_path_from_csv(full_response)
                    
            elif "GENERATE_PATH_MODULE:" in full_response:
                learning_path_json = self._generate_path_from_csv(full_response)
                    
            elif "GENERATE_PATH_ALL" in full_response:
                learning_path_json = self._generate_path_from_csv(full_response)
            
            # Fallback: buscar JSON tradicional
            if not learning_path_json:
                learning_path_json = learning_path_service.extract_json_from_response(full_response)
            
            if learning_path_json:
                print("✅ Learning path generated successfully")
                yield "", learning_path_json
                    
        except Exception as e:
            print(f"❌ OpenAI API error in learning path: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f"Error en el chat: {str(e)}", None

    def _generate_path_from_csv(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """
        Genera automáticamente un JSON de ruta de aprendizaje basado en el CSV
        usando el comando GENERATE_PATH_COUNT del AI
        """
        try:
            print("🚀 Starting _generate_path_from_csv")
            print(f"🔍 AI Response length: {len(ai_response)}")
            
            # Extraer la cantidad solicitada
            import re
            match = re.search(r'GENERATE_PATH_COUNT:\s*(\w+)', ai_response)
            if not match:
                print("❌ No se encontró GENERATE_PATH_COUNT en la respuesta")
                return None
            
            count_str = match.group(1).strip()
            print(f"🔍 Detected count: {count_str}")
            
            # Determinar cuántos módulos generar
            if count_str.upper() == "ALL":
                count = len(learning_path_service.modules_data)
            else:
                try:
                    count = int(count_str)
                except ValueError:
                    count = 5  # Default fallback
            
            # Limitar a los datos disponibles
            count = min(count, len(learning_path_service.modules_data))
            print(f"🎯 Generating path with {count} modules from CSV")
            print(f"� Available modules in CSV: {len(learning_path_service.modules_data)}")
            
            # Tomar los primeros N módulos del CSV
            selected_modules = learning_path_service.modules_data[:count]
            print(f"✅ Selected {len(selected_modules)} modules")
            
            # Construir el JSON automáticamente
            learning_path_json = {
                "action": "generate_learning_path",
                "student_profile": f"Usuario solicita {count_str} ejes temáticos",
                "recommended_modules": []
            }
            
            for i, module in enumerate(selected_modules):
                path_module = {
                    "eje_tematico": module["eje_tematico"],
                    "modulo": module["modulo"],
                    "competencia": module["competencia"],
                    "categoria": module.get("categoria", "General"),
                    "justification": "Eje fundamental según el curriculum STEM+",
                    "priority": "alta",
                    "estimated_duration": "3-4 semanas"
                }
                learning_path_json["recommended_modules"].append(path_module)
                print(f"  {i+1}. {module['eje_tematico'][:50]}...")
            
            # Generar secuencia y próximos pasos
            sequence_items = [f"{i+1}. {mod['eje_tematico'][:30]}..." for i, mod in enumerate(selected_modules[:5])]
            learning_path_json["learning_sequence"] = " → ".join(sequence_items)
            learning_path_json["next_steps"] = f"Comenzar con el primer eje temático y avanzar secuencialmente a través de los {count} módulos."
            
            print(f"✅ Generated learning path JSON with {len(learning_path_json['recommended_modules'])} modules")
            return learning_path_json
            
        except Exception as e:
            print(f"❌ Error generating path from CSV: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def chat_completion_stream(
        self, 
        messages: list[Dict[str, str]], 
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming chat completion using OpenAI API
        """
        try:
            model = model or settings.openai_model
            print(f"Making OpenAI request with model: {model}")
            print(f"Messages: {messages}")
            
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=settings.openai_max_tokens,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def chat_completion(
        self, 
        messages: list[Dict[str, str]], 
        model: str = None
    ) -> str:
        """
        Generate regular chat completion using OpenAI API
        """
        try:
            model = model or settings.openai_model
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=settings.openai_max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"

# Global instance
openai_service = OpenAIService()
