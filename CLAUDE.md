# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

## Descripción del Proyecto

Este es un bot de Discord para juegos de rol por texto construido en Python usando discord.py v2.3.0+. El bot gestiona sesiones de rol en servidores de Discord con sistema de personajes, dados, NPCs e inventarios. Usa archivos Excel para hojas de personajes individuales, SQLite para datos del servidor, y opcionalmente sincroniza con Google Sheets.

## Comando de Desarrollo

```bash
# Instalar dependencias
pip install -r requierements.txt

# Ejecutar el bot (requiere DISCORD_TOKEN en .env)
python bot.py.py
```

## Estructura del Proyecto

**Archivo Principal:** `bot.py.py` - Contiene toda la lógica del bot en un solo archivo
**Directorio de Datos:** `unity_data/` - Todos los datos del bot se almacenan aquí

### Organización de Datos
```
unity_data/
├── personajes/
│   ├── activos/        # Archivos Excel de personajes activos (.xlsx)
│   └── archivados/     # Personajes eliminados
├── imagenes/
│   ├── personajes/     # Imágenes de avatares de personajes
│   ├── npcs/          # Imágenes de NPCs
│   └── items/         # Imágenes de objetos
├── logs/              # Logs del bot (unity.log)
└── unity_master.db    # Base de datos SQLite principal
```

## Arquitectura del Bot

### Sistema de Almacenamiento Híbrido
- **SQLite (unity_master.db):** Datos del servidor, relaciones, inventarios, NPCs
- **Excel Individual:** Cada personaje tiene su propio archivo .xlsx con estadísticas
- **Google Sheets (Opcional):** Sincronización en la nube para backup

### Mecánicas de Juego
- **Personajes:** 6 atributos (Fuerza, Destreza, Velocidad, Resistencia, Inteligencia, Maná)
- **Salud Fija:** Todos tienen 10 PG (no cambia con nivel)
- **Sistema de Dados:** D3, D6, D8, D10, D12, D20 con hasta 5 dados simultáneos
- **Fórmula:** `Tirada de Dados + Atributo + Bonos de Equipo + Bonus Situacional`
- **NPCs:** Valores fijos, pueden estar sincronizados (múltiples unidades)

### Componentes Principales

#### Clases de Gestión
- `UnityConfig`: Configuración centralizada y directorios
- `DatabaseManager`: Manejo de SQLite con context managers
- `ExcelManager`: Operaciones CRUD en archivos Excel de personajes
- `GoogleSheetsManager`: Sincronización opcional con Google Sheets
- `ImageHandler`: Procesamiento y almacenamiento de imágenes
- `InventorySystem`: Cálculo de bonos de equipo
- `DiceSystem`: Mecánicas de tiradas y acciones

#### Sistema de Comandos (Slash Commands)
- **Creación:** `/crear_personaje`, `/crear_npc`, `/crear_item`
- **Tiradas:** `/tirar` (personajes), `/tirada_npc` (NPCs con menús interactivos)
- **Gestión:** `/editar_personaje`, `/editar_npc`, `/borrar_personaje`, `/borrar_npc`
- **Inventario:** `/dar_item`, `/equipar_menu`, `/inventario`
- **Información:** `/info_personaje`, `/info_npc`

#### Componentes UI Interactivos
- `NPCActionSelect`: Menú de selección para acciones de NPCs
- `EquipItemSelect`: Menú para equipar/desequipar items
- `NPCActionView` y `EquipItemView`: Contenedores de componentes UI

## Patrones de Desarrollo

### Manejo de Datos
- Cada personaje tiene un archivo Excel individual en `personajes/activos/`
- SQLite almacena metadatos, relaciones e inventarios
- Context managers para todas las operaciones de base de datos
- Validación de propietario para operaciones de edición/borrado

### Integración Discord
- Solo comandos slash (app_commands)
- Componentes UI nativos (Select, Button, View)
- Imágenes como thumbnails en embeds
- Respuestas diferidas para operaciones largas

### Sistema de Bonos
Los bonos de equipo se calculan dinámicamente:
- Items equipados suman/restan atributos
- Fórmula final: `Atributo Base + Bonos de Equipo = Atributo Total`
- Sincronización automática con Google Sheets al mostrar info

### Logs y Debugging
- Logging completo en `unity_data/logs/unity.log`
- Errores capturados con contexto
- Operaciones de dados logeadas para auditoría

## Configuración Requerida

### Variables de Entorno
```bash
DISCORD_TOKEN=tu_token_aqui
BOT_NAME=UnityRPG
GUILD_NAME=Nombre_Servidor
GOOGLE_CREDENTIALS_FILE=google-credentials.json  # Opcional
```

### Google Sheets (Opcional)
- Requiere archivo `google-credentials.json` con credenciales de Service Account
- Permisos: Google Sheets API y Google Drive API
- Crea spreadsheet automáticamente: "Unity RPG - [GUILD_NAME]"
- Cada personaje obtiene su propia hoja de cálculo

## Notas Importantes

### Limitaciones
- Un personaje por usuario por comando (no hay sistema de múltiples personajes)
- Imágenes se almacenan localmente (no en cloud)
- NPCs sincronizados multiplican valores base por cantidad de unidades
- Sistema de oro presente pero no integrado completamente

### Convenciones de Código
- Nombres de personajes en formato título
- Context managers obligatorios para SQLite
- Logging extensivo para debugging
- Validaciones de entrada para todos los comandos
- Manejo de errores con mensajes user-friendly

### Extensibilidad
El código está diseñado modularmente. Para agregar nuevas características:
- Nuevos comandos: agregar funciones con decorador `@tree.command`
- Nuevas tablas: modificar `DatabaseManager.init_database()`
- Nuevos tipos de dados: actualizar `DICE_TYPES` en `UnityConfig`
- Nuevos atributos: modificar `BASE_ATTRIBUTES` y actualizar Excel/DB schemas