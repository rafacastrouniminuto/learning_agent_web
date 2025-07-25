from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Date
from sqlalchemy.sql import func
from .user import Base

class Reservation(Base):
    """Modelo para las reservas del Living Lab"""
    __tablename__ = "reservations"

    # Campos de la reserva
    n_solicitud = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_de_solicitud = Column(DateTime(timezone=True), server_default=func.now())
    fecha_reserva = Column(Date, nullable=False)  # Fecha específica de la reserva
    nombre = Column(String(255), nullable=False, index=True)
    rol_de_quien_reserva = Column(String(100), nullable=False)
    objetivo = Column(Text, nullable=False)
    escenario_de_la_reserva = Column(JSON, nullable=False)  # Lista de escenarios seleccionados
    horario = Column(String(50), nullable=False)
    n_participantes = Column(Integer, nullable=False)
    herramientas = Column(JSON, nullable=True)  # Lista de herramientas seleccionadas
    numero_de_telefono = Column(String(20), nullable=True)
    correo = Column(String(255), nullable=False)
    
    # Campos de metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(20), default="active")  # active, cancelled, completed

    def __repr__(self):
        return f"<Reservation(n_solicitud={self.n_solicitud}, nombre='{self.nombre}', escenario='{self.escenario_de_la_reserva}')>"
