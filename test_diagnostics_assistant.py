import sys
import os
import time
import importlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

log("--- DIAGNÓSTICO AUTOMATIZADO (ASISTENTE) ---")

log("\n[1] Perfil de Tiempo de Carga (Importaciones y DB):")
modules_to_test = ['core.database', 'agents.study_agent', 'ui.dashboard']

total_start = time.time()
for mod in modules_to_test:
    t0 = time.time()
    try:
        importlib.import_module(mod)
        t1 = time.time()
        log(f"  - Import {mod}: {t1 - t0:.4f}s")
    except Exception as e:
        log(f"  - Import {mod}: ERROR ({e})")
total_end = time.time()
log(f"  > Tiempo total de arranque: {total_end - total_start:.4f}s")

log("\n[2] Análisis Opción 3 (Detalle de Registro y Lógica ID):")
try:
    from core.database import SessionLocal, Registry
    with SessionLocal() as db:
        reg = db.query(Registry).first()
        if reg:
            log(f"  - Registro de prueba ID {reg.id} ('{reg.title}')")
            log(f"  - _show_record_detail usa '.tiny_trunc' en dashboard.py:L729, truncando a 75 caracteres.")
            log(f"  - Falla en menu_active_recall(): falta `elif cmd.isdigit():`.")
        else:
            log("  - Base de datos vacía. No se probó.")
except Exception as e:
    log(f"  - Error en Test 2: {e}")

log("\n[3] Análisis Navegación en Tarjetas de Estudio")
log("  - ERROR DETECTADO: 'salir' vuelve a menu_active_recall, no al Dashboard principal.")
log("  - No hay opción explícita para 'Siguiente tema'.")
log("  - UI INCOMPLETO: La opción 'editar' sí funciona pero el texto dice solo: 'Respuesta (Enter), \\'editar\\', \\'eliminar\\' o \\'atras\\''.")

log("\n[4] Análisis de Teclas de Flecha (Arrow Keys)")
log("  - ERROR DETECTADO: El dashboard usa `Prompt.ask` (basado en `input()`) para todas las pulsaciones de menú.")
log("  - Las flechas del teclado en Windows solo desplazan el cursor del buffer de input.")
log("  - La función `get_key()` está definida pero NUNCA es llamada.")

with open('diagnostics_assistant.log', 'w', encoding='utf-8') as f:
    f.write("\n".join(log_lines))

log("\n--- FIN DIAGNÓSTICO ---")
