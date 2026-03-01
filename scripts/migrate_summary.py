
import sqlite3
import os

# La base de datos esta en la raiz del proyecto
db_path = r'c:\Users\DELL\Proyectos\nexus\nexus.db'

if not os.path.exists(db_path):
    print(f"Error: No se encontro la base de datos en {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Intentar añadir la columna summary
        print("Anadiendo columna 'summary' a la tabla 'registry'...")
        cursor.execute("ALTER TABLE registry ADD COLUMN summary TEXT")
        
        conn.commit()
        conn.close()
        print("Exito: Columna 'summary' anidada con exito.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Aviso: La columna 'summary' ya existe.")
        else:
            print(f"Error de SQLite: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
