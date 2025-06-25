"""
Punto de entrada principal para Unity RPG Bot
Versión modular refactorizada
"""
import asyncio
import discord
from discord.ext import commands

# Configuración y logging
from unity_rpg_bot.config.settings import config
from unity_rpg_bot.utils.logging import logger

# Inicialización de sistemas
from unity_rpg_bot.database.manager import db
from unity_rpg_bot.storage.google_sheets import google_sheets

# Comandos modulares
from unity_rpg_bot.discord_bot.commands.character_commands import CharacterCommands
from unity_rpg_bot.discord_bot.commands.npc_commands import NPCCommands
from unity_rpg_bot.discord_bot.commands.combat_commands import CombatCommands
from unity_rpg_bot.discord_bot.commands.item_commands import ItemCommands
from unity_rpg_bot.discord_bot.commands.inventory_commands import InventoryCommands

# UI Components (ya están importados en los comandos que los necesitan)

def create_default_content():
    """Crea contenido por defecto para el bot"""
    default_items = [
        ("Espada de Acero", "arma", "Espada básica de acero", 3, 0, 0, 0, 0, 0, "raro", 50),
        ("Armadura de Cuero", "armadura", "Armadura ligera de cuero", 0, 1, 0, 2, 0, 0, "comun", 30),
        ("Amuleto Mágico", "accesorio", "Aumenta poder mágico", 0, 0, 0, 0, 2, 3, "epico", 200)
    ]
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for item_data in default_items:
                cursor.execute("""
                    INSERT OR IGNORE INTO items (nombre, tipo, descripcion, efecto_fuerza, efecto_destreza,
                                    efecto_velocidad, efecto_resistencia, efecto_inteligencia, efecto_mana,
                                    rareza, precio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, item_data)
            conn.commit()
        logger.info("✅ Contenido por defecto creado")
    except Exception as e:
        logger.error(f"❌ Error creando contenido por defecto: {e}")


class UnityRPGBot:
    """Clase principal del bot Unity RPG"""
    
    def __init__(self):
        # Configurar intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        # Crear cliente y tree de comandos
        self.client = discord.Client(intents=intents)
        self.tree = discord.app_commands.CommandTree(self.client)
        
        # Registrar eventos
        self.setup_events()
        
        # Registrar comandos modulares
        self.setup_commands()
    
    def setup_events(self):
        """Configura los eventos del bot"""
        
        @self.client.event
        async def on_ready():
            logger.info(f"✅ {config.BOT_NAME} conectado como {self.client.user}")
            try:
                synced = await self.tree.sync()
                logger.info(f"📡 {len(synced)} comandos sincronizados")
            except Exception as e:
                logger.error(f"❌ Error sincronizando: {e}")
    
    def setup_commands(self):
        """Registra todos los comandos modulares"""
        
        # Comandos de personajes
        CharacterCommands(self.tree)
        
        # Comandos de NPCs
        NPCCommands(self.tree)
        
        # Comandos de combate
        CombatCommands(self.tree)
        
        # Comandos de items
        ItemCommands(self.tree)
        
        # Comandos de inventario
        InventoryCommands(self.tree)
        
        logger.info("🎮 Todos los comandos modulares registrados exitosamente")
    
    async def start(self):
        """Inicia el bot"""
        try:
            # Crear contenido por defecto
            create_default_content()
            
            # Verificar configuración
            if not config.DISCORD_TOKEN:
                raise ValueError("DISCORD_TOKEN no configurado en variables de entorno")
            
            # Verificar Google Sheets
            if google_sheets.is_available():
                logger.info(f"📊 Google Sheets disponible: {google_sheets.get_spreadsheet_url()}")
            
            logger.info("🚀 Iniciando Unity RPG Bot...")
            await self.client.start(config.DISCORD_TOKEN)
            
        except Exception as e:
            logger.error(f"💥 Error crítico: {e}")
            raise


async def main():
    """Función principal"""
    bot = UnityRPGBot()
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
    finally:
        logger.info("👋 Unity RPG Bot cerrado")