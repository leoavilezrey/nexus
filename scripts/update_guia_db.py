
import os
import sys

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.database import nx_db, SessionLocal, Registry

def update_guide():
    path = os.path.abspath("docs/guia_tui_nexus.md")
    with open(path, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    with SessionLocal() as session:
        # ID de la guía que acabamos de crear
        reg_id = 23795
        reg = session.query(Registry).filter(Registry.id == reg_id).first()
        if reg:
            reg.content_raw = new_content
            session.commit()
            print(f"✅ Registro {reg_id} actualizado con el nuevo contenido de la guía.")
        else:
            print(f"❌ No se encontró el registro {reg_id}.")

if __name__ == "__main__":
    update_guide()
