"""
Gestor de base de datos SQLite para Unity RPG Bot
"""
import sqlite3
from unity_rpg_bot.config.settings import config
from unity_rpg_bot.utils.logging import logger


class DatabaseManager:
    def __init__(self):
        self.db_path = config.DB_PATH
        self.init_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos SQLite"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
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
            
            # Crear todas las tablas
            self._create_personajes_table(cursor)
            self._create_npcs_table(cursor)
            self._create_items_table(cursor)
            self._create_inventarios_table(cursor)
            
            conn.commit()
            logger.info("✅ Base de datos inicializada correctamente")
    
    def _create_personajes_table(self, cursor):
        """Crea la tabla de personajes"""
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
    
    def _create_npcs_table(self, cursor):
        """Crea la tabla de NPCs"""
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
    
    def _create_items_table(self, cursor):
        """Crea la tabla de items"""
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
    
    def _create_inventarios_table(self, cursor):
        """Crea la tabla de inventarios"""
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


# Instancia global del gestor de base de datos
db = DatabaseManager()