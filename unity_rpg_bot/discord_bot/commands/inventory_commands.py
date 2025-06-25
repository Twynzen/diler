"""
Comandos relacionados con inventarios y equipamiento
"""
import discord
from discord import app_commands
from unity_rpg_bot.config.constants import COLORS, EMOJIS
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.game.inventory import inventory_system
from unity_rpg_bot.discord_bot.ui.views import EquipItemView
from unity_rpg_bot.utils.logging import logger


class InventoryCommands:
    def __init__(self, tree):
        self.tree = tree
        self.register_commands()
    
    def register_commands(self):
        """Registra todos los comandos de inventario"""
        
        @self.tree.command(name="equipar_menu", description="Menú interactivo para equipar/desequipar items")
        async def equip_menu(interaction: discord.Interaction, personaje: str):
            await interaction.response.defer()
            
            try:
                # Obtener items equipables del personaje
                items = inventory_system.get_equipable_items(personaje)
                
                if not items:
                    await interaction.followup.send(f"❌ **{personaje}** no tiene items equipables")
                    return
                
                embed = discord.Embed(
                    title=f"🎒 Equipar Items - {personaje}", 
                    description="Selecciona un item para equipar o desequipar:", 
                    color=COLORS['ITEM']
                )
                
                # Mostrar preview de items
                equipped_count = sum(1 for item in items if item[1])  # Equipados
                total_count = len(items)
                embed.add_field(
                    name="📊 Resumen", 
                    value=f"✅ Equipados: {equipped_count}\n📦 Total: {total_count}", 
                    inline=True
                )
                
                view = EquipItemView(personaje, items)
                await interaction.followup.send(embed=embed, view=view)
                
            except Exception as e:
                logger.error(f"❌ Error mostrando menú equipar: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="dar_item", description="Entrega un item a un personaje")
        async def give_item(interaction: discord.Interaction, personaje: str, item: str, cantidad: int = 1):
            await interaction.response.defer()
            
            try:
                # Validar cantidad
                if cantidad <= 0:
                    await interaction.followup.send("❌ La cantidad debe ser mayor a 0")
                    return
                
                # Usar el sistema de inventario para añadir el item
                success, new_cantidad, message = inventory_system.add_item_to_inventory(personaje, item, cantidad)
                
                if not success:
                    await interaction.followup.send(message)
                    return
                
                embed = discord.Embed(
                    title="🎁 Item Entregado", 
                    description=message, 
                    color=COLORS['SUCCESS']
                )
                embed.add_field(name="📦 Total en Inventario", value=f"{new_cantidad} unidades", inline=True)
                
                # Obtener información del item para mostrar en el embed
                try:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT rareza, tipo FROM items WHERE nombre = ?", (item,))
                        item_info = cursor.fetchone()
                        
                        if item_info:
                            rareza, tipo = item_info
                            rarity_emoji = EMOJIS['rarity'].get(rareza, '⚪')
                            embed.add_field(name="ℹ️ Info del Item", value=f"{rarity_emoji} {tipo.title()}", inline=True)
                except:
                    pass  # No es crítico si no se puede obtener la info
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error dando item: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="inventario", description="Muestra el inventario de un personaje")
        async def show_inventory(interaction: discord.Interaction, personaje: str):
            await interaction.response.defer()
            
            try:
                # Obtener inventario completo
                inventory = inventory_system.get_character_inventory(personaje)
                
                if not inventory:
                    await interaction.followup.send(f"❌ **{personaje}** no tiene items o no existe")
                    return
                
                embed = discord.Embed(title=f"🎒 Inventario de {personaje}", color=COLORS['CHARACTER'])
                
                # Separar items equipados y no equipados
                equipped_items = []
                regular_items = []
                
                for item in inventory:
                    nombre, tipo, rareza, cantidad, equipado = item[0], item[1], item[2], item[3], item[4]
                    
                    rarity_emoji = EMOJIS['rarity'].get(rareza, '⚪')
                    equip_status = "✅ Equipado" if equipado else ""
                    item_line = f"{rarity_emoji} **{nombre}** x{cantidad} {equip_status}"
                    
                    if equipado:
                        equipped_items.append(item_line)
                    else:
                        regular_items.append(item_line)
                
                # Mostrar items equipados
                if equipped_items:
                    embed.add_field(
                        name="⚔️ Items Equipados", 
                        value='\n'.join(equipped_items[:10]), 
                        inline=False
                    )
                
                # Mostrar items del inventario
                if regular_items:
                    # Dividir en chunks si hay muchos items
                    chunks = [regular_items[i:i+10] for i in range(0, len(regular_items), 10)]
                    for i, chunk in enumerate(chunks[:2]):  # Máximo 2 chunks para evitar límite de Discord
                        field_name = "📦 Items en Inventario" if i == 0 else "📦 Más Items"
                        embed.add_field(name=field_name, value='\n'.join(chunk), inline=False)
                
                # Calcular estadísticas del inventario
                total_items = len(inventory)
                equipped_count = len(equipped_items)
                total_quantity = sum(item[3] for item in inventory)
                
                embed.add_field(
                    name="📊 Estadísticas", 
                    value=f"✅ Equipados: {equipped_count}\n📦 Tipos únicos: {total_items}\n🔢 Cantidad total: {total_quantity}", 
                    inline=True
                )
                
                embed.set_footer(text=f"Usa /equipar_menu {personaje} para gestionar equipamiento")
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error mostrando inventario: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="quitar_item", description="Quita un item del inventario de un personaje")
        async def remove_item(interaction: discord.Interaction, personaje: str, item: str, cantidad: int = 1):
            await interaction.response.defer()
            
            try:
                # Validar cantidad
                if cantidad <= 0:
                    await interaction.followup.send("❌ La cantidad debe ser mayor a 0")
                    return
                
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Verificar que el personaje existe
                    cursor.execute("SELECT id FROM personajes WHERE nombre = ?", (personaje,))
                    char_result = cursor.fetchone()
                    if not char_result:
                        await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                        return
                    
                    # Verificar que el item existe
                    cursor.execute("SELECT id FROM items WHERE nombre = ?", (item,))
                    item_result = cursor.fetchone()
                    if not item_result:
                        await interaction.followup.send(f"❌ Item **{item}** no encontrado")
                        return
                    
                    char_id, item_id = char_result[0], item_result[0]
                    
                    # Verificar que el personaje tiene el item
                    cursor.execute(
                        "SELECT id, cantidad, equipado FROM inventarios WHERE personaje_id = ? AND item_id = ?", 
                        (char_id, item_id)
                    )
                    existing = cursor.fetchone()
                    
                    if not existing:
                        await interaction.followup.send(f"❌ **{personaje}** no tiene el item **{item}**")
                        return
                    
                    inv_id, current_cantidad, equipado = existing
                    
                    if cantidad > current_cantidad:
                        await interaction.followup.send(f"❌ **{personaje}** solo tiene {current_cantidad} unidades de **{item}**")
                        return
                    
                    # Calcular nueva cantidad
                    new_cantidad = current_cantidad - cantidad
                    
                    if new_cantidad <= 0:
                        # Eliminar completamente del inventario
                        cursor.execute("DELETE FROM inventarios WHERE id = ?", (inv_id,))
                        status_message = f"**{item}** eliminado completamente del inventario de **{personaje}**"
                    else:
                        # Actualizar cantidad
                        cursor.execute("UPDATE inventarios SET cantidad = ? WHERE id = ?", (new_cantidad, inv_id))
                        status_message = f"**{item}** x{cantidad} quitado del inventario de **{personaje}**"
                    
                    conn.commit()
                
                embed = discord.Embed(
                    title="📤 Item Quitado", 
                    description=status_message, 
                    color=COLORS['WARNING']
                )
                
                if new_cantidad > 0:
                    embed.add_field(name="📦 Cantidad Restante", value=f"{new_cantidad} unidades", inline=True)
                
                if equipado and new_cantidad <= 0:
                    embed.add_field(name="⚠️ Nota", value="El item estaba equipado y fue desequipado automáticamente", inline=False)
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error quitando item: {e}")
                await interaction.followup.send("❌ Error interno")