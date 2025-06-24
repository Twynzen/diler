# 🏗️ Refactorización a Arquitectura Modular

Este documento explica la nueva arquitectura modular del Unity RPG Bot y cómo migrar desde el archivo único `bot.py.py`.

## 🎯 ¿Por qué refactorizar?

**Antes:** Todo el código en un solo archivo `bot.py.py` de 1500+ líneas
**Ahora:** Arquitectura modular con responsabilidades separadas

### Beneficios de la nueva arquitectura:
- ✅ **Mantenibilidad:** Código organizado por responsabilidades
- ✅ **Escalabilidad:** Fácil agregar nuevas funcionalidades
- ✅ **Testabilidad:** Cada módulo puede probarse independientemente
- ✅ **Colaboración:** Múltiples desarrolladores pueden trabajar sin conflictos
- ✅ **Debugging:** Errores más fáciles de localizar y corregir

## 📁 Nueva Estructura

```
unity_rpg_bot/
├── config/
│   ├── settings.py          # Configuración principal (UnityConfig)
│   └── constants.py         # Constantes del juego
├── database/
│   └── manager.py           # Gestor de SQLite (DatabaseManager)
├── game/
│   ├── dice_system.py       # Sistema de dados y combate
│   ├── inventory.py         # Sistema de inventario
│   └── entities/            # [Futuro] Clases de personajes, NPCs, items
├── storage/
│   ├── excel_manager.py     # Gestor de archivos Excel
│   ├── image_handler.py     # Procesamiento de imágenes
│   └── google_sheets.py     # Integración con Google Sheets
├── discord_bot/
│   ├── commands/
│   │   └── character_commands.py  # Comandos de personajes
│   └── ui/
│       ├── selectors.py     # Selectores interactivos
│       └── views.py         # Vistas de Discord
├── utils/
│   └── logging.py           # Sistema de logging
└── main.py                  # Punto de entrada principal
```

## 🔄 Migración desde bot.py.py

### Paso 1: Verificar funcionamiento actual
```bash
# Asegúrate de que el bot actual funciona
python bot.py.py
```

### Paso 2: Probar nueva arquitectura
```bash
# Ejecutar versión modular
python main.py
```

### Paso 3: Comparar funcionalidad
Ambas versiones deben tener la misma funcionalidad:

**Comandos implementados en la versión modular:**
- ✅ `/crear_personaje` - Creación de personajes
- ✅ `/info_personaje` - Información de personajes  
- ✅ `/borrar_personaje` - Eliminación de personajes
- ✅ Menús interactivos para NPCs e items

**Comandos pendientes de migrar:**
- 🔄 `/crear_npc`, `/editar_npc`, `/borrar_npc`, `/info_npc`
- 🔄 `/crear_item`, `/dar_item`, `/inventario`, `/equipar_menu`
- 🔄 `/tirar`, `/tirada_npc`
- 🔄 `/editar_personaje`

## 🎮 Cómo usar la nueva arquitectura

### Ejecutar el bot
```bash
python main.py
```

### Añadir nuevos comandos
1. Crear clase en `discord_bot/commands/`
2. Registrar en `main.py` en el método `setup_commands()`

### Modificar lógica de juego
- **Dados:** Editar `game/dice_system.py`
- **Inventario:** Editar `game/inventory.py`
- **Base de datos:** Editar `database/manager.py`

### Cambiar configuración
- **Variables:** Editar `config/settings.py`
- **Constantes:** Editar `config/constants.py`

## 🔧 Desarrollo futuro

### Comandos pendientes de migrar

**NPCCommands (crear archivo `discord_bot/commands/npc_commands.py`):**
```python
- crear_npc
- editar_npc  
- borrar_npc
- info_npc
- tirada_npc
```

**ItemCommands (crear archivo `discord_bot/commands/item_commands.py`):**
```python
- crear_item
- dar_item
- inventario
- equipar_menu
```

**CombatCommands (crear archivo `discord_bot/commands/combat_commands.py`):**
```python
- tirar
```

### Expansiones sugeridas

**Sistema de Entidades:**
```python
# game/entities/character.py
class Character:
    def __init__(self, name, stats):
        # Lógica específica de personajes
        
# game/entities/npc.py  
class NPC:
    def __init__(self, name, combat_stats):
        # Lógica específica de NPCs
```

**Sistema de Tests:**
```python
tests/
├── test_dice_system.py
├── test_inventory.py
├── test_database.py
└── test_commands.py
```

## ⚠️ Notas importantes

### Compatibilidad
- ✅ **Base de datos:** Usa la misma `unity_master.db`
- ✅ **Archivos Excel:** Usa los mismos archivos en `unity_data/personajes/`
- ✅ **Imágenes:** Usa las mismas carpetas en `unity_data/imagenes/`
- ✅ **Google Sheets:** Misma integración opcional

### Variables de entorno
Sigue usando las mismas variables:
```bash
DISCORD_TOKEN=tu_token
BOT_NAME=UnityRPG
GUILD_NAME=Servidor Unity
GOOGLE_CREDENTIALS_FILE=google-credentials.json
```

### Imports circulares
La nueva arquitectura evita imports circulares:
- Cada módulo importa solo lo que necesita
- Instancias globales en cada módulo
- Dependencias claras y organizadas

## 🚀 Próximos pasos

1. **Completar migración de comandos**
2. **Añadir tests unitarios**
3. **Crear sistema de entidades**
4. **Implementar eventos de Discord**
5. **Documentar APIs internas**

## 🤝 Contribuciones

Con la nueva arquitectura modular:
- Cada desarrollador puede trabajar en módulos específicos
- Pull requests más pequeños y enfocados
- Menor riesgo de conflictos de merge
- Código más fácil de revisar