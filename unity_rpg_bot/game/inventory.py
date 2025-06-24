"""
Sistema de inventario y equipamiento para Unity RPG Bot
"""
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.utils.logging import logger


class InventorySystem:
    @staticmethod
    def calculate_equipped_bonuses(character_name):
        """
        Calcula los bonos totales de todos los items equipados por un personaje
        
        Args:
            character_name: Nombre del personaje
            
        Returns:
            dict: Bonos por cada atributo
        """
        bonuses = {
            attr: 0 for attr in ['fuerza', 'destreza', 'velocidad', 'resistencia', 'inteligencia', 'mana']
        }
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.efecto_fuerza, i.efecto_destreza, i.efecto_velocidad,
                           i.efecto_resistencia, i.efecto_inteligencia, i.efecto_mana
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ? AND inv.equipado = TRUE
                """, (character_name,))
                
                for row in cursor.fetchall():
                    attrs = ['fuerza', 'destreza', 'velocidad', 'resistencia', 'inteligencia', 'mana']
                    for i, attr in enumerate(attrs):
                        bonuses[attr] += row[i] or 0
                        
        except Exception as e:
            logger.error(f"❌ Error calculando bonuses para {character_name}: {e}")
            
        return bonuses
    
    @staticmethod
    def get_character_inventory(character_name):
        """
        Obtiene el inventario completo de un personaje
        
        Args:
            character_name: Nombre del personaje
            
        Returns:
            list: Lista de items en el inventario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.nombre, i.tipo, i.rareza, inv.cantidad, inv.equipado,
                           i.efecto_fuerza, i.efecto_destreza, i.efecto_velocidad,
                           i.efecto_resistencia, i.efecto_inteligencia, i.efecto_mana,
                           i.descripcion, i.precio
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ?
                    ORDER BY inv.equipado DESC, i.nombre
                """, (character_name,))
                
                return cursor.fetchall()
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo inventario de {character_name}: {e}")
            return []
    
    @staticmethod
    def get_equipable_items(character_name):
        """
        Obtiene solo los items equipables de un personaje
        
        Args:
            character_name: Nombre del personaje
            
        Returns:
            list: Lista de items equipables
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.nombre, inv.equipado, i.rareza
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ? AND i.es_equipable = TRUE
                    ORDER BY inv.equipado DESC, i.nombre
                """, (character_name,))
                
                return cursor.fetchall()
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo items equipables de {character_name}: {e}")
            return []
    
    @staticmethod
    def toggle_item_equipment(character_name, item_name):
        """
        Alterna el estado de equipamiento de un item
        
        Args:
            character_name: Nombre del personaje
            item_name: Nombre del item
            
        Returns:
            tuple: (éxito: bool, nuevo_estado: str, mensaje: str)
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar que el personaje tiene el item
                cursor.execute("""
                    SELECT inv.id, inv.equipado 
                    FROM inventarios inv
                    JOIN personajes p ON inv.personaje_id = p.id
                    JOIN items i ON inv.item_id = i.id
                    WHERE p.nombre = ? AND i.nombre = ?
                """, (character_name, item_name))
                
                result = cursor.fetchone()
                if not result:
                    return False, "", f"❌ **{character_name}** no tiene el item **{item_name}**"
                
                inv_id, equipado = result
                
                # Cambiar estado de equipamiento
                new_status = not equipado
                cursor.execute("UPDATE inventarios SET equipado = ? WHERE id = ?", (new_status, inv_id))
                conn.commit()
                
                status_text = "equipado" if new_status else "desequipado"
                return True, status_text, f"**{item_name}** {status_text} por **{character_name}**"
                
        except Exception as e:
            logger.error(f"❌ Error equipando item {item_name} para {character_name}: {e}")
            return False, "", "❌ Error interno"
    
    @staticmethod
    def add_item_to_inventory(character_name, item_name, cantidad=1):
        """
        Añade un item al inventario de un personaje
        
        Args:
            character_name: Nombre del personaje
            item_name: Nombre del item
            cantidad: Cantidad a añadir
            
        Returns:
            tuple: (éxito: bool, cantidad_total: int, mensaje: str)
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar que el personaje existe
                cursor.execute("SELECT id FROM personajes WHERE nombre = ?", (character_name,))
                char_result = cursor.fetchone()
                if not char_result:
                    return False, 0, f"❌ Personaje **{character_name}** no encontrado"
                
                # Verificar que el item existe
                cursor.execute("SELECT id FROM items WHERE nombre = ?", (item_name,))
                item_result = cursor.fetchone()
                if not item_result:
                    return False, 0, f"❌ Item **{item_name}** no encontrado"
                
                char_id, item_id = char_result[0], item_result[0]
                
                # Verificar si ya tiene el item
                cursor.execute(
                    "SELECT id, cantidad FROM inventarios WHERE personaje_id = ? AND item_id = ?", 
                    (char_id, item_id)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Actualizar cantidad existente
                    new_cantidad = existing[1] + cantidad
                    cursor.execute(
                        "UPDATE inventarios SET cantidad = ? WHERE id = ?", 
                        (new_cantidad, existing[0])
                    )
                else:
                    # Crear nueva entrada
                    cursor.execute(
                        "INSERT INTO inventarios (personaje_id, item_id, cantidad) VALUES (?, ?, ?)",
                        (char_id, item_id, cantidad)
                    )
                    new_cantidad = cantidad
                
                conn.commit()
                return True, new_cantidad, f"**{item_name}** x{cantidad} entregado a **{character_name}**"
                
        except Exception as e:
            logger.error(f"❌ Error añadiendo item {item_name} a {character_name}: {e}")
            return False, 0, "❌ Error interno"


# Instancia global del sistema de inventario
inventory_system = InventorySystem()