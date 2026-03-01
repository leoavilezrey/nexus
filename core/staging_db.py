
import os
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from core.database import Base, NexusCRUD, Registry, RegistryCreate, nx_db
from rich.console import Console

console = Console()

# 1. Definir la ruta en G: (Google Drive)
STAGING_DB_DIR = r"G:\Mi unidad\Nexus_Staging"
STAGING_DB_PATH = os.path.join(STAGING_DB_DIR, "staging_buffer.db")

# Crear el engine para el buffer de G:
def get_staging_engine():
    if not os.path.exists(STAGING_DB_DIR):
        try:
            os.makedirs(STAGING_DB_DIR, exist_ok=True)
        except Exception as e:
            # Fallback a local si G: no esta montado
            console.print(f"[bold yellow]⚠ Buffer Google Drive (G:) no disponible. Operando en modo local.[/] ({e})")
            return None
    return create_engine(f"sqlite:///{STAGING_DB_PATH}")

staging_engine = get_staging_engine()

# Configurar PRAGMAs para el buffer
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session y CRUD para Staging
if staging_engine:
    StagingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=staging_engine)
else:
    StagingSessionLocal = None

class StagingCRUD(NexusCRUD):
    """
    Hereda de NexusCRUD pero apunta a la sesion del buffer en G:
    """
    def __init__(self):
        self.Session = StagingSessionLocal

    def _check_available(self):
        """Verifica que el Staging DB esté operativo antes de cualquier operación."""
        if self.Session is None:
            console.print("[bold yellow]⚠ Staging DB no disponible (G: no montado). Operación cancelada.[/]")
            return False
        return True

    def create_registry(self, data):
        if not self._check_available():
            return None
        return super().create_registry(data)

    def get_registry(self, registry_id):
        if not self._check_available():
            return None
        return super().get_registry(registry_id)

    def init_staging(self):
        if staging_engine:
            Base.metadata.create_all(bind=staging_engine)
            return True
        return False

# Instancia global del buffer
staging_db = StagingCRUD()

def get_current_db(mode="local"):
    """
    Retorna la instancia de DB activa.
    'local' -> nexus.db (SSD)
    'staging' -> staging_buffer.db (G: Drive)
    """
    if mode == "staging" and staging_engine:
        return staging_db
    return nx_db
