"""
Comandos administrativos para Unity RPG Bot
Incluye integración MCP para gestión inteligente de base de datos
"""
import discord
from discord import app_commands
import json
import sys
import os

# Añadir el directorio raíz al path para importar el MCP server
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from unity_mcp_server import UnityMCPDatabaseManager
from unity_rpg_bot.utils.logging import logger
from unity_rpg_bot.config.constants import COLORS

class AdminCommands:
    def __init__(self, tree):
        self.tree = tree
        self.register_commands()
    
    def register_commands(self):
        """Registra todos los comandos administrativos"""
        
        @self.tree.command(name="admin_db_analyze", description="[ADMIN] Analiza la base de datos con IA")
        async def analyze_database(interaction: discord.Interaction):
            # Verificar permisos de administrador
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Solo los administradores pueden usar este comando", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            try:
                logger.info(f"🤖 [MCP] {interaction.user.display_name} solicitó análisis de base de datos")
                
                # Crear manager MCP
                mcp_manager = UnityMCPDatabaseManager()
                
                # Análisis de schema
                schema_analysis = mcp_manager.analyze_database_schema()
                
                # Análisis de datos
                data_analysis = mcp_manager.analyze_game_data()
                
                # Crear embed con resultados
                embed = discord.Embed(
                    title="🤖 Análisis de Base de Datos (MCP)",
                    description="Análisis inteligente realizado por Claude",
                    color=COLORS['SUCCESS'] if len(schema_analysis['issues']) == 0 else COLORS['WARNING']
                )
                
                # Estado general
                embed.add_field(
                    name="📊 Estado General",
                    value=f"✅ Tablas: {len(schema_analysis['tables'])}\n"
                          f"⚠️ Problemas: {len(schema_analysis['issues'])}\n"
                          f"🎮 Personajes: {data_analysis['characters']['count']}\n"
                          f"⚔️ Items: {data_analysis['items']['count']}",
                    inline=True
                )
                
                # Problemas detectados
                if schema_analysis['issues']:
                    problems_text = []
                    for issue in schema_analysis['issues'][:3]:  # Máximo 3 para no saturar
                        status = "🔧 Auto-reparable" if issue.get('auto_fixable') else "⚠️ Manual"
                        problems_text.append(f"{status}: {issue['message']}")
                    
                    embed.add_field(
                        name="🔍 Problemas Detectados",
                        value='\n'.join(problems_text),
                        inline=False
                    )
                
                # Insights de datos
                if data_analysis['insights']:
                    insights_text = []
                    for insight in data_analysis['insights'][:2]:  # Máximo 2
                        insights_text.append(f"💡 {insight['message']}")
                    
                    embed.add_field(
                        name="📈 Insights de IA",
                        value='\n'.join(insights_text),
                        inline=False
                    )
                
                # Botones de acción si hay problemas auto-reparables
                view = None
                auto_fixable_issues = [issue for issue in schema_analysis['issues'] if issue.get('auto_fixable')]
                if auto_fixable_issues:
                    view = DatabaseFixView(auto_fixable_issues)
                
                embed.set_footer(text="🤖 Powered by MCP (Model Context Protocol)")
                
                await interaction.followup.send(embed=embed, view=view)
                
            except Exception as e:
                logger.error(f"❌ [MCP] Error en análisis: {e}")
                await interaction.followup.send(f"❌ Error en análisis: {str(e)}")
        
        @self.tree.command(name="admin_db_reset", description="[ADMIN] Resetea completamente la base de datos")
        async def reset_database(interaction: discord.Interaction, confirmacion: str):
            # Verificar permisos de administrador
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Solo los administradores pueden usar este comando", ephemeral=True)
                return
            
            # Verificar confirmación
            if confirmacion.lower() != "confirmar":
                await interaction.response.send_message("❌ Para resetear la base de datos, usa: `/admin_db_reset confirmacion:confirmar`", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            try:
                logger.warning(f"🔄 [RESET] {interaction.user.display_name} solicitó reset completo de base de datos")
                
                import os
                import shutil
                from datetime import datetime
                
                db_path = "unity_data/unity_master.db"
                
                if not os.path.exists(db_path):
                    embed = discord.Embed(
                        title="⚠️ Base de Datos No Existe",
                        description="No se encontró base de datos para resetear",
                        color=COLORS['WARNING']
                    )
                    await interaction.followup.send(embed=embed)
                    return
                
                # Crear backup antes de eliminar
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"unity_data/unity_master_backup_reset_{timestamp}.db"
                
                try:
                    shutil.copy2(db_path, backup_path)
                    backup_created = True
                except Exception as e:
                    logger.error(f"❌ Error creando backup: {e}")
                    backup_created = False
                
                # Eliminar base de datos
                try:
                    os.remove(db_path)
                    reset_success = True
                except Exception as e:
                    logger.error(f"❌ Error eliminando DB: {e}")
                    reset_success = False
                
                # Crear embed con resultados
                if reset_success:
                    embed = discord.Embed(
                        title="🔄 Base de Datos Reseteada",
                        description="La base de datos ha sido eliminada completamente",
                        color=COLORS['SUCCESS']
                    )
                    
                    embed.add_field(
                        name="📋 Acciones Realizadas",
                        value="✅ Base de datos eliminada\n🔄 Se creará nueva al reiniciar el bot",
                        inline=False
                    )
                    
                    if backup_created:
                        embed.add_field(
                            name="💾 Backup",
                            value=f"Backup automático: `{os.path.basename(backup_path)}`",
                            inline=False
                        )
                    
                    embed.add_field(
                        name="⚠️ Importante",
                        value="**Reinicia el bot** para crear una base de datos limpia con schema actualizado",
                        inline=False
                    )
                    
                    embed.set_footer(text="🤖 Reset completado por MCP")
                    
                else:
                    embed = discord.Embed(
                        title="❌ Error en Reset",
                        description="No se pudo eliminar la base de datos",
                        color=COLORS['ERROR']
                    )
                
                await interaction.followup.send(embed=embed)
                
                logger.warning(f"🔄 [RESET] Reset completado - Backup: {backup_created}")
                
            except Exception as e:
                logger.error(f"❌ [RESET] Error en reset: {e}")
                await interaction.followup.send(f"❌ Error en reset: {str(e)}")
        
        @self.tree.command(name="admin_db_fix", description="[ADMIN] Aplica correcciones automáticas a la DB")
        async def fix_database(interaction: discord.Interaction):
            # Verificar permisos de administrador
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Solo los administradores pueden usar este comando", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            try:
                logger.info(f"🔧 [MCP] {interaction.user.display_name} solicitó auto-reparación de DB")
                
                # Crear manager MCP
                mcp_manager = UnityMCPDatabaseManager()
                
                # Análisis inicial
                analysis = mcp_manager.analyze_database_schema()
                
                if not any(issue.get('auto_fixable') for issue in analysis['issues']):
                    embed = discord.Embed(
                        title="✅ Base de Datos Correcta",
                        description="No se encontraron problemas que requieran corrección automática",
                        color=COLORS['SUCCESS']
                    )
                    await interaction.followup.send(embed=embed)
                    return
                
                # Aplicar correcciones
                fix_report = mcp_manager.auto_fix_schema_issues(analysis)
                
                # Re-analizar
                post_analysis = mcp_manager.analyze_database_schema()
                
                # Crear embed con resultados
                embed = discord.Embed(
                    title="🔧 Correcciones Aplicadas",
                    description="Correcciones automáticas completadas",
                    color=COLORS['SUCCESS'] if len(fix_report['errors']) == 0 else COLORS['ERROR']
                )
                
                # Correcciones aplicadas
                if fix_report['fixes_applied']:
                    fixes_text = []
                    for fix in fix_report['fixes_applied']:
                        fixes_text.append(f"✅ {fix['description']}")
                    
                    embed.add_field(
                        name="🛠️ Correcciones Aplicadas",
                        value='\n'.join(fixes_text),
                        inline=False
                    )
                
                # Errores si los hay
                if fix_report['errors']:
                    errors_text = []
                    for error in fix_report['errors']:
                        errors_text.append(f"❌ {error.get('error', 'Error desconocido')}")
                    
                    embed.add_field(
                        name="⚠️ Errores",
                        value='\n'.join(errors_text),
                        inline=False
                    )
                
                # Backup info
                if fix_report['backup_created']:
                    embed.add_field(
                        name="💾 Backup",
                        value=f"Backup creado: `{os.path.basename(fix_report['backup_created'])}`",
                        inline=True
                    )
                
                # Estado final
                remaining_issues = len(post_analysis['issues'])
                embed.add_field(
                    name="📊 Estado Final",
                    value=f"Problemas restantes: {remaining_issues}",
                    inline=True
                )
                
                embed.set_footer(text="🤖 Auto-reparación completada por MCP")
                
                await interaction.followup.send(embed=embed)
                
                # Log importante
                logger.info(f"✅ [MCP] Auto-reparación completada - {len(fix_report['fixes_applied'])} correcciones aplicadas")
                
            except Exception as e:
                logger.error(f"❌ [MCP] Error en auto-reparación: {e}")
                await interaction.followup.send(f"❌ Error en auto-reparación: {str(e)}")

class DatabaseFixView(discord.ui.View):
    """Vista con botón para aplicar correcciones automáticas"""
    
    def __init__(self, auto_fixable_issues):
        super().__init__(timeout=300)  # 5 minutos
        self.auto_fixable_issues = auto_fixable_issues
    
    @discord.ui.button(label="🔧 Aplicar Correcciones Automáticas", style=discord.ButtonStyle.primary)
    async def apply_fixes(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verificar permisos
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Solo los administradores pueden aplicar correcciones", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Aplicar correcciones usando MCP
            mcp_manager = UnityMCPDatabaseManager()
            analysis = mcp_manager.analyze_database_schema()
            fix_report = mcp_manager.auto_fix_schema_issues(analysis)
            
            if fix_report['fixes_applied']:
                fixes_text = '\n'.join([f"✅ {fix['description']}" for fix in fix_report['fixes_applied']])
                
                embed = discord.Embed(
                    title="🎉 Correcciones Aplicadas Exitosamente",
                    description=fixes_text,
                    color=COLORS['SUCCESS']
                )
                
                if fix_report['backup_created']:
                    embed.add_field(
                        name="💾 Backup",
                        value=f"Backup automático: `{os.path.basename(fix_report['backup_created'])}`",
                        inline=False
                    )
                
                embed.set_footer(text="¡Ahora puedes usar /equipar_menu sin problemas!")
            else:
                embed = discord.Embed(
                    title="⚠️ No se Aplicaron Correcciones",
                    description="No se encontraron problemas auto-reparables o ya fueron corregidos",
                    color=COLORS['WARNING']
                )
            
            # Deshabilitar el botón
            button.disabled = True
            await interaction.followup.edit_message(interaction.message.id, view=self)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error aplicando correcciones: {str(e)}", ephemeral=True)