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

def reset_sequence(neon_db, table_name: str, column_name: str = "id", log_func=print):
    """Ajusta la secuencia de una tabla usando pg_get_serial_sequence (robusto)."""
    result = neon_db.execute(text(
        f"SELECT pg_get_serial_sequence('{table_name}', '{column_name}')"
    )).scalar()
    
    if result is None:
        log_func(f"  AVISO: No se encontró secuencia para {table_name}.{column_name} — omitiendo.")
        return

    neon_db.execute(text(
        f"SELECT setval('{result}', COALESCE((SELECT MAX({column_name}) FROM {table_name}), 1))"
    ))
    log_func(f"  OK: Secuencia '{result}' ajustada.")

def migrate_data(progress_callback=None):
    def report(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    report("Iniciando migración de datos a Neon...")
    
    if not test_connection(neon_engine):
        report("La prueba de conexión inicial falló. Abortando migración.")
        return

    report("\n[1/2] Creando tablas en Neon...")
    CoreBase.metadata.create_all(bind=neon_engine)
    CloudBase.metadata.create_all(bind=neon_engine)
    report("  OK: Tablas creadas (o ya existían).")
    
    sqlite_db = SqliteSessionLocal()
    neon_db = NeonSessionLocal()
    
    try:
        report("\n[2/2] Migrando datos...")

        report("  Migrando Registry...")
        registries = sqlite_db.query(Registry).all()
        total_reg = len(registries)
        for i, reg in enumerate(registries):
            neon_db.merge(reg)
            if i > 0 and i % 50 == 0:
                report(f"  Migrando Registry: {i}/{total_reg} procesados...")
        neon_db.commit()
        report(f"  OK: {total_reg} registros.")

        report("  Migrando Tags...")
        tags = sqlite_db.query(Tag).all()
        total_tags = len(tags)
        for i, t in enumerate(tags):
            neon_db.merge(t)
            if i > 0 and i % 50 == 0:
                report(f"  Migrando Tags: {i}/{total_tags} procesados...")
        neon_db.commit()
        report(f"  OK: {total_tags} registros.")

        report("  Migrando NexusLinks...")
        links = sqlite_db.query(NexusLink).all()
        total_links = len(links)
        for i, link in enumerate(links):
            neon_db.merge(link)
            if i > 0 and i % 50 == 0:
                report(f"  Migrando NexusLinks: {i}/{total_links} procesados...")
        neon_db.commit()
        report(f"  OK: {total_links} registros.")

        report("  Migrando Cards...")
        cards = sqlite_db.query(Card).all()
        total_cards = len(cards)
        for i, card in enumerate(cards):
            neon_db.merge(card)
            if i > 0 and i % 50 == 0:
                report(f"  Migrando Cards: {i}/{total_cards} procesados...")
        neon_db.commit()
        report(f"  OK: {total_cards} registros.")

        report("\n[3/3] Ajustando secuencias en PostgreSQL...")
        reset_sequence(neon_db, "registry", log_func=report)
        reset_sequence(neon_db, "nexus_links", log_func=report)
        reset_sequence(neon_db, "cards", log_func=report)
        neon_db.commit()

        report("\n✓ MIGRACIÓN COMPLETADA CON ÉXITO")

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
