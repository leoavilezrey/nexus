import sys
import os
import json
from sqlalchemy.orm import Session
from rich.console import Console

# Forzar salida en UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Añadir el path base para poder importar los módulos de core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, Registry, Tag

console = Console()

CACHES_DIR = r"c:\Users\DELL\Proyectos\personal_file_mcp"
CACHE_FILES = [
    "cache_youtube.json",
    "cache_drive.json",
    "cache_onedrive.json",
    "cache_dropbox.json"
]

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'}

def run_video_migration():
    console.print("\n[bold magenta]🎥 Migrando Videos desde archivos JSON...[/]")
    
    total_imported = 0
    total_skipped = 0
    
    with SessionLocal() as db:
        for filename in CACHE_FILES:
            filepath = os.path.join(CACHES_DIR, filename)
            if not os.path.exists(filepath):
                continue
                
            console.print(f"[cyan]Procesando {filename}...[/]")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                console.print(f"[red]Error leyendo {filename}: {e}[/]")
                continue
                
            for entry in data:
                nombre = entry.get('nombre', '')
                link = entry.get('link', '')
                comentario = entry.get('comentario', '')
                origen = entry.get('origen', 'Legacy JSON')
                id_legacy = entry.get('id', '')
                
                is_video = False
                res_type = "web" # Default
                
                if filename == "cache_youtube.json" or "youtube.com" in link or "youtu.be" in link:
                    is_video = True
                    res_type = "youtube"
                else:
                    # Verificar por extensión o comentario
                    ext = os.path.splitext(nombre)[1].lower()
                    if ext in VIDEO_EXTENSIONS or "video" in comentario.lower():
                        is_video = True
                        res_type = "file" # Cloud file
                
                if is_video:
                    if not link:
                        total_skipped += 1
                        continue
                        
                    # Verificar si ya existe
                    exists = db.query(Registry).filter(Registry.path_url == link).first()
                    
                    if exists:
                        # Si existe pero tiene el tipo mal (ej: migrado como 'file' anteriormente)
                        # lo corregimos y enriquecemos
                        if exists.type != res_type:
                            exists.type = res_type
                            if not exists.content_raw or "Auto-Descripción" in exists.content_raw:
                                exists.content_raw = comentario if comentario else exists.content_raw
                            
                            # Actualizar metadatos
                            original_meta = exists.meta_info if exists.meta_info else {}
                            original_meta.update({"id_legacy": id_legacy, "source": origen, "reclassified": True})
                            exists.meta_info = original_meta
                            
                            # Asegurar tags sin duplicados
                            for tag_val in ["video", origen.lower().replace(' ', '_')]:
                                tag_exists = db.query(Tag).filter_by(registry_id=exists.id, value=tag_val).first()
                                if not tag_exists:
                                    db.add(Tag(registry_id=exists.id, value=tag_val))
                            
                            db.commit()
                            total_imported += 1
                        else:
                            total_skipped += 1
                        continue
                        
                    # Crear Registro nuevo si no existe
                    new_reg = Registry(
                        type=res_type,
                        title=nombre,
                        path_url=link,
                        content_raw=comentario if comentario else f"Video importado de {origen}",
                        meta_info={"id_legacy": id_legacy, "source": origen, "original_cache": filename}
                    )
                    db.add(new_reg)
                    db.commit()
                    db.refresh(new_reg)
                    
                    # Añadir Tags iniciales
                    for tag_val in ["video", origen.lower().replace(' ', '_')]:
                        db.add(Tag(registry_id=new_reg.id, value=tag_val))
                    db.commit()
                    
                    total_imported += 1
                    
        console.print(f"\n[bold green]✓ Migración de Videos finalizada.[/]")
        console.print(f"-> Videos importados: {total_imported}")
        console.print(f"-> Registros omitidos/duplicados: {total_skipped}")

if __name__ == "__main__":
    run_video_migration()
