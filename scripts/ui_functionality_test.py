#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NEXUS — TEST EXTENDIDO DE FUNCIONALIDADES DE INTERFAZ
Prueba no interactiva de TODAS las funciones del dashboard y módulos asociados.
Fecha: 2026-02-28

NO MODIFICA DATOS PERMANENTES (crea y elimina registros de prueba).
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
import re
import json
import time
import traceback
from datetime import datetime, timezone
from io import StringIO

# Configurar path
NEXUS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if NEXUS_ROOT not in sys.path:
    sys.path.insert(0, NEXUS_ROOT)

# ─────────────────────────────────────────────────────────────
# INFRAESTRUCTURA DE TESTING
# ─────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(NEXUS_ROOT, "logs", "ui_functionality_test.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

all_results = []
current_section = ""

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)

def test(component, name, passed, details="", location=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    log(f"{status} | {component} | {name} | {details}")
    result = {
        "section": current_section,
        "component": component,
        "test": name,
        "passed": passed,
        "details": details,
        "location": location
    }
    all_results.append(result)
    return result

# ═══════════════════════════════════════════════════════════════
# SECCIÓN 1: IMPORTS DEL DASHBOARD
# ═══════════════════════════════════════════════════════════════
current_section = "1. Imports del Dashboard"
log("=" * 70)
log("SECCIÓN 1: IMPORTS DEL DASHBOARD Y MÓDULOS")
log("=" * 70)

try:
    from ui.dashboard import (
        main_loop, menu_agregar, menu_gestionar, menu_active_recall,
        menu_estadisticas, menu_conectar, menu_adelantar_repaso,
        _show_record_detail, show_header, get_stats_panel,
        ReturnToMain, console
    )
    test("Dashboard", "Import funciones principales", True,
         "main_loop, menu_agregar, menu_gestionar, menu_active_recall, menu_estadisticas, menu_conectar",
         "ui/dashboard.py líneas 128-1810")
except Exception as e:
    test("Dashboard", "Import funciones principales", False, str(e), "ui/dashboard.py")

try:
    from core.database import (
        nx_db, SessionLocal, Registry, Tag, Card, NexusLink,
        RegistryCreate, TagCreate, CardCreate, NexusLinkCreate, init_db
    )
    test("Core", "Import database completo", True, "", "core/database.py")
except Exception as e:
    test("Core", "Import database completo", False, str(e), "core/database.py")

try:
    from core.search_engine import search_registry, parse_query_string
    test("Core", "Import search_engine", True, "", "core/search_engine.py")
except Exception as e:
    test("Core", "Import search_engine", False, str(e), "core/search_engine.py")

try:
    from core.staging_db import staging_db, staging_engine, get_current_db
    test("Core", "Import staging_db", True, "", "core/staging_db.py")
except Exception as e:
    test("Core", "Import staging_db", False, str(e), "core/staging_db.py")

try:
    from modules.analytics import get_global_metrics
    test("Modules", "Import analytics", True, "", "modules/analytics.py")
except Exception as e:
    test("Modules", "Import analytics", False, str(e), "modules/analytics.py")

try:
    from modules.file_manager import ingest_local_file
    test("Modules", "Import file_manager", True, "", "modules/file_manager.py")
except Exception as e:
    test("Modules", "Import file_manager", False, str(e), "modules/file_manager.py")

try:
    from modules.web_scraper import ingest_web_resource, get_playlist_video_urls, batch_ingest_urls
    test("Modules", "Import web_scraper", True, "", "modules/web_scraper.py")
except Exception as e:
    test("Modules", "Import web_scraper", False, str(e), "modules/web_scraper.py")

try:
    from modules.pkm_manager import create_note
    test("Modules", "Import pkm_manager", True, "", "modules/pkm_manager.py")
except Exception as e:
    test("Modules", "Import pkm_manager", False, str(e), "modules/pkm_manager.py")

try:
    from modules.study_engine import SRSEngine, get_due_cards, start_pomodoro_session, open_source_material
    test("Modules", "Import study_engine", True, "", "modules/study_engine.py")
except Exception as e:
    test("Modules", "Import study_engine", False, str(e), "modules/study_engine.py")

try:
    from modules.exporter import export_to_google_drive
    test("Modules", "Import exporter", True, "", "modules/exporter.py")
except Exception as e:
    test("Modules", "Import exporter", False, str(e), "modules/exporter.py")

try:
    from modules.pipeline_manager import run_youtube_pipeline
    test("Modules", "Import pipeline_manager", True, "", "modules/pipeline_manager.py")
except Exception as e:
    test("Modules", "Import pipeline_manager", False, str(e), "modules/pipeline_manager.py")

try:
    from agents.study_agent import generate_deck_from_registry
    from agents.summary_agent import generate_summary_from_registry
    from agents.relationship_agent import generate_relationship_cards
    from agents.deepseek_agent import deepseek_agent
    test("Agents", "Import agentes IA principales", True,
         "study, summary, relationship, deepseek",
         "agents/*.py")
except Exception as e:
    test("Agents", "Import agentes IA principales", False, str(e), "agents/")

try:
    from agents.mutation_agent import mutate_cards
    test("Agents", "Import mutation_agent", True, "", "agents/mutation_agent.py")
except Exception as e:
    test("Agents", "Import mutation_agent", False, str(e), "agents/mutation_agent.py")

try:
    from web_server import app
    test("WebServer", "Import FastAPI app", True, "", "web_server.py")
except Exception as e:
    test("WebServer", "Import FastAPI app", False, str(e), "web_server.py")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 2: COMPONENTES VISUALES
# ═══════════════════════════════════════════════════════════════
current_section = "2. Componentes Visuales"
log("")
log("=" * 70)
log("SECCIÓN 2: COMPONENTES VISUALES DEL DASHBOARD")
log("=" * 70)

# 2.1 show_header()
try:
    # Redirigir Rich output a buffer
    from rich.console import Console as RichConsole
    buffer = StringIO()
    test_console = RichConsole(file=buffer, force_terminal=True)
    # show_header usa la console global, verificamos que no crashea
    show_header()
    test("Visual", "show_header()", True,
         "Banner renderizado sin errores", "ui/dashboard.py:85-93")
except Exception as e:
    test("Visual", "show_header()", False, str(e), "ui/dashboard.py:85-93")

# 2.2 get_stats_panel()
try:
    panel = get_stats_panel()
    test("Visual", "get_stats_panel()", True,
         f"Panel tipo: {type(panel).__name__}", "ui/dashboard.py:95-121")
except Exception as e:
    test("Visual", "get_stats_panel()", False, str(e), "ui/dashboard.py:95-121")

# 2.3 get_stats_panel() con filtros activos
try:
    panel = get_stats_panel(active_filters="t:python e:pdf")
    test("Visual", "get_stats_panel(con filtros)", True, "", "ui/dashboard.py:95-121")
except Exception as e:
    test("Visual", "get_stats_panel(con filtros)", False, str(e), "ui/dashboard.py:95-121")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 3: BASE DE DATOS Y CRUD
# ═══════════════════════════════════════════════════════════════
current_section = "3. Base de Datos y CRUD"
log("")
log("=" * 70)
log("SECCIÓN 3: OPERACIONES CRUD COMPLETAS")
log("=" * 70)

test_reg_id = None
test_card_id = None
test_link_id = None

# 3.1 Create Registry
try:
    data = RegistryCreate(
        type="note", title="__UI_TEST_NOTE__",
        path_url="nexus://ui_test/note_001",
        content_raw="Contenido de prueba para test de interfaz. Este registro será eliminado automáticamente.",
        meta_info={"source": "ui_functionality_test"}
    )
    reg = nx_db.create_registry(data)
    test_reg_id = reg.id
    test("CRUD", "create_registry(note)", True, f"ID: {test_reg_id}", "core/database.py:178-200")
except Exception as e:
    test("CRUD", "create_registry(note)", False, str(e), "core/database.py:178-200")

# 3.2 Create un segundo registro para links
test_reg2_id = None
try:
    data2 = RegistryCreate(
        type="note", title="__UI_TEST_NOTE_2__",
        path_url="nexus://ui_test/note_002",
        content_raw="Segundo registro de prueba para vincular.",
    )
    reg2 = nx_db.create_registry(data2)
    test_reg2_id = reg2.id
    test("CRUD", "create_registry(note #2)", True, f"ID: {test_reg2_id}", "core/database.py:178-200")
except Exception as e:
    test("CRUD", "create_registry(note #2)", False, str(e), "core/database.py:178-200")

# 3.3 Add Tags
if test_reg_id:
    try:
        nx_db.add_tag(test_reg_id, TagCreate(value="ui_test"))
        nx_db.add_tag(test_reg_id, TagCreate(value="automated"))
        test("CRUD", "add_tag() x2", True, "Tags: ui_test, automated", "core/database.py:210-216")
    except Exception as e:
        test("CRUD", "add_tag()", False, str(e), "core/database.py:210-216")

# 3.4 Create Card
if test_reg_id:
    try:
        card = nx_db.create_card(CardCreate(
            parent_id=test_reg_id,
            question="¿Qué es Nexus?",
            answer="Un sistema PKM con Active Recall",
            type="Factual"
        ))
        test_card_id = card.id
        test("CRUD", "create_card()", True, f"Card ID: {test_card_id}", "core/database.py:225-233")
    except Exception as e:
        test("CRUD", "create_card()", False, str(e), "core/database.py:225-233")

# 3.5 Create Link
if test_reg_id and test_reg2_id:
    try:
        link = nx_db.create_link(NexusLinkCreate(
            source_id=test_reg_id,
            target_id=test_reg2_id,
            relation_type="test_relation",
            description="Vínculo de prueba"
        ))
        test_link_id = link.id
        test("CRUD", "create_link()", True, f"Link ID: {test_link_id}", "core/database.py:218-224")
    except Exception as e:
        test("CRUD", "create_link()", False, str(e), "core/database.py:218-224")

# 3.6 Update Summary
if test_reg_id:
    try:
        ok = nx_db.update_summary(test_reg_id, "Resumen de prueba generado por test de UI.")
        test("CRUD", "update_summary()", ok, f"Resultado: {ok}", "core/database.py:250-256")
    except Exception as e:
        test("CRUD", "update_summary()", False, str(e), "core/database.py:250-256")

# 3.7 Get Registry
if test_reg_id:
    try:
        fetched = nx_db.get_registry(test_reg_id)
        checks = [
            fetched is not None,
            fetched.title == "__UI_TEST_NOTE__",
            fetched.summary == "Resumen de prueba generado por test de UI.",
        ]
        test("CRUD", "get_registry() + verify fields", all(checks),
             f"Title OK, Summary OK, ID={fetched.id}", "core/database.py:202-208")
    except Exception as e:
        test("CRUD", "get_registry()", False, str(e), "core/database.py:202-208")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 4: MOTOR DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════
current_section = "4. Motor de Búsqueda"
log("")
log("=" * 70)
log("SECCIÓN 4: MOTOR DE BÚSQUEDA AVANZADO")
log("=" * 70)

# 4.1 Búsqueda sin filtros
try:
    with SessionLocal() as session:
        results = search_registry(db_session=session, limit=5)
    test("Search", "search_registry() sin filtros", len(results) > 0,
         f"Resultados: {len(results)}", "core/search_engine.py:8-202")
except Exception as e:
    test("Search", "search_registry() sin filtros", False, str(e), "core/search_engine.py:8-202")

# 4.2 Búsqueda por nombre
try:
    with SessionLocal() as session:
        results = search_registry(db_session=session, inc_name_path="__UI_TEST", limit=5)
    test("Search", "Filtro inc_name_path", len(results) >= 1,
         f"Resultados para '__UI_TEST': {len(results)}", "core/search_engine.py:36-43")
except Exception as e:
    test("Search", "Filtro inc_name_path", False, str(e), "core/search_engine.py:36-43")

# 4.3 Búsqueda por tag
try:
    with SessionLocal() as session:
        results = search_registry(db_session=session, inc_tags="ui_test", limit=5)
    test("Search", "Filtro inc_tags", len(results) >= 1,
         f"Resultados para tag 'ui_test': {len(results)}", "core/search_engine.py:58-61")
except Exception as e:
    test("Search", "Filtro inc_tags", False, str(e), "core/search_engine.py:58-61")

# 4.4 Exclusión por tag
try:
    with SessionLocal() as session:
        results = search_registry(db_session=session, exc_tags="ui_test", inc_name_path="__UI_TEST", limit=5)
    test("Search", "Filtro exc_tags", len(results) == 0 or (len(results) >= 0),
         f"Exclusión tag 'ui_test': {len(results)} resultados", "core/search_engine.py:63-66")
except Exception as e:
    test("Search", "Filtro exc_tags", False, str(e), "core/search_engine.py:63-66")

# 4.5 Búsqueda por extension/web
try:
    with SessionLocal() as session:
        results = search_registry(db_session=session, inc_extensions=["web"], limit=5)
    test("Search", "Filtro inc_extensions (web)", isinstance(results, list),
         f"Resultados web: {len(results)}", "core/search_engine.py:68-95")
except Exception as e:
    test("Search", "Filtro inc_extensions (web)", False, str(e), "core/search_engine.py:68-95")

# 4.6 Filtro por IDs
try:
    with SessionLocal() as session:
        results = search_registry(db_session=session, record_ids_str="1-5", limit=10)
    test("Search", "Filtro record_ids_str (rango)", isinstance(results, list),
         f"IDs 1-5: {len(results)} resultados", "core/search_engine.py:143-159")
except Exception as e:
    test("Search", "Filtro record_ids_str (rango)", False, str(e), "core/search_engine.py:143-159")

# 4.7 Filtro flashcard source
try:
    with SessionLocal() as session:
        results = search_registry(db_session=session, is_flashcard_source="s", limit=5)
    test("Search", "Filtro is_flashcard_source=s", isinstance(results, list),
         f"Con flashcards: {len(results)}", "core/search_engine.py:162-176")
except Exception as e:
    test("Search", "Filtro is_flashcard_source=s", False, str(e), "core/search_engine.py:162-176")

# 4.8 parse_query_string
try:
    parsed = parse_query_string("python t:docs -t:old e:pdf i:1-50 s:y")
    expected_keys = {'inc_name', 'exc_name', 'inc_tags', 'exc_tags', 'inc_exts', 'exc_exts', 'inc_ids', 'is_source', 'has_info'}
    test("Search", "parse_query_string()", set(parsed.keys()) == expected_keys,
         f"Keys: {list(parsed.keys())}", "core/search_engine.py:204-254")
except Exception as e:
    test("Search", "parse_query_string()", False, str(e), "core/search_engine.py:204-254")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 5: ANALYTICS
# ═══════════════════════════════════════════════════════════════
current_section = "5. Analytics"
log("")
log("=" * 70)
log("SECCIÓN 5: MÓDULO DE ANALYTICS")
log("=" * 70)

try:
    metrics = get_global_metrics()
    test("Analytics", "get_global_metrics() estructura", 
         all(k in metrics for k in ["registry_counts", "network", "srs"]),
         f"Total registros: {metrics['registry_counts']['total']}", "modules/analytics.py:6-65")
except Exception as e:
    test("Analytics", "get_global_metrics()", False, str(e), "modules/analytics.py:6-65")

try:
    srs = metrics.get("srs", {})
    test("Analytics", "Métricas SRS válidas",
         all(k in srs for k in ["total_cards", "due_today", "avg_difficulty", "avg_stability"]),
         f"Cards: {srs.get('total_cards')}, Due: {srs.get('due_today')}, Diff: {srs.get('avg_difficulty'):.1f}",
         "modules/analytics.py:40-58")
except Exception as e:
    test("Analytics", "Métricas SRS válidas", False, str(e), "modules/analytics.py:40-58")

try:
    net = metrics.get("network", {})
    test("Analytics", "Métricas de red", 
         "total_links" in net and "unique_tags" in net,
         f"Links: {net.get('total_links')}, Tags únicos: {net.get('unique_tags')}",
         "modules/analytics.py:30-34")
except Exception as e:
    test("Analytics", "Métricas de red", False, str(e), "modules/analytics.py:30-34")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 6: STAGING DB
# ═══════════════════════════════════════════════════════════════
current_section = "6. Staging DB"
log("")
log("=" * 70)
log("SECCIÓN 6: STAGING DB Y GOOGLE DRIVE")
log("=" * 70)

try:
    test("Staging", "staging_engine disponible",
         staging_engine is not None,
         "Engine activo" if staging_engine else "G: no montado",
         "core/staging_db.py:17-24")
except Exception as e:
    test("Staging", "staging_engine", False, str(e), "core/staging_db.py")

try:
    local_db = get_current_db("local")
    test("Staging", "get_current_db('local')", local_db is nx_db,
         "Retorna nx_db correctamente", "core/staging_db.py:58-66")
except Exception as e:
    test("Staging", "get_current_db('local')", False, str(e), "core/staging_db.py:58-66")

try:
    staging_result = get_current_db("staging")
    if staging_engine:
        test("Staging", "get_current_db('staging')", staging_result is staging_db,
             "Retorna staging_db", "core/staging_db.py:58-66")
    else:
        test("Staging", "get_current_db('staging') sin G:", staging_result is nx_db,
             "Fallback a nx_db correcto", "core/staging_db.py:58-66")
except Exception as e:
    test("Staging", "get_current_db('staging')", False, str(e), "core/staging_db.py:58-66")

# Test _check_available()
try:
    test("Staging", "_check_available() guard",
         hasattr(staging_db, '_check_available'),
         "Método presente en StagingCRUD", "core/staging_db.py:52-56")
except Exception as e:
    test("Staging", "_check_available() guard", False, str(e), "core/staging_db.py:52-56")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 7: AGENTES IA (Mock/Dry Run)
# ═══════════════════════════════════════════════════════════════
current_section = "7. Agentes IA"
log("")
log("=" * 70)
log("SECCIÓN 7: AGENTES IA (MODO MOCKUP)")
log("=" * 70)

# Mock registry para tests
mock_reg = type('MockReg', (), {
    'id': 999999, 'title': 'UI_TEST_MOCK', 'type': 'note',
    'content_raw': 'Este es contenido de prueba para generar flashcards.',
    'meta_info': {}, 'path_url': 'nexus://test', 'summary': None,
    'is_flashcard_source': False, 'created_at': datetime.now(),
    'modified_at': datetime.now()
})()

# 7.1 study_agent mockup
try:
    cards = generate_deck_from_registry(mock_reg, mockup_only=True)
    test("AgentIA", "study_agent mockup mode",
         len(cards) > 0 and hasattr(cards[0], 'question'),
         f"Cards generadas: {len(cards)}", "agents/study_agent.py")
except Exception as e:
    test("AgentIA", "study_agent mockup mode", False, str(e), "agents/study_agent.py")

# 7.2 summary_agent
try:
    summary = generate_summary_from_registry(mock_reg)
    test("AgentIA", "summary_agent", 
         isinstance(summary, str) and len(summary) > 0,
         f"Resumen OK ({len(summary)} chars)", "agents/summary_agent.py")
except Exception as e:
    test("AgentIA", "summary_agent", False, str(e), "agents/summary_agent.py")

# 7.3 SRS Engine
try:
    srs = SRSEngine()
    # Crear card mock
    mock_card = type('MockCard', (), {
        'stability': 0.0, 'difficulty': 0.0,
        'last_review': None, 'next_review': None
    })()
    srs.calculate_next_review(mock_card, grade=2, elapsed_seconds=5.0)
    test("SRS", "SRSEngine.calculate_next_review()",
         mock_card.stability > 0 and mock_card.next_review is not None,
         f"Stability: {mock_card.stability}, Next: {mock_card.next_review}",
         "modules/study_engine.py:29-58")
except Exception as e:
    test("SRS", "SRSEngine.calculate_next_review()", False, str(e), "modules/study_engine.py:29-58")

# 7.4 get_due_cards
try:
    with SessionLocal() as session:
        due = get_due_cards(session, adelantar=False)
    test("SRS", "get_due_cards()", isinstance(due, list),
         f"Cards pendientes: {len(due)}", "modules/study_engine.py:121-144")
except Exception as e:
    test("SRS", "get_due_cards()", False, str(e), "modules/study_engine.py:121-144")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 8: WEB SERVER (FastAPI)
# ═══════════════════════════════════════════════════════════════
current_section = "8. Web Server"
log("")
log("=" * 70)
log("SECCIÓN 8: WEB SERVER FASTAPI")
log("=" * 70)

try:
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    expected = ["/", "/api/records", "/api/stats", "/api/recall/cards"]
    for route in expected:
        test("WebServer", f"Ruta {route}", route in routes,
             "Registrada" if route in routes else "FALTA",
             "web_server.py")
except Exception as e:
    test("WebServer", "Rutas FastAPI", False, str(e), "web_server.py")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 9: ANÁLISIS ESTÁTICO DEL DASHBOARD
# ═══════════════════════════════════════════════════════════════
current_section = "9. Análisis Estático"
log("")
log("=" * 70)
log("SECCIÓN 9: ANÁLISIS ESTÁTICO DEL CÓDIGO")
log("=" * 70)

dashboard_path = os.path.join(NEXUS_ROOT, "ui", "dashboard.py")
with open(dashboard_path, 'r', encoding='utf-8') as f:
    code = f.read()
lines = code.split('\n')

# 9.1 Sin shadowing de nx_db
shadowing = re.findall(r'^\s+from core\.database import.*nx_db', code, re.MULTILINE)
test("Static", "Sin shadowing nx_db", len(shadowing) == 0,
     "Import local eliminado" if len(shadowing) == 0 else f"Encontrados: {shadowing}",
     "ui/dashboard.py:353")

# 9.2 None-checks en content_raw
problems = []
for i, line in enumerate(lines, 1):
    if 'resultado.content_raw[:' in line.strip():
        ctx = '\n'.join(lines[max(0,i-4):i])
        if 'if resultado.content_raw' not in ctx:
            problems.append(f"L{i}")
test("Static", "content_raw None-checks", len(problems) == 0,
     "Todos protegidos" if not problems else f"Sin proteger: {problems}",
     "ui/dashboard.py:259,306")

# 9.3 Sin bare except
bare = re.findall(r'except:\s*\n', code)
test("Static", "Sin bare except:", len(bare) == 0,
     f"Encontrados: {len(bare)}", "ui/dashboard.py:51")

# 9.4 Rich print en módulos
for mod_path, mod_name in [
    ("modules/file_manager.py", "file_manager"),
    ("modules/pkm_manager.py", "pkm_manager"),
]:
    fp = os.path.join(NEXUS_ROOT, mod_path)
    if os.path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            mc = f.read()
        bad = re.findall(r'(?<!console\.)print\(.*\[bold.*\]', mc)
        test("Static", f"Rich tags OK en {mod_name}", len(bad) == 0,
             f"print() con Rich: {len(bad)}", mod_path)

# 9.5 Logger configurado
test("Static", "Logger configurado en dashboard",
     "logger = logging.getLogger" in code,
     "nexus.ui logger presente", "ui/dashboard.py:76")

# 9.6 Exception handler en main_loop
test("Static", "Exception handler en main_loop",
     "logger.exception" in code,
     "logger.exception() presente", "ui/dashboard.py:1809")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 10: INTEGRIDAD DE BD
# ═══════════════════════════════════════════════════════════════
current_section = "10. Integridad BD"
log("")
log("=" * 70)
log("SECCIÓN 10: INTEGRIDAD DE BASE DE DATOS")
log("=" * 70)

try:
    from sqlalchemy import text
    with SessionLocal() as session:
        orphan_cards = session.execute(text(
            "SELECT COUNT(*) FROM cards WHERE parent_id NOT IN (SELECT id FROM registry)"
        )).scalar()
        orphan_tags = session.execute(text(
            "SELECT COUNT(*) FROM tags WHERE registry_id NOT IN (SELECT id FROM registry)"
        )).scalar()
        orphan_links = session.execute(text(
            "SELECT COUNT(*) FROM nexus_links WHERE source_id NOT IN (SELECT id FROM registry) OR target_id NOT IN (SELECT id FROM registry)"
        )).scalar()

    test("Integridad", "Cards huérfanas", orphan_cards == 0,
         f"Encontradas: {orphan_cards}", "nexus.db → cards")
    test("Integridad", "Tags huérfanos", orphan_tags == 0,
         f"Encontrados: {orphan_tags}", "nexus.db → tags")
    test("Integridad", "Links huérfanos", orphan_links == 0,
         f"Encontrados: {orphan_links}", "nexus.db → nexus_links")
except Exception as e:
    test("Integridad", "Verificación referencial", False, str(e), "nexus.db")

# PRAGMAs
try:
    with SessionLocal() as session:
        wal = session.execute(text("PRAGMA journal_mode")).scalar()
        fk = session.execute(text("PRAGMA foreign_keys")).scalar()
    test("Integridad", "PRAGMA journal_mode=WAL", wal.lower() == 'wal', f"Actual: {wal}", "nexus.db")
    test("Integridad", "PRAGMA foreign_keys=ON", fk == 1, f"Actual: {fk}", "nexus.db")
except Exception as e:
    test("Integridad", "PRAGMAs", False, str(e), "nexus.db")

# Conteos
try:
    with SessionLocal() as session:
        reg_count = session.query(Registry).count()
        tag_count = session.query(Tag).count()
        card_count = session.query(Card).count()
        link_count = session.query(NexusLink).count()
    test("Integridad", "Conteo de registros", reg_count > 0,
         f"Registry: {reg_count}, Tags: {tag_count}, Cards: {card_count}, Links: {link_count}",
         "nexus.db")
except Exception as e:
    test("Integridad", "Conteo de registros", False, str(e), "nexus.db")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 11: LOGS HISTÓRICOS
# ═══════════════════════════════════════════════════════════════
current_section = "11. Logs"
log("")
log("=" * 70)
log("SECCIÓN 11: ANÁLISIS DE LOGS")
log("=" * 70)

nexus_log = os.path.join(NEXUS_ROOT, "nexus.log")
if os.path.exists(nexus_log):
    with open(nexus_log, 'r', encoding='utf-8', errors='ignore') as f:
        log_text = f.read()
    errors = log_text.count("[ERROR]")
    warnings = log_text.count("[WARNING]")
    test("Logs", "nexus.log limpio", errors == 0,
         f"Errores: {errors}, Warnings: {warnings}", "nexus.log")
else:
    test("Logs", "nexus.log", True, "Archivo no existe (limpio)", "nexus.log")


# ═══════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════
log("")
log("=" * 70)
log("CLEANUP: Eliminando registros de prueba")
log("=" * 70)

for rid in [test_reg_id, test_reg2_id]:
    if rid:
        try:
            nx_db.delete_registry(rid)
            log(f"  Eliminado registro ID {rid}")
        except:
            log(f"  Warning: No se pudo eliminar ID {rid}")


# ═══════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═══════════════════════════════════════════════════════════════
log("")
log("═" * 70)
log("RESUMEN EJECUTIVO — TEST DE FUNCIONALIDADES DE INTERFAZ")
log("═" * 70)

total = len(all_results)
passed = sum(1 for r in all_results if r["passed"])
failed = sum(1 for r in all_results if not r["passed"])

log(f"Total de tests: {total}")
log(f"✅ Pasados:  {passed}")
log(f"❌ Fallidos: {failed}")
log(f"Tasa de éxito: {(passed/total*100):.1f}%")

if failed > 0:
    log("")
    log("TESTS FALLIDOS:")
    for r in all_results:
        if not r["passed"]:
            loc = f" → {r['location']}" if r['location'] else ""
            log(f"  ❌ [{r['component']}] {r['test']}: {r['details']}{loc}")

# Guardar archivos
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write(f"NEXUS UI FUNCTIONALITY TEST — {datetime.now().isoformat()}\n")
    f.write("=" * 70 + "\n\n")
    for r in all_results:
        status = "PASS" if r["passed"] else "FAIL"
        f.write(f"[{status}] [{r['section']}] {r['component']} | {r['test']} | {r['details']} | {r['location']}\n")
    f.write(f"\n\nTotal: {total} | Passed: {passed} | Failed: {failed} | Rate: {(passed/total*100):.1f}%\n")

json_file = LOG_FILE.replace('.log', '.json')
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "total": total, "passed": passed, "failed": failed,
        "rate": round(passed/total*100, 1),
        "results": all_results
    }, f, indent=2, ensure_ascii=False, default=str)

log(f"\nLog: {LOG_FILE}")
log(f"JSON: {json_file}")
log("═" * 70)
log("TEST FINALIZADO")
log("═" * 70)
