#!/usr/bin/env python3
"""
Script para actualizar la base de datos con la nueva estructura
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models.reservation import Reservation

def migrate_database():
    """Migrar la base de datos para agregar las columnas faltantes"""
    
    print("🔄 Iniciando migración de base de datos...")
    
    # Crear session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Verificar si la tabla existe
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='reservations'"))
        table_exists = result.fetchone()
        
        if not table_exists:
            print("📋 La tabla 'reservations' no existe. Creando desde cero...")
            Base.metadata.create_all(bind=engine)
            print("✅ Tabla 'reservations' creada exitosamente")
            return
        
        # Verificar si la columna fecha_reserva existe
        result = session.execute(text("PRAGMA table_info(reservations)"))
        columns = result.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Columnas existentes: {column_names}")
        
        if 'fecha_reserva' not in column_names:
            print("🔧 Agregando columna 'fecha_reserva'...")
            session.execute(text("ALTER TABLE reservations ADD COLUMN fecha_reserva DATE"))
            session.commit()
            print("✅ Columna 'fecha_reserva' agregada exitosamente")
        else:
            print("✅ Columna 'fecha_reserva' ya existe")
            
        # Verificar otras columnas que puedan faltar
        expected_columns = [
            'n_solicitud', 'fecha_de_solicitud', 'fecha_reserva', 'nombre', 
            'rol_de_quien_reserva', 'objetivo', 'escenario_de_la_reserva', 
            'horario', 'n_participantes', 'herramientas', 'numero_de_telefono', 
            'correo', 'created_at', 'updated_at', 'status'
        ]
        
        missing_columns = [col for col in expected_columns if col not in column_names]
        
        if missing_columns:
            print(f"⚠️  Columnas faltantes detectadas: {missing_columns}")
            print("🔄 Recreando tabla con estructura completa...")
            
            # Respaldar datos existentes
            result = session.execute(text("SELECT * FROM reservations"))
            existing_data = result.fetchall()
            
            # Eliminar tabla existente
            session.execute(text("DROP TABLE reservations"))
            session.commit()
            
            # Crear nueva tabla
            Base.metadata.create_all(bind=engine)
            print("✅ Tabla recreada con estructura completa")
            
            # Restaurar datos si los había
            if existing_data:
                print("🔄 Restaurando datos existentes...")
                # Aquí se podría agregar lógica para restaurar datos
                print("⚠️  Datos existentes requerirán migración manual")
        
        print("✅ Migración completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_database()
