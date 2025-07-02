#!/usr/bin/env python3
"""
Script simplificado para generar diagramas PNG del sistema Learning Agent Web
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.saas.chat import Slack
from diagrams.generic.database import SQL
from diagrams.generic.network import Router
from diagrams.generic.storage import Storage
import os

def create_architecture_diagram():
    """Crear diagrama de arquitectura general simplificado"""
    with Diagram("Learning Agent Web - Arquitectura General", 
                 filename="architecture_overview", 
                 show=False):
        
        # Frontend
        user = Users("Frontend\n(Jinja2 + CSS/JS)")
        
        # API Layer
        api = FastAPI("FastAPI\nREST Endpoints")
        
        # Services
        with Cluster("Services"):
            openai_svc = Python("OpenAI Service")
            mcp_svc = Python("MCP Service")
            learning_svc = Python("Learning Path Service")
        
        # Data
        with Cluster("Data Layer"):
            db = SQL("SQLite Database")
            csv = Storage("CSV Data")
            external = Router("External APIs")
        
        # Connections
        user >> api
        api >> openai_svc
        api >> mcp_svc
        api >> learning_svc
        
        openai_svc >> external
        mcp_svc >> csv
        learning_svc >> db

def create_database_schema():
    """Crear diagrama de esquema de base de datos"""
    with Diagram("Learning Agent Web - Database Schema", 
                 filename="database_schema", 
                 show=False):
        
        # Tables
        users = SQL("Users Table")
        learning_paths = SQL("Learning Paths Table")
        
        # External Data
        csv_data = Storage("learning_modules.csv")
        openai_api = Router("OpenAI API")
        
        # Relationships
        users >> Edge(label="1:N") >> learning_paths
        csv_data >> users
        openai_api >> users

def create_chat_flow():
    """Crear diagrama de flujo del chat IA"""
    with Diagram("Learning Agent Web - Flujo del Chat IA", 
                 filename="chat_flow", 
                 show=False):
        
        user = Users("Usuario")
        auth = Router("Autenticación JWT")
        parser = Python("Parse Request")
        openai = Python("OpenAI Service")
        response = Router("Stream Response")
        save = SQL("Guardar Conversación")
        
        # Flow
        user >> auth >> parser >> openai >> response >> save

def create_mcp_components():
    """Crear diagrama de componentes MCP"""
    with Diagram("Learning Agent Web - Arquitectura MCP", 
                 filename="mcp_components", 
                 show=False):
        
        fastmcp = Router("FastMCP SDK")
        
        with Cluster("MCP Tools"):
            search = Router("Search Modules")
            accessibility = Router("Accessibility Tools")
        
        with Cluster("APIs"):
            health = FastAPI("Health API")
            modules = FastAPI("Modules API")
        
        data = Storage("CSV Data")
        
        # Connections
        fastmcp >> search
        fastmcp >> accessibility
        search >> health
        accessibility >> modules
        health >> data
        modules >> data

def create_auth_flow():
    """Crear diagrama de flujo de autenticación"""
    with Diagram("Learning Agent Web - Flujo de Autenticación", 
                 filename="auth_flow", 
                 show=False):
        
        user = Users("Usuario")
        token_check = Router("Verificar Token")
        login = Users("Login Form")
        validate = Python("Validar Credenciales")
        generate = Python("Generar JWT")
        access = Router("Acceso Concedido")
        
        # Main flow
        user >> token_check >> access
        
        # Login flow
        login >> validate >> generate >> access

def main():
    """Generar todos los diagramas"""
    print("🎨 Generando diagramas PNG simplificados...")
    
    try:
        print("📊 Creando diagrama de arquitectura general...")
        create_architecture_diagram()
        
        print("🗄️ Creando diagrama de esquema de base de datos...")
        create_database_schema()
        
        print("💬 Creando diagrama de flujo del chat IA...")
        create_chat_flow()
        
        print("🔌 Creando diagrama de componentes MCP...")
        create_mcp_components()
        
        print("🔐 Creando diagrama de flujo de autenticación...")
        create_auth_flow()
        
        print("✅ ¡Todos los diagramas PNG han sido generados exitosamente!")
        
        # Listar archivos generados
        png_files = [f for f in os.listdir('.') if f.endswith('.png')]
        print(f"\n📁 Archivos PNG generados ({len(png_files)}):")
        for file in sorted(png_files):
            print(f"  - {file}")
            
    except Exception as e:
        print(f"❌ Error generando diagramas: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
