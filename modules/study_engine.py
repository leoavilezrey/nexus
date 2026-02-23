import datetime
from sqlalchemy import or_
from typing import List
from core.database import SessionLocal, Card, nx_db
from core.models import StudyCard, ResourceRecord

def get_due_cards() -> List[StudyCard]:
    """Obtiene las tarjetas que están listas para ser repasadas hoy o nunca antes repasadas."""
    with SessionLocal() as session:
        now = datetime.datetime.utcnow()
        # Tarjetas sin revisar o listas para repasar
        cards = session.query(Card).filter(
            or_(
                Card.next_review == None,
                Card.next_review <= now
            )
        ).all()
        
        # Mapeamos a Pydantic
        result = []
        for c in cards:
            result.append(StudyCard(
                id=c.id,
                parent_id=c.parent_id,
                question=c.question,
                answer=c.answer,
                card_type=c.type if c.type else "Factual",
                srs_data={
                    "difficulty": c.difficulty,
                    "stability": c.stability,
                    "last_review": c.last_review,
                    "next_review": c.next_review
                }
            ))
        return result

def update_card_srs(card_id: int, rating: int):
    """
    rating: 1 (Dificil), 2 (Bien), 3 (Facil)
    Actualiza los valores básicos SRS de la tarjeta en la BD adaptando su próximo repaso.
    """
    with SessionLocal() as session:
        card = session.query(Card).filter(Card.id == card_id).first()
        if not card:
            return
        
        now = datetime.datetime.utcnow()
        card.last_review = now
        
        # Algoritmo Ficticio SRS Inicial (Simplificado)
        if rating == 1:
            days = 1
        elif rating == 2:
            days = 3
        else:
            days = 7
            
        card.next_review = now + datetime.timedelta(days=days)
        session.commit()

def get_resource_record(reg_id: int) -> ResourceRecord:
    """Extrae un registro del Core DB por ID y lo mapea al modelo maestro de Pydantic."""
    reg = nx_db.get_registry(reg_id)
    if not reg:
        return None
    return ResourceRecord(
        id=reg.id,
        type=reg.type,
        title=reg.title or "",
        path_url=reg.path_url or "",
        content_raw=reg.content_raw,
        metadata_dict=reg.meta_info if reg.meta_info else {},
        created_at=reg.created_at,
        modified_at=reg.modified_at
    )
