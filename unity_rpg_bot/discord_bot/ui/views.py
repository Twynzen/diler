"""
Vistas (Views) para componentes UI de Discord
"""
import discord
from unity_rpg_bot.discord_bot.ui.selectors import NPCActionSelect, EquipItemSelect


class NPCActionView(discord.ui.View):
    """Vista para selección de acciones de NPCs"""
    
    def __init__(self, npc_name):
        super().__init__(timeout=60)
        self.add_item(NPCActionSelect(npc_name))


class EquipItemView(discord.ui.View):
    """Vista para equipar/desequipar items"""
    
    def __init__(self, character_name, items):
        super().__init__(timeout=60)
        self.add_item(EquipItemSelect(character_name, items))