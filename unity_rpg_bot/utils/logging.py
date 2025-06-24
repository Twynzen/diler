"""
Sistema de logging para Unity RPG Bot
"""
import logging
import os
from unity_rpg_bot.config.settings import config


def setup_logging():
    """Configura el sistema de logging para el bot"""
    
    # Crear directorio de logs si no existe
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    
    # Configurar el logger principal
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{config.LOGS_DIR}/unity.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Logger específico para el bot
    logger = logging.getLogger("UnityRPG")
    
    return logger


# Logger global
logger = setup_logging()