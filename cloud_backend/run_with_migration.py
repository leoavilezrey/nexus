import os
from fastapi import FastAPI
from cloud_backend.main import app as main_app

app = FastAPI(title="Migration Wrapper App")

@app.get("/api/run-migration", tags=["Sistema"])
def run_migration_endpoint():
    """Endpoint temporal para disparar la migración desde el navegador"""
    try:
        import importlib.util
        # Buscamos de forma segura el script migrate_sqlite_to_neon.py
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "migrate_sqlite_to_neon.py")
        spec = importlib.util.spec_from_file_location("migrate_module", script_path)
        migrate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migrate_module)
        
        migrate_module.migrate_data()
        return {"status": "success", "message": "Migración ejecutada exitosamente. Revisa tu base de datos Neon!"}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

app.mount("/", main_app)
