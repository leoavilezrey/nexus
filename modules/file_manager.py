import os
from pathlib import Path
from typing import List, Optional

from core.database import nx_db, RegistryCreate, TagCreate
from core.models import ResourceRecord

# Definimos extensiones que consideramos texto plano directamente legible
TEXT_EXTENSIONS = {'.txt', '.md', '.csv', '.json', '.xml', '.py', '.js', '.html', '.css', '.ini', '.yaml', '.yml'}

def ingest_local_file(filepath: str, tags: List[str]) -> Optional[ResourceRecord]:
    """
    Ingesta un archivo local en la base de datos maestra de Nexus.
    Extrae metadatos y, si es texto plano, una vista previa del contenido.
    No almacena binarios bajo ninguna circunstancia.
    """
    file_path_obj = Path(filepath)
    
    # 1. Validación de existencia
    if not file_path_obj.exists() or not file_path_obj.is_file():
        print(f"[bold white on red]Error:[/] El archivo no existe o no es un archivo válido: {filepath}")
        return None

    # 2. Extracción de Metadatos Base
    title = file_path_obj.name
    absolute_posix_path = file_path_obj.absolute().as_posix() # Ruta multiplataforma
    ext = file_path_obj.suffix.lower()
    
    try:
        size_bytes = file_path_obj.stat().st_size
    except Exception as e:
        print(f"[yellow]Advertencia:[/] No se pudo obtener el tamaño de {filepath}. Error: {e}")
        size_bytes = 0

    # 3. Manejo de Texto Plano (Lectura Rápida)
    content_raw = None
    if ext in TEXT_EXTENSIONS:
        try:
            # Leemos los primeros 5000 caracteres para evitar saturar la base de datos
            # con archivos de texto masivos (ej. logs gigantes)
            with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                content_raw = f.read(5000)
                if len(content_raw) == 5000:
                    content_raw += "\n...[Contenido truncado]"
        except Exception as e:
            print(f"[yellow]Advertencia:[/] No se pudo extraer texto parcial de {filepath}. Error: {e}")

    # Estructura del diccionario JSON para el campo 'meta_info' (metadatos base)
    meta_info = {
        "extension": ext.lstrip('.'),
        "size_bytes": size_bytes,
        "source": "local_file_manager"
    }

    # 4. Inserción estricta en la Base de Datos a través del ORM (Pydantic Mapped)
    file_record_data = RegistryCreate(
        type="file",
        title=title,
        path_url=absolute_posix_path,
        content_raw=content_raw,
        meta_info=meta_info
    )

    try:
        # Inyectar registro maestro en el Core DB
        reg = nx_db.create_registry(file_record_data)
        
        # Inyectar las etiquetas vinculadas (limpiando espacios)
        for tag_val in tags:
            tag_clean = tag_val.strip().lower()
            if tag_clean:
                nx_db.add_tag(reg.id, TagCreate(value=tag_clean))
        
        # Empaquetamos al modelo maestro Pydantic para devolver el ResourceRecord
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
        
        print(f"✅ Archivo '{title}' indexado exitosamente (ID: {reg.id}).")
        return rr
        
    except Exception as e:
        print(f"[bold white on red]Error fatal al intentar guardar en la base de datos:[/] {e}")
        return None

if __name__ == "__main__":
    # Test rápido de compilación
    pass
