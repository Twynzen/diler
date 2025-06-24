"""
Manejador de imágenes para personajes, NPCs e items
"""
import os
import hashlib
from datetime import datetime
from unity_rpg_bot.config.settings import config
from unity_rpg_bot.utils.logging import logger


class ImageHandler:
    @staticmethod
    async def save_image(attachment, entity_type, entity_name):
        """
        Guarda una imagen adjunta y retorna la URL
        
        Args:
            attachment: Archivo adjunto de Discord
            entity_type: Tipo de entidad ('personaje', 'npc', 'item')
            entity_name: Nombre de la entidad
            
        Returns:
            str: URL de la imagen guardada o None si hay error
        """
        if not attachment:
            return None
            
        try:
            # Mapeo de tipos de entidad a directorios
            dirs = {
                'personaje': config.CHAR_IMAGES,
                'npc': config.NPC_IMAGES,
                'item': config.ITEM_IMAGES
            }
            
            save_dir = dirs.get(entity_type, config.IMAGES_DIR)
            
            # Generar nombre único para el archivo
            file_ext = attachment.filename.split('.')[-1]
            file_hash = hashlib.md5(f"{entity_name}_{datetime.now()}".encode()).hexdigest()[:8]
            filename = f"{entity_name}_{file_hash}.{file_ext}"
            filepath = os.path.join(save_dir, filename)
            
            # Guardar el archivo
            await attachment.save(filepath)
            logger.info(f"✅ Imagen guardada: {filename} para {entity_type} {entity_name}")
            
            # Retornar la URL original del attachment (Discord la mantiene disponible)
            return attachment.url
            
        except Exception as e:
            logger.error(f"❌ Error guardando imagen para {entity_type} {entity_name}: {e}")
            return None
    
    @staticmethod
    def get_image_path(entity_type, entity_name, filename=None):
        """
        Obtiene la ruta de una imagen específica
        
        Args:
            entity_type: Tipo de entidad ('personaje', 'npc', 'item')
            entity_name: Nombre de la entidad
            filename: Nombre específico del archivo (opcional)
            
        Returns:
            str: Ruta completa del archivo de imagen
        """
        dirs = {
            'personaje': config.CHAR_IMAGES,
            'npc': config.NPC_IMAGES,
            'item': config.ITEM_IMAGES
        }
        
        save_dir = dirs.get(entity_type, config.IMAGES_DIR)
        
        if filename:
            return os.path.join(save_dir, filename)
        else:
            # Buscar archivos que empiecen con el nombre de la entidad
            if os.path.exists(save_dir):
                for file in os.listdir(save_dir):
                    if file.startswith(f"{entity_name}_"):
                        return os.path.join(save_dir, file)
            return None
    
    @staticmethod
    def list_entity_images(entity_type, entity_name):
        """
        Lista todas las imágenes de una entidad específica
        
        Args:
            entity_type: Tipo de entidad ('personaje', 'npc', 'item')
            entity_name: Nombre de la entidad
            
        Returns:
            list: Lista de nombres de archivos de imagen
        """
        dirs = {
            'personaje': config.CHAR_IMAGES,
            'npc': config.NPC_IMAGES,
            'item': config.ITEM_IMAGES
        }
        
        save_dir = dirs.get(entity_type, config.IMAGES_DIR)
        images = []
        
        try:
            if os.path.exists(save_dir):
                for file in os.listdir(save_dir):
                    if file.startswith(f"{entity_name}_"):
                        images.append(file)
            return images
        except Exception as e:
            logger.error(f"❌ Error listando imágenes para {entity_type} {entity_name}: {e}")
            return []
    
    @staticmethod
    def delete_entity_images(entity_type, entity_name):
        """
        Elimina todas las imágenes de una entidad
        
        Args:
            entity_type: Tipo de entidad ('personaje', 'npc', 'item')
            entity_name: Nombre de la entidad
            
        Returns:
            int: Número de archivos eliminados
        """
        images = ImageHandler.list_entity_images(entity_type, entity_name)
        deleted_count = 0
        
        dirs = {
            'personaje': config.CHAR_IMAGES,
            'npc': config.NPC_IMAGES,
            'item': config.ITEM_IMAGES
        }
        
        save_dir = dirs.get(entity_type, config.IMAGES_DIR)
        
        try:
            for image_file in images:
                file_path = os.path.join(save_dir, image_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"🗑️ Imagen eliminada: {image_file}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error eliminando imágenes para {entity_type} {entity_name}: {e}")
            return 0


# Instancia global del manejador de imágenes
image_handler = ImageHandler()