from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import contextlib

from .core.config import settings
from .core.database import get_db, Base, engine
from .api.auth import router as auth_router, get_current_user
from .api.chat import router as chat_router
from .api.mcp import router as mcp_router
from .api.reservations import router as reservations_router
from .models.user import User
from .models.reservation import Reservation
from .models.learning_path import LearningPath
from .services.mcp_service import mcp_service_instance, MCP_AVAILABLE
from . import integrations  # Initialize MCP integration

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=settings.templates_dir)

# Mount MCP server if FastMCP is available
if MCP_AVAILABLE and hasattr(mcp_service_instance["server"], 'streamable_http_app'):
    try:
        # Mount the FastMCP server using streamable HTTP transport
        mcp_app = mcp_service_instance["server"].streamable_http_app()
        app.mount("/mcp", mcp_app)
        print("✅ FastMCP server montado en /mcp")
    except Exception as e:
        print(f"⚠️  Error montando FastMCP server: {e}")

# Include API routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(mcp_router)
app.include_router(reservations_router)

# Web Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to dashboard"""
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)  
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat page"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/learning-paths", response_class=HTMLResponse)
async def learning_paths_page(request: Request):
    """Learning paths page"""
    return templates.TemplateResponse("learning_paths.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Profile page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/mcp-tools", response_class=HTMLResponse)
async def mcp_tools_page(request: Request):
    """MCP Tools testing page"""
    return templates.TemplateResponse("mcp_tools.html", {"request": request})

@app.get("/reservations", response_class=HTMLResponse)
async def reservations_page(request: Request):
    """Reservations management page"""
    return templates.TemplateResponse("reservations.html", {"request": request})

@app.get("/my-reservations")
async def my_reservations_page(request: Request):
    """Página de mis reservas"""
    return templates.TemplateResponse("my_reservations_simple.html", {"request": request})

@app.get("/test-debug")
async def test_debug_page(request: Request):
    """Página de test de debugging"""
    return templates.TemplateResponse("test_debug.html", {"request": request})

@app.get("/test-frontend", response_class=HTMLResponse)
async def test_frontend(request: Request):
    """Test frontend page"""
    with open("test_frontend.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)

@app.get("/debug-tabs", response_class=HTMLResponse)
async def debug_tabs(request: Request):
    """Debug tabs page"""
    with open("debug_tabs.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.version}

@app.post("/api/learning-paths", response_model=dict)
async def save_learning_path(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Espera un objeto con la ruta generada en 'data' y opcionalmente 'title'
    if "data" not in payload:
        raise HTTPException(status_code=400, detail="Falta 'data' con la ruta")

    # Guardar siempre una nueva versión
    lp = LearningPath(
        user_id=str(current_user.id),
        title=payload.get("title") or payload["data"].get("title"),
        data=payload["data"]
    )
    db.add(lp)
    db.commit()
    db.refresh(lp)
    return {"id": lp.id, "title": lp.title, "created_at": str(lp.created_at)}

@app.get("/api/learning-paths/me", response_model=dict)
async def get_my_learning_paths(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(LearningPath).filter(LearningPath.user_id == str(current_user.id)).order_by(LearningPath.created_at.desc()).all()
    return {"items": [{"id": r.id, "title": r.title, "created_at": str(r.created_at), "data": r.data} for r in rows]}

@app.get("/api/learning-paths/latest", response_model=dict)
async def get_latest_learning_path(request: Request, db: Session = Depends(get_db)):
    try:
        # Try to get current user, but don't fail if not authenticated
        from .api.auth import get_current_user_optional
        current_user = await get_current_user_optional(request, db)
        
        if not current_user:
            print("🔍 DEBUG - No authenticated user for learning path request")
            return {"item": None}
        
        print(f"🔍 DEBUG - Looking for learning path for user {current_user.email} (ID: {current_user.id})")
        row = db.query(LearningPath).filter(LearningPath.user_id == str(current_user.id)).order_by(LearningPath.created_at.desc()).first()
        if not row:
            print(f"🔍 DEBUG - No learning path found for user {current_user.email}")
            return {"item": None}
        
        print(f"✅ Found learning path for user {current_user.email} created at {row.created_at}")
        return {"item": {"id": row.id, "title": row.title, "created_at": str(row.created_at), "data": row.data}}
    except Exception as e:
        print(f"❌ Error getting learning path: {e}")
        # If authentication fails, return None instead of error
        return {"item": None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
