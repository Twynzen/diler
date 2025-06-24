"""
Selectores interactivos para la interfaz de Discord
"""
import discord
from unity_rpg_bot.config.constants import COLORS
from unity_rpg_bot.game.dice_system import dice_system
from unity_rpg_bot.game.inventory import inventory_system
from unity_rpg_bot.utils.logging import logger


class NPCActionSelect(discord.ui.Select):
    def __init__(self, npc_name):
        self.npc_name = npc_name
        
        options = [
            # Ataques
            discord.SelectOption(
                label="Ataque Físico", 
                description="Daño fijo basado en ATAQ_FISIC", 
                emoji="⚔️", 
                value="fisico"
            ),
            discord.SelectOption(
                label="Ataque Mágico", 
                description="Daño fijo basado en ATAQ_MAGIC", 
                emoji="🔮", 
                value="magico"
            ),
            discord.SelectOption(
                label="Ataque a Distancia", 
                description="Daño fijo basado en ATAQ_DIST", 
                emoji="🏹", 
                value="distancia"
            ),
            # Defensas
            discord.SelectOption(
                label="Defensa Física", 
                description="Defensa basada en RES_FISICA", 
                emoji="🛡️", 
                value="defensa_fisica"
            ),
            discord.SelectOption(
                label="Defensa Mágica", 
                description="Defensa basada en RES_MAGICA", 
                emoji="✨", 
                value="defensa_magica"
            ),
            discord.SelectOption(
                label="Esquivar", 
                description="Esquive basado en VELOCIDAD", 
                emoji="🏃", 
                value="esquivar"
            )
        ]
        
        super().__init__(placeholder="🎯 Selecciona la acción del NPC...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        """Maneja la selección de acción del NPC"""
        result = dice_system.npc_action(self.npc_name, self.values[0])
        
        if not result:
            await interaction.response.send_message(
                f"❌ NPC **{self.npc_name}** no encontrado", 
                ephemeral=True
            )
            return
        
        # Determinar colores y descripción según el resultado
        if result['action_category'] == 'ataque':
            color = COLORS['ERROR']
            if result['total_value'] >= 50:
                embed_desc = "💀 **¡ATAQUE DEVASTADOR!**"
                color = COLORS['CRITICAL']
            elif result['total_value'] >= 30:
                embed_desc = "⚔️ **¡ATAQUE PODEROSO!**"
            elif result['total_value'] >= 15:
                embed_desc = "✅ **Ataque Efectivo**"
            else:
                embed_desc = "👊 **Ataque Básico**"
        else:  # defensa
            color = COLORS['INFO']
            if result['total_value'] >= 50:
                embed_desc = "🛡️ **¡DEFENSA IMPENETRABLE!**"
                color = 0x000080
            elif result['total_value'] >= 30:
                embed_desc = "🛡️ **¡DEFENSA SÓLIDA!**"
            elif result['total_value'] >= 15:
                embed_desc = "✅ **Defensa Efectiva**"
            else:
                embed_desc = "🛡️ **Defensa Básica**"
        
        # Mapeo de emojis y nombres de acciones
        action_emoji = {
            'fisico': '⚔️', 'magico': '🔮', 'distancia': '🏹',
            'defensa_fisica': '🛡️', 'defensa_magica': '✨', 'esquivar': '🏃'
        }
        
        action_names = {
            'fisico': 'Ataque Físico', 'magico': 'Ataque Mágico', 'distancia': 'Ataque a Distancia',
            'defensa_fisica': 'Defensa Física', 'defensa_magica': 'Defensa Mágica', 'esquivar': 'Esquivar'
        }
        
        emoji = action_emoji.get(result['action_type'], '🎯')
        action_name = action_names.get(result['action_type'], result['action_type'].title())
        
        # Crear embed de resultado
        embed = discord.Embed(
            title=f"👹 {result['action_description']} - {action_name}", 
            color=color
        )
        embed.description = embed_desc
        
        if result['sincronizado']:
            embed.add_field(name="🤝 NPCs Sincronizados", value=f"{result['cantidad']} unidades", inline=True)
            embed.add_field(name="💪 Valor Base c/u", value=f"`{result['base_value']}`", inline=True)
            value_name = "🏆 **DAÑO TOTAL**" if result['action_category'] == 'ataque' else "🛡️ **DEFENSA TOTAL**"
            embed.add_field(name=value_name, value=f"**`{result['total_value']}`**", inline=True)
        else:
            embed.add_field(name="👤 NPC Individual", value=result['npc_name'], inline=True)
            value_name = "🏆 **DAÑO**" if result['action_category'] == 'ataque' else "🛡️ **DEFENSA**"
            embed.add_field(name=value_name, value=f"**`{result['total_value']}`**", inline=True)
        
        if result['imagen_url']:
            embed.set_thumbnail(url=result['imagen_url'])
        
        await interaction.response.edit_message(embed=embed, view=None)


class EquipItemSelect(discord.ui.Select):
    def __init__(self, character_name, items):
        self.character_name = character_name
        
        options = []
        for item in items[:25]:  # Discord limite de 25 opciones
            nombre, equipado, rareza = item[0], item[1], item[2]
            status_emoji = "✅" if equipado else "⚪"
            
            options.append(discord.SelectOption(
                label=nombre,
                description=f"{'Equipado' if equipado else 'No equipado'} - {rareza.title()}",
                emoji=status_emoji,
                value=nombre
            ))
        
        super().__init__(placeholder="🎒 Selecciona un item para equipar/desequipar...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        """Maneja el equipamiento/desequipamiento de items"""
        item_name = self.values[0]
        
        success, status, message = inventory_system.toggle_item_equipment(self.character_name, item_name)
        
        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return
        
        # Determinar color y emoji según el estado
        if status == "equipado":
            color = COLORS['SUCCESS']
            emoji = "⚔️"
        else:
            color = COLORS['WARNING'] 
            emoji = "📤"
        
        embed = discord.Embed(
            title=f"{emoji} Item {status.title()}", 
            description=message, 
            color=color
        )
        
        await interaction.response.edit_message(embed=embed, view=None)