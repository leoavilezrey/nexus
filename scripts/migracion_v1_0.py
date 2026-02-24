import sys
import os
from sqlalchemy import or_, and_

# Add project root to sys.path so we can import from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, Registry

def run_migration():
    print("Iniciando migración de limpieza de datos en Nexus DB...")
    
    with SessionLocal() as session:
        # 1. Registros con título vacío o None
        registros_sin_titulo = session.query(Registry).filter(
            or_(Registry.title.is_(None), Registry.title == "")
        ).all()
        
        reparados_titulo = 0
        for reg in registros_sin_titulo:
            if reg.path_url:
                # Tratar de deducir el título desde la ruta/URL (e.g., el último segmento o nombre del archivo)
                nombre_base = os.path.basename(reg.path_url.rstrip('/\\'))
                nuevo_titulo = nombre_base if nombre_base else "Registro Recuperado (URL)"
            else:
                nuevo_titulo = f"Registro Sin Título {reg.id}"
                
            reg.title = nuevo_titulo
            reparados_titulo += 1
            
        if reparados_titulo > 0:
            print(f"- Se corrigieron {reparados_titulo} registros sin título válido.")

        # 2. Registros con descripción vacía (content_raw) o None
        registros_sin_desc = session.query(Registry).filter(
            or_(Registry.content_raw.is_(None), Registry.content_raw == "")
        ).all()
        
        reparados_desc = 0
        for reg in registros_sin_desc:
            titulo_usado = reg.title if reg.title else "Sin Título"
            ruta_usada = reg.path_url if reg.path_url else "Sin Ruta Asignada"
            
            reg.content_raw = f"(Auto-Descripción Migrada) Título: {titulo_usado} | Ruta: {ruta_usada}"
            reparados_desc += 1
            
        if reparados_desc > 0:
            print(f"- Se inyectó Auto-Descripción en {reparados_desc} registros vacíos.")

        # 3. Guardar cambios
        if reparados_titulo > 0 or reparados_desc > 0:
            session.commit()
            print("[OK] Migración exitosa. Cambios guardados permanentemente en la base de datos.")
        else:
            print("[INFO] La base de datos ya se encuentra estandarizada. No se requirieron cambios.")

if __name__ == "__main__":
    run_migration()
