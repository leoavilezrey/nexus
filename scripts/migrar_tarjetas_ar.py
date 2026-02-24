import sys
import os
import sqlite3
from sqlalchemy.orm import Session
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import SessionLocal, Registry, Card, Tag

OLD_AR_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ar-console', 'data', 'ar_console.db'))

def parse_tags(tags_str):
    if not tags_str:
        return []
    return list(set([t.strip() for t in tags_str.split(',') if t.strip()]))

def get_or_create_concept(session, concept_title):
    if not concept_title or concept_title.strip() == "":
        concept_title = "Conceptos Huérfanos (AR-Console)"
        
    # Check if a concept with this title already exists
    existing = session.query(Registry).filter(Registry.title == concept_title).first()
    if existing:
        return existing
        
    # Create new concept registry
    reg = Registry(
        type="concept",
        title=concept_title,
        content_raw=f"Colección de Tarjetas (Flashcards) migradas sobre el tema: {concept_title}",
        meta_info={"source": "AR-Console Legacy"}
    )
    session.add(reg)
    session.commit()
    session.refresh(reg)
    return reg

def convert_datetime(iso_str):
    if not iso_str:
        return None
    try:
        # AR-Console dates were usually isoformat strings like '2024-05-12T15:30:00'
        # Fallback to current time if parsing fails
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except Exception:
        return None

def run_migration():
    if not os.path.exists(OLD_AR_DB_PATH):
        print(f"Error: No se encontró la base de datos de tarjetas antigua en {OLD_AR_DB_PATH}")
        return
        
    print(f"Abriendo conexión a la vieja AR-Console DB: {OLD_AR_DB_PATH}")
    conn_old = sqlite3.connect(OLD_AR_DB_PATH)
    conn_old.row_factory = sqlite3.Row
    cursor_old = conn_old.cursor()
    
    imported_cards_count = 0
    skipped_cards_count = 0
    concepts_mapped = 0
    
    with SessionLocal() as db_session:
        print("\nAnalizando tarjetas disponibles...")
        cursor_old.execute("SELECT * FROM cards")
        rows = cursor_old.fetchall()
        
        for row in rows:
            concept_title = row['source_concept']
            if not concept_title:
                concept_title = "Sin Concepto (Legado)"
                
            # Validar si esta tarjeta exacta ya existe para el concepto (Anti-duplicate heurístico)
            reg = get_or_create_concept(db_session, concept_title)
            
            existing_card = db_session.query(Card).filter(
                Card.parent_id == reg.id,
                Card.question == row['question']
            ).first()
            
            if existing_card:
                skipped_cards_count += 1
                continue
                
            # Build the card
            new_card = Card(
                parent_id=reg.id,
                question=row['question'],
                answer=row['answer'],
                type=row['card_type'] if row['card_type'] else 'Conceptual',
                difficulty=row['difficulty'] if row['difficulty'] is not None else 5.0,
                stability=row['stability'] if row['stability'] is not None else 1.0,
                last_review=convert_datetime(row['last_review']),
                next_review=convert_datetime(row['next_review'])
            )
            
            db_session.add(new_card)
            imported_cards_count += 1
            db_session.commit()
            
            # Add Tags if they exist
            tags = parse_tags(row['tags'])
            for tag_str in tags:
                # Comprobamos directamente en base de datos para no cruzar el Identity Map de SQLAlchemy
                existing_tag = db_session.query(Tag).filter_by(registry_id=reg.id, value=tag_str).first()
                if not existing_tag:
                    db_session.add(Tag(registry_id=reg.id, value=tag_str))
                    try:
                        db_session.commit()
                    except Exception:
                        db_session.rollback()

    conn_old.close()
    print("\n[OK] Migración de Tarjetas (SRS Flashcards) Finalizada con Éxito.")
    print(f"-> Tarjetas importadas funcionalmente a Nexus DB: {imported_cards_count}")
    print(f"-> Tarjetas omitidas (ya existían/duplicadas): {skipped_cards_count}")

if __name__ == "__main__":
    run_migration()
