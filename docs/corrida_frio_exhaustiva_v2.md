# Corrida en Frio Exhaustiva v2 - Nexus

**Fecha:** 2026-03-01 10:05

## Resultado Global

| Metrica | Valor |
|---|---|
| Total tests | 107 |
| Pasados | 103 |
| Fallidos | 4 |
| Tasa de exito | 96.3% |

## Desglose por Seccion

| Seccion | Total | Pass | Fail | Estado |
|---|:---:|:---:|:---:|:---:|
| 1. Imports | 7 | 7 | 0 | OK |
| 2. Visuales | 3 | 3 | 0 | OK |
| 3. CRUD | 10 | 10 | 0 | OK |
| 4. Busqueda | 21 | 19 | 2 | FAIL |
| 5. Menu2 Code | 12 | 12 | 0 | OK |
| 6. Omnibar | 16 | 16 | 0 | OK |
| 7. Ctrl+C | 15 | 14 | 1 | FAIL |
| 8. Agentes IA | 3 | 3 | 0 | OK |
| 9. Estatico | 14 | 13 | 1 | FAIL |
| 10. Integridad | 6 | 6 | 0 | OK |

## Tests Fallidos (Requieren Atencion)

### Search — parse_query_string('s:y')
- **Detalle:** Parsed: {"is_source": "s"}
- **Ubicacion:** `search_engine.py:L204-254`
- **Severidad:** deep

### Search — parse_query_string('h:y')
- **Detalle:** Parsed: {"inc_name": "h:y"}
- **Ubicacion:** `search_engine.py:L204-254`
- **Severidad:** deep

### Ctrl+C:Code — menu_agregar opcion 1: try/except en ingesta
- **Detalle:** try:False, except:False
- **Ubicacion:** `dashboard.py:L188-193`
- **Severidad:** critical

### Estatico — Console importado en modules/youtube_manager.py
- **Detalle:** Usa console sin importar
- **Ubicacion:** `modules/youtube_manager.py`
- **Severidad:** normal


## Detalle Completo por Seccion

### 1. Imports

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 1 | Import funciones principales | PASS | 12 funciones importadas correctamente | `ui/dashboard.py` |
| 2 | Import database | PASS |  | `core/database.py` |
| 3 | Import search_engine | PASS |  | `core/search_engine.py` |
| 4 | Import staging_db | PASS |  | `core/staging_db.py` |
| 5 | Import todos los modulos | PASS | 7 modulos OK | `` |
| 6 | Import agentes principales | PASS | study, summary, relationship, deepseek | `` |
| 7 | Import mutation_agent | PASS | pydantic_ai OK | `` |

### 2. Visuales

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 8 | show_header() sin crash | PASS |  | `dashboard.py:L85-93` |
| 9 | get_stats_panel() sin filtros | PASS | Tipo: Panel | `dashboard.py:L95-121` |
| 10 | get_stats_panel(con filtros) | PASS |  | `dashboard.py:L95-121` |

### 3. CRUD

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 11 | create_registry test #1 | PASS | ID: 23804 | `database.py:L178-200` |
| 12 | create_registry test #2 | PASS | ID: 23805 | `database.py:L178-200` |
| 13 | create_registry test #3 | PASS | ID: 23806 | `database.py:L178-200` |
| 14 | add_tags ID 23804 | PASS | cold_run_v2, automated_test | `database.py:L210-216` |
| 15 | add_tags ID 23805 | PASS | cold_run_v2, automated_test | `database.py:L210-216` |
| 16 | add_tags ID 23806 | PASS | cold_run_v2, automated_test | `database.py:L210-216` |
| 17 | create_card | PASS | Card ID: 224 | `database.py:L225-233` |
| 18 | create_link | PASS | Link ID: 5 | `database.py:L218-224` |
| 19 | get_registry + verify | PASS | ID=23804, Title OK, Content OK | `database.py:L202-208` |
| 20 | update_summary | PASS |  | `database.py:L250-256` |

### 4. Busqueda

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 21 | Sin filtros (limit=5) | PASS | Resultados: 5 | `search_engine.py:L8` |
| 22 | Filtro inc_name_path='__COLD_RUN_TEST' | PASS | Resultados: 3 (esperado >= 3) | `search_engine.py:L36-43` |
| 23 | Filtro inc_tags='cold_run_v2' | PASS | Resultados: 3 | `search_engine.py:L58-61` |
| 24 | Filtro exc_tags (excluir cold_run_v2) | PASS | Resultados: 0 (esperado 0) | `search_engine.py:L63-66` |
| 25 | Filtro inc_extensions=['web'] | PASS | Resultados: 5 | `search_engine.py:L68-95` |
| 26 | Filtro inc_extensions=['youtube'] | PASS | Resultados: 5 | `search_engine.py:L68-95` |
| 27 | Filtro inc_extensions=['note'] | PASS | Resultados: 0 | `search_engine.py:L68-95` |
| 28 | Filtro record_ids_str='1-5' | PASS | Resultados: 3 | `search_engine.py:L143-159` |
| 29 | Filtro record_ids_str='23804,23805,23806' | PASS | Resultados: 3 (esperado 3) | `search_engine.py:L143-159` |
| 30 | Filtro is_flashcard_source='s' | PASS | Con flashcards: 5 | `search_engine.py:L162-176` |
| 31 | Filtro has_info='y' | PASS | Con info: 5 | `search_engine.py:L96-115` |
| 32 | Paginacion (offset 0 vs 5) | PASS | Page0[0].id=23804, Page1[0].id=23801 | `search_engine.py` |
| 33 | parse_query_string('python') | PASS | Parsed: {"inc_name": "python"} | `search_engine.py:L204-254` |
| 34 | parse_query_string('t:docs') | PASS | Parsed: {"inc_tags": "docs"} | `search_engine.py:L204-254` |
| 35 | parse_query_string('-t:old') | PASS | Parsed: {"exc_tags": "old"} | `search_engine.py:L204-254` |
| 36 | parse_query_string('e:pdf') | PASS | Parsed: {"inc_exts": "pdf"} | `search_engine.py:L204-254` |
| 37 | parse_query_string('-e:py') | PASS | Parsed: {"exc_exts": "py"} | `search_engine.py:L204-254` |
| 38 | parse_query_string('i:1-50') | PASS | Parsed: {"inc_ids": "1-50"} | `search_engine.py:L204-254` |
| 39 | parse_query_string('s:y') | **FAIL** | Parsed: {"is_source": "s"} | `search_engine.py:L204-254` |
| 40 | parse_query_string('h:y') | **FAIL** | Parsed: {"inc_name": "h:y"} | `search_engine.py:L204-254` |
| 41 | parse_query_string('python t:docs -t:old e:pd | PASS | Parsed: {"inc_name": "python", "inc_tags": "docs", "exc_tags... | `search_engine.py:L204-254` |

### 5. Menu2 Code

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 42 | menu_gestionar acepta initial_query | PASS | Parametro initial_query presente | `dashboard.py:L415` |
| 43 | Logica de paginacion (page +=1, -=1, has_next | PASS | Inc:True Dec:True HasNext:True | `dashboard.py:L529-534` |
| 44 | Guard: ultima pagina no incrementa | PASS | Condicion has_next verificada antes de incremento | `dashboard.py:L529` |
| 45 | Guard: primera pagina no decrementa | PASS | Condicion page > 0 verificada antes de decremento | `dashboard.py:L534` |
| 46 | Filtro Q parse_query_string | PASS | parse_query_string invocado para Q | `dashboard.py:L542` |
| 47 | Limpieza L (reset filtros) | PASS | Comando L reconocido | `dashboard.py:L548` |
| 48 | Borrado del + confirmacion | PASS | del + confirmacion 'eliminar lote' | `dashboard.py:L554-594` |
| 49 | Vinculacion m/ia implementada | PASS | Ambos modos presentes | `dashboard.py:L597` |
| 50 | Detalle por ID (parseo de entrada numerica) | PASS | ID numerico reconocido como entrada | `dashboard.py:L536-541` |
| 51 | Tabla contiene columnas basicas (ID, Tipo, Ta | PASS | Columnas verificadas: ['ID', 'Tipo', 'Tags'] | `dashboard.py:L471-479` |
| 52 | content_raw None guard en tabla | PASS | Guard (or '') presente para content_raw | `dashboard.py:L492` |
| 53 | Salida con 0 (break) | PASS | cmd_lower == '0' -> break | `dashboard.py:L524-525` |

### 6. Omnibar

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 54 | elif user_input: activa omnibar | PASS | Entrada no-menu activa omnibar | `dashboard.py:L1805` |
| 55 | Deteccion de ':' como comando desconocido | PASS | ':comando' detectado como invalido | `dashboard.py:L1806` |
| 56 | Mensaje 'Comando desconocido' en amarillo | PASS | Feedback visual correcto | `dashboard.py:L1807` |
| 57 | Omnibar invoca menu_gestionar(initial_query=) | PASS | Pasa user_input como filtro inicial | `dashboard.py:L1812` |
| 58 | Mensaje 'Saltando al Gestor' visible | PASS | Feedback visual presente | `dashboard.py:L1810` |
| 59 | user_input.strip() aplicado | PASS | Entrada limpiada de espacios | `dashboard.py:L1790` |
| 60 | Comandos de salida reconocidos (5,0,q,exit,qu | PASS | Encontrados: ['"5"', '"0"', '"q"', '"exit"', '"quit"'] | `dashboard.py:L1801` |
| 61 | Captura ReturnToMain exception | PASS | ReturnToMain manejado con continue | `dashboard.py:L1813` |
| 62 | Captura Exception general con logger | PASS | Exception capturada + logger.exception | `dashboard.py:L1815-1817` |
| 63 | parse_query_string('python') | PASS | OK: {"inc_name": "python"} | `search_engine.py + dashboard.py:L430` |
| 64 | parse_query_string('t:youtube') | PASS | OK: {"inc_tags": "youtube"} | `search_engine.py + dashboard.py:L430` |
| 65 | parse_query_string('e:pdf') | PASS | OK: {"inc_exts": "pdf"} | `search_engine.py + dashboard.py:L430` |
| 66 | parse_query_string('python t:docs e:web') | PASS | OK: {"inc_name": "python", "inc_tags": "docs", "inc_exts": "... | `search_engine.py + dashboard.py:L430` |
| 67 | parse_query_string('i:1-10') | PASS | OK: {"inc_ids": "1-10"} | `search_engine.py + dashboard.py:L430` |
| 68 | Busqueda real con 'python' | PASS | Resultados: 5 | `dashboard.py:L1812 -> L444-458` |
| 69 | Busqueda real con '__COLD_RUN_TEST' | PASS | Resultados: 3 | `dashboard.py:L1812 -> L444-458` |

### 7. Ctrl+C

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 70 | main.py maneja KeyboardInterrupt | PASS | KeyboardInterrupt capturado en main.py | `main.py` |
| 71 | main.py hace sys.exit(0) en handler | PASS | Salida limpia con exit code 0 | `main.py` |
| 72 | dashboard.py __main__ maneja KeyboardInterrup | PASS | KeyboardInterrupt en bloque __main__ | `dashboard.py:L1821-1825` |
| 73 | Mensaje 'Interrupcion detectada' formateado | PASS | Mensaje visible al usuario | `dashboard.py:L1824` |
| 74 | main_loop captura Exception (no KeyboardInter | PASS | Exception general capturada para errores internos | `dashboard.py:L1815` |
| 75 | Rich Prompt.ask es un classmethod | PASS | Prompt.ask disponible | `rich/prompt.py` |
| 76 | menu_agregar() dentro del try de main_loop | PASS | try@1988, menu_agregar@2043, except@3002 | `dashboard.py:L1792-1815` |
| 77 | menu_agregar protegido por exception handler | PASS | Posicion relativa OK | `dashboard.py:L1792-1815` |
| 78 | menu_gestionar protegido por exception handle | PASS | Posicion relativa OK | `dashboard.py:L1792-1815` |
| 79 | menu_active_recall protegido por exception ha | PASS | Posicion relativa OK | `dashboard.py:L1792-1815` |
| 80 | menu_estadisticas protegido por exception han | PASS | Posicion relativa OK | `dashboard.py:L1792-1815` |
| 81 | menu_agregar opcion 1: Prompt.ask para ruta | PASS | Prompt visible para ruta de archivo | `dashboard.py:L183` |
| 82 | menu_agregar opcion 1: try/except en ingesta | **FAIL** | try:False, except:False | `dashboard.py:L188-193` |
| 83 | Validacion ruta vacia en menu_agregar | PASS | Guard contra ruta vacia implementado | `dashboard.py:L184-187` |
| 84 | Validacion URL vacia en menu_agregar | PASS | Guard contra URL vacia implementado | `dashboard.py:L237-240` |

### 8. Agentes IA

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 85 | study_agent mockup | PASS | Cards: 1 | `study_agent.py` |
| 86 | summary_agent | PASS | Resumen: 913 chars | `summary_agent.py` |
| 87 | SRSEngine.calculate_next_review | PASS | Stability: 3.00 | `study_engine.py:L29-58` |

### 9. Estatico

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 88 | Sin print() con Rich tags (todos usan console | PASS | Verificados 4115 directorios | `` |
| 89 | Sin bare except en dashboard | PASS | Encontrados: 0 | `dashboard.py` |
| 90 | Sin nx_db shadowing | PASS | OK | `dashboard.py` |
| 91 | Logger configurado | PASS | Logger presente | `dashboard.py:L76` |
| 92 | Console importado en modules/file_manager.py | PASS |  | `modules/file_manager.py` |
| 93 | Console importado en modules/pipeline_manager | PASS |  | `modules/pipeline_manager.py` |
| 94 | Console importado en modules/pkm_manager.py | PASS |  | `modules/pkm_manager.py` |
| 95 | Console importado en modules/study_engine.py | PASS |  | `modules/study_engine.py` |
| 96 | Console importado en modules/web_scraper.py | PASS |  | `modules/web_scraper.py` |
| 97 | Console importado en modules/youtube_manager. | **FAIL** | Usa console sin importar | `modules/youtube_manager.py` |
| 98 | Console importado en agents/deepseek_agent.py | PASS |  | `agents/deepseek_agent.py` |
| 99 | Console importado en agents/mutation_agent.py | PASS |  | `agents/mutation_agent.py` |
| 100 | Console importado en agents/relationship_agen | PASS |  | `agents/relationship_agent.py` |
| 101 | Console importado en agents/study_agent.py | PASS |  | `agents/study_agent.py` |

### 10. Integridad

| # | Test | Estado | Detalle | Ubicacion |
|---|---|:---:|---|---|
| 102 | Cards huerfanas | PASS | Encontradas: 0 | `` |
| 103 | Tags huerfanos | PASS | Encontrados: 0 | `` |
| 104 | Links huerfanos | PASS | Encontrados: 0 | `` |
| 105 | PRAGMA journal_mode=WAL | PASS | Actual: wal | `` |
| 106 | PRAGMA foreign_keys=ON | PASS | Actual: 1 | `` |
| 107 | Conteos | PASS | Registry:19957 Tags:792 Cards:217 Links:5 | `` |


---

*Reporte generado automaticamente por cold_run_exhaustive_v2.py*
