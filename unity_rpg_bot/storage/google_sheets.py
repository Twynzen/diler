"""
Integración opcional con Google Sheets para sincronización de datos
"""
import os
import gspread
from google.oauth2.service_account import Credentials
from unity_rpg_bot.config.settings import config
from unity_rpg_bot.utils.logging import logger


class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.init_google_sheets()
    
    def init_google_sheets(self):
        """Inicializa la conexión con Google Sheets si está configurado"""
        try:
            if not os.path.exists(config.GOOGLE_CREDENTIALS_FILE):
                logger.info("ℹ️ Google Sheets no configurado - Usando solo almacenamiento local")
                return
                
            # Configurar autenticación
            scope = [
                'https://spreadsheets.google.com/feeds', 
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_FILE, scopes=scope)
            self.client = gspread.authorize(creds)
            
            # Abrir o crear spreadsheet principal
            spreadsheet_name = f"Unity RPG - {config.GUILD_NAME}"
            try:
                self.spreadsheet = self.client.open(spreadsheet_name)
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.client.create(spreadsheet_name)
                logger.info(f"📊 Nuevo spreadsheet creado: {spreadsheet_name}")
                
            logger.info("✅ Google Sheets conectado exitosamente")
            
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets no disponible: {e}")
            self.client = None
            self.spreadsheet = None
    
    def sync_character(self, character_name, stats):
        """
        Sincroniza las estadísticas de un personaje con Google Sheets
        
        Args:
            character_name: Nombre del personaje
            stats: Diccionario con estadísticas del personaje
        """
        if not self.client or not self.spreadsheet:
            return
            
        try:
            worksheet_name = f"PJ_{character_name}"
            
            # Obtener o crear hoja para el personaje
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=20, 
                    cols=6
                )
                logger.info(f"📋 Nueva hoja creada para {character_name}")
            
            # Preparar datos para sincronización
            data = [['ATRIBUTO', 'BASE', 'BONUS', 'TOTAL']]
            for attr, values in stats.items():
                data.append([
                    attr.title(), 
                    values['base'], 
                    values['bonus'], 
                    values['total']
                ])
            
            # Actualizar hoja
            worksheet.clear()
            worksheet.update('A1', data)
            
            logger.info(f"✅ {character_name} sincronizado en Google Sheets")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo sincronizar {character_name} con Google Sheets: {e}")
    
    def sync_npc(self, npc_name, npc_data):
        """
        Sincroniza los datos de un NPC con Google Sheets
        
        Args:
            npc_name: Nombre del NPC
            npc_data: Diccionario con datos del NPC
        """
        if not self.client or not self.spreadsheet:
            return
            
        try:
            worksheet_name = "NPCs_Database"
            
            # Obtener o crear hoja para NPCs
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=100, 
                    cols=15
                )
                # Crear encabezados
                headers = [
                    'Nombre', 'Tipo', 'ATAQ_FISIC', 'ATAQ_DIST', 'ATAQ_MAGIC',
                    'RES_FISICA', 'RES_MAGICA', 'Velocidad', 'Mana',
                    'Sincronizado', 'Cantidad', 'Descripción'
                ]
                worksheet.update('A1', [headers])
                logger.info("📋 Nueva hoja NPCs creada")
            
            # Buscar si el NPC ya existe
            all_values = worksheet.get_all_values()
            npc_row = None
            for i, row in enumerate(all_values):
                if row and row[0] == npc_name:
                    npc_row = i + 1
                    break
            
            # Preparar datos del NPC
            npc_row_data = [
                npc_name,
                npc_data.get('tipo', 'general'),
                npc_data.get('ataq_fisic', 10),
                npc_data.get('ataq_dist', 10),
                npc_data.get('ataq_magic', 10),
                npc_data.get('res_fisica', 10),
                npc_data.get('res_magica', 10),
                npc_data.get('velocidad', 10),
                npc_data.get('mana', 10),
                'Sí' if npc_data.get('sincronizado', False) else 'No',
                npc_data.get('cantidad', 1),
                npc_data.get('descripcion', '')
            ]
            
            if npc_row:
                # Actualizar NPC existente
                worksheet.update(f'A{npc_row}', [npc_row_data])
            else:
                # Añadir nuevo NPC
                worksheet.append_row(npc_row_data)
            
            logger.info(f"✅ NPC {npc_name} sincronizado en Google Sheets")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo sincronizar NPC {npc_name} con Google Sheets: {e}")
    
    def is_available(self):
        """
        Verifica si Google Sheets está disponible y configurado
        
        Returns:
            bool: True si está disponible
        """
        return self.client is not None and self.spreadsheet is not None
    
    def get_spreadsheet_url(self):
        """
        Obtiene la URL del spreadsheet principal
        
        Returns:
            str: URL del spreadsheet o None si no está disponible
        """
        if self.spreadsheet:
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"
        return None


# Instancia global del gestor de Google Sheets
google_sheets = GoogleSheetsManager()