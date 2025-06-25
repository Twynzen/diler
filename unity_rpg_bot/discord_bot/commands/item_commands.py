"""
Comandos relacionados con items
"""
import discord
from discord import app_commands
import sqlite3
from unity_rpg_bot.config.constants import COLORS, EMOJIS
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.storage.image_handler import image_handler
from unity_rpg_bot.utils.logging import logger


class ItemCommands:
    def __init__(self, tree):
        self.tree = tree
        self.register_commands()
    
    def register_commands(self):
        """Registra todos los comandos de items"""
        
        @self.tree.command(name="crear_item", description="Crea un item equipable con efectos")
        async def create_item(
            interaction: discord.Interaction, 
            nombre: str, 
            tipo: str, 
            descripcion: str = "",
            efecto_fuerza: int = 0, 
            efecto_destreza: int = 0, 
            efecto_velocidad: int = 0,
            efecto_resistencia: int = 0, 
            efecto_inteligencia: int = 0, 
            efecto_mana: int = 0,
            rareza: str = "comun", 
            precio: int = 0, 
            imagen: discord.Attachment = None
        ):
            await interaction.response.defer()
            
            try:
                # Guardar imagen si se proporciona
                imagen_url = None
                if imagen:
                    imagen_url = await image_handler.save_image(imagen, 'item', nombre)
                
                # Crear item en base de datos
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO items (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza,
                                        efecto_velocidad, efecto_resistencia, efecto_inteligencia, efecto_mana,
                                        rareza, precio, imagen_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza, efecto_velocidad,
                          efecto_resistencia, efecto_inteligencia, efecto_mana, rareza, precio, imagen_url))
                    conn.commit()
                
                # Crear embed de respuesta
                embed = discord.Embed(
                    title="✨ ¡Item Creado!", 
                    description=f"**{nombre}** ha sido forjado", 
                    color=COLORS['ITEM']
                )
                embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
                embed.add_field(name="⭐ Rareza", value=rareza.title(), inline=True)
                embed.add_field(name="💰 Precio", value=f"{precio} oro", inline=True)
                
                if descripcion:
                    embed.add_field(name="📝 Descripción", value=descripcion[:200], inline=False)
                
                # Mostrar efectos del item
                effects = []
                effect_mapping = {
                    'efecto_fuerza': ('💪 Fuerza', efecto_fuerza),
                    'efecto_destreza': ('🎯 Destreza', efecto_destreza),
                    'efecto_velocidad': ('⚡ Velocidad', efecto_velocidad),
                    'efecto_resistencia': ('🛡️ Resistencia', efecto_resistencia),
                    'efecto_inteligencia': ('🧠 Inteligencia', efecto_inteligencia),
                    'efecto_mana': ('🔮 Maná', efecto_mana)
                }
                
                for key, (name, value) in effect_mapping.items():
                    if value != 0:
                        sign = '+' if value > 0 else ''
                        effects.append(f"{name}: {sign}{value}")
                
                if effects:
                    embed.add_field(name="⚡ Efectos", value='\n'.join(effects), inline=False)
                else:
                    embed.add_field(name="⚡ Efectos", value="Sin efectos especiales", inline=False)
                
                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                await interaction.followup.send(embed=embed)
                
            except sqlite3.IntegrityError:
                await interaction.followup.send(f"❌ El item **{nombre}** ya existe")
            except Exception as e:
                logger.error(f"❌ Error creando item: {e}")
                await interaction.followup.send(f"❌ Error interno al crear item **{nombre}**")
        
        @self.tree.command(name="info_item", description="Información completa de un item")
        async def item_info(interaction: discord.Interaction, item: str):
            await interaction.response.defer()
            
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM items WHERE nombre = ?", (item,))
                    item_data = cursor.fetchone()
                
                if not item_data:
                    await interaction.followup.send(f"❌ Item **{item}** no encontrado")
                    return
                
                # Extraer datos del item
                (id, nombre, tipo, subtipo, rareza, descripcion, efecto_fuerza, efecto_destreza,
                 efecto_velocidad, efecto_resistencia, efecto_inteligencia, efecto_mana, precio,
                 es_equipable, slot_equipo, imagen_url, created_at) = item_data
                
                # Determinar color según rareza
                rarity_colors = {
                    'comun': 0x808080,
                    'raro': 0x0070ff,
                    'epico': 0x9932cc,
                    'legendario': 0xff8000
                }
                color = rarity_colors.get(rareza, COLORS['ITEM'])
                
                embed = discord.Embed(
                    title=f"✨ {nombre}", 
                    description=descripcion or "Un objeto misterioso", 
                    color=color
                )
                
                # Información básica
                rarity_emoji = EMOJIS['rarity'].get(rareza, '⚪')
                embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
                embed.add_field(name="⭐ Rareza", value=f"{rarity_emoji} {rareza.title()}", inline=True)
                embed.add_field(name="💰 Precio", value=f"{precio} oro", inline=True)
                
                if subtipo:
                    embed.add_field(name="🔖 Subtipo", value=subtipo.title(), inline=True)
                
                embed.add_field(name="⚔️ Equipable", value="Sí" if es_equipable else "No", inline=True)
                
                if es_equipable and slot_equipo:
                    embed.add_field(name="📍 Slot", value=slot_equipo.title(), inline=True)
                
                # Mostrar efectos
                effects = []
                effect_mapping = {
                    'efecto_fuerza': ('💪 Fuerza', efecto_fuerza),
                    'efecto_destreza': ('🎯 Destreza', efecto_destreza),
                    'efecto_velocidad': ('⚡ Velocidad', efecto_velocidad),
                    'efecto_resistencia': ('🛡️ Resistencia', efecto_resistencia),
                    'efecto_inteligencia': ('🧠 Inteligencia', efecto_inteligencia),
                    'efecto_mana': ('🔮 Maná', efecto_mana)
                }
                
                for key, (name, value) in effect_mapping.items():
                    if value != 0:
                        sign = '+' if value > 0 else ''
                        effects.append(f"{name}: {sign}{value}")
                
                if effects:
                    embed.add_field(name="⚡ Efectos", value='\n'.join(effects), inline=False)
                else:
                    embed.add_field(name="⚡ Efectos", value="Sin efectos especiales", inline=False)
                
                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error mostrando info del item: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="listar_items", description="Lista todos los items disponibles")
        async def list_items(interaction: discord.Interaction, rareza: str = None):
            await interaction.response.defer()
            
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    if rareza:
                        cursor.execute("SELECT nombre, tipo, rareza, precio FROM items WHERE rareza = ? ORDER BY nombre", (rareza,))
                    else:
                        cursor.execute("SELECT nombre, tipo, rareza, precio FROM items ORDER BY rareza, nombre")
                    
                    items = cursor.fetchall()
                
                if not items:
                    filter_text = f" de rareza **{rareza}**" if rareza else ""
                    await interaction.followup.send(f"❌ No se encontraron items{filter_text}")
                    return
                
                embed = discord.Embed(
                    title="📦 Lista de Items", 
                    color=COLORS['ITEM']
                )
                
                if rareza:
                    embed.description = f"Items de rareza **{rareza.title()}**"
                
                # Agrupar items por rareza
                items_by_rarity = {}
                for nombre, tipo, item_rareza, precio in items:
                    if item_rareza not in items_by_rarity:
                        items_by_rarity[item_rareza] = []
                    items_by_rarity[item_rareza].append((nombre, tipo, precio))
                
                # Mostrar items agrupados
                for rarity in ['legendario', 'epico', 'raro', 'comun']:
                    if rarity in items_by_rarity:
                        rarity_emoji = EMOJIS['rarity'].get(rarity, '⚪')
                        items_text = []
                        
                        for nombre, tipo, precio in items_by_rarity[rarity][:10]:  # Límite de 10 por rareza
                            items_text.append(f"• **{nombre}** ({tipo}) - {precio} oro")
                        
                        if items_text:
                            field_name = f"{rarity_emoji} {rarity.title()}"
                            embed.add_field(name=field_name, value='\n'.join(items_text), inline=False)
                
                total_items = len(items)
                embed.set_footer(text=f"Total de items: {total_items}")
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error listando items: {e}")
                await interaction.followup.send("❌ Error interno")