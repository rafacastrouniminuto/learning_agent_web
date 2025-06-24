from .services.openai_service import openai_service
from .services.mcp_service import mcp_service_instance

def initialize_mcp_integration():
    """Initialize MCP integration with OpenAI service"""
    try:
        # The new OpenAI service already has MCP integration built-in
        # via the mcp_service_instance import
        print("✅ MCP Integration: OpenAI service initialized with MCP tools")
        print(f"✅ MCP Implementation: {mcp_service_instance['server_info']['implementation']}")
    except Exception as e:
        print(f"❌ MCP Integration Error: {e}")

# Initialize on import
initialize_mcp_integration()
