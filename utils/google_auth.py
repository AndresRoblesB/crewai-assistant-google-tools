import os
import logging
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Configuración de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración para Google API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/calendar']

def get_google_credentials():
    """
    Obtiene las credenciales OAuth2 para los servicios de Google.
    Si no existen credenciales válidas, inicia el flujo de autorización.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing token: {e}. Se necesitará nueva autorización.")
                creds = None # Forzar nueva autorización
        if not creds: # Si creds es None después del intento de refresh o si no existía
            if not os.path.exists('credentials.json'):
                logger.error("credentials.json no encontrado. Por favor, descárgalo desde Google Cloud Console y colócalo en el directorio.")
                raise FileNotFoundError("credentials.json no encontrado.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds