import sys
import os
import sqlite3
from sqlalchemy.orm import Session
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import SessionLocal, Registry, Tag

OLD_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'personal_file_mcp', 'files.db'))

def parse_tags(tags_str):
    if not tags_str:
        return []
    return list(set([t.strip() for t in tags_str.split(',') if t.strip()]))

def get_or_create_registry(session, type, title, path_url, content_raw, meta_info_dict, tags_list):
    # Validation
    if not title or title.strip() == "":
        title = path_url if path_url else "Registro Sin Título N"
        
    if not content_raw or content_raw.strip() == "":
        content_raw = f"(Auto-Descripción Migrada) Título: {title} | Ruta: {path_url}"
        
    # Anti-Duplicate by path_url if it's not empty
    if path_url:
        existing = session.query(Registry).filter(Registry.path_url == path_url).first()
        if existing:
            return None # Skip duplicate
            
    # Also attempt collision detection by identical type + title if path_url is empty
    if not path_url:
        existing = session.query(Registry).filter(Registry.type == type, Registry.title == title).first()
        if existing:
            return None
            
    reg = Registry(
        type=type,
        title=title,
        path_url=path_url,
        content_raw=content_raw,
        meta_info=meta_info_dict
    )
    session.add(reg)
    session.commit()
    session.refresh(reg)
    
    # Insert tags
    if tags_list:
        for tag_str in tags_list:
            session.add(Tag(registry_id=reg.id, value=tag_str))
        session.commit()
        
    return reg

def run_migration():
    if not os.path.exists(OLD_DB_PATH):
        print(f"Error: No se encontró la base de datos antigua en {OLD_DB_PATH}")
        return
        
    print(f"Abriendo conexión a la vieja DB en: {OLD_DB_PATH}")
    conn_old = sqlite3.connect(OLD_DB_PATH)
    conn_old.row_factory = sqlite3.Row
    cursor_old = conn_old.cursor()
    
    imported_count = 0
    skipped_count = 0
    
    with SessionLocal() as db_session:
        # =======================================================
        # 1. ARCHIVOS
        # =======================================================
        print("\nMigrando Archivos...")
        cursor_old.execute("SELECT id, path, filename, extension, size, resource_type FROM files")
        rows = cursor_old.fetchall()
        total_files = len(rows)
        print(f"Archivos encontrados para evaluar: {total_files}")
        
        for idx, row in enumerate(rows):
            # Imprimir progreso cada 50 items
            if idx % 50 == 0 and idx > 0:
                print(f"  -> {idx}/{total_files} procesados... (Importados: {imported_count}, Omitidos: {skipped_count})")
                
            # Descripción
            desc = ""
            desc_row = conn_old.execute("SELECT description FROM descriptions WHERE file_id = ?", (row['id'],)).fetchone()
            if desc_row and desc_row['description']:
                desc = desc_row['description']
                
            # Extraer Tags desde metadata si existe un key 'tags' o 'tag'
            tags_str = ""
            meta_rows = conn_old.execute("SELECT key, value FROM metadata WHERE file_id = ?", (row['id'],)).fetchall()
            for m in meta_rows:
                if m['key'].lower() in ('tags', 'tag'):
                    tags_str += m['value'] + ","
            tags = parse_tags(tags_str)
            
            meta_dict = {
                'extension': row['extension'],
                'size_bytes': row['size'],
                'resource_type': row['resource_type']
            }
            
            reg = get_or_create_registry(
                session=db_session,
                type="file",
                title=row['filename'],
                path_url=row['path'],
                content_raw=desc,
                meta_info_dict=meta_dict,
                tags_list=tags
            )
            if reg: imported_count += 1
            else: skipped_count += 1

        # =======================================================
        # 2. APLICACIONES
        # =======================================================
        print("Migrando Aplicaciones...")
        cursor_old.execute("SELECT nombre, plataforma, categoria, link_tienda, notas, tags FROM apps")
        for row in cursor_old.fetchall():
            tags = parse_tags(row['tags'])
            if row['categoria']: tags.append(f"cat:{row['categoria']}")
            
            meta_dict = {
                'platform_type': row['plataforma']
            }
            
            reg = get_or_create_registry(
                session=db_session,
                type="app",
                title=row['nombre'],
                path_url=row['link_tienda'],
                content_raw=row['notas'] if row['notas'] else f"Aplicación o Herramienta: {row['nombre']}",
                meta_info_dict=meta_dict,
                tags_list=tags
            )
            if reg: imported_count += 1
            else: skipped_count += 1

        # =======================================================
        # 3. CUENTAS WEB
        # =======================================================
        print("Migrando Cuentas Web...")
        cursor_old.execute("SELECT sitio, url, categoria, email_usuario, notas, tags FROM cuentas_web")
        for row in cursor_old.fetchall():
            tags = parse_tags(row['tags'])
            if row['categoria']: tags.append(f"cat:{row['categoria']}")
            
            meta_dict = {
                'email': row['email_usuario'],
                'requires_login': True
            }
            
            reg = get_or_create_registry(
                session=db_session,
                type="account",
                title=row['sitio'],
                path_url=row['url'],
                content_raw=row['notas'] if row['notas'] else f"Cuenta asociada en el sitio {row['sitio']} ({row['email_usuario']})",
                meta_info_dict=meta_dict,
                tags_list=tags
            )
            if reg: imported_count += 1
            else: skipped_count += 1

        # =======================================================
        # 4. PÁGINAS WEB
        # =======================================================
        print("Migrando Páginas Web sin Registro...")
        cursor_old.execute("SELECT nombre, url, categoria, descripcion, tags FROM paginas_sin_registro")
        for row in cursor_old.fetchall():
            tags = parse_tags(row['tags'])
            if row['categoria']: tags.append(f"cat:{row['categoria']}")
            
            reg = get_or_create_registry(
                session=db_session,
                type="web",
                title=row['nombre'],
                path_url=row['url'],
                content_raw=row['descripcion'] if row['descripcion'] else f"Página web: {row['nombre']}",
                meta_info_dict={},
                tags_list=tags
            )
            if reg: imported_count += 1
            else: skipped_count += 1

    conn_old.close()
    
    print("\n[OK] Migración finalizada.")
    print(f"-> Registros importados de la vieja BD: {imported_count}")
    print(f"-> Registros omitidos (ya existían / redundantes): {skipped_count}")

if __name__ == "__main__":
    run_migration()
