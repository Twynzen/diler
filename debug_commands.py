#!/usr/bin/env python3
"""
Script de debugging para verificar comandos y base de datos Unity RPG Bot
"""
import sqlite3
import os
from datetime import datetime

def check_database():
    """Verifica el estado de la base de datos"""
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
    print("=" * 50)
    
    db_path = "unity_data/unity_master.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de datos NO EXISTE")
        print(f"   Ruta esperada: {db_path}")
        print("💡 Solución: Ejecutar 'python main.py' para crear la DB")
        return False
    
    print(f"✅ Base de datos existe: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table}")
        
        # Verificar tabla items específicamente
        if 'items' in tables:
            cursor.execute("PRAGMA table_info(items)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"\n🗂️  Tabla 'items' - {len(columns)} columnas:")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Verificar la columna problemática
            if 'es_equipable' in column_names:
                print("\n✅ Columna 'es_equipable' EXISTE")
                
                # Contar items equipables
                cursor.execute("SELECT COUNT(*) FROM items WHERE es_equipable = TRUE")
                equipable_count = cursor.fetchone()[0]
                print(f"   Items equipables: {equipable_count}")
            else:
                print("\n❌ Columna 'es_equipable' NO EXISTE - Este es el problema!")
                return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error accediendo a la base de datos: {e}")
        return False

def reset_database():
    """Resetea completamente la base de datos"""
    print("\n🔄 RESET DE BASE DE DATOS")
    print("=" * 50)
    
    db_path = "unity_data/unity_master.db"
    
    if os.path.exists(db_path):
        # Crear backup antes de eliminar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"unity_data/unity_master_backup_reset_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Backup creado: {backup_path}")
        except Exception as e:
            print(f"⚠️ Error creando backup: {e}")
        
        # Eliminar base de datos actual
        try:
            os.remove(db_path)
            print(f"🗑️ Base de datos eliminada: {db_path}")
        except Exception as e:
            print(f"❌ Error eliminando DB: {e}")
            return False
    
    print("✅ Base de datos reseteada")
    print("💡 Ejecuta 'python main.py' para crear una nueva DB limpia")
    return True

def fix_es_equipable():
    """Arregla específicamente el problema de es_equipable"""
    print("\n🔧 ARREGLO DE COLUMNA es_equipable")
    print("=" * 50)
    
    db_path = "unity_data/unity_master.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no existe")
        return False
    
    try:
        # Crear backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"unity_data/unity_master_backup_fix_{timestamp}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup creado: {backup_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna existe
        cursor.execute("PRAGMA table_info(items)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'es_equipable' not in column_names:
            print("🔧 Añadiendo columna 'es_equipable'...")
            cursor.execute("ALTER TABLE items ADD COLUMN es_equipable BOOLEAN DEFAULT TRUE")
            cursor.execute("UPDATE items SET es_equipable = TRUE WHERE es_equipable IS NULL")
            
            # Verificar cuántos items se actualizaron
            cursor.execute("SELECT COUNT(*) FROM items")
            total_items = cursor.fetchone()[0]
            
            conn.commit()
            print(f"✅ Columna añadida exitosamente")
            print(f"📊 {total_items} items marcados como equipables")
        else:
            print("✅ Columna 'es_equipable' ya existe")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error arreglando columna: {e}")
        return False

def test_equipar_menu_query():
    """Prueba la query específica que falla en /equipar_menu"""
    print("\n🧪 TEST DE QUERY /equipar_menu")
    print("=" * 50)
    
    db_path = "unity_data/unity_master.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no existe")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # La query problemática del comando /equipar_menu
        test_query = """
            SELECT i.nombre, inv.equipado, i.rareza, i.es_equipable, inv.cantidad, i.tipo
            FROM inventarios inv
            JOIN items i ON inv.item_id = i.id
            JOIN personajes p ON inv.personaje_id = p.id
            WHERE p.nombre = ? AND inv.cantidad > 0
            ORDER BY i.es_equipable DESC, inv.equipado DESC, i.nombre
        """
        
        # Buscar un personaje para probar
        cursor.execute("SELECT nombre FROM personajes LIMIT 1")
        personaje_result = cursor.fetchone()
        
        if not personaje_result:
            print("❌ No hay personajes en la base de datos")
            print("💡 Crea un personaje primero con /crear_personaje")
            return False
        
        personaje_nombre = personaje_result[0]
        print(f"🎭 Probando con personaje: {personaje_nombre}")
        
        # Ejecutar la query problemática
        cursor.execute(test_query, (personaje_nombre,))
        results = cursor.fetchall()
        
        print(f"✅ Query ejecutada exitosamente")
        print(f"📦 Items encontrados en inventario: {len(results)}")
        
        if results:
            print("📋 Items encontrados:")
            for item in results:
                nombre, equipado, rareza, es_equipable, cantidad, tipo = item
                print(f"   - {nombre}: equipado={equipado}, equipable={es_equipable}, cantidad={cantidad}")
        else:
            print("📭 Inventario vacío para este personaje")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando query: {e}")
        print("🔍 Este es probablemente el error que ves en /equipar_menu")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🤖 UNITY RPG BOT - DIAGNÓSTICO Y REPARACIÓN")
    print("=" * 60)
    
    # Verificar base de datos
    db_ok = check_database()
    
    if not db_ok:
        print("\n🔧 OPCIONES DE REPARACIÓN:")
        print("1. Resetear completamente la base de datos")
        print("2. Intentar arreglar la columna es_equipable")
        print("3. Salir")
        
        choice = input("\nElige una opción (1/2/3): ").strip()
        
        if choice == "1":
            if reset_database():
                print("\n✅ Base de datos reseteada. Ejecuta 'python main.py' para crear una nueva.")
        elif choice == "2":
            fix_es_equipable()
        elif choice == "3":
            print("👋 Saliendo...")
        else:
            print("❌ Opción no válida")
    else:
        # Si la DB está bien, probar la query
        test_equipar_menu_query()
    
    print("\n" + "=" * 60)
    print("🏁 Diagnóstico completado")

if __name__ == "__main__":
    main()