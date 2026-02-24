from datetime import datetime, timezone
from core.database import SessionLocal, Registry, Card, NexusLink, Tag
from sqlalchemy import func

def get_global_metrics():
    """Calcula y devuelve las métricas globales del sistema Nexus."""
    metrics = {
        "registry_counts": {
            "file": 0, "youtube": 0, "web": 0, "note": 0, "concept": 0, "app": 0, "account": 0, "total": 0
        },
        "network": {
            "total_links": 0,
            "unique_tags": 0
        },
        "srs": {
            "total_cards": 0,
            "due_today": 0,
            "due_future": 0,
            "avg_difficulty": 0.0,
            "avg_stability": 0.0,
            "retention_desc": "N/A"
        }
    }
    
    with SessionLocal() as session:
        # 1. Composición del Cerebro (Registros)
        registry_stats = session.query(Registry.type, func.count(Registry.id)).group_by(Registry.type).all()
        for r_type, count in registry_stats:
            metrics["registry_counts"][r_type] = count
            metrics["registry_counts"]["total"] += count
            
        # 2. Red Neuronal (Vínculos y Tags)
        metrics["network"]["total_links"] = session.query(func.count(NexusLink.id)).scalar() or 0
        metrics["network"]["unique_tags"] = session.query(func.count(func.distinct(Tag.value))).scalar() or 0
        
        # 3. Madurez Cognitiva (SRS)
        now = datetime.now(timezone.utc)
        
        total_cards = session.query(func.count(Card.id)).scalar() or 0
        metrics["srs"]["total_cards"] = total_cards
        
        if total_cards > 0:
            due_today = session.query(func.count(Card.id)).filter(
                (Card.next_review == None) | (Card.next_review <= now)
            ).scalar() or 0
            
            metrics["srs"]["due_today"] = due_today
            metrics["srs"]["due_future"] = total_cards - due_today
            
            avg_diff = session.query(func.avg(Card.difficulty)).filter(Card.difficulty > 0).scalar() or 0.0
            avg_stab = session.query(func.avg(Card.stability)).filter(Card.stability > 0).scalar() or 0.0
            
            metrics["srs"]["avg_difficulty"] = float(avg_diff)
            metrics["srs"]["avg_stability"] = float(avg_stab)
            
            # Interpretar dificultad (1-10 por SM-2/FSRS adaptado)
            if avg_diff < 3.0:
                metrics["srs"]["retention_desc"] = "Alta (Fácil)"
            elif 3.0 <= avg_diff <= 6.0:
                metrics["srs"]["retention_desc"] = "Media (Estable)"
            else:
                metrics["srs"]["retention_desc"] = "Baja (Difícil)"

    return metrics
