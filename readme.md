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



📚 MANUAL DE COMANDOS - UNITY RPG BOT
🎭 COMANDOS DE PERSONAJES
/crear_personaje
Descripción: Crea un nuevo personaje jugador
Parámetros:

nombre (obligatorio): Nombre único del personaje
fuerza (opcional, default: 10): Estadística de fuerza
destreza (opcional, default: 10): Estadística de destreza
velocidad (opcional, default: 10): Estadística de velocidad
inteligencia (opcional, default: 10): Estadística de inteligencia
mana (opcional, default: 10): Estadística de maná
def_esquive (opcional, default: 10): Defensa por esquive
def_fisica (opcional, default: 10): Defensa física
def_magica (opcional, default: 10): Defensa mágica
descripcion (opcional): Descripción del personaje
imagen (opcional): Adjuntar imagen del personaje

Ejemplo: /crear_personaje nombre:Arthas fuerza:15 inteligencia:12 descripcion:"Paladín caído"

/editar_personaje 🆕
Descripción: Edita las estadísticas de tu personaje
Parámetros:

personaje (obligatorio): Nombre del personaje a editar
fuerza, destreza, velocidad, inteligencia, mana (opcionales): Nuevos valores
def_esquive, def_fisica, def_magica (opcionales): Nuevas defensas
oro (opcional): Nuevo valor de oro
vida_actual, vida_max (opcionales): Modificar puntos de vida

Ejemplo: /editar_personaje personaje:Arthas fuerza:20 oro:500

/info_personaje
Descripción: Muestra información completa del personaje
Parámetros:

personaje (obligatorio): Nombre del personaje

Ejemplo: /info_personaje personaje:Arthas

/eliminar_personaje
Descripción: Elimina permanentemente un personaje
Parámetros:

personaje (obligatorio): Nombre del personaje
confirmacion (obligatorio): Escribe "confirmar" para proceder

Ejemplo: /eliminar_personaje personaje:Arthas confirmacion:confirmar

👹 COMANDOS DE NPCS
/crear_npc
Descripción: Crea un NPC (Non-Player Character)
Parámetros:

nombre (obligatorio): Nombre único del NPC
tipo (obligatorio): Tipo de NPC (enemigo, aliado, mercader, etc.)
nivel (opcional, default: 1): Nivel del NPC
vida_max (opcional, default: 100): Puntos de vida máximos
ataque_fisico, ataque_magico (opcionales, default: 10): Poder de ataque
defensa_fisica, defensa_magica, defensa_esquive (opcionales, default: 10): Defensas
velocidad, inteligencia (opcionales, default: 10): Estadísticas adicionales
descripcion (opcional): Descripción del NPC
imagen (opcional): Adjuntar imagen del NPC

Ejemplo: /crear_npc nombre:"Dragón Rojo" tipo:jefe nivel:50 vida_max:5000 ataque_fisico:80

/editar_npc 🆕
Descripción: Edita las estadísticas de un NPC
Parámetros:

npc (obligatorio): Nombre del NPC a editar
Todos los demás parámetros son opcionales y sobrescriben los valores actuales

Ejemplo: /editar_npc npc:"Dragón Rojo" nivel:55 ataque_magico:100

/vida_npc
Descripción: Modifica los puntos de vida actuales de un NPC
Parámetros:

npc (obligatorio): Nombre del NPC
nueva_vida (obligatorio): Nuevo valor de vida actual

Ejemplo: /vida_npc npc:"Dragón Rojo" nueva_vida:3500

✨ COMANDOS DE ITEMS
/crear_item
Descripción: Crea un nuevo item equipable
Parámetros:

nombre (obligatorio): Nombre único del item
tipo (obligatorio): Tipo de item (arma, armadura, accesorio, etc.)
descripcion (opcional): Descripción del item
efecto_fuerza, efecto_destreza, etc. (opcionales, default: 0): Bonificaciones que otorga
rareza (opcional, default: "comun"): Rareza (comun, raro, epico, legendario)
precio (opcional, default: 0): Precio en oro
imagen (opcional): Adjuntar imagen del item

Ejemplo: /crear_item nombre:"Excalibur" tipo:arma efecto_fuerza:10 rareza:legendario precio:5000

/editar_item 🆕
Descripción: Edita las propiedades de un item existente
Parámetros:

item (obligatorio): Nombre del item a editar
Todos los demás parámetros son opcionales

Ejemplo: /editar_item item:Excalibur efecto_fuerza:15 precio:7500

🎒 COMANDOS DE INVENTARIO
/dar_item
Descripción: Entrega un item a un personaje
Parámetros:

personaje (obligatorio): Nombre del personaje receptor
item (obligatorio): Nombre del item a entregar
cantidad (opcional, default: 1): Cantidad a entregar

Ejemplo: /dar_item personaje:Arthas item:Excalibur cantidad:1

/inventario
Descripción: Muestra todos los items de un personaje
Parámetros:

personaje (obligatorio): Nombre del personaje

Ejemplo: /inventario personaje:Arthas

/equipar
Descripción: Equipa o desequipa un item del inventario
Parámetros:

personaje (obligatorio): Nombre del personaje
item (obligatorio): Nombre del item a equipar/desequipar

Ejemplo: /equipar personaje:Arthas item:Excalibur

/quitar_item
Descripción: Elimina un item del inventario
Parámetros:

personaje (obligatorio): Nombre del personaje
item (obligatorio): Nombre del item a quitar
cantidad (opcional, default: 1): Cantidad a quitar

Ejemplo: /quitar_item personaje:Arthas item:"Poción de Vida" cantidad:5

🎲 COMANDOS DE TIRADAS
/tirar
Descripción: Sistema de tiradas con dados D20 + modificadores
Parámetros:

personaje (obligatorio): Nombre del personaje que realiza la tirada
accion (obligatorio): Tipo de acción ("ataque" o "defensa")
bonificador (opcional, default: 0): Bonificador adicional a la tirada

Funcionamiento:

Ataque: Aparece un menú para elegir entre:

Físico (usa Fuerza)
Mágico (usa Maná)
Distancia (usa Destreza)


Defensa: Aparece un menú para elegir entre:

Esquive (usa Def. Esquive)
Física (usa Def. Física)
Mágica (usa Def. Mágica)



Ejemplo: /tirar personaje:Arthas accion:ataque bonificador:2

🔧 CARACTERÍSTICAS ESPECIALES
📸 Sistema de Imágenes

Todos los comandos de creación (crear_personaje, crear_npc, crear_item) aceptan imágenes adjuntas
Las imágenes se guardan localmente y se muestran en los embeds de Discord
Formatos soportados: PNG, JPG, GIF

📊 Sistema de Estadísticas

Las estadísticas base se guardan en archivos Excel individuales
Los bonuses de items equipados se calculan automáticamente
Sincronización opcional con Google Sheets

🎯 Sistema de Dados

Tiradas con D20 + modificadores
Críticos (20 natural) y pifias (1 natural)
Los items equipados afectan automáticamente las tiradas

💾 Persistencia de Datos

Base de datos SQLite para almacenamiento permanente
Archivos Excel para estadísticas de personajes
Sistema de respaldo automático

🛡️ Seguridad

Solo el creador puede editar/eliminar sus personajes
Validación de datos en todos los comandos
Sistema de logs para auditoría

📝 NOTAS IMPORTANTES

Nombres únicos: Todos los nombres (personajes, NPCs, items) deben ser únicos
Permisos: Solo puedes editar/eliminar tus propios personajes
Items equipados: Los bonuses se aplican automáticamente a las tiradas
Imágenes: Se recomienda usar imágenes de menos de 8MB
Respaldos: El bot crea respaldos automáticos de los datos

🚀 INICIO RÁPIDO

Crea tu personaje: /crear_personaje nombre:TuNombre
Crea algunos items: /crear_item nombre:"Espada Inicial" tipo:arma efecto_fuerza:2
Dale items a tu personaje: /dar_item personaje:TuNombre item:"Espada Inicial"
Equipa el item: /equipar personaje:TuNombre item:"Espada Inicial"
¡Haz una tirada de ataque!: /tirar personaje:TuNombre accion:ataque

¡Disfruta tu aventura en Unity RPG! 🎮