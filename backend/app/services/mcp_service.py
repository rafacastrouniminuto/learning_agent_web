from typing import Dict, Any, List, Optional
import json
import csv
import asyncio
from pathlib import Path
from ..core.config import settings
from .learning_path_service import learning_path_service

# MCP official imports
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
    print("✅ MCP: FastMCP SDK cargado correctamente")
except ImportError as e:
    print(f"⚠️  MCP: FastMCP SDK no disponible, usando implementación custom: {e}")
    MCP_AVAILABLE = False

# Global FastMCP instance - initialized outside the class to use decorators
mcp_server = None
modules_data = []

def initialize_mcp_data():
    """Initialize modules data"""
    global modules_data
    try:
        csv_path = Path(settings.base_dir) / "data" / "learning_modules.csv"
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                raw_data = list(reader)
                
                # Convert CSV format to expected module format
                modules_data = []
                for i, row in enumerate(raw_data):
                    module = {
                        "id": f"mod_{i+1}",
                        "nombre": row.get('modulo', ''),
                        "descripcion": row.get('competencia', ''),
                        "eje_tematico": row.get('eje_tematico', ''),
                        "nivel_dificultad": "intermedio",  # Default value
                        "duracion_estimada": "4 horas",  # Default value
                        "prerrequisitos": "",
                        "competencias": row.get('competencia', ''),
                        "tipo_contenido": "teórico-práctico",
                        "modalidad": "presencial",
                        "prioridad": "media",
                        "preguntas": row.get('preguntas', '')
                    }
                    modules_data.append(module)
                    
            print(f"✅ MCP: Loaded {len(modules_data)} learning modules")
        else:
            print(f"⚠️  MCP: No modules file found at {csv_path}")
    except Exception as e:
        print(f"❌ Error loading modules: {e}")

def load_evaluation_questions():
    """Load evaluation questions from CSV"""
    try:
        csv_path = Path(settings.base_dir) / "data" / "preguntas_evaluacion.csv"
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                questions = list(reader)
                print(f"✅ Loaded {len(questions)} evaluation questions")
                return questions
        else:
            print("⚠️ Evaluation questions CSV not found")
            return []
    except Exception as e:
        print(f"❌ Error loading evaluation questions: {e}")
        return []
    except Exception as e:
        print(f"❌ MCP: Error loading modules: {e}")

# Initialize MCP server with FastMCP if available
if MCP_AVAILABLE:
    try:
        mcp_server = FastMCP(settings.mcp_server_name)
        initialize_mcp_data()
        print("✅ MCP: FastMCP server inicializado correctamente")
    except Exception as e:
        print(f"❌ MCP: Error inicializando FastMCP server: {e}")
        mcp_server = None
        MCP_AVAILABLE = False

# MCP Tool Functions using FastMCP decorators (if available)
if MCP_AVAILABLE and mcp_server:
    
    @mcp_server.tool()
    def search_learning_modules(
        topic: str = "",
        difficulty: str = "all", 
        eje_tematico: str = "all",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Buscar módulos de aprendizaje por tema, dificultad y eje temático"""
        results = []
        topic_lower = topic.lower() if topic else ""
        
        for module in modules_data:
            # Filter by topic (search in name and description)
            if topic_lower and topic_lower not in module.get('nombre', '').lower() and topic_lower not in module.get('descripcion', '').lower():
                continue
                
            # Filter by difficulty
            if difficulty != "all" and module.get('nivel_dificultad', '').lower() != difficulty.lower():
                continue
                
            # Filter by thematic axis
            if eje_tematico != "all" and module.get('eje_tematico', '').lower() != eje_tematico.lower():
                continue
            
            results.append({
                "id": module.get('id', ''),
                "nombre": module.get('nombre', ''),
                "descripcion": module.get('descripcion', ''),
                "eje_tematico": module.get('eje_tematico', ''),
                "nivel_dificultad": module.get('nivel_dificultad', ''),
                "duracion_estimada": module.get('duracion_estimada', ''),
                "prerrequisitos": module.get('prerrequisitos', ''),
                "competencias": module.get('competencias', ''),
                "tipo_contenido": module.get('tipo_contenido', ''),
                "modalidad": module.get('modalidad', ''),
                "prioridad": module.get('prioridad', 'media')
            })
            
            if len(results) >= limit:
                break
        
        return results

    @mcp_server.tool()
    def get_available_thematic_axes() -> List[str]:
        """Obtener todos los ejes temáticos disponibles de los módulos de aprendizaje"""
        axes = set()
        for module in modules_data:
            if module.get('eje_tematico'):
                axes.add(module.get('eje_tematico'))
        return sorted(list(axes))

    @mcp_server.tool()
    def create_personalized_learning_path(
        user_profile: Dict[str, Any], 
        learning_goals: List[str],
        time_constraints: str = "flexible",
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """Crear una ruta de aprendizaje personalizada basada en el perfil del usuario y objetivos"""
        
        if focus_areas is None:
            focus_areas = []
        
        # Get relevant modules based on goals and focus areas
        relevant_modules = []
        
        for goal in learning_goals:
            modules = search_learning_modules(topic=goal, limit=5)
            relevant_modules.extend(modules)
        
        for area in focus_areas:
            modules = search_learning_modules(eje_tematico=area, limit=3)
            relevant_modules.extend(modules)
        
        # Remove duplicates
        seen_ids = set()
        unique_modules = []
        for module in relevant_modules:
            if module['id'] not in seen_ids:
                unique_modules.append(module)
                seen_ids.add(module['id'])
        
        # Sort by priority and difficulty
        def sort_key(module):
            priority_order = {'alta': 1, 'media': 2, 'baja': 3}
            difficulty_order = {'principiante': 1, 'intermedio': 2, 'avanzado': 3}
            
            priority = priority_order.get(module.get('prioridad', 'media').lower(), 2)
            difficulty = difficulty_order.get(module.get('nivel_dificultad', 'intermedio').lower(), 2)
            
            return (priority, difficulty)
        
        unique_modules.sort(key=sort_key)
        
        # Calculate total duration
        total_hours = 0
        for module in unique_modules:
            duration_str = module.get('duracion_estimada', '0 horas')
            try:
                hours = int(''.join(filter(str.isdigit, duration_str)))
                total_hours += hours
            except:
                total_hours += 2  # Default 2 hours if parsing fails
        
        if total_hours < 24:
            estimated_duration = f"{total_hours} horas"
        else:
            weeks = total_hours // 40  # Assuming 40 hours per week
            remaining_hours = total_hours % 40
            if remaining_hours > 0:
                estimated_duration = f"{weeks} semanas y {remaining_hours} horas"
            else:
                estimated_duration = f"{weeks} semanas"
        
        # Create the learning path structure
        learning_path = {
            "path_id": f"path_{user_profile.get('user_id', 'anonymous')}_{len(learning_goals)}",
            "title": f"Ruta Personalizada: {', '.join(learning_goals[:2])}{'...' if len(learning_goals) > 2 else ''}",
            "user_id": user_profile.get('user_id'),
            "learning_goals": learning_goals,
            "focus_areas": focus_areas,
            "estimated_duration": estimated_duration,
            "difficulty_level": user_profile.get('preferred_difficulty', 'intermedio'),
            "modules": unique_modules[:8],  # Limit to 8 modules for now
            "created_at": "2024-12-20",
            "status": "draft",
            "completion_percentage": 0,
            "recommendations": _generate_recommendations(unique_modules, user_profile)
        }
        
        return learning_path

    @mcp_server.tool()
    def get_user_learning_profile(user_id: str) -> Dict[str, Any]:
        """Obtener el perfil de aprendizaje y preferencias del usuario del sistema"""
        # In a real implementation, this would query the database
        # For now, we'll return a structured profile template
        return {
            "user_id": user_id,
            "learning_style": "visual",  # visual, auditory, kinesthetic, reading
            "preferred_difficulty": "intermedio",  # principiante, intermedio, avanzado
            "goals": [],  # Will be populated from chat interaction
            "background": "",  # Will be populated from chat interaction
            "interests": [],  # STEM+ areas of interest
            "time_availability": "flexible",  # flexible, limited, intensive
            "completion_rate": 0.0,  # Historical completion rate
            "preferred_modules": []  # Modules they've shown interest in
        }

    def _generate_recommendations(modules: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on selected modules and user profile"""
        recommendations = []
        
        # Analyze difficulty progression
        difficulties = [module.get('nivel_dificultad', 'intermedio') for module in modules]
        if 'avanzado' in difficulties and 'principiante' not in difficulties:
            recommendations.append("Considera agregar módulos básicos para fortalecer fundamentos")
        
        # Analyze thematic diversity
        themes = set(module.get('eje_tematico', '') for module in modules)
        if len(themes) < 2:
            recommendations.append("Tu ruta se enfoca en un área específica - considera diversificar con otros ejes temáticos")
        
        # Time management recommendations
        total_duration = len(modules) * 3  # Rough estimate
        if total_duration > 20:
            recommendations.append("Esta es una ruta intensiva - considera dividirla en fases")
        
        return recommendations

else:
    # Fallback function definitions when FastMCP is not available
    def search_learning_modules(topic: str = "", difficulty: str = "all", eje_tematico: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
        """Fallback function - not available without FastMCP"""
        return []
    
    def get_available_thematic_axes() -> List[str]:
        """Fallback function - not available without FastMCP"""
        return []
    
    def create_personalized_learning_path(user_profile: Dict[str, Any], learning_goals: List[str], time_constraints: str = "flexible", focus_areas: List[str] = None) -> Dict[str, Any]:
        """Fallback function - not available without FastMCP"""
        return {}
    
    def get_user_learning_profile(user_id: str) -> Dict[str, Any]:
        """Fallback function - not available without FastMCP"""
        return {}
    
    def _generate_recommendations(modules: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[str]:
        """Fallback function - not available without FastMCP"""
        return []

# Fallback implementation for when MCP is not available
class MCPService:
    def __init__(self):
        self.server_name = settings.mcp_server_name
        self.server_version = settings.mcp_server_version
        self.tools = {}
        self.modules_data = []
        self._setup_tools()
        self._load_modules_data()    
    def _load_modules_data(self):
        """Load learning modules from CSV"""
        try:
            csv_path = Path(settings.base_dir) / "data" / "learning_modules.csv"
            if csv_path.exists():
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    self.modules_data = list(reader)
                print(f"✅ MCP: Loaded {len(self.modules_data)} learning modules")
            else:
                print(f"⚠️  MCP: No modules file found at {csv_path}")
        except Exception as e:
            print(f"❌ MCP: Error loading modules: {e}")
    
    def _setup_tools(self):
        """Setup MCP tools for learning agent"""
        
        # Register tools in our internal dictionary
        self.tools = {
            "get_user_learning_profile": {
                "function": self.get_user_learning_profile,
                "description": "Get user's learning profile and preferences from the system",
                "parameters": {"user_id": str}
            },
            "search_learning_modules": {
                "function": self.search_learning_modules,
                "description": "Search for learning modules by topic, difficulty, and thematic axis",
                "parameters": {
                    "topic": str,
                    "difficulty": str,
                    "eje_tematico": str,
                    "limit": int
                }
            },
            "get_available_thematic_axes": {
                "function": self.get_available_thematic_axes,
                "description": "Get all available thematic axes from the learning modules",
                "parameters": {}
            },
            "create_personalized_learning_path": {
                "function": self.create_personalized_learning_path,
                "description": "Create a personalized learning path based on user profile and goals",
                "parameters": {
                    "user_profile": dict,
                    "learning_goals": list,
                    "time_constraints": str,
                    "focus_areas": list
                }
            },
            "analyze_learning_readiness": {
                "function": self.analyze_learning_readiness,
                "description": "Analyze user's readiness for specific learning modules",
                "parameters": {
                    "user_responses": dict,
                    "target_modules": list
                }
            },
            "get_learning_path_progress": {
                "function": self.get_learning_path_progress,
                "description": "Get progress information for a learning path",
                "parameters": {
                    "path_id": str,
                    "user_id": str
                }
            }
        }

    async def get_user_learning_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user's learning profile and preferences from the system"""
        # In a real implementation, this would query the database
        # For now, we'll return a structured profile template
        return {
            "user_id": user_id,
            "learning_style": "visual",  # visual, auditory, kinesthetic, reading
            "preferred_difficulty": "intermedio",  # principiante, intermedio, avanzado
            "goals": [],  # Will be populated from chat interaction
            "background": "",  # Will be populated from chat interaction
            "interests": [],  # STEM+ areas of interest
            "time_availability": "flexible",  # flexible, limited, intensive
            "completion_rate": 0.0,  # Historical completion rate
            "preferred_modules": []  # Modules they've shown interest in
        }
    
    async def search_learning_modules(
        self, 
        topic: str = "", 
        difficulty: str = "all", 
        eje_tematico: str = "all",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for learning modules by topic, difficulty, and thematic axis"""
        
        results = []
        topic_lower = topic.lower() if topic else ""
        
        for module in self.modules_data:
            # Filter by topic (search in name and description)
            if topic_lower and topic_lower not in module.get('nombre', '').lower() and topic_lower not in module.get('descripcion', '').lower():
                continue
                
            # Filter by difficulty
            if difficulty != "all" and module.get('nivel_dificultad', '').lower() != difficulty.lower():
                continue
                
            # Filter by thematic axis
            if eje_tematico != "all" and module.get('eje_tematico', '').lower() != eje_tematico.lower():
                continue
            
            results.append({
                "id": module.get('id', ''),
                "nombre": module.get('nombre', ''),
                "descripcion": module.get('descripcion', ''),
                "eje_tematico": module.get('eje_tematico', ''),
                "nivel_dificultad": module.get('nivel_dificultad', ''),
                "duracion_estimada": module.get('duracion_estimada', ''),
                "prerrequisitos": module.get('prerrequisitos', ''),
                "competencias": module.get('competencias', ''),
                "tipo_contenido": module.get('tipo_contenido', ''),
                "modalidad": module.get('modalidad', ''),
                "prioridad": module.get('prioridad', 'media')
            })
            
            if len(results) >= limit:
                break
        
        return results
    
    async def get_available_thematic_axes(self) -> List[str]:
        """Get all available thematic axes from the learning modules"""
        axes = set()
        for module in self.modules_data:
            if module.get('eje_tematico'):
                axes.add(module.get('eje_tematico'))
        return sorted(list(axes))
    
    async def create_personalized_learning_path(
        self,
        user_profile: Dict[str, Any], 
        learning_goals: List[str],
        time_constraints: str = "flexible",
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """Create a personalized learning path based on user profile and goals"""
        
        if focus_areas is None:
            focus_areas = []
        
        # Get relevant modules based on goals and focus areas
        relevant_modules = []
        
        for goal in learning_goals:
            modules = await self.search_learning_modules(topic=goal, limit=5)
            relevant_modules.extend(modules)
        
        for area in focus_areas:
            modules = await self.search_learning_modules(eje_tematico=area, limit=3)
            relevant_modules.extend(modules)
        
        # Remove duplicates
        seen_ids = set()
        unique_modules = []
        for module in relevant_modules:
            if module['id'] not in seen_ids:
                unique_modules.append(module)
                seen_ids.add(module['id'])
        
        # Sort by priority and difficulty
        def sort_key(module):
            priority_order = {'alta': 1, 'media': 2, 'baja': 3}
            difficulty_order = {'principiante': 1, 'intermedio': 2, 'avanzado': 3}
            
            priority = priority_order.get(module.get('prioridad', 'media').lower(), 2)
            difficulty = difficulty_order.get(module.get('nivel_dificultad', 'intermedio').lower(), 2)
            
            return (priority, difficulty)
        
        unique_modules.sort(key=sort_key)
        
        # Create the learning path structure
        learning_path = {
            "path_id": f"path_{user_profile.get('user_id', 'anonymous')}_{len(learning_goals)}",
            "title": f"Ruta Personalizada: {', '.join(learning_goals[:2])}{'...' if len(learning_goals) > 2 else ''}",
            "user_id": user_profile.get('user_id'),
            "learning_goals": learning_goals,
            "focus_areas": focus_areas,
            "estimated_duration": self._calculate_total_duration(unique_modules),
            "difficulty_level": user_profile.get('preferred_difficulty', 'intermedio'),
            "modules": unique_modules[:8],  # Limit to 8 modules for now
            "created_at": "2024-12-20",
            "status": "draft",
            "completion_percentage": 0,
            "recommendations": self._generate_recommendations(unique_modules, user_profile)
        }
        
        return learning_path
    
    async def analyze_learning_readiness(
        self,
        user_responses: Dict[str, Any],
        target_modules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user's readiness for specific learning modules"""
        
        readiness_analysis = {
            "overall_readiness": "intermedio",
            "readiness_score": 0.7,
            "module_recommendations": [],
            "prerequisite_gaps": [],
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # Analyze each module
        for module in target_modules:
            module_analysis = {
                "module_id": module.get('id'),
                "module_name": module.get('nombre'),
                "readiness_level": "ready",  # ready, needs_preparation, not_ready
                "confidence_score": 0.8,
                "missing_prerequisites": [],
                "preparation_suggestions": []
            }
            
            # Check prerequisites
            prereqs = module.get('prerrequisitos', '').split(',') if module.get('prerrequisitos') else []
            for prereq in prereqs:
                prereq = prereq.strip()
                if prereq and not self._check_prerequisite_met(prereq, user_responses):
                    module_analysis["missing_prerequisites"].append(prereq)
                    module_analysis["readiness_level"] = "needs_preparation"
                    module_analysis["confidence_score"] -= 0.2
            
            readiness_analysis["module_recommendations"].append(module_analysis)
        
        return readiness_analysis
    
    async def get_learning_path_progress(self, path_id: str, user_id: str) -> Dict[str, Any]:
        """Get progress information for a learning path"""
        # In a real implementation, this would query the database
        return {
            "path_id": path_id,
            "user_id": user_id,
            "overall_progress": 0.0,
            "completed_modules": [],
            "current_module": None,
            "next_recommended_module": None,
            "estimated_completion_date": None,
            "time_spent": "0 hours",
            "achievements": []
        }
    
    def _calculate_total_duration(self, modules: List[Dict[str, Any]]) -> str:
        """Calculate total estimated duration for a set of modules"""
        total_hours = 0
        for module in modules:
            duration_str = module.get('duracion_estimada', '0 horas')
            # Extract hours from duration string
            try:
                hours = int(''.join(filter(str.isdigit, duration_str)))
                total_hours += hours
            except:
                total_hours += 2  # Default 2 hours if parsing fails
        
        if total_hours < 24:
            return f"{total_hours} horas"
        else:
            weeks = total_hours // 40  # Assuming 40 hours per week
            remaining_hours = total_hours % 40
            if remaining_hours > 0:
                return f"{weeks} semanas y {remaining_hours} horas"
            else:
                return f"{weeks} semanas"
    
    def _generate_recommendations(self, modules: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on selected modules and user profile"""
        recommendations = []
        
        # Analyze difficulty progression
        difficulties = [module.get('nivel_dificultad', 'intermedio') for module in modules]
        if 'avanzado' in difficulties and 'principiante' not in difficulties:
            recommendations.append("Considera agregar módulos básicos para fortalecer fundamentos")
        
        # Analyze thematic diversity
        themes = set(module.get('eje_tematico', '') for module in modules)
        if len(themes) < 2:
            recommendations.append("Tu ruta se enfoca en un área específica - considera diversificar con otros ejes temáticos")
        
        # Time management recommendations
        total_duration = len(modules) * 3  # Rough estimate
        if total_duration > 20:
            recommendations.append("Esta es una ruta intensiva - considera dividirla en fases")
        
        return recommendations
    
    def _check_prerequisite_met(self, prerequisite: str, user_responses: Dict[str, Any]) -> bool:
        """Check if a prerequisite is met based on user responses"""
        # Simple implementation - in reality this would be more sophisticated
        prerequisite_lower = prerequisite.lower()
        
        # Check if mentioned in user responses
        for key, value in user_responses.items():
            if isinstance(value, str) and prerequisite_lower in value.lower():
                return True
        
        return False

    def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server"""
        return {
            "server_name": self.server_name,
            "server_version": self.server_version,
            "official_mcp": False,
            "modules_loaded": len(self.modules_data),
            "tools_available": len(self.tools),
            "implementation": "custom"
        }
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a specific MCP tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool_func = self.tools[tool_name]["function"]
        return await tool_func(**kwargs)
    
    async def get_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available MCP tools"""
        return [
            {
                "name": "get_user_learning_profile",
                "description": "Get user's learning profile and preferences",
                "parameters": ["user_id"]
            },
            {
                "name": "search_learning_modules", 
                "description": "Search for learning modules by various criteria",
                "parameters": ["topic", "difficulty", "eje_tematico", "limit"]
            },
            {
                "name": "get_available_thematic_axes",
                "description": "Get all available thematic axes",
                "parameters": []
            },
            {
                "name": "create_personalized_learning_path",
                "description": "Create a personalized learning path",
                "parameters": ["user_profile", "learning_goals", "time_constraints", "focus_areas"]
            },
            {
                "name": "analyze_learning_readiness",
                "description": "Analyze user's readiness for specific modules", 
                "parameters": ["user_responses", "target_modules"]
            },
            {
                "name": "get_learning_path_progress",
                "description": "Get progress information for a learning path",
                "parameters": ["path_id", "user_id"]
            }
        ]

    def get_app(self):
        """Get MCP service instance (always custom for fallback)"""
        return self

# Create service instance - use FastMCP if available, otherwise fallback
def get_mcp_service():
    """Get the appropriate MCP service instance"""
    if MCP_AVAILABLE and mcp_server:
        return {
            "server": mcp_server,
            "server_info": {
                "server_name": settings.mcp_server_name,
                "server_version": settings.mcp_server_version,
                "official_mcp": True,
                "modules_loaded": len(modules_data),
                "tools_available": 4,  # Number of registered tools
                "implementation": "official"
            }
        }
    else:
        fallback_service = MCPService()
        return {
            "server": fallback_service,
            "server_info": fallback_service.get_server_info()
        }

# Global service instance
mcp_service_instance = get_mcp_service()
mcp_service = mcp_service_instance["server"]

# Additional functions for evaluation questions
def get_evaluation_questions(licenciatura=None):
    """Get evaluation questions, optionally filtered by degree"""
    questions = load_evaluation_questions()
    
    # Always include general questions
    filtered_questions = [q for q in questions if not q.get('licenciatura_especifica') or q.get('licenciatura_especifica') == '']
    
    # Add specific questions for the degree if provided
    if licenciatura:
        specific_questions = [q for q in questions if q.get('licenciatura_especifica') == licenciatura]
        filtered_questions.extend(specific_questions)
    
    return filtered_questions

def format_questions_for_chat():
    """Format questions for chat presentation"""
    questions = load_evaluation_questions()
    
    formatted = {
        "escala": [],
        "abiertas_generales": [],
        "abiertas_especificas": {}
    }
    
    for q in questions:
        if q['tipo'] == 'escala':
            formatted["escala"].append({
                "categoria": q['categoria'],
                "pregunta": q['pregunta'],
                "escala": f"{q['escala_min']}-{q['escala_max']}"
            })
        elif q['tipo'] == 'abierta':
            if q['licenciatura_especifica']:
                if q['licenciatura_especifica'] not in formatted["abiertas_especificas"]:
                    formatted["abiertas_especificas"][q['licenciatura_especifica']] = []
                formatted["abiertas_especificas"][q['licenciatura_especifica']].append({
                    "categoria": q['categoria'],
                    "pregunta": q['pregunta']
                })
            else:
                formatted["abiertas_generales"].append({
                    "categoria": q['categoria'],
                    "pregunta": q['pregunta']
                })
    
    return formatted
