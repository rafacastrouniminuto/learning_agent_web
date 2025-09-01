from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from ..services.mcp_service import mcp_service_instance, MCP_AVAILABLE, search_learning_modules, get_available_thematic_axes, create_personalized_learning_path, get_user_learning_profile
from .auth import get_current_user
from ..models.user import User
from sqlalchemy.orm import Session
from ..core.database import get_db  # fixed path

router = APIRouter(prefix="/api/mcp", tags=["MCP"])

class MCPToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None

@router.get("/tools")
async def get_available_tools(current_user: User = Depends(get_current_user)):
    """Get list of available MCP tools"""
    try:
        if MCP_AVAILABLE:
            # For FastMCP, we provide a static list of available tools
            tools_info = [
                {
                    "name": "search_learning_modules",
                    "description": "Buscar módulos de aprendizaje por tema, dificultad y eje temático",
                    "parameters": ["topic", "difficulty", "eje_tematico", "limit"]
                },
                {
                    "name": "get_available_thematic_axes",
                    "description": "Obtener todos los ejes temáticos disponibles",
                    "parameters": []
                },
                {
                    "name": "create_personalized_learning_path",
                    "description": "Crear una ruta de aprendizaje personalizada",
                    "parameters": ["user_profile", "learning_goals", "time_constraints", "focus_areas"]
                },
                {
                    "name": "get_user_learning_profile",
                    "description": "Obtener el perfil de aprendizaje del usuario",
                    "parameters": ["user_id"]
                }
            ]
        else:
            # Fallback to custom service
            tools_info = await mcp_service_instance["server"].get_tools_info()
        
        return MCPResponse(success=True, data=tools_info)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.post("/call-tool")
async def call_mcp_tool(
    tool_call: MCPToolCall,
    current_user: User = Depends(get_current_user)
):
    """Call a specific MCP tool"""
    try:
        # Add user_id to parameters if needed
        if tool_call.tool_name in ["get_user_learning_profile", "get_learning_path_progress"]:
            tool_call.parameters["user_id"] = str(current_user.id)
        
        if MCP_AVAILABLE:
            # Call FastMCP functions directly
            if tool_call.tool_name == "search_learning_modules":
                result = search_learning_modules(**tool_call.parameters)
            elif tool_call.tool_name == "get_available_thematic_axes":
                result = get_available_thematic_axes()
            elif tool_call.tool_name == "create_personalized_learning_path":
                result = create_personalized_learning_path(**tool_call.parameters)
            elif tool_call.tool_name == "get_user_learning_profile":
                result = get_user_learning_profile(**tool_call.parameters)
            else:
                raise ValueError(f"Tool '{tool_call.tool_name}' not found")
        else:
            # Fallback to custom service
            result = await mcp_service_instance["server"].call_tool(tool_call.tool_name, **tool_call.parameters)
        
        return MCPResponse(success=True, data=result)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's learning profile"""
    try:
        if MCP_AVAILABLE:
            profile = get_user_learning_profile(str(current_user.id))
        else:
            profile = await mcp_service_instance["server"].get_user_learning_profile(str(current_user.id))
        return MCPResponse(success=True, data=profile)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/modules/search")
async def search_modules(
    topic: str = "",
    difficulty: str = "all",
    eje_tematico: str = "all",
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Search for learning modules"""
    try:
        if MCP_AVAILABLE:
            modules = search_learning_modules(
                topic=topic,
                difficulty=difficulty,
                eje_tematico=eje_tematico,
                limit=limit
            )
        else:
            modules = await mcp_service_instance["server"].search_learning_modules(
                topic=topic,
                difficulty=difficulty,
                eje_tematico=eje_tematico,
                limit=limit
            )
        return MCPResponse(success=True, data=modules)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/modules/axes")
async def get_thematic_axes(current_user: User = Depends(get_current_user)):
    """Get available thematic axes"""
    try:
        if MCP_AVAILABLE:
            axes = get_available_thematic_axes()
        else:
            axes = await mcp_service_instance["server"].get_available_thematic_axes()
        return MCPResponse(success=True, data=axes)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

class LearningPathRequest(BaseModel):
    learning_goals: List[str]
    time_constraints: str = "flexible"
    focus_areas: List[str] = []

@router.post("/learning-path/create")
async def create_learning_path(
    request: LearningPathRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a personalized learning path"""
    try:
        # Get user profile first
        if MCP_AVAILABLE:
            user_profile = get_user_learning_profile(str(current_user.id))
            learning_path = create_personalized_learning_path(
                user_profile=user_profile,
                learning_goals=request.learning_goals,
                time_constraints=request.time_constraints,
                focus_areas=request.focus_areas
            )
        else:
            user_profile = await mcp_service_instance["server"].get_user_learning_profile(str(current_user.id))
            learning_path = await mcp_service_instance["server"].create_personalized_learning_path(
                user_profile=user_profile,
                learning_goals=request.learning_goals,
                time_constraints=request.time_constraints,
                focus_areas=request.focus_areas
            )
        # Nuevo: persistir
        try:
            from ..models.learning_path import LearningPath
            lp = LearningPath(user_id=str(current_user.id), title=learning_path.get('title'), data=learning_path)
            db.add(lp)
            db.commit()
        except Exception:
            db.rollback()
        return MCPResponse(success=True, data=learning_path)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

class ReadinessAnalysisRequest(BaseModel):
    user_responses: Dict[str, Any]
    target_modules: List[Dict[str, Any]]

@router.post("/analyze-readiness")
async def analyze_readiness(
    request: ReadinessAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze user's readiness for specific modules"""
    try:
        if not MCP_AVAILABLE:
            # Only available in fallback mode for now
            analysis = await mcp_service_instance["server"].analyze_learning_readiness(
                user_responses=request.user_responses,
                target_modules=request.target_modules
            )
        else:
            # For FastMCP, return a placeholder response
            analysis = {
                "overall_readiness": "intermedio",
                "readiness_score": 0.7,
                "module_recommendations": [],
                "prerequisite_gaps": [],
                "strengths": [],
                "areas_for_improvement": []
            }
        return MCPResponse(success=True, data=analysis)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/progress/{path_id}")
async def get_path_progress(
    path_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific learning path"""
    try:
        if not MCP_AVAILABLE:
            progress = await mcp_service_instance["server"].get_learning_path_progress(path_id, str(current_user.id))
        else:
            # For FastMCP, return a placeholder response
            progress = {
                "path_id": path_id,
                "user_id": str(current_user.id),
                "overall_progress": 0.0,
                "completed_modules": [],
                "current_module": None,
                "next_recommended_module": None,
                "estimated_completion_date": None,
                "time_spent": "0 hours",
                "achievements": []
            }
        return MCPResponse(success=True, data=progress)
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/search-modules")
async def search_modules_endpoint(
    topic: str = "",
    difficulty: str = "",
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Search for learning modules"""
    try:
        if MCP_AVAILABLE:
            result = await search_learning_modules(
                topic=topic or "",
                difficulty=difficulty or "",
                eje_tematico="",
                limit=limit
            )
        else:
            result = await mcp_service_instance["server"].call_tool(
                "search_learning_modules",
                topic=topic,
                difficulty=difficulty,
                limit=limit
            )
        return MCPResponse(success=True, data={"modules": result})
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/thematic-axes")
async def get_thematic_axes_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Get available thematic axes"""
    try:
        if MCP_AVAILABLE:
            result = await get_available_thematic_axes()
        else:
            result = await mcp_service_instance["server"].call_tool("get_available_thematic_axes")
        return MCPResponse(success=True, data={"axes": result})
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.post("/create-path")
async def create_path_endpoint(
    request_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a personalized learning path"""
    try:
        module_ids = request_data.get("module_ids", [])
        user_profile = request_data.get("user_profile", "Usuario estándar")
        
        if MCP_AVAILABLE:
            result = await create_personalized_learning_path(
                user_profile=user_profile,
                learning_goals="Objetivos personalizados",
                time_constraints="Flexible",
                focus_areas=",".join(map(str, module_ids))
            )
        else:
            result = await mcp_service_instance["server"].call_tool(
                "create_personalized_learning_path",
                user_profile=user_profile,
                module_ids=module_ids
            )
        return MCPResponse(success=True, data={"path": result})
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/user-profile")
async def get_user_profile_endpoint(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user learning profile"""
    try:
        if MCP_AVAILABLE:
            result = await get_user_learning_profile(user_id=user_id)
        else:
            result = await mcp_service_instance["server"].call_tool(
                "get_user_learning_profile",
                user_id=user_id
            )
        return MCPResponse(success=True, data={"profile": result})
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@router.get("/health")
async def mcp_health_check():
    """Health check for MCP service"""
    try:
        server_info = mcp_service_instance["server_info"]
        
        if MCP_AVAILABLE:
            tools_list = ["search_learning_modules", "get_available_thematic_axes", "create_personalized_learning_path", "get_user_learning_profile"]
        else:
            tools_list = list(mcp_service_instance["server"].tools.keys())
        
        return MCPResponse(
            success=True,
            data={
                "status": "healthy",
                **server_info,
                "tools": tools_list
            }
        )
    except Exception as e:
        return MCPResponse(success=False, error=str(e))
