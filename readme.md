# Asistente IA con Google Calendar y Gmail

Este proyecto implementa un asistente personal basado en IA que puede buscar correos electrónicos en Gmail y programar eventos en Google Calendar, todo a través de comandos en lenguaje natural. El asistente utiliza CrewAI para gestionar agentes y tareas, y puede ser accedido a través de un bot de Telegram.

## Ejemplo

![Vista previa del asistente](img/demo.jpg)

## Características

- Búsqueda de correos en Gmail con consultas en lenguaje natural (Vistas previas de los correos)
- Creación de eventos en Google Calendar especificando título, fecha, hora y participantes
- Interfaz conversacional a través de Telegram
- Procesamiento de lenguaje natural con modelos LLM avanzados

## Requisitos previos

- Python 3.10 o superior
- Una cuenta de Google con Gmail y Calendar
- API Key de OpenAI
- Bot de Telegram (opcional para la funcionalidad de mensajería)

## Configuración

1. Clona este repositorio:
   ```bash
   git clone https://github.com/AndresRoblesB/crewai-assistant-google-tools.git
   cd crewai-assistant-google-tools
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura tus credenciales:
   - Crea un archivo `.env` con las siguientes variables:
     ```
     TELEGRAM_TOKEN=tu_token_de_telegram
     OPENAI_API_KEY=tu_api_key_de_openai
     OPENAI_MODEL_NAME=gpt-4 # o el modelo que prefieras
     ```
   - Descarga el archivo `credentials.json` desde la consola de Google Cloud para OAuth (sigue las instrucciones en la sección de Autenticación de Google)

## Autenticación de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita las APIs de Gmail y Calendar
4. Configura las credenciales OAuth:
   - Crea credenciales OAuth 2.0 para aplicación de escritorio
   - Descarga el archivo JSON de credenciales y guárdalo como `credentials.json` en la raíz del proyecto

## Uso

### Ejecutar el bot de Telegram:

```bash
python bot.py
```

La primera vez que ejecutes el script, se abrirá una ventana del navegador para que autorices el acceso a tu cuenta de Google.

### Ejemplos de comandos:

- "Busca correos sobre el proyecto X"
- "Programa una reunión para revisar el diseño mañana a las 3 PM con ana@example.com"
- "Crea un evento de almuerzo con cliente para el 20 de mayo a las 13:00"

## Estructura del proyecto

- `bot.py`: Punto de entrada principal con la integración de Telegram
- `crew.py`: Configuración de agentes y tareas de CrewAI
- `tools/`: Herramientas específicas para interactuar con los servicios
  - `gmail_tools.py`: Herramientas para buscar en Gmail
  - `calendar_tools.py`: Herramientas para gestionar el calendario
- `utils/`: Funciones auxiliares
  - `google_auth.py`: Manejo de autenticación con Google

## Contribuciones
Esto e sun proyecto de prueba o practica, sin embargo, si lo quieres mejorar eres libre de mandar Pull Request

## Pruebas locales sin Telegram

Para probar la funcionalidad sin usar Telegram, puedes descomentar y modificar la sección de pruebas directas en `bot.py`:

```python
# Descomenta para probar directamente desde la consola
import asyncio
async def run_test():
    await test_crew_directly("Busca correos sobre facturación")
    # o
    await test_crew_directly("Crea un evento para reunión de equipo mañana a las 15:00")

if __name__ == '__main__':
    # Comenta esta línea para no iniciar el bot de Telegram
    # main_telegram_bot()
    
    # Descomenta para ejecutar pruebas directas
    asyncio.run(run_test())
```

## Limitaciones

- Se requiere autorización inicial a través de OAuth para acceder a las APIs de Google
- Las consultas deben ser claras y específicas para obtener los mejores resultados
- El token de acceso a Google expira y necesita renovarse ocasionalmente
- No tiene manejo de sesiones, por lo tanto no guarda los mensajes enviados y no tiene la capacidad de recordarlos
