import sys
import psycopg2

try:
    conn = psycopg2.connect("postgresql://postgres:dev@localhost:5432/nexus_dev")
    print("Conexión exitosa!")
except Exception as e:
    import traceback
    traceback.print_exc()
    if hasattr(e, 'pgerror'):
        print("pgerror:", repr(e.pgerror))
        
    try:
        print("Raw exception string representation:", repr(str(e)))
    except Exception as e2:
        print("Error al intentar imprimir el string de la excepción", e2)
