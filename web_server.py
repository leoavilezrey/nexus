
import os
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.database import SessionLocal, Registry, Card, Tag, nx_db
from core.search_engine import search_registry, parse_query_string

app = FastAPI(title="Nexus Hybrid API")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/api/records")
async def get_records(q: str = ""):
    db = SessionLocal()
    try:
        filtros = parse_query_string(q)
        # Convertir filtros de string a listas si es necesario (el search_engine lo hace por dentro)
        results = search_registry(
            db_session=db,
            inc_name_path=filtros.get('inc_name'),
            exc_name_path=filtros.get('exc_name'),
            inc_tags=filtros.get('inc_tags'),
            exc_tags=filtros.get('exc_tags'),
            limit=50
        )
        return results
    finally:
        db.close()

@app.get("/api/records/{record_id}")
async def get_record(record_id: int):
    db = SessionLocal()
    try:
        reg = db.query(Registry).filter(Registry.id == record_id).first()
        if not reg:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        # Obtener tags
        tags = db.query(Tag).filter(Tag.registry_id == record_id).all()
        # Obtener cards
        cards = db.query(Card).filter(Card.parent_id == record_id).all()
        
        return {
            "id": reg.id,
            "type": reg.type,
            "title": reg.title,
            "path_url": reg.path_url,
            "content_raw": reg.content_raw,
            "summary": reg.summary,
            "meta_info": reg.meta_info,
            "tags": [t.value for t in tags],
            "cards": [{"id": c.id, "question": c.question, "answer": c.answer} for c in cards]
        }
    finally:
        db.close()

@app.get("/api/stats")
async def get_stats():
    db = SessionLocal()
    try:
        total_records = db.query(Registry).count()
        total_cards = db.query(Card).count()
        # Contar videos con IA (resumen)
        processed_ai = db.query(Registry).filter(
            Registry.type == 'youtube',
            Registry.summary != None,
            Registry.summary != '',
            ~Registry.summary.like('Sin resumen%')
        ).count()
        
        # Simulación de progreso de estudio (en una versión real consultaría los registros de repaso)
        study_progress = {
            "total_reviewed": 124, 
            "mastered": 45,
            "pending": total_cards - 45
        }
        
        return {
            "total_records": total_records,
            "total_cards": total_cards,
            "processed_ai": processed_ai,
            "study_progress": study_progress,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    finally:
        db.close()

@app.get("/api/recall/cards")
async def get_recall_cards(limit: int = 10):
    db = SessionLocal()
    try:
        # Por ahora, simplemente obtener tarjetas aleatorias o próximas a revisión
        # Primero intentamos las que tienen next_review vencido o nulo
        cards = db.query(Card).order_by(Card.next_review.asc()).limit(limit).all()
        
        result = []
        for c in cards:
            # Obtener el registro padre para contexto
            parent = db.query(Registry).filter(Registry.id == c.parent_id).first()
            result.append({
                "id": c.id,
                "question": c.question,
                "answer": c.answer,
                "parent_title": parent.title if parent else "Desconocido",
                "difficulty": c.difficulty
            })
        return result
    finally:
        db.close()

@app.post("/api/recall/answer")
async def post_recall_answer(card_id: int, quality: int):
    """
    quality: 0 (olvidado), 1 (difícil), 2 (bien), 3 (fácil)
    """
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
        
        # Lógica simplificada de Spaced Repetition (después podemos meter FSRS o Anki logic)
        card.last_review = datetime.now()
        
        # Ajuste básico de estabilidad (días hasta el próximo repaso)
        days = 1
        if quality == 3: days = 4
        elif quality == 2: days = 2
        elif quality == 1: days = 1
        else: days = 0 # Repasar hoy mismo
        
        from datetime import timedelta
        card.next_review = datetime.now() + timedelta(days=days)
        
        db.commit()
        return {"status": "ok", "next_review": card.next_review}
    finally:
        db.close()

@app.get("/api/pipeline/status")
async def get_pipeline_status():
    from core.staging_db import StagingSessionLocal, staging_engine
    
    status = {
        "staging_connected": False,
        "queue_count": 0,
        "blocked_count": 0,
        "ready_count": 0
    }
    
    if staging_engine and StagingSessionLocal:
        db = StagingSessionLocal()
        try:
            status["staging_connected"] = True
            # Contar videos con error de IP
            status["blocked_count"] = db.query(Registry).filter(Registry.content_raw.like('%IpBlocked%')).count()
            # Contar videos listos para migrar (con transcripcion y sin error)
            status["ready_count"] = db.query(Registry).filter(
                Registry.content_raw != None,
                Registry.content_raw != '',
                ~Registry.content_raw.like('%IpBlocked%')
            ).count()
            # Total en cola
            status["queue_count"] = db.query(Registry).count()
        except Exception as e:
            print(f"Error accediendo a Staging DB: {e}")
        finally:
            db.close()
    
    return status

@app.post("/api/ingest")
async def post_ingest(data: dict):
    url = data.get("url")
    tags = data.get("tags", [])
    if not url:
        raise HTTPException(status_code=400, detail="URL requerida")
    
    from modules.web_scraper import ingest_web_resource
    
    try:
        # Procesar recurso
        reg = ingest_web_resource(url, tags)
        if reg:
            return {
                "status": "ok", 
                "id": reg.id, 
                "title": reg.title,
                "message": "Recurso indexado correctamente."
            }
        else:
            return {"status": "error", "message": "No se pudo procesar el recurso. Verifica la URL."}
    except Exception as e:
        return {"status": "error", "message": f"Error interno: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
