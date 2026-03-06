import os
import traceback
from fastapi import FastAPI, BackgroundTasks
from cloud_backend.main import app as main_app

app = FastAPI(title="Migration Wrapper App")

# Estado global para monitorear la migración en memoria
migration_state = {
    "status": "idle",  # Puede ser: idle, running, completed, failed
    "message": "Ninguna migración ejecutada recientemente.",
    "error": None
}


def _run_migration_task():
    global migration_state

    migration_state["status"] = "running"
    migration_state["message"] = "Migración en proceso. Esto puede tardar varios minutos..."
    migration_state["error"] = None

    try:
        import importlib.util

        # Buscamos de forma segura el script migrate_sqlite_to_neon.py
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scripts",
            "migrate_sqlite_to_neon.py"
        )
        spec = importlib.util.spec_from_file_location("migrate_module", script_path)
        migrate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migrate_module)

        # Ejecutar la migración
        migrate_module.migrate_data()

        migration_state["status"] = "completed"
        migration_state["message"] = "Migración ejecutada exitosamente."
        print(migration_state["message"])

    except Exception as e:
        migration_state["status"] = "failed"
        migration_state["message"] = f"Migración falló: {str(e)}"
        migration_state["error"] = traceback.format_exc()
        print(f"Error en migración: {e}")


@app.get("/api/run-migration", tags=["Sistema"])
def run_migration_endpoint(background_tasks: BackgroundTasks):
    """Endpoint para disparar la migración en segundo plano"""
    global migration_state

    if migration_state["status"] == "running":
        return {
            "status": "warning",
            "message": "Una migración ya está en curso. Por favor revisa /api/migration-status."
        }

    # Agregamos la tarea al background de FastAPI
    background_tasks.add_task(_run_migration_task)

    return {
        "status": "accepted",
        "message": "Migración iniciada en segundo plano. Consulta el endpoint /api/migration-status para ver el progreso."
    }


@app.get("/api/migration-status", tags=["Sistema"])
def get_migration_status():
    """Endpoint para monitorear el progreso de la migración"""
    global migration_state
    return migration_state


# Montamos la app principal debajo de este wrapper
app.mount("/", main_app)
