from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application
    app_name: str = "Learning Agent - Living Lab UNIMINUTO"
    debug: bool = True
    version: str = "1.0.0"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite:///./learning_agent.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    
    # MCP
    mcp_server_name: str = "learning-agent-mcp"
    mcp_server_version: str = "1.0.0"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    static_dir: str = str(Path(__file__).parent.parent / "static")
    templates_dir: str = str(Path(__file__).parent.parent.parent / "templates")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
