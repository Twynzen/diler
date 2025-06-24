"""
Configuración principal del bot Unity RPG
"""
import os
from dotenv import load_dotenv


class UnityConfig:
    def __init__(self):
        load_dotenv()
        
        # Configuración Discord y servicios externos
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        self.BOT_NAME = os.getenv('BOT_NAME', 'UnityRPG')
        self.GUILD_NAME = os.getenv('GUILD_NAME', 'Servidor Unity')
        self.GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'google-credentials.json')
        
        # Directorios del sistema
        self.DATA_DIR = "unity_data"
        self.EXCEL_DIR = f"{self.DATA_DIR}/personajes"
        self.IMAGES_DIR = f"{self.DATA_DIR}/imagenes"
        self.LOGS_DIR = f"{self.DATA_DIR}/logs"
        self.DB_PATH = f"{self.DATA_DIR}/unity_master.db"
        
        # Subdirectorios para imágenes
        self.CHAR_IMAGES = f"{self.IMAGES_DIR}/personajes"
        self.NPC_IMAGES = f"{self.IMAGES_DIR}/npcs"
        self.ITEM_IMAGES = f"{self.IMAGES_DIR}/items"
        
        # Crear directorios necesarios
        self.create_directories()
        
    def create_directories(self):
        """Crea todos los directorios necesarios para el funcionamiento del bot"""
        dirs = [
            self.DATA_DIR, self.EXCEL_DIR, self.IMAGES_DIR, self.LOGS_DIR,
            f"{self.EXCEL_DIR}/activos", f"{self.EXCEL_DIR}/archivados",
            self.CHAR_IMAGES, self.NPC_IMAGES, self.ITEM_IMAGES
        ]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)


# Instancia global de configuración
config = UnityConfig()