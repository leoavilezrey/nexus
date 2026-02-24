import sys; import os
sys.path.append('C:/Users/DELL/Proyectos/nexus')
from core.database import SessionLocal, Registry, nx_db

def delete_anki():
    with SessionLocal() as s:
        regs = s.query(Registry).filter(Registry.title == 'anki').all()
        for r in regs:
            nx_db.delete_registry(r.id)
            print(f"Deleted {r.title} (ID: {r.id})")

if __name__ == "__main__":
    delete_anki()
