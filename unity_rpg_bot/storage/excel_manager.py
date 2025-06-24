"""
Gestor de archivos Excel para estadísticas de personajes
"""
import os
import pandas as pd
from unity_rpg_bot.config.settings import config
from unity_rpg_bot.config.constants import BASE_ATTRIBUTES
from unity_rpg_bot.utils.logging import logger


class ExcelManager:
    @staticmethod
    def create_character_excel(character_name, user_id, initial_stats=None):
        """
        Crea un archivo Excel para un nuevo personaje
        
        Args:
            character_name: Nombre del personaje
            user_id: ID del usuario de Discord
            initial_stats: Estadísticas iniciales del personaje
            
        Returns:
            str: Ruta del archivo Excel creado
        """
        if initial_stats is None:
            initial_stats = {}
            
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        
        # Datos de estadísticas del personaje
        character_data = {
            'Atributo': BASE_ATTRIBUTES,
            'Valor': [
                initial_stats.get('fuerza', 10), 
                initial_stats.get('destreza', 10),
                initial_stats.get('velocidad', 10), 
                initial_stats.get('resistencia', 10),
                initial_stats.get('inteligencia', 10), 
                initial_stats.get('mana', 10)
            ]
        }
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Hoja de estadísticas
                df_stats = pd.DataFrame(character_data)
                df_stats.to_excel(writer, sheet_name='Estadisticas', index=False)
                
                # Hoja de información del personaje
                info_data = {
                    'Campo': ['Nombre', 'Usuario_ID', 'Oro'],
                    'Valor': [character_name, str(user_id), 0]
                }
                df_info = pd.DataFrame(info_data)
                df_info.to_excel(writer, sheet_name='Info', index=False)
            
            logger.info(f"✅ Excel creado para {character_name}")
            return file_path
            
        except Exception as e:
            logger.error(f"❌ Error creando Excel para {character_name}: {e}")
            raise
    
    @staticmethod
    def read_character_stats(character_name):
        """
        Lee las estadísticas de un personaje desde su archivo Excel
        
        Args:
            character_name: Nombre del personaje
            
        Returns:
            dict: Estadísticas del personaje o None si hay error
        """
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Archivo Excel no encontrado para {character_name}")
            return None
            
        try:
            df = pd.read_excel(file_path, sheet_name='Estadisticas')
            stats = {}
            
            for _, row in df.iterrows():
                attr_name = row['Atributo'].lower()
                stats[attr_name] = {
                    'base': int(row['Valor']), 
                    'bonus': 0, 
                    'total': int(row['Valor'])
                }
                
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error leyendo stats de {character_name}: {e}")
            return None
    
    @staticmethod
    def update_character_stats(character_name, new_stats):
        """
        Actualiza las estadísticas de un personaje en su archivo Excel
        
        Args:
            character_name: Nombre del personaje
            new_stats: Diccionario con nuevas estadísticas
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Archivo Excel no encontrado para {character_name}")
            return False
            
        try:
            # Leer archivos existentes
            with pd.ExcelFile(file_path) as xls:
                df_stats = pd.read_excel(xls, sheet_name='Estadisticas')
                df_info = pd.read_excel(xls, sheet_name='Info')
            
            # Actualizar estadísticas
            for idx, row in df_stats.iterrows():
                attr_name = row['Atributo'].lower()
                if attr_name in new_stats:
                    df_stats.at[idx, 'Valor'] = new_stats[attr_name]
            
            # Guardar cambios
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_stats.to_excel(writer, sheet_name='Estadisticas', index=False)
                df_info.to_excel(writer, sheet_name='Info', index=False)
            
            logger.info(f"✅ Stats actualizadas para {character_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando stats de {character_name}: {e}")
            return False
    
    @staticmethod
    def archive_character(character_name):
        """
        Mueve el archivo Excel de un personaje a la carpeta de archivados
        
        Args:
            character_name: Nombre del personaje
            
        Returns:
            bool: True si el archivado fue exitoso
        """
        try:
            import shutil
            active_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
            archived_path = f"{config.EXCEL_DIR}/archivados/{character_name}.xlsx"
            
            if os.path.exists(active_path):
                shutil.move(active_path, archived_path)
                logger.info(f"📁 Excel movido a archivados: {character_name}")
                return True
            else:
                logger.warning(f"⚠️ Archivo Excel no encontrado para archivar: {character_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error archivando {character_name}: {e}")
            return False


# Instancia global del gestor de Excel
excel_manager = ExcelManager()