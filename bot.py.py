"""
🎲 Unity RPG Bot - Versión Definitiva para Roleplay Profundo
Versión: 3.0 - Experiencia Inmersiva Completa
Características: Menús interactivos + Gestión completa + Sistema de vida + Sin límites
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import logging
import os
import random
import pandas as pd
import openpyxl
import sqlite3
import gspread
import requests
from PIL import Image
from io import BytesIO
import base64
from datetime import datetime, timedelta
from collections import defaultdict
import re
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# ============= CONFIGURACIÓN DEFINITIVA =============

class UnityConfig:
    """Configuración definitiva del bot Unity RPG"""
    
    def __init__(self):
        load_dotenv()
        
        # Tokens y configuración básica
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        self.BOT_NAME = os.getenv('BOT_NAME', 'UnityRPG')
        self.GUILD_NAME = os.getenv('GUILD_NAME', 'Servidor Unity')
        
        # Configuración Google Sheets
        self.GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'google-credentials.json')
        self.GOOGLE_SPREADSHEET_NAME = f"Unity RPG - {self.GUILD_NAME}"
        
        # Directorios organizados
        self.DATA_DIR = "unity_data"
        self.EXCEL_DIR = f"{self.DATA_DIR}/personajes"
        self.NPC_DIR = f"{self.DATA_DIR}/npcs"
        self.ITEMS_DIR = f"{self.DATA_DIR}/items"
        self.IMAGES_DIR = f"{self.DATA_DIR}/imagenes"
        self.BACKUP_DIR = f"{self.DATA_DIR}/respaldos"
        self.LOGS_DIR = f"{self.DATA_DIR}/logs"
        self.DB_PATH = f"{self.DATA_DIR}/unity_master.db"
        
        # Configuración de dados
        self.DICE_TYPE = 20
        
        # Estadísticas base (SIN LÍMITES)
        self.BASE_ATTRIBUTES = ['Fuerza', 'Destreza', 'Velocidad', 'Inteligencia', 'Mana']
        self.DEFENSE_TYPES = ['Defensa_Esquive', 'Defensa_Fisica', 'Defensa_Magica']
        
        # Crear estructura de directorios
        self.create_directory_structure()
        self.validate_config()
    
    def create_directory_structure(self):
        """Crea estructura de directorios completa"""
        directories = [
            self.DATA_DIR, self.EXCEL_DIR, self.NPC_DIR, 
            self.ITEMS_DIR, self.IMAGES_DIR, self.BACKUP_DIR, self.LOGS_DIR,
            f"{self.EXCEL_DIR}/activos",
            f"{self.EXCEL_DIR}/archivados", 
            f"{self.ITEMS_DIR}/armas",
            f"{self.ITEMS_DIR}/armaduras",
            f"{self.ITEMS_DIR}/accesorios",
            f"{self.IMAGES_DIR}/personajes",
            f"{self.IMAGES_DIR}/items",
            f"{self.IMAGES_DIR}/npcs",
            f"{self.LOGS_DIR}/combates",
            f"{self.LOGS_DIR}/tiradas"
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ Directorio creado: {directory}")
    
    def validate_config(self):
        """Valida configuración"""
        if not self.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN no encontrado en .env")
        print("✅ Unity RPG Definitivo configurado correctamente")

config = UnityConfig()

# ============= SISTEMA DE LOGGING DEFINITIVO =============

def setup_comprehensive_logging():
    """Sistema de logging comprehensivo para roleplay"""
    
    # Crear formateadores específicos
    roleplay_formatter = logging.Formatter(
        '%(asctime)s - [ROLEPLAY] - %(levelname)s - %(message)s'
    )
    combat_formatter = logging.Formatter(
        '%(asctime)s - [COMBATE] - %(levelname)s - %(message)s'
    )
    dice_formatter = logging.Formatter(
        '%(asctime)s - [DADOS] - %(levelname)s - %(message)s'
    )
    
    # Logger principal
    logger = logging.getLogger("UnityRPG")
    logger.setLevel(logging.INFO)
    
    # Handler para roleplay general
    roleplay_handler = logging.FileHandler(f"{config.LOGS_DIR}/roleplay.log", encoding='utf-8')
    roleplay_handler.setLevel(logging.INFO)
    roleplay_handler.setFormatter(roleplay_formatter)
    
    # Handler para combates
    combat_handler = logging.FileHandler(f"{config.LOGS_DIR}/combates/combates.log", encoding='utf-8')
    combat_handler.setLevel(logging.INFO)
    combat_handler.setFormatter(combat_formatter)
    
    # Handler para tiradas de dados
    dice_handler = logging.FileHandler(f"{config.LOGS_DIR}/tiradas/dados.log", encoding='utf-8')
    dice_handler.setLevel(logging.INFO)
    dice_handler.setFormatter(dice_formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    logger.addHandler(roleplay_handler)
    logger.addHandler(combat_handler)
    logger.addHandler(dice_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_comprehensive_logging()

# ============= BASE DE DATOS DEFINITIVA =============

class MasterDatabaseManager:
    """Sistema de base de datos maestro para roleplay profundo"""
    
    def __init__(self):
        self.db_path = config.DB_PATH
        self.init_master_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_master_database(self):
        """Inicializa base de datos maestra con tablas completas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de personajes completa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    usuario_id TEXT NOT NULL,
                    webhook_id TEXT,
                    tupperbox_name TEXT,
                    excel_path TEXT NOT NULL,
                    google_sheet_id TEXT,
                    imagen_url TEXT,
                    descripcion TEXT,
                    trasfondo TEXT,
                    nivel INTEGER DEFAULT 1,
                    experiencia INTEGER DEFAULT 0,
                    puntos_vida_actual INTEGER DEFAULT 100,
                    puntos_vida_max INTEGER DEFAULT 100,
                    oro INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'activo',
                    ubicacion TEXT DEFAULT 'Desconocida',
                    notas_rp TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de NPCs completa con sistema de vida
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS npcs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    subtipo TEXT,
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
                    experiencia_otorgada INTEGER DEFAULT 10,
                    oro_otorgado INTEGER DEFAULT 5,
                    items_drop TEXT,
                    descripcion TEXT,
                    trasfondo TEXT,
                    imagen_url TEXT,
                    ubicacion TEXT DEFAULT 'Varias',
                    comportamiento TEXT DEFAULT 'Hostil',
                    facciones TEXT,
                    debilidades TEXT,
                    fortalezas TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de items súper completa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    subtipo TEXT,
                    rareza TEXT DEFAULT 'comun',
                    descripcion TEXT,
                    trasfondo TEXT,
                    imagen_url TEXT,
                    efecto_fuerza INTEGER DEFAULT 0,
                    efecto_destreza INTEGER DEFAULT 0,
                    efecto_velocidad INTEGER DEFAULT 0,
                    efecto_inteligencia INTEGER DEFAULT 0,
                    efecto_mana INTEGER DEFAULT 0,
                    efecto_def_esquive INTEGER DEFAULT 0,
                    efecto_def_fisica INTEGER DEFAULT 0,
                    efecto_def_magica INTEGER DEFAULT 0,
                    efectos_especiales TEXT,
                    requisitos TEXT,
                    precio INTEGER DEFAULT 0,
                    peso REAL DEFAULT 0.0,
                    durabilidad_max INTEGER DEFAULT 100,
                    durabilidad_actual INTEGER DEFAULT 100,
                    requisito_nivel INTEGER DEFAULT 1,
                    es_magico BOOLEAN DEFAULT FALSE,
                    es_maldito BOOLEAN DEFAULT FALSE,
                    crafteable BOOLEAN DEFAULT TRUE,
                    ingredientes TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de inventarios avanzada
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personaje_id INTEGER,
                    item_id INTEGER,
                    cantidad INTEGER DEFAULT 1,
                    equipado BOOLEAN DEFAULT FALSE,
                    slot_equipo TEXT,
                    durabilidad_actual INTEGER DEFAULT 100,
                    personalizado BOOLEAN DEFAULT FALSE,
                    nombre_personalizado TEXT,
                    historia_item TEXT,
                    obtenido_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    obtenido_como TEXT,
                    FOREIGN KEY (personaje_id) REFERENCES personajes (id),
                    FOREIGN KEY (item_id) REFERENCES items (id)
                )
            """)
            
            # Tabla de combates detallada
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS combates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personaje_id INTEGER,
                    oponente_nombre TEXT,
                    oponente_tipo TEXT,
                    ubicacion TEXT,
                    tipo_combate TEXT,
                    tirada_personaje INTEGER,
                    tirada_oponente INTEGER,
                    resultado TEXT,
                    daño_causado INTEGER DEFAULT 0,
                    daño_recibido INTEGER DEFAULT 0,
                    vida_perdida INTEGER DEFAULT 0,
                    vida_restante INTEGER,
                    experiencia_ganada INTEGER DEFAULT 0,
                    oro_ganado INTEGER DEFAULT 0,
                    items_obtenidos TEXT,
                    contexto_rp TEXT,
                    consecuencias TEXT,
                    testigos TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (personaje_id) REFERENCES personajes (id)
                )
            """)
            
            # Tabla de sesiones de roleplay
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sesiones_rp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_sesion TEXT NOT NULL,
                    narrador TEXT,
                    participantes TEXT,
                    ubicacion TEXT,
                    fecha_inicio TIMESTAMP,
                    fecha_fin TIMESTAMP,
                    resumen TEXT,
                    eventos_importantes TEXT,
                    items_otorgados TEXT,
                    experiencia_otorgada INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'activa'
                )
            """)
            
            # Tabla de relaciones entre personajes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personaje1_id INTEGER,
                    personaje2_id INTEGER,
                    tipo_relacion TEXT,
                    nivel_relacion INTEGER DEFAULT 0,
                    descripcion TEXT,
                    historia_compartida TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (personaje1_id) REFERENCES personajes (id),
                    FOREIGN KEY (personaje2_id) REFERENCES personajes (id)
                )
            """)
            
            conn.commit()
            logger.info("✅ Base de datos maestra inicializada")

db = MasterDatabaseManager()

# ============= GOOGLE SHEETS MANAGER MEJORADO =============

class AdvancedGoogleSheetsManager:
    """Gestor avanzado de Google Sheets con más funcionalidades"""
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.init_google_sheets()
    
    def init_google_sheets(self):
        """Inicializa conexión con Google Sheets"""
        try:
            if not os.path.exists(config.GOOGLE_CREDENTIALS_FILE):
                logger.warning("⚠️ Google Sheets no configurado - funcionando sin sincronización")
                return
                
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            
            creds = Credentials.from_service_account_file(
                config.GOOGLE_CREDENTIALS_FILE, scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            
            try:
                self.spreadsheet = self.client.open(config.GOOGLE_SPREADSHEET_NAME)
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.client.create(config.GOOGLE_SPREADSHEET_NAME)
                logger.info(f"✅ Spreadsheet creado: {config.GOOGLE_SPREADSHEET_NAME}")
            
            try:
                self.spreadsheet.share('', perm_type='anyone', role='reader')
            except:
                pass
                
            logger.info("✅ Google Sheets conectado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Google Sheets no disponible: {e}")
    
    def sync_character_to_sheets(self, character_name, stats, inventory_summary="", health_info=""):
        """Sincroniza personaje completo a Google Sheets"""
        if not self.client:
            return False
            
        try:
            worksheet_name = f"PJ_{character_name}"
            
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name, rows=40, cols=8
                )
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            data = [
                ['🎭 PERSONAJE', character_name, '', '', '📅 ACTUALIZADO', current_time],
                ['', '', '', '', '', ''],
                ['❤️ SALUD', health_info, '', '', '', ''],
                ['', '', '', '', '', ''],
                ['📊 ATRIBUTO', 'VALOR BASE', 'BONUS ITEMS', 'TOTAL', 'DESCRIPCIÓN', ''],
                ['💪 Fuerza', stats.get('fuerza', {}).get('base', 10), 
                 stats.get('fuerza', {}).get('bonus', 0), 
                 stats.get('fuerza', {}).get('total', 10), 'Combate físico cuerpo a cuerpo', ''],
                ['🎯 Destreza', stats.get('destreza', {}).get('base', 10),
                 stats.get('destreza', {}).get('bonus', 0),
                 stats.get('destreza', {}).get('total', 10), 'Ataques a distancia y precisión', ''],
                ['⚡ Velocidad', stats.get('velocidad', {}).get('base', 10),
                 stats.get('velocidad', {}).get('bonus', 0),
                 stats.get('velocidad', {}).get('total', 10), 'Iniciativa y movimientos rápidos', ''],
                ['🧠 Inteligencia', stats.get('inteligencia', {}).get('base', 10),
                 stats.get('inteligencia', {}).get('bonus', 0),
                 stats.get('inteligencia', {}).get('total', 10), 'Estrategia, análisis y hechizos', ''],
                ['🔮 Maná', stats.get('mana', {}).get('base', 10),
                 stats.get('mana', {}).get('bonus', 0),
                 stats.get('mana', {}).get('total', 10), 'Poder mágico y hechizos', ''],
                ['', '', '', '', '', ''],
                ['🛡️ DEFENSAS', 'VALOR BASE', 'BONUS ITEMS', 'TOTAL', 'DESCRIPCIÓN', ''],
                ['🏃 Esquive', stats.get('defensaesquive', {}).get('base', 10),
                 stats.get('defensaesquive', {}).get('bonus', 0),
                 stats.get('defensaesquive', {}).get('total', 10), 'Evasión y agilidad', ''],
                ['🛡️ Física', stats.get('defensafisica', {}).get('base', 10),
                 stats.get('defensafisica', {}).get('bonus', 0),
                 stats.get('defensafisica', {}).get('total', 10), 'Resistencia a daño físico', ''],
                ['✨ Mágica', stats.get('defensamagica', {}).get('base', 10),
                 stats.get('defensamagica', {}).get('bonus', 0),
                 stats.get('defensamagica', {}).get('total', 10), 'Resistencia a magia', ''],
                ['', '', '', '', '', ''],
                ['🎒 INVENTARIO', inventory_summary, '', '', '', '']
            ]
            
            worksheet.clear()
            worksheet.update('A1:F25', data)
            
            # Formatear con colores
            worksheet.format('A1:F1', {'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 1}, 'textFormat': {'bold': True}})
            worksheet.format('A5:F5', {'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}, 'textFormat': {'bold': True}})
            worksheet.format('A13:F13', {'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}, 'textFormat': {'bold': True}})
            
            logger.info(f"✅ {character_name} sincronizado a Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sincronizando {character_name}: {e}")
            return False
    
    def get_spreadsheet_url(self):
        """Obtiene URL del spreadsheet"""
        if self.spreadsheet:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"
        return None

google_sheets = AdvancedGoogleSheetsManager()

# ============= SISTEMA DE ITEMS MAESTRO =============

class MasterItemManager:
    """Gestor maestro de items con funcionalidades completas"""
    
    @staticmethod
    def create_item(nombre, tipo, subtipo="", descripcion="", trasfondo="", 
                   imagen_url="", efectos=None, rareza="comun", precio=0, 
                   peso=0.0, durabilidad=100, requisito_nivel=1, 
                   es_magico=False, es_maldito=False, efectos_especiales="",
                   requisitos="", created_by=""):
        """Crea un item súper completo"""
        if efectos is None:
            efectos = {}
            
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO items 
                    (nombre, tipo, subtipo, rareza, descripcion, trasfondo, imagen_url,
                     efecto_fuerza, efecto_destreza, efecto_velocidad, 
                     efecto_inteligencia, efecto_mana, efecto_def_esquive,
                     efecto_def_fisica, efecto_def_magica, efectos_especiales,
                     requisitos, precio, peso, durabilidad_max, durabilidad_actual,
                     requisito_nivel, es_magico, es_maldito, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nombre, tipo, subtipo, rareza, descripcion, trasfondo, imagen_url,
                    efectos.get('fuerza', 0), efectos.get('destreza', 0),
                    efectos.get('velocidad', 0), efectos.get('inteligencia', 0),
                    efectos.get('mana', 0), efectos.get('def_esquive', 0),
                    efectos.get('def_fisica', 0), efectos.get('def_magica', 0),
                    efectos_especiales, requisitos, precio, peso, 
                    durabilidad, durabilidad, requisito_nivel, 
                    es_magico, es_maldito, created_by
                ))
                conn.commit()
                
                logger.info(f"✅ Item épico creado: {nombre}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error creando item {nombre}: {e}")
            return False
    
    @staticmethod
    def remove_item_from_character(character_name, item_name, cantidad=1):
        """Quita un item del inventario de un personaje"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener IDs
                cursor.execute("SELECT id FROM personajes WHERE nombre = ?", (character_name,))
                char_result = cursor.fetchone()
                if not char_result:
                    return False, "Personaje no encontrado"
                
                cursor.execute("SELECT id FROM items WHERE nombre = ?", (item_name,))
                item_result = cursor.fetchone()
                if not item_result:
                    return False, "Item no encontrado"
                
                char_id, item_id = char_result[0], item_result[0]
                
                # Verificar si tiene el item
                cursor.execute("""
                    SELECT id, cantidad FROM inventarios 
                    WHERE personaje_id = ? AND item_id = ?
                """, (char_id, item_id))
                existing = cursor.fetchone()
                
                if not existing:
                    return False, "El personaje no tiene este item"
                
                inv_id, current_cantidad = existing
                
                if current_cantidad <= cantidad:
                    # Eliminar completamente
                    cursor.execute("DELETE FROM inventarios WHERE id = ?", (inv_id,))
                    message = f"{item_name} eliminado completamente del inventario"
                else:
                    # Reducir cantidad
                    cursor.execute("""
                        UPDATE inventarios SET cantidad = cantidad - ?
                        WHERE id = ?
                    """, (cantidad, inv_id))
                    message = f"{item_name} x{cantidad} removido del inventario"
                
                conn.commit()
                return True, message
                
        except Exception as e:
            logger.error(f"❌ Error quitando item: {e}")
            return False, str(e)
    
    @staticmethod
    def get_detailed_item_info(item_name):
        """Obtiene información súper detallada de un item"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM items WHERE nombre = ?", (item_name,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"❌ Error obteniendo info de item: {e}")
            return None

item_manager = MasterItemManager()

# ============= SISTEMA DE INVENTARIO MAESTRO =============

class MasterInventorySystem:
    """Sistema de inventario maestro con funcionalidades completas"""
    
    @staticmethod
    def calculate_equipped_bonuses(character_name):
        """Calcula bonuses de items equipados"""
        bonuses = {
            'fuerza': 0, 'destreza': 0, 'velocidad': 0,
            'inteligencia': 0, 'mana': 0,
            'defensaesquive': 0, 'defensafisica': 0, 'defensamagica': 0
        }
        
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
                    bonuses['fuerza'] += row[0] or 0
                    bonuses['destreza'] += row[1] or 0
                    bonuses['velocidad'] += row[2] or 0
                    bonuses['inteligencia'] += row[3] or 0
                    bonuses['mana'] += row[4] or 0
                    bonuses['defensaesquive'] += row[5] or 0
                    bonuses['defensafisica'] += row[6] or 0
                    bonuses['defensamagica'] += row[7] or 0
                    
        except Exception as e:
            logger.error(f"❌ Error calculando bonuses: {e}")
            
        return bonuses
    
    @staticmethod
    def get_detailed_inventory(character_name):
        """Obtiene inventario súper detallado"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.nombre, i.tipo, i.subtipo, i.rareza, inv.cantidad, 
                           inv.equipado, inv.slot_equipo, inv.durabilidad_actual,
                           i.descripcion, i.efectos_especiales, i.es_magico, i.es_maldito,
                           i.efecto_fuerza, i.efecto_destreza, i.efecto_velocidad,
                           i.efecto_inteligencia, i.efecto_mana, i.efecto_def_esquive,
                           i.efecto_def_fisica, i.efecto_def_magica, inv.historia_item,
                           inv.nombre_personalizado
                    FROM inventarios inv
                    JOIN items i ON inv.item_id = i.id
                    JOIN personajes p ON inv.personaje_id = p.id
                    WHERE p.nombre = ?
                    ORDER BY inv.equipado DESC, i.rareza DESC, i.nombre
                """, (character_name,))
                
                return cursor.fetchall()
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo inventario detallado: {e}")
            return []

inventory_system = MasterInventorySystem()

# ============= SISTEMA DE EXCEL MAESTRO =============

class MasterExcelManager:
    """Excel Manager maestro sin límites de puntuación"""
    
    @staticmethod
    def create_character_excel(character_name, user_id, initial_stats=None):
        """Crea Excel SIN LÍMITES de puntuación"""
        if initial_stats is None:
            initial_stats = {}
            
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        
        # Estadísticas base SIN LÍMITES
        character_data = {
            'Atributo': config.BASE_ATTRIBUTES + config.DEFENSE_TYPES,
            'Valor': [
                initial_stats.get('fuerza', 10),
                initial_stats.get('destreza', 10),
                initial_stats.get('velocidad', 10),
                initial_stats.get('inteligencia', 10),
                initial_stats.get('mana', 10),
                initial_stats.get('def_esquive', 10),
                initial_stats.get('def_fisica', 10),
                initial_stats.get('def_magica', 10)
            ],
            'Bonus_Items': [0] * 8,
            'Total': [
                initial_stats.get('fuerza', 10),
                initial_stats.get('destreza', 10),
                initial_stats.get('velocidad', 10),
                initial_stats.get('inteligencia', 10),
                initial_stats.get('mana', 10),
                initial_stats.get('def_esquive', 10),
                initial_stats.get('def_fisica', 10),
                initial_stats.get('def_magica', 10)
            ]
        }
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Hoja de estadísticas
            df_stats = pd.DataFrame(character_data)
            df_stats.to_excel(writer, sheet_name='Estadisticas', index=False)
            
            # Hoja de información completa
            info_data = {
                'Campo': ['Nombre', 'Usuario_ID', 'Nivel', 'Experiencia', 'PV_Actual', 'PV_Max', 'Oro', 'Ubicación'],
                'Valor': [character_name, str(user_id), 1, 0, 100, 100, 0, 'Desconocida']
            }
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='Info', index=False)
            
            # Hoja de roleplay
            rp_data = {
                'Aspecto': ['Descripción', 'Trasfondo', 'Personalidad', 'Objetivos', 'Miedos', 'Aliados', 'Enemigos'],
                'Contenido': ['', '', '', '', '', '', '']
            }
            df_rp = pd.DataFrame(rp_data)
            df_rp.to_excel(writer, sheet_name='Roleplay', index=False)
        
        logger.info(f"✅ Excel maestro creado para {character_name}")
        return file_path
    
    @staticmethod
    def read_character_stats_with_items(character_name):
        """Lee estadísticas completas con bonuses de items"""
        file_path = f"{config.EXCEL_DIR}/activos/{character_name}.xlsx"
        
        if not os.path.exists(file_path):
            return None
            
        try:
            df = pd.read_excel(file_path, sheet_name='Estadisticas')
            
            # Obtener bonuses de items equipados
            item_bonuses = inventory_system.calculate_equipped_bonuses(character_name)
            
            stats = {}
            for _, row in df.iterrows():
                attr_name = row['Atributo'].lower().replace('_', '')
                base_value = int(row['Valor'])
                
                bonus_key = attr_name
                if attr_name.startswith('defensa'):
                    bonus_key = attr_name
                
                item_bonus = item_bonuses.get(bonus_key, 0)
                
                stats[attr_name] = {
                    'base': base_value,
                    'bonus': item_bonus,
                    'total': base_value + item_bonus
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error leyendo stats de {character_name}: {e}")
            return None

excel_manager = MasterExcelManager()

# ============= SISTEMA DE DADOS MAESTRO =============

class MasterDiceSystem:
    """Sistema de dados maestro con funcionalidades completas"""
    
    @staticmethod
    def roll_attack(character_name, attack_type, bonificador=0):
        """Realiza tirada de ataque específica"""
        stats = excel_manager.read_character_stats_with_items(character_name)
        if not stats:
            return None
            
        dice_roll = random.randint(1, 20)
        
        attack_mapping = {
            'fisico': 'fuerza',
            'magico': 'mana', 
            'distancia': 'destreza'
        }
        
        if attack_type not in attack_mapping:
            return None
            
        attr_key = attack_mapping[attack_type]
        attr_value = stats[attr_key]['total']
        
        total = dice_roll + attr_value + bonificador
        
        # Log detallado para roleplay
        logger.info(f"[DADOS] {character_name} - Ataque {attack_type}: D20({dice_roll}) + {attr_key.title()}({attr_value}) + Bonus({bonificador}) = {total}")
        
        return {
            'dice': dice_roll,
            'attribute': attr_value,
            'attribute_name': attr_key.title(),
            'bonuses': bonificador,
            'total': total,
            'attack_type': attack_type,
            'is_critical': dice_roll == 20,
            'is_fumble': dice_roll == 1
        }
    
    @staticmethod
    def roll_defense(character_name, defense_type, bonificador=0):
        """Realiza tirada de defensa específica"""
        stats = excel_manager.read_character_stats_with_items(character_name)
        if not stats:
            return None
            
        dice_roll = random.randint(1, 20)
        
        defense_mapping = {
            'esquive': 'defensaesquive',
            'fisica': 'defensafisica',
            'magica': 'defensamagica'
        }
        
        if defense_type not in defense_mapping:
            return None
            
        attr_key = defense_mapping[defense_type]
        attr_value = stats[attr_key]['total']
        
        total = dice_roll + attr_value + bonificador
        
        # Log detallado para roleplay
        logger.info(f"[DADOS] {character_name} - Defensa {defense_type}: D20({dice_roll}) + Def.{defense_type.title()}({attr_value}) + Bonus({bonificador}) = {total}")
        
        return {
            'dice': dice_roll,
            'attribute': attr_value,
            'attribute_name': f"Defensa {defense_type.title()}",
            'bonuses': bonificador,
            'total': total,
            'defense_type': defense_type,
            'is_critical': dice_roll == 20,
            'is_fumble': dice_roll == 1
        }

dice_system = MasterDiceSystem()

# ============= SISTEMA DE NPCs MAESTRO =============

class MasterNPCManager:
    """Gestor maestro de NPCs con sistema completo"""
    
    @staticmethod
    def create_npc(nombre, tipo, subtipo="", nivel=1, vida_max=100, 
                   ataque_fisico=10, ataque_magico=10, defensa_fisica=10, 
                   defensa_magica=10, defensa_esquive=10, velocidad=10, 
                   inteligencia=10, descripcion="", trasfondo="", 
                   imagen_url="", ubicacion="Varias", comportamiento="Hostil",
                   created_by=""):
        """Crea un NPC completo con sistema de vida"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO npcs 
                    (nombre, tipo, subtipo, nivel, puntos_vida_actual, puntos_vida_max,
                     ataque_fisico, ataque_magico, defensa_fisica, defensa_magica,
                     defensa_esquive, velocidad, inteligencia, descripcion, trasfondo,
                     imagen_url, ubicacion, comportamiento, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nombre, tipo, subtipo, nivel, vida_max, vida_max,
                    ataque_fisico, ataque_magico, defensa_fisica, defensa_magica,
                    defensa_esquive, velocidad, inteligencia, descripcion, trasfondo,
                    imagen_url, ubicacion, comportamiento, created_by
                ))
                conn.commit()
                
                logger.info(f"✅ NPC maestro creado: {nombre}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error creando NPC {nombre}: {e}")
            return False
    
    @staticmethod
    def update_npc_health(npc_name, new_health):
        """Actualiza la vida de un NPC"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE npcs SET puntos_vida_actual = ?
                    WHERE nombre = ?
                """, (new_health, npc_name))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"✅ Vida de {npc_name} actualizada a {new_health}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error actualizando vida de NPC: {e}")
            return False
    
    @staticmethod
    def get_npc_detailed(npc_name):
        """Obtiene información completa de un NPC"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM npcs WHERE nombre = ?", (npc_name,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"❌ Error obteniendo NPC: {e}")
            return None

npc_manager = MasterNPCManager()

# ============= VIEWS Y MENÚS INTERACTIVOS =============

class AttackTypeSelect(discord.ui.Select):
    """Menú de selección para tipos de ataque"""
    
    def __init__(self, character_name, bonificador=0):
        self.character_name = character_name
        self.bonificador = bonificador
        
        options = [
            discord.SelectOption(
                label="Ataque Físico",
                description="Usa Fuerza para combate cuerpo a cuerpo",
                emoji="⚔️",
                value="fisico"
            ),
            discord.SelectOption(
                label="Ataque Mágico", 
                description="Usa Maná para hechizos ofensivos",
                emoji="🔮",
                value="magico"
            ),
            discord.SelectOption(
                label="Ataque a Distancia",
                description="Usa Destreza para ataques ranged",
                emoji="🏹",
                value="distancia"
            )
        ]
        
        super().__init__(
            placeholder="🎯 Selecciona tu tipo de ataque...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        attack_type = self.values[0]
        
        result = dice_system.roll_attack(self.character_name, attack_type, self.bonificador)
        
        if not result:
            await interaction.response.send_message(
                f"❌ Personaje **{self.character_name}** no encontrado", 
                ephemeral=True
            )
            return
        
        # Crear embed épico del resultado
        color = 0x00ff00 if result['total'] >= 18 else 0xff6600 if result['total'] >= 12 else 0xff0000
        
        embed = discord.Embed(
            title=f"⚔️ Ataque {attack_type.title()} - {self.character_name}",
            color=color
        )
        
        # Determinar resultado épico
        if result['is_critical']:
            embed.description = "🎯 **¡CRÍTICO DEVASTADOR!**\n*El ataque encuentra el punto perfecto*"
            embed.color = 0xffd700
        elif result['is_fumble']:
            embed.description = "💥 **¡PIFIA ÉPICA!**\n*Algo salió terriblemente mal*"
            embed.color = 0x8b0000
        elif result['total'] >= 25:
            embed.description = "🌟 **¡ATAQUE LEGENDARIO!**\n*Una demostración de poder puro*"
        elif result['total'] >= 20:
            embed.description = "⭐ **¡ATAQUE MAGISTRAL!**\n*Ejecutado con perfección técnica*"
        elif result['total'] >= 15:
            embed.description = "✅ **Ataque Exitoso**\n*Un golpe bien conectado*"
        elif result['total'] >= 12:
            embed.description = "🔶 **Ataque Parcial**\n*Impacto menor pero efectivo*"
        else:
            embed.description = "❌ **Ataque Fallido**\n*El golpe no conecta*"
        
        embed.add_field(name="🎲 Dado D20", value=f"`{result['dice']}`", inline=True)
        embed.add_field(name=f"📊 {result['attribute_name']}", value=f"`{result['attribute']}`", inline=True)
        
        if self.bonificador != 0:
            embed.add_field(name="➕ Bonificador", value=f"`{self.bonificador}`", inline=True)
        
        embed.add_field(name="🏆 **RESULTADO FINAL**", value=f"**`{result['total']}`**", inline=False)
        
        # Añadir contexto de roleplay
        if result['is_critical']:
            embed.add_field(
                name="🎭 Contexto de Roleplay",
                value="*Perfecto momento para describir un ataque espectacular*",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=None)

class DefenseTypeSelect(discord.ui.Select):
    """Menú de selección para tipos de defensa"""
    
    def __init__(self, character_name, bonificador=0):
        self.character_name = character_name
        self.bonificador = bonificador
        
        options = [
            discord.SelectOption(
                label="Defensa por Esquive",
                description="Evita el ataque con agilidad y velocidad",
                emoji="🏃",
                value="esquive"
            ),
            discord.SelectOption(
                label="Defensa Física", 
                description="Bloquea o absorbe el daño físico",
                emoji="🛡️",
                value="fisica"
            ),
            discord.SelectOption(
                label="Defensa Mágica",
                description="Resiste efectos mágicos y hechizos",
                emoji="✨",
                value="magica"
            )
        ]
        
        super().__init__(
            placeholder="🛡️ Selecciona tu tipo de defensa...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        defense_type = self.values[0]
        
        result = dice_system.roll_defense(self.character_name, defense_type, self.bonificador)
        
        if not result:
            await interaction.response.send_message(
                f"❌ Personaje **{self.character_name}** no encontrado", 
                ephemeral=True
            )
            return
        
        # Crear embed épico del resultado
        color = 0x0099ff if result['total'] >= 15 else 0xff6600 if result['total'] >= 12 else 0xff0000
        
        embed = discord.Embed(
            title=f"🛡️ Defensa {defense_type.title()} - {self.character_name}",
            color=color
        )
        
        # Determinar resultado épico
        if result['is_critical']:
            embed.description = "🎯 **¡DEFENSA PERFECTA!**\n*Una maniobra defensiva impecable*"
            embed.color = 0x00ffff
        elif result['is_fumble']:
            embed.description = "💥 **¡DEFENSA FALLIDA!**\n*Completamente desprotegido*"
            embed.color = 0x8b0000
        elif result['total'] >= 25:
            embed.description = "🌟 **¡DEFENSA LEGENDARIA!**\n*Una demostración de maestría defensiva*"
        elif result['total'] >= 20:
            embed.description = "⭐ **¡DEFENSA MAGISTRAL!**\n*Técnica defensiva superior*"
        elif result['total'] >= 15:
            embed.description = "✅ **Defensa Exitosa**\n*El ataque es neutralizado*"
        elif result['total'] >= 12:
            embed.description = "🔶 **Defensa Parcial**\n*Reduce el impacto del ataque*"
        else:
            embed.description = "❌ **Defensa Fallida**\n*El ataque pasa las defensas*"
        
        embed.add_field(name="🎲 Dado D20", value=f"`{result['dice']}`", inline=True)
        embed.add_field(name=f"📊 {result['attribute_name']}", value=f"`{result['attribute']}`", inline=True)
        
        if self.bonificador != 0:
            embed.add_field(name="➕ Bonificador", value=f"`{self.bonificador}`", inline=True)
        
        embed.add_field(name="🏆 **RESULTADO FINAL**", value=f"**`{result['total']}`**", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=None)

class AttackView(discord.ui.View):
    """Vista para selección de ataque"""
    
    def __init__(self, character_name, bonificador=0):
        super().__init__(timeout=60)
        self.add_item(AttackTypeSelect(character_name, bonificador))

class DefenseView(discord.ui.View):
    """Vista para selección de defensa"""
    
    def __init__(self, character_name, bonificador=0):
        super().__init__(timeout=60)
        self.add_item(DefenseTypeSelect(character_name, bonificador))

# ============= BOT MAESTRO CON COMANDOS DEFINITIVOS =============

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    logger.info(f"✅ {config.BOT_NAME} DEFINITIVO conectado como {client.user}")
    
    try:
        synced = await tree.sync()
        logger.info(f"📡 {len(synced)} comandos maestros sincronizados")
    except Exception as e:
        logger.error(f"❌ Error sincronizando comandos: {e}")
    
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="Unity RPG Definitivo - Roleplay Profundo"
        )
    )

# ============= COMANDOS MAESTROS =============

@tree.command(name="crear_personaje", description="Crea un personaje épico SIN LÍMITES de puntuación")
async def create_character_master(
    interaction: discord.Interaction,
    nombre: str,
    fuerza: int = 10,
    destreza: int = 10,
    velocidad: int = 10,
    inteligencia: int = 10,
    mana: int = 10,
    def_esquive: int = 10,
    def_fisica: int = 10,
    def_magica: int = 10,
    descripcion: str = "Un aventurero misterioso"
):
    """Crea personaje SIN LÍMITES de puntuación"""
    await interaction.response.defer()
    
    try:
        initial_stats = {
            'fuerza': fuerza, 'destreza': destreza, 'velocidad': velocidad,
            'inteligencia': inteligencia, 'mana': mana,
            'def_esquive': def_esquive, 'def_fisica': def_fisica, 'def_magica': def_magica
        }
        
        # Crear Excel
        excel_path = excel_manager.create_character_excel(nombre, interaction.user.id, initial_stats)
        
        # Registrar en base de datos
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO personajes 
                (nombre, usuario_id, excel_path, descripcion)
                VALUES (?, ?, ?, ?)
            """, (nombre, str(interaction.user.id), excel_path, descripcion))
            conn.commit()
        
        # Sincronizar con Google Sheets
        stats = excel_manager.read_character_stats_with_items(nombre)
        google_sheets.sync_character_to_sheets(nombre, stats, "", "100/100 PV")
        
        # Crear embed épico
        embed = discord.Embed(
            title="🎭 ¡Personaje Épico Creado!",
            description=f"**{nombre}** ha despertado en el universo Unity",
            color=0x00ff00
        )
        
        embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
        
        # Estadísticas principales
        stats_text = f"💪 **Fuerza:** {fuerza}\n🎯 **Destreza:** {destreza}\n⚡ **Velocidad:** {velocidad}\n🧠 **Inteligencia:** {inteligencia}\n🔮 **Maná:** {mana}"
        embed.add_field(name="📊 Atributos", value=stats_text, inline=True)
        
        # Defensas
        def_text = f"🏃 **Esquive:** {def_esquive}\n🛡️ **Física:** {def_fisica}\n✨ **Mágica:** {def_magica}"
        embed.add_field(name="🛡️ Defensas", value=def_text, inline=True)
        
        embed.add_field(name="❤️ Vida", value="100/100 PV", inline=True)
        
        if google_sheets.get_spreadsheet_url():
            embed.add_field(
                name="📊 Google Sheets",
                value=f"[Ver en tiempo real]({google_sheets.get_spreadsheet_url()})",
                inline=False
            )
        
        embed.set_footer(text="¡Listo para comenzar tu aventura épica!")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error creando personaje: {e}")
        await interaction.followup.send("❌ Error interno al crear personaje")

@tree.command(name="crear_npc", description="Crea un NPC completo con sistema de vida")
async def create_npc_master(
    interaction: discord.Interaction,
    nombre: str,
    tipo: str,
    nivel: int = 1,
    vida_max: int = 100,
    ataque_fisico: int = 10,
    ataque_magico: int = 10,
    defensa_fisica: int = 10,
    defensa_magica: int = 10,
    defensa_esquive: int = 10,
    velocidad: int = 10,
    inteligencia: int = 10,
    descripcion: str = "Un ser del universo Unity",
    ubicacion: str = "Varias"
):
    """Crea un NPC completo"""
    await interaction.response.defer()
    
    try:
        success = npc_manager.create_npc(
            nombre, tipo, "", nivel, vida_max, ataque_fisico, ataque_magico,
            defensa_fisica, defensa_magica, defensa_esquive, velocidad,
            inteligencia, descripcion, "", "", ubicacion, "Hostil",
            str(interaction.user.id)
        )
        
        if success:
            embed = discord.Embed(
                title="👹 ¡NPC Épico Creado!",
                description=f"**{nombre}** ha sido añadido al universo Unity",
                color=0xff4444
            )
            
            embed.add_field(name="🏷️ Tipo", value=tipo.title(), inline=True)
            embed.add_field(name="📊 Nivel", value=str(nivel), inline=True)
            embed.add_field(name="❤️ Vida", value=f"{vida_max}/{vida_max} PV", inline=True)
            
            # Estadísticas de combate
            combat_text = f"⚔️ **At. Físico:** {ataque_fisico}\n🔮 **At. Mágico:** {ataque_magico}\n⚡ **Velocidad:** {velocidad}\n🧠 **Inteligencia:** {inteligencia}"
            embed.add_field(name="⚔️ Combate", value=combat_text, inline=True)
            
            # Defensas
            def_text = f"🏃 **Esquive:** {defensa_esquive}\n🛡️ **Física:** {defensa_fisica}\n✨ **Mágica:** {defensa_magica}"
            embed.add_field(name="🛡️ Defensas", value=def_text, inline=True)
            
            embed.add_field(name="📍 Ubicación", value=ubicacion, inline=True)
            embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
            
            embed.set_footer(text="NPC listo para interactuar con los aventureros")
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="No se pudo crear el NPC (posiblemente ya existe).",
                color=0xff0000
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error creando NPC: {e}")
        await interaction.followup.send("❌ Error interno creando NPC")

@tree.command(name="tirar", description="Sistema de tiradas maestro con menús interactivos")
async def roll_master(
    interaction: discord.Interaction,
    personaje: str,
    accion: str,  # "ataque" o "defensa"
    bonificador: int = 0
):
    """Sistema de tiradas con menús interactivos"""
    await interaction.response.defer()
    
    try:
        if accion.lower() == "ataque":
            embed = discord.Embed(
                title=f"⚔️ {personaje} - Seleccionar Ataque",
                description="Elige el tipo de ataque que deseas realizar:",
                color=0xff6600
            )
            embed.add_field(
                name="🎯 Opciones Disponibles",
                value="⚔️ **Físico** - Usa Fuerza\n🔮 **Mágico** - Usa Maná\n🏹 **Distancia** - Usa Destreza",
                inline=False
            )
            if bonificador != 0:
                embed.add_field(name="➕ Bonificador", value=str(bonificador), inline=True)
                
            view = AttackView(personaje, bonificador)
            await interaction.followup.send(embed=embed, view=view)
            
        elif accion.lower() == "defensa":
            embed = discord.Embed(
                title=f"🛡️ {personaje} - Seleccionar Defensa",
                description="Elige el tipo de defensa que deseas usar:",
                color=0x0099ff
            )
            embed.add_field(
                name="🛡️ Opciones Disponibles",
                value="🏃 **Esquive** - Evita con agilidad\n🛡️ **Física** - Bloquea el daño\n✨ **Mágica** - Resiste magia",
                inline=False
            )
            if bonificador != 0:
                embed.add_field(name="➕ Bonificador", value=str(bonificador), inline=True)
                
            view = DefenseView(personaje, bonificador)
            await interaction.followup.send(embed=embed, view=view)
            
        else:
            await interaction.followup.send(
                "❌ Acción inválida. Usa: `ataque` o `defensa`"
            )
            
    except Exception as e:
        logger.error(f"❌ Error en tirada maestro: {e}")
        await interaction.followup.send("❌ Error interno en tirada")

@tree.command(name="vida_npc", description="Modifica la vida de un NPC")
async def npc_health_command(
    interaction: discord.Interaction,
    npc: str,
    nueva_vida: int
):
    """Modifica la vida de un NPC"""
    await interaction.response.defer()
    
    try:
        # Obtener datos actuales del NPC
        npc_data = npc_manager.get_npc_detailed(npc)
        
        if not npc_data:
            await interaction.followup.send(f"❌ NPC **{npc}** no encontrado")
            return
        
        vida_anterior = npc_data[5]  # puntos_vida_actual
        vida_max = npc_data[6]  # puntos_vida_max
        
        # Validar nueva vida
        if nueva_vida < 0:
            nueva_vida = 0
        elif nueva_vida > vida_max:
            nueva_vida = vida_max
        
        # Actualizar vida
        success = npc_manager.update_npc_health(npc, nueva_vida)
        
        if success:
            embed = discord.Embed(
                title=f"❤️ Vida de {npc} Actualizada",
                color=0x00ff00 if nueva_vida > vida_anterior else 0xff0000
            )
            
            embed.add_field(name="❤️ Vida Anterior", value=f"{vida_anterior}/{vida_max} PV", inline=True)
            embed.add_field(name="❤️ Vida Nueva", value=f"{nueva_vida}/{vida_max} PV", inline=True)
            
            cambio = nueva_vida - vida_anterior
            if cambio > 0:
                embed.add_field(name="💚 Curado", value=f"+{cambio} PV", inline=True)
                embed.description = f"**{npc}** ha sido curado"
            elif cambio < 0:
                embed.add_field(name="💔 Daño", value=f"{cambio} PV", inline=True)
                embed.description = f"**{npc}** ha recibido daño"
            else:
                embed.description = f"Vida de **{npc}** sin cambios"
            
            if nueva_vida == 0:
                embed.add_field(name="💀 Estado", value="**DERROTADO**", inline=False)
                embed.color = 0x8b0000
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="No se pudo actualizar la vida del NPC",
                color=0xff0000
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error actualizando vida NPC: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="quitar_item", description="Quita un item del inventario de un personaje")
async def remove_item_command(
    interaction: discord.Interaction,
    personaje: str,
    item: str,
    cantidad: int = 1
):
    """Quita item del inventario"""
    await interaction.response.defer()
    
    try:
        success, message = item_manager.remove_item_from_character(personaje, item, cantidad)
        
        if success:
            embed = discord.Embed(
                title="🗑️ Item Removido",
                description=message,
                color=0xff6600
            )
            
            # Actualizar Google Sheets
            stats = excel_manager.read_character_stats_with_items(personaje)
            if stats:
                google_sheets.sync_character_to_sheets(
                    personaje, stats, f"Item removido: {item}"
                )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=message,
                color=0xff0000
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error quitando item: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="eliminar_personaje", description="Elimina completamente un personaje")
async def delete_character_command(
    interaction: discord.Interaction,
    personaje: str,
    confirmacion: str
):
    """Elimina un personaje completamente"""
    await interaction.response.defer()
    
    try:
        if confirmacion.lower() != "confirmar":
            await interaction.followup.send(
                "⚠️ Para eliminar un personaje debes escribir `confirmar` en el campo confirmación"
            )
            return
        
        # Verificar que el personaje existe y pertenece al usuario
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, usuario_id, excel_path FROM personajes 
                WHERE nombre = ?
            """, (personaje,))
            char_data = cursor.fetchone()
            
            if not char_data:
                await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
                return
            
            char_id, usuario_id, excel_path = char_data
            
            # Verificar permisos (solo el creador puede eliminar)
            if usuario_id != str(interaction.user.id):
                await interaction.followup.send("❌ Solo puedes eliminar tus propios personajes")
                return
            
            # Eliminar de la base de datos
            cursor.execute("DELETE FROM inventarios WHERE personaje_id = ?", (char_id,))
            cursor.execute("DELETE FROM combates WHERE personaje_id = ?", (char_id,))
            cursor.execute("DELETE FROM personajes WHERE id = ?", (char_id,))
            conn.commit()
            
            # Mover Excel a archivo
            if os.path.exists(excel_path):
                archive_path = excel_path.replace("/activos/", "/archivados/")
                os.rename(excel_path, archive_path)
        
        embed = discord.Embed(
            title="🗑️ Personaje Eliminado",
            description=f"**{personaje}** ha sido eliminado completamente del universo Unity",
            color=0x8b0000
        )
        embed.add_field(
            name="📁 Archivo Excel",
            value="Movido a la carpeta de archivados",
            inline=False
        )
        embed.set_footer(text="Esta acción no se puede deshacer")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error eliminando personaje: {e}")
        await interaction.followup.send("❌ Error interno")

@tree.command(name="info_personaje", description="Muestra información completa de un personaje")
async def character_info_command(
    interaction: discord.Interaction,
    personaje: str
):
    """Muestra información épica y completa de un personaje"""
    await interaction.response.defer()
    
    try:
        # Obtener datos del personaje
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM personajes WHERE nombre = ?
            """, (personaje,))
            char_data = cursor.fetchone()
        
        if not char_data:
            await interaction.followup.send(f"❌ Personaje **{personaje}** no encontrado")
            return
        
        # Obtener estadísticas
        stats = excel_manager.read_character_stats_with_items(personaje)
        
        if not stats:
            await interaction.followup.send(f"❌ No se pudieron cargar las estadísticas de **{personaje}**")
            return
        
        # Crear embed épico
        embed = discord.Embed(
            title=f"🎭 {personaje}",
            description=char_data[8] if char_data[8] else "Un aventurero misterioso del universo Unity",
            color=0x9932cc
        )
        
        # Imagen si existe
        if char_data[7]:  # imagen_url
            embed.set_thumbnail(url=char_data[7])
        
        # Información básica
        embed.add_field(name="📊 Nivel", value=str(char_data[10]), inline=True)
        embed.add_field(name="⭐ Experiencia", value=str(char_data[11]), inline=True)
        embed.add_field(name="❤️ Vida", value=f"{char_data[12]}/{char_data[13]} PV", inline=True)
        
        # Estadísticas principales
        main_attrs = ['fuerza', 'destreza', 'velocidad', 'inteligencia', 'mana']
        stats_text = ""
        for attr in main_attrs:
            if attr in stats:
                s = stats[attr]
                emoji = {'fuerza': '💪', 'destreza': '🎯', 'velocidad': '⚡', 'inteligencia': '🧠', 'mana': '🔮'}[attr]
                bonus_text = f" (+{s['bonus']})" if s['bonus'] > 0 else f" ({s['bonus']})" if s['bonus'] < 0 else ""
                stats_text += f"{emoji} **{attr.title()}:** {s['total']} ({s['base']}{bonus_text})\n"
        
        embed.add_field(name="📊 Atributos", value=stats_text, inline=True)
        
        # Defensas
        defense_attrs = ['defensaesquive', 'defensafisica', 'defensamagica']
        defense_names = ['🏃 Esquive', '🛡️ Física', '✨ Mágica']
        def_text = ""
        
        for attr, name in zip(defense_attrs, defense_names):
            if attr in stats:
                s = stats[attr]
                bonus_text = f" (+{s['bonus']})" if s['bonus'] > 0 else f" ({s['bonus']})" if s['bonus'] < 0 else ""
                def_text += f"{name}: {s['total']} ({s['base']}{bonus_text})\n"
        
        embed.add_field(name="🛡️ Defensas", value=def_text, inline=True)
        
        # Información adicional
        embed.add_field(name="💰 Oro", value=str(char_data[14]), inline=True)
        embed.add_field(name="📍 Ubicación", value=char_data[16] if char_data[16] else "Desconocida", inline=True)
        embed.add_field(name="📝 Estado", value=char_data[15].title(), inline=True)
        
        # Sincronizar con Google Sheets
        health_info = f"{char_data[12]}/{char_data[13]} PV"
        google_sheets.sync_character_to_sheets(personaje, stats, "Info consultada", health_info)
        
        if google_sheets.get_spreadsheet_url():
            embed.add_field(
                name="📊 Ver en Google Sheets",
                value=f"[Enlace directo]({google_sheets.get_spreadsheet_url()})",
                inline=False
            )
        
        embed.set_footer(text=f"Creado: {char_data[18][:10]} | Última vez usado: {char_data[19][:10]}")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"❌ Error mostrando info de personaje: {e}")
        await interaction.followup.send("❌ Error interno")

# ============= FUNCIONES DE INICIALIZACIÓN =============

def create_epic_items():
    """Crea items épicos por defecto"""
    epic_items = [
        {
            'nombre': 'Espada Flamígera del Amanecer',
            'tipo': 'arma',
            'subtipo': 'espada',
            'descripcion': 'Una espada legendaria que arde con el fuego del amanecer eterno',
            'trasfondo': 'Forjada por los antiguos maestros herreros en las llamas del primer amanecer',
            'rareza': 'legendario',
            'efectos': {'fuerza': 8, 'mana': 3, 'def_fisica': 2},
            'es_magico': True,
            'efectos_especiales': 'Daño de fuego adicional al amanecer'
        },
        {
            'nombre': 'Armadura de Escamas Dracónicas',
            'tipo': 'armadura',
            'subtipo': 'armadura_pesada',
            'descripcion': 'Armadura forjada con las escamas de un dragón ancestral',
            'trasfondo': 'Creada a partir de las escamas del legendario Dragón de Obsidiana',
            'rareza': 'epico',
            'efectos': {'def_fisica': 12, 'def_magica': 8, 'velocidad': -2},
            'es_magico': True,
            'efectos_especiales': 'Resistencia al fuego y miedo'
        },
        {
            'nombre': 'Amuleto de los Vientos Susurrantes',
            'tipo': 'accesorio',
            'subtipo': 'amuleto',
            'descripcion': 'Un amuleto que contiene la esencia de los vientos ancestrales',
            'trasfondo': 'Bendecido por los espíritus del viento en las montañas sagradas',
            'rareza': 'raro',
            'efectos': {'velocidad': 6, 'def_esquive': 4, 'inteligencia': 2},
            'es_magico': True,
            'efectos_especiales': 'Permite levitación breve'
        }
    ]
    
    for item_data in epic_items:
        item_manager.create_item(**item_data, created_by="system")

def create_legendary_npcs():
    """Crea NPCs legendarios por defecto"""
    legendary_npcs = [
        ("Chancho Verde Ancestral", "criatura", "bestia_magica", 3, 150, 15, 5, 18, 25, 12, 15, 12, 
         "Una criatura ancestral de los bosques profundos con sabiduría milenaria", 
         "Antiguamente fue el guardián de los bosques sagrados", "", "Bosques Profundos"),
        
        ("Dragón Rojo Emperador", "dragon", "dragón_ancestral", 15, 800, 45, 40, 35, 50, 20, 25, 20,
         "El más poderoso de los dragones rojos, emperador de las montañas ardientes",
         "Reinó durante mil años sobre las montañas volcánicas del norte", "", "Montañas Ardientes"),
        
        ("Lich Supremo Malachar", "no-muerto", "lich", 12, 400, 15, 50, 20, 45, 25, 18, 25,
         "Un poderoso hechicero que alcanzó la inmortalidad a través de la nigromancia",
         "Antiguamente fue el archimago más poderoso del reino, corrompido por el poder", "", "Torre Maldita"),
        
        ("Asesino de las Sombras", "humanoide", "asesino_élite", 8, 200, 35, 10, 15, 20, 40, 30, 15,
         "Un asesino legendario que se mueve entre las sombras como si fuera una de ellas",
         "Entrenado desde niño en las artes del sigilo y la muerte silenciosa", "", "Callejones Oscuros")
    ]
    
    for npc_data in legendary_npcs:
        npc_manager.create_npc(*npc_data, created_by="system")

async def main():
    """Función principal del bot maestro"""
    try:
        # Inicializar contenido épico
        create_epic_items()
        create_legendary_npcs()
        
        logger.info("🚀 Iniciando Unity RPG Bot DEFINITIVO...")
        logger.info(f"📊 Google Sheets: {'✅ Conectado' if google_sheets.client else '❌ Modo Local'}")
        logger.info("🎭 Sistema de roleplay profundo activado")
        logger.info("⚡ Sin límites de puntuación habilitado")
        logger.info("🎲 Menús interactivos listos")
        
        await client.start(config.DISCORD_TOKEN)
        
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        raise e

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot maestro detenido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
    finally:
        logger.info("👋 Unity RPG Bot DEFINITIVO cerrado - ¡Que continúen las aventuras!")