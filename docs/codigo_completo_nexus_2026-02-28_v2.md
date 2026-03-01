# Nexus — Código Completo Actualizado (v2)
**Generado**: 2026-02-28 10:37
**Post-correcciones**: 8 bugs corregidos, 131 tests pasados

---

## Índice

1. Core — Base de Datos ORM (`core/database.py`)
2. Core — Modelos Pydantic (`core/models.py`)
3. Core — Motor de Búsqueda (`core/search_engine.py`)
4. Core — Staging DB (`core/staging_db.py`)
5. Módulo — File Manager (`modules/file_manager.py`)
6. Módulo — Web Scraper (`modules/web_scraper.py`)
7. Módulo — PKM Manager (`modules/pkm_manager.py`)
8. Módulo — Analytics (`modules/analytics.py`)
9. Módulo — Study Engine (`modules/study_engine.py`)
10. Módulo — Exporter (`modules/exporter.py`)
11. Módulo — Pipeline Manager (`modules/pipeline_manager.py`)
12. Módulo — YouTube Manager (`modules/youtube_manager.py`)
13. Agente IA — Study (`agents/study_agent.py`)
14. Agente IA — Summary (`agents/summary_agent.py`)
15. Agente IA — Relationships (`agents/relationship_agent.py`)
16. Agente IA — DeepSeek (`agents/deepseek_agent.py`)
17. Agente IA — Mutation (`agents/mutation_agent.py`)
18. Web Server — FastAPI (`web_server.py`)
19. Entry Point (`main.py`)

20. Dashboard TUI (`ui/dashboard.py`) — secciones clave

---

## Core — Base de Datos ORM
**Archivo**: `core/database.py`

```python
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, JSON, 
    DateTime, ForeignKey, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.engine import Engine
from pydantic import BaseModel, Field, ConfigDict
from rich.console import Console

console = Console()

# ----------------------------------------------------------------------------
# 1. SQLAlchemy / Database Setup
# ----------------------------------------------------------------------------

# Ruta de la base de datos: En la raíz de Nexus (un nivel arriba de /core)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'nexus.db')

# Asegurarse de que el directorio padre existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Crear el engine usando SQLite
engine = create_engine(f"sqlite:///{DB_PATH}")

# Escuchar en la conexión para habilitar las opciones como WAL
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Modo WAL para alto rendimiento y concurrencia
    cursor.execute("PRAGMA journal_mode=WAL")
    # Activar el soporte para Foreign Keys (constraints)
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------------------------------------------------------------------
# 2. SQLAlchemy Models
# ----------------------------------------------------------------------------

class Registry(Base):
    """
    Tabla 1: registry (El Corazón)
    Almacena CUALQUIER tipo de recurso indexado.
    """
    __tablename__ = 'registry'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False) # file, youtube, web, note, concept, app, account
    title = Column(Text, nullable=True)
    path_url = Column(Text, nullable=True)
    content_raw = Column(Text, nullable=True)
    summary = Column(Text, nullable=True) # Resumen destilado por IA
    
    # Python atributo será 'meta_info', pero en la base de datos se llama 'metadata'
    # Esto previene choques con 'Base.metadata'
    meta_info = Column('metadata', JSON, nullable=True)
    
    is_flashcard_source = Column(Integer, default=0) # 0=False, 1=True
    
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Relaciones ---
    tags = relationship("Tag", back_populates="registry", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="registry", cascade="all, delete-orphan")
    
    links_out = relationship(
        "NexusLink",
        foreign_keys='NexusLink.source_id',
        back_populates="source",
        cascade="all, delete-orphan"
    )
    links_in = relationship(
        "NexusLink",
        foreign_keys='NexusLink.target_id',
        back_populates="target",
        cascade="all, delete-orphan"
    )

class Tag(Base):
    """
    Tabla 2: tags
    Modelo tag-a-registro (uno a muchos)
    """
    __tablename__ = 'tags'
    
    registry_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), primary_key=True)
    value = Column(String, primary_key=True)
    
    registry = relationship("Registry", back_populates="tags")

class NexusLink(Base):
    """
    Tabla 3: nexus_links (Grafos de Relación)
    Conecta cualquier par de registros.
    """
    __tablename__ = 'nexus_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), nullable=False)
    relation_type = Column(String, nullable=True) # ej: "complementa", "referencia", "comparar"
    description = Column(Text, nullable=True)
    
    source = relationship("Registry", foreign_keys=[source_id], back_populates="links_out")
    target = relationship("Registry", foreign_keys=[target_id], back_populates="links_in")

class Card(Base):
    """
    Tabla 4: cards (Sistema de Aprendizaje)
    Preguntas del sistema de repetición espaciada asociadas a registros.
    """
    __tablename__ = 'cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    type = Column(String, nullable=True) # Factual, Conceptual, Relacional
    difficulty = Column(Float, default=0.0)
    stability = Column(Float, default=0.0)
    last_review = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    
    registry = relationship("Registry", back_populates="cards")

# ----------------------------------------------------------------------------
# 3. Pydantic Schemas (Data Validation)
# ----------------------------------------------------------------------------

class RegistryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str = Field(..., description="file, youtube, web, note, concept, app, account")
    title: Optional[str] = None
    path_url: Optional[str] = None
    content_raw: Optional[str] = None
    summary: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None
    is_flashcard_source: bool = False

class TagCreate(BaseModel):
    value: str

class NexusLinkCreate(BaseModel):
    source_id: int
    target_id: int
    relation_type: Optional[str] = None
    description: Optional[str] = None

class CardCreate(BaseModel):
    parent_id: int
    question: str
    answer: str
    type: str = "Factual"
    difficulty: float = 0.0
    stability: float = 0.0

# ----------------------------------------------------------------------------
# 4. CRUD Operations
# ----------------------------------------------------------------------------

def init_db():
    """Crea las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)
    console.print(f"[bold green]✓ Base de datos Nexus (SQLite WAL) inicializada correctamente en:[/] {DB_PATH}")

class NexusCRUD:
    """Clase principal de abstracción para realizar operaciones CRUD básicas."""
    
    def __init__(self):
        self.Session = SessionLocal
        
    def create_registry(self, data: RegistryCreate) -> Registry:
        """Crea un nuevo registro usando los esquemas de Pydantic."""
        with self.Session() as session:
            # Validación: Evitar duplicados por path_url (excepto notas donde path_url puede ser nulo, pero si existe se bloquea)
            if data.path_url:
                existing = session.query(Registry).filter(Registry.path_url == data.path_url).first()
                if existing:
                    console.print(f"[bold white on red]❌ Error de Duplicado:[/] El registro con la ruta/URL '{data.path_url}' ya existe en el Súper Schema (ID {existing.id}). Operación bloqueada.")
                    raise ValueError(f"Registro Duplicado: {data.path_url}")

            # Validación: Descripción obligatoria
            if not data.content_raw or not data.content_raw.strip():
                console.print("[yellow]Aviso: No se proporcionó descripción. Usando título como descripción básica requerida.[/yellow]")
                data.content_raw = f"(Auto-Descripción) Título: {data.title} | Ruta: {data.path_url}"

            # Usar model_dump() de Pydantic v2
            reg = Registry(**data.model_dump())
            session.add(reg)
            session.commit()
            session.refresh(reg)
            console.print(f"[blue]Registry creado:[/] ID {reg.id} (Tipo: {reg.type})")
            return reg
            
    def get_registry(self, registry_id: int) -> Optional[Registry]:
        """Obtiene un registro a partir de su ID."""
        with self.Session() as session:
            # Devolvemos el registro separado pero cargado
            # (Ten en cuenta que usar las relaciones fuera de sesión puede requerir eager_loading)
            return session.query(Registry).filter(Registry.id == registry_id).first()
            
    def add_tag(self, registry_id: int, tag_data: TagCreate) -> Tag:
        """Añade una única etiqueta al registro."""
        with self.Session() as session:
            tag = Tag(registry_id=registry_id, value=tag_data.value)
            session.merge(tag)
            session.commit()
            return tag
            
    def create_link(self, link_data: NexusLinkCreate) -> NexusLink:
        """Crea una relación entre dos registros."""
        with self.Session() as session:
            link = NexusLink(**link_data.model_dump())
            session.add(link)
            session.commit()
            session.refresh(link)
            console.print(f"[magenta]Link Creado:[/] Entre {link.source_id} y {link.target_id}")
            return link

    def create_card(self, card_data: CardCreate) -> Card:
        """Adiciona una nueva flashcard."""
        with self.Session() as session:
            card = Card(**card_data.model_dump())
            session.add(card)
            session.commit()
            session.refresh(card)
            console.print(f"[yellow]Card Creada:[/] Asociada al registro ID {card.parent_id}")
            return card

    def delete_registry(self, registry_id: int) -> bool:
        """Elimina un registro física y lógicamente de la Base de Datos, destruyendo dependencias por si SQLite no activó el PRAGMA CASCADE."""
        with self.Session() as session:
            from sqlalchemy import or_
            # Eliminación explícita defensiva 
            session.query(Tag).filter(Tag.registry_id == registry_id).delete(synchronize_session=False)
            session.query(NexusLink).filter(or_(NexusLink.source_id == registry_id, NexusLink.target_id == registry_id)).delete(synchronize_session=False)
            session.query(Card).filter(Card.parent_id == registry_id).delete(synchronize_session=False)
            
            # Matar registro principal
            deleted = session.query(Registry).filter(Registry.id == registry_id).delete(synchronize_session=False)
            session.commit()
            return deleted > 0

    def update_summary(self, registry_id: int, summary_text: str) -> bool:
        """Actualiza el resumen de un registro."""
        with self.Session() as session:
            rows = session.query(Registry).filter(Registry.id == registry_id).update({
                Registry.summary: summary_text
            })
            session.commit()
            return rows > 0

# Exportamos la instancia para su uso global si así se requiere
nx_db = NexusCRUD()

if __name__ == "__main__":
    init_db()

```

---

## Core — Modelos Pydantic
**Archivo**: `core/models.py`

```python
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

# Definición de tipos permitidos para el registro
ResourceType = Literal['file', 'youtube', 'web', 'note', 'concept', 'app', 'account']

class ResourceRecord(BaseModel):
    """
    Espejo de la tabla 'registry'.
    Almacena los datos maestros de cualquier recurso indexado.
    """
    id: Optional[int] = None
    type: ResourceType = Field(..., description="Tipo de recurso")
    title: str = Field(..., description="Nombre o título del recurso")
    path_url: str = Field(..., description="Ruta física local o URL externa")
    content_raw: Optional[str] = Field(default=None, description="Contenido extraído o notas")
    summary: Optional[str] = Field(default=None, description="Resumen destilado por IA")
    metadata_dict: Dict[str, Any] = Field(default_factory=dict, description="Metadatos en formato JSON")
    is_flashcard_source: bool = Field(default=False, description="¿Marcado como fuente de flashcards?")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)


class NexusLink(BaseModel):
    """
    Representa un grafo de relaciones entre dos ResourceRecords.
    """
    source_id: int = Field(..., description="ID del recurso origen")
    target_id: int = Field(..., description="ID del recurso destino")
    relation_type: str = Field(..., description="Tipo de relación (ej. complementa, referencia)")
    description: str = Field(..., description="Notas sobre la relación")


class StudyCard(BaseModel):
    """
    Representa una tarjeta de estudio estilo Spaced Repetition System.
    """
    id: Optional[int] = None
    parent_id: int = Field(..., description="ID del ResourceRecord del cual proviene esta pregunta")
    question: str = Field(..., description="Pregunta a evaluar")
    answer: str = Field(..., description="Respuesta a la pregunta")
    card_type: str = Field(..., description="Tipo de carta (Factual, Conceptual, Relacional)")
    srs_data: Dict[str, Any] = Field(
        default_factory=lambda: {"difficulty": 0.0, "stability": 0.0, "last_review": None, "next_review": None},
        description="Datos requeridos por el algoritmo de repetición espaciada"
    )

```

---

## Core — Motor de Búsqueda
**Archivo**: `core/search_engine.py`

```python
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

    # 8. Paginador y Orden (Siempre el modificado recientemente de primero)
    query = query.order_by(Registry.modified_at.desc()).limit(limit).offset(offset)
    
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
            modified_at=row.modified_at
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
        'inc_ids': "", 'is_source': ""
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
        'has_info': ""
    }

```

---

## Core — Staging DB
**Archivo**: `core/staging_db.py`

```python

import os
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from core.database import Base, NexusCRUD, Registry, RegistryCreate, nx_db
from rich.console import Console

console = Console()

# 1. Definir la ruta en G: (Google Drive)
STAGING_DB_DIR = r"G:\Mi unidad\Nexus_Staging"
STAGING_DB_PATH = os.path.join(STAGING_DB_DIR, "staging_buffer.db")

# Crear el engine para el buffer de G:
def get_staging_engine():
    if not os.path.exists(STAGING_DB_DIR):
        try:
            os.makedirs(STAGING_DB_DIR, exist_ok=True)
        except Exception as e:
            # Fallback a local si G: no esta montado
            console.print(f"[bold yellow]⚠ Buffer Google Drive (G:) no disponible. Operando en modo local.[/] ({e})")
            return None
    return create_engine(f"sqlite:///{STAGING_DB_PATH}")

staging_engine = get_staging_engine()

# Configurar PRAGMAs para el buffer
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session y CRUD para Staging
if staging_engine:
    StagingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=staging_engine)
else:
    StagingSessionLocal = None

class StagingCRUD(NexusCRUD):
    """
    Hereda de NexusCRUD pero apunta a la sesion del buffer en G:
    """
    def __init__(self):
        self.Session = StagingSessionLocal

    def _check_available(self):
        """Verifica que el Staging DB esté operativo antes de cualquier operación."""
        if self.Session is None:
            console.print("[bold yellow]⚠ Staging DB no disponible (G: no montado). Operación cancelada.[/]")
            return False
        return True

    def create_registry(self, data):
        if not self._check_available():
            return None
        return super().create_registry(data)

    def get_registry(self, registry_id):
        if not self._check_available():
            return None
        return super().get_registry(registry_id)

    def init_staging(self):
        if staging_engine:
            Base.metadata.create_all(bind=staging_engine)
            return True
        return False

# Instancia global del buffer
staging_db = StagingCRUD()

def get_current_db(mode="local"):
    """
    Retorna la instancia de DB activa.
    'local' -> nexus.db (SSD)
    'staging' -> staging_buffer.db (G: Drive)
    """
    if mode == "staging" and staging_engine:
        return staging_db
    return nx_db

```

---

## Módulo — File Manager
**Archivo**: `modules/file_manager.py`

```python
import os
from pathlib import Path
from typing import List, Optional

from core.database import nx_db, RegistryCreate, TagCreate
from core.models import ResourceRecord
from rich.console import Console

console = Console()

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
        console.print(f"[bold white on red]Error:[/] El archivo no existe o no es un archivo válido: {filepath}")
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
        console.print(f"[bold white on red]Error fatal al intentar guardar en la base de datos:[/] {e}")
        return None

if __name__ == "__main__":
    # Test rápido de compilación
    pass

```

---

## Módulo — Web Scraper
**Archivo**: `modules/web_scraper.py`

```python
import re
from urllib.parse import urlparse, parse_qs
from core.database import nx_db, RegistryCreate, TagCreate

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

def ingest_web_resource(url: str, tags: list[str], db_target=nx_db):
    """
    Determina si la URL es de YouTube o una página web genérica,
    extrae el contenido y lo guarda en la base de datos especificada (Local o Staging).
    """
    if not requests or not BeautifulSoup:
        print("[bold white on red]Faltan librerías. Por favor instala: requests y beautifulsoup4[/]")
        return None

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    if "youtube.com" in domain or "youtu.be" in domain:
        return _ingest_youtube(url, parsed_url, tags, db_target)
    else:
        return _ingest_generic_web(url, tags, db_target)

def _get_youtube_video_id(url: str, parsed_url) -> str:
    """Extrae el ID del video de YouTube a partir de la URL."""
    if "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip('/')
    if "youtube.com" in parsed_url.netloc:
        qs = parse_qs(parsed_url.query)
        if 'v' in qs:
            return qs['v'][0]
    return ""

def _ingest_youtube(url: str, parsed_url, tags: list[str], db_target):
    """Extrae título y subtítulos de un video de YouTube."""
    if not YouTubeTranscriptApi or not yt_dlp:
        print("[bold white on red]Faltan librerías para YouTube. Instala: youtube-transcript-api y yt-dlp[/]")
        return None
        
    video_id = _get_youtube_video_id(url, parsed_url)
    if not video_id:
        print(f"[yellow]No se pudo extraer de ID de video de YouTube para: {url}[/yellow]")
        return None
        
    title = f"YouTube Video ({video_id})"
    content_raw = ""
    
    # Intentar obtener métricas y metadatos usando yt-dlp
    meta_info = {"video_id": video_id, "platform": "youtube"}
    try:
        class MyLogger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        ydl_opts = {
            'quiet': True, 
            'no_warnings': True, 
            'logger': MyLogger(),
            'extract_flat': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict:
                title = info_dict.get('title', title)
                meta_info.update({
                    "channel": info_dict.get('uploader'),
                    "duration": info_dict.get('duration'),
                    "view_count": info_dict.get('view_count'),
                    "upload_date": info_dict.get('upload_date'),
                    "description": info_dict.get('description', '')[:500] # Primeras lineas
                })
    except Exception as e:
        # Fallback silencioso para el título si yt-dlp falla
        pass

    # Obtener transcripción
    try:
        # Intenta primero español, luego inglés si falla u otros.
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        # Buscar transcript manual antes de los generados (idioma es o en)
        try:
            transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
        except Exception:
            # Si no encuentra manual, agarrar cualquiera o el generado
            try:
                transcript = transcript_list.find_generated_transcript(['es', 'en'])
            except:
                # Si no hay es/en, agarrar el primero disponible
                transcript = next(iter(transcript_list))
            
        full_transcript = transcript.fetch()
        
        text_fragments = [item.text if hasattr(item, "text") else item["text"] for item in full_transcript]
        content_raw = " ".join(text_fragments)
        
        if len(content_raw) > 50000:
            content_raw = content_raw[:49997] + "..."
            
    except Exception as e:
        error_msg = str(e).split('\n')[0] or type(e).__name__
        print(f"[yellow]Aviso: No se pudo obtener la transcripción. Se guardará sin texto base. ({error_msg})[/yellow]")
        content_raw = "(Video guardado sin Transcripción Disponible)."

    # Insertar en BD
    try:
        data = RegistryCreate(
            type="youtube",
            title=title,
            path_url=url,
            content_raw=content_raw,
            meta_info=meta_info
        )
        reg = db_target.create_registry(data)
        
        # Asociar tags
        for t in tags:
            db_target.add_tag(reg.id, TagCreate(value=t))
            
        return reg
    except Exception as e:
        print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return None

def get_playlist_video_urls(playlist_url: str):
    """
    Usa yt-dlp para obtener todas las URLs de videos de una playlist.
    """
    urls = []
    try:
        class MyLogger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'logger': MyLogger(),
            'extract_flat': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            if 'entries' in playlist_info:
                for entry in playlist_info['entries']:
                    if entry.get('url'):
                        # yt-dlp a veces devuelve solo el ID o el path, aseguramos URL completa
                        video_url = entry['url']
                        if not video_url.startswith('http'):
                            video_url = f"https://www.youtube.com/watch?v={video_url}"
                        urls.append(video_url)
    except Exception as e:
        print(f"[red]Error extrayendo playlist: {e}[/]")
    return urls

def batch_ingest_urls(urls_list: list[str], tags: list[str], db_target=nx_db):
    """
    Procesa un lote de URLs secuencialmente.
    Retorna (un proceso exitoso, un proceso fallido).
    """
    total = len(urls_list)
    success = []
    failed = []
    
    for i, url in enumerate(urls_list):
        url = url.strip()
        if not url: continue
        
        print(f"\n[bold cyan][{i+1}/{total}][/] Procesando: [dim]{url}[/]")
        reg = ingest_web_resource(url, tags, db_target=db_target)
        if reg:
            success.append(reg)
        else:
            failed.append(url)
            
    return success, failed


def _ingest_generic_web(url: str, tags: list[str], db_target):
    """Extrae título y párrafos limpiados de una página web."""
    try:
        # Añadir cabeceras comunes para evitar bloqueos básicos de web servers (403 Prohibidden)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"[yellow]Aviso: Ocurrió un error conectando a la página (puede requerir JS o estar bloqueada). Se guardará la URL huérfana. Error: {str(e)}[/yellow]")
        # Guardado básico de rescate para url
        try:
            reg = db_target.create_registry(RegistryCreate(
                type="web", title=url, path_url=url, content_raw="Error al raspar el contenido web."
            ))
            for t in tags:
                db_target.add_tag(reg.id, TagCreate(value=t))
            return reg
        except:
             return None
             
    soup = BeautifulSoup(res.text, 'html.parser')

    # Obtener el Título
    title = soup.title.string.strip() if soup.title and soup.title.string else url

    # Limpiar tags basura que no aportan al raw text
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()

    # Extraer texto de párrafos y divs de manera legible
    paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
    content_raw = "\n\n".join([p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    if len(content_raw) > 50000:
            content_raw = content_raw[:49997] + "..."
            
    try:
        data = RegistryCreate(
            type="web",
            title=title,
            path_url=url,
            content_raw=content_raw,
            meta_info={"platform": "web"}
        )
        reg = db_target.create_registry(data)
        
        for t in tags:
            db_target.add_tag(reg.id, TagCreate(value=t))
            
        return reg
    except Exception as e:
        print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return None

```

---

## Módulo — PKM Manager
**Archivo**: `modules/pkm_manager.py`

```python
import os
import tempfile
import subprocess
from typing import List, Optional

from core.database import nx_db, RegistryCreate, TagCreate, SessionLocal
from core.models import ResourceRecord
from rich.console import Console

console = Console()

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
        console.print(f"\n[bold cyan]Abriendo editor para la nota:[/bold cyan] '{title}'...")
        console.print("[yellow]La terminal está en espera. Cierra el bloc de notas para guardar...[/yellow]\n")
        
        # subprocess.run es bloqueante por defecto
        subprocess.run(['notepad', temp_path], check=True)
        
    except Exception as e:
        console.print(f"[bold white on red]Error al intentar abrir el editor:[/] {e}")
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
        console.print("[bold white on red]La nota está vacía o sin cambios. Abortando guardado.[/]")
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

```

---

## Módulo — Analytics
**Archivo**: `modules/analytics.py`

```python
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

```

---

## Módulo — Study Engine
**Archivo**: `modules/study_engine.py`

```python
import time
import os
import subprocess
import webbrowser
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Asumiendo que el script principal establece la raíz del proyecto para importaciones
from core.database import nx_db, Card, Registry

from rich.theme import Theme

# Tema de alto contraste para visibilidad absoluta
custom_theme = Theme({
    "dim": "bright_white",
    "cyan": "bright_cyan",
    "magenta": "yellow",
    "blue": "bright_blue",
})

console = Console(theme=custom_theme)

class SRSEngine:
    def __init__(self):
        pass

    def calculate_next_review(self, card: Card, grade: int, elapsed_seconds: float):
        """
        Calcula y actualiza los factores SRS de la tarjeta (stability, difficulty, dates)
        incorporando el tiempo de respuesta. Si el usuario tardó mucho pero marcó 'Fácil', 
        se penaliza la respuesta para no incrementar tanto el intervalo de retención.
        """
        # Grade: 1 (Difícil), 2 (Bien), 3 (Fácil)
        # Ajuste penalizando 'Fácil' si tomó mucho tiempo (ej > 15 segs)
        if grade == 3 and elapsed_seconds > 15.0:
            # Penalizar convirtiendo en un "Bien" virtual para el cálculo de estabilidad
            grade_calc = 2.5
        else:
            grade_calc = float(grade)
        
        # Algoritmo simple inspirado en FSRS/SM-2
        
        if card.stability == 0.0 or card.stability is None:
             # Valores iniciales (en días)
             initial_stability = {1: 1.0, 2: 3.0, 3: 5.0, 2.5: 4.0}
             card.stability = initial_stability.get(grade_calc, 3.0)
             card.difficulty = 5.0 - grade_calc # 1 -> 4, 2 -> 3, 3 -> 2
        else:
             modifier = {1: 0.5, 2: 1.5, 2.5: 1.8, 3: 2.5}.get(grade_calc, 1.5)
             card.stability = max(1.0, card.stability * modifier)
             card.difficulty = max(1.0, min(10.0, card.difficulty + (2.0 - grade_calc) * 0.5))

        # Calcular próxima fecha
        interval_days = card.stability
        card.last_review = datetime.now(timezone.utc)
        card.next_review = card.last_review + timedelta(days=interval_days)


def open_source_material(registry):
    """
    Abre o muestra el material fuente asociado a un registro cruzando local y web.
    """
    path_or_url = str(registry.path_url).strip() if registry.path_url else ""
    
    # 1. Si es un Link de Internet (YouTube/Web) -> Navegador Default
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        import webbrowser
        webbrowser.open(path_or_url)
    
    # 2. Si es una Ruta Física Local (Archivo PDF/Nota) -> Lanzar programa local
    elif path_or_url and os.path.exists(path_or_url):
        try:
            if os.name == 'nt':
                os.startfile(os.path.normpath(path_or_url))  # Intento normal en Windows
            else:
                import subprocess
                subprocess.run(['xdg-open', path_or_url]) 
        except Exception as e:
            # Fallback para WinError 1155 (Sin asociación) o errores similares
            if os.name == 'nt':
                console.print(f"[yellow]Aviso: No hay una app predeterminada para este archivo. Abriendo selector...[/]")
                os.system(f'rundll32.exe shell32.dll,OpenAs_RunDLL {os.path.normpath(path_or_url)}')
            else:
                console.print(f"[bold red]Error al abrir el archivo:[/] {e}")
                time.sleep(2)
            
    # 3. Si no tiene archivo físico sino que es una mera "Nota" de texto en la Base de Datos
    elif registry.content_raw and registry.content_raw.strip():
        import tempfile
        import subprocess
        
        # Crear un archivo markdown temporal para que el OS lo abra
        fd, temp_path = tempfile.mkstemp(suffix=".md", prefix="nota_virtual_")
        
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(f"# {registry.title}\n\n")
            f.write(registry.content_raw)
            
        try:
            if os.name == 'nt':
                console.print(f"[bold cyan]Forzando la selección de visor de Markdown para '{registry.title}'...[/]")
                console.print("[dim]Por favor, selecciona 'Markdown Viewer' (o tu app preferida) en la ventana que aparecerá y marca 'Siempre usar esta aplicación' para que en el futuro sea automático.[/dim]")
                time.sleep(1)
                
                # Invoca el cuadro de "Abrir con..." nativo de Windows para forzar la vinculación
                os.system(f'rundll32.exe shell32.dll,OpenAs_RunDLL {temp_path}')
            else:
                import subprocess
                subprocess.run(['xdg-open', temp_path])
        except Exception as e:
            console.print(f"[bold red]Aviso: No se pudo abrir la app. Error: {e}[/]")
            console.print(Panel(registry.content_raw[:1500] + ("..." if len(registry.content_raw) > 1500 else ""), title=f"Nota Virtual: {registry.title}", border_style="yellow"))
        
    else:
        console.print("[bold white on red]Este Registro no tiene archivo físico local, Ni un link Web, Ni contenido de texto.[/]")
        
    Prompt.ask("\n[bold]Presiona Enter para continuar con la sesión...[/]", console=console)

def get_due_cards(session, adelantar=False, topic_id=None, shuffled=False, card_limit=None):
    """
    Obtiene las tarjetas programadas para repaso, filtrando opcionalmente por un Registro/Tema.
    """
    now = datetime.now(timezone.utc)
    query = session.query(Card)
    if topic_id is not None:
        query = query.filter(Card.parent_id == topic_id)
        
    if not adelantar:
        # Filtra las que no tengan fecha o cuya fecha esté en el pasado/presente
        query = query.filter((Card.next_review == None) | (Card.next_review <= now))
    
    if shuffled:
        import random
        cards = query.all()
        random.shuffle(cards)
    else:
        cards = query.order_by(Card.next_review).all()

    if card_limit and card_limit > 0:
        cards = cards[:card_limit]
        
    return cards

def start_pomodoro_session(pomodoro_minutes: int = 25, adelantar: bool = False, topic_id: int = None, skip_first_source_prompt: bool = False, shuffled: bool = False, card_limit: int = None):
    """
    Inicia una sesión de Active Recall bajo el método Pomodoro.
    """
    srs = SRSEngine()
    start_time = time.time()
    duration_secs = pomodoro_minutes * 60
    
    with nx_db.Session() as session:
        cards = get_due_cards(session, adelantar=adelantar, topic_id=topic_id, shuffled=shuffled, card_limit=card_limit)
        
        if not cards:
            if session.query(Card).count() == 0:
                console.print("\n[bold white on red]¡Tu Sistema no tiene Flashcards![/]")
                console.print("[yellow]Aún no has generado ninguna tarjeta de estudio en toda la base de datos.[/]")
                console.print("[bright_cyan]Idea:[/] Ve al Menú Explorador (Opción 2), abre un registro con [bold]vID[/bold] y usa el agente de IA para generar un mazo de cartas de ese documento.\n")
            else:
                console.print("\n[yellow]No hay tarjetas pendientes para repasar hoy.[/]")
                if not adelantar:
                     console.print("Utiliza la opción 'Adelantar Tarjetas' en el menú principal si quieres forzar la cola de estudio.\n")
            return

        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(f"[bold yellow]🚀 Iniciando Sesión Active Recall (Pomodoro: {pomodoro_minutes} min)[/]\n")
        time.sleep(1.5)

        total_cards = len(cards)
        last_topic_id = None
        cards_to_mutate = []
        for idx, card in enumerate(cards, 1):
            current_time = time.time()
            if current_time - start_time >= duration_secs:
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print(Panel("[bold white on red]¡Tiempo de Pomodoro agotado![/]\n\n"
                                    f"Has estudiado intensamente durante {pomodoro_minutes} minutos.\n"
                                    "¡Toma un descanso y procesa lo aprendido!", 
                                    title="🍅 Pomodoro Finalizado", border_style="red"))
                break
            
            console.clear()
            # Mostrar progreso de tiempo limpio desde cero
            time_left = duration_secs - (current_time - start_time)
            mins, secs = divmod(int(max(0, time_left)), 60)
            
            # Chromatic visual para el tiempo
            color_time = "bright_cyan" if time_left > 300 else "bold white on red"
            
            # Obtener contexto
            reg = session.query(Registry).get(card.parent_id)
            source_title = reg.title if reg else "Desconocido"
            source_url = reg.path_url if reg and reg.path_url else "Sin URL física o Web"
            
            # Formateamos URL para terminales modernas si es link
            disp_url = f"[link={source_url}]{source_url}[/link]" if str(source_url).startswith("http") else source_url
            
            is_new_topic = (card.parent_id != last_topic_id)
            
            # 1. Función Interna para repintar la Cabecera limpidamente y evitar Overlaps
            def draw_header():
                os.system('cls' if os.name == 'nt' else 'clear') # Hard clear en OS
                console.print(f"[{color_time}]⏳ Tiempo restante: {mins:02d}:{secs:02d}[/]  |  [bold yellow]🗂️ Tarjeta {idx} de {total_cards}[/]\n")
                if is_new_topic:
                    console.print(Panel(f"[bold bright_cyan]Tema de Estudio:[/] {source_title}\n[bold bright_cyan]Ubicación/Enlace:[/] {disp_url}\n[yellow](Para navegar hasta esta ubicación, escribe la tecla 'f' en el menú de abajo, o haz Ctrl+Click si la URL es azul)[/yellow]", title="📚 Contexto de la Tarjeta", border_style="bright_cyan"))
                else:
                    console.print(f"[white]📚 Repasando:[/] [bold bright_cyan]{source_title}[/]\n")
                
            draw_header()
            
            # 2. Bucle interactivo para Material Fuente (SOLO si es un tema nuevo en la cola actual)
            if is_new_topic:
                # Si venimos del menú 2 y ya abrimos la fuente antes del pomodoro, omitimos esta molestia en la 1ra tarjeta
                if skip_first_source_prompt and last_topic_id is None:
                    pass
                else:
                    while True:
                        action = Prompt.ask("\n[yellow]¿Deseas leer el tema fuente ahora? ([bold]f[/] para abrir / [bold]Enter[/] para saltar a la Pregunta)[/]", console=console).strip().lower()
                        if action == 'f':
                            if reg:
                                console.print("\n[bright_white]Abriendo material fuente en segundo plano...[/bright_white]")
                                open_source_material(reg)
                                draw_header() # Redibujamos cabecera tras volver
                            else:
                                console.print("[bold white on red]Registro huérfano o no encontrado en la base de datos.[/]")
                                time.sleep(1.5)
                                draw_header()
                        else:
                            break
                # Guardar el tema actual como "último visto"
                last_topic_id = card.parent_id
            
            # 3. Mostrar Pregunta (Lógica de Renderizado Dinámico por Tipo)
            draw_header()
            console.print("")
            
            card_type = str(card.type).lower()
            auto_graded = False
            correct_answer = card.answer
            user_attempt = None

            # --- RENDERIZADO POR TIPO ---
            if "cloze" in card_type or "hueco" in card_type:
                import re
                display_q = re.sub(r"\{\{c\d+::(.*?)\}\}", "[...]", card.question)
                console.print(Panel(display_q, title="❓ Rellenar Huecos", border_style="bright_blue"))
            
            elif "mcq" in card_type or "opcion multiple" in card_type:
                try:
                    import json
                    data = json.loads(card.question)
                    prompt_text = data.get("prompt", "Selecciona la opción correcta:")
                    options = data.get("options", {})
                    console.print(Panel(prompt_text, title="❓ Opción Múltiple", border_style="bright_blue"))
                    for k, v in options.items():
                        console.print(f"  [bold yellow]{k})[/] {v}")
                    auto_graded = True
                except:
                    console.print(Panel(card.question, title="❓ Opción Múltiple (Formato Simple)", border_style="blue"))
            
            elif "tf" in card_type or "verdadero" in card_type:
                console.print(Panel(card.question, title="❓ ¿Verdadero o Falso?", border_style="bright_blue"))
                console.print("  [bold bright_cyan]v)[/] Verdadero")
                console.print("  [bold bright_cyan]f[/]) Falso")
                auto_graded = True

            elif "matching" in card_type or "emparejar" in card_type:
                try:
                    import json
                    data = json.loads(card.question) # p.ej {"pairs": {"Perú": "Lima", "Chile": "Santiago"}}
                    pairs = data.get("pairs", {})
                    left = list(pairs.keys())
                    right = list(pairs.values())
                    import random
                    random.shuffle(right)
                    
                    console.print(Panel("Empareja los términos de la izquierda con la derecha:", title="❓ Emparejamiento", border_style="bright_blue"))
                    for idx, val in enumerate(left, 1):
                        console.print(f"  {idx}. [bold bright_cyan]{val}[/]  <--->  [bold yellow]{chr(96+idx)})[/] {right[idx-1]}")
                    auto_graded = True
                except:
                    console.print(Panel(card.question, title="❓ Emparejamiento", border_style="bright_blue"))

            else:
                # Caso por defecto: Factual/Normal
                console.print(Panel(card.question, title="❓ Pregunta a Resolver", border_style="bright_blue"))
            
            action_start_time = time.time()
            card_needs_grading = True
            
            while True:
                prompt_msg = "\n[yellow]Respuesta (Enter), 'editar', 'eliminar' o 'atras'[/]"
                if auto_graded:
                    prompt_msg = "\n[bold yellow]Tu Elección (ej. 'a', 'b' o 'v'):[/]"
                
                user_answer = Prompt.ask(prompt_msg, console=console)
                u_ans_lower = user_answer.strip().lower()

                if u_ans_lower in ['salir', 'atras', 'regresar']:
                    console.print("\n[yellow]Saliendo de la sesión de Active Recall...[/]")
                    time.sleep(1)
                    card_needs_grading = False
                    break
                
                elif u_ans_lower == 'eliminar':
                    confirm = Prompt.ask("¿Seguro que deseas [bold red]ELIMINAR[/] esta Flashcard permanentemente? (s/n)", console=console).strip().lower()
                    if confirm == 's':
                        session.delete(card)
                        session.commit()
                        console.print("[bold green]✔ Tarjeta eliminada.[/]")
                        time.sleep(1)
                        card_needs_grading = False
                        break
                    else:
                        draw_header()
                        # Re-mostrar
                        continue
                
                elif u_ans_lower == 'editar':
                    console.print("\n[bold bright_cyan]--- Modificando Tarjeta ---[/]")
                    new_q = Prompt.ask("Nueva Pregunta o JSON", default=card.question, console=console).strip()
                    new_a = Prompt.ask("Nueva Respuesta", default=card.answer, console=console).strip()
                    if new_q: card.question = new_q
                    if new_a: card.answer = new_a
                    session.commit()
                    console.print("[bold green]✔ Actualizada.[/]")
                    time.sleep(1)
                    draw_header()
                    continue
                
                else:
                    user_attempt = user_answer
                    break
            
            if not card_needs_grading:
                if u_ans_lower in ['salir', 'atras', 'regresar']:
                    break
                continue 
            
            elapsed_seconds = time.time() - action_start_time
            
            # 4. Mostrar Respuesta y Calificar
            console.print("")
            if user_attempt and user_attempt.strip():
                console.print(f"[bold bright_blue]Tú escribiste/elegiste:[/] {user_attempt}\n")
            
            # Verificación automática
            is_correct = None
            if auto_graded and user_attempt:
                if u_ans_lower == str(card.answer).strip().lower():
                    is_correct = True
                    console.print("[bold green]✅ ¡Correcto![/]")
                else:
                    is_correct = False
                    console.print(f"[bold red]❌ Incorrecto. La respuesta era: {card.answer}[/]")

            console.print(Panel(card.answer, title="💡 Respuesta Correcta", border_style="green"))
            
            # 5. Calificación
            if is_correct is True:
                grade_str = "3" # Fácil
            elif is_correct is False:
                grade_str = "1" # Malo
            else:
                grade_str = Prompt.ask("\nCalifica tu nivel de recuerdo:\n [1] [bold red]Malo/Olvidado[/] \n [2] [bold green]Bueno/Correcto[/] \n [3] [bold bright_cyan]Fácil/Perfecto[/]\n Elije un número", choices=["1", "2", "3"], default="2", console=console)
            
            agrade = {"1": "Malo (Re-estudio)", "2": "Bueno (Repaso normal)", "3": "Fácil (Salto largo)"}[grade_str]
            grade = int(grade_str)
            
            # 6. Actualizar BD
            srs.calculate_next_review(card, grade, elapsed_seconds)
            cards_to_mutate.append(card.id) 
            session.commit()
            
            console.print(f"\n[bold green]✔ Hecho! Próximo repaso: {card.next_review.strftime('%Y-%m-%d %H:%M')}[/]")
            time.sleep(1.5) 
            
        else:
            # Si culminó el loop de tarjetas sin interrupción de tiempo
            os.system('cls' if os.name == 'nt' else 'clear')
            time_total = int(time.time() - start_time)
            mins, secs = divmod(time_total, 60)
            console.print(Panel(f"[bold green]¡Has terminado todas las tarjetas en la cola actual![/]\n\n"
                                f"Tiempo invertido: {mins:02d}m {secs:02d}s",
                                title="🏆 Cola Completada", border_style="green"))

        # ---------------------------------------------------------------------
        # FASE FINAL: Intervención del Agente Mutador (IA) (Acumulación >= 20)
        # ---------------------------------------------------------------------
        if cards_to_mutate:
            import json
            # Definir locación para acumular las tarjetas repasadas
            pending_mutations_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'pending_mutations.json')
            
            # Cargar pendientes anteriores si existen
            pending_cards = []
            if os.path.exists(pending_mutations_file):
                try:
                    with open(pending_mutations_file, 'r', encoding='utf-8') as f:
                        pending_cards = json.load(f)
                except Exception:
                    pass
            
            # Agregar nuevas y quitar duplicados (para no acumular la misma tarjeta en varias sesiones seguidas)
            pending_cards.extend(cards_to_mutate)
            pending_cards = list(set(pending_cards))
            
            # Chequear si llegamos a la meta de al menos 20
            if len(pending_cards) >= 20:
                run_m = Prompt.ask(
                    f"\n[bold yellow]🤖 Has alcanzado el límite para el Mutador ({len(pending_cards)} tarjetas acumuladas).\n"
                    "¿Deseas activar el Agente Mutador de IA para analizarlas y reformularlas (rompiendo la memorización sistemática)?[/] (s/n)",
                    choices=["s", "n"], default="n", console=console
                ).strip().lower()
                
                if run_m == 's':
                    from agents.mutation_agent import mutate_cards
                    mutate_cards(pending_cards)
                    # Tras correr el mutador, vaciamos el acumulador
                    if os.path.exists(pending_mutations_file):
                        os.remove(pending_mutations_file)
                else:
                    # El usuario dijo 'n', guardamos el acumulado para la próxima sesión
                    os.makedirs(os.path.dirname(pending_mutations_file), exist_ok=True)
                    with open(pending_mutations_file, 'w', encoding='utf-8') as f:
                        json.dump(pending_cards, f)
            else:
                # Si no llegó a 20, grabamos el progreso para que se acumulen sin molestar aún
                console.print(f"\n[white]Se han guardado estas tarjetas para futura mutación de la IA (Total acumulado: {len(pending_cards)}/20).[/white]")
                os.makedirs(os.path.dirname(pending_mutations_file), exist_ok=True)
                with open(pending_mutations_file, 'w', encoding='utf-8') as f:
                    json.dump(pending_cards, f)

if __name__ == '__main__':
    # Punto de prueba aislado para testing rápido
    try:
        start_pomodoro_session(25, adelantar=False)
    except KeyboardInterrupt:
        console.clear()
        console.print("[yellow]Sesión interrumpida por el usuario.[/yellow]")

```

---

## Módulo — Exporter
**Archivo**: `modules/exporter.py`

```python

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

```

---

## Módulo — Pipeline Manager
**Archivo**: `modules/pipeline_manager.py`

```python

import os
import json
import time
from datetime import datetime
from modules.web_scraper import get_playlist_video_urls, ingest_web_resource
from agents.deepseek_agent import deepseek_agent
from core.database import nx_db, RegistryCreate, CardCreate, TagCreate
from core.staging_db import staging_db
from rich.console import Console
from rich.progress import Progress

console = Console()

QUEUE_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_queue.txt"
HISTORY_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_history.json"

from modules.youtube_manager import YouTubeManager

def run_youtube_pipeline():
    """
    Ejecuta el plan de trabajo automatizado para playlists:
    1. Lee cola de playlists.
    2. Descarga a Staging (G:).
    3. Procesa con DeepSeek.
    4. Mueve a Nexus Local.
    5. Opcional: Elimina el video de la playlist de YouTube (via API).
    """
    # Asegurar que el Buffer de Staging esté inicializado
    staging_db.init_staging()

    yt_manager = None
    if os.path.exists('client_secrets.json'):
        try:
            # Forzamos un timeout corto para no bloquear el inicio si no hay red
            with console.status("[dim]Estableciendo conexión con YouTube API...[/dim]", spinner="dots"):
                yt_manager = YouTubeManager()
                console.print("[bold green]✓ Conexión con YouTube API establecida (Modo Gestión Activo).[/bold green]")
        except Exception as e:
            console.print(f"[yellow]Aviso: No se pudo conectar con YouTube API. Se usará Modo Scraping (Modo Rescate). {e}[/yellow]")
            yt_manager = None

    if not os.path.exists(QUEUE_FILE):
        console.print(f"[yellow]Aviso: No se encontro el archivo de cola en {QUEUE_FILE}[/yellow]")
        return

    # Cargar historial
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)

    with open(QUEUE_FILE, 'r') as f:
        playlists_urls = [line.strip() for line in f if line.strip() and line.strip() not in history]

    if not playlists_urls:
        console.print("[green]No hay nuevas playlists para procesar en la cola.[/green]")
        return

    console.print(f"[bold cyan]🚀 Iniciando Pipeline para {len(playlists_urls)} playlists...[/bold cyan]")

    for p_url in playlists_urls:
        console.print(f"\n[bold yellow]📂 Procesando Playlist:[/] {p_url}")
        
        videos_to_process = []
        playlist_id = None
        
        # Intentar obtener videos via API oficial si esta disponible
        if yt_manager:
            playlist_id = yt_manager.get_playlist_id_from_url(p_url)
            if playlist_id:
                videos_to_process = yt_manager.get_playlist_items(playlist_id)
        
        # Fallback a yt-dlp si la API fallo o no esta disponible
        if not videos_to_process:
            raw_urls = get_playlist_video_urls(p_url)
            if raw_urls:
                videos_to_process = [{'url': u, 'title': u, 'playlist_item_id': None} for u in raw_urls]
            else:
                # Si no es playlist, es un video individual. Lo agregamos para procesar.
                videos_to_process = [{'url': p_url, 'title': p_url, 'playlist_item_id': None}]

        console.print(f"   • {len(videos_to_process)} recursos detectados para procesar.")
        
        for v_data in videos_to_process:
            v_url = v_data['url']
            v_item_id = v_data['playlist_item_id']
            
            console.print(f"\n   [cyan]»[/] Procesando: [italic]{v_data['title']}[/italic]")
            
            # 2. Descarga masiva a Staging (G:)
            reg_staging = ingest_web_resource(v_url, ["pipeline_staging"], db_target=staging_db)
            
            if reg_staging:
                # 3. Procesamiento Inteligente con DeepSeek
                console.print(f"     • Generando Inteligencia con DeepSeek...")
                resumen, cards = deepseek_agent.process_content(reg_staging.title, reg_staging.content_raw)
                
                # 4. Centralizacion en Nexus (Local SSD)
                try:
                    data_final = RegistryCreate(
                        type="youtube",
                        title=reg_staging.title,
                        path_url=reg_staging.path_url,
                        content_raw=reg_staging.content_raw,
                        summary=resumen,
                        meta_info=reg_staging.meta_info,
                        is_flashcard_source=True
                    )
                    reg_nexus = nx_db.create_registry(data_final)
                    
                    # Agregar tags y cards
                    nx_db.add_tag(reg_nexus.id, TagCreate(value="YouTube_Pipeline"))
                    for c in cards:
                        nx_db.create_card(CardCreate(
                            parent_id=reg_nexus.id,
                            question=c['question'],
                            answer=c['answer'],
                            type="DeepSeek_AI"
                        ))
                    
                    console.print(f"     [bold green]✅ Centralizado en Nexus ID {reg_nexus.id}[/bold green]")
                    
                    # 5. ELIMINACIÓN DEL HISTORIAL DE YOUTUBE (Gestión de Cola)
                    if yt_manager and v_item_id:
                        if yt_manager.remove_video_from_playlist(v_item_id):
                            console.print(f"     [bold blue]🗑️  Video eliminado de la playlist de YouTube (Cola despejada).[/bold blue]")
                        else:
                            console.print(f"     [yellow]⚠️ No se pudo eliminar de YouTube, pero el dato ya esta en Nexus.[/yellow]")

                except Exception as e:
                    console.print(f"     [bold red]❌ Error moviendo a Nexus: {e}[/bold red]")
            else:
                console.print(f"     [bold red]⚠️  Fallo ingesta de video {v_url}[/bold red]")
            
            # Pequeña pausa para mitigar bloqueos de IP (Rate Limiting)
            time.sleep(2)

        # Actualizar historial local
        history.append(p_url)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        
        console.print(f"[green]✓ Playlist {p_url} completada.[/green]")

    console.print("\n[bold green]🏁 Pipeline finalizado con exito.[/bold green]")

```

---

## Módulo — YouTube Manager
**Archivo**: `modules/youtube_manager.py`

```python

import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Permisos necesarios para gestionar playlists (Lectura y Escritura)
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

class YouTubeManager:
    """
    Gestor oficial de YouTube via Data API v3.
    Permite leer, listar y ELIMINAR videos de playlists (limpieza de cola).
    """
    def __init__(self, credentials_path='client_secrets.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.youtube = self._authenticate()

    def _authenticate(self):
        creds = None
        # El archivo token.pickle almacena los tokens de acceso y refresco del usuario
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales validas, pedir login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"No se encontro '{self.credentials_path}'. Necesitas descargar este archivo desde Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('youtube', 'v3', credentials=creds)

    def get_playlist_items(self, playlist_id):
        """Lista todos los videos (IDs y URLs) de una playlist."""
        videos = []
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            playlist_item_id = item['id'] # Necesario para eliminarlo luego
            title = item['snippet']['title']
            videos.append({
                'id': video_id,
                'playlist_item_id': playlist_item_id,
                'title': title,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            })
        return videos

    def remove_video_from_playlist(self, playlist_item_id):
        """Elimina un video de la playlist usando su ID de item (no el ID de video)."""
        try:
            self.youtube.playlistItems().delete(id=playlist_item_id).execute()
            return True
        except Exception as e:
            print(f"Error al eliminar video de la playlist: {e}")
            return False

    def get_playlist_id_from_url(self, url):
        """Extrae el ID de la playlist de una URL."""
        from urllib.parse import urlparse, parse_qs
        query = urlparse(url).query
        params = parse_qs(query)
        return params.get('list', [None])[0]

```

---

## Agente IA — Study
**Archivo**: `agents/study_agent.py`

```python
import os
import json
from typing import List

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[bold white on red]Librería 'google-genai' no encontrada. Verifica si se instaló correctamente.[/]")

from pydantic import TypeAdapter, BaseModel

from core.models import StudyCard
from core.database import Registry

from rich.prompt import Confirm
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

def get_client():
    """Obtiene el cliente estandarizado GenAI agarrando GOOGLE_API_KEY local."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

def generate_deck_from_registry(record: Registry, mockup_only: bool = False) -> List[StudyCard]:
    """
    Agente Pedagógico de Extracción.
    Genera tarjetas (StudyCard) mediante inteligencia artificial destilando el contenido de un solo registro.
    """
    if mockup_only:
        return [
            StudyCard(
                parent_id=record.id,
                question=f"¿Cuál es el tema principal de '{record.title}'?",
                answer=f"{record.title}",
                card_type="Conceptual"
            )
        ]

    client = get_client()
    if not client:
        # Mockup Inteligente (Heurístico) para cuando no hay API KEY
        cards = []
        # Tarjeta 1: Identificación y Tipo
        cards.append(StudyCard(
            parent_id=record.id,
            question=f"¿Cuál es el propósito o tema del registro '{record.title}' y qué tipo de recurso es?",
            answer=f"El tema es '{record.title}' y está clasificado como {record.type.upper()}.",
            card_type="Conceptual"
        ))
        
        # Tarjeta 2: Fragmento de contenido (si existe)
        if record.content_raw and len(record.content_raw.strip()) > 15:
            # Limpiar un poco el texto para la pregunta
            clean_text = record.content_raw.replace('\n', ' ').strip()
            cards.append(StudyCard(
                parent_id=record.id,
                question=f"Basado en la descripción de '{record.title}', completa el siguiente fragmento:\n\"{clean_text[:60]}...\"",
                answer=f"{clean_text[:120]}",
                card_type="Cloze"
            ))
            
        # Tarjeta 3: Referencia
        if record.path_url:
            cards.append(StudyCard(
                parent_id=record.id,
                question=f"¿Cuál es la ubicación física o enlace asociado al registro '{record.title}'?",
                answer=record.path_url,
                card_type="Factual"
            ))
            
        return cards

    # Definimos esquema simplificado para evitar errores de 'additionalProperties' en la API de Gemini
    class SimplifiedStudyCard(BaseModel):
        parent_id: int
        question: str
        answer: str
        card_type: str

    prompt = f"""
    Eres un profesor universitario de alto nivel, experto en pedagogía y Active Recall.
    Tu objetivo es leer el siguiente documento y extraer un mazo de Flashcards de ALTO RENDIMIENTO.

    --- Registro (ID: {record.id}) ---
    Título: {record.title}
    Info Cruda: {record.content_raw}
    Extra Metadatos: {record.meta_info}

    Reglas Mandatorias de Generación:
    1. NIVEL COGNITIVO: Mantén un nivel de complejidad Universitario Media-Alta. No hagas preguntas obvias; busca evaluar comprensión profunda y aplicación.
    2. PARAFRASEO: Nunca copies y pegues texto del documento. Reformula (parafrasea) las ideas para que el estudiante deba procesar el significado y no solo reconocer palabras.
    3. DIVERSIDAD DE FORMATOS: Utiliza una mezcla variada de los siguientes tipos en el campo 'card_type':
       - [Factual/Conceptual]: Preguntas directas o de desarrollo.
       - [Reversible]: Conceptos con definiciones claras.
       - [MCQ]: Opción múltiple (Almacena en 'question' como JSON: {{"prompt": "...", "options": {{"a": "...", "b": "..."}}}} y en 'answer' la letra).
       - [TF]: Verdadero o Falso. (Respuesta 'v' o 'f').
       - [Cloze]: Rellenar huecos usando la sintaxis: "La {{c1::palabra}} es {{c2::importante}}".
       - [Matching]: Emparejamiento (Almacenado como JSON de pares en 'question').
       - [MAQ]: Selección múltiple.
    4. CANTIDAD: Genera entre 3 y 7 tarjetas según la densidad de la información.
    5. REFERENCIA: Asigna 'parent_id' SIEMPRE a {record.id}.

    Retorna estrictamente un ARRAY de objetos JSON que sigan el esquema StudyCard proporcionado.
    """

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[SimplifiedStudyCard],
        temperature=0.3
    )

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash"
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            
            if response.text:
                json_data = json.loads(response.text)
                # Convertimos de SimplifiedStudyCard a StudyCard real
                final_cards = []
                for item in json_data:
                    final_cards.append(StudyCard(
                        parent_id=item['parent_id'],
                        question=item['question'],
                        answer=item['answer'],
                        card_type=item['card_type']
                    ))
                return final_cards
                
        except Exception as e:
            if model_name == models_to_try[-1]:
                print(f"[bold white on red]Error Fatal: Todos los modelos de Gemini fallaron. Último intento ({model_name}) dio el error: {e}[/]")
            continue

    return []

```

---

## Agente IA — Summary
**Archivo**: `agents/summary_agent.py`

```python

import os
import json
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

from core.database import Registry

load_dotenv()

def get_client():
    """Obtiene el cliente GenAI."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

def generate_summary_from_registry(record: Registry) -> Optional[str]:
    """
    Agente de Síntesis.
    Genera un resumen ejecutivo y estructurado de todas las ideas del registro.
    """
    client = get_client()

    if not client:
        return f"Resumen básico de '{record.title}': Este recurso de tipo {record.type} contiene información sobre {record.title}. (Instala GOOGLE_API_KEY para un resumen profesional)."

    prompt = f"""
    Eres un experto en síntesis de información y gestión del conocimiento (PKM).
    Tu objetivo es leer el siguiente documento y crear un RESUMEN EJECUTIVO DE ALTO NIVEL.

    --- Registro (ID: {record.id}) ---
    Título: {record.title}
    Contenido: {record.content_raw}
    Metadatos: {record.meta_info}

    Reglas del Resumen:
    1. ESTRUCTURA: Usa viñetas para los puntos clave.
    2. BREVEDAD: No más de 300 palabras.
    3. VALOR: Enfócate en las ideas más importantes y conclusiones "accionables".
    4. TONO: Profesional, claro y directo.

    Responde únicamente con el texto del resumen en formato Markdown. No añadidas introducciones como "Aquí está el resumen".
    """

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )
            
            if response.text:
                return response.text.strip()
                
        except Exception as e:
            continue

    return None

```

---

## Agente IA — Relationships
**Archivo**: `agents/relationship_agent.py`

```python
import os
import json
from typing import List

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[bold white on red]Librería 'google-genai' no encontrada. Verifica si se instaló correctamente.[/]")

from pydantic import TypeAdapter

from core.models import StudyCard
# Importamos la abstracción de SQLalchemy (Record) directamente, ya que el dashboard nos arroja un Registry.
from core.database import Registry

from rich import print
from rich.prompt import Confirm
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def get_client():
    """Obtiene el cliente estandarizado GenAI agarrando GOOGLE_API_KEY local."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

def generate_relationship_cards(record_a: Registry, record_b: Registry) -> List[StudyCard]:
    """
    Agente Pedagógico Match Forzado.
    Genera tarjetas (StudyCard) mediante inteligencia artificial centradas en la diferenciación 
    excluyente entre dos conceptos (Registro A vs Registro B).
    """
    client = get_client()

    prompt = f"""
    Eres un profesor de universidad riguroso diseñando material de estudio enfocado en la "Discriminación Cognitiva" (Match Forzado).
    Tu objetivo es leer un 'Registro A' y un 'Registro B', identificar la frontera, paradigma divergente o caso de uso distintivo entre ambos, y generar tarjetas de estudio de contraste rápido.

    --- Registro A (ID Ficticio o Real: {record_a.id}) ---
    Título: {record_a.title}
    Info Cruda: {record_a.content_raw}
    Extra Metadatos: {record_a.meta_info}

    --- Registro B (ID Ficticio o Real: {record_b.id}) ---
    Título: {record_b.title}
    Info Cruda: {record_b.content_raw}
    Extra Metadatos: {record_b.meta_info}

    Reglas de Diseño (IMPORTANTE):
    1. Preguntas de Identificación: Presenta una característica, ventaja o desventaja y pregunta a CUÁL de los dos conceptos pertenece. 
    2. Preguntas de Contraste: Pregunta por la diferencia radical entre A y B.
    3. Evita resúmenes genéricos "Concepto A es X, Concepto B es Y". 
    4. Usa "Relacional" o "Conceptual" estrictamente en el campo 'card_type'.
    5. Asigna el campo 'parent_id' EXACTAMENTE ya sea en {record_a.id} si la respuesta es principalmente sobre A, o {record_b.id} si defiende o se enfoca en B.

    Retorna únicamente el array con los objetos válidos que encajen exhaustivamente en este esquema.
    """

    # Forzar el output a un array estructurado (List[StudyCard]) via JSON
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[StudyCard],
        temperature=0.3
    )

    if not os.environ.get("GOOGLE_API_KEY"):
        # Mockup Funcional si no hay llave para evitar el Crash Masivo
        print("[yellow]\n[Mockup Mode] Simulación de IA en curso debido a ausencia de API KEY. Generando tarjeta de prueba...[/yellow]")
        return [
            StudyCard(
                parent_id=record_a.id,
                question=f"A diferencia del registro '{record_b.title}', ¿qué característica exclusiva tiene '{record_a.title}'?",
                answer=f"(Generado por MockIA) - El concepto A resalta por atributos no compartidos con B.",
                card_type="Relacional"
            )
        ]

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    for model_name in models_to_try:
        try:
            # print() desactivado aquí si queremos mantener la pureza en el dashboard
            # Pero podemos usar rich si es invocado directamente.
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            
            if response.text:
                json_data = json.loads(response.text)
                # Validar la salida de nuevo contra nuestro Core Pydantic para eliminar la posibilidad de disonancia
                adapter = TypeAdapter(List[StudyCard])
                cards = adapter.validate_python(json_data)
                return cards
                
        except Exception as e:
            # Silenciar error para intentar el próximo modelo silenciosamente como pidió el blueprint
            # pero imprimir la excepcion si es el ultimo modelo
            if model_name == models_to_try[-1]:
                print(f"[bold white on red]Error Fatal: Todos los modelos de Gemini fallaron. Último intento ({model_name}) dio el error: {e}[/]")
            continue

    return []

if __name__ == "__main__":
    pass

```

---

## Agente IA — DeepSeek
**Archivo**: `agents/deepseek_agent.py`

```python

import os
import json
from typing import List, Optional
from pydantic import BaseModel
from core.database import Registry, CardCreate

try:
    import requests
except ImportError:
    requests = None

from dotenv import load_dotenv

load_dotenv()

class DeepSeekCard(BaseModel):
    question: str
    answer: str

class DeepSeekAgent:
    """
    Agente especializado en usar DeepSeek para transformar transcripciones 
    en resúmenes concisos y flashcards.
    """
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com" # URL base oficial

    def process_content(self, title: str, content: str):
        """
        Genera un resumen y un conjunto de flashcards usando DeepSeek.
        """
        if not self.api_key:
            return None, []

        # No procesar si no hay contenido útil (evitar gasto de tokens en errores)
        if "Transcripción Disponible" in content or "Error al raspar" in content or len(content) < 100:
            return f"Sin resumen: No hay suficiente contenido base para analizar '{title}'.", []

        prompt = f"""
        Analiza el siguiente contenido extraído de un video de YouTube titulado "{title}".
        
        1. Genera un RESUMEN EJECUTIVO de no más de 3 párrafos.
        2. Genera 5 Flashcards de estudio en formato JSON exacto:
           [{{"question": "...", "answer": "..."}}, ...]

        Contenido:
        {content[:15000]} # Limitamos para evitar contexto excesivo en V1
        
        Responde estrictamente en este formato:
        RESUMEN: [Tu resumen aquí]
        FLASHCARDS: [Tu JSON de flashcards aquí]
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            full_text = result['choices'][0]['message']['content']
            
            # Parsing más robusto
            resumen = ""
            cards_json = []
            
            # Intentar extraer el resumen
            if "RESUMEN:" in full_text:
                if "FLASHCARDS:" in full_text:
                    resumen = full_text.split("RESUMEN:")[1].split("FLASHCARDS:")[0].strip()
                else:
                    resumen = full_text.split("RESUMEN:")[1].strip()
            
            # Intentar extraer las flashcards (JSON)
            if "FLASHCARDS:" in full_text:
                json_part = full_text.split("FLASHCARDS:")[1].strip()
                # Limpiar bloques de código markdown si existen
                if "```json" in json_part:
                    json_part = json_part.split("```json")[1].split("```")[0].strip()
                elif "```" in json_part:
                    json_part = json_part.split("```")[1].split("```")[0].strip()
                
                try:
                    cards_json = json.loads(json_part)
                except Exception as je:
                    print(f"[yellow]Error parseando JSON de DeepSeek: {je}[/yellow]")
                    # Intento desesperado: buscar el primer '[' y el último ']'
                    import re
                    match = re.search(r'\[\s*\{.*\}\s*\]', json_part, re.DOTALL)
                    if match:
                        try:
                            cards_json = json.loads(match.group())
                        except:
                            pass
            
            return resumen, cards_json
            
        except Exception as e:
            print(f"[red]Error en DeepSeek API: {e}[/]")
            return None, []

deepseek_agent = DeepSeekAgent()

```

---

## Agente IA — Mutation
**Archivo**: `agents/mutation_agent.py`

```python
import json
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from core.database import nx_db, Card
from rich.console import Console
from rich.panel import Panel

console = Console()

class MutatedCard(BaseModel):
    id: int = Field(description="El ID original de la tarjeta a modificar.")
    question: str = Field(description="La nueva pregunta reformulada o en nuevo formato (JSON si es MCQ/Matching).")
    answer: str = Field(description="La nueva respuesta adaptada.")
    card_type: str = Field(description="El nuevo tipo de tarjeta (Factual, Conceptual, MCQ, TF, Cloze, Matching, MAQ).")

class MutatedDeck(BaseModel):
    cards: list[MutatedCard] = Field(description="Lista de tarjetas reformuladas.")

# Agente mutador. Utilizamos gemini-2.0-flash como modelo estándar (más rápido para mutaciones).
mutator_agent = Agent(
    'google-gla:gemini-2.0-flash',
    result_type=MutatedDeck,
    system_prompt='''Eres el Ingeneiro de Mutación Cognitiva de Nexus.
Tu objetivo es destruir la memorización por habituación (cuando el estudiante reconoce la forma de la pregunta pero no el fondo).

RECIBIRÁS: Un listado de tarjetas que el usuario ha repasado.

TU TAREA:
1. PARAFRASEO RADICAL: Reescribe la pregunta y respuesta desde cero. Mantén el significado pero usa sinónimos y estructuras diferentes.
2. NIVEL UNIVERSITARIO: Asegura que la complejidad sea Media-Alta.
3. TRANSFORMACIÓN DE FORMATO: Cambia el tipo de la tarjeta original a uno nuevo si es posible.
   Tipos permitidos en 'card_type':
   - [Factual/Conceptual]: Preguntas directas.
   - [MCQ]: Opción múltiple (Pregunta como JSON: {"prompt": "...", "options": {"a": "...", "b": "..."}}).
   - [TF]: Verdadero/Falso (Respuesta 'v' o 'f').
   - [Cloze]: Rellenar huecos (Sintaxis: "La {{c1::palabra}} es...").
   - [Matching]: Emparejamiento (JSON de pares en question).
   - [MAQ]: Selección múltiple.
4. INTEGRIDAD: No inventes información. La respuesta debe seguir siendo válida según el conocimiento original.
'''
)

def mutate_cards(card_ids: list[int]):
    """
    Toma una lista de IDs de tarjetas, consulta su texto original,
    los envía a Gemini para que los re-formule en memoria, y actualiza la Base de Datos.
    """
    if not card_ids:
        return
        
    console.print(f"\n[bold magenta]🧠 Agente Mutador Iniciado...[/]")
    console.print(f"[dim]Analizando {len(card_ids)} tarjetas difíciles para reescribirlas y romper tu adaptación estática...[/dim]")
    
    with nx_db.Session() as session:
        cards_to_mutate = session.query(Card).filter(Card.id.in_(card_ids)).all()
        
        if not cards_to_mutate:
            return
            
        # Preparar el payload
        prompt_content = "Tarjetas a reformular:\n\n"
        for c in cards_to_mutate:
            prompt_content += f"--- TARJETA ID {c.id} ---\nPregunta Original: {c.question}\nRespuesta Original: {c.answer}\n\n"
            
        console.print("[dim]Conectándose a Gemini AI para reformulación cognitiva...[/dim]")
        
        try:
            result = mutator_agent.run_sync(prompt_content)
            mutated_deck = result.data
            
            # Sobreescribir las tarjetas
            mutades_count = 0
            for mut_card in mutated_deck.cards:
                local_card = session.query(Card).get(mut_card.id)
                if local_card:
                    # Registramos el éxito
                    local_card.question = mut_card.question
                    local_card.answer = mut_card.answer
                    local_card.type = mut_card.card_type
                    mutades_count += 1
            
            session.commit()
            console.print(Panel(f"[bold green]¡Mutación Completada![/]\nSe han reformulado {mutades_count} Flashcards.\nMañana te sorprenderán con ángulos totalmente nuevos.", title="🧬 Mutación de Aprendizaje", border_style="green"))
            
        except Exception as e:
            console.print(f"\n[bold white on red]Error al contactar con la IA para la mutación: {e}[/]")

```

---

## Web Server — FastAPI
**Archivo**: `web_server.py`

```python

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

```

---

## Entry Point
**Archivo**: `main.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Punto de Entrada Oficial para Nexus
"""

import sys
import os

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH para las importaciones relativas.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ui.dashboard import main_loop
from core.database import init_db

if __name__ == "__main__":
    # Asegurar que la base de datos y sus tablas estén creadas antes de arrancar.
    init_db()
    
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nSaliendo de Nexus desde main.py...")
        sys.exit(0)

```

---

## Dashboard TUI
**Archivo**: `ui/dashboard.py`

> Archivo principal (1818 líneas, 101,571 bytes) — secciones clave

### Imports y Setup (L1-80)
```python
import sys
import time

# Forzar salida en UTF-8 para evitar errores de renderizado de Emojis en la terminal de Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.align import Align
from rich import box
from rich.text import Text
from rich.theme import Theme

# Tema personalizado de ALTO CONTRASTE para visibilidad total en terminales azules/oscuras
custom_theme = Theme({
    "dim": "bright_white",
    "cyan": "bright_cyan",
    "magenta": "yellow",
    "blue": "bright_blue",
    "prompt.choices": "bold yellow",
    "prompt.default": "bold bright_white",
    "prompt.invalid": "bold red",
    "prompt.invalid.choice": "bold white on red",
})

console = Console(theme=custom_theme)

import os
import subprocess
import msvcrt

def get_key() -> str:
    """Captura un solo carácter del teclado sin esperar a Enter (Solo Windows).
    Retorna 'left' / 'right' para teclas de flecha, o el carácter en minúsculas.
    """
    if sys.platform == "win32":
        try:
            char = msvcrt.getch()
            # Secuencias de escape: flechas devuelven 0x00 o 0xE0 + código
            if char in [b'\x00', b'\xe0']:
                ext = msvcrt.getch()
                if ext == b'K': return "left"   # Flecha izquierda
                if ext == b'M': return "right"  # Flecha derecha
                if ext == b'H': return "up"     # Flecha arriba
                if ext == b'P': return "down"   # Flecha abajo
                return ""  # Otro código especial ignorado
            return char.decode('utf-8').lower()
        except Exception:
            return ""
    return ""

from modules.file_manager import ingest_local_file
from modules.web_scraper import ingest_web_resource
from modules.pkm_manager import create_note
from core.search_engine import search_registry, parse_query_string
from core.database import SessionLocal, nx_db, CardCreate, NexusLinkCreate
from agents.relationship_agent import generate_relationship_cards
from modules.study_engine import start_pomodoro_session, open_source_material
from modules.analytics import get_global_metrics
from modules.exporter import export_to_google_drive
from core.staging_db import staging_db, STAGING_DB_PATH
from modules.pipeline_manager import run_youtube_pipeline

import logging

logging.basicConfig(
    filename="nexus.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexus.ui")


class ReturnToMain(Exception):
    """Señal de navegación para volver al menú principal desde cualquier profundidad."""
    pass

```

### menu_agregar con fixes (L128-400)
```python
def menu_agregar():
    """
    [1] AGREGAR ARCHIVOS A LA BD
    Captura y almacena nuevo contenido en la base de datos.
    """
    current_target = "local"
    
    while True:
        console.clear()
        show_header()
        
        target_color = "green" if current_target == "local" else "bold white on gold3"
        target_name = "CORE (Local SSD)" if current_target == "local" else f"BUFFER (Nube G: {STAGING_DB_PATH})"
        
        # Resumen de filtros permanentes en el header
        console.print(Align.center(get_stats_panel()))
        console.print()
        console.print(Panel(
            f"[bold yellow]📂 AGREGAR ARCHIVOS A LA BD[/]\n"
            f"Destino Actual: [{target_color}]{target_name}[/]\n\n"
            f"Selecciona el tipo de recurso a indexar:", 
            box=box.ROUNDED,
            title="[bold bright_cyan]Componente 1[/]"
        ))
        
        console.print("  [bold bright_cyan][1][/] 📄 Añadir Archivo Local [dim](manual / Lote desde archivo .txt)[/]")
        console.print("  [bold bright_cyan][2][/] 🌐 Añadir URL (Web/YouTube) [dim](manual / Lote de URLs)[/]")
        console.print("  [bold bright_cyan][3][/] 📝 Escribir Nota Libre [dim](abre editor externo)[/]")
        console.print("  [bold bright_cyan][4][/] ⚙️  Añadir Aplicación / Herramienta")
        console.print("  [bold bright_cyan][6][/] 🤖 Pipeline Automatizado (YouTube) [dim](playlists, descarga, resumen, flashcards)[/]")
        console.print(f"  [bold yellow][S][/] Cambiar Destino → {'Buffer G:' if current_target=='local' else 'Nexus Core'}")
        console.print("  [bold white][0][/] 🔙 Volver al Menú Principal\n")

        opcion = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4", "6", "s", "S"], show_choices=False, console=console).lower()

        if opcion == "0":
            break
            
        if opcion == "s":
            if current_target == "local":
                if staging_db.init_staging():
                    current_target = "staging"
                    console.print("[bold yellow]🚀 ¡Modo STAGING Activado! Los datos irán a la unidad G:[/]")
                else:
                    console.print("[bold red]Error: No se puede activar Staging. ¿Está el drive G: montado?[/]")
            else:
                current_target = "local"
                console.print("[bold green]Modo CORE Local reactivado.[/]")
            time.sleep(1.2)
            continue

        db_active = nx_db if current_target == "local" else staging_db

        if opcion == "1":
            while True:
                ruta = Prompt.ask("\n[bold]Ruta absoluta del archivo[/bold]", console=console)
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                # Note: Local files always go to Local Core for now as path references are local
                try:
                    resultado = ingest_local_file(ruta, tags_list)
                except Exception as e:
                    console.print(f"\n[bold red]❌ Error de ingestión:[/] {e}")
                    logger.exception("Fallo en ingest_local_file")
                    resultado = None
                if resultado is not None:
                    console.print(f"\n[bold green]✅ Archivo indexado correctamente:[/] {resultado.title}")
                    
                    summary_text = Text()
                    summary_text.append(f"ID: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.id}\n", style="white")
                    summary_text.append(f"Tipo: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.type}\n", style="white")
                    summary_text.append(f"Título: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.title}\n", style="white")
                    summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                    summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                    
                    if resultado.content_raw:
                        content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                        summary_text.append(f"Vista Previa del Contenido:\n", style="bold green")
                        summary_text.append(content_preview, style="white")
                    else:
                        summary_text.append(f"Contenido: ", style="bold green")
                        summary_text.append("No se pudo extraer texto (Archivo binario o ilegible).", style="white italic")

                    console.print(Panel(summary_text, title="Detalles del Archivo", border_style="green"))
                    
                    if Prompt.ask("\n¿Deseas editar o ver los detalles completos de este registro ahora? (s/n)", choices=["s", "n"], default="n") == 's':
                        _show_record_detail(resultado.id)
                else:
                    console.print("\n[bold white on red]❌ No se pudo indexar. Verifica la ruta o los permisos.[/]")
                    
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRO archivo local | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False, console=console)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == "2":
            while True:
                url = Prompt.ask("\n[bold]Pega la URL (YouTube o Genérica)[/bold]", console=console)
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                console.print(f"\n[bright_cyan]Iniciando raspado contextual y transcripción hacia {current_target.upper()}...[/]")
                try:
                    with console.status("[bright_white]Descargando Súper Schema de Web, por favor espera...[/bright_white]", spinner="dots"):
                         resultado = ingest_web_resource(url, tags_list, db_target=db_active)
                except Exception as e:
                    console.print(f"\n[bold red]❌ Error de ingestión web:[/] {e}")
                    logger.exception("Fallo en ingest_web_resource")
                    resultado = None
                     
                if resultado is not None:
                     console.print(f"\n[bold green]✅ Recurso Web indexado exitosamente en la Knowledge Base.[/bold green]")
                     
                     # Mostrar lo descargado al usuario
                     summary_text = Text()
                     summary_text.append(f"ID: ", style="bold bright_cyan")
                     summary_text.append(f"{resultado.id}\n", style="white")
                     summary_text.append(f"Tipo: ", style="bold bright_cyan")
                     summary_text.append(f"{resultado.type}\n", style="white")
                     summary_text.append(f"Título: ", style="bold bright_cyan")
                     summary_text.append(f"{resultado.title}\n", style="white")
                     summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                     summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                     
                     if resultado.content_raw:
                         content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                         summary_text.append(f"Contenido Extraído:\n", style="bold green")
                         summary_text.append(content_preview, style="white")
                     else:
                         summary_text.append("Contenido: ", style="bold green")
                         summary_text.append("No se pudo extraer contenido de esta URL.", style="white italic")
                     
                     console.print(Panel(summary_text, title="Detalles de Ingesta", border_style="green"))
                     
                     if Prompt.ask("\n¿Deseas editar o ver los detalles completos de este registro ahora? (s/n)", choices=["s", "n"], default="n", console=console) == 's':
                         _show_record_detail(resultado.id)

                else:
                     console.print("\n[bold white on red]❌ Hubo un fallo en la ingesta o no se pudo generar el texto principal de la URL.[/]")
                     
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRA URL | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False, console=console)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == "3":
            while True:
                titulo = Prompt.ask("\n[bold]Título de la Nueva Nota[/bold]", console=console)
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                console.print("\n[bright_white]Abriendo el sistema nativo. Al cerrar la ventana, tu nota se guardará automáticamente...[/bright_white]")
                
                try:
                    resultado = create_note(titulo, tags_list)
                except Exception as e:
                    console.print(f"\n[bold red]❌ Error al crear nota:[/] {e}")
                    logger.exception("Fallo en create_note")
                    resultado = None
                if resultado is not None:
                    console.print(f"\n[bold green]✅ Nota \"{resultado.title}\" almacenada en Knowledge Base.[/bold green]")
                    
                    summary_text = Text()
                    summary_text.append(f"ID: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.id}\n", style="white")
                    summary_text.append(f"Tipo: ", style="bold bright_cyan")
                    summary_text.append(f"nota_libre\n", style="white") # create_note returns a Registry object usually, check it
                    summary_text.append(f"Título: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.title}\n", style="white")
                    summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                    summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                    
                    if resultado.content_raw:
                        content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                        summary_text.append(f"Contenido de la Nota:\n", style="bold green")
                        summary_text.append(content_preview, style="white")
                    else:
                        summary_text.append("Nota: ", style="bold green")
                        summary_text.append("Sin contenido capturado.", style="white italic")
                    
                    console.print(Panel(summary_text, title="Detalles de la Nota", border_style="green"))
                    
                    if Prompt.ask("\n¿Deseas editar o ver los detalles completos de esta nota ahora? (s/n)", choices=["s", "n"], default="n") == 's':
                        _show_record_detail(resultado.id)
                else:
                    console.print("\n[yellow]⚠️ Nota cancelada. No se guardó nada.[/yellow]")
                    
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Escribir OTRA nota | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == "6":
            # 1.6 Pipeline Automatizado (YouTube)
            console.print("\n[bold bright_cyan]Iniciando Pipeline Automatizado de YouTube...[/]")
            try:
                with console.status("[white]Procesando playlists en cola...[/white]", spinner="dots"):
                    run_youtube_pipeline()
            except Exception as e:
                console.print(f"\n[bold red]❌ Error en pipeline YouTube:[/] {e}")
                logger.exception("Fallo en run_youtube_pipeline")
            Prompt.ask("\n[bold]Pipeline finalizado. Enter para continuar...[/bold]", console=console)


        elif opcion == "4":
            while True:
                console.print("\n[bold yellow]Añadir Aplicación o Herramienta[/]")
                titulo = Prompt.ask("\n[bold]Nombre de la App / Plataforma[/bold]", console=console)
                ruta = Prompt.ask("[bold]Ruta / URL o Comando de Ejecución[/bold]", console=console)
                
                # Nuevos campos solicitados por Arquitecto:
                plataforma_input = Prompt.ask("[bold]Plataforma[/] (ej. PC, Android, Web)", default="PC", console=console)
                logueo = Prompt.ask("[bold]¿Requiere Credenciales / Logueo?[/] (s/n)", default="n", console=console).lower() == 's'
                logueo_str = "Sí" if logueo else "No"
                descripcion = Prompt.ask("[bold]Breve Descripción o Uso Principal[/] (opcional)", console=console)
                
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                try:
                    from core.database import RegistryCreate, TagCreate
                    
                    # Construir bloque de texto para Active Recall 
                    content_blob = (
                        f"Herramienta o Aplicación: {titulo}\n"
                        f"Plataforma: {plataforma_input.strip()}\n"
                        f"Requiere Logueo: {logueo_str}\n"
                        f"Ruta o Comando: {ruta}\n"
                    )
                    if descripcion:
                        content_blob += f"Descripción: {descripcion.strip()}\n"

                    data = RegistryCreate(
                        type="app",
                        title=titulo,
                        path_url=ruta,
                        content_raw=content_blob,
                        meta_info={
                            "platform_type": plataforma_input.strip(),
                            "requires_login": logueo,
                            "app_description": descripcion.strip() if descripcion else ""
                        }
                    )
                    reg = nx_db.create_registry(data)
                    for t in tags_list:
                        nx_db.add_tag(reg.id, TagCreate(value=t))
                    console.print(f"\n[bold green]✅ Aplicación '{titulo}' (ID {reg.id}) registrada correctamente en la base de datos.[/bold green]")
                except Exception as e:
                    console.print(f"\n[bold white on red]❌ Error al guardar la aplicación: {str(e)}[/]")

                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Añadir OTRA Aplicación | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return

# Alias de compatibilidad (por si algún módulo importa el nombre antiguo)
def menu_ingreso():
```

### main_loop (L1746-fin)
```python
def main_loop():
    """Bucle infinito del Dashboard Principal — Arquitectura de 5 Componentes."""
    while True:
        console.clear()
        show_header()
        
        console.print(Align.center(get_stats_panel()))
        console.print()
        
        # Menú Principal — grid 5 componentes
        grid = Table.grid(expand=True, padding=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)

        grid.add_row(
            Panel("[bold bright_cyan][1] ➕ AGREGAR[/]\n[white]Archivos a la BD", border_style="bright_cyan", title="Captura"),
            Panel("[bold yellow][2] 🗂️ GESTIONAR[/]\n[bold bright_white]Explorar, Editar, Vincular", border_style="yellow", title="Mente"),
            Panel("[bold white on red][3] 🧠 RECALL[/]\n[bold yellow]Sesión Pomodoro SRS", border_style="red", title="Entreno")
        )
        grid.add_row(
            Panel("[bold green][4] 📊 ESTADÍSTICAS[/]\n[white]Métricas + Exportar", border_style="green", title="Análisis"),
            Panel("[bold white][5] ❌ SALIR[/]\n[white]Cerrar Nexus", border_style="white", title="Nexus"),
            Panel("[bold bright_white]🔍 OMNIBAR[/]\n[white]Escribe cualquier término para buscar", border_style="bright_white", title="Búsqueda"),
        )

        console.print(grid)
        
        help_content = (
            "[bold bright_cyan]1[/] Agregar │ [bold yellow]2[/] Gestionar │ [bold white on red]3[/] Recall │ "
            "[bold green]4[/] Estadísticas │ [bold white]5[/] Salir\n"
            "[bold white]Gestor:[/][yellow] ←/→ Págs │ Q Filtrar │ L Limpiar │ [ID] Ver detalle │ del [IDs] Borrar │ m/ia ID1 ID2 Vincular[/yellow]"
        )
        console.print(Panel(help_content, title="[white]COMANDOS RÁPIDOS[/]", border_style="white", padding=(0, 1)))
        console.print()

        user_input = Prompt.ask("[bold bright_cyan]Nexus ▶[/]", console=console).strip()

        try:
            if user_input == "1":
                menu_agregar()
            elif user_input == "2":
                menu_gestionar()
            elif user_input == "3":
                menu_active_recall()
            elif user_input == "4":
                menu_estadisticas()
            elif user_input in ["5", "0"] or user_input.lower() in ["q", "exit", "quit"]:
                console.print("\n[bold bright_cyan]Cerrando módulos de Nexus... ¡Hasta pronto![/]")
                time.sleep(1)
                sys.exit(0)
            elif user_input:
                if user_input.startswith(":"):
                    console.print(f"[yellow]Comando desconocido: {user_input}[/]")
                    time.sleep(1)
                    continue
                console.print(f"\n[bright_cyan]🔍 Omnibar: Saltando al Gestor con '[bold]{user_input}[/]'...[/]")
                time.sleep(0.5)
                menu_gestionar(initial_query=user_input)
        except ReturnToMain:
            continue
        except Exception as e:
            console.print(f"\n[bold red]❌ Error crítico en módulo:[/] {e}")
            logger.exception("Error en main_loop")
            Prompt.ask("[white]Enter para continuar...[/]")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold white on red]Interrupción detectada. Saliendo de Nexus...[/]")
        sys.exit(0)

```

