import sys
import os

# Forzar salida en UTF-8 para evitar errores de renderizado de Emojis en la terminal de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Añadir path para importar core y modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.file_manager import ingest_local_file
from agents.study_agent import generate_deck_from_registry
from core.database import nx_db, Card

def index_and_learn_guide():
    guide_path = r"c:\Users\DELL\Proyectos\nexus\docs\guia_maestra_nexus.md"
    
    # 1. Ingestar el archivo
    print(f"Indexando manual maestro: {guide_path}")
    resource = ingest_local_file(guide_path, ["guía", "estrategia", "nexus", "master"])
    
    if not resource:
        # Si falló (ej: duplicado), intentamos recuperarlo manualmente
        print("El archivo parece ya estar indexado o hubo un error. Buscando registro existente...")
        with nx_db.Session() as s:
            from core.database import Registry as RegistryDB
            # Normalizamos la ruta para la búsqueda (como lo hace Path.absolute().as_posix())
            normalized_path = os.path.abspath(guide_path).replace("\\", "/")
            resource = s.query(RegistryDB).filter(RegistryDB.path_url == normalized_path).first()
    
    if resource:
        print(f"✅ Documento indexado con ID: {resource.id}")
        
        # 2. Generar Flashcards con IA
        print("🤖 Generando Flashcards de dominio para el manual maestro...")
        try:
            # Obtener el objeto Registry real desde la DB
            with nx_db.Session() as s:
                from core.database import Registry as RegistryDB
                reg_obj = s.query(RegistryDB).filter(RegistryDB.id == resource.id).first()
                
                if reg_obj:
                    # Usar el nombre de función correcto
                    cards = generate_deck_from_registry(reg_obj)
                    
                    if cards:
                        cards_added = 0
                        for c_data in cards:
                            # c_data ya es un objeto StudyCard (Pydantic), pero lo guardamos en la tabla SQL Card
                            new_card = Card(
                                parent_id=resource.id,
                                question=c_data.question,
                                answer=c_data.answer,
                                type=c_data.card_type or "Conceptual"
                            )
                            s.add(new_card)
                            cards_added += 1
                        s.commit()
                        print(f"✨ Se han añadido {cards_added} flashcards para que no olvides las reglas de Nexus.")
                    else:
                        print("⚠️ No se generaron tarjetas (posible error de IA o contenido insuficiente).")
        except Exception as e:
            print(f"❌ Error generando tarjetas: {e}")
    else:
        print("❌ Error al indexar el documento.")

if __name__ == "__main__":
    index_and_learn_guide()
