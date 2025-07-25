from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime, date
from enum import Enum

class EscenarioEnum(str, Enum):
    """Escenarios válidos para las reservas"""
    CREALAB = "CREALAB"
    INNOVALAB = "INNOVALAB"
    LEGOBOT = "LEGOBOT"
    LIVINGLAB = "LIVINGLAB"
    MAKERSPACE = "MAKERSPACE"

class HerramientasEnum(str, Enum):
    """Herramientas válidas para las reservas"""
    HERRAMIENTAS_LIVINGLAB = "HERRAMIENTAS DEL LIVINGLAB"
    IMPRESORAS_3D = "IMPRESORAS 3D"
    LEGOS = "LEGOS"
    MESA_FIRSH_LEGO = "MESA DE FIRSH LEGO"
    METAQUEST = "METAQUEST"
    KIT_ARDUINOS = "KIT ARDUINOS"
    USO_ECOSISTEMAS = "USO DE LOS ECOSISTEMAS"

class ReservationCreate(BaseModel):
    """Schema para crear una nueva reserva"""
    nombre: str = Field(..., min_length=2, max_length=255, description="Nombre completo de quien hace la reserva")
    rol_de_quien_reserva: str = Field(..., min_length=2, max_length=100, description="Rol de la persona que hace la reserva")
    objetivo: str = Field(..., min_length=10, max_length=1000, description="Propósito de la reserva")
    fecha_reserva: date = Field(..., description="Fecha específica de la reserva")
    escenario_de_la_reserva: List[EscenarioEnum] = Field(..., description="Escenarios a reservar (múltiple selección)")
    horario: str = Field(..., description="Rango de hora (ej: 08:00-10:00)")
    n_participantes: int = Field(..., gt=0, le=50, description="Número de participantes")
    herramientas: List[HerramientasEnum] = Field(..., description="Herramientas a utilizar (requerido)")
    numero_de_telefono: Optional[str] = Field(None, max_length=20, description="Número de teléfono")
    correo: EmailStr = Field(..., description="Correo electrónico")

    @validator('fecha_reserva')
    def validate_fecha_reserva(cls, v):
        """Validar que la fecha de reserva no sea en el pasado"""
        if v and v < date.today():
            raise ValueError('La fecha de reserva no puede ser en el pasado')
        return v

    @validator('escenario_de_la_reserva')
    def validate_escenarios(cls, v):
        """Validar que al menos un escenario esté seleccionado"""
        if not v or len(v) == 0:
            raise ValueError('Debe seleccionar al menos un escenario')
        return v

    @validator('herramientas')
    def validate_herramientas(cls, v):
        """Validar que al menos una herramienta esté seleccionada"""
        if not v or len(v) == 0:
            raise ValueError('Debe seleccionar al menos una herramienta')
        return v

    @validator('horario')
    def validate_horario(cls, v):
        """Validar formato de horario"""
        if not v or len(v.strip()) == 0:
            raise ValueError('El horario es requerido')
        
        # Validación básica de formato HH:MM-HH:MM
        if '-' not in v:
            raise ValueError('El horario debe tener formato HH:MM-HH:MM')
        
        parts = v.split('-')
        if len(parts) != 2:
            raise ValueError('El horario debe tener formato HH:MM-HH:MM')
        
        for part in parts:
            if ':' not in part or len(part.split(':')) != 2:
                raise ValueError('El horario debe tener formato HH:MM-HH:MM')
        
        return v.strip()

    @validator('numero_de_telefono')
    def validate_phone(cls, v):
        """Validar número de teléfono"""
        if v and v.strip():
            # Permitir "N.A" o números
            if v.strip().upper() == "N.A":
                return v.strip()
            # Remover espacios y caracteres especiales para validación
            cleaned = ''.join(filter(str.isdigit, v))
            if len(cleaned) < 7:
                raise ValueError('Número de teléfono inválido')
        return v

class ReservationUpdate(BaseModel):
    """Schema para actualizar una reserva existente"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    rol_de_quien_reserva: Optional[str] = Field(None, min_length=2, max_length=100)
    objetivo: Optional[str] = Field(None, min_length=10, max_length=1000)
    fecha_reserva: Optional[date] = None
    escenario_de_la_reserva: Optional[List[EscenarioEnum]] = None
    horario: Optional[str] = None
    n_participantes: Optional[int] = Field(None, gt=0, le=50)
    herramientas: Optional[List[HerramientasEnum]] = None
    numero_de_telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[EmailStr] = None
    status: Optional[str] = Field(None, pattern="^(active|cancelled|completed)$")

    @validator('horario')
    def validate_horario(cls, v):
        """Validar formato de horario si se proporciona"""
        if v is not None:
            return ReservationCreate.validate_horario(v)
        return v

class ReservationResponse(BaseModel):
    """Schema para respuesta de reserva"""
    n_solicitud: int
    fecha_de_solicitud: datetime
    fecha_reserva: date
    nombre: str
    rol_de_quien_reserva: str
    objetivo: str
    escenario_de_la_reserva: List[str]
    horario: str
    n_participantes: int
    herramientas: List[str]
    numero_de_telefono: Optional[str]
    correo: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReservationFilter(BaseModel):
    """Schema para filtros de búsqueda de reservas"""
    escenario: Optional[EscenarioEnum] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    nombre: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|cancelled|completed)$")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
