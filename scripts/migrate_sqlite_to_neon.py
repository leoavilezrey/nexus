import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError

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

def test_connection(engine, log_func=print):
    log_func("Probando conexión a Neon...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
            log_func(f"  OK: Conectado a PostgreSQL — {result[:40]}...")
            return True
    except Exception as e:
        log_func(f"  ERROR de conexión: {e}")
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
    
    if not test_connection(neon_engine, log_func=report):
        report("La prueba de conexión inicial falló. Abortando migración.")
        return

    report("\n[1/2] Creando tablas en Neon...")
    CoreBase.metadata.create_all(bind=neon_engine)
    CloudBase.metadata.create_all(bind=neon_engine)
    report("  OK: Tablas creadas (o ya existían).")
    
    sqlite_db = SqliteSessionLocal()
    neon_db = NeonSessionLocal()
    
    def migrate_table(name, records, merge_fn):
        total = len(records)
        if total == 0:
            report(f"  {name}: sin registros.")
            return 0

        # Frecuencia dinámica: cada 10% o cada 50, lo que sea menor
        report_every = max(1, min(50, total // 10))
        skipped = 0

        for i, record in enumerate(records):
            try:
                merge_fn(record)
            except IntegrityError as e:
                neon_db.rollback()
                report(f"  ⚠️ {name} registro {i+1}: conflicto omitido — {str(e.orig)[:100]}")
                skipped += 1
                continue
            except OperationalError:
                report(f"  ❌ Error fatal de conexión procesando {name} registro {i+1}")
                raise

            if i == 0 or i == total - 1 or i % report_every == 0:
                pct = int((i + 1) / total * 100)
                report(f"  Migrando {name}: {i+1}/{total} ({pct}%) procesados...")

        neon_db.commit()
        report(f"  ✅ {name}: {total - skipped} migrados, {skipped} omitidos.")
        return skipped

    try:
        report("\n[2/2] Migrando datos...")

        migrate_table("Registry",   sqlite_db.query(Registry).all(),   neon_db.merge)
        migrate_table("Tags",       sqlite_db.query(Tag).all(),        neon_db.merge)
        migrate_table("NexusLinks", sqlite_db.query(NexusLink).all(),  neon_db.merge)
        migrate_table("Cards",      sqlite_db.query(Card).all(),       neon_db.merge)

        report("\n[3/3] Ajustando secuencias en PostgreSQL...")
        reset_sequence(neon_db, "registry", log_func=report)
        reset_sequence(neon_db, "nexus_links", log_func=report)
        reset_sequence(neon_db, "cards", log_func=report)
        neon_db.commit()

        report("\n✓ MIGRACIÓN COMPLETADA CON ÉXITO")

    except Exception as e:
        report(f"\n✗ Error fatal durante la migración: {e}")
        import traceback
        traceback.print_exc()
        neon_db.rollback()
        raise e  # Relanzamos para que run_with_migration lo atrape y lo suba a la DB logs
    finally:
        sqlite_db.close()
        neon_db.close()

if __name__ == "__main__":
    migrate_data()
