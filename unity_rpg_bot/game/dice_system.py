"""
Sistema de dados y combate para Unity RPG Bot
"""
import random
from unity_rpg_bot.config.constants import PLAYER_ACTION_MAPPING, NPC_ACTION_MAPPING
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.utils.logging import logger


class DiceSystem:
    @staticmethod
    def roll_multiple_dice(dice_count, dice_type):
        """Tira múltiples dados del mismo tipo"""
        rolls = [random.randint(1, dice_type) for _ in range(dice_count)]
        return {'rolls': rolls, 'total': sum(rolls)}
    
    @staticmethod
    def roll_action(character_name, action_type, dice_count=1, dice_type=20, bonificador=0):
        """
        Ejecuta una tirada de acción para un personaje
        
        Args:
            character_name: Nombre del personaje
            action_type: Tipo de acción (ataque_fisico, defensa_fisica, etc.)
            dice_count: Número de dados a tirar
            dice_type: Tipo de dado (d6, d20, etc.)
            bonificador: Bonificador adicional a la tirada
            
        Returns:
            dict: Resultado detallado de la tirada o None si hay error
        """
        # Obtener estadísticas base del personaje
        from unity_rpg_bot.storage.excel_manager import excel_manager
        base_stats = excel_manager.read_character_stats(character_name)
        if not base_stats:
            return None
        
        # Calcular bonos de items equipados
        from unity_rpg_bot.game.inventory import inventory_system
        item_bonuses = inventory_system.calculate_equipped_bonuses(character_name)
        
        # Combinar estadísticas base con bonos de items
        combined_stats = {}
        for attr in base_stats:
            combined_stats[attr] = {
                'base': base_stats[attr]['base'],
                'bonus': item_bonuses.get(attr, 0),
                'total': base_stats[attr]['base'] + item_bonuses.get(attr, 0)
            }
        
        # Tirar dados múltiples
        dice_result = DiceSystem.roll_multiple_dice(dice_count, dice_type)
        dice_total = dice_result['total']
        
        # Validar tipo de acción
        if action_type not in PLAYER_ACTION_MAPPING:
            return None
            
        # Obtener el atributo correspondiente a la acción
        attr_key = PLAYER_ACTION_MAPPING[action_type]
        attr_value = combined_stats[attr_key]['total']
        total = dice_total + attr_value + bonificador
        
        # Verificar críticos y pifias
        is_critical = any(roll == dice_type for roll in dice_result['rolls'])
        is_fumble = any(roll == 1 for roll in dice_result['rolls'])
        
        # Log de la tirada
        logger.info(
            f"[DADOS] {character_name} - {action_type}: "
            f"{dice_count}d{dice_type}({dice_result['rolls']}) + "
            f"{attr_key.title()}({attr_value}) + Bonus({bonificador}) = {total}"
        )
        
        return {
            'dice_rolls': dice_result['rolls'], 
            'dice_total': dice_total,
            'dice_count': dice_count,
            'dice_type': dice_type,
            'attribute': attr_value, 
            'attribute_name': attr_key.title(),
            'bonuses': bonificador, 
            'total': total, 
            'action_type': action_type,
            'is_critical': is_critical, 
            'is_fumble': is_fumble
        }
    
    @staticmethod
    def npc_action(npc_name, action_type):
        """
        Ejecuta una acción de NPC (ataque o defensa) con stats fijas
        
        Args:
            npc_name: Nombre del NPC
            action_type: Tipo de acción (fisico, magico, defensa_fisica, etc.)
            
        Returns:
            dict: Resultado de la acción del NPC o None si hay error
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ataq_fisic, ataq_dist, ataq_magic, res_fisica, res_magica, velocidad,
                           sincronizado, cantidad, imagen_url 
                    FROM npcs WHERE nombre = ?
                """, (npc_name,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                (ataq_fisic, ataq_dist, ataq_magic, res_fisica, res_magica, 
                 velocidad, sincronizado, cantidad, imagen_url) = result
                
                # Mapeo de acciones a valores de stats
                action_stats = {
                    'fisico': ataq_fisic,
                    'distancia': ataq_dist, 
                    'magico': ataq_magic,
                    'defensa_fisica': res_fisica,
                    'defensa_magica': res_magica,
                    'esquivar': velocidad
                }
                
                if action_type not in action_stats:
                    return None
                
                base_value = action_stats[action_type]
                
                # Si está sincronizado, multiplica por cantidad
                if sincronizado:
                    total_value = base_value * cantidad
                    action_description = f"{cantidad} {npc_name}s sincronizados"
                else:
                    total_value = base_value
                    action_description = f"{npc_name}"
                
                # Determinar si es ataque o defensa
                is_attack = action_type in ['fisico', 'distancia', 'magico']
                action_category = "ataque" if is_attack else "defensa"
                
                logger.info(f"[NPC {action_category.upper()}] {action_description} - {action_type}: {total_value}")
                
                return {
                    'npc_name': npc_name,
                    'action_type': action_type,
                    'action_category': action_category,
                    'base_value': base_value,
                    'total_value': total_value,
                    'sincronizado': sincronizado,
                    'cantidad': cantidad,
                    'action_description': action_description,
                    'imagen_url': imagen_url
                }
        except Exception as e:
            logger.error(f"❌ Error en acción NPC: {e}")
            return None


# Instancia global del sistema de dados
dice_system = DiceSystem()