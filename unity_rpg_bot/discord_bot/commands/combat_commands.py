"""
Comandos relacionados con combate y tiradas de dados
"""
import discord
from discord import app_commands
from unity_rpg_bot.config.constants import COLORS, DICE_TYPES, MAX_DICE_COUNT
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.game.dice_system import dice_system
from unity_rpg_bot.discord_bot.ui.views import NPCActionView
from unity_rpg_bot.utils.logging import logger


class CombatCommands:
    def __init__(self, tree):
        self.tree = tree
        self.register_commands()
    
    def register_commands(self):
        """Registra todos los comandos de combate"""
        
        @self.tree.command(name="tirar", description="Tirada directa con parámetros")
        @app_commands.describe(
            personaje="Nombre del personaje",
            tipo_dado="Tipo de dado (3, 6, 8, 10, 12, 20)",
            cantidad="Cantidad de dados (1-5)",
            accion="Tipo de acción",
            bonificador="Bonificador adicional"
        )
        @app_commands.choices(tipo_dado=[
            app_commands.Choice(name="d3", value=3),
            app_commands.Choice(name="d6", value=6),
            app_commands.Choice(name="d8", value=8),
            app_commands.Choice(name="d10", value=10),
            app_commands.Choice(name="d12", value=12),
            app_commands.Choice(name="d20", value=20)
        ])
        @app_commands.choices(cantidad=[
            app_commands.Choice(name="1 dado", value=1),
            app_commands.Choice(name="2 dados", value=2),
            app_commands.Choice(name="3 dados", value=3),
            app_commands.Choice(name="4 dados", value=4),
            app_commands.Choice(name="5 dados", value=5)
        ])
        @app_commands.choices(accion=[
            app_commands.Choice(name="Ataque Físico", value="ataque_fisico"),
            app_commands.Choice(name="Ataque Mágico", value="ataque_magico"),
            app_commands.Choice(name="Ataque Distancia", value="ataque_distancia"),
            app_commands.Choice(name="Defensa Física", value="defensa_fisica"),
            app_commands.Choice(name="Defensa Mágica", value="defensa_magica"),
            app_commands.Choice(name="Defensa Esquive", value="defensa_esquive")
        ])
        async def roll_dice(
            interaction: discord.Interaction, 
            personaje: str, 
            tipo_dado: int, 
            cantidad: int, 
            accion: str, 
            bonificador: int = 0
        ):
            await interaction.response.defer()
            
            try:
                # Validaciones
                if tipo_dado not in DICE_TYPES:
                    await interaction.followup.send("❌ Tipo de dado inválido. Usa: 3, 6, 8, 10, 12, 20")
                    return
                
                if cantidad < 1 or cantidad > MAX_DICE_COUNT:
                    await interaction.followup.send(f"❌ Cantidad de dados debe ser entre 1 y {MAX_DICE_COUNT}")
                    return
                
                # Ejecutar tirada
                result = dice_system.roll_action(personaje, accion, cantidad, tipo_dado, bonificador)
                
                if not result:
                    await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                    return
                
                # Obtener imagen del personaje
                try:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT imagen_url FROM personajes WHERE nombre = ?", (personaje,))
                        imagen_result = cursor.fetchone()
                        imagen_url = imagen_result[0] if imagen_result else None
                except:
                    imagen_url = None
                
                # Determinar color y descripción según el resultado
                if 'ataque' in result['action_type']:
                    color = COLORS['SUCCESS'] if result['total'] >= 18 else COLORS['WARNING'] if result['total'] >= 12 else COLORS['ERROR']
                    action_emoji = "⚔️" if 'fisico' in result['action_type'] else "🔮" if 'magico' in result['action_type'] else "🏹"
                else:
                    color = COLORS['INFO'] if result['total'] >= 15 else COLORS['WARNING'] if result['total'] >= 12 else COLORS['ERROR']
                    action_emoji = "🛡️" if 'fisica' in result['action_type'] else "✨" if 'magica' in result['action_type'] else "🏃"
                
                action_name = result['action_type'].replace('_', ' ').title()
                embed = discord.Embed(title=f"{action_emoji} {action_name} - {personaje}", color=color)
                
                # Determinar descripción según el resultado
                if result['is_critical']:
                    embed.description = "🎯 **¡CRÍTICO DEVASTADOR!**"
                    embed.color = COLORS['LEGENDARY']
                elif result['is_fumble']:
                    embed.description = "💥 **¡PIFIA ÉPICA!**"
                    embed.color = COLORS['CRITICAL']
                elif result['total'] >= 25:
                    embed.description = "🌟 **¡RESULTADO LEGENDARIO!**"
                elif result['total'] >= 15:
                    embed.description = "✅ **Resultado Exitoso**"
                else:
                    embed.description = "❌ **Resultado Fallido**"
                
                # Mostrar dados de forma clara
                dice_display = ' + '.join(map(str, result['dice_rolls']))
                embed.add_field(
                    name=f"🎲 {result['dice_count']}d{result['dice_type']}", 
                    value=f"`{dice_display}` = `{result['dice_total']}`", 
                    inline=True
                )
                embed.add_field(
                    name=f"📊 {result['attribute_name']}", 
                    value=f"`{result['attribute']}`", 
                    inline=True
                )
                
                if bonificador != 0:
                    embed.add_field(name="➕ Bonus", value=f"`{bonificador}`", inline=True)
                
                embed.add_field(name="🏆 **TOTAL**", value=f"**`{result['total']}`**", inline=False)
                
                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                await interaction.followup.send(embed=embed)
                
            except Exception as e:
                logger.error(f"❌ Error en tirada: {e}")
                await interaction.followup.send("❌ Error interno")
        
        @self.tree.command(name="tirada_npc", description="Ejecuta ataques y defensas de NPCs con stats fijas")
        async def npc_roll(interaction: discord.Interaction, npc: str):
            try:
                # Verificar que el NPC existe
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT nombre, sincronizado, cantidad FROM npcs WHERE nombre = ?", (npc,))
                    result = cursor.fetchone()
                    
                    if not result:
                        await interaction.response.send_message(f"❌ NPC **{npc}** no encontrado", ephemeral=True)
                        return
                    
                    nombre, sincronizado, cantidad = result
                
                # Crear embed de selección
                embed = discord.Embed(
                    title=f"👹 {npc} - Seleccionar Acción", 
                    description="Elige el tipo de acción del NPC:", 
                    color=COLORS['NPC']
                )
                
                if sincronizado:
                    embed.add_field(name="🤝 NPCs Sincronizados", value=f"{cantidad} unidades", inline=True)
                    embed.add_field(name="💥 Valores", value="Base × Cantidad", inline=True)
                else:
                    embed.add_field(name="👤 NPC Individual", value="Valores fijos", inline=True)
                
                embed.add_field(
                    name="🎯 Acciones Disponibles", 
                    value="**Ataques:** ⚔️ Físico, 🔮 Mágico, 🏹 Distancia\n**Defensas:** 🛡️ Física, ✨ Mágica, 🏃 Esquivar", 
                    inline=False
                )
                
                view = NPCActionView(npc)
                await interaction.response.send_message(embed=embed, view=view)
                
            except Exception as e:
                logger.error(f"❌ Error en tirada NPC: {e}")
                await interaction.response.send_message("❌ Error interno", ephemeral=True)