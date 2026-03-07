import os
import sys

# Añadir el directorio actual al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30,
    }
)

def create_migration_log_table():
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS migration_log (
                    id          SERIAL PRIMARY KEY,
                    status      VARCHAR(20)  NOT NULL DEFAULT 'idle',
                    message     TEXT,
                    error       TEXT,
                    started_at  TIMESTAMP,
                    finished_at TIMESTAMP,
                    updated_at  TIMESTAMP    DEFAULT NOW()
                );
            """))
            
            # Verificar si ya existe el registro 1
            result = conn.execute(text("SELECT id FROM migration_log WHERE id = 1")).scalar()
            if not result:
                conn.execute(text("INSERT INTO migration_log (id, status, message) VALUES (1, 'idle', 'Sin migraciones ejecutadas.')"))

        print("Tabla migration_log creada e inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la tabla: {e}")

if __name__ == "__main__":
    create_migration_log_table()
