#!/usr/bin/env python3
"""
Unity RPG Bot - MCP Server para gestión inteligente de base de datos
Integración con Claude para análisis y resolución automática de problemas de DB
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio

class UnityMCPDatabaseManager:
    """
    Servidor MCP para gestión inteligente de la base de datos Unity RPG
    Soluciona problemas de schema, analiza datos y proporciona insights
    """
    
    def __init__(self, db_path: str = "unity_data/unity_master.db"):
        self.db_path = db_path
        self.schema_version = "2.0"  # Versión actual esperada
        
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    # ============= ANÁLISIS DE SCHEMA =============
    
    def analyze_database_schema(self) -> Dict[str, Any]:
        """
        Analiza el schema actual vs el esperado
        Retorna análisis completo para Claude
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "database_path": self.db_path,
            "database_exists": os.path.exists(self.db_path),
            "tables": {},
            "issues": [],
            "recommendations": []
        }
        
        if not analysis["database_exists"]:
            analysis["issues"].append({
                "type": "critical",
                "message": "Base de datos no existe",
                "solution": "Ejecutar el bot para crear la estructura inicial"
            })
            return analysis
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Analizar todas las tablas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = [row[0] for row in cursor.fetchall()]
                
                for table_name in table_names:
                    analysis["tables"][table_name] = self._analyze_table(cursor, table_name)
                
                # Verificar problemas específicos conocidos
                self._check_known_issues(cursor, analysis)
                
        except Exception as e:
            analysis["issues"].append({
                "type": "error",
                "message": f"Error accediendo a la base de datos: {str(e)}",
                "solution": "Verificar permisos y integridad del archivo"
            })
            
        return analysis
    
    def _analyze_table(self, cursor: sqlite3.Cursor, table_name: str) -> Dict[str, Any]:
        """Analiza una tabla específica"""
        table_info = {
            "columns": [],
            "row_count": 0,
            "issues": []
        }
        
        try:
            # Obtener estructura de columnas
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            table_info["columns"] = [
                {
                    "name": col[1],
                    "type": col[2], 
                    "not_null": bool(col[3]),
                    "default": col[4],
                    "primary_key": bool(col[5])
                }
                for col in columns
            ]
            
            # Contar filas
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            table_info["row_count"] = cursor.fetchone()[0]
            
        except Exception as e:
            table_info["issues"].append(f"Error analizando tabla: {str(e)}")
            
        return table_info
    
    def _check_known_issues(self, cursor: sqlite3.Cursor, analysis: Dict[str, Any]):
        """Verifica problemas conocidos específicos"""
        
        # Problema 1: Columna es_equipable faltante en items
        if "items" in analysis["tables"]:
            items_columns = [col["name"] for col in analysis["tables"]["items"]["columns"]]
            
            if "es_equipable" not in items_columns:
                analysis["issues"].append({
                    "type": "schema_missing_column",
                    "table": "items",
                    "column": "es_equipable",
                    "message": "Columna 'es_equipable' faltante en tabla items",
                    "impact": "El sistema de equipamiento no funciona",
                    "solution": "ALTER TABLE items ADD COLUMN es_equipable BOOLEAN DEFAULT TRUE",
                    "auto_fixable": True
                })
            
            if "slot_equipo" not in items_columns:
                analysis["issues"].append({
                    "type": "schema_missing_column", 
                    "table": "items",
                    "column": "slot_equipo",
                    "message": "Columna 'slot_equipo' faltante en tabla items",
                    "impact": "Sistema de slots de equipamiento limitado",
                    "solution": "ALTER TABLE items ADD COLUMN slot_equipo TEXT DEFAULT 'general'",
                    "auto_fixable": True
                })
        
        # Problema 2: Verificar integridad de datos
        try:
            cursor.execute("SELECT COUNT(*) FROM items WHERE es_equipable IS NULL")
            null_equipable = cursor.fetchone()[0]
            if null_equipable > 0:
                analysis["issues"].append({
                    "type": "data_integrity",
                    "table": "items", 
                    "message": f"{null_equipable} items tienen es_equipable = NULL",
                    "solution": "UPDATE items SET es_equipable = TRUE WHERE es_equipable IS NULL",
                    "auto_fixable": True
                })
        except:
            pass  # La columna no existe, ya lo detectamos arriba
    
    # ============= AUTO-REPARACIÓN =============
    
    def auto_fix_schema_issues(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica correcciones automáticas basadas en el análisis
        Retorna reporte de cambios aplicados
        """
        fix_report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": [],
            "errors": [],
            "backup_created": False
        }
        
        # Crear backup antes de modificar
        backup_path = self._create_backup()
        if backup_path:
            fix_report["backup_created"] = backup_path
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Aplicar correcciones automáticas
                for issue in analysis["issues"]:
                    if issue.get("auto_fixable", False):
                        try:
                            if issue["type"] == "schema_missing_column":
                                cursor.execute(issue["solution"])
                                fix_report["fixes_applied"].append({
                                    "type": issue["type"],
                                    "description": f"Añadida columna {issue['column']} a tabla {issue['table']}",
                                    "sql": issue["solution"]
                                })
                                
                            elif issue["type"] == "data_integrity":
                                cursor.execute(issue["solution"])
                                fix_report["fixes_applied"].append({
                                    "type": issue["type"],
                                    "description": issue["message"],
                                    "sql": issue["solution"]
                                })
                                
                        except Exception as e:
                            fix_report["errors"].append({
                                "issue": issue,
                                "error": str(e)
                            })
                
                conn.commit()
                
        except Exception as e:
            fix_report["errors"].append({
                "type": "general",
                "error": str(e)
            })
        
        return fix_report
    
    def _create_backup(self) -> Optional[str]:
        """Crea backup de la base de datos antes de modificar"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"unity_data/unity_master_backup_mcp_{timestamp}.db"
            
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creando backup: {e}")
            return None
    
    # ============= ANÁLISIS DE DATOS =============
    
    def analyze_game_data(self) -> Dict[str, Any]:
        """
        Analiza los datos del juego para insights
        Perfecto para que Claude proporcione recomendaciones
        """
        data_analysis = {
            "timestamp": datetime.now().isoformat(),
            "characters": {"count": 0, "stats": {}, "issues": []},
            "items": {"count": 0, "equipable_count": 0, "rarity_distribution": {}},
            "npcs": {"count": 0, "types": {}},
            "inventory": {"total_items": 0, "equipped_items": 0},
            "insights": []
        }
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Analizar personajes
                cursor.execute("SELECT COUNT(*) FROM personajes WHERE estado = 'activo'")
                data_analysis["characters"]["count"] = cursor.fetchone()[0]
                
                # Analizar items
                cursor.execute("SELECT COUNT(*) FROM items")
                data_analysis["items"]["count"] = cursor.fetchone()[0]
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM items WHERE es_equipable = TRUE")
                    data_analysis["items"]["equipable_count"] = cursor.fetchone()[0]
                except:
                    data_analysis["items"]["equipable_count"] = "N/A (columna faltante)"
                
                # Distribución de rareza
                cursor.execute("SELECT rareza, COUNT(*) FROM items GROUP BY rareza")
                data_analysis["items"]["rarity_distribution"] = dict(cursor.fetchall())
                
                # Analizar NPCs
                cursor.execute("SELECT COUNT(*) FROM npcs")
                data_analysis["npcs"]["count"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT tipo, COUNT(*) FROM npcs GROUP BY tipo")
                data_analysis["npcs"]["types"] = dict(cursor.fetchall())
                
                # Analizar inventarios
                cursor.execute("SELECT COUNT(*) FROM inventarios")
                data_analysis["inventory"]["total_items"] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM inventarios WHERE equipado = TRUE")
                data_analysis["inventory"]["equipped_items"] = cursor.fetchone()[0]
                
                # Generar insights automáticos
                self._generate_insights(cursor, data_analysis)
                
        except Exception as e:
            data_analysis["error"] = str(e)
        
        return data_analysis
    
    def _generate_insights(self, cursor: sqlite3.Cursor, analysis: Dict[str, Any]):
        """Genera insights automáticos sobre los datos"""
        insights = []
        
        # Insight 1: Ratio de items equipados
        if analysis["inventory"]["total_items"] > 0:
            equipped_ratio = analysis["inventory"]["equipped_items"] / analysis["inventory"]["total_items"]
            if equipped_ratio < 0.3:
                insights.append({
                    "type": "low_equipment_usage",
                    "message": f"Solo {equipped_ratio:.1%} de los items están equipados",
                    "recommendation": "Los jugadores podrían necesitar más guidance sobre equipamiento"
                })
        
        # Insight 2: Balance de rareza
        rarity_dist = analysis["items"]["rarity_distribution"]
        if rarity_dist.get("legendario", 0) > rarity_dist.get("comun", 0):
            insights.append({
                "type": "rarity_imbalance",
                "message": "Hay más items legendarios que comunes",
                "recommendation": "Considerar balancear la distribución de rareza"
            })
        
        # Insight 3: Actividad de personajes
        if analysis["characters"]["count"] == 0:
            insights.append({
                "type": "no_active_characters",
                "message": "No hay personajes activos",
                "recommendation": "El servidor podría necesitar más promoción o tutoriales"
            })
        
        analysis["insights"] = insights

# ============= FUNCIONES MCP TOOLS =============

async def mcp_analyze_database() -> str:
    """MCP Tool: Analiza la base de datos y retorna reporte para Claude"""
    manager = UnityMCPDatabaseManager()
    analysis = manager.analyze_database_schema()
    data_analysis = manager.analyze_game_data()
    
    combined_report = {
        "schema_analysis": analysis,
        "data_analysis": data_analysis,
        "mcp_version": "1.0",
        "generated_by": "Unity RPG MCP Server"
    }
    
    return json.dumps(combined_report, indent=2)

async def mcp_fix_database_issues() -> str:
    """MCP Tool: Aplica correcciones automáticas a la base de datos"""
    manager = UnityMCPDatabaseManager()
    
    # Primero analizar
    analysis = manager.analyze_database_schema()
    
    # Luego aplicar correcciones
    fix_report = manager.auto_fix_schema_issues(analysis)
    
    # Re-analizar después de las correcciones
    post_analysis = manager.analyze_database_schema()
    
    result = {
        "pre_analysis": analysis,
        "fixes_applied": fix_report,
        "post_analysis": post_analysis,
        "success": len(fix_report["errors"]) == 0
    }
    
    return json.dumps(result, indent=2)

# ============= PUNTO DE ENTRADA =============

if __name__ == "__main__":
    print("🤖 Unity RPG Bot - MCP Database Manager")
    print("=" * 50)
    
    # Análisis inmediato
    manager = UnityMCPDatabaseManager()
    print("🔍 Analizando base de datos...")
    analysis = manager.analyze_database_schema()
    
    print(f"\n📊 Resultados del análisis:")
    print(f"  - Base de datos existe: {analysis['database_exists']}")
    print(f"  - Tablas encontradas: {len(analysis['tables'])}")
    print(f"  - Problemas detectados: {len(analysis['issues'])}")
    
    if analysis['issues']:
        print(f"\n⚠️ Problemas encontrados:")
        for i, issue in enumerate(analysis['issues'], 1):
            print(f"  {i}. {issue['message']}")
            if issue.get('auto_fixable'):
                print(f"     ✅ Auto-reparable")
        
        print(f"\n🔧 Aplicando correcciones automáticas...")
        fix_report = manager.auto_fix_schema_issues(analysis)
        
        print(f"  - Correcciones aplicadas: {len(fix_report['fixes_applied'])}")
        print(f"  - Errores: {len(fix_report['errors'])}")
        
        if fix_report['backup_created']:
            print(f"  - Backup creado: {fix_report['backup_created']}")
    else:
        print("\n✅ No se encontraron problemas en la base de datos")
    
    print(f"\n📈 Análisis de datos del juego...")
    data_analysis = manager.analyze_game_data()
    print(f"  - Personajes activos: {data_analysis['characters']['count']}")
    print(f"  - Items totales: {data_analysis['items']['count']}")
    print(f"  - NPCs: {data_analysis['npcs']['count']}")
    print(f"  - Insights generados: {len(data_analysis['insights'])}")
    
    print(f"\n🎉 Análisis completado. Base de datos lista para usar con /equipar_menu")