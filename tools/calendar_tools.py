import logging
import json
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional, List, Type
from crewai.tools import BaseTool
from utils.google_auth import get_google_credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class EventDetails(BaseModel):
    """Esquema para los datos de creación de eventos"""
    summary: str = Field(..., description="Título del evento", examples=["Reunión de equipo"])
    start_time_iso: str = Field(..., description="Fecha y hora de inicio en formato ISO (YYYY-MM-DDTHH:MM:SS)", 
                            examples=["2025-05-15T14:00:00"])
    attendees: Optional[List[str]] = Field(None, description="Lista de correos de invitados")
    description: Optional[str] = Field(None, description="Descripción detallada del evento")
    location: Optional[str] = Field(None, description="Ubicación física del evento")

class CreateCalendarEventTool(BaseTool):
    name: str = "CreateCalendarEventTool"
    description: str = """
    Crea un nuevo evento en el Google Calendar del usuario.
    La entrada es un string JSON que especifica 'summary' (título), 'start_time_iso' (fecha y hora de inicio en formato ISO YYYY-MM-DDTHH:MM:SS), 
    y opcionalmente 'attendees' (lista de correos), 'description', 'location'.
    Ejemplo: '{"summary": "Reunión de equipo", "start_time_iso": "2025-07-21T14:00:00", "attendees": ["colega@example.com"]}'
    """
    args_schema: Type[BaseModel] = EventDetails

    def _run(self, **kwargs) -> str:
        """Implementación de la creación de eventos"""
        try:
            event_data = kwargs
            
            summary = event_data.get("summary")
            start_time_str = event_data.get("start_time_iso")
            
            if not summary or not start_time_str:
                return "Error: 'summary' y 'start_time_iso' son requeridos en el JSON de entrada."

            start_time = datetime.fromisoformat(start_time_str)
            # Por defecto, los eventos duran 1 hora si no se especifica otra cosa
            end_time = start_time + timedelta(hours=1) 

            attendees = event_data.get("attendees") # lista de emails
            description = event_data.get("description", "Evento creado por Asistente IA")
            location = event_data.get("location")

        except json.JSONDecodeError:
            return "Error: La entrada para crear evento debe ser un string JSON válido."
        except ValueError:
            return "Error: 'start_time_iso' debe estar en formato ISO correcto (ej: 2025-05-15T10:00:00)."
        except Exception as e:
            return f"Error al parsear la entrada para create_calendar_event: {str(e)}"

        logger.info(f"GoogleServices: Creando evento: {summary} a las {start_time.isoformat()}")
        
        # Obtener servicio de Calendar
        credentials = get_google_credentials()
        service = build('calendar', 'v3', credentials=credentials)
        
        event_body = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Bogota', # AJUSTA A TU ZONA HORARIA LOCAL o hazla configurable
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Bogota', # AJUSTA A TU ZONA HORARIA LOCAL
            },
        }
        
        if attendees and isinstance(attendees, list):
            event_body['attendees'] = [{'email': email.strip()} for email in attendees]
            event_body['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            }
        
        try:
            created_event = service.events().insert(calendarId='primary', body=event_body, sendUpdates='all' if attendees else 'none').execute()
            return f"Evento creado exitosamente: {created_event.get('htmlLink')} y del detalle del evento es {event_body}"
        except Exception as e:
            logger.error(f"Error creando evento en Google Calendar: {e}")
            return f"Error al crear el evento en Google Calendar: {str(e)}"