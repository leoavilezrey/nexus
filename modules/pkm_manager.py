import os
import tempfile
import subprocess
from typing import List, Optional

from core.database import nx_db, RegistryCreate, TagCreate, SessionLocal
from core.models import ResourceRecord

def create_note(title: str, tags: List[str]) -> Optional[ResourceRecord]:
    """
    Inicia el flujo de creación de una Nota (PKM).
    Abre el bloc de notas (notepad), espera a que el usuario termine la edición,
    cierra el editor y guarda el contenido en la base de datos maestra.
    """
    # 1. Crear un archivo temporal con extensión .md
    fd, temp_path = tempfile.mkstemp(suffix=".md", prefix="nexus_note_", text=True)
    
    # Escribir un encabezado opcional inicial
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\nEscribe tu nota aquí...\n")

    try:
        # 2. Abrir el editor de texto nativo de forma bloqueante
        print(f"\n[bold cyan]Abriendo editor para la nota:[/bold cyan] '{title}'...")
        print("[yellow]La terminal está en espera. Cierra el bloc de notas para guardar...[/yellow]\n")
        
        # subprocess.run es bloqueante por defecto
        subprocess.run(['notepad', temp_path], check=True)
        
    except Exception as e:
        print(f"[bold white on red]Error al intentar abrir el editor:[/] {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None
        
    # 3. Leer el contenido modificado tras cerrar el editor
    with open(temp_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        
    # 4. Limpieza: Borrar el archivo temporal (no almacenamos binarios)
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    # Si la nota quedó vacía o con el texto por defecto, la abortamos para no ensuciar la BD
    if not content or content == f"# {title}\n\nEscribe tu nota aquí...":
        print("[bold white on red]La nota está vacía o sin cambios. Abortando guardado.[/]")
        return None
        
    # 5. Mapear los datos al esquema de Pydantic y guardarlos a la BD
    note_data = RegistryCreate(
        type="note",
        title=title,
        # Path URI lógico en lugar de físico, ya que su info resida en la DB directamente.
        path_url=f"nexus://note/{title.replace(' ', '_').lower()}",
        content_raw=content,
        meta_info={"extension": "md", "source": "pkm_manager"}
    )
    
    # Inyectar a la base de datos usando nuestro CRUD
    reg = nx_db.create_registry(note_data)
    
    # Inyectar las etiquetas asociadas (Asegurando limpiar mayúsculas y espacios)
    for tag_val in tags:
        tag_clean = tag_val.strip().lower()
        if tag_clean:
            nx_db.add_tag(reg.id, TagCreate(value=tag_clean))
            
    # Empaquetamos al modelo maestro Pydantic (basado en el Blueprint)
    rr = ResourceRecord(
        id=reg.id,
        type=reg.type,
        title=reg.title or "",
        path_url=reg.path_url or "",
        content_raw=reg.content_raw,
        metadata_dict=reg.meta_info if reg.meta_info else {},
        created_at=reg.created_at,
        modified_at=reg.modified_at
    )
    
    # console.print no está importado aquí pero usaremos un print normal
    # o podríamos usar la librería rich para mayor visibilidad (la incluimos más adelante)
    print(f"✅ Nota '{title}' guardada exitosamente en la DB con el ID {reg.id} y {len(tags)} etiqueta(s).")
    return rr

if __name__ == "__main__":
    # Prueba de compilación directa y bloqueo
    # Descomentar para probar sin llamar desde el dashboard
    # create_note("Mi Primera Nota Nexus", ["pkm", "test", "zettelkasten"])
    pass
