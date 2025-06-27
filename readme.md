# 🎲 Unity RPG Bot - Manual Completo

## 📋 Introducción

**Unity RPG Bot** es un bot de Discord especializado en juegos de rol por texto con arquitectura modular. Gestiona personajes con archivos Excel individuales, sistema de inventario avanzado, NPCs inteligentes y mecánicas de dados D20 completamente automatizadas.

## ⚙️ Arquitectura Actual

### 🏗️ Estructura Modular
```
unity_rpg_bot/
├── config/          # Configuración y constantes
├── database/        # Gestión de SQLite
├── discord_bot/     # Comandos y UI de Discord
│   ├── commands/    # Comandos organizados por categoría
│   └── ui/          # Selectores y vistas interactivas
├── game/           # Lógica de juego (dados, inventario)
├── storage/        # Excel, Google Sheets, imágenes
└── utils/          # Utilidades y logging
```

### 💾 Sistema de Almacenamiento Híbrido
- **SQLite (unity_master.db):** Datos del servidor, inventarios, NPCs, relaciones
- **Excel Individual:** Cada personaje tiene su archivo `.xlsx` con estadísticas base
- **Google Sheets (Opcional):** Sincronización en la nube para backup
- **Almacenamiento Local:** Imágenes organizadas por categoría

## 🎯 Mecánicas de Juego

### Sistema de Atributos
| Atributo | Uso Principal | Valor Base |
|----------|---------------|------------|
| **Fuerza** | Combate cuerpo a cuerpo | 10 |
| **Destreza** | Ataques a distancia, precisión | 10 |
| **Velocidad** | Iniciativa, esquives | 10 |
| **Resistencia** | Defensa física | 10 |
| **Inteligencia** | Estrategia, análisis | 10 |
| **Maná** | Hechizos y habilidades mágicas | 10 |

### Fórmula de Tiradas
```
🎲 RESULTADO = D20 + Atributo Base + Bonos de Equipo + Bonus Situacional
```

### Sistema de Salud
- **Todos los personajes:** 10 PG fijos (no escala con nivel)
- **NPCs:** Valores personalizables por tipo

## 🎮 Comandos Principales

### 🎭 Gestión de Personajes

#### `/crear_personaje`
Crea un nuevo personaje con archivo Excel individual.
```
/crear_personaje nombre:Arthas fuerza:15 destreza:12 descripcion:"Paladín caído"
```
**Parámetros:**
- `nombre` (obligatorio): Nombre único del personaje
- `fuerza, destreza, velocidad, resistencia, inteligencia, mana` (opcionales): Stats iniciales
- `descripcion` (opcional): Descripción del personaje
- `imagen` (opcional): Avatar del personaje

#### `/editar_personaje`
Modifica las estadísticas de tu personaje.
```
/editar_personaje personaje:Arthas fuerza:18 mana:14 oro:500
```

#### `/info_personaje`
Muestra información completa con bonos de equipo calculados dinámicamente.
```
/info_personaje personaje:Arthas
```

#### `/borrar_personaje`
Elimina permanentemente un personaje (solo el propietario).
```
/borrar_personaje personaje:Arthas confirmacion:confirmar
```

### 👹 Sistema de NPCs

#### `/crear_npc`
Crea NPCs con valores fijos (no tiran dados).
```
/crear_npc nombre:"Dragón Ancestral" tipo:jefe vida_max:5000 ataque_fisico:80 sincronizado:si cantidad:3
```
**Características especiales:**
- **NPCs Sincronizados:** Múltiples unidades que escalan automáticamente
- **Menús Interactivos:** Selección de acciones mediante Discord UI
- **Gestión de Vida:** Control individual de puntos de vida

#### `/tirada_npc`
Sistema de tiradas para NPCs con menú interactivo.
```
/tirada_npc npc:"Dragón Ancestral"
```

### ✨ Sistema de Items Avanzado

#### `/crear_item`
Crea items equipables con efectos en atributos.
```
/crear_item nombre:"Excalibur" tipo:arma efecto_fuerza:10 efecto_mana:5 rareza:legendario precio:5000
```

#### `/dar_item` (con Búsqueda Fuzzy)
Entrega items a personajes con corrección automática de nombres.
```
/dar_item personaje:Arthas item:excalibur cantidad:1
# ✅ Auto-corrige a "Excalibur" aunque escribas mal
```

### 🎒 Inventario Inteligente

#### `/equipar_menu`
Menú interactivo para gestionar equipamiento con diagnóstico automático.
```
/equipar_menu personaje:Arthas
```
**Características:**
- **Logging Detallado:** Muestra en consola qué items encuentra y por qué
- **Diagnóstico Automático:** Identifica problemas de configuración
- **Vista Previa:** Muestra items equipados vs disponibles

#### `/inventario`
Visualización organizada del inventario completo.
```
/inventario personaje:Arthas
```

### 🎲 Sistema de Tiradas Interactivo

#### `/tirar`
Sistema de tiradas con menús de selección dinámicos.
```
/tirar personaje:Arthas accion:ataque bonificador:2
```
**Tipos de Acción:**
- **Ataque:** Físico (Fuerza), Mágico (Maná), Distancia (Destreza)
- **Defensa:** Esquive (Velocidad), Física (Resistencia), Mágica (Inteligencia)

**Ejemplo de Resultado:**
```
⚔️ Ataque Físico - Arthas
🎲 Crítico Natural!

Dado D20: 🎲 20
Fuerza: 💪 18 (15+3)
Bonificador: ➕ 2
🏆 TOTAL: 40

✨ Bonos de Equipo:
⚔️ Excalibur: +3 Fuerza
```

## 🛠️ Características Técnicas

### 🔍 Sistema de Logging Avanzado
```python
# Logs automáticos en consola para debugging
🔍 [INVENTORY] Buscando items equipables para: 'Arthas'
✅ [INVENTORY] Personaje encontrado: ID=5, Nombre='Arthas'
📦 [INVENTORY] Items encontrados en inventario: 3
  - 'Excalibur' [arma]: equipado=SÍ, equipable=SÍ, cantidad=1, rareza=legendario
⚔️ [INVENTORY] Items equipables filtrados: 2
```

### 🎯 Búsqueda Fuzzy Inteligente
```python
# Encuentra items aunque escribas mal el nombre
/dar_item personaje:Arthas item:espada fuego
🎯 [FUZZY] Coincidencia parcial: 'espada fuego' -> 'Espada de Fuego'
```

### 🔄 Integración con Google Sheets
- Sincronización automática de estadísticas
- Backup en la nube
- Acceso desde cualquier dispositivo

### 📊 Base de Datos Optimizada

#### Tablas Principales:
```sql
personajes     # Metadatos y relaciones
items          # Catálogo de items con efectos
inventarios    # Relación personaje-item con equipamiento
npcs           # NPCs con estadísticas fijas
```

## 🚀 Flujo de Trabajo Típico

### 1️⃣ **Configuración Inicial**
```bash
# Crear personaje con stats personalizadas
/crear_personaje nombre:Kael fuerza:16 destreza:14 mana:12

# Crear items equipables
/crear_item nombre:"Espada Flamígera" tipo:arma efecto_fuerza:5 efecto_mana:2 rareza:raro

# Entregar y equipar items
/dar_item personaje:Kael item:"Espada Flamígera"
/equipar_menu personaje:Kael
```

### 2️⃣ **Durante el Combate**
```bash
# Tirada de ataque del jugador
/tirar personaje:Kael accion:ataque bonificador:3
# Resultado: Total 28 (D20:15 + Fuerza:18 + Bonus:3 + Equipo:2)

# Respuesta del NPC
/tirada_npc npc:"Goblin Chamán"
# Seleccionar: Defensa Mágica
# Resultado fijo: 22 (sin dados)
```

### 3️⃣ **Gestión Post-Combate**
```bash
# Ver inventario completo
/inventario personaje:Kael

# Añadir recompensas
/dar_item personaje:Kael item:"Poción de Maná" cantidad:3

# Actualizar stats por experiencia
/editar_personaje personaje:Kael inteligencia:13 oro:250
```

## 📁 Estructura de Archivos

```
unity_data/
├── personajes/
│   ├── activos/        # Archivos Excel de personajes activos
│   └── archivados/     # Personajes eliminados (backup)
├── imagenes/
│   ├── personajes/     # Avatares de personajes
│   ├── npcs/          # Imágenes de NPCs
│   └── items/         # Imágenes de objetos
├── logs/              # Logs categorizados
│   ├── tiradas/       # Historial de dados
│   └── combates/      # Log de combates
└── unity_master.db    # Base de datos principal
```

## 🔧 Configuración y Desarrollo

### Variables de Entorno
```bash
DISCORD_TOKEN=tu_token_aqui
BOT_NAME=UnityRPG
GUILD_NAME=Nombre_Servidor
GOOGLE_CREDENTIALS_FILE=google-credentials.json  # Opcional
```

### Comando de Desarrollo
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar bot
python main.py
```

## 🛡️ Seguridad y Validaciones

- **Propiedad de Personajes:** Solo el creador puede editar/eliminar
- **Validación de Entrada:** Todos los comandos validan parámetros
- **Logging de Auditoría:** Todas las acciones se registran
- **Manejo de Errores:** Mensajes user-friendly para errores

## 🆕 Nuevas Características (v2.0)

### ✨ Búsqueda Inteligente
- Auto-corrección de nombres de items
- Sugerencias cuando no encuentra coincidencias
- Tolerancia a errores de escritura

### 📊 Diagnóstico Automático
- Detección de problemas en configuración de items
- Logs detallados para debugging
- Información sobre items no equipables

### 🎮 UI Mejorada
- Menús interactivos para NPCs
- Selectores dinámicos para tiradas
- Embeds informativos con estadísticas

### 🔄 Arquitectura Modular
- Separación clara de responsabilidades
- Fácil mantenimiento y extensión
- Reutilización de componentes

## 📝 Notas Importantes

- **Nombres Únicos:** Todos los nombres (personajes, NPCs, items) deben ser únicos
- **Archivos Excel:** Editables manualmente, pero usa comandos para sincronización
- **Imágenes:** Máximo 8MB, formatos PNG/JPG/GIF
- **NPCs Sincronizados:** Las estadísticas se multiplican por la cantidad de unidades
- **Backup Automático:** Personajes eliminados se mueven a carpeta archivados

## 🚀 Comandos de Referencia Rápida

```bash
# 🎭 PERSONAJES
/crear_personaje nombre:Nombre [stats] [descripcion] [imagen]
/editar_personaje personaje:Nombre [nuevos_valores]
/info_personaje personaje:Nombre
/borrar_personaje personaje:Nombre confirmacion:confirmar

# 👹 NPCS  
/crear_npc nombre:Nombre tipo:Tipo [stats] [sincronizado] [cantidad]
/tirada_npc npc:Nombre
/info_npc npc:Nombre

# ✨ ITEMS
/crear_item nombre:Nombre tipo:Tipo [efectos] [rareza] [imagen]
/editar_item item:Nombre [nuevos_valores]

# 🎒 INVENTARIO
/dar_item personaje:Nombre item:Item [cantidad]
/equipar_menu personaje:Nombre
/inventario personaje:Nombre
/quitar_item personaje:Nombre item:Item [cantidad]

# 🎲 TIRADAS
/tirar personaje:Nombre accion:ataque|defensa [bonificador]
```

---

*¡Disfruta tus aventuras en el universo Unity con el sistema más avanzado de RPG por Discord! 🎲⚔️✨*