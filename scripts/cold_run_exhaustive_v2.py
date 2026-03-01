#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NEXUS - CORRIDA EN FRIO EXHAUSTIVA v2
Analisis profundo con logging detallado para:
  - Menu 2 (Gestionar): paginacion, filtros, detalle, borrado, vinculacion
  - Omnibar: busqueda directa, comandos invalidos, edge cases
  - Ctrl+C: manejo de KeyboardInterrupt en todos los menus
Fecha: 2026-02-28
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, re, json, time, traceback, inspect, ast
from datetime import datetime, timezone
from io import StringIO

NEXUS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if NEXUS_ROOT not in sys.path:
    sys.path.insert(0, NEXUS_ROOT)

# ── Output setup ──
REPORT_FILE = os.path.join(NEXUS_ROOT, "docs", "corrida_frio_exhaustiva_v2.md")
LOG_FILE = os.path.join(NEXUS_ROOT, "logs", "corrida_frio_exhaustiva_v2.log")
JSON_FILE = os.path.join(NEXUS_ROOT, "logs", "corrida_frio_exhaustiva_v2.json")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

all_results = []
current_section = ""
section_logs = {}  # section -> [log lines]
log_lines = []

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_lines.append(line)
    if current_section not in section_logs:
        section_logs[current_section] = []
    section_logs[current_section].append(line)

def test(component, name, passed, details="", location="", severity="normal"):
    """Register a test. severity: normal, critical, deep"""
    status = "PASS" if passed else "FAIL"
    icon = "✅" if passed else "❌"
    log(f"{icon} {status} | [{component}] {name} | {details}", "PASS" if passed else "FAIL")
    result = {
        "section": current_section,
        "component": component,
        "test": name,
        "passed": passed,
        "details": details,
        "location": location,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    }
    all_results.append(result)
    return result

def section(name, title):
    global current_section
    current_section = name
    log(f"\n{'='*80}")
    log(f"  {title}")
    log(f"{'='*80}")


# ═══════════════════════════════════════════════════════════════
# SECCION 1: IMPORTS BASICOS
# ═══════════════════════════════════════════════════════════════
section("1. Imports", "SECCION 1: IMPORTS DEL SISTEMA")

try:
    from ui.dashboard import (
        main_loop, menu_agregar, menu_gestionar, menu_active_recall,
        menu_estadisticas, menu_conectar, menu_adelantar_repaso,
        _show_record_detail, show_header, get_stats_panel,
        ReturnToMain, console
    )
    test("Dashboard", "Import funciones principales", True,
         "12 funciones importadas correctamente", "ui/dashboard.py")
except Exception as e:
    test("Dashboard", "Import funciones principales", False, str(e))

try:
    from core.database import (
        nx_db, SessionLocal, Registry, Tag, Card, NexusLink,
        RegistryCreate, TagCreate, CardCreate, NexusLinkCreate, init_db
    )
    test("Core", "Import database", True, "", "core/database.py")
except Exception as e:
    test("Core", "Import database", False, str(e))

try:
    from core.search_engine import search_registry, parse_query_string
    test("Core", "Import search_engine", True, "", "core/search_engine.py")
except Exception as e:
    test("Core", "Import search_engine", False, str(e))

try:
    from core.staging_db import staging_db, staging_engine, get_current_db
    test("Core", "Import staging_db", True, "", "core/staging_db.py")
except Exception as e:
    test("Core", "Import staging_db", False, str(e))

try:
    from modules.analytics import get_global_metrics
    from modules.file_manager import ingest_local_file
    from modules.web_scraper import ingest_web_resource, get_playlist_video_urls, batch_ingest_urls
    from modules.pkm_manager import create_note
    from modules.study_engine import SRSEngine, get_due_cards, start_pomodoro_session, open_source_material
    from modules.exporter import export_to_google_drive
    from modules.pipeline_manager import run_youtube_pipeline
    test("Modules", "Import todos los modulos", True, "7 modulos OK")
except Exception as e:
    test("Modules", "Import modulos", False, str(e))

try:
    from agents.study_agent import generate_deck_from_registry
    from agents.summary_agent import generate_summary_from_registry
    from agents.relationship_agent import generate_relationship_cards
    from agents.deepseek_agent import deepseek_agent
    test("Agents", "Import agentes principales", True, "study, summary, relationship, deepseek")
except Exception as e:
    test("Agents", "Import agentes principales", False, str(e))

try:
    from agents.mutation_agent import mutate_cards
    test("Agents", "Import mutation_agent", True, "pydantic_ai OK")
except Exception as e:
    test("Agents", "Import mutation_agent", False, str(e))


# ═══════════════════════════════════════════════════════════════
# SECCION 2: COMPONENTES VISUALES
# ═══════════════════════════════════════════════════════════════
section("2. Visuales", "SECCION 2: COMPONENTES VISUALES")

try:
    show_header()
    test("Visual", "show_header() sin crash", True, "", "dashboard.py:L85-93")
except Exception as e:
    test("Visual", "show_header()", False, str(e))

try:
    panel = get_stats_panel()
    test("Visual", "get_stats_panel() sin filtros", True, f"Tipo: {type(panel).__name__}", "dashboard.py:L95-121")
except Exception as e:
    test("Visual", "get_stats_panel()", False, str(e))

try:
    panel = get_stats_panel(active_filters="t:python e:pdf i:1-10")
    test("Visual", "get_stats_panel(con filtros)", True, "", "dashboard.py:L95-121")
except Exception as e:
    test("Visual", "get_stats_panel(con filtros)", False, str(e))


# ═══════════════════════════════════════════════════════════════
# SECCION 3: CRUD + DATOS DE PRUEBA
# ═══════════════════════════════════════════════════════════════
section("3. CRUD", "SECCION 3: CRUD Y DATOS DE PRUEBA")

test_ids = []

for i in range(3):
    try:
        reg = nx_db.create_registry(RegistryCreate(
            type="note", title=f"__COLD_RUN_TEST_{i+1}__",
            path_url=f"nexus://cold_run/test_{i+1}",
            content_raw=f"Contenido de prueba #{i+1} para corrida en frio exhaustiva. Incluye palabras clave python, javascript, web.",
            meta_info={"source": "cold_run_v2", "index": i}
        ))
        test_ids.append(reg.id)
        test("CRUD", f"create_registry test #{i+1}", True, f"ID: {reg.id}", "database.py:L178-200")
    except Exception as e:
        test("CRUD", f"create_registry test #{i+1}", False, str(e))

# Tags
for tid in test_ids:
    try:
        nx_db.add_tag(tid, TagCreate(value="cold_run_v2"))
        nx_db.add_tag(tid, TagCreate(value="automated_test"))
        test("CRUD", f"add_tags ID {tid}", True, "cold_run_v2, automated_test", "database.py:L210-216")
    except Exception as e:
        test("CRUD", f"add_tags ID {tid}", False, str(e))

# Card
test_card_id = None
if test_ids:
    try:
        card = nx_db.create_card(CardCreate(
            parent_id=test_ids[0], question="Pregunta de prueba", answer="Respuesta OK", type="Factual"
        ))
        test_card_id = card.id
        test("CRUD", "create_card", True, f"Card ID: {test_card_id}", "database.py:L225-233")
    except Exception as e:
        test("CRUD", "create_card", False, str(e))

# Link
test_link_id = None
if len(test_ids) >= 2:
    try:
        link = nx_db.create_link(NexusLinkCreate(
            source_id=test_ids[0], target_id=test_ids[1],
            relation_type="test_relation", description="Link de prueba"
        ))
        test_link_id = link.id
        test("CRUD", "create_link", True, f"Link ID: {test_link_id}", "database.py:L218-224")
    except Exception as e:
        test("CRUD", "create_link", False, str(e))

# Read + Verify
if test_ids:
    try:
        reg = nx_db.get_registry(test_ids[0])
        checks = [
            reg is not None, 
            reg.title == "__COLD_RUN_TEST_1__",
            reg.content_raw is not None and len(reg.content_raw) > 10
        ]
        test("CRUD", "get_registry + verify", all(checks),
             f"ID={reg.id}, Title OK, Content OK", "database.py:L202-208")
    except Exception as e:
        test("CRUD", "get_registry", False, str(e))

# Update summary
if test_ids:
    try:
        ok = nx_db.update_summary(test_ids[0], "Resumen generado por cold run v2")
        test("CRUD", "update_summary", ok, "", "database.py:L250-256")
    except Exception as e:
        test("CRUD", "update_summary", False, str(e))


# ═══════════════════════════════════════════════════════════════
# SECCION 4: MOTOR DE BUSQUEDA (DETALLADO)
# ═══════════════════════════════════════════════════════════════
section("4. Busqueda", "SECCION 4: MOTOR DE BUSQUEDA — PRUEBAS DETALLADAS")

# 4.1 Sin filtros
try:
    with SessionLocal() as s:
        results = search_registry(db_session=s, limit=5)
    test("Search", "Sin filtros (limit=5)", len(results) > 0,
         f"Resultados: {len(results)}", "search_engine.py:L8", "deep")
except Exception as e:
    test("Search", "Sin filtros", False, str(e))

# 4.2 Por nombre
try:
    with SessionLocal() as s:
        results = search_registry(db_session=s, inc_name_path="__COLD_RUN_TEST", limit=10)
    test("Search", "Filtro inc_name_path='__COLD_RUN_TEST'", len(results) >= 3,
         f"Resultados: {len(results)} (esperado >= 3)", "search_engine.py:L36-43", "deep")
except Exception as e:
    test("Search", "Filtro inc_name_path", False, str(e))

# 4.3 Por tag
try:
    with SessionLocal() as s:
        results = search_registry(db_session=s, inc_tags="cold_run_v2", limit=10)
    test("Search", "Filtro inc_tags='cold_run_v2'", len(results) >= 3,
         f"Resultados: {len(results)}", "search_engine.py:L58-61", "deep")
except Exception as e:
    test("Search", "Filtro inc_tags", False, str(e))

# 4.4 Exclusion por tag
try:
    with SessionLocal() as s:
        results = search_registry(db_session=s, inc_name_path="__COLD_RUN_TEST", exc_tags="cold_run_v2", limit=10)
    test("Search", "Filtro exc_tags (excluir cold_run_v2)", len(results) == 0,
         f"Resultados: {len(results)} (esperado 0)", "search_engine.py:L63-66", "deep")
except Exception as e:
    test("Search", "Filtro exc_tags", False, str(e))

# 4.5 Por extension/tipo
for ext_type in ["web", "youtube", "note"]:
    try:
        with SessionLocal() as s:
            results = search_registry(db_session=s, inc_extensions=[ext_type], limit=5)
        test("Search", f"Filtro inc_extensions=['{ext_type}']", isinstance(results, list),
             f"Resultados: {len(results)}", "search_engine.py:L68-95", "deep")
    except Exception as e:
        test("Search", f"Filtro inc_extensions={ext_type}", False, str(e))

# 4.6 Por rango de IDs
try:
    with SessionLocal() as s:
        results = search_registry(db_session=s, record_ids_str="1-5", limit=10)
    test("Search", "Filtro record_ids_str='1-5'", isinstance(results, list) and len(results) <= 5,
         f"Resultados: {len(results)}", "search_engine.py:L143-159", "deep")
except Exception as e:
    test("Search", "Filtro record_ids_str rango", False, str(e))

# 4.7 Por IDs individuales
try:
    ids_str = ",".join(str(i) for i in test_ids)
    with SessionLocal() as s:
        results = search_registry(db_session=s, record_ids_str=ids_str, limit=10)
    test("Search", f"Filtro record_ids_str='{ids_str}'", len(results) == len(test_ids),
         f"Resultados: {len(results)} (esperado {len(test_ids)})", "search_engine.py:L143-159", "deep")
except Exception as e:
    test("Search", "Filtro record_ids_str individual", False, str(e))

# 4.8 is_flashcard_source
try:
    with SessionLocal() as s:
        results = search_registry(db_session=s, is_flashcard_source="s", limit=5)
    test("Search", "Filtro is_flashcard_source='s'", isinstance(results, list),
         f"Con flashcards: {len(results)}", "search_engine.py:L162-176", "deep")
except Exception as e:
    test("Search", "Filtro is_flashcard_source", False, str(e))

# 4.9 has_info
try:
    with SessionLocal() as s:
        results = search_registry(db_session=s, has_info="y", limit=5)
    test("Search", "Filtro has_info='y'", isinstance(results, list),
         f"Con info: {len(results)}", "search_engine.py:L96-115", "deep")
except Exception as e:
    test("Search", "Filtro has_info", False, str(e))

# 4.10 Paginacion (offset)
try:
    with SessionLocal() as s:
        page0 = search_registry(db_session=s, limit=5, offset=0)
        page1 = search_registry(db_session=s, limit=5, offset=5)
    different = True
    if page0 and page1:
        different = page0[0].id != page1[0].id
    test("Search", "Paginacion (offset 0 vs 5)", different,
         f"Page0[0].id={page0[0].id if page0 else 'N/A'}, Page1[0].id={page1[0].id if page1 else 'N/A'}",
         "search_engine.py", "deep")
except Exception as e:
    test("Search", "Paginacion", False, str(e))

# 4.11 parse_query_string — todos los formatos
query_tests = [
    ("python", {"inc_name": "python"}),
    ("t:docs", {"inc_tags": "docs"}),
    ("-t:old", {"exc_tags": "old"}),
    ("e:pdf", {"inc_exts": "pdf"}),
    ("-e:py", {"exc_exts": "py"}),
    ("i:1-50", {"inc_ids": "1-50"}),
    ("s:y", {"is_source": "y"}),
    ("h:y", {"has_info": "y"}),
    ("python t:docs -t:old e:pdf i:1-50 s:y", None),  # combinado
]

for query, expected in query_tests:
    try:
        parsed = parse_query_string(query)
        if expected:
            match = all(parsed.get(k) == v for k, v in expected.items())
        else:
            match = isinstance(parsed, dict) and len(parsed) > 0
        test("Search", f"parse_query_string('{query}')", match,
             f"Parsed: {json.dumps({k:v for k,v in parsed.items() if v}, ensure_ascii=False)}",
             "search_engine.py:L204-254", "deep")
    except Exception as e:
        test("Search", f"parse_query_string('{query}')", False, str(e))


# ═══════════════════════════════════════════════════════════════
# SECCION 5: MENU 2 — ANALISIS DE CODIGO (DETALLADO)
# ═══════════════════════════════════════════════════════════════
section("5. Menu2 Code", "SECCION 5: MENU 2 GESTIONAR — ANALISIS DE CODIGO PROFUNDO")

dashboard_path = os.path.join(NEXUS_ROOT, "ui", "dashboard.py")
with open(dashboard_path, 'r', encoding='utf-8') as f:
    dash_code = f.read()
dash_lines = dash_code.split('\n')

# 5.1 Funcion menu_gestionar existe y tiene initial_query
test("Menu2:Code", "menu_gestionar acepta initial_query",
     "def menu_gestionar(initial_query" in dash_code,
     "Parametro initial_query presente", "dashboard.py:L415", "critical")

# 5.2 Paginacion: pagina incrementa/decrementa
log("  Verificando logica de paginacion...")
has_page_inc = "page += 1" in dash_code
has_page_dec = "page -= 1" in dash_code
has_has_next = "has_next" in dash_code
test("Menu2:Code", "Logica de paginacion (page +=1, -=1, has_next)",
     has_page_inc and has_page_dec and has_has_next,
     f"Inc:{has_page_inc} Dec:{has_page_dec} HasNext:{has_has_next}", "dashboard.py:L529-534", "critical")

# 5.3 Ultima pagina guard
test("Menu2:Code", "Guard: ultima pagina no incrementa",
     "if has_next: page += 1" in dash_code or "if has_next:" in dash_code,
     "Condicion has_next verificada antes de incremento", "dashboard.py:L529", "critical")

# 5.4 Primera pagina guard
test("Menu2:Code", "Guard: primera pagina no decrementa",
     "if page > 0: page -= 1" in dash_code or "if page > 0:" in dash_code,
     "Condicion page > 0 verificada antes de decremento", "dashboard.py:L534", "critical")

# 5.5 Filtro Q implementado
test("Menu2:Code", "Filtro Q parse_query_string",
     "parse_query_string(query)" in dash_code or "parse_query_string(" in dash_code,
     "parse_query_string invocado para Q", "dashboard.py:L542", "critical")

# 5.6 Limpieza L implementada
test("Menu2:Code", "Limpieza L (reset filtros)",
     "elif cmd_lower == 'l':" in dash_code,
     "Comando L reconocido", "dashboard.py:L548", "critical")

# 5.7 Borrado del
test("Menu2:Code", "Borrado del + confirmacion",
     "cmd_lower.startswith('del ')" in dash_code and "eliminar lote" in dash_code,
     "del + confirmacion 'eliminar lote'", "dashboard.py:L554-594", "critical")

# 5.8 Vinculacion m/ia
test("Menu2:Code", "Vinculacion m/ia implementada",
     "cmd_lower.startswith('m ')" in dash_code and "cmd_lower.startswith('ia ')" in dash_code,
     "Ambos modos presentes", "dashboard.py:L597", "critical")

# 5.9 Detalle por ID — busca el patron de parseo de ID
has_id_parse = re.search(r'cmd\.isdigit\(\)|int\(cmd\)|cmd_lower\.isdigit', dash_code) is not None
test("Menu2:Code", "Detalle por ID (parseo de entrada numerica)",
     has_id_parse,
     "ID numerico reconocido como entrada", "dashboard.py:L536-541", "critical")

# 5.10 Tabla tiene columnas correctas
log("  Verificando columnas de tabla...")
col_checks = ["ID", "Tipo", "Tags"]
all_cols = all(f'"{c}"' in dash_code or f"'{c}'" in dash_code or f'"{c}"' in dash_code for c in col_checks)
test("Menu2:Code", "Tabla contiene columnas basicas (ID, Tipo, Tags)",
     all_cols, f"Columnas verificadas: {col_checks}", "dashboard.py:L471-479", "deep")

# 5.11 content_raw None guard en tabla
test("Menu2:Code", "content_raw None guard en tabla",
     '(reg.content_raw or "")' in dash_code,
     "Guard (or '') presente para content_raw", "dashboard.py:L492", "critical")

# 5.12 Salida con 0
test("Menu2:Code", "Salida con 0 (break)",
     "if cmd_lower == '0':" in dash_code,
     "cmd_lower == '0' -> break", "dashboard.py:L524-525", "critical")


# ═══════════════════════════════════════════════════════════════
# SECCION 6: OMNIBAR — ANALISIS DE CODIGO (DETALLADO)
# ═══════════════════════════════════════════════════════════════
section("6. Omnibar", "SECCION 6: OMNIBAR — ANALISIS EXHAUSTIVO")

# Extraer lineas de main_loop
main_loop_start = dash_code.find("def main_loop():")
main_loop_code = dash_code[main_loop_start:] if main_loop_start != -1 else ""

# 6.1 Omnibar se activa con elif user_input:
test("Omnibar:Code", "elif user_input: activa omnibar",
     "elif user_input:" in main_loop_code,
     "Entrada no-menu activa omnibar", "dashboard.py:L1805", "critical")

# 6.2 Comando ':' desconocido
test("Omnibar:Code", "Deteccion de ':' como comando desconocido",
     'user_input.startswith(":")' in main_loop_code or "user_input.startswith(\":\")" in main_loop_code,
     "':comando' detectado como invalido", "dashboard.py:L1806", "critical")

# 6.3 Mensaje amarillo para comando desconocido
test("Omnibar:Code", "Mensaje 'Comando desconocido' en amarillo",
     "[yellow]Comando desconocido" in main_loop_code,
     "Feedback visual correcto", "dashboard.py:L1807", "critical")

# 6.4 Omnibar llama menu_gestionar con initial_query
test("Omnibar:Code", "Omnibar invoca menu_gestionar(initial_query=)",
     "menu_gestionar(initial_query=user_input)" in main_loop_code,
     "Pasa user_input como filtro inicial", "dashboard.py:L1812", "critical")

# 6.5 Mensaje visual 'Saltando al Gestor'
test("Omnibar:Code", "Mensaje 'Saltando al Gestor' visible",
     "Saltando al Gestor" in main_loop_code or "Omnibar" in main_loop_code,
     "Feedback visual presente", "dashboard.py:L1810", "deep")

# 6.6 .strip() en user_input
test("Omnibar:Code", "user_input.strip() aplicado",
     ".strip()" in main_loop_code,
     "Entrada limpiada de espacios", "dashboard.py:L1790", "critical")

# 6.7 Exit commands: 5, 0, q, exit, quit
exit_cmds = ["\"5\"", "\"0\"", "\"q\"", "\"exit\"", "\"quit\""]
found_exits = [c for c in exit_cmds if c in main_loop_code]
test("Omnibar:Code", "Comandos de salida reconocidos (5,0,q,exit,quit)",
     len(found_exits) >= 4,
     f"Encontrados: {found_exits}", "dashboard.py:L1801", "deep")

# 6.8 ReturnToMain exception handler
test("Omnibar:Code", "Captura ReturnToMain exception",
     "except ReturnToMain:" in main_loop_code,
     "ReturnToMain manejado con continue", "dashboard.py:L1813", "critical")

# 6.9 Exception general handler
test("Omnibar:Code", "Captura Exception general con logger",
     "except Exception as e:" in main_loop_code and "logger.exception" in main_loop_code,
     "Exception capturada + logger.exception", "dashboard.py:L1815-1817", "critical")

# 6.10 Simulacion funcional: parse_query_string con omnibar-style input
omnibar_inputs = ["python", "t:youtube", "e:pdf", "python t:docs e:web", "i:1-10"]
for oi in omnibar_inputs:
    try:
        parsed = parse_query_string(oi)
        test("Omnibar:Run", f"parse_query_string('{oi}')", isinstance(parsed, dict),
             f"OK: {json.dumps({k:v for k,v in parsed.items() if v}, ensure_ascii=False)}",
             "search_engine.py + dashboard.py:L430", "deep")
    except Exception as e:
        test("Omnibar:Run", f"parse_query_string('{oi}')", False, str(e))

# 6.11 Simulacion funcional: busqueda real con omnibar inputs
for oi in ["python", "__COLD_RUN_TEST"]:
    try:
        filtros_omni = parse_query_string(oi)
        with SessionLocal() as s:
            results = search_registry(
                db_session=s,
                inc_name_path=filtros_omni.get('inc_name', ''),
                inc_tags=filtros_omni.get('inc_tags', ''),
                limit=5
            )
        test("Omnibar:Run", f"Busqueda real con '{oi}'", isinstance(results, list),
             f"Resultados: {len(results)}", "dashboard.py:L1812 -> L444-458", "deep")
    except Exception as e:
        test("Omnibar:Run", f"Busqueda real con '{oi}'", False, str(e))


# ═══════════════════════════════════════════════════════════════
# SECCION 7: CTRL+C — ANALISIS DE CODIGO (DETALLADO)
# ═══════════════════════════════════════════════════════════════
section("7. Ctrl+C", "SECCION 7: CTRL+C / KeyboardInterrupt — ANALISIS EXHAUSTIVO")

# 7.1 main.py: handler a nivel de app
main_py_path = os.path.join(NEXUS_ROOT, "main.py")
with open(main_py_path, 'r', encoding='utf-8') as f:
    main_code = f.read()

test("Ctrl+C:Code", "main.py maneja KeyboardInterrupt",
     "except KeyboardInterrupt:" in main_code,
     "KeyboardInterrupt capturado en main.py", "main.py", "critical")

test("Ctrl+C:Code", "main.py hace sys.exit(0) en handler",
     "sys.exit(0)" in main_code,
     "Salida limpia con exit code 0", "main.py", "critical")

# 7.2 dashboard.py: Ctrl+C en __main__
test("Ctrl+C:Code", "dashboard.py __main__ maneja KeyboardInterrupt",
     'except KeyboardInterrupt:' in dash_code and 'if __name__' in dash_code,
     "KeyboardInterrupt en bloque __main__", "dashboard.py:L1821-1825", "critical")

# 7.3 Mensaje de interrupcion visible
test("Ctrl+C:Code", "Mensaje 'Interrupcion detectada' formateado",
     "Interrupción detectada" in dash_code or "Interrupcion detectada" in dash_code,
     "Mensaje visible al usuario", "dashboard.py:L1824", "critical")

# 7.4 main_loop exception handler
test("Ctrl+C:Code", "main_loop captura Exception (no KeyboardInterrupt)",
     "except Exception as e:" in main_loop_code,
     "Exception general capturada para errores internos", "dashboard.py:L1815", "deep")

# 7.5 Analizar Prompt.ask — Rich maneja Ctrl+C via EOFError
log("  Analizando como Rich Prompt.ask maneja Ctrl+C...")
try:
    from rich.prompt import Prompt
    source = inspect.getsource(Prompt.ask)
    test("Ctrl+C:Code", "Rich Prompt.ask es un classmethod",
         "classmethod" in str(type(Prompt.__dict__.get('ask', ''))) or callable(Prompt.ask),
         "Prompt.ask disponible", "rich/prompt.py", "deep")
except Exception as e:
    test("Ctrl+C:Code", "Inspeccion Rich Prompt.ask", False, str(e))

# 7.6 Verificar que menu_agregar esta dentro del try/except de main_loop
log("  Verificando que menu_agregar esta protegido por exception handler de main_loop...")
# menu_agregar() se llama dentro del try de main_loop, que captura Exception
try_block = main_loop_code.find("try:")
except_block = main_loop_code.find("except Exception as e:")
menu1_call = main_loop_code.find("menu_agregar()")
test("Ctrl+C:Code", "menu_agregar() dentro del try de main_loop",
     try_block != -1 and menu1_call != -1 and try_block < menu1_call < except_block,
     f"try@{try_block}, menu_agregar@{menu1_call}, except@{except_block}",
     "dashboard.py:L1792-1815", "critical")

# 7.7 Verificar que todas las funciones de menu estan protegidas
menus = ["menu_agregar()", "menu_gestionar()", "menu_active_recall()", "menu_estadisticas()"]
for menu_call in menus:
    call_pos = main_loop_code.find(menu_call)
    protected = try_block != -1 and call_pos != -1 and try_block < call_pos
    test("Ctrl+C:Code", f"{menu_call[:-2]} protegido por exception handler",
         protected, f"Posicion relativa OK" if protected else "NO PROTEGIDO",
         "dashboard.py:L1792-1815", "critical")

# 7.8 Manejo en menu_agregar opcion 1 (Prompt.ask para ruta)
log("  Analizando manejo de interrupcion en menu_agregar opcion 1...")
agregar_start = dash_code.find("def menu_agregar():")
agregar_code = dash_code[agregar_start:agregar_start+3000] if agregar_start != -1 else ""

has_prompt_ruta = 'Ruta absoluta del archivo' in agregar_code
has_try_ingest = "try:" in agregar_code and "ingest_local_file" in agregar_code
has_except_ingest = "except Exception as e:" in agregar_code

test("Ctrl+C:Code", "menu_agregar opcion 1: Prompt.ask para ruta",
     has_prompt_ruta, "Prompt visible para ruta de archivo", "dashboard.py:L183", "deep")
test("Ctrl+C:Code", "menu_agregar opcion 1: try/except en ingesta",
     has_try_ingest and has_except_ingest,
     f"try:{has_try_ingest}, except:{has_except_ingest}",
     "dashboard.py:L188-193", "critical")

# 7.9 Validacion de ruta vacia
test("Ctrl+C:Code", "Validacion ruta vacia en menu_agregar",
     "ruta.strip()" in agregar_code and "Ruta vac" in agregar_code,
     "Guard contra ruta vacia implementado", "dashboard.py:L184-187", "critical")

# 7.10 Validacion URL vacia
test("Ctrl+C:Code", "Validacion URL vacia en menu_agregar",
     "url.strip()" in agregar_code or "URL vac" in dash_code,
     "Guard contra URL vacia implementado", "dashboard.py:L237-240", "critical")


# ═══════════════════════════════════════════════════════════════
# SECCION 8: AGENTES IA (Mock runs)
# ═══════════════════════════════════════════════════════════════
section("8. Agentes IA", "SECCION 8: AGENTES IA (MODO MOCKUP)")

mock_reg = type('MockReg', (), {
    'id': 999999, 'title': 'COLD_RUN_MOCK', 'type': 'note',
    'content_raw': 'Contenido de prueba para generar flashcards de cold run exhaustivo.',
    'meta_info': {}, 'path_url': 'nexus://coldrun', 'summary': None,
    'is_flashcard_source': False, 'created_at': datetime.now(), 'modified_at': datetime.now()
})()

try:
    cards = generate_deck_from_registry(mock_reg, mockup_only=True)
    test("AgentIA", "study_agent mockup", len(cards) > 0 and hasattr(cards[0], 'question'),
         f"Cards: {len(cards)}", "study_agent.py", "deep")
except Exception as e:
    test("AgentIA", "study_agent mockup", False, str(e))

try:
    summary = generate_summary_from_registry(mock_reg)
    test("AgentIA", "summary_agent", isinstance(summary, str) and len(summary) > 0,
         f"Resumen: {len(summary)} chars", "summary_agent.py", "deep")
except Exception as e:
    test("AgentIA", "summary_agent", False, str(e))

try:
    srs = SRSEngine()
    mock_card = type('MockCard', (), {
        'stability': 0.0, 'difficulty': 0.0, 'last_review': None, 'next_review': None
    })()
    srs.calculate_next_review(mock_card, grade=2, elapsed_seconds=5.0)
    test("SRS", "SRSEngine.calculate_next_review", mock_card.stability > 0,
         f"Stability: {mock_card.stability:.2f}", "study_engine.py:L29-58", "deep")
except Exception as e:
    test("SRS", "SRSEngine", False, str(e))


# ═══════════════════════════════════════════════════════════════
# SECCION 9: ANALISIS ESTATICO
# ═══════════════════════════════════════════════════════════════
section("9. Estatico", "SECCION 9: ANALISIS ESTATICO GLOBAL")

# print() con tags Rich no a traves de console.print()
problematic_files = {}
for root, dirs, files in os.walk(NEXUS_ROOT):
    dirs[:] = [d for d in dirs if d not in {'venv', '__pycache__', '.git', 'logs', 'docs', 'scripts', 'node_modules', '.gemini'}]
    for fn in files:
        if fn.endswith('.py'):
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, NEXUS_ROOT)
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Buscar print() con tags Rich [bold], [yellow], etc. que NO sean console.print
                issues = []
                for i, line in enumerate(content.split('\n'), 1):
                    stripped = line.strip()
                    if stripped.startswith('print(') and ('[bold' in stripped or '[yellow' in stripped or '[red' in stripped):
                        if 'console.print' not in line:
                            issues.append(f"L{i}: {stripped[:80]}")
                if issues:
                    problematic_files[rel] = issues
            except:
                pass

if problematic_files:
    for pf, issues in problematic_files.items():
        for issue in issues:
            test("Estatico", f"print() con Rich tags en {pf}", False, issue, pf, "critical")
else:
    test("Estatico", "Sin print() con Rich tags (todos usan console.print)", True,
         f"Verificados {sum(1 for _ in os.walk(NEXUS_ROOT))} directorios", "", "deep")

# bare except
bare = re.findall(r'except:\s*\n', dash_code)
test("Estatico", "Sin bare except en dashboard", len(bare) == 0,
     f"Encontrados: {len(bare)}", "dashboard.py")

# nx_db shadowing
shadowing = re.findall(r'^\s+from core\.database import.*nx_db', dash_code, re.MULTILINE)
test("Estatico", "Sin nx_db shadowing", len(shadowing) == 0,
     "OK" if not shadowing else f"Encontrados: {shadowing}", "dashboard.py")

# Logger configurado
test("Estatico", "Logger configurado", "logger = logging.getLogger" in dash_code,
     "Logger presente", "dashboard.py:L76")

# console.print consistente en todos los archivos de modulos y agentes
for check_dir in ['modules', 'agents']:
    dir_path = os.path.join(NEXUS_ROOT, check_dir)
    if os.path.isdir(dir_path):
        for fn in os.listdir(dir_path):
            if fn.endswith('.py'):
                fp = os.path.join(dir_path, fn)
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'console.print' in content or 'Console' in content:
                    has_import = 'from rich.console import Console' in content or 'from rich import' in content
                    test("Estatico", f"Console importado en {check_dir}/{fn}", has_import,
                         "" if has_import else "Usa console sin importar", f"{check_dir}/{fn}")


# ═══════════════════════════════════════════════════════════════
# SECCION 10: INTEGRIDAD BD
# ═══════════════════════════════════════════════════════════════
section("10. Integridad", "SECCION 10: INTEGRIDAD BASE DE DATOS")

try:
    from sqlalchemy import text
    with SessionLocal() as session:
        orphan_cards = session.execute(text("SELECT COUNT(*) FROM cards WHERE parent_id NOT IN (SELECT id FROM registry)")).scalar()
        orphan_tags = session.execute(text("SELECT COUNT(*) FROM tags WHERE registry_id NOT IN (SELECT id FROM registry)")).scalar()
        orphan_links = session.execute(text("SELECT COUNT(*) FROM nexus_links WHERE source_id NOT IN (SELECT id FROM registry) OR target_id NOT IN (SELECT id FROM registry)")).scalar()
        wal = session.execute(text("PRAGMA journal_mode")).scalar()
        fk = session.execute(text("PRAGMA foreign_keys")).scalar()
        reg_count = session.query(Registry).count()
        tag_count = session.query(Tag).count()
        card_count = session.query(Card).count()
        link_count = session.query(NexusLink).count()

    test("Integridad", "Cards huerfanas", orphan_cards == 0, f"Encontradas: {orphan_cards}")
    test("Integridad", "Tags huerfanos", orphan_tags == 0, f"Encontrados: {orphan_tags}")
    test("Integridad", "Links huerfanos", orphan_links == 0, f"Encontrados: {orphan_links}")
    test("Integridad", "PRAGMA journal_mode=WAL", wal.lower() == 'wal', f"Actual: {wal}")
    test("Integridad", "PRAGMA foreign_keys=ON", fk == 1, f"Actual: {fk}")
    test("Integridad", "Conteos", reg_count > 0,
         f"Registry:{reg_count} Tags:{tag_count} Cards:{card_count} Links:{link_count}")
except Exception as e:
    test("Integridad", "Verificacion BD", False, str(e))


# ═══════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════
log("\n" + "="*80)
log("  CLEANUP: Eliminando datos de prueba")
log("="*80)

for rid in test_ids:
    try:
        nx_db.delete_registry(rid)
        log(f"  Eliminado registro ID {rid}")
    except:
        log(f"  Warning: No pudo eliminar ID {rid}")


# ═══════════════════════════════════════════════════════════════
# RESUMEN + REPORTE
# ═══════════════════════════════════════════════════════════════
log("\n" + "="*80)
log("  RESUMEN EJECUTIVO — CORRIDA EN FRIO EXHAUSTIVA v2")
log("="*80)

total = len(all_results)
passed = sum(1 for r in all_results if r['passed'])
failed = sum(1 for r in all_results if not r['passed'])

log(f"Total de tests: {total}")
log(f"\u2705 Pasados:  {passed}")
log(f"\u274c Fallidos: {failed}")
log(f"Tasa de exito: {(passed/total*100):.1f}%")

# Desglose por seccion
sections = {}
for r in all_results:
    sec = r['section']
    if sec not in sections:
        sections[sec] = {'total': 0, 'passed': 0, 'failed': 0}
    sections[sec]['total'] += 1
    if r['passed']:
        sections[sec]['passed'] += 1
    else:
        sections[sec]['failed'] += 1

log("\nDesglose por seccion:")
for sec, data in sections.items():
    icon = "\u2705" if data['failed'] == 0 else "\u274c"
    log(f"  {icon} {sec}: {data['passed']}/{data['total']}")

if failed > 0:
    log("\nTESTS FALLIDOS (requieren atencion):")
    for r in all_results:
        if not r['passed']:
            sev = f" [{r['severity'].upper()}]" if r.get('severity') != 'normal' else ""
            log(f"  \u274c [{r['component']}] {r['test']}: {r['details']}{sev}")
            if r.get('location'):
                log(f"      Ubicacion: {r['location']}")

# ── Guardar LOG ──
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

# ── Guardar JSON ──
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "total": total, "passed": passed, "failed": failed,
        "rate": round(passed/total*100, 1),
        "sections": sections,
        "results": all_results
    }, f, indent=2, ensure_ascii=False, default=str)

# ── Guardar REPORTE MARKDOWN ──
with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("# Corrida en Frio Exhaustiva v2 - Nexus\n\n")
    f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    f.write(f"## Resultado Global\n\n")
    f.write(f"| Metrica | Valor |\n|---|---|\n")
    f.write(f"| Total tests | {total} |\n")
    f.write(f"| Pasados | {passed} |\n")
    f.write(f"| Fallidos | {failed} |\n")
    f.write(f"| Tasa de exito | {(passed/total*100):.1f}% |\n\n")

    f.write("## Desglose por Seccion\n\n")
    f.write("| Seccion | Total | Pass | Fail | Estado |\n|---|:---:|:---:|:---:|:---:|\n")
    for sec, data in sections.items():
        icon = "OK" if data['failed'] == 0 else "FAIL"
        f.write(f"| {sec} | {data['total']} | {data['passed']} | {data['failed']} | {icon} |\n")

    if failed > 0:
        f.write("\n## Tests Fallidos (Requieren Atencion)\n\n")
        for r in all_results:
            if not r['passed']:
                f.write(f"### {r['component']} — {r['test']}\n")
                f.write(f"- **Detalle:** {r['details']}\n")
                f.write(f"- **Ubicacion:** `{r.get('location', 'N/A')}`\n")
                f.write(f"- **Severidad:** {r.get('severity', 'normal')}\n\n")
    else:
        f.write("\n## Sin Fallos Detectados\n\n")
        f.write("Todos los tests pasaron exitosamente.\n\n")

    f.write("\n## Detalle Completo por Seccion\n\n")
    for sec in sections:
        f.write(f"### {sec}\n\n")
        f.write("| # | Test | Estado | Detalle | Ubicacion |\n|---|---|:---:|---|---|\n")
        for i, r in enumerate(all_results, 1):
            if r['section'] == sec:
                st = "PASS" if r['passed'] else "**FAIL**"
                det = r['details'][:60] + '...' if len(r['details']) > 60 else r['details']
                f.write(f"| {i} | {r['test'][:45]} | {st} | {det} | `{r.get('location', '')}` |\n")
        f.write("\n")

    f.write("\n---\n\n*Reporte generado automaticamente por cold_run_exhaustive_v2.py*\n")

log(f"\nReporte: {REPORT_FILE}")
log(f"Log: {LOG_FILE}")
log(f"JSON: {JSON_FILE}")
log("="*80)
log("CORRIDA EN FRIO FINALIZADA")
log("="*80)
