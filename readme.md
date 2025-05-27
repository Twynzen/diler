# 🎲 Manual de Usuario - Unity RPG Bot

## 📋 Introducción

El **Unity RPG Bot** es tu compañero para partidas de roleplay narrativo con sistema de dados D20. Maneja automáticamente las estadísticas de tus personajes, calcula tiradas y gestiona NPCs del universo Unity.

## 🎯 Conceptos Básicos

### Sistema de Dados
- **Fórmula:** `D20 + Atributo + Bonificadores + Crecimiento`
- **Crítico:** Dado = 20 (éxito automático)
- **Pifia:** Dado = 1 (fallo automático)

### Atributos del Personaje
| Atributo | Uso |
|----------|-----|
| **Fuerza** | Combate cuerpo a cuerpo, cargas |
| **Destreza** | Ataques a distancia, precisión |
| **Velocidad** | Iniciativa, movimientos rápidos |
| **Inteligencia** | Estrategia, análisis, fabricación |
| **Maná** | Hechizos y habilidades mágicas |
| **Crecimiento** | Bonus de experiencia acumulada |

### Tipos de Defensa
- **Esquive:** Evadir ataques con agilidad
- **Física:** Resistir/bloquear daño físico  
- **Mágica:** Resistir efectos mágicos

---

## 🎭 Gestión de Personajes

### ➕ Registrar Personaje Nuevo
```
/registrar_personaje nombre:Kael
```
- Crea automáticamente archivo Excel con stats base
- Valores iniciales: todos los atributos en 10, crecimiento en 0
- El personaje queda vinculado a tu usuario de Discord

### 📊 Ver Estadísticas
```
/stats personaje:Kael
```
- Muestra todos los atributos y defensas
- Formato: `Total (Base+Bonus)`
- Ejemplo: `Fuerza: 18 (15+3)`

### 🎭 Listar Tus Personajes
```
/mis_personajes
```
- Muestra todos los personajes registrados por ti
- Ordenados por uso más reciente

### ✏️ Editar Estadísticas
```
/editar_stats personaje:Kael atributo:fuerza nuevo_valor:15 bonificador:3
```
- Modifica el valor base y bonificador de cualquier atributo
- Los cambios se guardan automáticamente en Excel

---

## 🎲 Sistema de Tiradas

### ⚔️ Tirada de Ataque/Acción
```
/tirar personaje:Kael atributo:fuerza bonificador:2
```

**Parámetros:**
- `personaje`: Nombre exacto del personaje
- `atributo`: fuerza, destreza, velocidad, inteligencia, mana
- `bonificador`: Bonus extra (opcional, por defecto 0)

**Ejemplo de Resultado:**
```
🎲 Tirada de Kael
✅ Éxito

Dado D20: 🎲 15
Fuerza: 📊 18  
Bonificador: ➕ 2
Crecimiento: 📈 3
🏆 TOTAL: 38
```

### 🛡️ Tirada de Defensa
```
/defensa personaje:Kael tipo_defensa:esquive bonificador:1
```

**Tipos de Defensa:**
- `esquive`: Usar Defensa_Esquive
- `fisica`: Usar Defensa_Fisica  
- `magica`: Usar Defensa_Magica

**Ejemplo de Resultado:**
```
🛡️ Defensa Esquive - Kael
✅ Éxito

Dado D20: 🎲 12
Defensa Esquive: 🛡️ 14
Bonificador: ➕ 1  
Crecimiento: 📈 3
🏆 TOTAL DEFENSA: 30
```

---

## 👹 NPCs y Monstruos

### 📖 Ver Estadísticas de NPC
```
/npc_stats nombre:Chancho Verde
```
- Muestra las estadísticas fijas del NPC
- Los NPCs NO tiran dados, tienen valores fijos

### ➕ Crear NPC Personalizado
```
/crear_npc nombre:Dragon Rojo tipo:dragon ataque_fisico:25 defensa_fisica:20 velocidad:15 defensa_magica:30 ataque_mana:20
```

### 📋 NPCs Incluidos por Defecto
- **Chancho Verde** - Criatura común (AT:12, DF:15, VE:10, DM:20, AM:0)
- **Lobo Gris** - Bestia rápida (AT:15, DF:12, VE:18, DM:8, AM:0)  
- **Esqueleto Guerrero** - No-muerto resistente (AT:14, DF:16, VE:8, DM:25, AM:5)
- **Goblin Explorador** - Humanoide ágil (AT:10, DF:8, VE:20, DM:6, AM:3)

---

## 🎮 Flujo de Juego Típico

### 1️⃣ **Preparación**
```
/registrar_personaje nombre:MiPersonaje
/editar_stats personaje:MiPersonaje atributo:fuerza nuevo_valor:16
/stats personaje:MiPersonaje
```

### 2️⃣ **Durante el Combate**
```
Jugador: "Kael ataca con su espada al chancho verde"
/tirar personaje:Kael atributo:fuerza bonificador:3

Narrador: "El chancho verde esquiva"  
/defensa personaje:Chancho Verde tipo_defensa:esquive
```

### 3️⃣ **Comparar Resultados**
- **Ataque: 23** vs **Defensa: 18** = ✅ **Impacta**
- **Ataque: 15** vs **Defensa: 20** = ❌ **Falla**

---

## 🔄 Integración con TupperBox

Si usas **TupperBox** para múltiples personajes:

1. El bot detecta automáticamente mensajes de webhooks
2. Auto-registra personajes nuevos basándose en el nombre del webhook
3. Puedes usar los comandos normalmente con el nombre del personaje

**Ejemplo:**
- Webhook configurado como "Lyra Nightshade"
- Bot detecta y auto-registra a "Lyra Nightshade"
- Usar: `/tirar personaje:Lyra Nightshade atributo:destreza`

---

## 📊 Interpretación de Resultados

### 🎯 Escalas de Éxito
| Total | Resultado |
|-------|-----------|
| **20** (Dado) | 🎯 **CRÍTICO** - Éxito espectacular |
| **1** (Dado) | 💥 **PIFIA** - Fallo crítico |
| **18+** | ⭐ **Éxito Notable** |
| **15-17** | ✅ **Éxito** |
| **12-14** | 🔶 **Éxito Parcial** |
| **11-** | ❌ **Fallo** |

### 💡 Consejos para Narradores
- Los NPCs tienen stats **fijos** - no tiran dados
- Compara la tirada del jugador vs el valor fijo del NPC
- Los bonificadores pueden representar: armas, habilidades, situación táctica
- El "Crecimiento" refleja la experiencia acumulada del personaje

---

## 🛠️ Datos y Archivos

### 📁 Almacenamiento Automático
- **Excel individual** por cada personaje en `unity_data/personajes/`
- **Base de datos SQLite** para NPCs y historial de tiradas
- **Logs automáticos** de todas las acciones

### 🔄 Respaldo de Datos
- Los archivos Excel son compatibles con cualquier programa de hojas de cálculo
- La base de datos SQLite puede exportarse fácilmente
- Todo se guarda automáticamente tras cada acción

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo tener múltiples personajes?**  
R: Sí, usa `/registrar_personaje` para cada uno.

**P: ¿Los NPCs pueden subir de nivel?**  
R: No, tienen estadísticas fijas. Solo los personajes de jugadores evolucionan.

**P: ¿Puedo editar las stats en el Excel directamente?**  
R: Sí, pero usa `/editar_stats` para que el bot se mantenga sincronizado.

**P: ¿Qué pasa si borro un archivo Excel?**  
R: Usa `/registrar_personaje` otra vez para recrearlo con valores base.

**P: ¿El bot guarda el historial de tiradas?**  
R: Sí, todas las tiradas se registran en la base de datos interna.

---

## 🚀 Comandos Rápidos

```bash
# Gestión de personajes
/registrar_personaje nombre:NombrePersonaje
/mis_personajes
/stats personaje:NombrePersonaje
/editar_stats personaje:Nombre atributo:fuerza nuevo_valor:15

# Tiradas
/tirar personaje:Nombre atributo:fuerza bonificador:2
/defensa personaje:Nombre tipo_defensa:esquive bonificador:1

# NPCs
/npc_stats nombre:Chancho Verde
/crear_npc nombre:MiMonstruo tipo:bestia ataque_fisico:20 defensa_fisica:15
```

---

*¡Que tengas excelentes aventuras en el universo Unity! 🎲⚔️*