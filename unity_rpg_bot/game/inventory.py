"""
Sistema de inventario y equipamiento para Unity RPG Bot
"""
import difflib
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.utils.logging import logger


class InventorySystem:
    @staticmethod
    def fuzzy_find_item(search_term, available_items):
        """
        Busca un item usando coincidencia aproximada (fuzzy matching)
        
        Args:
            search_term: Término de búsqueda
            available_items: Lista de nombres de items disponibles
            
        Returns:
            str or None: Nombre exacto del item encontrado o None
        """
        if not search_term or not available_items:
            return None
        
        # Normalizar términos para comparación
        search_normalized = search_term.lower().strip()
        
        # Buscar coincidencia exacta primero
        for item in available_items:
            if item.lower().strip() == search_normalized:
                logger.info(f"🎯 [FUZZY] Coincidencia exacta: '{search_term}' -> '{item}'")
                return item
        
        # Buscar coincidencias parciales
        for item in available_items:
            if search_normalized in item.lower() or item.lower() in search_normalized:
                logger.info(f"🎯 [FUZZY] Coincidencia parcial: '{search_term}' -> '{item}'")
                return item
        
        # Usar difflib para encontrar la mejor coincidencia
        matches = difflib.get_close_matches(search_normalized, 
                                          [item.lower() for item in available_items], 
                                          n=1, cutoff=0.6)
        
        if matches:
            # Encontrar el item original correspondiente
            for item in available_items:
                if item.lower() == matches[0]:
                    logger.info(f"🎯 [FUZZY] Coincidencia aproximada: '{search_term}' -> '{item}' (score: difflib)")
                    return item
        
        logger.warning(f"❌ [FUZZY] No se encontró coincidencia para: '{search_term}'")
        logger.info(f"ℹ️ [FUZZY] Items disponibles: {available_items}")
        return None
    
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
            logger.info(f"🔍 [INVENTORY] Buscando items equipables para: '{character_name}'")
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Primero verificar si el personaje existe
                cursor.execute("SELECT id, nombre FROM personajes WHERE nombre = ?", (character_name,))
                char_result = cursor.fetchone()
                if not char_result:
                    logger.warning(f"❌ [INVENTORY] Personaje '{character_name}' no encontrado")
                    return []
                
                char_id, char_name = char_result
                logger.info(f"✅ [INVENTORY] Personaje encontrado: ID={char_id}, Nombre='{char_name}'")
                
                # Obtener todos los items del inventario (más flexible)
                cursor.execute("""
                    SELECT i.nombre, inv.equipado, i.rareza, i.es_equipable, inv.cantidad, i.tipo
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ? AND inv.cantidad > 0
                    ORDER BY i.es_equipable DESC, inv.equipado DESC, i.nombre
                """, (character_name,))
                
                all_items = cursor.fetchall()
                logger.info(f"📦 [INVENTORY] Items encontrados en inventario: {len(all_items)}")
                
                # Log detallado de cada item
                for item in all_items:
                    nombre, equipado, rareza, es_equipable, cantidad, tipo = item
                    equipado_text = "SÍ" if equipado else "NO"
                    equipable_text = "SÍ" if es_equipable else "NO"
                    logger.info(f"  - '{nombre}' [{tipo}]: equipado={equipado_text}, equipable={equipable_text}, cantidad={cantidad}, rareza={rareza}")
                
                # Filtrar solo items equipables
                equipable_items = []
                non_equipable_items = []
                
                for item in all_items:
                    nombre, equipado, rareza, es_equipable, cantidad, tipo = item
                    if es_equipable:
                        equipable_items.append((nombre, equipado, rareza))
                    else:
                        non_equipable_items.append(nombre)
                
                logger.info(f"⚔️ [INVENTORY] Items equipables filtrados: {len(equipable_items)}")
                if equipable_items:
                    equipable_names = [item[0] for item in equipable_items]
                    logger.info(f"  - Equipables: {equipable_names}")
                
                if non_equipable_items:
                    logger.info(f"📦 [INVENTORY] Items NO equipables: {non_equipable_items}")
                
                # Si no hay items equipables, verificar problemas comunes
                if not equipable_items and all_items:
                    logger.warning(f"⚠️ [INVENTORY] PROBLEMA: Personaje tiene {len(all_items)} items pero ninguno es equipable")
                    logger.warning(f"⚠️ [INVENTORY] Posibles causas:")
                    logger.warning(f"   1. Items no tienen 'es_equipable = TRUE' en la base de datos")
                    logger.warning(f"   2. Valores NULL en campo 'es_equipable'")
                    
                    # Verificar valores es_equipable en la DB
                    cursor.execute("""
                        SELECT i.nombre, i.es_equipable 
                        FROM inventarios inv
                        JOIN items i ON inv.item_id = i.id
                        JOIN personajes p ON inv.personaje_id = p.id
                        WHERE p.nombre = ?
                    """, (character_name,))
                    
                    debug_items = cursor.fetchall()
                    logger.warning(f"🔍 [INVENTORY] DEBUG - Valores es_equipable en DB:")
                    for debug_item in debug_items:
                        debug_nombre, debug_equipable = debug_item
                        logger.warning(f"   - '{debug_nombre}': es_equipable = {debug_equipable} (tipo: {type(debug_equipable)})")
                
                elif not all_items:
                    logger.warning(f"📦 [INVENTORY] Personaje '{character_name}' no tiene items en inventario")
                
                return equipable_items
                
        except Exception as e:
            logger.error(f"❌ [INVENTORY] Error obteniendo items equipables de {character_name}: {e}")
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
            logger.info(f"🎒 [ADD_ITEM] Intentando añadir '{item_name}' x{cantidad} a '{character_name}'")
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar que el personaje existe
                cursor.execute("SELECT id FROM personajes WHERE nombre = ?", (character_name,))
                char_result = cursor.fetchone()
                if not char_result:
                    logger.warning(f"❌ [ADD_ITEM] Personaje '{character_name}' no encontrado")
                    return False, 0, f"❌ Personaje **{character_name}** no encontrado"
                
                logger.info(f"✅ [ADD_ITEM] Personaje encontrado: ID={char_result[0]}")
                
                # Buscar item con fuzzy matching
                cursor.execute("SELECT nombre FROM items")
                all_item_names = [row[0] for row in cursor.fetchall()]
                logger.info(f"🔍 [ADD_ITEM] Buscando item '{item_name}' entre {len(all_item_names)} items disponibles")
                
                # Intentar búsqueda fuzzy
                found_item_name = InventorySystem.fuzzy_find_item(item_name, all_item_names)
                
                if not found_item_name:
                    logger.warning(f"❌ [ADD_ITEM] Item '{item_name}' no encontrado con búsqueda fuzzy")
                    close_matches = difflib.get_close_matches(item_name.lower(), 
                                                            [name.lower() for name in all_item_names], 
                                                            n=3, cutoff=0.4)
                    if close_matches:
                        suggestions = [name for name in all_item_names if name.lower() in close_matches]
                        suggestion_text = f"\n*¿Quisiste decir: {', '.join(suggestions[:3])}?*"
                    else:
                        suggestion_text = ""
                    
                    return False, 0, f"❌ Item **{item_name}** no encontrado{suggestion_text}"
                
                # Usar el nombre encontrado por fuzzy matching
                if found_item_name != item_name:
                    logger.info(f"🎯 [ADD_ITEM] Corrigiendo nombre: '{item_name}' -> '{found_item_name}'")
                
                # Obtener ID del item
                cursor.execute("SELECT id FROM items WHERE nombre = ?", (found_item_name,))
                item_result = cursor.fetchone()
                if not item_result:
                    logger.error(f"❌ [ADD_ITEM] Error crítico: Item '{found_item_name}' encontrado por fuzzy pero no existe en DB")
                    return False, 0, f"❌ Error interno con item **{found_item_name}**"
                
                char_id, item_id = char_result[0], item_result[0]
                logger.info(f"🔗 [ADD_ITEM] IDs obtenidos: char_id={char_id}, item_id={item_id}")
                
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
                    logger.info(f"📦 [ADD_ITEM] Cantidad actualizada: {existing[1]} -> {new_cantidad}")
                else:
                    # Crear nueva entrada
                    cursor.execute(
                        "INSERT INTO inventarios (personaje_id, item_id, cantidad) VALUES (?, ?, ?)",
                        (char_id, item_id, cantidad)
                    )
                    new_cantidad = cantidad
                    logger.info(f"📦 [ADD_ITEM] Nueva entrada creada con cantidad: {new_cantidad}")
                
                conn.commit()
                logger.info(f"✅ [ADD_ITEM] Item añadido exitosamente")
                
                # Usar el nombre corregido en el mensaje
                final_item_name = found_item_name if found_item_name != item_name else item_name
                return True, new_cantidad, f"**{final_item_name}** x{cantidad} entregado a **{character_name}**"
                
        except Exception as e:
            logger.error(f"❌ Error añadiendo item {item_name} a {character_name}: {e}")
            return False, 0, "❌ Error interno"


# Instancia global del sistema de inventario
inventory_system = InventorySystem()