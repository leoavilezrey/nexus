
import os
import csv
import sqlite3
import shutil
from datetime import datetime
from core.database import nx_db, SessionLocal, Registry, Tag

def export_to_google_drive():
    """
    Exporta la base de datos actual y genera un reporte CSV en Google Drive (Unidad G:).
    """
    # 1. Definir rutas en G:
    g_drive_base = r"G:\Mi unidad\Nexus_Data"
    if not os.path.exists(r"G:\Mi unidad"):
        return False, "No se detecto la unidad Google Drive (G:). Asegura que el cliente de escritorio este abierto."

    if not os.path.exists(g_drive_base):
        os.makedirs(g_drive_base)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_export_path = os.path.join(g_drive_base, f"nexus_backup_{timestamp}.db")
    csv_export_path = os.path.join(g_drive_base, f"nexus_registros_{timestamp}.csv")

    try:
        # --- A. Exportar Base de Datos (Copia Fisica) ---
        # Cerramos conexiones/flushing no es necesario con copy2 si no es vital, 
        # pero es mejor copiar el archivo nexus.db de la raiz.
        source_db = r"c:\Users\DELL\Proyectos\nexus\nexus.db"
        if os.path.exists(source_db):
            shutil.copy2(source_db, db_export_path)
            
        # --- B. Exportar a CSV (Para lectura facil/descarga) ---
        with SessionLocal() as session:
            registries = session.query(Registry).all()
            
            with open(csv_export_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
                fieldnames = ['id', 'tipo', 'titulo', 'url_ruta', 'resumen', 'contenido_raw', 'tags', 'fecha_creacion']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for r in registries:
                    # Obtener tags
                    tags = ", ".join([t.value for t in r.tags])
                    
                    writer.writerow({
                        'id': r.id,
                        'tipo': r.type,
                        'titulo': r.title,
                        'url_ruta': r.path_url,
                        'resumen': r.summary if r.summary else "",
                        'contenido_raw': r.content_raw if r.content_raw else "",
                        'tags': tags,
                        'fecha_creacion': r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
                    })

        return True, g_drive_base
    except Exception as e:
        return False, str(e)
