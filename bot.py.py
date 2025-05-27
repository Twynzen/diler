"""
🎲 Unity RPG Bot - Versión Optimizada Completa
Características: Sistema completo de roleplay con inventario, equipamiento y NPCs
Límite: 1800 líneas manteniendo funcionalidad completa
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging
import os
import random
import pandas as pd
import sqlite3
import gspread
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# ============= CONFIGURACIÓN =============
class UnityConfig:
    def __init__(self):
        load_dotenv()
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        self.BOT_NAME = os.getenv('BOT_NAME', 'UnityRPG')
        self.GUILD_NAME = os.getenv('GUILD_NAME', 'Servidor Unity')
        self.GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'google-credentials.json')
        
        # Directorios
        self.DATA_DIR = "unity_data"
        self.EXCEL_DIR = f"{self.DATA_DIR}/personajes"
        self.IMAGES_DIR = f"{self.DATA_DIR}/imagenes"
        self.LOGS_DIR = f"{self.DATA_DIR}/logs"
        self.DB_PATH = f"{self.DATA_DIR}/unity_master.db"
        
        # Atributos base
        self.BASE_ATTRIBUTES = ['Fuerza', 'Destreza', 'Velocidad', 'Inteligencia', 'Mana']
        self.DEFENSE_TYPES = ['Defensa_Esquive', 'Defensa_Fisica', 'Defensa_Magica']
        
        self.create_directories()
        
    def create_directories(self):
        dirs = [self.DATA_DIR, self.EXCEL_DIR, self.IMAGES_DIR, self.LOGS_DIR,
                f"{self.EXCEL_DIR}/activos", f"{self.EXCEL_DIR}/archivados"]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)

config = UnityConfig()

# ============= LOGGING =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{config.LOGS_DIR}/unity.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("UnityRPG")

# ============= BASE DE DATOS =============
class DatabaseManager:
    def __init__(self):
        self.db_path = config.DB_PATH
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Personajes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    usuario_id TEXT NOT NULL,
                    excel_path TEXT NOT NULL,
                    descripcion TEXT,
                    puntos_vida_actual INTEGER DEFAULT 100,
                    puntos_vida_max INTEGER DEFAULT 100,
                    oro INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'activo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # NPCs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npcs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    nivel INTEGER DEFAULT 1,
                    puntos_vida_actual INTEGER DEFAULT 100,
                    puntos_vida_max INTEGER DEFAULT 100,
                    ataque_fisico INTEGER DEFAULT 10,
                    ataque_magico INTEGER DEFAULT 10,
                    defensa_fisica INTEGER DEFAULT 10,
                    defensa_magica INTEGER DEFAULT 10,
                    defensa_esquive INTEGER DEFAULT 10,
                    velocidad INTEGER DEFAULT 10,
                    inteligencia INTEGER DEFAULT 10,
                    descripcion TEXT,
                    ubicacion TEXT DEFAULT 'Varias',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    subtipo TEXT,
                    rareza TEXT DEFAULT 'comun',
                    descripcion TEXT,
                    efecto_fuerza INTEGER DEFAULT 0,
                    efecto_destreza INTEGER DEFAULT 0,
                    efecto_velocidad INTEGER DEFAULT 0,
                    efecto_inteligencia INTEGER DEFAULT 0,
                    efecto_mana INTEGER DEFAULT 0,
                    efecto_def_esquive INTEGER DEFAULT 0,
                    efecto_def_fisica INTEGER DEFAULT 0,
                    efecto_def_magica INTEGER DEFAULT 0,
                    precio INTEGER DEFAULT 0,
                    es_equipable BOOLEAN DEFAULT TRUE,
                    slot_equipo TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Inventarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personaje_id INTEGER,
                    item_id INTEGER,
                    cantidad INTEGER DEFAULT 1,
                    equipado BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (personaje_id) REFERENCES personajes (id),
                    FOREIGN KEY (item_id) REFERENCES items (id)
                )
            """)
            
            conn.commit()
            logger.info("✅ Base de datos inicializada")

db = DatabaseManager()

# ============= GOOGLE SHEETS =============
class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.init_google_sheets()
    
    def init_google_sheets(self):
        try:
            if not os.path.exists(config.GOOGLE_CREDENTIALS_FILE):
                logger.warning("⚠️ Google Sheets no configurado")
                return
                
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_FILE, scopes=scope)
            self.client = gspread.authorize(creds)
            
            try:
                self.spreadsheet = self.client.open(f"Unity RPG - {config.GUILD_NAME}")
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.client.create(f"Unity RPG - {config.GUILD_NAME}")
                
            logger.info("✅ Google Sheets conectado")
        except Exception as e:
            logger.error(f"❌ Google Sheets error: {e}")
    
    def sync_character(self, character_name, stats):
        if not self.client:
            return
        try:
            worksheet_name = f"PJ_{character_name}"
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=20, cols=6)
            
            data = [['ATRIBUTO', 'BASE', 'BONUS', 'TOTAL']]
            for attr, values in stats.items():
                data.append([attr.title(), values['base'], values['bonus'], values['total']])
            
            worksheet.clear()
            worksheet.update('A1', data)
            logger.info(f"✅ {character_name} sincronizado")
        except Exception as e:
            logger.error(f"❌ Error sincronizando: {e}")

google_sheets = GoogleSheetsManager()

# ============= EXCEL MANAGER =============
class ExcelManager:
    @staticmethod
    def create_character_excel(character_name, user_id, initial_stats=None):
        if initial_stats is None:
            initial_stats = {}
            
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        
        character_data = {
            'Atributo': config.BASE_ATTRIBUTES + config.DEFENSE_TYPES,
            'Valor': [
                initial_stats.get('fuerza', 10), initial_stats.get('destreza', 10),
                initial_stats.get('velocidad', 10), initial_stats.get('inteligencia', 10),
                initial_stats.get('mana', 10), initial_stats.get('def_esquive', 10),
                initial_stats.get('def_fisica', 10), initial_stats.get('def_magica', 10)
            ]
        }
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_stats = pd.DataFrame(character_data)
            df_stats.to_excel(writer, sheet_name='Estadisticas', index=False)
            
            info_data = {
                'Campo': ['Nombre', 'Usuario_ID', 'PV_Actual', 'PV_Max', 'Oro'],
                'Valor': [character_name, str(user_id), 100, 100, 0]
            }
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='Info', index=False)
        
        logger.info(f"✅ Excel creado para {character_name}")
        return file_path
    
    @staticmethod
    def read_character_stats(character_name):
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        if not os.path.exists(file_path):
            return None
            
        try:
            df = pd.read_excel(file_path, sheet_name='Estadisticas')
            stats = {}
            for _, row in df.iterrows():
                attr_name = row['Atributo'].lower().replace('_', '')
                stats[attr_name] = {'base': int(row['Valor']), 'bonus': 0, 'total': int(row['Valor'])}
            return stats
        except Exception as e:
            logger.error(f"❌ Error leyendo stats: {e}")
            return None

excel_manager = ExcelManager()

# ============= INVENTORY SYSTEM =============
class InventorySystem:
    @staticmethod
    def calculate_equipped_bonuses(character_name):
        bonuses = {attr: 0 for attr in ['fuerza', 'destreza', 'velocidad', 'inteligencia', 'mana', 
                                       'defensaesquive', 'defensafisica', 'defensamagica']}
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.efecto_fuerza, i.efecto_destreza, i.efecto_velocidad,
                           i.efecto_inteligencia, i.efecto_mana, i.efecto_def_esquive,
                           i.efecto_def_fisica, i.efecto_def_magica
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ? AND inv.equipado = TRUE
                """, (character_name,))
                
                for row in cursor.fetchall():
                    attrs = ['fuerza', 'destreza', 'velocidad', 'inteligencia', 'mana', 
                            'defensaesquive', 'defensafisica', 'defensamagica']
                    for i, attr in enumerate(attrs):
                        bonuses[attr] += row[i] or 0
        except Exception as e:
            logger.error(f"❌ Error calculando bonuses: {e}")
        return bonuses
    
    @staticmethod
    def get_character_inventory(character_name):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.nombre, i.tipo, i.rareza, inv.cantidad, inv.equipado,
                           i.efecto_fuerza, i.efecto_destreza, i.efecto_velocidad,
                           i.efecto_inteligencia, i.efecto_mana, i.efecto_def_esquive,
                           i.efecto_def_fisica, i.efecto_def_magica
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ?
                    ORDER BY inv.equipado DESC, i.nombre
                """, (character_name,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ Error obteniendo inventario: {e}")
            return []

inventory_system = InventorySystem()

# ============= DICE SYSTEM =============
class DiceSystem:
    @staticmethod
    def roll_attack(character_name, attack_type, bonificador=0):
        # Obtener stats base
        base_stats = excel_manager.read_character_stats(character_name)
        if not base_stats:
            return None
        
        # Obtener bonuses de items
        item_bonuses = inventory_system.calculate_equipped_bonuses(character_name)
        
        # Combinar stats
        combined_stats = {}
        for attr in base_stats:
            combined_stats[attr] = {
                'base': base_stats[attr]['base'],
                'bonus': item_bonuses.get(attr, 0),
                'total': base_stats[attr]['base'] + item_bonuses.get(attr, 0)
            }
        
        dice_roll = random.randint(1, 20)
        attack_mapping = {'fisico': 'fuerza', 'magico': 'mana', 'distancia': 'destreza'}
        
        if attack_type not in attack_mapping:
            return None
            
        attr_key = attack_mapping[attack_type]
        attr_value = combined_stats[attr_key]['total']
        total = dice_roll + attr_value + bonificador
        
        logger.info(f"[DADOS] {character_name} - Ataque {attack_type}: D20({dice_roll}) + {attr_key.title()}({attr_value}) + Bonus({bonificador}) = {total}")
        
        return {
            'dice': dice_roll, 'attribute': attr_value, 'attribute_name': attr_key.title(),
            'bonuses': bonificador, 'total': total, 'attack_type': attack_type,
            'is_critical': dice_roll == 20, 'is_fumble': dice_roll == 1
        }
    
    @staticmethod
    def roll_defense(character_name, defense_type, bonificador=0):
        base_stats = excel_manager.read_character_stats(character_name)
        if not base_stats:
            return None
        
        item_bonuses = inventory_system.calculate_equipped_bonuses(character_name)
        
        combined_stats = {}
        for attr in base_stats:
            combined_stats[attr] = {
                'base': base_stats[attr]['base'],
                'bonus': item_bonuses.get(attr, 0),
                'total': base_stats[attr]['base'] + item_bonuses.get(attr, 0)
            }
        
        dice_roll = random.randint(1, 20)
        defense_mapping = {'esquive': 'defensaesquive', 'fisica': 'defensafisica', 'magica': 'defensamagica'}
        
        if defense_type not in defense_mapping:
            return None
            
        attr_key = defense_mapping[defense_type]
        attr_value = combined_stats[attr_key]['total']
        total = dice_roll + attr_value + bonificador
        
        logger.info(f"[DADOS] {character_name} - Defensa {defense_type}: D20({dice_roll}) + Def.{defense_type.title()}({attr_value}) + Bonus({bonificador}) = {total}")
        
        return {
            'dice': dice_roll, 'attribute': attr_value, 'attribute_name': f"Defensa {defense_type.title()}",
            'bonuses': bonificador, 'total': total, 'defense_type': defense_type,
            'is_critical': dice_roll == 20, 'is_fumble': dice_roll == 1
        }

dice_system = DiceSystem()

# ============= INTERACTIVE MENUS =============
class AttackTypeSelect(discord.ui.Select):
    def __init__(self, character_name, bonificador=0):
        self.character_name = character_name
        self.bonificador = bonificador
        
        options = [
            discord.SelectOption(label="Ataque Físico", description="Usa Fuerza", emoji="⚔️", value="fisico"),
            discord.SelectOption(label="Ataque Mágico", description="Usa Maná", emoji="🔮", value="magico"),
            discord.SelectOption(label="Ataque a Distancia", description="Usa Destreza", emoji="🏹", value="distancia")
        ]
        
        super().__init__(placeholder="🎯 Selecciona tu tipo de ataque...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        result = dice_system.roll_attack(self.character_name, self.values[0], self.bonificador)
        
        if not result:
            await interaction.response.send_message(f"❌ Personaje **{self.character_name}** no encontrado", ephemeral=True)
            return
        
        color = 0x00ff00 if result['total'] >= 18 else 0xff6600 if result['total'] >= 12 else 0xff0000
        embed = discord.Embed(title=f"⚔️ Ataque {result['attack_type'].title()} - {self.character_name}", color=color)
        
        if result['is_critical']:
            embed.description = "🎯 **¡CRÍTICO DEVASTADOR!**"
            embed.color = 0xffd700
        elif result['is_fumble']:
            embed.description = "💥 **¡PIFIA ÉPICA!**"
            embed.color = 0x8b0000
        elif result['total'] >= 25:
            embed.description = "🌟 **¡ATAQUE LEGENDARIO!**"
        elif result['total'] >= 15:
            embed.description = "✅ **Ataque Exitoso**"
        else:
            embed.description = "❌ **Ataque Fallido**"
        
        embed.add_field(name="🎲 Dado", value=f"`{result['dice']}`", inline=True)
        embed.add_field(name=f"📊 {result['attribute_name']}", value=f"`{result['attribute']}`", inline=True)
        if self.bonificador != 0:
            embed.add_field(name="➕ Bonus", value=f"`{self.bonificador}`", inline=True)
        embed.add_field(name="🏆 **TOTAL**", value=f"**`{result['total']}`**", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)

class DefenseTypeSelect(discord.ui.Select):
    def __init__(self, character_name, bonificador=0):
        self.character_name = character_name
        self.bonificador = bonificador
        
        options = [
            discord.SelectOption(label="Defensa por Esquive", description="Evita con agilidad", emoji="🏃", value="esquive"),
            discord.SelectOption(label="Defensa Física", description="Bloquea daño físico", emoji="🛡️", value="fisica"),
            discord.SelectOption(label="Defensa Mágica", description="Resiste magia", emoji="✨", value="magica")
        ]
        
        super().__init__(placeholder="🛡️ Selecciona tu defensa...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        result = dice_system.roll_defense(self.character_name, self.values[0], self.bonificador)
        
        if not result:
            await interaction.response.send_message(f"❌ Personaje **{self.character_name}** no encontrado", ephemeral=True)
            return
        
        color = 0x0099ff if result['total'] >= 15 else 0xff6600 if result['total'] >= 12 else 0xff0000
        embed = discord.Embed(title=f"🛡️ Defensa {result['defense_type'].title()} - {self.character_name}", color=color)
        
        if result['is_critical']:
            embed.description = "🎯 **¡DEFENSA PERFECTA!**"
            embed.color = 0x00ffff
        elif result['is_fumble']:
            embed.description = "💥 **¡DEFENSA FALLIDA!**"
            embed.color = 0x8b0000
        elif result['total'] >= 25:
            embed.description = "🌟 **¡DEFENSA LEGENDARIA!**"
        elif result['total'] >= 15:
            embed.description = "✅ **Defensa Exitosa**"
        else:
            embed.description = "❌ **Defensa Fallida**"
        
        embed.add_field(name="🎲 Dado", value=f"`{result['dice']}`", inline=True)
        embed.add_field(name=f"📊 {result['attribute_name']}", value=f"`{result['attribute']}`", inline=True)
        if self.bonificador != 0:
            embed.add_field(name="➕ Bonus", value=f"`{self.bonificador}`", inline=True)
        embed.add_field(name="🏆 **TOTAL**", value=f"**`{result['total']}`**", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)

class AttackView(discord.ui.View):
    def __init__(self, character_name, bonificador=0):
        super().__init__(timeout=60)
        self.add_item(AttackTypeSelect(character_name, bonificador))

class DefenseView(discord.ui.View):
    def __init__(self, character_name, bonificador=0):
        super().__init__(timeout=60)
        self.add_item(DefenseTypeSelect(character_name, bonificador))

# ============= BOT SETUP =============
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    logger.info(f"✅ {config.BOT_NAME} conectado como {client.user}")
    try:
        synced = await tree.sync()
        logger.info(f"📡 {len(synced)} comandos sincronizados")
    except Exception as e:
        logger.error(f"❌ Error sincronizando: {e}")

# ============= COMANDOS =============

@tree.command(name="crear_personaje", description="Crea un personaje épico SIN LÍMITES")
async def create_character(interaction: discord.Interaction, nombre: str, fuerza: int = 10, destreza: int = 10, 
                         velocidad: int = 10, inteligencia: int = 10, mana: int = 10, def_esquive: int = 10, 
                         def_fisica: int = 10, def_magica: int = 10, descripcion: str = "Un aventurero misterioso"):
    await interaction.response.defer()
    
    try:
        initial_stats = {'fuerza': fuerza, 'destreza': destreza, 'velocidad': velocidad, 
                        'inteligencia': inteligencia, 'mana': mana, 'def_esquive': def_esquive,
                        'def_fisica': def_fisica, 'def_magica': def_magica}
        
        excel_path = excel_manager.create_character_excel(nombre, interaction.user.id, initial_stats)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO personajes (nombre, usuario_id, excel_path, descripcion) VALUES (?, ?, ?, ?)",
                         (nombre, str(interaction.user.id), excel_path, descripcion))
            conn.commit()
        
        embed = discord.Embed(title="🎭 ¡Personaje Creado!", description=f"**{nombre}** ha despertado en Unity", color=0x00ff00)
        embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
        
        stats_text = f"💪 **Fuerza:** {fuerza}\n🎯 **Destreza:** {destreza}\n⚡ **Velocidad:** {velocidad}\n🧠 **Inteligencia:** {inteligencia}\n🔮 **Maná:** {mana}"
        embed.add_field(name="📊 Atributos", value=stats_text, inline=True)
        
        def_text = f"🏃 **Esquive:** {def_esquive}\n🛡️ **Física:** {def_fisica}\n✨ **Mágica:** {def_magica}"
        embed.add_field(name="🛡️ Defensas", value=def_text, inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error creando personaje: {e}")
        await interaction.followup.send("❌ Error interno o personaje ya existe")

@tree.command(name="crear_npc", description="Crea un NPC completo")
async def create_npc(interaction: discord.Interaction, nombre: str, tipo: str, nivel: int = 1, vida_max: int = 100,
                    ataque_fisico: int = 10, ataque_magico: int = 10, defensa_fisica: int = 10, 
                    defensa_magica: int = 10, defensa_esquive: int = 10, velocidad: int = 10,
                    inteligencia: int = 10, descripcion: str = "Un ser del universo Unity"):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO npcs (nombre, tipo, nivel, puntos_vida_actual, puntos_vida_max,
                            ataque_fisico, ataque_magico, defensa_fisica, defensa_magica, defensa_esquive,
                            velocidad, inteligencia, descripcion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (nombre, tipo, nivel, vida_max, vida_max, ataque_fisico, ataque_magico, defensa_fisica,
                          defensa_magica, defensa_esquive, velocidad, inteligencia, descripcion))
            conn.commit()
        
        embed = discord.Embed(title="👹 ¡NPC Creado!", description=f"**{nombre}** añadido al universo", color=0xff4444)
        embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
        embed.add_field(name="📊 Nivel", value=str(nivel), inline=True)
        embed.add_field(name="❤️ Vida", value=f"{vida_max} PV", inline=True)
        
        combat_text = f"⚔️ **At. Físico:** {ataque_fisico}\n🔮 **At. Mágico:** {ataque_magico}"
        embed.add_field(name="⚔️ Combate", value=combat_text, inline=True)
        
        def_text = f"🏃 **Esquive:** {defensa_esquive}\n🛡️ **Física:** {defensa_fisica}\n✨ **Mágica:** {defensa_magica}"
        embed.add_field(name="🛡️ Defensas", value=def_text, inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error creando NPC: {e}")
        await interaction.followup.send("❌ Error interno o NPC ya existe")

@tree.command(name="crear_item", description="Crea un item equipable")
async def create_item(interaction: discord.Interaction, nombre: str, tipo: str, descripcion: str = "",
                     efecto_fuerza: int = 0, efecto_destreza: int = 0, efecto_velocidad: int = 0,
                     efecto_inteligencia: int = 0, efecto_mana: int = 0, efecto_def_esquive: int = 0,
                     efecto_def_fisica: int = 0, efecto_def_magica: int = 0, rareza: str = "comun",
                     precio: int = 0):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO items (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza,
                            efecto_velocidad, efecto_inteligencia, efecto_mana, efecto_def_esquive,
                            efecto_def_fisica, efecto_def_magica, rareza, precio)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza, efecto_velocidad,
                          efecto_inteligencia, efecto_mana, efecto_def_esquive, efecto_def_fisica,
                          efecto_def_magica, rareza, precio))
            conn.commit()
        
        embed = discord.Embed(title="✨ ¡Item Creado!", description=f"**{nombre}** ha sido forjado", color=0x9932cc)
        embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
        embed.add_field(name="⭐ Rareza", value=rareza.title(), inline=True)
        embed.add_field(name="💰 Precio", value=f"{precio} oro", inline=True)
        
        if descripcion:
            embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
        
        # Mostrar efectos
        effects = []
        effect_mapping = {
            'efecto_fuerza': ('💪 Fuerza', efecto_fuerza),
            'efecto_destreza': ('🎯 Destreza', efecto_destreza),
            'efecto_velocidad': ('⚡ Velocidad', efecto_velocidad),
            'efecto_inteligencia': ('🧠 Inteligencia', efecto_inteligencia),
            'efecto_mana': ('🔮 Maná', efecto_mana),
            'efecto_def_esquive': ('🏃 Def. Esquive', efecto_def_esquive),
            'efecto_def_fisica': ('🛡️ Def. Física', efecto_def_fisica),
            'efecto_def_magica': ('✨ Def. Mágica', efecto_def_magica)
        }
        
        for key, (name, value) in effect_mapping.items():
            if value != 0:
                sign = '+' if value > 0 else ''
                effects.append(f"{name}: {sign}{value}")
        
        if effects:
            embed.add_field(name="⚡ Efectos", value='\n'.join(effects[:4]), inline=True)
            if len(effects) > 4:
                embed.add_field(name="⚡ Más Efectos", value='\n'.join(effects[4:]), inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error creando item: {e}")
        await interaction.followup.send("❌ Error interno o item ya existe")

@tree.command(name="dar_item", description="Entrega un item a un personaje")
async def give_item(interaction: discord.Interaction, personaje: str, item: str, cantidad: int = 1):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar personaje
            cursor.execute("SELECT id FROM personajes WHERE nombre = ?", (personaje,))
            char_result = cursor.fetchone()
            if not char_result:
                await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                return
            
            # Verificar item
            cursor.execute("SELECT id, nombre FROM items WHERE nombre = ?", (item,))
            item_result = cursor.fetchone()
            if not item_result:
                await interaction.followup.send(f"❌ Item **{item}** no encontrado")
                return
            
            char_id, item_id = char_result[0], item_result[0]
            
            # Verificar si ya tiene el item
            cursor.execute("SELECT id, cantidad FROM inventarios WHERE personaje_id = ? AND item_id = ?", 
                         (char_id, item_id))
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar cantidad
                cursor.execute("UPDATE inventarios SET cantidad = cantidad + ? WHERE id = ?", 
                             (cantidad, existing[0]))
                new_cantidad = existing[1] + cantidad
            else:
                # Crear nueva entrada
                cursor.execute("INSERT INTO inventarios (personaje_id, item_id, cantidad) VALUES (?, ?, ?)",
                             (char_id, item_id, cantidad))
                new_cantidad = cantidad
            
            conn.commit()
        
        embed = discord.Embed(title="🎁 Item Entregado", 
                            description=f"**{item}** x{cantidad} entregado a **{personaje}**", 
                            color=0x00ff00)
        embed.add_field(name="📦 Total en Inventario", value=f"{new_cantidad} unidades", inline=True)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error dando item: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="inventario", description="Muestra el inventario de un personaje")
async def show_inventory(interaction: discord.Interaction, personaje: str):
    await interaction.response.defer()
    
    try:
        inventory = inventory_system.get_character_inventory(personaje)
        
        if not inventory:
            await interaction.followup.send(f"❌ **{personaje}** no tiene items o no existe")
            return
        
        embed = discord.Embed(title=f"🎒 Inventario de {personaje}", color=0x9932cc)
        
        equipped_items = []
        regular_items = []
        
        for item in inventory:
            nombre, tipo, rareza, cantidad, equipado = item[0], item[1], item[2], item[3], item[4]
            
            # Crear línea del item
            rarity_emoji = {"comun": "⚪", "raro": "🔵", "epico": "🟣", "legendario": "🟠"}.get(rareza, "⚪")
            equip_status = "✅ Equipado" if equipado else ""
            item_line = f"{rarity_emoji} **{nombre}** x{cantidad} {equip_status}"
            
            if equipado:
                equipped_items.append(item_line)
            else:
                regular_items.append(item_line)
        
        # Mostrar items equipados primero
        if equipped_items:
            embed.add_field(name="⚔️ Items Equipados", value='\n'.join(equipped_items[:10]), inline=False)
        
        # Mostrar items regulares
        if regular_items:
            # Dividir en chunks si hay muchos items
            chunks = [regular_items[i:i+10] for i in range(0, len(regular_items), 10)]
            for i, chunk in enumerate(chunks[:2]):  # Máximo 2 chunks
                field_name = "📦 Items en Inventario" if i == 0 else "📦 Más Items"
                embed.add_field(name=field_name, value='\n'.join(chunk), inline=False)
        
        embed.set_footer(text=f"Total de tipos de items: {len(inventory)}")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error mostrando inventario: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="equipar", description="Equipa un item del inventario")
async def equip_item(interaction: discord.Interaction, personaje: str, item: str):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el personaje tiene el item
            cursor.execute("""SELECT inv.id, inv.equipado FROM inventarios inv
                            JOIN personajes p ON inv.personaje_id = p.id
                            JOIN items i ON inv.item_id = i.id
                            WHERE p.nombre = ? AND i.nombre = ?""", (personaje, item))
            result = cursor.fetchone()
            
            if not result:
                await interaction.followup.send(f"❌ **{personaje}** no tiene el item **{item}**")
                return
            
            inv_id, equipado = result
            
            if equipado:
                # Desequipar
                cursor.execute("UPDATE inventarios SET equipado = FALSE WHERE id = ?", (inv_id,))
                status = "desequipado"
                color = 0xff6600
                emoji = "📤"
            else:
                # Equipar
                cursor.execute("UPDATE inventarios SET equipado = TRUE WHERE id = ?", (inv_id,))
                status = "equipado"
                color = 0x00ff00
                emoji = "⚔️"
            
            conn.commit()
        
        embed = discord.Embed(title=f"{emoji} Item {status.title()}", 
                            description=f"**{item}** {status} por **{personaje}**", 
                            color=color)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error equipando item: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="quitar_item", description="Quita un item del inventario")
async def remove_item(interaction: discord.Interaction, personaje: str, item: str, cantidad: int = 1):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener info del item en inventario
            cursor.execute("""SELECT inv.id, inv.cantidad FROM inventarios inv
                            JOIN personajes p ON inv.personaje_id = p.id
                            JOIN items i ON inv.item_id = i.id
                            WHERE p.nombre = ? AND i.nombre = ?""", (personaje, item))
            result = cursor.fetchone()
            
            if not result:
                await interaction.followup.send(f"❌ **{personaje}** no tiene el item **{item}**")
                return
            
            inv_id, current_cantidad = result
            
            if current_cantidad <= cantidad:
                # Eliminar completamente
                cursor.execute("DELETE FROM inventarios WHERE id = ?", (inv_id,))
                message = f"**{item}** eliminado completamente del inventario de **{personaje}**"
            else:
                # Reducir cantidad
                cursor.execute("UPDATE inventarios SET cantidad = cantidad - ? WHERE id = ?", 
                             (cantidad, inv_id))
                message = f"**{item}** x{cantidad} removido del inventario de **{personaje}**"
            
            conn.commit()
        
        embed = discord.Embed(title="🗑️ Item Removido", description=message, color=0xff6600)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error quitando item: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="tirar", description="Sistema de tiradas con menús interactivos")
async def roll_dice(interaction: discord.Interaction, personaje: str, accion: str, bonificador: int = 0):
    await interaction.response.defer()
    
    try:
        if accion.lower() == "ataque":
            embed = discord.Embed(title=f"⚔️ {personaje} - Seleccionar Ataque", 
                                description="Elige el tipo de ataque:", color=0xff6600)
            embed.add_field(name="🎯 Opciones", 
                          value="⚔️ **Físico** - Usa Fuerza\n🔮 **Mágico** - Usa Maná\n🏹 **Distancia** - Usa Destreza", 
                          inline=False)
            if bonificador != 0:
                embed.add_field(name="➕ Bonificador", value=str(bonificador), inline=True)
            
            view = AttackView(personaje, bonificador)
            await interaction.followup.send(embed=embed, view=view)
            
        elif accion.lower() == "defensa":
            embed = discord.Embed(title=f"🛡️ {personaje} - Seleccionar Defensa", 
                                description="Elige el tipo de defensa:", color=0x0099ff)
            embed.add_field(name="🛡️ Opciones", 
                          value="🏃 **Esquive** - Evita con agilidad\n🛡️ **Física** - Bloquea daño\n✨ **Mágica** - Resiste magia", 
                          inline=False)
            if bonificador != 0:
                embed.add_field(name="➕ Bonificador", value=str(bonificador), inline=True)
            
            view = DefenseView(personaje, bonificador)
            await interaction.followup.send(embed=embed, view=view)
            
        else:
            await interaction.followup.send("❌ Acción inválida. Usa: `ataque` o `defensa`")
            
    except Exception as e:
        logger.error(f"❌ Error en tirada: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="vida_npc", description="Modifica la vida de un NPC")
async def npc_health(interaction: discord.Interaction, npc: str, nueva_vida: int):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener datos actuales
            cursor.execute("SELECT puntos_vida_actual, puntos_vida_max FROM npcs WHERE nombre = ?", (npc,))
            result = cursor.fetchone()
            
            if not result:
                await interaction.followup.send(f"❌ NPC **{npc}** no encontrado")
                return
            
            vida_anterior, vida_max = result
            
            # Validar nueva vida
            nueva_vida = max(0, min(nueva_vida, vida_max))
            
            # Actualizar
            cursor.execute("UPDATE npcs SET puntos_vida_actual = ? WHERE nombre = ?", (nueva_vida, npc))
            conn.commit()
        
        embed = discord.Embed(title=f"❤️ Vida de {npc} Actualizada", 
                            color=0x00ff00 if nueva_vida > vida_anterior else 0xff0000)
        embed.add_field(name="❤️ Vida Anterior", value=f"{vida_anterior}/{vida_max} PV", inline=True)
        embed.add_field(name="❤️ Vida Nueva", value=f"{nueva_vida}/{vida_max} PV", inline=True)
        
        cambio = nueva_vida - vida_anterior
        if cambio > 0:
            embed.add_field(name="💚 Curado", value=f"+{cambio} PV", inline=True)
        elif cambio < 0:
            embed.add_field(name="💔 Daño", value=f"{cambio} PV", inline=True)
        
        if nueva_vida == 0:
            embed.add_field(name="💀 Estado", value="**DERROTADO**", inline=False)
            embed.color = 0x8b0000
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error actualizando vida NPC: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="info_personaje", description="Info completa de un personaje")
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
        
        # Obtener estadísticas con bonuses
        base_stats = excel_manager.read_character_stats(personaje)
        item_bonuses = inventory_system.calculate_equipped_bonuses(personaje)
        
        if not base_stats:
            await interaction.followup.send(f"❌ No se pudieron cargar las estadísticas de **{personaje}**")
            return
        
        # Combinar stats
        combined_stats = {}
        for attr in base_stats:
            combined_stats[attr] = {
                'base': base_stats[attr]['base'],
                'bonus': item_bonuses.get(attr, 0),
                'total': base_stats[attr]['base'] + item_bonuses.get(attr, 0)
            }
        
        embed = discord.Embed(title=f"🎭 {personaje}", description=char_data[4] or "Un aventurero misterioso", color=0x9932cc)
        
        # Vida y oro
        embed.add_field(name="❤️ Vida", value=f"{char_data[5]}/{char_data[6]} PV", inline=True)
        embed.add_field(name="💰 Oro", value=str(char_data[7]), inline=True)
        embed.add_field(name="📝 Estado", value=char_data[8].title(), inline=True)
        
        # Estadísticas principales
        main_attrs = ['fuerza', 'destreza', 'velocidad', 'inteligencia', 'mana']
        stats_text = ""
        for attr in main_attrs:
            if attr in combined_stats:
                s = combined_stats[attr]
                emoji = {'fuerza': '💪', 'destreza': '🎯', 'velocidad': '⚡', 'inteligencia': '🧠', 'mana': '🔮'}[attr]
                bonus_text = f" (+{s['bonus']})" if s['bonus'] > 0 else f" ({s['bonus']})" if s['bonus'] < 0 else ""
                stats_text += f"{emoji} **{attr.title()}:** {s['total']} ({s['base']}{bonus_text})\n"
        
        embed.add_field(name="📊 Atributos", value=stats_text, inline=True)
        
        # Defensas
        defense_attrs = ['defensaesquive', 'defensafisica', 'defensamagica']
        defense_names = ['🏃 Esquive', '🛡️ Física', '✨ Mágica']
        def_text = ""
        
        for attr, name in zip(defense_attrs, defense_names):
            if attr in combined_stats:
                s = combined_stats[attr]
                bonus_text = f" (+{s['bonus']})" if s['bonus'] > 0 else f" ({s['bonus']})" if s['bonus'] < 0 else ""
                def_text += f"{name}: {s['total']} ({s['base']}{bonus_text})\n"
        
        embed.add_field(name="🛡️ Defensas", value=def_text, inline=True)
        
        # Sincronizar con Google Sheets
        google_sheets.sync_character(personaje, combined_stats)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error mostrando info: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="eliminar_personaje", description="Elimina un personaje")
async def delete_character(interaction: discord.Interaction, personaje: str, confirmacion: str):
    await interaction.response.defer()
    
    try:
        if confirmacion.lower() != "confirmar":
            await interaction.followup.send("⚠️ Para eliminar escribe `confirmar` en el campo confirmación")
            return
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, usuario_id, excel_path FROM personajes WHERE nombre = ?", (personaje,))
            char_data = cursor.fetchone()
            
            if not char_data:
                await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                return
            
            char_id, usuario_id, excel_path = char_data
            
            if usuario_id != str(interaction.user.id):
                await interaction.followup.send("❌ Solo puedes eliminar tus propios personajes")
                return
            
            # Eliminar datos relacionados
            cursor.execute("DELETE FROM inventarios WHERE personaje_id = ?", (char_id,))
            cursor.execute("DELETE FROM personajes WHERE id = ?", (char_id,))
            conn.commit()
            
            # Mover Excel a archivados
            if os.path.exists(excel_path):
                archive_path = excel_path.replace("/activos/", "/archivados/")
                os.rename(excel_path, archive_path)
        
        embed = discord.Embed(title="🗑️ Personaje Eliminado", 
                            description=f"**{personaje}** eliminado del universo Unity", 
                            color=0x8b0000)
        embed.set_footer(text="Esta acción no se puede deshacer")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error eliminando personaje: {e}")
        await interaction.followup.send("❌ Error interno")

# ============= INICIALIZACIÓN =============
def create_default_content():
    """Crea contenido por defecto"""
    default_items = [
        ("Espada de Acero", "arma", "Espada básica de acero", 3, 0, 0, 0, 0, 0, 1, 0, "raro", 50),
        ("Armadura de Cuero", "armadura", "Armadura ligera de cuero", 0, 1, 0, 0, 0, 1, 3, 0, "comun", 30),
        ("Amuleto Mágico", "accesorio", "Aumenta poder mágico", 0, 0, 0, 2, 3, 0, 0, 2, "epico", 200)
    ]
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for item_data in default_items:
                cursor.execute("""INSERT OR IGNORE INTO items (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza,
                                efecto_velocidad, efecto_inteligencia, efecto_mana, efecto_def_esquive,
                                efecto_def_fisica, efecto_def_magica, rareza, precio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", item_data)
            conn.commit()
        logger.info("✅ Contenido por defecto creado")
    except Exception as e:
        logger.error(f"❌ Error creando contenido por defecto: {e}")

async def main():
    try:
        create_default_content()
        logger.info("🚀 Iniciando Unity RPG Bot Optimizado...")
        await client.start(config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
    finally:
        logger.info("👋 Unity RPG Bot cerrado")