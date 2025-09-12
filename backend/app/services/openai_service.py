import asyncio
import re
import time
from typing import AsyncGenerator, Dict, Any, Optional, Tuple, List
import openai
import json
from sqlalchemy.orm import Session
from ..core.config import settings
from .prompts import get_system_prompt, get_conversation_prompt
from .learning_path_service import learning_path_service
from .mcp_service import mcp_service_instance, MCP_AVAILABLE, search_learning_modules, get_available_thematic_axes, create_personalized_learning_path, get_user_learning_profile, get_evaluation_questions, format_questions_for_chat
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
    
    def analyze_conversation_state(self, conversation_history: list) -> Dict[str, Any]:
        """
        Analiza el estado actual de la conversación para determinar qué preguntas se han hecho
        """
        questions_asked = {
            "question_1_objectives": False,
            "question_2_level": False, 
            "question_3_time_preference": False
        }
        
        user_responses = {
            "objectives": None,
            "level": None,
            "time_preference": None
        }
        
        recommendation_presented = False
        user_approved_recommendation = False
        
        if not conversation_history:
            return {
                "questions_asked": questions_asked,
                "user_responses": user_responses,
                "recommendation_presented": recommendation_presented,
                "user_approved_recommendation": user_approved_recommendation,
                "ready_to_generate": False,
                "next_action": "ask_question_1"
            }
        
        # Convertir a string para análisis
        conversation_text = ""
        for msg in conversation_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n"
        
        # Detectar preguntas hechas por el asistente
        if "Pregunta 1 de 3" in conversation_text or "objetivos de aprendizaje" in conversation_text.lower():
            questions_asked["question_1_objectives"] = True
            
        if "Pregunta 2 de 3" in conversation_text or "nivel actual" in conversation_text.lower():
            questions_asked["question_2_level"] = True
            
        if "Pregunta 3 de 3" in conversation_text or "organizar tu aprendizaje" in conversation_text.lower():
            questions_asked["question_3_time_preference"] = True
        
        # Detectar si se presentó recomendación
        if "GENERATE_RECOMMENDATION" in conversation_text or "CURSOS RECOMENDADOS" in conversation_text or "Te parecen bien estos cursos" in conversation_text or "EJES TEMÁTICOS RECOMENDADOS" in conversation_text:
            recommendation_presented = True
        
        # Detectar aprobación del usuario (solo si se presentó una recomendación)
        last_user_messages = []
        for msg in reversed(conversation_history):
            if msg.get("role") == "user":
                last_user_messages.append(msg.get("content", "").lower())
                if len(last_user_messages) >= 3:  # Revisar últimos 3 mensajes del usuario
                    break
        
        # Solo buscar aprobación si ya se presentó una recomendación
        if recommendation_presented:
            approval_words = ["sí", "si", "de acuerdo", "perfecto", "generar", "crear ruta", "está bien", "me parece bien", "ok", "vale", "adelante"]
            for user_msg in last_user_messages:
                if any(word in user_msg for word in approval_words):
                    user_approved_recommendation = True
                    print(f"🔍 DEBUG - Found approval in user message: '{user_msg}'")
                    break
        
        # Extraer respuestas del usuario (buscar después de cada pregunta)
        messages = conversation_history
        for i, msg in enumerate(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                # Si hay un mensaje del usuario después, es una respuesta
                if i + 1 < len(messages) and messages[i + 1].get("role") == "user":
                    user_response = messages[i + 1].get("content", "")
                    
                    if "Pregunta 1 de 3" in content and not user_responses["objectives"]:
                        user_responses["objectives"] = user_response
                    elif "Pregunta 2 de 3" in content and not user_responses["level"]:
                        user_responses["level"] = user_response
                    elif "Pregunta 3 de 3" in content and not user_responses["time_preference"]:
                        user_responses["time_preference"] = user_response
        
        # Determinar próxima acción
        next_action = "ask_question_1"
        
        if questions_asked["question_1_objectives"] and user_responses["objectives"]:
            next_action = "ask_question_2"
        if questions_asked["question_2_level"] and user_responses["level"]:
            next_action = "ask_question_3"
        if questions_asked["question_3_time_preference"] and user_responses["time_preference"]:
            next_action = "present_recommendation"
        if recommendation_presented and not user_approved_recommendation:
            next_action = "wait_for_approval"
        if recommendation_presented and user_approved_recommendation:
            next_action = "generate_path"
        
        # Determinar si está listo para generar - dos escenarios válidos:
        # 1. Completó el flujo normal de 3 preguntas + recomendación + aprobación
        # 2. Usuario aprobó explícitamente la recomendación (para casos de testing/admin)
        ready_to_generate = (
            (
                all([
                    questions_asked["question_1_objectives"] and user_responses["objectives"],
                    questions_asked["question_2_level"] and user_responses["level"],
                    questions_asked["question_3_time_preference"] and user_responses["time_preference"]
                ]) and 
                recommendation_presented and 
                user_approved_recommendation
            ) or 
            (
                # Escenario alternativo: usuario aprobó explícitamente sin seguir flujo completo
                recommendation_presented and 
                user_approved_recommendation and
                next_action == "generate_path"
            )
        )
        
        return {
            "questions_asked": questions_asked,
            "user_responses": user_responses,
            "recommendation_presented": recommendation_presented,
            "user_approved_recommendation": user_approved_recommendation,
            "ready_to_generate": ready_to_generate,
            "next_action": next_action,
            "last_user_messages": last_user_messages  # Debug info
        }

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
        
        # Analizar estado de la conversación
        conversation_state = self.analyze_conversation_state(conversation_history)
        print(f"🔍 DEBUG - Conversation state: {conversation_state}")
        
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
        
        # Modificar el prompt del sistema basado en el estado de la conversación
        system_prompt = get_system_prompt(modules_context, include_questions=True)
        
        # Agregar contexto adicional sobre el estado de las preguntas
        if conversation_state["next_action"] in ["ask_question_1", "ask_question_2", "ask_question_3"]:
            additional_context = f"""
ESTADO ACTUAL DE LA CONVERSACIÓN:
- Pregunta 1 (Objetivos): {'✅ Completada' if conversation_state['user_responses']['objectives'] else '❌ Pendiente'}
- Pregunta 2 (Nivel): {'✅ Completada' if conversation_state['user_responses']['level'] else '❌ Pendiente'}  
- Pregunta 3 (Tiempo): {'✅ Completada' if conversation_state['user_responses']['time_preference'] else '❌ Pendiente'}

PRÓXIMA ACCIÓN: {conversation_state['next_action']}

RECUERDA: NO generes ninguna ruta hasta completar las 3 preguntas Y obtener aprobación del usuario.
"""
            system_prompt += additional_context
            
        elif conversation_state["next_action"] == "present_recommendation":
            additional_context = f"""
INFORMACIÓN DEL USUARIO PARA RECOMENDACIÓN:
- Objetivos: {conversation_state['user_responses']['objectives']}
- Nivel: {conversation_state['user_responses']['level']}
- Preferencias de tiempo: {conversation_state['user_responses']['time_preference']}

PRÓXIMA ACCIÓN: Presentar recomendación de cursos específicos para aprobación.
NO uses GENERATE_PATH_* todavía. El usuario debe aprobar primero la selección.
"""
            system_prompt += additional_context
            
        elif conversation_state["next_action"] == "wait_for_approval":
            additional_context = f"""
ESTADO: Ya presentaste la recomendación de cursos. Esperando aprobación del usuario.
Si el usuario no está de acuerdo, permite modificar la selección.
Solo usa GENERATE_PATH_* cuando confirme explícitamente que está de acuerdo.
"""
            system_prompt += additional_context
            
        elif conversation_state["next_action"] == "generate_path":
            responses_summary = f"""
INFORMACIÓN DEL USUARIO PARA PERSONALIZACIÓN:
- Objetivos: {conversation_state['user_responses']['objectives']}
- Nivel: {conversation_state['user_responses']['level']}
- Preferencias de tiempo: {conversation_state['user_responses']['time_preference']}

ESTADO: Usuario aprobó la recomendación. AHORA SÍ puedes usar GENERATE_PATH_* para generar la ruta.
Usa esta información para personalizar la explicación de por qué la ruta recomendada es ideal.
"""
            system_prompt += responses_summary
        
        # Sistema prompt con contexto optimizado
        system_message = {
            "role": "system",
            "content": system_prompt
        }
        
        print(f"🔍 DEBUG - Final system prompt length: {len(system_message['content'])}")
        
        # Construir historial de conversación
        messages = [system_message]
        
        # Incluir historial completo para mantener contexto de preguntas
        for msg in conversation_history:
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
            
            # Al final del stream, buscar patrones GENERATE_PATH o GENERATE_RECOMMENDATION
            conversation_state = self.analyze_conversation_state(conversation_history or [])
            learning_path_json = None
            
            print(f"🔍 DEBUG - Conversation state: {conversation_state}")
            
            # FORZAR BOTÓN DE APROBACIÓN en múltiples escenarios
            should_force_approval_button = (
                # Escenario 1: Debe presentar recomendación pero no está en la respuesta
                (conversation_state["next_action"] == "present_recommendation" and 
                 "GENERATE_RECOMMENDATION" not in full_response and 
                 not conversation_state["recommendation_presented"]) or
                 
                # Escenario 2: Está esperando aprobación pero no se mostró el botón
                (conversation_state["next_action"] == "wait_for_approval" and 
                 "GENERATE_RECOMMENDATION" not in full_response) or
                 
                # Escenario 3: Ya se presentó recomendación pero usuario no ha aprobado y no hay botón
                (conversation_state["recommendation_presented"] and 
                 not conversation_state["user_approved_recommendation"] and
                 "GENERATE_RECOMMENDATION" not in full_response and
                 conversation_state["next_action"] in ["wait_for_approval", "present_recommendation"])
            )
            
            if should_force_approval_button:
                print("🔧 FORCING GENERATE_RECOMMENDATION pattern - Multiple scenarios detected")
                print(f"🔧 Next action: {conversation_state['next_action']}")
                print(f"🔧 Recommendation presented: {conversation_state['recommendation_presented']}")
                print(f"🔧 User approved: {conversation_state['user_approved_recommendation']}")
                
                recommendation_data = {
                    "action": "show_recommendation",
                    "type": "recommendation", 
                    "message": "Recomendación lista - esperando aprobación del usuario"
                }
                print(f"📋 Forcing recommendation_data: {recommendation_data}")
                yield "", recommendation_data
                return
            
            # Si encuentra GENERATE_RECOMMENDATION, enviar evento para mostrar botón de aprobación
            print(f"🔍 DEBUG - Checking for GENERATE_RECOMMENDATION in response...")
            print(f"🔍 DEBUG - Full response length: {len(full_response)}")
            print(f"🔍 DEBUG - Last 200 chars: {full_response[-200:]}")
            
            if "GENERATE_RECOMMENDATION" in full_response:
                print("📋 Found GENERATE_RECOMMENDATION - showing approval button")
                # Crear un objeto temporal para la recomendación
                recommendation_data = {
                    "action": "show_recommendation",
                    "type": "recommendation",
                    "message": "Recomendación presentada - esperando aprobación del usuario"
                }
                print(f"📋 Sending recommendation_data: {recommendation_data}")
                yield "", recommendation_data
                return
            else:
                print("❌ GENERATE_RECOMMENDATION pattern NOT found in response")
            
            # Solo procesar generación de rutas si el usuario aprobó la recomendación Y se presentó la recomendación
            if (conversation_state["ready_to_generate"] and 
                conversation_state["next_action"] == "generate_path" and 
                conversation_state["recommendation_presented"] and 
                conversation_state["user_approved_recommendation"]):
                print("✅ User approved recommendation, processing path generation...")
                
                # Buscar diferentes patrones de generación
                if "GENERATE_PATH_COUNT:" in full_response:
                    print("🎯 Found GENERATE_PATH_COUNT pattern!")
                    count_match = re.search(r'GENERATE_PATH_COUNT:\s*(\d+|ALL)', full_response)
                    if count_match:
                        print(f"🎯 Count match: {count_match.group(1)}")
                        learning_path_json = self._generate_path_from_csv(full_response, conversation_state)
                    else:
                        print("❌ No count match found")
                        # Generar ruta por defecto si no hay match
                        learning_path_json = self._generate_default_path_from_conversation(conversation_state)
                            
                elif "GENERATE_PATH_IDS:" in full_response:
                    learning_path_json = self._generate_path_from_csv(full_response, conversation_state)
                        
                elif "GENERATE_PATH_CATEGORY:" in full_response:
                    learning_path_json = self._generate_path_from_csv(full_response, conversation_state)
                        
                elif "GENERATE_PATH_MODULE:" in full_response:
                    learning_path_json = self._generate_path_from_csv(full_response, conversation_state)
                        
                elif "GENERATE_PATH_ALL" in full_response:
                    learning_path_json = self._generate_path_from_csv(full_response, conversation_state)
                    
                else:
                    # Si no hay patrón específico pero el usuario aprobó, generar ruta por defecto
                    learning_path_json = self._generate_default_path_from_conversation(conversation_state)
                
                # Fallback: buscar JSON tradicional
                if not learning_path_json:
                    learning_path_json = learning_path_service.extract_json_from_response(full_response)
                
                if learning_path_json:
                    print("✅ Learning path generated successfully")
                    yield "", learning_path_json
            else:
                print(f"ℹ️ Next action: {conversation_state['next_action']}. Waiting for user approval.")
                
                # Validación especial: Si hay GENERATE_PATH_COUNT pero no se aprobó la recomendación
                if "GENERATE_PATH_COUNT:" in full_response and not conversation_state["user_approved_recommendation"]:
                    print("⚠️ WARNING: Found GENERATE_PATH_COUNT but user hasn't approved recommendation yet")
                    print(f"🔍 Recommendation presented: {conversation_state['recommendation_presented']}")
                    print(f"🔍 User approved: {conversation_state['user_approved_recommendation']}")
                    
                # No generar rutas hasta que el usuario apruebe la recomendación
                pass
                    
        except Exception as e:
            print(f"❌ OpenAI API error in learning path: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f"Error en el chat: {str(e)}", None

    def _generate_path_from_csv(self, ai_response: str, conversation_state: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
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
            
            # Construir el perfil del estudiante basado en las respuestas
            if conversation_state and conversation_state.get("user_responses"):
                responses = conversation_state["user_responses"]
                student_profile = f"Objetivos: {responses.get('objectives', 'No especificado')}. "
                student_profile += f"Nivel: {responses.get('level', 'No especificado')}. "
                student_profile += f"Preferencias: {responses.get('time_preference', 'No especificado')}."
            else:
                student_profile = f"Usuario solicita {count_str} ejes temáticos"
            
            # Construir el JSON automáticamente
            learning_path_json = {
                "action": "generate_learning_path",
                "student_profile": student_profile,
                "recommended_modules": []
            }
            
            # Determinar prioridades basadas en las respuestas del usuario
            default_priority = "media"
            default_duration = "3-4 semanas"
            
            if conversation_state and conversation_state.get("user_responses"):
                time_pref = conversation_state["user_responses"].get("time_preference", "").lower()
                level = conversation_state["user_responses"].get("level", "").lower()
                
                # Ajustar duración basada en preferencias de tiempo
                if any(word in time_pref for word in ["intensivo", "rápido", "poco tiempo"]):
                    default_duration = "2-3 semanas"
                elif any(word in time_pref for word in ["relajado", "flexible", "tiempo"]):
                    default_duration = "4-5 semanas"
                
                # Ajustar prioridad basada en nivel
                if any(word in level for word in ["principiante", "novato", "empiezo"]):
                    # Para principiantes, dar alta prioridad a módulos básicos
                    pass
                elif any(word in level for word in ["avanzado", "experto", "experiencia"]):
                    # Para avanzados, dar alta prioridad a módulos complejos
                    default_priority = "alta"
            
            for i, module in enumerate(selected_modules):
                # Personalizar justificación basada en respuestas del usuario
                justification = "Eje fundamental según el curriculum STEM+"
                if conversation_state and conversation_state.get("user_responses"):
                    objectives = conversation_state["user_responses"].get("objectives", "")
                    if objectives:
                        justification = f"Relevante para tus objetivos: {objectives[:100]}{'...' if len(objectives) > 100 else ''}"
                
                path_module = {
                    "eje_tematico": module["eje_tematico"],
                    "modulo": module["modulo"],
                    "competencia": module["competencia"],
                    "categoria": module.get("categoria", "General"),
                    "justification": justification,
                    "priority": default_priority,
                    "estimated_duration": default_duration
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

    def _generate_default_path_from_conversation(self, messages: list[Dict[str, str]]) -> Optional[Dict]:
        """
        Generate a default learning path based on conversation history
        """
        try:
            # Extract user preferences from conversation
            user_topic = "General Learning"
            user_level = "beginner"
            user_goals = "Learn new skills"
            
            # Analyze conversation to extract preferences
            conversation_text = ""
            for msg in messages:
                if msg.get("role") == "user":
                    conversation_text += msg.get("content", "") + " "
            
            # Simple keyword extraction for topic
            conversation_lower = conversation_text.lower()
            if any(word in conversation_lower for word in ["python", "programming", "code"]):
                user_topic = "Python Programming"
            elif any(word in conversation_lower for word in ["web", "html", "css", "javascript"]):
                user_topic = "Web Development"
            elif any(word in conversation_lower for word in ["data", "analysis", "science"]):
                user_topic = "Data Science"
            elif any(word in conversation_lower for word in ["machine learning", "ai", "ml"]):
                user_topic = "Machine Learning"
            
            # Determine level
            if any(word in conversation_lower for word in ["beginner", "start", "new"]):
                user_level = "beginner"
            elif any(word in conversation_lower for word in ["intermediate", "some experience"]):
                user_level = "intermediate"
            elif any(word in conversation_lower for word in ["advanced", "expert", "experienced"]):
                user_level = "advanced"
            
            # Generate a default path structure
            learning_path = {
                "id": f"path_{int(time.time())}",
                "title": f"Personalized {user_topic} Learning Path",
                "description": f"A customized learning path for {user_level} level {user_topic}",
                "level": user_level,
                "topic": user_topic,
                "modules": [
                    {
                        "id": 1,
                        "title": f"Introduction to {user_topic}",
                        "description": f"Get started with the basics of {user_topic}",
                        "duration": "2-3 hours",
                        "resources": ["Reading materials", "Video tutorials"],
                        "completed": False
                    },
                    {
                        "id": 2,
                        "title": f"Practical {user_topic} Exercises",
                        "description": f"Hands-on practice with {user_topic}",
                        "duration": "3-4 hours",
                        "resources": ["Interactive exercises", "Practice projects"],
                        "completed": False
                    },
                    {
                        "id": 3,
                        "title": f"Advanced {user_topic} Concepts",
                        "description": f"Deep dive into advanced {user_topic} topics",
                        "duration": "4-5 hours",
                        "resources": ["Advanced tutorials", "Case studies"],
                        "completed": False
                    }
                ],
                "total_duration": "9-12 hours",
                "created_at": time.time()
            }
            
            print(f"✅ Generated default learning path for {user_topic} at {user_level} level")
            return learning_path
            
        except Exception as e:
            print(f"❌ Error generating default path: {e}")
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
