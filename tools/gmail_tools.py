import logging
import json
from crewai.tools import BaseTool
from utils.google_auth import get_google_credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class SearchGmailTool(BaseTool):
    name: str = "SearchGmailTool"
    description: str = """
    Busca correos electrónicos en la cuenta de Gmail del usuario. 
    La entrada es un string JSON con una clave 'query' que contiene los términos de búsqueda. 
    Ejemplo: '{"query": "actualizaciones de proyecto"}'
    """
    
    def _run(self, query_json_str: str) -> str:
        """Implementación de la búsqueda de correos"""
        try:
            data = json.loads(query_json_str)
            query = data.get("query")
            if not query:
                return "Error: La consulta de búsqueda (query) es necesaria en el JSON de entrada."
        except json.JSONDecodeError:
            # Si no es JSON, asumir que es una query directa por simplicidad para el LLM
            query = query_json_str 
        except Exception as e:
            return f"Error al parsear la entrada para search_emails: {str(e)}"

        logger.info(f"GoogleServices: Buscando correos con query: {query}")
        
        # Obtener el servicio de Gmail
        credentials = get_google_credentials()
        service = build('gmail', 'v1', credentials=credentials)
        
        results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "No se encontraron correos que coincidan con tu búsqueda."
        
        email_details = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Sin asunto')
            from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Desconocido')
            snippet = msg.get('snippet', 'No hay vista previa disponible')
            email_details.append({
                'subject': subject,
                'from': from_header,
                'snippet': snippet,
                'id': message['id']
            })
        
        result_text = "Estos son los correos que encontré:\n\n"
        for i, email in enumerate(email_details, 1):
            result_text += f"{i}. De: {email['from']}\n   Asunto: {email['subject']}\n   Vista previa: {email['snippet'][:100]}...\n\n"
        return result_text