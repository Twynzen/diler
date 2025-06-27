# 🎲 Unity RPG Bot - Documentación Completa del Proyecto

## 📋 Descripción General

**Unity RPG Bot** es un bot de Discord avanzado para juegos de rol por texto que ha evolucionado desde una arquitectura monolítica (`bot.py.py`) a una estructura modular completamente refactorizada (`unity_rpg_bot/`). El sistema gestiona personajes con archivos Excel individuales, inventarios inteligentes con búsqueda fuzzy, NPCs con mecánicas sincronizadas, y un sistema de combate basado en dados D20 con logging detallado.

> **Estado Actual:** Migración completa de 14 comandos a arquitectura modular (commit `1cc586b`)

## 🏗️ Evolución y Arquitectura del Proyecto

### 📈 Historial de Desarrollo

#### Versión Legacy: `bot.py.py` (Preservada)
- **Tamaño:** ~1,500 líneas en un solo archivo monolítico
- **Características:** Todas las funcionalidades integradas en una sola clase
- **Limitaciones:** Difícil mantenimiento, colaboración compleja, testing limitado
- **Estado:** Preservada como referencia histórica y backup funcional

#### Versión Modular Actual: `unity_rpg_bot/` (Activa)
- **Estructura:** Modular con responsabilidades claramente separadas
- **Beneficios:** Mantenibilidad mejorada, escalabilidad, testabilidad, colaboración eficiente
- **Comandos:** 14 comandos slash completamente migrados y funcionales
- **Código:** ~2,000+ líneas distribuidas en 20+ archivos especializados

### 🏗️ Estructura Modular Completa

```
unity_rpg_bot/                    # 📁 Raíz de la arquitectura modular
├── config/                       # ⚙️ Configuración centralizada
│   ├── settings.py              # UnityConfig: directorios, constantes del juego
│   ├── constants.py             # COLORS, EMOJIS, DICE_TYPES, BASE_ATTRIBUTES
│   └── __init__.py
├── database/                     # 💾 Gestión de datos
│   ├── manager.py               # DatabaseManager: SQLite con context managers
│   └── __init__.py
├── discord_bot/                  # 🤖 Integración con Discord
│   ├── commands/                # 🎮 Comandos organizados por funcionalidad
│   │   ├── character_commands.py    # Crear, editar, info, borrar personajes
│   │   ├── npc_commands.py         # Crear, editar, info, borrar, tiradas NPCs
│   │   ├── item_commands.py        # Crear, editar items con efectos
│   │   ├── inventory_commands.py   # Dar, equipar, inventario, quitar items
│   │   ├── combat_commands.py      # Sistema de tiradas con menús dinámicos
│   │   └── __init__.py
│   ├── ui/                      # 🎨 Componentes de interfaz
│   │   ├── selectors.py         # NPCActionSelect, EquipItemSelect
│   │   ├── views.py             # NPCActionView, EquipItemView
│   │   └── __init__.py
│   └── __init__.py
├── game/                        # 🎯 Lógica de juego
│   ├── dice_system.py           # DiceSystem: mecánicas D20, críticos, pifias
│   ├── inventory.py             # InventorySystem: fuzzy search, logging detallado
│   ├── entities/                # 👥 [Preparado para expansión]
│   └── __init__.py
├── storage/                     # 💾 Almacenamiento y persistencia
│   ├── excel_manager.py         # ExcelManager: CRUD archivos .xlsx individuales
│   ├── google_sheets.py         # GoogleSheetsManager: sincronización nube
│   ├── image_handler.py         # ImageHandler: procesamiento, almacenamiento
│   └── __init__.py
├── utils/                       # 🛠️ Utilidades
│   ├── logging.py               # Sistema de logging categorizado
│   └── __init__.py
└── __init__.py

Archivos del proyecto:
├── main.py                      # 🚀 Punto de entrada modular (ACTIVO)
├── bot.py.py                   # 📜 Versión legacy monolítica (PRESERVADA)
├── CLAUDE.md                   # 🤖 Documentación para Claude Code
├── REFACTOR_README.md          # 📋 Documentación de migración
├── readme.md                   # 📖 Este archivo - Manual completo
└── requierements.txt           # 📦 Dependencias del proyecto
```

## 💾 Sistema de Almacenamiento Híbrido Avanzado

### 1. 🗄️ Base de Datos SQLite (`unity_master.db`)

#### Tabla: `personajes` - Metadatos de personajes
```sql
CREATE TABLE personajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,           # Nombre único del personaje
    usuario_id TEXT NOT NULL,              # Discord user ID del propietario
    excel_path TEXT NOT NULL,              # Ruta al archivo .xlsx individual
    descripcion TEXT,                      # Descripción personalizada
    oro INTEGER DEFAULT 0,                 # Sistema monetario
    estado TEXT DEFAULT 'activo',          # activo/archivado
    imagen_url TEXT,                       # Ruta a imagen de avatar
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: `npcs` - NPCs con valores fijos
```sql
CREATE TABLE npcs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tipo TEXT DEFAULT 'general',           # enemigo, aliado, neutral, jefe
    ataq_fisic INTEGER DEFAULT 10,         # Ataque físico FIJO (no tira dados)
    ataq_dist INTEGER DEFAULT 10,          # Ataque a distancia FIJO
    ataq_magic INTEGER DEFAULT 10,         # Ataque mágico FIJO
    res_fisica INTEGER DEFAULT 10,         # Resistencia física FIJA
    res_magica INTEGER DEFAULT 10,         # Resistencia mágica FIJA
    velocidad INTEGER DEFAULT 10,          # Velocidad FIJA
    mana INTEGER DEFAULT 10,               # Maná FIJO
    descripcion TEXT,
    imagen_url TEXT,
    sincronizado BOOLEAN DEFAULT FALSE,    # 🔄 NPCs múltiples sincronizados
    cantidad INTEGER DEFAULT 1,            # Número de unidades (escala automática)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: `items` - Catálogo de objetos equipables
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL,                    # arma, armadura, accesorio, consumible
    subtipo TEXT,                          # espada, escudo, anillo, poción
    rareza TEXT DEFAULT 'comun',           # comun, raro, epico, legendario
    descripcion TEXT,
    # 📊 Efectos en atributos (se suman al equipar)
    efecto_fuerza INTEGER DEFAULT 0,
    efecto_destreza INTEGER DEFAULT 0,
    efecto_velocidad INTEGER DEFAULT 0,
    efecto_resistencia INTEGER DEFAULT 0,
    efecto_inteligencia INTEGER DEFAULT 0,
    efecto_mana INTEGER DEFAULT 0,
    precio INTEGER DEFAULT 0,              # Valor en oro
    es_equipable BOOLEAN DEFAULT TRUE,     # 🔍 Crítico para sistema de equipamiento
    slot_equipo TEXT DEFAULT 'general',    # main_hand, off_hand, armor, accessory
    imagen_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: `inventarios` - Relación personaje-item
```sql
CREATE TABLE inventarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personaje_id INTEGER,
    item_id INTEGER,
    cantidad INTEGER DEFAULT 1,            # Stack de items
    equipado BOOLEAN DEFAULT FALSE,        # 🔄 Estado de equipamiento
    FOREIGN KEY (personaje_id) REFERENCES personajes (id),
    FOREIGN KEY (item_id) REFERENCES items (id)
);
```

### 2. 📊 Archivos Excel Individuales

**Ubicación:** `unity_data/personajes/activos/[NombrePersonaje].xlsx`

**Estructura de Hojas:**
- **"Estadisticas":** Atributos base del personaje (Fuerza, Destreza, Velocidad, Resistencia, Inteligencia, Maná)
- **"Info":** Metadatos (Nombre, Usuario_ID, Oro, Descripción)

**Atributos Base (todos inician en 10):**
```python
BASE_ATTRIBUTES = {
    'Fuerza': 10,      # Combate cuerpo a cuerpo
    'Destreza': 10,    # Ataques a distancia
    'Velocidad': 10,   # Esquives, iniciativa
    'Resistencia': 10, # Defensa física
    'Inteligencia': 10,# Estrategia, defensa mágica
    'Mana': 10         # Ataques mágicos
}
```

### 3. ☁️ Google Sheets (Opcional)

**Configuración:** `google-credentials.json` (Service Account)  
**Spreadsheet:** Automático: "Unity RPG - [GUILD_NAME]"  
**Sincronización:** Cada personaje obtiene su propia hoja  
**Trigger:** Se actualiza al mostrar información (`/info_personaje`)

### 4. 🖼️ Sistema de Imágenes Organizado

```
unity_data/imagenes/
├── personajes/     # 20+ avatares únicos con hash MD5
├── npcs/          # 9+ imágenes de NPCs
└── items/         # 12+ imágenes de objetos equipables
```

**Características:**
- **Nombres únicos:** Hash MD5 + timestamp para evitar colisiones
- **Formatos soportados:** PNG, JPG, GIF, WebP
- **Eliminación inteligente:** Cleanup automático al borrar entidades

## 🎮 Mecánicas de Juego Avanzadas

### 📊 Sistema de Atributos

| Atributo | Función Principal | Uso en Combate | Valor Inicial |
|----------|-------------------|-----------------|---------------|
| **Fuerza** | Combate cuerpo a cuerpo | Ataque físico | 10 |
| **Destreza** | Ataques a distancia, precisión | Ataque a distancia | 10 |
| **Velocidad** | Esquives, iniciativa | Defensa esquive | 10 |
| **Resistencia** | Defensa física, aguante | Defensa física | 10 |
| **Inteligencia** | Estrategia, análisis | Defensa mágica | 10 |
| **Maná** | Hechizos y habilidades mágicas | Ataque mágico | 10 |

### 🎲 Fórmula de Combate Unificada

```
🎲 RESULTADO = D20 + Atributo Base + Bonos de Equipo + Bonificador Situacional

Ejemplos:
⚔️ Ataque Físico = D20 + Fuerza + Bonus_Items + Bonus_Situacional
🏹 Ataque Distancia = D20 + Destreza + Bonus_Items + Bonus_Situacional
✨ Ataque Mágico = D20 + Maná + Bonus_Items + Bonus_Situacional
🛡️ Defensa Física = D20 + Resistencia + Bonus_Items + Bonus_Situacional
🏃 Defensa Esquive = D20 + Velocidad + Bonus_Items + Bonus_Situacional
🔮 Defensa Mágica = D20 + Inteligencia + Bonus_Items + Bonus_Situacional
```

### ❤️ Sistema de Salud

- **Personajes:** 10 PG fijos (constante `FIXED_HP = 10`)
- **NPCs:** Valores personalizables según tipo y balanceado por DM

### 👹 Mecánicas de NPCs Únicas

#### NPCs Individuales (sincronizado=False)
```python
# Un NPC usa sus valores directamente
"Jefe Goblin": ataq_fisic=20 → Ataque fijo de 20
```

#### NPCs Sincronizados (sincronizado=True)
```python
# Múltiples unidades escalan automáticamente
"Goblins": ataq_fisic=8, cantidad=5 → Ataque total de 40 (8×5)
```

**Característica Especial:** Los NPCs **NO tiran dados**, tienen valores fijos para balancear el combate.

## 🎯 Comandos Implementados (14 Totales)

### 🎭 Gestión de Personajes (4 comandos)

#### 1. `/crear_personaje` - Creación con Excel automático
```bash
/crear_personaje nombre:Arthas fuerza:15 destreza:12 descripcion:"Paladín caído"
```
**Proceso interno:**
1. Crea registro en tabla `personajes`
2. Genera archivo `Arthas.xlsx` en `unity_data/personajes/activos/`
3. Procesa imagen si se adjunta
4. Sincroniza con Google Sheets (opcional)

#### 2. `/editar_personaje` - Modificación de stats
```bash
/editar_personaje personaje:Arthas fuerza:18 mana:14 oro:500
```
**Características:**
- Solo el propietario puede editar
- Actualización automática en Excel y Google Sheets
- Validación de valores numéricos

#### 3. `/info_personaje` - Información completa
```bash
/info_personaje personaje:Arthas
```
**Muestra:**
- Estadísticas base (desde Excel)
- Bonos de equipo (calculados dinámicamente desde inventario)
- Total efectivo (Base + Bonos)
- Items equipados con efectos
- Inventario resumido

#### 4. `/borrar_personaje` - Eliminación con archivado
```bash
/borrar_personaje personaje:Arthas confirmacion:confirmar
```
**Proceso de seguridad:**
- Verificación de propiedad
- Movimiento a `unity_data/personajes/archivados/`
- Limpieza de inventario
- Eliminación de imagen asociada

### 👹 Sistema de NPCs (5 comandos)

#### 5. `/crear_npc` - Creación avanzada con sincronización
```bash
# NPC individual
/crear_npc nombre:"Dragón Ancestral" tipo:jefe ataq_fisic:80 res_fisica:50

# NPCs sincronizados (múltiples unidades)
/crear_npc nombre:Goblins tipo:enemigo ataq_fisic:8 sincronizado:si cantidad:5
```

#### 6. `/editar_npc` - Modificación de estadísticas
```bash
/editar_npc npc:"Dragón Ancestral" ataq_fisic:85 cantidad:1
```

#### 7. `/info_npc` - Información detallada
```bash
/info_npc npc:Goblins
```
**Muestra:** Stats base, cantidad, valores totales (si sincronizado), imagen

#### 8. `/borrar_npc` - Eliminación con confirmación
```bash
/borrar_npc npc:Goblins confirmacion:confirmar
```

#### 9. `/tirada_npc` - Sistema interactivo único
```bash
/tirada_npc npc:"Dragón Ancestral"
```
**Características:**
- Menú de selección con opciones dinámicas
- Valores fijos (no dados) para balanceo
- Resultados inmediatos sin RNG

### ✨ Sistema de Items (2 comandos)

#### 10. `/crear_item` - Creación con efectos
```bash
/crear_item nombre:"Excalibur" tipo:arma efecto_fuerza:10 efecto_mana:5 rareza:legendario precio:5000
```
**Efectos disponibles:** Todos los atributos base (fuerza, destreza, velocidad, resistencia, inteligencia, mana)

#### 11. `/editar_item` - Modificación de propiedades
```bash
/editar_item item:Excalibur efecto_fuerza:15 precio:7500 rareza:mitico
```

### 🎒 Sistema de Inventario Inteligente (3 comandos)

#### 12. `/dar_item` - Entrega con búsqueda fuzzy
```bash
# Búsqueda exacta
/dar_item personaje:Arthas item:"Excalibur" cantidad:1

# Búsqueda fuzzy (auto-corrección)
/dar_item personaje:Arthas item:excalibur cantidad:1  # ✅ Funciona
/dar_item personaje:Arthas item:"espada leg" cantidad:1  # ✅ Encuentra "Espada Legendaria"
```

**Algoritmo fuzzy:**
1. **Coincidencia exacta** (prioridad máxima)
2. **Coincidencia parcial** (búsqueda en subcadenas)
3. **Algoritmo difflib** (similitud aproximada, umbral 0.6)
4. **Sugerencias** cuando no encuentra coincidencias

#### 13. `/equipar_menu` - Gestión interactiva con diagnóstico
```bash
/equipar_menu personaje:Arthas
```

**Características avanzadas:**
- **Logging detallado** para debugging en consola
- **Diagnóstico automático** de problemas de configuración
- **Menú interactivo** con Discord UI
- **Vista previa** de items equipados vs disponibles
- **Detección de items no equipables** con explicación

**Ejemplo de logs automáticos:**
```
🔍 [INVENTORY] Buscando items equipables para: 'Arthas'
✅ [INVENTORY] Personaje encontrado: ID=5, Nombre='Arthas'
📦 [INVENTORY] Items encontrados en inventario: 3
  - 'Excalibur' [arma]: equipado=SÍ, equipable=SÍ, cantidad=1, rareza=legendario
  - 'Poción de Vida' [consumible]: equipado=NO, equipable=NO, cantidad=5, rareza=comun
⚔️ [INVENTORY] Items equipables filtrados: 1
```

#### 14. `/inventario` - Visualización organizada
```bash
/inventario personaje:Arthas
```
**Muestra:**
- Items equipados (con efectos)
- Items no equipados (organizados por rareza)
- Estadísticas del inventario
- Sugerencias de equipamiento

### 🎲 Sistema de Combate Interactivo (1 comando)

#### 15. `/tirar` - Tiradas con menús dinámicos
```bash
/tirar personaje:Arthas accion:ataque bonificador:2
```

**Flujo interactivo:**
1. **Selección de acción:** Ataque o Defensa
2. **Menú dinámico** según la acción:
   - **Ataque:** Físico (Fuerza), Mágico (Maná), Distancia (Destreza)
   - **Defensa:** Esquive (Velocidad), Física (Resistencia), Mágica (Inteligencia)
3. **Cálculo automático** con bonos de equipo
4. **Resultado detallado** con desglose completo

**Ejemplo de resultado:**
```
⚔️ Ataque Físico - Arthas
🎲 Crítico Natural!

Dado D20: 🎲 20
Fuerza: 💪 18 (15+3)
Bonificador: ➕ 2
🏆 TOTAL: 40

✨ Bonos de Equipo:
⚔️ Excalibur: +3 Fuerza
🛡️ Escudo Draconico: +2 Resistencia
```

## 🛠️ Características Técnicas Avanzadas

### 🔍 Sistema de Logging Categorizado

```python
# Logs por funcionalidad con emojis y categorías
🔍 [INVENTORY] Buscando items equipables para: 'Arthas'
✅ [INVENTORY] Personaje encontrado: ID=5, Nombre='Arthas'
🎯 [FUZZY] Coincidencia parcial: 'espada fuego' -> 'Espada de Fuego'
🎲 [DADOS] Arthas - ataque_fisico: 1d20(15) + Fuerza(18) + Bonus(2) = 35
💾 [DATABASE] Nueva entrada en inventarios: personaje_id=5, item_id=12
❌ [ERROR] Error crítico en comando /dar_item: Item no encontrado
```

**Archivos de log especializados:**
```
unity_data/logs/
├── unity.log           # Log principal del bot
├── tiradas/dados.log   # Historial de todas las tiradas
├── combates/combates.log  # Logs de sesiones de combate
└── roleplay.log        # Logs de sesiones de roleplay
```

### 🎯 Algoritmo de Búsqueda Fuzzy

```python
def fuzzy_find_item(search_term, available_items):
    """
    Búsqueda inteligente con múltiples niveles de coincidencia
    """
    # 1. Coincidencia exacta (mayor prioridad)
    for item in available_items:
        if item.lower().strip() == search_term.lower().strip():
            return item
    
    # 2. Coincidencia parcial (subcadenas)
    for item in available_items:
        if search_term.lower() in item.lower() or item.lower() in search_term.lower():
            return item
    
    # 3. Algoritmo difflib (similitud aproximada)
    matches = difflib.get_close_matches(search_term.lower(), 
                                      [item.lower() for item in available_items], 
                                      n=1, cutoff=0.6)
    if matches:
        return find_original_item(matches[0], available_items)
    
    return None  # No encontrado
```

**Casos de uso:**
```bash
Búsqueda: "excalibur" → Encuentra: "Excalibur" (exacta)
Búsqueda: "espada leg" → Encuentra: "Espada Legendaria" (parcial)
Búsqueda: "exaclibur" → Encuentra: "Excalibur" (difflib, 0.8 similitud)
Búsqueda: "xyz123" → No encuentra, sugiere items similares
```

### 🎨 UI Interactiva de Discord

#### Selectores Personalizados
```python
class NPCActionSelect(discord.ui.Select):
    """Menú dinámico para acciones de NPCs"""
    options = [
        "Ataque Físico", "Ataque Mágico", "Ataque Distancia",
        "Defensa Física", "Defensa Mágica", "Defensa Esquive"
    ]

class EquipItemSelect(discord.ui.Select):
    """Menú para equipar/desequipar items con preview"""
    # Muestra estado actual: ✅ Equipado / ⚪ No equipado
```

#### Embeds Temáticos
```python
COLORS = {
    'CHARACTER': 0x3498db,    # Azul para personajes
    'NPC': 0xe74c3c,          # Rojo para NPCs
    'ITEM': 0x9932cc,         # Púrpura para items
    'SUCCESS': 0x2ecc71,      # Verde para éxitos
    'WARNING': 0xf39c12,      # Naranja para advertencias
    'ERROR': 0xe74c3c         # Rojo para errores
}

EMOJIS = {
    'rarity': {
        'comun': '⚪',
        'raro': '🔵', 
        'epico': '🟣',
        'legendario': '🟡',
        'mitico': '🔴'
    }
}
```

### 💾 Gestión de Base de Datos con Context Managers

```python
class DatabaseManager:
    def get_connection(self):
        """Context manager para conexiones SQLite"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicialización de todas las tablas con relaciones"""
        # Crea tablas con foreign keys y índices optimizados

# Uso en comandos
with db.get_connection() as conn:
    cursor = conn.cursor()
    # Operaciones transaccionales automáticas
    cursor.execute("INSERT INTO...")
    conn.commit()  # Auto-commit en context manager
```

### 🖼️ Procesamiento Inteligente de Imágenes

```python
class ImageHandler:
    def save_image(self, image_url, entity_type, entity_name):
        """
        Guarda imágenes con nombres únicos y organización por categoría
        """
        # Genera hash MD5 + timestamp para unicidad
        # Organiza en carpetas por tipo: personajes/npcs/items
        # Soporta múltiples formatos automáticamente
        # Cleanup automático al eliminar entidades
```

## 📊 Estructura de Datos del Proyecto

### 📁 Organización de Archivos Actual

```
unity_data/                       # 📂 Datos del bot (30+ archivos)
├── personajes/
│   ├── activos/                  # 30+ archivos Excel de personajes activos
│   │   ├── Andariel.xlsx         # Cada personaje tiene su archivo individual
│   │   ├── Feanor.xlsx
│   │   ├── Yurany.xlsx
│   │   ├── Zamir.xlsx
│   │   └── ...                   # 26+ personajes más
│   └── archivados/               # Personajes eliminados (backup automático)
│       ├── Andariel.xlsx         # Versiones archivadas
│       ├── Arcadio.xlsx
│       └── ...
├── imagenes/                     # 40+ archivos de imágenes organizados
│   ├── personajes/               # 20+ avatares únicos con hash MD5
│   │   ├── Andariel_18335085.png
│   │   ├── Feanor_d4d8e9b4.jpg
│   │   ├── Yurany_75ae7072.png
│   │   └── ...
│   ├── npcs/                     # 9+ imágenes de NPCs
│   │   ├── Asesinos Eversor_1435d953.jpg
│   │   ├── Chancho Verde_22b475ef.png
│   │   ├── Lobo Lunar_5768ff67.webp
│   │   └── ...
│   └── items/                    # 12+ imágenes de objetos
│       ├── Excalibur_350a6948.png
│       ├── Bastón de Nexum Puro_11486bdb.png
│       ├── Lanza Carmesí de Tharz'Ael_1b1ab59d.png
│       └── ...
├── logs/                         # Sistema de logging categorizado
│   ├── unity.log                # Log principal del bot
│   ├── unity_detailed.log       # Log detallado de operaciones
│   ├── unity_errors.log         # Solo errores críticos
│   ├── tiradas/                 # Logs especializados
│   │   └── dados.log            # Historial de todas las tiradas
│   ├── combates/
│   │   └── combates.log         # Logs de sesiones de combate
│   └── roleplay.log             # Logs de sesiones de RP
├── unity_master.db              # Base de datos SQLite principal
├── unity_advanced.db            # Base de datos de desarrollo
└── unity_detailed.log           # Log adicional de desarrollo
```

### 📊 Métricas del Proyecto

**Código:**
- **Versión Legacy:** ~1,500 líneas (bot.py.py)
- **Versión Modular:** ~2,000+ líneas distribuidas
- **Archivos:** 20+ archivos especializados
- **Clases:** 15+ clases con responsabilidades únicas

**Datos Activos:**
- **Personajes:** 30+ archivos Excel únicos
- **NPCs:** Múltiples tipos con sincronización
- **Items:** 100+ items con efectos variados  
- **Imágenes:** 40+ archivos organizados por categoría
- **Comandos:** 14 comandos slash completamente funcionales

## 🔧 Configuración y Desarrollo

### 🌐 Variables de Entorno

```bash
# Archivo .env (requerido)
DISCORD_TOKEN=tu_token_discord_aqui
BOT_NAME=UnityRPG
GUILD_NAME=Nombre_Tu_Servidor

# Opcional (para Google Sheets)
GOOGLE_CREDENTIALS_FILE=google-credentials.json
```

### 📦 Dependencias Críticas (`requierements.txt`)

```txt
discord.py>=2.3.0          # API de Discord con slash commands
pandas>=1.5.0              # Manipulación de datos Excel
openpyxl>=3.0.0            # Lectura/escritura de archivos .xlsx
python-dotenv>=1.0.0       # Manejo de variables de entorno
gspread>=5.0.0             # Integración con Google Sheets
google-auth>=2.0.0         # Autenticación Google API
Pillow>=9.0.0              # Procesamiento de imágenes
requests>=2.28.0           # Descarga de imágenes de Discord
```

### 🚀 Comandos de Desarrollo

```bash
# Ejecutar versión modular (RECOMENDADA)
python main.py

# Ejecutar versión legacy (PRESERVADA para backup)
python bot.py.py

# Instalación de dependencias
pip install -r requierements.txt

# Verificar estructura
python -c "import unity_rpg_bot; print('✅ Importación exitosa')"
```

### 🔍 Configuración de Google Sheets (Opcional)

1. **Crear Service Account** en Google Cloud Console
2. **Habilitar APIs:** Google Sheets API + Google Drive API  
3. **Descargar credenciales** como `google-credentials.json`
4. **Colocar archivo** en raíz del proyecto
5. **El bot** creará automáticamente: "Unity RPG - [GUILD_NAME]"

## 🛡️ Seguridad y Validaciones Robustas

### 🔐 Control de Acceso

```python
# Verificación de propiedad en todos los comandos críticos
async def verify_character_ownership(user_id, character_name):
    cursor.execute("SELECT usuario_id FROM personajes WHERE nombre = ?", (character_name,))
    result = cursor.fetchone()
    return result and result[0] == str(user_id)

# Ejemplo en comando
if not await verify_character_ownership(interaction.user.id, personaje):
    await interaction.response.send_message("❌ Solo puedes editar tus propios personajes")
    return
```

### 🛠️ Manejo de Errores Avanzado

```python
# Context managers para todas las operaciones DB
try:
    with db.get_connection() as conn:
        cursor = conn.cursor()
        # Operaciones transaccionales
        cursor.execute("INSERT INTO...")
        conn.commit()
except sqlite3.IntegrityError as e:
    logger.error(f"Error de integridad: {e}")
    await interaction.response.send_message("❌ Datos duplicados")
except Exception as e:
    logger.error(f"Error crítico: {e}")
    await interaction.response.send_message("❌ Error interno del sistema")
```

### 📋 Validaciones de Entrada

```python
# Validación de parámetros numéricos
if not (1 <= fuerza <= 100):
    await interaction.response.send_message("❌ Fuerza debe estar entre 1-100")
    return

# Validación de nombres únicos
cursor.execute("SELECT COUNT(*) FROM personajes WHERE nombre = ?", (nombre,))
if cursor.fetchone()[0] > 0:
    await interaction.response.send_message("❌ Ya existe un personaje con ese nombre")
    return
```

### 🗃️ Integridad de Datos

- **Foreign Keys:** Relaciones preservadas en SQLite
- **Backup Automático:** Archivado en lugar de eliminación definitiva
- **Transacciones:** Operaciones atómicas en base de datos
- **Logging de Auditoría:** Todas las acciones críticas registradas
- **Cleanup Automático:** Eliminación de archivos huérfanos

## 🚀 Historial de Evolución (Git)

```bash
# Commits más significativos del proyecto
a82b673 docs: update README with current modular architecture
7456242 feat: improve inventory system with detailed logging and fuzzy search  
1cc586b feat: complete migration of all 14 commands to modular architecture ⭐
b594a28 refactor: implement modular architecture for Unity RPG Bot
1a1b771 Merge pull request #1 from Twynzen/update-claude-md
056cf8a docs: add comprehensive CLAUDE.md documentation
0c05eac feat(update):delete-npcs-or-characters

Estado actual: 100% migración completa a arquitectura modular
```

## 🎯 Flujos de Trabajo Típicos

### 1. 🎮 Sesión de Combate Completa

```bash
# 🏗️ Preparación inicial
/crear_personaje nombre:Kael fuerza:16 destreza:14 mana:12
/crear_npc nombre:"Dragón Ancestral" tipo:jefe ataq_fisic:25 res_fisica:20
/crear_item nombre:"Espada Flamígera" tipo:arma efecto_fuerza:5 efecto_mana:2
/dar_item personaje:Kael item:"Espada Flamígera"
/equipar_menu personaje:Kael  # Menú interactivo

# ⚔️ Durante el combate
/tirar personaje:Kael accion:ataque bonificador:2
# Resultado: D20(15) + Fuerza(16) + Item(5) + Bonus(2) = 38

/tirada_npc npc:"Dragón Ancestral"  # Menú de selección
# Seleccionar: Defensa Física
# Resultado: Fijo 20 (sin dados)

# 🏆 Post-combate
/dar_item personaje:Kael item:"Poción de Vida" cantidad:3
/editar_personaje personaje:Kael fuerza:17 oro:250  # Recompensas
```

### 2. 🎒 Gestión Avanzada de Inventario

```bash
# 🔍 Búsqueda fuzzy inteligente
/dar_item personaje:Kael item:"espada fuego"  # Auto-corrige a "Espada de Fuego"
/dar_item personaje:Kael item:"excalbiur"     # Auto-corrige a "Excalibur"

# 🎮 Equipamiento interactivo con diagnóstico
/equipar_menu personaje:Kael
# Logs automáticos muestran:
# ✅ Items encontrados, equipables vs no equipables
# ⚠️ Problemas de configuración si los hay

# 📊 Visualización completa
/inventario personaje:Kael
# Muestra: Items equipados, no equipados, estadísticas
```

### 3. 👹 Administración de NPCs

```bash
# 👤 NPCs individuales
/crear_npc nombre:"Jefe Goblin" tipo:jefe ataq_fisic:20 res_fisica:15

# 👥 NPCs sincronizados (múltiples unidades)
/crear_npc nombre:"Goblins" tipo:enemigo ataq_fisic:8 sincronizado:si cantidad:5
# Resultado: 5 goblins con ataque total de 40 (8×5)

# 🎲 Sistema de tiradas para NPCs
/tirada_npc npc:"Goblins"
# Menú muestra valores escalados automáticamente
```

## 🔮 Arquitectura Preparada para Expansión

### 🏗️ Sistema de Entidades (Framework preparado)

```python
# game/entities/character.py (preparado)
class Character:
    def __init__(self, name, stats, equipment):
        # Lógica específica de personajes
        # Métodos: level_up(), apply_buffs(), calculate_total_stats()

# game/entities/npc.py (preparado)  
class NPC:
    def __init__(self, name, combat_stats, behavior):
        # Lógica específica de NPCs
        # Métodos: scale_stats(), execute_action(), get_loot_table()
```

### 🧪 Sistema de Testing (Framework preparado)

```python
tests/
├── test_dice_system.py      # Tests de mecánicas de dados
├── test_inventory.py        # Tests de inventario y fuzzy search
├── test_database.py         # Tests de integridad de datos
├── test_commands.py         # Tests de comandos slash
└── test_integration.py      # Tests de integración completa
```

### 🚀 Características Avanzadas Planeadas

- **🎯 Sistema de Eventos:** Eventos automáticos de Discord
- **⚔️ Combate Automático:** Sistema de turnos automatizado  
- **📋 Quest System:** Sistema de misiones persistentes
- **🔨 Crafting System:** Creación de items usando ingredientes
- **🏆 Sistema de Experiencia:** Progresión automática de personajes
- **📊 Estadísticas Avanzadas:** Métricas de uso y balanceo

## 🎯 Casos de Uso Especializados

### 🔧 Debugging y Mantenimiento

```bash
# Ver logs detallados en consola al usar comandos
/equipar_menu personaje:Test
# Output automático:
🔍 [INVENTORY] Buscando items equipables para: 'Test'  
❌ [INVENTORY] Personaje 'Test' no encontrado
⚠️ [INVENTORY] PROBLEMA: Items no equipables detectados
```

### 🎮 Gestión de Sesiones de Juego

```bash
# Setup rápido para nueva campaña
/crear_personaje nombre:Heroe1 fuerza:15
/crear_personaje nombre:Heroe2 destreza:15  
/crear_npc nombre:"Boss Final" ataq_fisic:30 tipo:jefe
/crear_item nombre:"Arma Legendaria" efecto_fuerza:8

# Distribución de items
/dar_item personaje:Heroe1 item:"Arma Legendaria"
/dar_item personaje:Heroe2 item:"Arco Élfico"

# Combate coordinado
/tirar personaje:Heroe1 accion:ataque bonificador:5
/tirar personaje:Heroe2 accion:ataque bonificador:3
/tirada_npc npc:"Boss Final"  # Respuesta del jefe
```

## 📚 Documentación Adicional del Proyecto

### 📖 Archivos de Documentación

- **`CLAUDE.md`**: Documentación específica para Claude Code con instrucciones técnicas
- **`REFACTOR_README.md`**: Documentación del proceso de migración de monolítico a modular
- **`readme.md`** (este archivo): Manual completo del usuario y documentación técnica

### 🔧 Archivos de Configuración

- **`main.py`**: Punto de entrada modular (versión actual)
- **`bot.py.py`**: Versión legacy preservada (1,500+ líneas monolíticas) 
- **`requierements.txt`**: Dependencias del proyecto
- **`.env`**: Variables de entorno (crear manualmente)
- **`google-credentials.json`**: Credenciales de Google Sheets (opcional)

## 🏁 Conclusión

Unity RPG Bot representa una evolución completa desde una arquitectura monolítica (`bot.py.py` con 1,500+ líneas) hacia un sistema modular robusto y escalable (`unity_rpg_bot/` con 2,000+ líneas distribuidas). Con **14 comandos completamente funcionales**, **búsqueda fuzzy inteligente**, **logging detallado para debugging**, **almacenamiento híbrido** (SQLite + Excel + Google Sheets), y **UI interactiva**, es una solución profesional completa para comunidades de RPG en Discord.

La **arquitectura modular** facilita el mantenimiento, la escalabilidad y la colaboración, mientras que características avanzadas como la **sincronización automática**, el **sistema de inventario inteligente**, y las **mecánicas de NPCs únicas** lo posicionan como una herramienta de vanguardia para juegos de rol por texto.

### 🎯 Estado Actual
- ✅ **Migración 100% completa** a arquitectura modular
- ✅ **14 comandos** completamente funcionales
- ✅ **Sistema de búsqueda fuzzy** implementado
- ✅ **Logging detallado** para debugging
- ✅ **30+ personajes activos** en base de datos real
- ✅ **40+ imágenes** organizadas y funcionales

### 🚀 Preparado para el Futuro
- 🔧 **Framework de testing** preparado
- 🏗️ **Sistema de entidades** modular listo para expansión  
- 📊 **Métricas y estadísticas** avanzadas en desarrollo
- 🎯 **Quest system** y **crafting** en roadmap

---

*Documentación completa actualizada basada en análisis exhaustivo del proyecto en la rama `refactor/modular-architecture` - Última actualización: Commit `a82b673`*

**🎲 ¡Disfruta tus aventuras en el universo Unity con el sistema más avanzado de RPG por Discord! ⚔️✨**