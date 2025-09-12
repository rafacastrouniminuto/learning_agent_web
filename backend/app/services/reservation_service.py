from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime, date

from ..models.reservation import Reservation
from ..schemas.reservation import ReservationCreate, ReservationUpdate, ReservationFilter

class ReservationService:
    """Servicio para manejo de reservas del Living Lab"""

    @staticmethod
    def create_reservation(db: Session, reservation_data: ReservationCreate) -> Reservation:
        """Crear una nueva reserva"""
        
        # Convertir herramientas enum a strings para JSON
        herramientas_list = [tool.value for tool in reservation_data.herramientas]
        
        # Convertir escenarios enum a strings para JSON
        escenarios_list = [escenario.value for escenario in reservation_data.escenario_de_la_reserva]
        
        db_reservation = Reservation(
            nombre=reservation_data.nombre,
            rol_de_quien_reserva=reservation_data.rol_de_quien_reserva,
            objetivo=reservation_data.objetivo,
            fecha_reserva=reservation_data.fecha_reserva,
            escenario_de_la_reserva=escenarios_list,
            horario=reservation_data.horario,
            n_participantes=reservation_data.n_participantes,
            herramientas=herramientas_list,
            numero_de_telefono=reservation_data.numero_de_telefono,
            correo=reservation_data.correo
        )
        
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation

    @staticmethod
    def get_reservation(db: Session, n_solicitud: int) -> Optional[Reservation]:
        """Obtener una reserva por número de solicitud"""
        return db.query(Reservation).filter(Reservation.n_solicitud == n_solicitud).first()

    @staticmethod
    def get_reservations(
        db: Session, 
        filters: ReservationFilter,
        user_email: Optional[str] = None
    ) -> List[Reservation]:
        """Obtener reservas con filtros"""
        
        print(f"🔍 SERVICE DEBUG - get_reservations llamado con user_email: {user_email}")
        
        query = db.query(Reservation)
        
        # Filtro por usuario (si se especifica)
        if user_email:
            query = query.filter(Reservation.correo == user_email)
        
        # Aplicar filtros
        if filters.escenario:
            # Buscar reservas que contengan el escenario especificado en su lista
            query = query.filter(func.json_extract(Reservation.escenario_de_la_reserva, '$') == filters.escenario.value)
        
        if filters.nombre:
            query = query.filter(Reservation.nombre.ilike(f"%{filters.nombre}%"))
        
        if filters.status:
            query = query.filter(Reservation.status == filters.status)
        
        if filters.fecha_inicio:
            query = query.filter(Reservation.fecha_de_solicitud >= filters.fecha_inicio)
        
        if filters.fecha_fin:
            query = query.filter(Reservation.fecha_de_solicitud <= filters.fecha_fin)
        
        # Ordenar por fecha de solicitud descendente (más recientes primero)
        query = query.order_by(desc(Reservation.fecha_de_solicitud))
        
        # Aplicar paginación
        query = query.offset(filters.offset).limit(filters.limit)
        
        return query.all()

    @staticmethod
    def update_reservation(
        db: Session, 
        n_solicitud: int, 
        reservation_update: ReservationUpdate
    ) -> Optional[Reservation]:
        """Actualizar una reserva existente"""
        
        db_reservation = ReservationService.get_reservation(db, n_solicitud)
        if not db_reservation:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = reservation_update.dict(exclude_unset=True)
        
        # Manejar herramientas si se actualizan
        if 'herramientas' in update_data and update_data['herramientas'] is not None:
            herramientas_list = [tool.value for tool in update_data['herramientas']]
            update_data['herramientas'] = herramientas_list
        
        # Manejar escenarios si se actualizan
        if 'escenario_de_la_reserva' in update_data and update_data['escenario_de_la_reserva'] is not None:
            escenarios_list = [escenario.value for escenario in update_data['escenario_de_la_reserva']]
            update_data['escenario_de_la_reserva'] = escenarios_list
        
        # rol_de_quien_reserva ahora es string, no necesita conversión
        
        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(db_reservation, field, value)
        
        db.commit()
        db.refresh(db_reservation)
        return db_reservation

    @staticmethod
    def cancel_reservation(db: Session, n_solicitud: int) -> Optional[Reservation]:
        """Cancelar una reserva"""
        db_reservation = ReservationService.get_reservation(db, n_solicitud)
        if not db_reservation:
            return None
        
        db_reservation.status = "cancelled"
        db.commit()
        db.refresh(db_reservation)
        return db_reservation

    @staticmethod
    def get_reservation_statistics(db: Session) -> dict:
        """Obtener estadísticas de reservas"""
        
        total_reservations = db.query(Reservation).count()
        active_reservations = db.query(Reservation).filter(Reservation.status == "active").count()
        cancelled_reservations = db.query(Reservation).filter(Reservation.status == "cancelled").count()
        completed_reservations = db.query(Reservation).filter(Reservation.status == "completed").count()
        
        # Reservas por escenario - esto será más complejo con arrays JSON
        # Por ahora, contar todas las reservas sin desglosar por escenario específico
        escenarios_stats = []
        
        # Reservas del último mes
        last_month = datetime.now().replace(day=1)
        recent_reservations = db.query(Reservation).filter(
            Reservation.fecha_de_solicitud >= last_month
        ).count()
        
        return {
            "total_reservations": total_reservations,
            "active_reservations": active_reservations,
            "cancelled_reservations": cancelled_reservations,
            "completed_reservations": completed_reservations,
            "escenarios_stats": {},  # Simplificado por ahora
            "recent_reservations": recent_reservations
        }

    @staticmethod
    def check_availability(
        db: Session, 
        escenarios: List[str], 
        fecha: date, 
        horario: str
    ) -> bool:
        """Verificar disponibilidad de escenarios en una fecha y horario específicos"""
        
        # Buscar reservas activas que contengan cualquiera de los escenarios solicitados
        for escenario in escenarios:
            existing_reservations = db.query(Reservation).filter(
                and_(
                    func.json_extract(Reservation.escenario_de_la_reserva, '$') == escenario,
                    func.date(Reservation.fecha_de_solicitud) == fecha,
                    Reservation.horario == horario,
                    Reservation.status == "active"
                )
            ).count()
            
            # Si algún escenario ya está reservado, no hay disponibilidad
            if existing_reservations > 0:
                return False
        
        return True

# Instancia del servicio
reservation_service = ReservationService()
