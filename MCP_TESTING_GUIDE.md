# 🤖 Guía Completa de Testing - Integración MCP Unity RPG Bot

## 📋 **Introducción**

Esta guía te permitirá probar la **primera integración MCP (Model Context Protocol)** para gestión inteligente de bases de datos en un bot de Discord. El sistema permite que Claude analice y repare automáticamente problemas de schema de base de datos.

## 🎯 **¿Qué hace la Integración MCP?**

### **Problema Original:**
- Error: `no such column: i.es_equipable` al usar `/equipar_menu`
- Bases de datos diferentes entre PCs de desarrollo
- Schema desactualizado vs código moderno

### **Solución MCP:**
- ✅ **Análisis inteligente** de schema con Claude
- ✅ **Auto-detección** de columnas faltantes
- ✅ **Reparación automática** con backup
- ✅ **Insights de datos** del juego
- ✅ **Funciona en cualquier PC** sin configuración manual

## 🚀 **Preparación Inicial**

### **1. Actualizar el Código**
```bash
# En tu PC con Windows
git pull origin refactor/modular-architecture
```

### **2. Verificar Archivos Nuevos**
Después del pull deberías tener:
- ✅ `unity_mcp_server.py` (Motor MCP)
- ✅ `unity_rpg_bot/discord_bot/commands/admin_commands.py` (Comandos)
- ✅ `.gitignore` actualizado (Ignora archivos .db)

### **3. Ejecutar el Bot**
```bash
python main.py
```

**Verifica en la consola:**
```
✅ Base de datos inicializada correctamente
🎮 Todos los comandos modulares registrados exitosamente  
📡 XX comandos sincronizados  # Debe incluir los nuevos comandos admin
```

## 🧪 **Escenarios de Testing**

### **Escenario 1: Problema de Schema Existente** ⭐ (Más probable)

**Si ya tienes el error `es_equipable`:**

#### **Paso 1: Confirmar el Problema**
```bash
# En Discord:
/equipar_menu personaje:TuPersonaje
```
**Resultado esperado:** Error `no such column: i.es_equipable`

#### **Paso 2: Análisis MCP**
```bash
# En Discord (como admin):
/admin_db_analyze
```

**Resultado esperado:**
```
🤖 Análisis de Base de Datos (MCP)
📊 Estado General
✅ Tablas: X
⚠️ Problemas: 1+
🎮 Personajes: X

🔍 Problemas Detectados  
🔧 Auto-reparable: Columna 'es_equipable' faltante en tabla items
```

#### **Paso 3: Reparación Automática**
- **Opción A:** Clic en botón "🔧 Aplicar Correcciones Automáticas"
- **Opción B:** Comando `/admin_db_fix`

**Resultado esperado:**
```
🎉 Correcciones Aplicadas Exitosamente
✅ Añadida columna es_equipable a tabla items
💾 Backup: unity_master_backup_mcp_YYYYMMDD_HHMMSS.db
¡Ahora puedes usar /equipar_menu sin problemas!
```

#### **Paso 4: Verificar Solución**
```bash
# En Discord:
/equipar_menu personaje:TuPersonaje
```
**Resultado esperado:** ✅ Menú de equipamiento funciona correctamente

---

### **Escenario 2: Base de Datos Limpia/Nueva** 

**Si no tienes problemas de schema:**

#### **Paso 1: Análisis MCP**
```bash
/admin_db_analyze
```

**Resultado esperado:**
```
✅ Base de Datos Correcta
📊 Estado General
✅ Tablas: X
⚠️ Problemas: 0
```

#### **Paso 2: Ver Insights de Datos**
El comando también mostrará:
```
📈 Insights de IA
💡 Solo X% de los items están equipados
💡 Hay más items legendarios que comunes
```

---

### **Escenario 3: Simulación de Problema** 🧪

**Para probar la funcionalidad completa:**

#### **Paso 1: Crear Problema Artificial**
```bash
# Ejecuta esto en tu PC (comando directo Python):
python -c "
import sqlite3
conn = sqlite3.connect('unity_data/unity_master.db')
conn.execute('ALTER TABLE items DROP COLUMN es_equipable')
conn.commit()
print('Problema artificial creado')
"
```

#### **Paso 2: Reproducir Error**
```bash
/equipar_menu personaje:Cualquiera
```
**Debe fallar** con `no such column: i.es_equipable`

#### **Paso 3: Diagnóstico y Reparación**
```bash
/admin_db_analyze  # Detecta el problema
# Clic en botón de reparar
```

#### **Paso 4: Verificación**
```bash
/equipar_menu personaje:Cualquiera  # Debe funcionar
```

## 🔍 **Comandos de Testing Disponibles**

### **Comandos Admin (Requieren permisos de administrador)**

#### **`/admin_db_analyze`**
- **Función:** Análisis completo de base de datos con IA
- **Output:** Estado de schema, problemas, insights de datos
- **UI:** Embed interactivo con botón de reparación

#### **`/admin_db_fix`**
- **Función:** Aplica correcciones automáticas
- **Incluye:** Backup automático antes de modificar
- **Output:** Reporte detallado de cambios aplicados

### **Comandos de Inventario (Para verificar funcionamiento)**

#### **`/crear_item`**
```bash
/crear_item nombre:"Item Test" tipo:arma efecto_fuerza:5 rareza:raro
```

#### **`/dar_item`**
```bash
/dar_item personaje:TuPersonaje item:"Item Test" cantidad:1
```

#### **`/equipar_menu`** ⭐ (Comando objetivo)
```bash
/equipar_menu personaje:TuPersonaje
```

#### **`/inventario`**
```bash
/inventario personaje:TuPersonaje
```

## 📊 **Verificaciones de Funcionalidad**

### **1. Logs de Consola**
Busca en la consola del bot:
```
🔍 [INVENTORY] Buscando items equipables para: 'NombrePersonaje'
✅ [INVENTORY] Personaje encontrado: ID=X, Nombre='NombrePersonaje'  
📦 [INVENTORY] Items encontrados en inventario: X
⚔️ [INVENTORY] Items equipables filtrados: X
```

### **2. Funcionamiento del Menú**
El comando `/equipar_menu` debe mostrar:
- ✅ Embed con título "🎒 Equipar Items - [Personaje]"
- ✅ Menú desplegable con items
- ✅ Estado actual: ✅ Equipado / ⚪ No equipado

### **3. Archivos de Backup**
Después de usar `/admin_db_fix`, verifica que existe:
```
unity_data/unity_master_backup_mcp_YYYYMMDD_HHMMSS.db
```

## 🚨 **Resolución de Problemas**

### **Error: "Solo los administradores pueden usar este comando"**
- **Causa:** No tienes permisos de administrador en el servidor
- **Solución:** Pide permisos admin o usa una cuenta con permisos

### **Error: "ModuleNotFoundError: No module named 'unity_mcp_server'"**
- **Causa:** El archivo no se descargó correctamente
- **Solución:** Verificar que `unity_mcp_server.py` existe en la raíz del proyecto

### **Error: "Base de datos no encontrada"**
- **Causa:** El bot no se ha ejecutado nunca
- **Solución:** Ejecutar `python main.py` para crear la DB inicial

### **El comando MCP no detecta problemas pero `/equipar_menu` falla**
- **Causa:** Problema no contemplado en el MCP actual
- **Solución:** Revisar logs de consola para error específico

## 🎯 **Casos de Éxito Esperados**

### **Flujo Completo Exitoso:**
1. ✅ Pull del código actualizado
2. ✅ Ejecutar bot sin errores  
3. ✅ `/admin_db_analyze` detecta problema `es_equipable`
4. ✅ Reparación automática con backup
5. ✅ `/equipar_menu` funciona perfectamente
6. ✅ Logs detallados en consola muestran proceso completo

### **Métricas de Éxito:**
- **Performance:** Análisis MCP completo en <5 segundos
- **Precision:** 100% detección de problemas de schema conocidos
- **Safety:** Backup automático antes de cualquier modificación
- **UX:** UI interactiva en Discord sin necesidad de comandos manuales

## 🔄 **Testing Repetitivo**

### **Para Probar Múltiples Veces:**
```bash
# 1. Simular problema
python -c "import sqlite3; conn = sqlite3.connect('unity_data/unity_master.db'); conn.execute('ALTER TABLE items DROP COLUMN es_equipable'); conn.commit()"

# 2. Probar detección
/admin_db_analyze

# 3. Probar reparación  
/admin_db_fix

# 4. Verificar funcionamiento
/equipar_menu personaje:Test
```

## 🤖 **Características Únicas de esta Implementación**

### **Primero en su Clase:**
- ✅ **Primera integración MCP** en un bot de Discord
- ✅ **Auto-diagnóstico** de problemas de base de datos
- ✅ **Reparación inteligente** sin intervención manual
- ✅ **Funciona cross-platform** (Windows/macOS/Linux)

### **Tecnología Avanzada:**
- ✅ **Claude como DBA virtual** analizando schema
- ✅ **Backup automático** antes de modificaciones
- ✅ **UI nativa de Discord** para interacción
- ✅ **Logging categorizado** para debugging

## 📝 **Reporte de Testing**

### **Template de Reporte:**
```
🧪 REPORTE DE TESTING MCP - Unity RPG Bot

Fecha: [FECHA]
PC: [Windows/macOS/Linux]
Problema Original: [SÍ/NO] - ¿Tenías error es_equipable?

Resultados:
✅/❌ Pull del código exitoso
✅/❌ Bot inicia sin errores  
✅/❌ /admin_db_analyze detecta problemas
✅/❌ Reparación automática funciona
✅/❌ /equipar_menu funciona después
✅/❌ Backup creado correctamente

Observaciones:
[Cualquier comportamiento inesperado, errores, o sugerencias]

Performance:
- Tiempo análisis MCP: [X segundos]
- Tiempo reparación: [X segundos]
- Comandos totales sincronizados: [X]
```

---

## 🎉 **¡Listo para Probar!**

Esta integración MCP representa un **avance significativo** en la automatización de mantenimiento de bases de datos para bots de Discord. ¡Pruébala y reporta tus resultados!

**¿Problemas o preguntas?** Comparte los logs de consola y el comportamiento observado.