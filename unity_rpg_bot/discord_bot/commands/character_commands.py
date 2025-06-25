"""
Comandos relacionados con personajes
"""
import discord
from discord import app_commands
import sqlite3
from unity_rpg_bot.config.constants import COLORS, FIXED_HP, EMOJIS
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.storage.excel_manager import excel_manager
from unity_rpg_bot.storage.image_handler import image_handler
from unity_rpg_bot.storage.google_sheets import google_sheets
from unity_rpg_bot.game.inventory import inventory_system
from unity_rpg_bot.utils.logging import logger


class CharacterCommands:
    def __init__(self, tree):
        self.tree = tree
        self.register_commands()
    
    def register_commands(self):
        """Registra todos los comandos de personajes"""
        
        @self.tree.command(name="crear_personaje", description="Crea un personaje con 10 PG fijos")
        async def create_character(
            interaction: discord.Interaction, 
            nombre: str, 
            fuerza: int = 10, 
            destreza: int = 10,
            velocidad: int = 10, 
            resistencia: int = 10, 
            inteligencia: int = 10, 
            mana: int = 10,
            descripcion: str = "Un aventurero misterioso", 
            imagen: discord.Attachment = None
        ):
            await interaction.response.defer()
            
            try:
                # Guardar imagen si se proporciona
                imagen_url = None
                if imagen:
                    imagen_url = await image_handler.save_image(imagen, 'personaje', nombre)
                
                # Preparar estadísticas iniciales
                initial_stats = {
                    'fuerza': fuerza, 'destreza': destreza, 'velocidad': velocidad, 
                    'resistencia': resistencia, 'inteligencia': inteligencia, 'mana': mana
                }
                
                # Crear archivo Excel del personaje
                excel_path = excel_manager.create_character_excel(nombre, interaction.user.id, initial_stats)
                
                # Guardar en base de datos
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO personajes (nombre, usuario_id, excel_path, descripcion, imagen_url) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (nombre, str(interaction.user.id), excel_path, descripcion, imagen_url))
                    conn.commit()
                
                # Crear embed de respuesta
                embed = discord.Embed(
                    title="🎭 ¡Personaje Creado!", 
                    description=f"**{nombre}** ha despertado en Unity", 
                    color=COLORS['SUCCESS']
                )
                embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
                embed.add_field(name="❤️ Puntos de Golpe", value=f"{FIXED_HP} PG (fijos para todos)", inline=True)
                
                # Estadísticas
                stats_text = ""
                for attr, value in initial_stats.items():
                    emoji = EMOJIS['attributes'].get(attr, '📊')
                    stats_text += f"{emoji} **{attr.title()}:** {value}\n"
                
                embed.add_field(name="📊 Atributos", value=stats_text, inline=True)
                
                embed.add_field(
                    name="🎲 Sistema de Combate", 
                    value="**Ataques:**\n⚔️ Físico (Fuerza)\n🏹 Distancia (Destreza)\n🔮 Mágico (Maná)\n\n**Defensas:**\n🏃 Esquive (Velocidad)\n🛡️ Física (Resistencia)\n✨ Mágica (Destreza)", 
                    inline=True
                )
                
                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                await interaction.followup.send(embed=embed)
                
            except sqlite3.IntegrityError:
                await interaction.followup.send(f"❌ El personaje **{nombre}** ya existe")
            except Exception as e:
                logger.error(f"❌ Error creando personaje: {e}")
                await interaction.followup.send(f"❌ Error interno al crear **{nombre}**")
        
        @self.tree.command(name="info_personaje", description="Información completa de un personaje")
        async def character_info(interaction: discord.Interaction, personaje: str):
            await interaction.response.defer()
            
            try:
                # Obtener datos del personaje
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM personajes WHERE nombre = ?", (personaje,))
                    char_data = cursor.fetchone()
                
                if not char_data:
                    await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                    return
                
                # Obtener estadísticas
                base_stats = excel_manager.read_character_stats(personaje)
                item_bonuses = inventory_system.calculate_equipped_bonuses(personaje)
                
                if not base_stats:
                    await interaction.followup.send(f"❌ No se pudieron cargar las estadísticas de **{personaje}**")
                    return
                
                # Combinar estadísticas base con bonos
                combined_stats = {}
                for attr in base_stats:
                    combined_stats[attr] = {
                        'base': base_stats[attr]['base'],
                        'bonus': item_bonuses.get(attr, 0),
                        'total': base_stats[attr]['base'] + item_bonuses.get(attr, 0)
                    }
                
                # Crear embed
                embed = discord.Embed(
                    title=f"🎭 {personaje}", 
                    description=char_data[4] or "Un aventurero misterioso", 
                    color=COLORS['CHARACTER']
                )
                
                embed.add_field(name="❤️ Puntos de Golpe", value=f"{FIXED_HP} PG", inline=True)
                embed.add_field(name="💰 Oro", value=str(char_data[5]), inline=True)
                embed.add_field(name="📝 Estado", value=char_data[6].title(), inline=True)
                
                # Mostrar estadísticas con bonos
                stats_text = ""
                for attr in ['fuerza', 'destreza', 'velocidad', 'resistencia', 'inteligencia', 'mana']:
                    if attr in combined_stats:
                        s = combined_stats[attr]
                        emoji = EMOJIS['attributes'].get(attr, '📊')
                        bonus_text = f" (+{s['bonus']})" if s['bonus'] > 0 else f" ({s['bonus']})" if s['bonus'] < 0 else ""
                        stats_text += f"{emoji} **{attr.title()}:** {s['total']} ({s['base']}{bonus_text})\n"
                
                embed.add_field(name="📊 Atributos", value=stats_text, inline=False)
                
                if char_data[7]:  # imagen_url
                    embed.set_thumbnail(url=char_data[7])
                
                # Sincronizar con Google Sheets
                google_sheets.sync_character(personaje, combined_stats)
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error mostrando info de {personaje}: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="borrar_personaje", description="Borra tu personaje (solo el creador puede borrarlo)")
        async def delete_character(interaction: discord.Interaction, personaje: str):
            await interaction.response.defer()
            
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Verificar que el personaje existe y pertenece al usuario
                    cursor.execute("SELECT id, usuario_id, excel_path FROM personajes WHERE nombre = ?", (personaje,))
                    result = cursor.fetchone()
                    
                    if not result:
                        await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                        return
                    
                    char_id, owner_id, excel_path = result
                    
                    if owner_id != str(interaction.user.id):
                        await interaction.followup.send("❌ Solo puedes borrar tus propios personajes")
                        return
                    
                    # Borrar inventario del personaje
                    cursor.execute("DELETE FROM inventarios WHERE personaje_id = ?", (char_id,))
                    
                    # Borrar personaje de la base de datos
                    cursor.execute("DELETE FROM personajes WHERE id = ?", (char_id,))
                    conn.commit()
                    
                    # Archivar archivo Excel
                    excel_manager.archive_character(personaje)
                    
                    # Eliminar imágenes del personaje
                    deleted_images = image_handler.delete_entity_images('personaje', personaje)
                
                embed = discord.Embed(
                    title="🗑️ Personaje Borrado", 
                    description=f"**{personaje}** ha sido eliminado del universo Unity", 
                    color=COLORS['WARNING']
                )
                embed.add_field(
                    name="🧹 Limpieza", 
                    value=f"• Inventario eliminado\n• Archivo movido a archivados\n• {deleted_images} imágenes eliminadas", 
                    inline=False
                )
                embed.set_footer(text="Esta acción no se puede deshacer")
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error borrando personaje: {e}")
                await interaction.followup.send("❌ Error interno al borrar personaje")
        
        @self.tree.command(name="editar_personaje", description="Edita las estadísticas e imagen de tu personaje")
        async def edit_character(
            interaction: discord.Interaction, 
            personaje: str, 
            fuerza: int = None, 
            destreza: int = None, 
            velocidad: int = None,
            resistencia: int = None, 
            inteligencia: int = None, 
            mana: int = None,
            oro: int = None, 
            imagen: discord.Attachment = None
        ):
            await interaction.response.defer()
            
            try:
                # Verificar propiedad del personaje
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT usuario_id FROM personajes WHERE nombre = ?", (personaje,))
                    result = cursor.fetchone()
                    
                    if not result:
                        await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                        return
                        
                    if result[0] != str(interaction.user.id):
                        await interaction.followup.send("❌ Solo puedes editar tus propios personajes")
                        return
                
                # Actualizar imagen si se proporciona
                imagen_url = None
                if imagen:
                    imagen_url = await image_handler.save_image(imagen, 'personaje', personaje)
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE personajes SET imagen_url = ? WHERE nombre = ?", (imagen_url, personaje))
                        conn.commit()
                
                # Preparar nuevas estadísticas
                new_stats = {}
                if fuerza is not None: new_stats['fuerza'] = fuerza
                if destreza is not None: new_stats['destreza'] = destreza
                if velocidad is not None: new_stats['velocidad'] = velocidad
                if resistencia is not None: new_stats['resistencia'] = resistencia
                if inteligencia is not None: new_stats['inteligencia'] = inteligencia
                if mana is not None: new_stats['mana'] = mana
                
                # Actualizar estadísticas en Excel
                if new_stats:
                    excel_manager.update_character_stats(personaje, new_stats)
                
                # Actualizar oro en base de datos
                if oro is not None:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE personajes SET oro = ? WHERE nombre = ?", (oro, personaje))
                        conn.commit()
                
                # Crear embed de respuesta
                embed = discord.Embed(
                    title="✏️ Personaje Editado", 
                    description=f"**{personaje}** actualizado exitosamente", 
                    color=COLORS['SUCCESS']
                )
                
                if new_stats:
                    stats_text = '\n'.join([f"• **{k.title()}:** {v}" for k, v in new_stats.items()])
                    embed.add_field(name="📊 Estadísticas Actualizadas", value=stats_text[:1024], inline=False)
                
                if oro is not None:
                    embed.add_field(name="💰 Oro Actualizado", value=f"{oro} monedas", inline=True)
                
                if imagen:
                    embed.add_field(name="🖼️ Imagen", value="Actualizada", inline=True)
                    if imagen_url:
                        embed.set_thumbnail(url=imagen_url)
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error editando personaje: {e}")
                await interaction.followup.send("❌ Error interno")