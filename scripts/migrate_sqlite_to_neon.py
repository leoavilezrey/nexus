import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurar PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cloud_backend', '.env'))

NEON_DATABASE_URL = os.environ.get('DATABASE_URL')
if not NEON_DATABASE_URL:
    print("Error: DATABASE_URL no encontrada en cloud_backend/.env")
    sys.exit(1)

from core.database import Base as CoreBase, Registry, Tag, NexusLink, Card, DB_PATH
from cloud_backend.database import Base as CloudBase
from cloud_backend.models import User

sqlite_engine = create_engine(f"sqlite:///{DB_PATH}")
SqliteSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

if NEON_DATABASE_URL.startswith("postgres://"):
    NEON_DATABASE_URL = NEON_DATABASE_URL.replace("postgres://", "postgresql://", 1)

neon_engine = create_engine(
    NEON_DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30,
    }
)
NeonSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=neon_engine)

def test_connection(engine):
    print("Probando conexión a Neon...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
            print(f"  OK: Conectado a PostgreSQL — {result[:40]}...")
            return True
    except Exception as e:
        print(f"  ERROR de conexión: {e}")
        return False

def reset_sequence(neon_db, table_name: str, column_name: str = "id"):
    """Ajusta la secuencia de una tabla usando pg_get_serial_sequence (robusto)."""
    result = neon_db.execute(text(
        f"SELECT pg_get_serial_sequence('{table_name}', '{column_name}')"
    )).scalar()
    
    if result is None:
        print(f"  AVISO: No se encontró secuencia para {table_name}.{column_name} — omitiendo.")
        return

    neon_db.execute(text(
        f"SELECT setval('{result}', COALESCE((SELECT MAX({column_name}) FROM {table_name}), 1))"
    ))
    print(f"  OK: Secuencia '{result}' ajustada.")

def migrate_data():
    print("Iniciando migración de datos a Neon...")
    
    if not test_connection(neon_engine):
        print("La prueba de conexión inicial falló. Abortando migración.")
        return

    print("\n[1/2] Creando tablas en Neon...")
    CoreBase.metadata.create_all(bind=neon_engine)
    CloudBase.metadata.create_all(bind=neon_engine)
    print("  OK: Tablas creadas (o ya existían).")
    
    sqlite_db = SqliteSessionLocal()
    neon_db = NeonSessionLocal()
    
    try:
        print("\n[2/2] Migrando datos...")

        print("  Migrando Registry...")
        registries = sqlite_db.query(Registry).all()
        for reg in registries:
            neon_db.merge(reg)
        neon_db.commit()
        print(f"  OK: {len(registries)} registros.")

        print("  Migrando Tags...")
        tags = sqlite_db.query(Tag).all()
        for t in tags:
            neon_db.merge(t)
        neon_db.commit()
        print(f"  OK: {len(tags)} registros.")

        print("  Migrando NexusLinks...")
        links = sqlite_db.query(NexusLink).all()
        for link in links:
            neon_db.merge(link)
        neon_db.commit()
        print(f"  OK: {len(links)} registros.")

        print("  Migrando Cards...")
        cards = sqlite_db.query(Card).all()
        for card in cards:
            neon_db.merge(card)
        neon_db.commit()
        print(f"  OK: {len(cards)} registros.")

        print("\n[3/3] Ajustando secuencias en PostgreSQL...")
        reset_sequence(neon_db, "registry")
        reset_sequence(neon_db, "nexus_links")
        reset_sequence(neon_db, "cards")
        neon_db.commit()

        print("\n✓ MIGRACIÓN COMPLETADA CON ÉXITO")

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        neon_db.rollback()
    finally:
        sqlite_db.close()
        neon_db.close()

if __name__ == "__main__":
    migrate_data()
