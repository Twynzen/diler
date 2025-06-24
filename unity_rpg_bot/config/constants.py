"""
Constantes del sistema de juego Unity RPG
"""

# Atributos base para personajes
BASE_ATTRIBUTES = ['Fuerza', 'Destreza', 'Velocidad', 'Resistencia', 'Inteligencia', 'Mana']

# Tipos de dados disponibles
DICE_TYPES = [3, 6, 8, 10, 12, 20]

# Máximo número de dados que se pueden tirar simultáneamente
MAX_DICE_COUNT = 5

# Puntos de golpe fijos para todos los personajes y NPCs
FIXED_HP = 10

# Mapeo de acciones de combate a atributos para personajes
PLAYER_ACTION_MAPPING = {
    'ataque_fisico': 'fuerza',
    'ataque_magico': 'mana', 
    'ataque_distancia': 'destreza',
    'defensa_fisica': 'resistencia',
    'defensa_magica': 'destreza',
    'defensa_esquive': 'velocidad'
}

# Mapeo de acciones de combate para NPCs (usa estadísticas específicas)
NPC_ACTION_MAPPING = {
    'fisico': 'ataq_fisic',
    'distancia': 'ataq_dist', 
    'magico': 'ataq_magic',
    'defensa_fisica': 'res_fisica',
    'defensa_magica': 'res_magica',
    'esquivar': 'velocidad'
}

# Colores para embeds de Discord
COLORS = {
    'SUCCESS': 0x00ff00,
    'WARNING': 0xff6600,
    'ERROR': 0xff0000,
    'INFO': 0x0099ff,
    'CRITICAL': 0x8b0000,
    'LEGENDARY': 0xffd700,
    'CHARACTER': 0x9932cc,
    'NPC': 0xff4444,
    'ITEM': 0x9932cc
}

# Emojis para diferentes elementos del juego
EMOJIS = {
    'attributes': {
        'fuerza': '💪',
        'destreza': '🎯', 
        'velocidad': '⚡',
        'resistencia': '🛡️',
        'inteligencia': '🧠',
        'mana': '🔮'
    },
    'actions': {
        'fisico': '⚔️',
        'magico': '🔮',
        'distancia': '🏹',
        'defensa_fisica': '🛡️',
        'defensa_magica': '✨',
        'esquivar': '🏃'
    },
    'rarity': {
        'comun': '⚪',
        'raro': '🔵',
        'epico': '🟣',
        'legendario': '🟠'
    }
}

# Rangos de éxito para tiradas
SUCCESS_RANGES = {
    'FUMBLE': 1,
    'FAILURE_LOW': (2, 10),
    'FAILURE_MID': (11, 11),
    'SUCCESS_LOW': (12, 14),
    'SUCCESS_MID': (15, 17),
    'SUCCESS_HIGH': (18, 19),
    'CRITICAL': 20
}