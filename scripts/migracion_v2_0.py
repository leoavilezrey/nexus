import sys
import os

# Forzar salida en UTF-8 para evitar errores de renderizado de Emojis en la terminal de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

import sqlite3
from sqlalchemy.orm import Session
from datetime import datetime
from rich.console import Console

# Añadir el path base para poder importar los módulos de core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, Registry, Tag, Card, NexusLink

console = Console()

# Rutas de bases de datos antiguas
OLD_FILES_DB = r"c:\Users\DELL\Proyectos\personal_file_mcp\files.db"
OLD_AR_DB = r"c:\Users\DELL\Proyectos\ar-console\data\ar_console.db"

def parse_iso(iso_str):
    if not iso_str: return None
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except:
        return None

def run_migration_v2():
    console.print("\n[bold magenta]🚀 Iniciando Migración Maestra v2.0 (Reconstructor de Red Neuronal)[/]")
    
    if not os.path.exists(OLD_FILES_DB):
        console.print(f"[bold red]Error:[/] No se encontró {OLD_FILES_DB}")
        return
    if not os.path.exists(OLD_AR_DB):
        console.print(f"[bold red]Error:[/] No se encontró {OLD_AR_DB}")
        return

    conn_files = sqlite3.connect(OLD_FILES_DB)
    conn_files.row_factory = sqlite3.Row
    
    conn_ar = sqlite3.connect(OLD_AR_DB)
    conn_ar.row_factory = sqlite3.Row
    
    with SessionLocal() as db:
        # ========================================================
        # 1. Mapeo de IDs (Construcción del Puente)
        # ========================================================
        console.print("\n[bold cyan]1. Mapeando Registros entre Sistemas...[/]")
        
        # Diccionario para mapear (tabla_antigua, id_antiguo) -> id_nexus
        map_bridge = {}
        
        # Mapear Archivos
        rows = conn_files.execute("SELECT id, path FROM files").fetchall()
        for r in rows:
            nexus_reg = db.query(Registry).filter(Registry.path_url == r['path']).first()
            if nexus_reg: map_bridge[('files', r['id'])] = nexus_reg.id
            
        # Mapear Apps
        rows = conn_files.execute("SELECT rowid as id, nombre FROM apps").fetchall() # rowid si no hay id
        for r in rows:
            nexus_reg = db.query(Registry).filter(Registry.title == r['nombre'], Registry.type == 'app').first()
            if nexus_reg: map_bridge[('apps', r['id'])] = nexus_reg.id
            
        # Mapear Cuentas Web
        rows = conn_files.execute("SELECT rowid as id, url FROM cuentas_web").fetchall()
        for r in rows:
            nexus_reg = db.query(Registry).filter(Registry.path_url == r['url'], Registry.type == 'account').first()
            if nexus_reg: map_bridge[('cuentas_web', r['id'])] = nexus_reg.id

        # Mapear Páginas Web
        rows = conn_files.execute("SELECT rowid as id, url FROM paginas_sin_registro").fetchall()
        for r in rows:
            nexus_reg = db.query(Registry).filter(Registry.path_url == r['url'], Registry.type == 'web').first()
            if nexus_reg: map_bridge[('paginas_sin_registro', r['id'])] = nexus_reg.id

        console.print(f"[dim]Mapeo completado: {len(map_bridge)} elementos vinculados.[/dim]")

        # ========================================================
        # 2. Migración de Relaciones (Red Neuronal)
        # ========================================================
        console.print("\n[bold cyan]2. Reconstruyendo Vínculos (NexusLinks)...[/]")
        links_rows = conn_files.execute("SELECT * FROM notas_relacion").fetchall()
        links_added = 0
        
        for lr in links_rows:
            s_key = (lr['origen_tabla'], lr['origen_id'])
            t_key = (lr['destino_tabla'], lr['destino_id'])
            
            if s_key in map_bridge and t_key in map_bridge:
                s_id = map_bridge[s_key]
                t_id = map_bridge[t_key]
                
                # Evitar duplicados en NexusLinks
                exists = db.query(NexusLink).filter_by(source_id=s_id, target_id=t_id).first()
                if not exists:
                    new_link = NexusLink(
                        source_id=s_id,
                        target_id=t_id,
                        relation_type="migrated",
                        description=lr['descripcion']
                    )
                    db.add(new_link)
                    links_added += 1
        
        db.commit()
        console.print(f"[green]✓ {links_added} relaciones reconstruidas en Nexus.[/]")

        # ========================================================
        # 3. Migración de Notas (Excluyendo Virtuales)
        # ========================================================
        console.print("\n[bold cyan]3. Migrando Notas Nativas (Sin Notas Virtuales)...[/]")
        notes_rows = conn_ar.execute("SELECT * FROM notes").fetchall()
        notes_migrated = 0
        
        for nr in notes_rows:
            title = nr['title'] or "Nota Sin Título"
            # Excluir si el título contiene "virtual"
            if "virtual" in title.lower():
                continue
                
            # Verificar si ya existe por título y tipo note
            exists = db.query(Registry).filter_by(title=title, type='note').first()
            if not exists:
                new_note = Registry(
                    type='note',
                    title=title,
                    content_raw=nr['content'],
                    path_url=nr['filepath'],
                    meta_info={'source': 'legacy_ar_console'}
                )
                db.add(new_note)
                db.commit()
                db.refresh(new_note)
                
                # Tags de la nota
                if nr['tags']:
                    for t in nr['tags'].split(','):
                        t = t.strip()
                        if t:
                            db.add(Tag(registry_id=new_note.id, value=t.lower()))
                    db.commit()
                notes_migrated += 1
                
        console.print(f"[green]✓ {notes_migrated} notas migradas a Nexus.[/]")

        # ========================================================
        # 4. Sincronización de SRS (Carga de Repasos Antiguos)
        # ========================================================
        console.print("\n[bold cyan]4. Sincronizando Progreso de Aprendizaje (SRS)...[/]")
        # Aquí actualizamos las cards que ya existan en Nexus con los datos de AR_Console
        # Necesitamos mapear Concept -> parent_id
        cards_rows = conn_ar.execute("SELECT * FROM cards").fetchall()
        cards_updated = 0
        
        for cr in cards_rows:
            # Buscar la card en Nexus por la pregunta
            # Primero buscamos el parent_id por el source_concept del legacy
            nexus_card = db.query(Card).filter(Card.question == cr['question']).first()
            
            if nexus_card:
                # Si existe, actualizamos sus métricas
                nexus_card.difficulty = cr['difficulty'] if cr['difficulty'] is not None else 0.5
                nexus_card.stability = cr['stability'] if cr['stability'] is not None else 1.0
                nexus_card.last_review = parse_iso(cr['last_review'])
                nexus_card.next_review = parse_iso(cr['next_review'])
                cards_updated += 1
        
        db.commit()
        console.print(f"[green]✓ {cards_updated} tarjetas actualizadas con tu historial de repaso.[/]")

    conn_files.close()
    conn_ar.close()
    console.print("\n[bold green]⭐⭐ MIGRACIÓN MAESTRA V2.0 COMPLETADA ⭐⭐[/]")
    console.print("[dim]Tu red de conocimiento ahora vive plenamente en Nexus.[/dim]\n")

if __name__ == "__main__":
    run_migration_v2()
