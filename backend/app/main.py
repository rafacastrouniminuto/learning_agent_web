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
from .models.user import User
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
