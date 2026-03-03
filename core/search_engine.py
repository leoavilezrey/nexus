from typing import Optional, List
from sqlalchemy import or_, and_, not_, func
from sqlalchemy.orm import Session

from core.database import Registry, Tag
from core.models import ResourceRecord

def search_registry(
    db_session: Session,
    type_filter: Optional[str] = None,
    inc_name_path: Optional[str] = None,
    exc_name_path: Optional[str] = None,
    inc_tags: Optional[str] = None,
    exc_tags: Optional[str] = None,
    inc_extensions: Optional[List[str]] = None,
    exc_extensions: Optional[List[str]] = None,
    has_info: Optional[str] = None,
    record_ids_str: Optional[str] = None,
    is_flashcard_source: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[ResourceRecord]:
    """
    Motor maestro de búsqueda para Nexus.
    Retorna siempre una lista de instancias Pydantic ResourceRecord.
    Soporta Inclusión, Exclusión, tags especiales (__web__) y filtros de contenido.
    """
    query = db_session.query(Registry)

    # 1. Filtro estricto por Tipo (file, youtube, note, etc.)
    if type_filter:
        query = query.filter(Registry.type == type_filter)

    # 2. Búsqueda en Nombre y Ruta (Inclusiones y Exclusiones)
    # Soporte para múltiples términos separados por coma.
    if inc_name_path:
        for term in [t.strip() for t in inc_name_path.split(',') if t.strip()]:
            query = query.filter(
                or_(
                    Registry.title.ilike(f"%{term}%"),
                    Registry.path_url.ilike(f"%{term}%")
                )
            )

    if exc_name_path:
        for term in [t.strip() for t in exc_name_path.split(',') if t.strip()]:
            query = query.filter(
                not_(
                    or_(
                        Registry.title.ilike(f"%{term}%"),
                        Registry.path_url.ilike(f"%{term}%")
                    )
                )
            )

    # 3. Etiquetas (Inclusiones y Exclusiones)
    # Se usan Subqueries IN() y NOT IN() hacia la tabla Tag para máxima optimización y precisión
    if inc_tags:
        for term in [t.strip() for t in inc_tags.split(',') if t.strip()]:
            subquery = db_session.query(Tag.registry_id).filter(Tag.value.ilike(f"%{term}%"))
            query = query.filter(Registry.id.in_(subquery))

    if exc_tags:
        for term in [t.strip() for t in exc_tags.split(',') if t.strip()]:
            subquery = db_session.query(Tag.registry_id).filter(Tag.value.ilike(f"%{term}%"))
            query = query.filter(not_(Registry.id.in_(subquery)))

    # 4. Extensiones + Soporte para el tag especial '__web__'
    if inc_extensions:
        inc_exts_clean = [e.strip().lower() for e in inc_extensions if e.strip()]
        if inc_exts_clean:
            conditions = []
            has_web = False
            # Mapeo de conveniencia: Si el usuario escribe 'web' o 'youtube' en el campo de extensión,
            # lo interpretamos como el tag especial de búsqueda web.
            web_aliases = {'__web__', 'web', 'youtube', 'yt'}
            if any(alias in inc_exts_clean for alias in web_aliases):
                has_web = True
                for alias in web_aliases:
                    if alias in inc_exts_clean: inc_exts_clean.remove(alias)

            for ext in inc_exts_clean:
                ext_no_dot = ext.lstrip('.')
                ext_dot = f".{ext_no_dot}"
                # Buscar en la URL/Path físico, o usando el casteo JSON de SQLAlchemy de 'meta_info'
                conditions.append(Registry.path_url.ilike(f"%{ext_dot}"))
                conditions.append(func.json_extract(Registry.meta_info, '$.extension').ilike(ext_no_dot))

            if has_web:
                # El tag __web__ busca explícitamente recursos que viven en la red o son de plataforma web
                conditions.append(Registry.type.in_(['youtube', 'web', 'account']))
                conditions.append(Registry.path_url.ilike("http%"))

            if conditions:
                query = query.filter(or_(*conditions))

    if exc_extensions:
        exc_exts_clean = [e.strip().lower() for e in exc_extensions if e.strip()]
        if exc_exts_clean:
            conditions = []
            has_web = False
            web_aliases = {'__web__', 'web', 'youtube', 'yt'}
            if any(alias in exc_exts_clean for alias in web_aliases):
                has_web = True
                for alias in web_aliases:
                    if alias in exc_exts_clean: exc_exts_clean.remove(alias)

            for ext in exc_exts_clean:
                ext_no_dot = ext.lstrip('.')
                ext_dot = f".{ext_no_dot}"
                conditions.append(Registry.path_url.ilike(f"%{ext_dot}"))
                conditions.append(func.json_extract(Registry.meta_info, '$.extension').ilike(ext_no_dot))

            if has_web:
                conditions.append(Registry.type.in_(['youtube', 'web', 'account']))
                conditions.append(Registry.path_url.ilike("http%"))

            if conditions:
                query = query.filter(not_(or_(*conditions)))

    # 5. Tiene Información (has_info) -> 's' o 'n'
    if has_info:
        has_info_val = has_info.lower().strip()
        if has_info_val == 's':
            # 's': Obliga a que tenga 'content_raw' y no esté vacío, O tenga alguna etiqueta asociada en Tag.
            # Según tu Blueprint es "Registros que sí tengan content_raw o metadata de tags"
            query = query.filter(
                or_(
                    and_(Registry.content_raw.isnot(None), Registry.content_raw != ""),
                    Registry.id.in_(db_session.query(Tag.registry_id))
                )
            )
        elif has_info_val == 'n':
            # 'n': Son únicamente archivos de indexado rápido "crudos", sin raw description ni tags.
            query = query.filter(
                and_(
                    or_(Registry.content_raw.is_(None), Registry.content_raw == ""),
                    not_(Registry.id.in_(db_session.query(Tag.registry_id)))
                )
            )

    # 6. Filtrado por IDs específicos (Misma lógica csv / rangos que dashboard)
    if record_ids_str:
        ids_to_search = []
        for part in record_ids_str.split(','):
            part = part.strip()
            if '-' in part and not part.startswith('-'):
                try:
                    s_id, e_id = part.split('-')
                    ids_to_search.extend(range(min(int(s_id), int(e_id)), max(int(s_id), int(e_id)) + 1))
                except ValueError:
                    pass
            else:
                try:
                    if part: ids_to_search.append(int(part))
                except ValueError:
                    pass
        if ids_to_search:
            query = query.filter(Registry.id.in_(list(set(ids_to_search))))

    # 7. Es Fuente de Flashcard -> 's' o 'n'
    if is_flashcard_source:
        from core.database import Card
        f_val = is_flashcard_source.lower().strip()
        if f_val == 's':
            # Se devuelven los que tengan el check = 1 explícito, o que implícitamente YA tengan tarjetas hijas en la BD
            query = query.filter(or_(
                Registry.is_flashcard_source == 1,
                Registry.id.in_(db_session.query(Card.parent_id))
            ))
        elif f_val == 'n':
            # Solo registros sin el flag explícito, y que TAMPOCO tengan tarjetas hijas
            query = query.filter(and_(
                or_(Registry.is_flashcard_source == 0, Registry.is_flashcard_source.is_(None)),
                not_(Registry.id.in_(db_session.query(Card.parent_id)))
            ))

    # 8. Paginador y Orden (Dinámico)
    if order_by == 'vdesc':
        query = query.order_by(Registry.last_viewed_at.desc().nulls_last())
    elif order_by == 'vasc':
        query = query.order_by(Registry.last_viewed_at.asc().nulls_first())
    else:
        query = query.order_by(Registry.modified_at.desc())
        
    query = query.limit(limit).offset(offset)
    
    # 9. Ejecución SQL
    results = query.all()
    
    # 10. Mapeo estricto a Pydantic (Tal y como nos pidió la Base)
    pydantic_results: List[ResourceRecord] = []
    for row in results:
        # Algunos registros podrían no tener diccionario json si fueron inserts manuales parciales SQLite
        meta = row.meta_info if row.meta_info else {}
        rr = ResourceRecord(
            id=row.id,
            type=row.type,
            title=row.title or "",
            path_url=row.path_url or "",
            content_raw=row.content_raw,
            metadata_dict=meta,
            is_flashcard_source=bool(row.is_flashcard_source),
            created_at=row.created_at,
            modified_at=row.modified_at,
            last_viewed_at=row.last_viewed_at
        )
        pydantic_results.append(rr)

    return pydantic_results

def parse_query_string(query_str: str) -> dict:
    """
    Parses a smart query string into a dict of filters for search_registry.
    Example: 'python t:docs e:pdf -t:old i:1-50'
    - Default/No prefix: inc_name
    - t: Tag to include
    - -t: Tag to exclude
    - e: Extension to include
    - -e: Extension to exclude
    - i: IDs or ID range
    - s: Source (s:y, s:n)
    """
    filters = {
        'inc_name': [], 'exc_name': [], 
        'inc_tags': [], 'exc_tags': [],
        'inc_exts': [], 'exc_exts': [],
        'inc_ids': "", 'is_source': "",
        'has_info': "", 'order_by': ""
    }
    
    parts = query_str.split()
    for p in parts:
        if p.startswith('t:'):
            filters['inc_tags'].append(p[2:])
        elif p.startswith('-t:'):
            filters['exc_tags'].append(p[3:])
        elif p.startswith('e:'):
            filters['inc_exts'].append(p[2:])
        elif p.startswith('-e:'):
            filters['exc_exts'].append(p[3:])
        elif p.startswith('i:'):
            filters['inc_ids'] = p[2:]
        elif p.startswith('s:'):
            val = p[2:].lower()
            if val in ['s', 'y', '1', 'true']: filters['is_source'] = 's'
            elif val in ['n', '0', 'false']: filters['is_source'] = 'n'
        elif p.startswith('h:'):
            val = p[2:].lower()
            if val in ['s', 'y', '1', 'true']: filters['has_info'] = 's'
            elif val in ['n', '0', 'false']: filters['has_info'] = 'n'
            else: filters['has_info'] = val
        elif p.startswith('o:'):
            filters['order_by'] = p[2:].lower()
        elif p.startswith('-'):
            filters['exc_name'].append(p[1:])
        else:
            filters['inc_name'].append(p)
            
    return {
        'inc_name': ",".join(filters['inc_name']),
        'exc_name': ",".join(filters['exc_name']),
        'inc_tags': ",".join(filters['inc_tags']),
        'exc_tags': ",".join(filters['exc_tags']),
        'inc_exts': ",".join(filters['inc_exts']),
        'exc_exts': ",".join(filters['exc_exts']),
        'inc_ids': filters['inc_ids'],
        'is_source': filters['is_source'],
        'has_info': filters['has_info'],
        'order_by': filters['order_by']
    }
