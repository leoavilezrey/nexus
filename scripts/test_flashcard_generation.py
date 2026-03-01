
import os
import sys

# Añadir el path del proyecto para importar módulos de core
sys.path.append(os.getcwd())

from core.database import nx_db, SessionLocal
from agents.study_agent import generate_deck_from_registry

def test_gen():
    # Intentar con el ID que falló antes
    test_id = 11603
    print(f"Probando generación para ID {test_id}...")
    
    reg_obj = nx_db.get_registry(test_id)
    if not reg_obj:
        print("Registro no encontrado. Buscando el primero disponible...")
        with SessionLocal() as db:
            from core.database import Registry
            reg_obj = db.query(Registry).first()
            if reg_obj:
                test_id = reg_obj.id
    
    if reg_obj:
        print(f"Indexando: {reg_obj.title}")
        # Usamos mockup_only=False para probar la conexión real a Gemini
        # Pero como no puedo responder al Prompt interactivo en este entorno, 
        # me aseguro de que el agente NO pida confirmación si ya se la pasamos (aunque sea por parámetro)
        # Nota: Mi cambio anterior en dashboard.py manejaba la confirmación.
        # En el agente, si mockup_only es False, intentará llamar a Gemini.
        
        try:
            cards = generate_deck_from_registry(reg_obj, mockup_only=False)
            print(f"Éxito. Se generaron {len(cards)} tarjetas.")
            for i, c in enumerate(cards):
                print(f"[{i+1}] Q: {c.question[:50]}... A: {c.answer[:50]}...")
        except Exception as e:
            print(f"Error durante la prueba: {e}")
    else:
        print("No hay registros en la base de datos para probar.")

if __name__ == "__main__":
    test_gen()
