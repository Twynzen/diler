"""
Comandos relacionados con NPCs
"""
import discord
from discord import app_commands
import sqlite3
from unity_rpg_bot.config.constants import COLORS, FIXED_HP
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.storage.image_handler import image_handler
from unity_rpg_bot.storage.google_sheets import google_sheets
from unity_rpg_bot.utils.logging import logger


class NPCCommands:
    def __init__(self, tree):
        self.tree = tree
        self.register_commands()
    
    def register_commands(self):
        """Registra todos los comandos de NPCs"""
        
        @self.tree.command(name="crear_npc", description="Crea un NPC con las nuevas estadísticas")
        async def create_npc(
            interaction: discord.Interaction, 
            nombre: str, 
            tipo: str = "general",
            ataq_fisic: int = 10, 
            ataq_dist: int = 10, 
            ataq_magic: int = 10,
            res_fisica: int = 10, 
            res_magica: int = 10, 
            velocidad: int = 10, 
            mana: int = 10,
            descripcion: str = "Un ser del universo Unity",
            sincronizado: bool = False, 
            cantidad: int = 1, 
            imagen: discord.Attachment = None
        ):
            await interaction.response.defer()
            
            try:
                # Guardar imagen si se proporciona
                imagen_url = None
                if imagen:
                    imagen_url = await image_handler.save_image(imagen, 'npc', nombre)
                
                # Crear NPC en base de datos
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO npcs (nombre, tipo, ataq_fisic, ataq_dist, ataq_magic,
                                        res_fisica, res_magica, velocidad, mana, descripcion, 
                                        sincronizado, cantidad, imagen_url) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nombre, tipo, ataq_fisic, ataq_dist, ataq_magic, res_fisica, res_magica,
                          velocidad, mana, descripcion, sincronizado, cantidad, imagen_url))
                    conn.commit()
                
                # Crear embed de respuesta
                embed = discord.Embed(
                    title="👹 ¡NPC Creado!", 
                    description=f"**{nombre}** añadido al universo", 
                    color=COLORS['NPC']
                )
                embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
                embed.add_field(name="❤️ Puntos de Golpe", value=f"{FIXED_HP} PG", inline=True)
                
                if sincronizado:
                    embed.add_field(name="🤝 Sincronizado", value=f"Sí ({cantidad} unidades)", inline=True)
                else:
                    embed.add_field(name="👤 Individual", value="Sí", inline=True)
                
                embed.add_field(name="📝 Descripción", value=descripcion[:200], inline=False)
                
                # Estadísticas del NPC
                stats_text = f"⚔️ ATAQ_FISIC: {ataq_fisic}\n🏹 ATAQ_DIST: {ataq_dist}\n🔮 ATAQ_MAGIC: {ataq_magic}\n🛡️ RES_FISICA: {res_fisica}\n✨ RES_MAGICA: {res_magica}\n⚡ Velocidad: {velocidad}\n🧙 Maná: {mana}"
                embed.add_field(name="📊 Estadísticas", value=stats_text, inline=True)
                
                # Valores de combate
                damage_text = f"⚔️ Físico: {ataq_fisic}\n🏹 Distancia: {ataq_dist}\n🔮 Mágico: {ataq_magic}"
                defense_text = f"🛡️ Defensa Física: {res_fisica}\n✨ Defensa Mágica: {res_magica}\n🏃 Esquivar: {velocidad}"
                
                if sincronizado:
                    damage_text += f"\n\n🤝 **Sincronizado:**\n⚔️ Físico: {ataq_fisic * cantidad}\n🏹 Distancia: {ataq_dist * cantidad}\n🔮 Mágico: {ataq_magic * cantidad}"
                    defense_text += f"\n\n🤝 **Sincronizado:**\n🛡️ Def. Física: {res_fisica * cantidad}\n✨ Def. Mágica: {res_magica * cantidad}\n🏃 Esquivar: {velocidad * cantidad}"
                
                embed.add_field(name="💥 Ataques", value=damage_text, inline=True)
                embed.add_field(name="🛡️ Defensas", value=defense_text, inline=True)
                
                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                # Sincronizar con Google Sheets
                npc_data = {
                    'tipo': tipo, 'ataq_fisic': ataq_fisic, 'ataq_dist': ataq_dist, 'ataq_magic': ataq_magic,
                    'res_fisica': res_fisica, 'res_magica': res_magica, 'velocidad': velocidad, 'mana': mana,
                    'sincronizado': sincronizado, 'cantidad': cantidad, 'descripcion': descripcion
                }
                google_sheets.sync_npc(nombre, npc_data)
                
                await interaction.followup.send(embed=embed)
                
            except sqlite3.IntegrityError:
                await interaction.followup.send(f"❌ El NPC **{nombre}** ya existe")
            except Exception as e:
                logger.error(f"❌ Error creando NPC: {e}")
                await interaction.followup.send(f"❌ Error interno al crear NPC **{nombre}**")
        
        @self.tree.command(name="info_npc", description="Información completa de un NPC")
        async def npc_info(interaction: discord.Interaction, npc: str):
            await interaction.response.defer()
            
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM npcs WHERE nombre = ?", (npc,))
                    npc_data = cursor.fetchone()
                
                if not npc_data:
                    await interaction.followup.send(f"❌ NPC **{npc}** no encontrado")
                    return
                
                # Extraer datos del NPC
                (id, nombre, tipo, ataq_fisic, ataq_dist, ataq_magic, res_fisica, res_magica, 
                 velocidad, mana, descripcion, imagen_url, sincronizado, cantidad, created_at) = npc_data
                
                embed = discord.Embed(
                    title=f"👹 {nombre}", 
                    description=descripcion or "Un ser misterioso del universo Unity", 
                    color=COLORS['NPC']
                )
                
                embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
                embed.add_field(name="❤️ Puntos de Golpe", value=f"{FIXED_HP} PG", inline=True)
                
                if sincronizado:
                    embed.add_field(name="🤝 Sincronizado", value=f"Sí ({cantidad} unidades)", inline=True)
                else:
                    embed.add_field(name="👤 Individual", value="Sí", inline=True)
                
                # Estadísticas
                stats_text = f"⚔️ **ATAQ_FISIC:** {ataq_fisic}\n🏹 **ATAQ_DIST:** {ataq_dist}\n🔮 **ATAQ_MAGIC:** {ataq_magic}\n🛡️ **RES_FISICA:** {res_fisica}\n✨ **RES_MAGICA:** {res_magica}\n⚡ **Velocidad:** {velocidad}\n🧙 **Maná:** {mana}"
                embed.add_field(name="📊 Estadísticas", value=stats_text, inline=True)
                
                # Valores de combate
                damage_text = f"**Ataques:**\n⚔️ Físico: {ataq_fisic}\n🏹 Distancia: {ataq_dist}\n🔮 Mágico: {ataq_magic}"
                defense_text = f"**Defensas:**\n🛡️ Física: {res_fisica}\n✨ Mágica: {res_magica}\n🏃 Esquivar: {velocidad}"
                
                if sincronizado:
                    damage_text += f"\n\n**Sincronizado:**\n⚔️ Físico: {ataq_fisic * cantidad}\n🏹 Distancia: {ataq_dist * cantidad}\n🔮 Mágico: {ataq_magic * cantidad}"
                    defense_text += f"\n\n**Sincronizado:**\n🛡️ Física: {res_fisica * cantidad}\n✨ Mágica: {res_magica * cantidad}\n🏃 Esquivar: {velocidad * cantidad}"
                
                embed.add_field(name="💥 Ataques", value=damage_text, inline=True)
                embed.add_field(name="🛡️ Defensas", value=defense_text, inline=True)
                
                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error mostrando info NPC: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="editar_npc", description="Edita las estadísticas de un NPC")
        async def edit_npc(
            interaction: discord.Interaction, 
            npc: str,
            ataq_fisic: int = None, 
            ataq_dist: int = None, 
            ataq_magic: int = None,
            res_fisica: int = None, 
            res_magica: int = None, 
            velocidad: int = None, 
            mana: int = None,
            sincronizado: bool = None, 
            cantidad: int = None
        ):
            await interaction.response.defer()
            
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Verificar que el NPC existe
                    cursor.execute("SELECT id FROM npcs WHERE nombre = ?", (npc,))
                    if not cursor.fetchone():
                        await interaction.followup.send(f"❌ NPC **{npc}** no encontrado")
                        return
                    
                    # Preparar actualizaciones
                    updates = []
                    params = []
                    
                    if ataq_fisic is not None:
                        updates.append("ataq_fisic = ?")
                        params.append(ataq_fisic)
                    if ataq_dist is not None:
                        updates.append("ataq_dist = ?")
                        params.append(ataq_dist)
                    if ataq_magic is not None:
                        updates.append("ataq_magic = ?")
                        params.append(ataq_magic)
                    if res_fisica is not None:
                        updates.append("res_fisica = ?")
                        params.append(res_fisica)
                    if res_magica is not None:
                        updates.append("res_magica = ?")
                        params.append(res_magica)
                    if velocidad is not None:
                        updates.append("velocidad = ?")
                        params.append(velocidad)
                    if mana is not None:
                        updates.append("mana = ?")
                        params.append(mana)
                    if sincronizado is not None:
                        updates.append("sincronizado = ?")
                        params.append(sincronizado)
                    if cantidad is not None:
                        updates.append("cantidad = ?")
                        params.append(cantidad)
                    
                    if updates:
                        params.append(npc)
                        query = f"UPDATE npcs SET {', '.join(updates)} WHERE nombre = ?"
                        cursor.execute(query, params)
                        conn.commit()
                
                embed = discord.Embed(
                    title="✏️ NPC Editado", 
                    description=f"**{npc}** actualizado exitosamente", 
                    color=COLORS['NPC']
                )
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error editando NPC: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="borrar_npc", description="Borra un NPC del universo")
        async def delete_npc(interaction: discord.Interaction, npc: str):
            await interaction.response.defer()
            
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Verificar que el NPC existe
                    cursor.execute("SELECT id FROM npcs WHERE nombre = ?", (npc,))
                    result = cursor.fetchone()
                    
                    if not result:
                        await interaction.followup.send(f"❌ NPC **{npc}** no encontrado")
                        return
                    
                    # Borrar NPC
                    cursor.execute("DELETE FROM npcs WHERE nombre = ?", (npc,))
                    conn.commit()
                
                # Eliminar imágenes del NPC
                deleted_images = image_handler.delete_entity_images('npc', npc)
                
                embed = discord.Embed(
                    title="🗑️ NPC Borrado", 
                    description=f"**{npc}** ha sido eliminado del universo Unity", 
                    color=COLORS['WARNING']
                )
                embed.add_field(
                    name="🧹 Limpieza", 
                    value=f"• NPC eliminado de la base de datos\n• {deleted_images} imágenes eliminadas", 
                    inline=False
                )
                embed.set_footer(text="Esta acción no se puede deshacer")
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error borrando NPC: {e}")
                await interaction.followup.send("❌ Error interno al borrar NPC")