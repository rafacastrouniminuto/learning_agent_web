from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ..core.database import get_db
from ..schemas.reservation import (
    ReservationCreate, 
    ReservationUpdate, 
    ReservationResponse, 
    ReservationFilter,
    EscenarioEnum,
    HerramientasEnum
)
from ..services.reservation_service import reservation_service

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva reserva del Living Lab"""
    try:
        # Verificar disponibilidad (opcional)
        # availability = reservation_service.check_availability(
        #     db, 
        #     reservation.escenario_de_la_reserva.value,
        #     datetime.now().date(),
        #     reservation.horario
        # )
        # if not availability:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="El escenario no está disponible para el horario seleccionado"
        #     )
        
        db_reservation = reservation_service.create_reservation(db, reservation)
        return db_reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando reserva: {str(e)}")

@router.get("/", response_model=List[ReservationResponse])
async def get_reservations(
    escenario: Optional[EscenarioEnum] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    nombre: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^(active|cancelled|completed)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de reservas con filtros opcionales"""
    
    filters = ReservationFilter(
        escenario=escenario,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        nombre=nombre,
        status=status,
        limit=limit,
        offset=offset
    )
    
    reservations = reservation_service.get_reservations(db, filters, user_email)
    return reservations

@router.get("/{n_solicitud}", response_model=ReservationResponse)
async def get_reservation(
    n_solicitud: int,
    db: Session = Depends(get_db)
):
    """Obtener una reserva específica por número de solicitud"""
    
    reservation = reservation_service.get_reservation(db, n_solicitud)
    if not reservation:
        raise HTTPException(
            status_code=404,
            detail=f"Reserva con número {n_solicitud} no encontrada"
        )
    return reservation

@router.put("/{n_solicitud}", response_model=ReservationResponse)
async def update_reservation(
    n_solicitud: int,
    reservation_update: ReservationUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una reserva existente"""
    
    updated_reservation = reservation_service.update_reservation(
        db, n_solicitud, reservation_update
    )
    
    if not updated_reservation:
        raise HTTPException(
            status_code=404,
            detail=f"Reserva con número {n_solicitud} no encontrada"
        )
    
    return updated_reservation

@router.delete("/{n_solicitud}", response_model=ReservationResponse)
async def cancel_reservation(
    n_solicitud: int,
    db: Session = Depends(get_db)
):
    """Cancelar una reserva (marcar como cancelada)"""
    
    cancelled_reservation = reservation_service.cancel_reservation(db, n_solicitud)
    
    if not cancelled_reservation:
        raise HTTPException(
            status_code=404,
            detail=f"Reserva con número {n_solicitud} no encontrada"
        )
    
    return cancelled_reservation

@router.get("/stats/overview")
async def get_reservation_statistics(db: Session = Depends(get_db)):
    """Obtener estadísticas generales de reservas"""
    
    stats = reservation_service.get_reservation_statistics(db)
    return stats

@router.get("/availability/check")
async def check_availability(
    escenario: EscenarioEnum,
    fecha: date,
    horario: str,
    db: Session = Depends(get_db)
):
    """Verificar disponibilidad de un escenario en fecha y horario específicos"""
    
    available = reservation_service.check_availability(
        db, escenario.value, fecha, horario
    )
    
    return {
        "available": available,
        "escenario": escenario.value,
        "fecha": fecha.isoformat(),
        "horario": horario
    }

@router.get("/enums/escenarios")
async def get_available_escenarios():
    """Obtener lista de escenarios disponibles"""
    return {
        "escenarios": [{"value": e.value, "label": e.value} for e in EscenarioEnum]
    }

@router.get("/enums/herramientas")
async def get_available_herramientas():
    """Obtener lista de herramientas disponibles"""
    return {
        "herramientas": [{"value": h.value, "label": h.value} for h in HerramientasEnum]
    }
