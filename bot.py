import os
import logging
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from crew import setup_crew, create_main_task
from crewai import Crew, Process

# Configuración de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_TOKEN no encontrado. El bot de Telegram no funcionará.")

# Diccionario para mantener el estado de las conversaciones de los usuarios
user_contexts = {}

async def execute_crew_instruction(update_or_context, text: str, is_telegram_context: bool = True):
    """
    Procesa una instrucción utilizando CrewAI y envía la respuesta.
    Puede ser llamado desde Telegram (con 'update') o directamente (con un 'context' simulado).
    """
    reply_func = update_or_context.message.reply_text if is_telegram_context else print

    await reply_func("⏳ Procesando tu solicitud con CrewAI...")

    try:
        # Configurar CrewAI
        assistant_agent = setup_crew()
        task = create_main_task(assistant_agent, text)

        # Crear la tripulación
        crew = Crew(
            agents=[assistant_agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )

        # Ejecutar el crew
        result = crew.kickoff()
        
        logger.info(f"Resultado de CrewAI: {result}")
        await reply_func(f"🤖 Asistente:\n{result}")

    except Exception as e:
        logger.error(f"Error procesando instrucción con CrewAI: {str(e)}", exc_info=True)
        await reply_func(f"Lo siento, ocurrió un error al procesar tu solicitud con CrewAI: {str(e)}")


# --- Funciones de Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"¡Hola {user.mention_html()}! 👋\n\n"
        "Soy tu asistente personal IA. Puedo ayudarte a buscar en tus correos y gestionar tu calendario.\n"
        "Envíame una instrucción por texto",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Comandos y Uso*\n\n"
        "/start - Inicia la conversación\n"
        "/help - Muestra este mensaje\n\n"
        "📝 *Ejemplos de instrucciones:*\n\n"
        "• \"Busca correos sobre la reunión de proyecto X\"\n"
        "• \"Programa una reunión para 'Revisión de diseño' mañana a las 3 PM con ana.perez@example.com\"\n"
        "• \"¿Tengo correos de mi jefe sobre el reporte trimestral?\"\n"
        "• \"Crea un evento llamado 'Almuerzo con cliente' para el 20 de mayo de 2025 a la 13:00\"\n",
        parse_mode='Markdown'
    )

async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await execute_crew_instruction(update, update.message.text)

async def test_crew_directly(instruction: str):
    """Función para probar CrewAI sin Telegram."""
    print(f"\n--- Probando instrucción: \"{instruction}\" ---")
    
    # Para simular el objeto update:
    class MockMessage:
        async def reply_text(self, text_response):
            print(text_response)
    class MockUpdateForDirectTest:
        message = MockMessage()

    await execute_crew_instruction(MockUpdateForDirectTest(), instruction, is_telegram_context=True)

def main_telegram_bot():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN no está configurado. El bot no puede iniciar.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    logger.info("Iniciando bot de Telegram...")
    application.run_polling()

if __name__ == '__main__':
    # Para ejecutar el bot de Telegram
    main_telegram_bot()
    
    # Para probar directamente desde la consola, descomenta:
    # import asyncio
    # asyncio.run(test_crew_directly("Crea un evento en el calendario para hoy a las 09:30 PM sobre estudio de IA Y cita a ejemplo@email.com"))