import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent, Task

from tools.gmail_tools import SearchGmailTool
from tools.calendar_tools import CreateCalendarEventTool

# Configuración de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no encontrada en las variables de entorno.")

# Definición de los agentes con CrewAI
def setup_crew():
    llm = ChatOpenAI(
        model_name=OPENAI_MODEL_NAME,
        temperature=0.2  # Un poco menos de creatividad para tareas directas
    )
    
    # Instanciando las herramientas
    search_email_tool = SearchGmailTool()
    create_calendar_event_tool = CreateCalendarEventTool()
    
    # Agente principal que interpreta y decide qué herramienta usar.
    personal_assistant_agent = Agent(
        role='Asistente Personal Inteligente',
        goal='Interpretar las solicitudes del usuario y utilizar las herramientas adecuadas para buscar correos electrónicos o programar eventos en el calendario. Debes pedir clarificación si la información es ambigua o insuficiente para usar una herramienta y debes responderle al usuario los datos de confirmación del evento: link, el titulo, la descripción, hora y a quién se citó.',
        backstory=(
            "Eres un asistente personal altamente eficiente. Tu especialidad es comprender las necesidades del usuario "
            "a partir de texto en lenguaje natural. Una vez que entiendes la solicitud, identificas la acción principal "
            "(buscar correos o crear evento) y los parámetros necesarios. Luego, utilizas la herramienta correcta para "
            "cumplir la solicitud. Si faltan detalles cruciales (ej. qué buscar en correos, o título/hora para un evento), "
            "debes indicarlo claramente en tu respuesta final."
        ),
        verbose=True,
        llm=llm,
        tools=[search_email_tool, create_calendar_event_tool],
        allow_delegation=False  # Este agente ejecutará las herramientas directamente
    )
    
    return personal_assistant_agent

# Tareas para los agentes
def create_main_task(agent, user_query):
    # Tarea única que el agente principal ejecutará.
    # El LLM del agente decidirá qué herramienta usar basado en la descripción de la herramienta y la consulta.

    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return Task(
        description=f"""
        Procesa la siguiente solicitud del usuario: -- {user_query} --.
        Tu objetivo es cumplir la solicitud utilizando una de tus herramientas: SearchGmailTool o CreateCalendarEventTool.

        Pasos a seguir:
        1. Analiza la solicitud para identificar la intención principal: ¿es buscar correos o crear un evento de calendario?
        2. Extrae todos los parámetros necesarios para la herramienta correspondiente.
           - Para SearchGmailTool: necesitas una 'query' de búsqueda.
           - Para CreateCalendarEventTool: necesitas 'summary' (título), 'start_time_iso' (en formato YYYY-MM-DDTHH:MM:SS). 
             Opcionalmente puedes tener 'attendees' (lista de emails), 'description', 'location'.
             Si el usuario da una fecha relativa como "mañana a las 10 AM", debes convertirla a formato ISO.
             Hoy es {fecha_actual}. Considera esto para fechas relativa y te doy un ejemplo, si hoy es 2025-05-10T23:40:00
              y te dicen que mañana a las 10 PM entonces el start_time_iso es 2025-05-11T22:00:00.

             Si no tienes los datos cómo el titulo disponible entonces infierelo    
        3. Prepara la entrada para la herramienta en el formato JSON string requerido por la descripción de la herramienta.
        4. Ejecuta la herramienta con la entrada preparada.
        5. Si la solicitud es ambigua o falta información crítica para usar una herramienta (por ejemplo, si piden crear un evento pero no dan título ni hora, o si piden buscar correos pero no dicen qué buscar), responde indicando qué información falta. NO intentes adivinar parámetros cruciales.
        6. Tu respuesta final debe ser el resultado de la herramienta o el mensaje de clarificación. En dado caso de que programes el evento especifica al usuario el link del evento, el  titulo que le pusiste, descripción, hora y a quién citaste cuando sea así.
        
        Ejemplos de cómo podrías procesar:
        - Usuario: "Busca correos de marketing sobre el nuevo producto."
          Acción: Usar SearchGmailTool con input {{"query": "marketing nuevo producto"}}
        - Usuario: "Programa una reunión para discutir el presupuesto mañana a las 2 PM con jefe@example.com"
          Acción: (Asumiendo que mañana es 2025-05-11) Usar CreateCalendarEventTool con input 
                  {{"summary": "Discutir presupuesto", "start_time_iso": "2025-05-11T14:00:00", "attendees": ["jefe@example.com"]}}
        - Usuario: "Necesito agendar algo."
          Acción: Responder "Por favor, especifica qué quieres agendar, incluyendo título, fecha y hora."
        """,
        agent=agent,
        expected_output="El resultado directo de la herramienta utilizada (resultados de búsqueda o confirmación de evento) o un mensaje pidiendo clarificación si la información es insuficiente. "
    )