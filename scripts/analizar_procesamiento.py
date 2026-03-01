
import os
import sys
import json

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.database import SessionLocal, Registry, Card, Tag
from core.staging_db import staging_db
from sqlalchemy import func

def analyze():
    main_db = SessionLocal()
    
    # Analyze Main DB
    yt_all = main_db.query(Registry).filter(Registry.type == 'youtube').all()
    total_yt = len(yt_all)
    
    with_summary = sum(1 for r in yt_all if r.summary and len(r.summary) > 50)
    with_transcript = sum(1 for r in yt_all if r.content_raw and "Transcripción Disponible" not in r.content_raw and "Error al raspar" not in r.content_raw)
    
    yt_ids = [r.id for r in yt_all]
    card_counts = main_db.query(Card.parent_id, func.count(Card.id)).filter(Card.parent_id.in_(yt_ids)).group_by(Card.parent_id).all()
    with_cards = len(card_counts)
    total_cards = sum(count for pid, count in card_counts)

    # Analyze Staging
    staging_total = 0
    try:
        with staging_db.Session() as s:
            staging_total = s.query(Registry).count()
    except Exception as e:
        pass

    # Analyze Queue/History
    QUEUE_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_queue.txt"
    HISTORY_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_history.json"
    
    queue_count = 0
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            queue_count = len([l for l in f if l.strip()])
            
    history_count = 0
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            history_count = len(history)

    print("-" * 50)
    print("REPORTE DE PROCESAMIENTO NEXUS (YouTube Pipeline)")
    print("-" * 50)
    print(f"Total Videos Youtube en Nexus Core:           {total_yt}")
    print(f"   * Con Resumen Detallado (IA):                {with_summary}")
    print(f"   * Con Transcripcion Completa:                {with_transcript}")
    print(f"   * Con Fallo de Transcripcion (IpBlocked):    {total_yt - with_transcript}")
    print(f"   * Con Flashcards Generadas:                  {with_cards}")
    print(f"   * Total de Flashcards en el sistema:         {total_cards}")
    print("-" * 50)
    print(f"Estado del Canal (G: Drive Staging):")
    print(f"   * Total en Buffer de Staging:                {staging_total}")
    print(f"   * Videos en Historial (Procesados total):    {history_count}")
    print(f"   * Videos restantes en la Cola:               {queue_count - history_count if queue_count > history_count else 0}")
    print("-" * 50)
    print(f"Nota: Los videos con 'IpBlocked' conservan su URL y metadatos,")
    print(f"pero el resumen es generico por falta de texto base.")
    print("-" * 50)

    main_db.close()

if __name__ == "__main__":
    analyze()
