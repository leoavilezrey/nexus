import os
import json
import traceback
import tempfile
from fastapi import FastAPI, BackgroundTasks
from cloud_backend.main import app as main_app

app = FastAPI(title="Migration Wrapper App")

# Usaremos un archivo JSON en el directorio temporal o local para compartir estado entre workers
STATE_FILE = os.path.join(tempfile.gettempdir(), "nexus_migration_state.json")

def get_migration_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "status": "idle",
        "message": "Ninguna migración ejecutada recientemente.",
        "error": None
    }

def set_migration_state(status, message, error=None):
    state = {
        "status": status,
        "message": message,
        "error": error
    }
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Error escribiendo estado de migración: {e}")

def _run_migration_task():
    set_migration_state("running", "Migración en proceso. Esto puede tardar varios minutos...")

    try:
        import importlib.util

        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scripts",
            "migrate_sqlite_to_neon.py"
        )
        spec = importlib.util.spec_from_file_location("migrate_module", script_path)
        migrate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migrate_module)

        def _update_progress(msg: str):
            set_migration_state("running", msg)

        # Ejecutar la migración con progress_callback
        migrate_module.migrate_data(progress_callback=_update_progress)

        state = get_migration_state()
        if state.get("status") == "running": # Evita pisar un error interno si ya cambió el status
            set_migration_state("completed", "Migración ejecutada exitosamente.")

    except Exception as e:
        error_trace = traceback.format_exc()
        set_migration_state("failed", f"Migración falló: {str(e)}", error_trace)
        print(f"Error en migración: {e}\n{error_trace}")

@app.get("/api/run-migration", tags=["Sistema"])
def run_migration_endpoint(background_tasks: BackgroundTasks):
    """Endpoint para disparar la migración en segundo plano con estado compartido"""
    state = get_migration_state()

    if state["status"] == "running":
        return {
            "status": "warning",
            "message": "Una migración ya está en curso. Por favor revisa /api/migration-status."
        }

    # Inicializamos el estado antes de mandar al background para bloquear race-conditions 
    # de llamadas simultáneas muy rápidas (aunque no es perfecto sin atomic locks, es suficiente aquí)
    set_migration_state("running", "Iniciando proceso de migración en background...")
    
    background_tasks.add_task(_run_migration_task)

    return {
        "status": "accepted",
        "message": "Migración iniciada. Consulta /api/migration-status para ver el progreso detallado."
    }

@app.get("/api/migration-status", tags=["Sistema"])
def get_migration_status():
    """Endpoint para monitorear el progreso de la migración"""
    return get_migration_state()

# Montamos la app principal debajo de este wrapper para que sirva tanto la API temporal como el sistema normal
app.mount("/", main_app)
