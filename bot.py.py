"""
🎲 Unity RPG Bot - Versión Mejorada y Optimizada
Sistema RPG basado en estadísticas puras sin niveles
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
import aiohttp
import hashlib

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
        
        # Subdirectorios para imágenes
        self.CHAR_IMAGES = f"{self.IMAGES_DIR}/personajes"
        self.NPC_IMAGES = f"{self.IMAGES_DIR}/npcs"
        self.ITEM_IMAGES = f"{self.IMAGES_DIR}/items"
        
        # Atributos base para personajes
        self.BASE_ATTRIBUTES = ['Fuerza', 'Destreza', 'Velocidad', 'Resistencia', 'Inteligencia', 'Mana']
        
        # Tipos de dados disponibles
        self.DICE_TYPES = [3, 6, 8, 10, 12, 20]
        self.MAX_DICE_COUNT = 5
        
        # Puntos de golpe fijos para todos
        self.FIXED_HP = 10
        
        self.create_directories()
        
    def create_directories(self):
        dirs = [self.DATA_DIR, self.EXCEL_DIR, self.IMAGES_DIR, self.LOGS_DIR,
                f"{self.EXCEL_DIR}/activos", f"{self.EXCEL_DIR}/archivados",
                self.CHAR_IMAGES, self.NPC_IMAGES, self.ITEM_IMAGES]
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
            
            # Verificar si necesitamos actualizar tablas NPCs
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='npcs'")
            npc_table_exists = cursor.fetchone()
            
            if npc_table_exists:
                cursor.execute("PRAGMA table_info(npcs)")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Verificar si tiene las columnas viejas y necesita actualización
                if 'fuerza' in columns or 'puntos_vida_actual' in columns:
                    cursor.execute("DROP TABLE IF EXISTS npcs")
                    logger.info("🔄 Recreando tabla NPCs con nueva estructura")
            
            # Personajes (sin vida)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    usuario_id TEXT NOT NULL,
                    excel_path TEXT NOT NULL,
                    descripcion TEXT,
                    oro INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'activo',
                    imagen_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # NPCs - Nueva estructura
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npcs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    tipo TEXT DEFAULT 'general',
                    ataq_fisic INTEGER DEFAULT 10,
                    ataq_dist INTEGER DEFAULT 10,
                    ataq_magic INTEGER DEFAULT 10,
                    res_fisica INTEGER DEFAULT 10,
                    res_magica INTEGER DEFAULT 10,
                    velocidad INTEGER DEFAULT 10,
                    mana INTEGER DEFAULT 10,
                    descripcion TEXT,
                    imagen_url TEXT,
                    sincronizado BOOLEAN DEFAULT FALSE,
                    cantidad INTEGER DEFAULT 1,
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
                    efecto_resistencia INTEGER DEFAULT 0,
                    efecto_inteligencia INTEGER DEFAULT 0,
                    efecto_mana INTEGER DEFAULT 0,
                    precio INTEGER DEFAULT 0,
                    es_equipable BOOLEAN DEFAULT TRUE,
                    slot_equipo TEXT DEFAULT 'general',
                    imagen_url TEXT,
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
            logger.info("✅ Base de datos inicializada correctamente")

db = DatabaseManager()

# ============= IMAGE HANDLER =============
class ImageHandler:
    @staticmethod
    async def save_image(attachment, entity_type, entity_name):
        """Guarda una imagen adjunta y retorna la URL"""
        if not attachment:
            return None
            
        try:
            dirs = {
                'personaje': config.CHAR_IMAGES,
                'npc': config.NPC_IMAGES,
                'item': config.ITEM_IMAGES
            }
            save_dir = dirs.get(entity_type, config.IMAGES_DIR)
            
            file_ext = attachment.filename.split('.')[-1]
            file_hash = hashlib.md5(f"{entity_name}_{datetime.now()}".encode()).hexdigest()[:8]
            filename = f"{entity_name}_{file_hash}.{file_ext}"
            filepath = os.path.join(save_dir, filename)
            
            await attachment.save(filepath)
            logger.info(f"✅ Imagen guardada: {filename}")
            return attachment.url
            
        except Exception as e:
            logger.error(f"❌ Error guardando imagen: {e}")
            return None

image_handler = ImageHandler()

# ============= GOOGLE SHEETS (OPCIONAL) =============
class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.init_google_sheets()
    
    def init_google_sheets(self):
        try:
            if not os.path.exists(config.GOOGLE_CREDENTIALS_FILE):
                logger.info("ℹ️ Google Sheets no configurado - Usando solo almacenamiento local")
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
            logger.warning(f"⚠️ Google Sheets no disponible: {e}")
    
    def sync_character(self, character_name, stats):
        if not self.client or not self.spreadsheet:
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
            logger.info(f"✅ {character_name} sincronizado en Google Sheets")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo sincronizar con Google Sheets: {e}")

google_sheets = GoogleSheetsManager()

# ============= EXCEL MANAGER =============
class ExcelManager:
    @staticmethod
    def create_character_excel(character_name, user_id, initial_stats=None):
        if initial_stats is None:
            initial_stats = {}
            
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        
        character_data = {
            'Atributo': config.BASE_ATTRIBUTES,
            'Valor': [
                initial_stats.get('fuerza', 10), initial_stats.get('destreza', 10),
                initial_stats.get('velocidad', 10), initial_stats.get('resistencia', 10),
                initial_stats.get('inteligencia', 10), initial_stats.get('mana', 10)
            ]
        }
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_stats = pd.DataFrame(character_data)
            df_stats.to_excel(writer, sheet_name='Estadisticas', index=False)
            
            info_data = {
                'Campo': ['Nombre', 'Usuario_ID', 'Oro'],
                'Valor': [character_name, str(user_id), 0]
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
                attr_name = row['Atributo'].lower()
                stats[attr_name] = {'base': int(row['Valor']), 'bonus': 0, 'total': int(row['Valor'])}
            return stats
        except Exception as e:
            logger.error(f"❌ Error leyendo stats: {e}")
            return None
    
    @staticmethod
    def update_character_stats(character_name, new_stats):
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        if not os.path.exists(file_path):
            return False
            
        try:
            with pd.ExcelFile(file_path) as xls:
                df_stats = pd.read_excel(xls, sheet_name='Estadisticas')
                df_info = pd.read_excel(xls, sheet_name='Info')
            
            for idx, row in df_stats.iterrows():
                attr_name = row['Atributo'].lower()
                if attr_name in new_stats:
                    df_stats.at[idx, 'Valor'] = new_stats[attr_name]
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_stats.to_excel(writer, sheet_name='Estadisticas', index=False)
                df_info.to_excel(writer, sheet_name='Info', index=False)
            
            return True
        except Exception as e:
            logger.error(f"❌ Error actualizando stats: {e}")
            return False

excel_manager = ExcelManager()

# ============= INVENTORY SYSTEM =============
class InventorySystem:
    @staticmethod
    def calculate_equipped_bonuses(character_name):
        bonuses = {attr: 0 for attr in ['fuerza', 'destreza', 'velocidad', 'resistencia', 'inteligencia', 'mana']}
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.efecto_fuerza, i.efecto_destreza, i.efecto_velocidad,
                           i.efecto_resistencia, i.efecto_inteligencia, i.efecto_mana
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ? AND inv.equipado = TRUE
                """, (character_name,))
                
                for row in cursor.fetchall():
                    attrs = ['fuerza', 'destreza', 'velocidad', 'resistencia', 'inteligencia', 'mana']
                    for i, attr in enumerate(attrs):
                        bonuses[attr] += row[i] or 0
        except Exception as e:
            logger.error(f"❌ Error calculando bonuses: {e}")
        return bonuses

inventory_system = InventorySystem()

# ============= DICE SYSTEM MEJORADO =============
class DiceSystem:
    @staticmethod
    def roll_multiple_dice(dice_count, dice_type):
        """Tira múltiples dados del mismo tipo"""
        rolls = [random.randint(1, dice_type) for _ in range(dice_count)]
        return {'rolls': rolls, 'total': sum(rolls)}
    
    @staticmethod
    def roll_action(character_name, action_type, dice_count=1, dice_type=20, bonificador=0):
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
        
        # Tirar dados múltiples
        dice_result = DiceSystem.roll_multiple_dice(dice_count, dice_type)
        dice_total = dice_result['total']
        
        # Mapeo de acciones a atributos
        action_mapping = {
            'ataque_fisico': 'fuerza',
            'ataque_magico': 'mana', 
            'ataque_distancia': 'destreza',
            'defensa_fisica': 'resistencia',
            'defensa_magica': 'destreza',
            'defensa_esquive': 'velocidad'
        }
        
        if action_type not in action_mapping:
            return None
            
        attr_key = action_mapping[action_type]
        attr_value = combined_stats[attr_key]['total']
        total = dice_total + attr_value + bonificador
        
        # Verificar críticos y pifias
        is_critical = any(roll == dice_type for roll in dice_result['rolls'])
        is_fumble = any(roll == 1 for roll in dice_result['rolls'])
        
        logger.info(f"[DADOS] {character_name} - {action_type}: {dice_count}d{dice_type}({dice_result['rolls']}) + {attr_key.title()}({attr_value}) + Bonus({bonificador}) = {total}")
        
        return {
            'dice_rolls': dice_result['rolls'], 
            'dice_total': dice_total,
            'dice_count': dice_count,
            'dice_type': dice_type,
            'attribute': attr_value, 
            'attribute_name': attr_key.title(),
            'bonuses': bonificador, 
            'total': total, 
            'action_type': action_type,
            'is_critical': is_critical, 
            'is_fumble': is_fumble
        }
    
    @staticmethod
    def npc_action(npc_name, action_type):
        """Acción de NPC (ataque o defensa) con stats fijas"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT ataq_fisic, ataq_dist, ataq_magic, res_fisica, res_magica, velocidad,
                                sincronizado, cantidad, imagen_url FROM npcs WHERE nombre = ?""", (npc_name,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                ataq_fisic, ataq_dist, ataq_magic, res_fisica, res_magica, velocidad, sincronizado, cantidad, imagen_url = result
                
                # Mapeo de acciones para NPCs
                action_mapping = {
                    'fisico': ataq_fisic,
                    'distancia': ataq_dist, 
                    'magico': ataq_magic,
                    'defensa_fisica': res_fisica,
                    'defensa_magica': res_magica,
                    'esquivar': velocidad
                }
                
                if action_type not in action_mapping:
                    return None
                
                base_value = action_mapping[action_type]
                
                # Si está sincronizado, multiplica por cantidad
                if sincronizado:
                    total_value = base_value * cantidad
                    action_description = f"{cantidad} {npc_name}s sincronizados"
                else:
                    total_value = base_value
                    action_description = f"{npc_name}"
                
                # Determinar si es ataque o defensa
                is_attack = action_type in ['fisico', 'distancia', 'magico']
                action_category = "ataque" if is_attack else "defensa"
                
                logger.info(f"[NPC {action_category.upper()}] {action_description} - {action_type}: {total_value}")
                
                return {
                    'npc_name': npc_name,
                    'action_type': action_type,
                    'action_category': action_category,
                    'base_value': base_value,
                    'total_value': total_value,
                    'sincronizado': sincronizado,
                    'cantidad': cantidad,
                    'action_description': action_description,
                    'imagen_url': imagen_url
                }
        except Exception as e:
            logger.error(f"❌ Error en acción NPC: {e}")
            return None

dice_system = DiceSystem()

# ============= INTERACTIVE MENUS =============

class NPCActionSelect(discord.ui.Select):
    def __init__(self, npc_name):
        self.npc_name = npc_name
        
        options = [
            # Ataques
            discord.SelectOption(label="Ataque Físico", description="Daño fijo basado en ATAQ_FISIC", emoji="⚔️", value="fisico"),
            discord.SelectOption(label="Ataque Mágico", description="Daño fijo basado en ATAQ_MAGIC", emoji="🔮", value="magico"),
            discord.SelectOption(label="Ataque a Distancia", description="Daño fijo basado en ATAQ_DIST", emoji="🏹", value="distancia"),
            # Defensas
            discord.SelectOption(label="Defensa Física", description="Defensa basada en RES_FISICA", emoji="🛡️", value="defensa_fisica"),
            discord.SelectOption(label="Defensa Mágica", description="Defensa basada en RES_MAGICA", emoji="✨", value="defensa_magica"),
            discord.SelectOption(label="Esquivar", description="Esquive basado en VELOCIDAD", emoji="🏃", value="esquivar")
        ]
        
        super().__init__(placeholder="🎯 Selecciona la acción del NPC...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        result = dice_system.npc_action(self.npc_name, self.values[0])
        
        if not result:
            await interaction.response.send_message(f"❌ NPC **{self.npc_name}** no encontrado", ephemeral=True)
            return
        
        # Colores según acción
        if result['action_category'] == 'ataque':
            color = 0xff4444
            if result['total_value'] >= 50:
                embed_desc = "💀 **¡ATAQUE DEVASTADOR!**"
                color = 0x8b0000
            elif result['total_value'] >= 30:
                embed_desc = "⚔️ **¡ATAQUE PODEROSO!**"
            elif result['total_value'] >= 15:
                embed_desc = "✅ **Ataque Efectivo**"
            else:
                embed_desc = "👊 **Ataque Básico**"
        else:  # defensa
            color = 0x4444ff
            if result['total_value'] >= 50:
                embed_desc = "🛡️ **¡DEFENSA IMPENETRABLE!**"
                color = 0x000080
            elif result['total_value'] >= 30:
                embed_desc = "🛡️ **¡DEFENSA SÓLIDA!**"
            elif result['total_value'] >= 15:
                embed_desc = "✅ **Defensa Efectiva**"
            else:
                embed_desc = "🛡️ **Defensa Básica**"
        
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
        
        embed = discord.Embed(title=f"👹 {result['action_description']} - {action_name}", color=color)
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
        for item in items[:25]:
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
        item_name = self.values[0]
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""SELECT inv.id, inv.equipado FROM inventarios inv
                                JOIN personajes p ON inv.personaje_id = p.id
                                JOIN items i ON inv.item_id = i.id
                                WHERE p.nombre = ? AND i.nombre = ?""", (self.character_name, item_name))
                result = cursor.fetchone()
                
                if not result:
                    await interaction.response.send_message(f"❌ **{self.character_name}** no tiene el item **{item_name}**", ephemeral=True)
                    return
                
                inv_id, equipado = result
                
                if equipado:
                    cursor.execute("UPDATE inventarios SET equipado = FALSE WHERE id = ?", (inv_id,))
                    status = "desequipado"
                    color = 0xff6600
                    emoji = "📤"
                else:
                    cursor.execute("UPDATE inventarios SET equipado = TRUE WHERE id = ?", (inv_id,))
                    status = "equipado"
                    color = 0x00ff00
                    emoji = "⚔️"
                
                conn.commit()
            
            embed = discord.Embed(title=f"{emoji} Item {status.title()}", 
                                description=f"**{item_name}** {status} por **{self.character_name}**", 
                                color=color)
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            logger.error(f"❌ Error equipando item: {e}")
            await interaction.response.send_message("❌ Error interno", ephemeral=True)

# Views
class NPCActionView(discord.ui.View):
    def __init__(self, npc_name):
        super().__init__(timeout=60)
        self.add_item(NPCActionSelect(npc_name))

class EquipItemView(discord.ui.View):
    def __init__(self, character_name, items):
        super().__init__(timeout=60)
        self.add_item(EquipItemSelect(character_name, items))

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

# ============= COMANDOS PRINCIPALES =============

@tree.command(name="crear_personaje", description="Crea un personaje con 10 PG fijos")
async def create_character(interaction: discord.Interaction, nombre: str, fuerza: int = 10, destreza: int = 10, 
                         velocidad: int = 10, resistencia: int = 10, inteligencia: int = 10, mana: int = 10,
                         descripcion: str = "Un aventurero misterioso", imagen: discord.Attachment = None):
    await interaction.response.defer()
    
    try:
        imagen_url = None
        if imagen:
            imagen_url = await image_handler.save_image(imagen, 'personaje', nombre)
        
        initial_stats = {'fuerza': fuerza, 'destreza': destreza, 'velocidad': velocidad, 
                        'resistencia': resistencia, 'inteligencia': inteligencia, 'mana': mana}
        
        excel_path = excel_manager.create_character_excel(nombre, interaction.user.id, initial_stats)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO personajes (nombre, usuario_id, excel_path, descripcion, imagen_url) 
                         VALUES (?, ?, ?, ?, ?)""",
                         (nombre, str(interaction.user.id), excel_path, descripcion, imagen_url))
            conn.commit()
        
        embed = discord.Embed(title="🎭 ¡Personaje Creado!", description=f"**{nombre}** ha despertado en Unity", color=0x00ff00)
        embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
        embed.add_field(name="❤️ Puntos de Golpe", value=f"{config.FIXED_HP} PG (fijos para todos)", inline=True)
        
        stats_text = f"💪 **Fuerza:** {fuerza}\n🎯 **Destreza:** {destreza}\n⚡ **Velocidad:** {velocidad}\n🛡️ **Resistencia:** {resistencia}\n🧠 **Inteligencia:** {inteligencia}\n🔮 **Maná:** {mana}"
        embed.add_field(name="📊 Atributos", value=stats_text, inline=True)
        
        embed.add_field(name="🎲 Sistema de Combate", 
                       value="**Ataques:**\n⚔️ Físico (Fuerza)\n🏹 Distancia (Destreza)\n🔮 Mágico (Maná)\n\n**Defensas:**\n🏃 Esquive (Velocidad)\n🛡️ Física (Resistencia)\n✨ Mágica (Destreza)", 
                       inline=True)
        
        if imagen_url:
            embed.set_thumbnail(url=imagen_url)
        
        await interaction.followup.send(embed=embed)
        
    except sqlite3.IntegrityError:
        await interaction.followup.send(f"❌ El personaje **{nombre}** ya existe")
    except Exception as e:
        logger.error(f"❌ Error creando personaje: {e}")
        await interaction.followup.send(f"❌ Error interno al crear **{nombre}**")

@tree.command(name="crear_npc", description="Crea un NPC con las nuevas estadísticas")
async def create_npc(interaction: discord.Interaction, nombre: str, tipo: str = "general",
                    ataq_fisic: int = 10, ataq_dist: int = 10, ataq_magic: int = 10,
                    res_fisica: int = 10, res_magica: int = 10, velocidad: int = 10, mana: int = 10,
                    descripcion: str = "Un ser del universo Unity",
                    sincronizado: bool = False, cantidad: int = 1, imagen: discord.Attachment = None):
    await interaction.response.defer()
    
    try:
        imagen_url = None
        if imagen:
            imagen_url = await image_handler.save_image(imagen, 'npc', nombre)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO npcs (nombre, tipo, ataq_fisic, ataq_dist, ataq_magic,
                            res_fisica, res_magica, velocidad, mana, descripcion, 
                            sincronizado, cantidad, imagen_url) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (nombre, tipo, ataq_fisic, ataq_dist, ataq_magic, res_fisica, res_magica,
                          velocidad, mana, descripcion, sincronizado, cantidad, imagen_url))
            conn.commit()
        
        embed = discord.Embed(title="👹 ¡NPC Creado!", description=f"**{nombre}** añadido al universo", color=0xff4444)
        embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
        embed.add_field(name="❤️ Puntos de Golpe", value=f"{config.FIXED_HP} PG", inline=True)
        
        if sincronizado:
            embed.add_field(name="🤝 Sincronizado", value=f"Sí ({cantidad} unidades)", inline=True)
        else:
            embed.add_field(name="👤 Individual", value="Sí", inline=True)
        
        embed.add_field(name="📝 Descripción", value=descripcion[:200], inline=False)
        
        stats_text = f"⚔️ ATAQ_FISIC: {ataq_fisic}\n🏹 ATAQ_DIST: {ataq_dist}\n🔮 ATAQ_MAGIC: {ataq_magic}\n🛡️ RES_FISICA: {res_fisica}\n✨ RES_MAGICA: {res_magica}\n⚡ Velocidad: {velocidad}\n🧙 Maná: {mana}"
        embed.add_field(name="📊 Estadísticas", value=stats_text, inline=True)
        
        damage_text = f"⚔️ Físico: {ataq_fisic}\n🏹 Distancia: {ataq_dist}\n🔮 Mágico: {ataq_magic}"
        defense_text = f"🛡️ Defensa Física: {res_fisica}\n✨ Defensa Mágica: {res_magica}\n🏃 Esquivar: {velocidad}"
        
        if sincronizado:
            damage_text += f"\n\n🤝 **Sincronizado:**\n⚔️ Físico: {ataq_fisic * cantidad}\n🏹 Distancia: {ataq_dist * cantidad}\n🔮 Mágico: {ataq_magic * cantidad}"
            defense_text += f"\n\n🤝 **Sincronizado:**\n🛡️ Def. Física: {res_fisica * cantidad}\n✨ Def. Mágica: {res_magica * cantidad}\n🏃 Esquivar: {velocidad * cantidad}"
        
        embed.add_field(name="💥 Ataques", value=damage_text, inline=True)
        embed.add_field(name="🛡️ Defensas", value=defense_text, inline=True)
        
        if imagen_url:
            embed.set_thumbnail(url=imagen_url)
        
        await interaction.followup.send(embed=embed)
        
    except sqlite3.IntegrityError:
        await interaction.followup.send(f"❌ El NPC **{nombre}** ya existe")
    except Exception as e:
        logger.error(f"❌ Error creando NPC: {e}")
        await interaction.followup.send(f"❌ Error interno al crear NPC **{nombre}**")

@tree.command(name="crear_item", description="Crea un item equipable con efectos")
async def create_item(interaction: discord.Interaction, nombre: str, tipo: str, descripcion: str = "",
                     efecto_fuerza: int = 0, efecto_destreza: int = 0, efecto_velocidad: int = 0,
                     efecto_resistencia: int = 0, efecto_inteligencia: int = 0, efecto_mana: int = 0,
                     rareza: str = "comun", precio: int = 0, imagen: discord.Attachment = None):
    await interaction.response.defer()
    
    try:
        imagen_url = None
        if imagen:
            imagen_url = await image_handler.save_image(imagen, 'item', nombre)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO items (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza,
                            efecto_velocidad, efecto_resistencia, efecto_inteligencia, efecto_mana,
                            rareza, precio, imagen_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza, efecto_velocidad,
                          efecto_resistencia, efecto_inteligencia, efecto_mana, rareza, precio, imagen_url))
            conn.commit()
        
        embed = discord.Embed(title="✨ ¡Item Creado!", description=f"**{nombre}** ha sido forjado", color=0x9932cc)
        embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
        embed.add_field(name="⭐ Rareza", value=rareza.title(), inline=True)
        embed.add_field(name="💰 Precio", value=f"{precio} oro", inline=True)
        
        if descripcion:
            embed.add_field(name="📝 Descripción", value=descripcion[:200], inline=False)
        
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
        
        if imagen_url:
            embed.set_thumbnail(url=imagen_url)
        
        await interaction.followup.send(embed=embed)
        
    except sqlite3.IntegrityError:
        await interaction.followup.send(f"❌ El item **{nombre}** ya existe")
    except Exception as e:
        logger.error(f"❌ Error creando item: {e}")
        await interaction.followup.send(f"❌ Error interno al crear item **{nombre}**")

# ============= COMANDOS DE BORRADO (NUEVOS) =============

@tree.command(name="borrar_personaje", description="Borra tu personaje (solo el creador puede borrarlo)")
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
            
            # Mover archivo Excel a carpeta de archivados
            try:
                import shutil
                if os.path.exists(excel_path):
                    archived_path = excel_path.replace('/activos/', '/archivados/')
                    shutil.move(excel_path, archived_path)
                    logger.info(f"📁 Excel movido a archivados: {archived_path}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo mover Excel: {e}")
        
        embed = discord.Embed(
            title="🗑️ Personaje Borrado", 
            description=f"**{personaje}** ha sido eliminado del universo Unity", 
            color=0xff6600
        )
        embed.add_field(name="🧹 Limpieza", value="• Inventario eliminado\n• Archivo movido a archivados", inline=False)
        embed.set_footer(text="Esta acción no se puede deshacer")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error borrando personaje: {e}")
        await interaction.followup.send("❌ Error interno al borrar personaje")

@tree.command(name="borrar_npc", description="Borra un NPC del universo")
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
        
        embed = discord.Embed(
            title="🗑️ NPC Borrado", 
            description=f"**{npc}** ha sido eliminado del universo Unity", 
            color=0xff6600
        )
        embed.set_footer(text="Esta acción no se puede deshacer")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error borrando NPC: {e}")
        await interaction.followup.send("❌ Error interno al borrar NPC")

# ============= COMANDOS DE TIRADAS SIMPLIFICADOS =============

@tree.command(name="tirar", description="Tirada directa con parámetros")
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
async def roll_dice(interaction: discord.Interaction, personaje: str, tipo_dado: int, cantidad: int, accion: str, bonificador: int = 0):
    await interaction.response.defer()
    
    try:
        # Validaciones
        if tipo_dado not in config.DICE_TYPES:
            await interaction.followup.send("❌ Tipo de dado inválido. Usa: 3, 6, 8, 10, 12, 20")
            return
        
        if cantidad < 1 or cantidad > config.MAX_DICE_COUNT:
            await interaction.followup.send(f"❌ Cantidad de dados debe ser entre 1 y {config.MAX_DICE_COUNT}")
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
        
        # Determinar color y descripción
        if 'ataque' in result['action_type']:
            color = 0x00ff00 if result['total'] >= 18 else 0xff6600 if result['total'] >= 12 else 0xff0000
            action_emoji = "⚔️" if 'fisico' in result['action_type'] else "🔮" if 'magico' in result['action_type'] else "🏹"
        else:
            color = 0x0099ff if result['total'] >= 15 else 0xff6600 if result['total'] >= 12 else 0xff0000
            action_emoji = "🛡️" if 'fisica' in result['action_type'] else "✨" if 'magica' in result['action_type'] else "🏃"
        
        action_name = result['action_type'].replace('_', ' ').title()
        embed = discord.Embed(title=f"{action_emoji} {action_name} - {personaje}", color=color)
        
        if result['is_critical']:
            embed.description = "🎯 **¡CRÍTICO DEVASTADOR!**"
            embed.color = 0xffd700
        elif result['is_fumble']:
            embed.description = "💥 **¡PIFIA ÉPICA!**"
            embed.color = 0x8b0000
        elif result['total'] >= 25:
            embed.description = "🌟 **¡RESULTADO LEGENDARIO!**"
        elif result['total'] >= 15:
            embed.description = "✅ **Resultado Exitoso**"
        else:
            embed.description = "❌ **Resultado Fallido**"
        
        # Mostrar dados de forma clara
        dice_display = ' + '.join(map(str, result['dice_rolls']))
        embed.add_field(name=f"🎲 {result['dice_count']}d{result['dice_type']}", value=f"`{dice_display}` = `{result['dice_total']}`", inline=True)
        embed.add_field(name=f"📊 {result['attribute_name']}", value=f"`{result['attribute']}`", inline=True)
        if bonificador != 0:
            embed.add_field(name="➕ Bonus", value=f"`{bonificador}`", inline=True)
        embed.add_field(name="🏆 **TOTAL**", value=f"**`{result['total']}`**", inline=False)
        
        if imagen_url:
            embed.set_thumbnail(url=imagen_url)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error en tirada: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="tirada_npc", description="Ejecuta ataques y defensas de NPCs con stats fijas")
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
        
        embed = discord.Embed(title=f"👹 {npc} - Seleccionar Acción", 
                            description="Elige el tipo de acción del NPC:", color=0xff4444)
        
        if sincronizado:
            embed.add_field(name="🤝 NPCs Sincronizados", value=f"{cantidad} unidades", inline=True)
            embed.add_field(name="💥 Valores", value="Base × Cantidad", inline=True)
        else:
            embed.add_field(name="👤 NPC Individual", value="Valores fijos", inline=True)
        
        embed.add_field(name="🎯 Acciones Disponibles", 
                       value="**Ataques:** ⚔️ Físico, 🔮 Mágico, 🏹 Distancia\n**Defensas:** 🛡️ Física, ✨ Mágica, 🏃 Esquivar", 
                       inline=False)
        
        view = NPCActionView(npc)
        await interaction.response.send_message(embed=embed, view=view)
        
    except Exception as e:
        logger.error(f"❌ Error en tirada NPC: {e}")
        await interaction.response.send_message("❌ Error interno", ephemeral=True)

# ============= COMANDOS DE EDICIÓN =============

@tree.command(name="editar_personaje", description="Edita las estadísticas e imagen de tu personaje")
async def edit_character(interaction: discord.Interaction, personaje: str, 
                        fuerza: int = None, destreza: int = None, velocidad: int = None,
                        resistencia: int = None, inteligencia: int = None, mana: int = None,
                        oro: int = None, imagen: discord.Attachment = None):
    await interaction.response.defer()
    
    try:
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
        
        new_stats = {}
        if fuerza is not None: new_stats['fuerza'] = fuerza
        if destreza is not None: new_stats['destreza'] = destreza
        if velocidad is not None: new_stats['velocidad'] = velocidad
        if resistencia is not None: new_stats['resistencia'] = resistencia
        if inteligencia is not None: new_stats['inteligencia'] = inteligencia
        if mana is not None: new_stats['mana'] = mana
        
        if new_stats:
            excel_manager.update_character_stats(personaje, new_stats)
        
        if oro is not None:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE personajes SET oro = ? WHERE nombre = ?", (oro, personaje))
                conn.commit()
        
        embed = discord.Embed(title="✏️ Personaje Editado", 
                            description=f"**{personaje}** actualizado exitosamente", 
                            color=0x00ff00)
        
        if new_stats:
            stats_text = '\n'.join([f"• **{k.title()}:** {v}" for k, v in new_stats.items()])
            embed.add_field(name="📊 Estadísticas Actualizadas", value=stats_text[:1024], inline=False)
        
        if imagen:
            embed.add_field(name="🖼️ Imagen", value="Actualizada", inline=True)
            if imagen_url:
                embed.set_thumbnail(url=imagen_url)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error editando personaje: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="editar_npc", description="Edita las estadísticas de un NPC")
async def edit_npc(interaction: discord.Interaction, npc: str,
                  ataq_fisic: int = None, ataq_dist: int = None, ataq_magic: int = None,
                  res_fisica: int = None, res_magica: int = None, velocidad: int = None, mana: int = None,
                  sincronizado: bool = None, cantidad: int = None):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM npcs WHERE nombre = ?", (npc,))
            if not cursor.fetchone():
                await interaction.followup.send(f"❌ NPC **{npc}** no encontrado")
                return
            
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
        
        embed = discord.Embed(title="✏️ NPC Editado", 
                            description=f"**{npc}** actualizado exitosamente", 
                            color=0xff4444)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error editando NPC: {e}")
        await interaction.followup.send("❌ Error interno")

# ============= COMANDOS DE INVENTARIO =============

@tree.command(name="equipar_menu", description="Menú interactivo para equipar/desequipar items")
async def equip_menu(interaction: discord.Interaction, personaje: str):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.nombre, inv.equipado, i.rareza
                FROM inventarios inv
                JOIN items i ON inv.item_id = i.id
                JOIN personajes p ON inv.personaje_id = p.id
                WHERE p.nombre = ? AND i.es_equipable = TRUE
                ORDER BY inv.equipado DESC, i.nombre
            """, (personaje,))
            items = cursor.fetchall()
        
        if not items:
            await interaction.followup.send(f"❌ **{personaje}** no tiene items equipables")
            return
        
        embed = discord.Embed(title=f"🎒 Equipar Items - {personaje}", 
                            description="Selecciona un item para equipar o desequipar:", 
                            color=0x9932cc)
        
        view = EquipItemView(personaje, items)
        await interaction.followup.send(embed=embed, view=view)
        
    except Exception as e:
        logger.error(f"❌ Error mostrando menú equipar: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="dar_item", description="Entrega un item a un personaje")
async def give_item(interaction: discord.Interaction, personaje: str, item: str, cantidad: int = 1):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM personajes WHERE nombre = ?", (personaje,))
            char_result = cursor.fetchone()
            if not char_result:
                await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                return
            
            cursor.execute("SELECT id, nombre FROM items WHERE nombre = ?", (item,))
            item_result = cursor.fetchone()
            if not item_result:
                await interaction.followup.send(f"❌ Item **{item}** no encontrado")
                return
            
            char_id, item_id = char_result[0], item_result[0]
            
            cursor.execute("SELECT id, cantidad FROM inventarios WHERE personaje_id = ? AND item_id = ?", 
                         (char_id, item_id))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("UPDATE inventarios SET cantidad = cantidad + ? WHERE id = ?", 
                             (cantidad, existing[0]))
                new_cantidad = existing[1] + cantidad
            else:
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
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.nombre, i.tipo, i.rareza, inv.cantidad, inv.equipado,
                       i.efecto_fuerza, i.efecto_destreza, i.efecto_velocidad,
                       i.efecto_resistencia, i.efecto_inteligencia, i.efecto_mana
                FROM inventarios inv
                JOIN items i ON inv.item_id = i.id
                JOIN personajes p ON inv.personaje_id = p.id
                WHERE p.nombre = ?
                ORDER BY inv.equipado DESC, i.nombre
            """, (personaje,))
            inventory = cursor.fetchall()
        
        if not inventory:
            await interaction.followup.send(f"❌ **{personaje}** no tiene items o no existe")
            return
        
        embed = discord.Embed(title=f"🎒 Inventario de {personaje}", color=0x9932cc)
        
        equipped_items = []
        regular_items = []
        
        for item in inventory:
            nombre, tipo, rareza, cantidad, equipado = item[0], item[1], item[2], item[3], item[4]
            
            rarity_emoji = {"comun": "⚪", "raro": "🔵", "epico": "🟣", "legendario": "🟠"}.get(rareza, "⚪")
            equip_status = "✅ Equipado" if equipado else ""
            item_line = f"{rarity_emoji} **{nombre}** x{cantidad} {equip_status}"
            
            if equipado:
                equipped_items.append(item_line)
            else:
                regular_items.append(item_line)
        
        if equipped_items:
            embed.add_field(name="⚔️ Items Equipados", value='\n'.join(equipped_items[:10]), inline=False)
        
        if regular_items:
            chunks = [regular_items[i:i+10] for i in range(0, len(regular_items), 10)]
            for i, chunk in enumerate(chunks[:2]):
                field_name = "📦 Items en Inventario" if i == 0 else "📦 Más Items"
                embed.add_field(name=field_name, value='\n'.join(chunk), inline=False)
        
        embed.set_footer(text=f"Total de tipos de items: {len(inventory)}")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error mostrando inventario: {e}")
        await interaction.followup.send("❌ Error interno")

# ============= COMANDOS DE INFORMACIÓN =============

@tree.command(name="info_npc", description="Información completa de un NPC")
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
        
        embed = discord.Embed(
            title=f"👹 {npc_data[1]}", 
            description=npc_data[10] or "Un ser misterioso del universo Unity", 
            color=0xff4444
        )
        
        embed.add_field(name="🏷️ Tipo", value=npc_data[2].title(), inline=True)
        embed.add_field(name="❤️ Puntos de Golpe", value=f"{config.FIXED_HP} PG", inline=True)
        
        # Campos de sincronización
        sincronizado = npc_data[12] if len(npc_data) > 12 else False
        cantidad = npc_data[13] if len(npc_data) > 13 else 1
        
        if sincronizado:
            embed.add_field(name="🤝 Sincronizado", value=f"Sí ({cantidad} unidades)", inline=True)
        else:
            embed.add_field(name="👤 Individual", value="Sí", inline=True)
        
        stats_text = f"⚔️ **ATAQ_FISIC:** {npc_data[3]}\n"
        stats_text += f"🏹 **ATAQ_DIST:** {npc_data[4]}\n"
        stats_text += f"🔮 **ATAQ_MAGIC:** {npc_data[5]}\n"
        stats_text += f"🛡️ **RES_FISICA:** {npc_data[6]}\n"
        stats_text += f"✨ **RES_MAGICA:** {npc_data[7]}\n"
        stats_text += f"⚡ **Velocidad:** {npc_data[8]}\n"
        stats_text += f"🧙 **Maná:** {npc_data[9]}"
        
        embed.add_field(name="📊 Estadísticas", value=stats_text, inline=True)
        
        damage_text = f"**Ataques:**\n"
        damage_text += f"⚔️ Físico: {npc_data[3]}\n"
        damage_text += f"🏹 Distancia: {npc_data[4]}\n"
        damage_text += f"🔮 Mágico: {npc_data[5]}"
        
        defense_text = f"**Defensas:**\n"
        defense_text += f"🛡️ Física: {npc_data[6]}\n"
        defense_text += f"✨ Mágica: {npc_data[7]}\n"
        defense_text += f"🏃 Esquivar: {npc_data[8]}"
        
        if sincronizado:
            damage_text += f"\n\n**Sincronizado:**\n"
            damage_text += f"⚔️ Físico: {npc_data[3] * cantidad}\n"
            damage_text += f"🏹 Distancia: {npc_data[4] * cantidad}\n"
            damage_text += f"🔮 Mágico: {npc_data[5] * cantidad}"
            
            defense_text += f"\n\n**Sincronizado:**\n"
            defense_text += f"🛡️ Física: {npc_data[6] * cantidad}\n"
            defense_text += f"✨ Mágica: {npc_data[7] * cantidad}\n"
            defense_text += f"🏃 Esquivar: {npc_data[8] * cantidad}"
        
        embed.add_field(name="💥 Ataques", value=damage_text, inline=True)
        embed.add_field(name="🛡️ Defensas", value=defense_text, inline=True)
        
        if npc_data[11]:  # imagen_url
            embed.set_thumbnail(url=npc_data[11])
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error mostrando info NPC: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="info_personaje", description="Información completa de un personaje")
async def character_info(interaction: discord.Interaction, personaje: str):
    await interaction.response.defer()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM personajes WHERE nombre = ?", (personaje,))
            char_data = cursor.fetchone()
        
        if not char_data:
            await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
            return
        
        base_stats = excel_manager.read_character_stats(personaje)
        item_bonuses = inventory_system.calculate_equipped_bonuses(personaje)
        
        if not base_stats:
            await interaction.followup.send(f"❌ No se pudieron cargar las estadísticas de **{personaje}**")
            return
        
        combined_stats = {}
        for attr in base_stats:
            combined_stats[attr] = {
                'base': base_stats[attr]['base'],
                'bonus': item_bonuses.get(attr, 0),
                'total': base_stats[attr]['base'] + item_bonuses.get(attr, 0)
            }
        
        embed = discord.Embed(title=f"🎭 {personaje}", description=char_data[4] or "Un aventurero misterioso", color=0x9932cc)
        
        embed.add_field(name="❤️ Puntos de Golpe", value=f"{config.FIXED_HP} PG", inline=True)
        embed.add_field(name="💰 Oro", value=str(char_data[5]), inline=True)
        embed.add_field(name="📝 Estado", value=char_data[6].title(), inline=True)
        
        main_attrs = ['fuerza', 'destreza', 'velocidad', 'resistencia', 'inteligencia', 'mana']
        stats_text = ""
        for attr in main_attrs:
            if attr in combined_stats:
                s = combined_stats[attr]
                emoji = {'fuerza': '💪', 'destreza': '🎯', 'velocidad': '⚡', 'resistencia': '🛡️', 'inteligencia': '🧠', 'mana': '🔮'}[attr]
                bonus_text = f" (+{s['bonus']})" if s['bonus'] > 0 else f" ({s['bonus']})" if s['bonus'] < 0 else ""
                stats_text += f"{emoji} **{attr.title()}:** {s['total']} ({s['base']}{bonus_text})\n"
        
        embed.add_field(name="📊 Atributos", value=stats_text, inline=False)
        
        if char_data[7]:  # imagen_url
            embed.set_thumbnail(url=char_data[7])
        
        google_sheets.sync_character(personaje, combined_stats)
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error mostrando info: {e}")
        await interaction.followup.send("❌ Error interno")

# ============= INICIALIZACIÓN =============
def create_default_content():
    """Crea contenido por defecto"""
    default_items = [
        ("Espada de Acero", "arma", "Espada básica de acero", 3, 0, 0, 0, 0, 0, "raro", 50),
        ("Armadura de Cuero", "armadura", "Armadura ligera de cuero", 0, 1, 0, 2, 0, 0, "comun", 30),
        ("Amuleto Mágico", "accesorio", "Aumenta poder mágico", 0, 0, 0, 0, 2, 3, "epico", 200)
    ]
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for item_data in default_items:
                cursor.execute("""INSERT OR IGNORE INTO items (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza,
                                efecto_velocidad, efecto_resistencia, efecto_inteligencia, efecto_mana,
                                rareza, precio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", item_data)
            conn.commit()
        logger.info("✅ Contenido por defecto creado")
    except Exception as e:
        logger.error(f"❌ Error creando contenido por defecto: {e}")

async def main():
    try:
        create_default_content()
        logger.info("🚀 Iniciando Unity RPG Bot...")
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