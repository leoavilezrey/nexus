#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NEXUS - COLD RUN DIAGNOSTIC SCRIPT
Chequeo en frio de todos los componentes del sistema
Fecha: 2026-02-28

Ejecuta pruebas no destructivas sobre cada componente de Nexus
sin interaccion del usuario. Genera un log detallado de resultados.

Uso: python scripts/cold_run_diagnostic.py
"""

import sys

# Forzar UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os
import traceback
import json
from datetime import datetime, timezone
from io import StringIO

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH
NEXUS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if NEXUS_ROOT not in sys.path:
    sys.path.insert(0, NEXUS_ROOT)

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DEL LOG
# ─────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(NEXUS_ROOT, "logs", "cold_run_diagnostic.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

results = []  # Lista de dicts con resultados de cada test

def log(msg):
    """Escribe al log y a stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    results.append({"time": timestamp, "message": msg})

def test_result(component, test_name, passed, details=""):
    """Registra el resultado de un test individual."""
    status = "✅ PASS" if passed else "❌ FAIL"
    log(f"{status} | {component} | {test_name} | {details}")
    return {"component": component, "test": test_name, "passed": passed, "details": details}

# ═════════════════════════════════════════════════════════════
# SECCIÓN 1: IMPORTS Y DEPENDENCIAS
# ═════════════════════════════════════════════════════════════
log("=" * 70)
log("SECCIÓN 1: VERIFICACIÓN DE IMPORTS Y DEPENDENCIAS")
log("=" * 70)

test_results = []

# 1.1 Core imports
for module_name, import_path in [
    ("core.database", "core.database"),
    ("core.models", "core.models"),
    ("core.search_engine", "core.search_engine"),
    ("core.staging_db", "core.staging_db"),
]:
    try:
        __import__(import_path)
        test_results.append(test_result("Imports", f"import {module_name}", True))
    except Exception as e:
        test_results.append(test_result("Imports", f"import {module_name}", False, str(e)))

# 1.2 Modules imports
for module_name in [
    "modules.analytics",
    "modules.file_manager",
    "modules.web_scraper",
    "modules.pkm_manager",
    "modules.exporter",
    "modules.study_engine",
    "modules.pipeline_manager",
    "modules.youtube_manager",
]:
    try:
        __import__(module_name)
        test_results.append(test_result("Imports", f"import {module_name}", True))
    except Exception as e:
        test_results.append(test_result("Imports", f"import {module_name}", False, str(e)))

# 1.3 Agents imports
for module_name in [
    "agents.study_agent",
    "agents.summary_agent",
    "agents.relationship_agent",
    "agents.deepseek_agent",
]:
    try:
        __import__(module_name)
        test_results.append(test_result("Imports", f"import {module_name}", True))
    except Exception as e:
        test_results.append(test_result("Imports", f"import {module_name}", False, str(e)))

# 1.4 UI imports
try:
    # Importamos solo la función, no ejecutamos nada
    from ui.dashboard import main_loop, menu_agregar, menu_gestionar, menu_active_recall
    test_results.append(test_result("Imports", "import ui.dashboard (funciones)", True))
except Exception as e:
    test_results.append(test_result("Imports", "import ui.dashboard (funciones)", False, str(e)))

# 1.5 Dependencias externas
for pkg in ["sqlalchemy", "pydantic", "rich", "dotenv", "requests", "bs4", "yt_dlp"]:
    try:
        __import__(pkg)
        test_results.append(test_result("Deps", f"pip package: {pkg}", True))
    except ImportError:
        test_results.append(test_result("Deps", f"pip package: {pkg}", False, "No instalado"))

# ═════════════════════════════════════════════════════════════
# SECCIÓN 2: BASE DE DATOS
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 2: VERIFICACIÓN DE BASE DE DATOS")
log("=" * 70)

try:
    from core.database import engine, SessionLocal, Registry, Tag, Card, NexusLink, init_db, nx_db, Base

    # 2.1 Verificar que el archivo DB existe
    db_path = os.path.join(NEXUS_ROOT, "nexus.db")
    test_results.append(test_result("Database", "nexus.db existe", os.path.exists(db_path), db_path))

    # 2.2 Verificar conexión
    try:
        with SessionLocal() as session:
            session.execute(
                __import__('sqlalchemy').text("SELECT 1")
            )
        test_results.append(test_result("Database", "Conexión SQLite", True))
    except Exception as e:
        test_results.append(test_result("Database", "Conexión SQLite", False, str(e)))

    # 2.3 Verificar tablas
    from sqlalchemy import inspect
    inspector = inspect(engine)
    expected_tables = {'registry', 'tags', 'nexus_links', 'cards'}
    actual_tables = set(inspector.get_table_names())
    missing = expected_tables - actual_tables
    test_results.append(test_result(
        "Database", "Tablas esperadas presentes",
        len(missing) == 0,
        f"Encontradas: {actual_tables} | Faltantes: {missing}" if missing else f"Todas presentes: {expected_tables}"
    ))

    # 2.4 Verificar conteos
    with SessionLocal() as session:
        reg_count = session.query(Registry).count()
        tag_count = session.query(Tag).count()
        card_count = session.query(Card).count()
        link_count = session.query(NexusLink).count()
        
        test_results.append(test_result("Database", "Registros en registry", True,
                                        f"Total: {reg_count}"))
        test_results.append(test_result("Database", "Tags en tags", True,
                                        f"Total: {tag_count}"))
        test_results.append(test_result("Database", "Cards en cards", True,
                                        f"Total: {card_count}"))
        test_results.append(test_result("Database", "Links en nexus_links", True,
                                        f"Total: {link_count}"))

    # 2.5 Verificar integridad referencial
    with SessionLocal() as session:
        # Cards huérfanas (parent_id sin registro)
        from sqlalchemy import text
        orphan_cards = session.execute(text(
            "SELECT COUNT(*) FROM cards WHERE parent_id NOT IN (SELECT id FROM registry)"
        )).scalar()
        test_results.append(test_result("Database", "Cards huérfanas", 
                                        orphan_cards == 0, 
                                        f"Encontradas: {orphan_cards}"))
        
        # Tags huérfanos
        orphan_tags = session.execute(text(
            "SELECT COUNT(*) FROM tags WHERE registry_id NOT IN (SELECT id FROM registry)"
        )).scalar()
        test_results.append(test_result("Database", "Tags huérfanos",
                                        orphan_tags == 0,
                                        f"Encontrados: {orphan_tags}"))
        
        # Links huérfanos
        orphan_links = session.execute(text(
            "SELECT COUNT(*) FROM nexus_links WHERE source_id NOT IN (SELECT id FROM registry) OR target_id NOT IN (SELECT id FROM registry)"
        )).scalar()
        test_results.append(test_result("Database", "Links huérfanos",
                                        orphan_links == 0,
                                        f"Encontrados: {orphan_links}"))

    # 2.6 PRAGMA checks
    with SessionLocal() as session:
        journal_mode = session.execute(text("PRAGMA journal_mode")).scalar()
        fk_status = session.execute(text("PRAGMA foreign_keys")).scalar()
        test_results.append(test_result("Database", "PRAGMA journal_mode=WAL",
                                        journal_mode.lower() == 'wal',
                                        f"Actual: {journal_mode}"))
        test_results.append(test_result("Database", "PRAGMA foreign_keys=ON",
                                        fk_status == 1,
                                        f"Actual: {fk_status}"))

except Exception as e:
    test_results.append(test_result("Database", "Inicialización crítica", False, traceback.format_exc()))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 3: CRUD OPERATIONS
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 3: VERIFICACIÓN DE OPERACIONES CRUD")
log("=" * 70)

try:
    from core.database import nx_db, RegistryCreate, TagCreate, CardCreate, NexusLinkCreate

    # 3.1 Create
    try:
        test_data = RegistryCreate(
            type="note",
            title="__COLD_RUN_TEST__",
            path_url="nexus://cold_run_test/diagnostic",
            content_raw="Registro de prueba creado por cold_run_diagnostic.py — se eliminará automáticamente."
        )
        reg = nx_db.create_registry(test_data)
        test_id = reg.id
        test_results.append(test_result("CRUD", "create_registry()", True, f"ID creado: {test_id}"))
    except Exception as e:
        test_results.append(test_result("CRUD", "create_registry()", False, str(e)))
        test_id = None

    # 3.2 Read
    if test_id:
        try:
            fetched = nx_db.get_registry(test_id)
            test_results.append(test_result("CRUD", "get_registry()", 
                                            fetched is not None and fetched.title == "__COLD_RUN_TEST__",
                                            f"Título: {fetched.title if fetched else 'None'}"))
        except Exception as e:
            test_results.append(test_result("CRUD", "get_registry()", False, str(e)))

    # 3.3 Add Tag
    if test_id:
        try:
            nx_db.add_tag(test_id, TagCreate(value="cold_run_test"))
            test_results.append(test_result("CRUD", "add_tag()", True))
        except Exception as e:
            test_results.append(test_result("CRUD", "add_tag()", False, str(e)))

    # 3.4 Create Card
    if test_id:
        try:
            card = nx_db.create_card(CardCreate(parent_id=test_id, question="Test Q?", answer="Test A."))
            test_results.append(test_result("CRUD", "create_card()", True, f"Card ID: {card.id}"))
        except Exception as e:
            test_results.append(test_result("CRUD", "create_card()", False, str(e)))

    # 3.5 Update Summary
    if test_id:
        try:
            result = nx_db.update_summary(test_id, "Resumen de prueba cold run.")
            test_results.append(test_result("CRUD", "update_summary()", result, f"Resultado: {result}"))
        except Exception as e:
            test_results.append(test_result("CRUD", "update_summary()", False, str(e)))

    # 3.6 Delete (cleanup)
    if test_id:
        try:
            deleted = nx_db.delete_registry(test_id)
            test_results.append(test_result("CRUD", "delete_registry()", deleted, f"Eliminado: {deleted}"))
        except Exception as e:
            test_results.append(test_result("CRUD", "delete_registry()", False, str(e)))

except Exception as e:
    test_results.append(test_result("CRUD", "Inicialización CRUD", False, traceback.format_exc()))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 4: SEARCH ENGINE
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 4: MOTOR DE BÚSQUEDA")
log("=" * 70)

try:
    from core.search_engine import search_registry, parse_query_string

    # 4.1 Búsqueda general
    with SessionLocal() as session:
        results_search = search_registry(db_session=session, limit=5)
        test_results.append(test_result("Search", "search_registry() sin filtros",
                                        isinstance(results_search, list),
                                        f"Resultados: {len(results_search)}"))

    # 4.2 parse_query_string
    parsed = parse_query_string("python t:docs e:pdf -t:old i:1-50")
    test_results.append(test_result("Search", "parse_query_string()",
                                    isinstance(parsed, dict),
                                    f"Parsed: {parsed}"))

    # 4.3 Búsqueda con filtros
    with SessionLocal() as session:
        results_filtered = search_registry(db_session=session, inc_tags="YouTube_Pipeline", limit=5)
        test_results.append(test_result("Search", "search_registry() con filtro tag",
                                        isinstance(results_filtered, list),
                                        f"Resultados: {len(results_filtered)}"))

except Exception as e:
    test_results.append(test_result("Search", "Motor de búsqueda", False, traceback.format_exc()))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 5: ANALYTICS
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 5: ANALYTICS MODULE")
log("=" * 70)

try:
    from modules.analytics import get_global_metrics

    metrics = get_global_metrics()
    test_results.append(test_result("Analytics", "get_global_metrics()", 
                                    isinstance(metrics, dict) and "registry_counts" in metrics,
                                    f"Keys: {list(metrics.keys())}, Total registros: {metrics.get('registry_counts', {}).get('total', 'N/A')}"))

    # Validar estructura esperada
    expected_keys = {"registry_counts", "network", "srs"}
    actual_keys = set(metrics.keys())
    test_results.append(test_result("Analytics", "Estructura de métricas",
                                    expected_keys.issubset(actual_keys),
                                    f"Esperadas: {expected_keys}, Presentes: {actual_keys}"))

except Exception as e:
    test_results.append(test_result("Analytics", "Analytics module", False, traceback.format_exc()))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 6: STAGING DB
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 6: STAGING DB (Google Drive Buffer)")
log("=" * 70)

try:
    from core.staging_db import staging_db, staging_engine, STAGING_DB_PATH

    test_results.append(test_result("Staging", "staging_engine inicializado",
                                    staging_engine is not None,
                                    f"Path: {STAGING_DB_PATH}"))
    
    # Verificar si G: está disponible
    g_drive_exists = os.path.exists(r"G:\Mi unidad")
    test_results.append(test_result("Staging", "Google Drive (G:) montado",
                                    g_drive_exists,
                                    "G:\\Mi unidad accesible" if g_drive_exists else "G: no detectada — funcionalidades de Staging/Pipeline inhabilitadas"))

    if staging_engine:
        try:
            result = staging_db.init_staging()
            test_results.append(test_result("Staging", "init_staging()", result))
        except Exception as e:
            test_results.append(test_result("Staging", "init_staging()", False, str(e)))

except Exception as e:
    test_results.append(test_result("Staging", "Staging DB", False, traceback.format_exc()))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 7: AGENTS / IA
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 7: AGENTES IA (NO se consume tokens)")
log("=" * 70)

try:
    from agents.study_agent import get_client as study_get_client
    client = study_get_client()
    test_results.append(test_result("Agents", "GOOGLE_API_KEY configurada",
                                    client is not None,
                                    "Clave presente" if client else "No hay GOOGLE_API_KEY en .env"))
except Exception as e:
    test_results.append(test_result("Agents", "study_agent.get_client()", False, str(e)))

try:
    from agents.deepseek_agent import deepseek_agent
    test_results.append(test_result("Agents", "DEEPSEEK_API_KEY configurada",
                                    deepseek_agent.api_key is not None,
                                    "Clave presente" if deepseek_agent.api_key else "No hay DEEPSEEK_API_KEY en .env"))
except Exception as e:
    test_results.append(test_result("Agents", "deepseek_agent", False, str(e)))

# Verificar mockup mode de study_agent
try:
    from agents.study_agent import generate_deck_from_registry
    from core.database import Registry as Reg
    
    # Crear un mock mínimo
    mock_reg = type('MockReg', (), {
        'id': 999999, 'title': 'COLD_RUN_MOCK', 'type': 'note',
        'content_raw': 'Test content for mock', 'meta_info': {},
        'path_url': 'nexus://test', 'summary': None,
        'is_flashcard_source': False, 'created_at': datetime.now(),
        'modified_at': datetime.now()
    })()
    
    cards = generate_deck_from_registry(mock_reg, mockup_only=True)
    test_results.append(test_result("Agents", "generate_deck_from_registry(mockup=True)",
                                    len(cards) > 0,
                                    f"Cards generadas: {len(cards)}"))
except Exception as e:
    test_results.append(test_result("Agents", "generate_deck_from_registry(mockup)", False, str(e)))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 8: ANÁLISIS ESTÁTICO DE CÓDIGO (Patrones de Error)
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 8: ANÁLISIS ESTÁTICO — PATRONES DE ERROR")
log("=" * 70)

# 8.1 Verificar el bug documentado en nexus.log
dashboard_path = os.path.join(NEXUS_ROOT, "ui", "dashboard.py")
import re
with open(dashboard_path, 'r', encoding='utf-8') as f:
    dashboard_code = f.read()

# 8.1a Buscar el import de nx_db en el scope correcto
# El error del log es: menu_agregar line 179: UnboundLocalError (nx_db)
# Esto ocurre cuando hay un import local que sombrea el import global
if "from core.database import RegistryCreate, nx_db, TagCreate" in dashboard_code:
    # Buscar si hay re-imports dentro de funciones que causan shadowing
    import re
    local_nx_db_imports = re.findall(r'def \w+.*?(?=def |\Z)', dashboard_code, re.DOTALL)
    shadowing_found = False
    for func_block in local_nx_db_imports:
        # Buscar imports locales que incluyan nx_db
        local_imports = re.findall(r'^\s+from core\.database import.*nx_db', func_block, re.MULTILINE)
        if local_imports:
            shadowing_found = True
            test_results.append(test_result("Static", "Shadowing de nx_db en función local", False,
                                            f"Import local: {local_imports[0].strip()}"))
    
    if not shadowing_found:
        test_results.append(test_result("Static", "Shadowing de nx_db", True,
                                        "No se detectó shadowing del import global"))

# 8.2 Verificar que menu_agregar usa nx_db sin re-import conflictivo (line ~353)
# La línea 353 hace: from core.database import RegistryCreate, nx_db, TagCreate
# Esto puede causar UnboundLocalError en Python 3.12+
line353_pattern = re.search(r'(elif opcion == "4".*?)(from core\.database import RegistryCreate, nx_db, TagCreate)', 
                            dashboard_code, re.DOTALL)
if line353_pattern:
    test_results.append(test_result("Static", "Import local de nx_db en menu_agregar opción 4", False,
                                    "Línea ~353: 'from core.database import RegistryCreate, nx_db, TagCreate' "
                                    "dentro de menu_agregar() crea un import local que sombrea el global —"
                                    " esto causa UnboundLocalError en línea 179 donde nx_db se usa antes del import local."
                                    " SOLUCIÓN: Eliminar nx_db del import local (ya está importado globalmente en línea 59)."))
else:
    test_results.append(test_result("Static", "Import local de nx_db en menu_agregar opción 4", True,
                                    "No se detectó import local conflictivo"))

# 8.3 Verificar acceso a content_raw sin None-check (potencial NoneType error)
# Línea 259 y 306
problems_none_check = []
lines = dashboard_code.split('\n')
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    # Patrón: resultado.content_raw[:800] sin verificar None
    if 'resultado.content_raw[:' in stripped and 'if resultado.content_raw' not in stripped:
        # Verificar si hay un check antes
        if i >= 3:
            context = '\n'.join(lines[max(0,i-4):i])
            if 'if resultado.content_raw' not in context and 'content_raw is not None' not in context:
                problems_none_check.append(f"Línea {i}: {stripped[:80]}")

if problems_none_check:
    test_results.append(test_result("Static", "content_raw[:800] sin None-check",
                                    False, f"Posibles crashes: {problems_none_check}"))
else:
    test_results.append(test_result("Static", "content_raw None-checks", True))

# 8.4 Verificar bare except clauses
bare_excepts = re.findall(r'except:\s*\n', dashboard_code)
test_results.append(test_result("Static", "Bare except: clauses",
                                len(bare_excepts) == 0,
                                f"Encontrados: {len(bare_excepts)} — Deben capturar excepciones específicas"))

# 8.5 Buscar prints con formato Rich fuera de console (en módulos que no importan Rich)
for mod_path, mod_name in [
    ("modules/file_manager.py", "file_manager"),
    ("modules/pkm_manager.py", "pkm_manager"),
]:
    full_path = os.path.join(NEXUS_ROOT, mod_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            mod_code = f.read()
        # Buscar prints que usan marcado Rich pero usan print() en vez de console.print()
        rich_prints = re.findall(r'(?<!console\.)print\(.*\[bold.*\]', mod_code)
        if rich_prints:
            test_results.append(test_result("Static", f"print() con Rich tags en {mod_name}",
                                            False,
                                            f"Usan print() con Tags Rich [bold] que no se renderizarán. "
                                            f"Debería usar console.print(). Ocurrencias: {len(rich_prints)}"))

# 8.6 Verificar import de msvcrt (solo Windows)
if "import msvcrt" in dashboard_code and sys.platform != "win32":
    test_results.append(test_result("Static", "msvcrt (Windows-only)", False,
                                    "El dashboard importa msvcrt incondicionalmente"))
else:
    test_results.append(test_result("Static", "msvcrt import", True,
                                    "Correcto en Windows o condicional"))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 9: ARCHIVOS Y RUTAS
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 9: ARCHIVOS Y RUTAS DEL SISTEMA")
log("=" * 70)

critical_files = [
    ("main.py", os.path.join(NEXUS_ROOT, "main.py")),
    ("core/database.py", os.path.join(NEXUS_ROOT, "core", "database.py")),
    ("core/models.py", os.path.join(NEXUS_ROOT, "core", "models.py")),
    ("core/search_engine.py", os.path.join(NEXUS_ROOT, "core", "search_engine.py")),
    ("ui/dashboard.py", os.path.join(NEXUS_ROOT, "ui", "dashboard.py")),
    ("modules/analytics.py", os.path.join(NEXUS_ROOT, "modules", "analytics.py")),
    (".env", os.path.join(NEXUS_ROOT, ".env")),
    ("requirements.txt", os.path.join(NEXUS_ROOT, "requirements.txt")),
]

for name, path in critical_files:
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    test_results.append(test_result("Files", f"{name}", exists,
                                    f"Size: {size:,} bytes" if exists else "NO ENCONTRADO"))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 10: WEB SERVER (FastAPI)
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 10: WEB SERVER (FastAPI)")
log("=" * 70)

try:
    from web_server import app
    test_results.append(test_result("WebServer", "FastAPI app importable", True))
    
    # Verificar rutas registradas
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    expected_routes = ["/", "/api/records", "/api/stats", "/api/recall/cards"]
    for route in expected_routes:
        test_results.append(test_result("WebServer", f"Ruta {route}",
                                        route in routes,
                                        "Registrada" if route in routes else "NO registrada"))

except Exception as e:
    test_results.append(test_result("WebServer", "FastAPI import", False, str(e)))


# ═════════════════════════════════════════════════════════════
# SECCIÓN 11: NEXUS.LOG HISTÓRICO
# ═════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("SECCIÓN 11: ANÁLISIS DE NEXUS.LOG HISTÓRICO")
log("=" * 70)

nexus_log_path = os.path.join(NEXUS_ROOT, "nexus.log")
if os.path.exists(nexus_log_path):
    with open(nexus_log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    error_count = log_content.count("[ERROR]")
    warning_count = log_content.count("[WARNING]")
    
    test_results.append(test_result("Logs", "Errores en nexus.log",
                                    error_count == 0,
                                    f"Errores: {error_count}, Warnings: {warning_count}"))
    
    # Errores únicos
    error_lines = [line for line in log_content.split('\n') if '[ERROR]' in line]
    unique_errors = set(error_lines)
    for err in unique_errors:
        test_results.append(test_result("Logs", "Error histórico", False, err.strip()[:120]))
else:
    test_results.append(test_result("Logs", "nexus.log", True, "Archivo limpio (no existe)"))


# ═════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═════════════════════════════════════════════════════════════
log("")
log("═" * 70)
log("RESUMEN EJECUTIVO DEL DIAGNÓSTICO EN FRÍO")
log("═" * 70)

total_tests = len(test_results)
passed = sum(1 for r in test_results if r["passed"])
failed = sum(1 for r in test_results if not r["passed"])

log(f"Total de tests ejecutados: {total_tests}")
log(f"✅ Pasados: {passed}")
log(f"❌ Fallidos: {failed}")
log(f"Tasa de éxito: {(passed/total_tests*100):.1f}%")

if failed > 0:
    log("")
    log("TESTS FALLIDOS:")
    for r in test_results:
        if not r["passed"]:
            log(f"  ❌ [{r['component']}] {r['test']}: {r['details']}")

# Guardar log a archivo
log("")
log(f"Log completo guardado en: {LOG_FILE}")

with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write(f"NEXUS COLD RUN DIAGNOSTIC — {datetime.now().isoformat()}\n")
    f.write("=" * 70 + "\n\n")
    
    for entry in results:
        f.write(f"{entry['message']}\n")
    
    f.write("\n\n" + "=" * 70 + "\n")
    f.write("RESULTADOS JSON:\n")
    f.write("=" * 70 + "\n")
    f.write(json.dumps(test_results, indent=2, ensure_ascii=False))

# También guardar JSON puro para procesamiento
json_log = LOG_FILE.replace('.log', '.json')
with open(json_log, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "success_rate": round(passed/total_tests*100, 1),
        "results": test_results
    }, f, indent=2, ensure_ascii=False)

log(f"JSON de resultados en: {json_log}")
log("═" * 70)
log("DIAGNÓSTICO FINALIZADO")
log("═" * 70)
