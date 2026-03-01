# NEXUS — Código Fuente Completo (Snapshot 2026-02-28)

> Generado automáticamente. Incluye los 18 archivos fuente del proyecto.

---

## Índice

| # | Archivo | Líneas | Propósito |
|---|---|:---:|---|
| 1 | `main.py` | 28 | Punto de entrada |
| 2 | `core/database.py` | 268 | ORM, modelos, CRUD |
| 3 | `core/models.py` | 48 | Schemas Pydantic |
| 4 | `core/search_engine.py` | 255 | Motor de búsqueda |
| 5 | `core/staging_db.py` | 67 | Buffer Google Drive |
| 6 | `ui/dashboard.py` | 1811 | Dashboard TUI principal |
| 7 | `modules/analytics.py` | 65 | Métricas globales |
| 8 | `modules/file_manager.py` | 96 | Ingesta archivos locales |
| 9 | `modules/web_scraper.py` | 253 | Ingesta web/YouTube |
| 10 | `modules/pkm_manager.py` | 90 | Creación de notas |
| 11 | `modules/exporter.py` | 60 | Export a Google Drive |
| 12 | `modules/study_engine.py` | 444 | Motor SRS/Pomodoro |
| 13 | `modules/pipeline_manager.py` | 147 | Pipeline YouTube auto |
| 14 | `modules/youtube_manager.py` | 81 | YouTube API manager |
| 15 | `agents/study_agent.py` | 148 | Agente Flashcards IA |
| 16 | `agents/summary_agent.py` | 70 | Agente Resúmenes IA |
| 17 | `agents/relationship_agent.py` | 114 | Agente Relaciones IA |
| 18 | `agents/deepseek_agent.py` | 113 | Agente DeepSeek |
| 19 | `agents/mutation_agent.py` | 87 | Agente Mutador |
| 20 | `web_server.py` | 215 | API FastAPI |

**Total: ~4,510 líneas de código**

---

## 1. main.py

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

## 2. core/database.py

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

## 3. core/models.py

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

## 4. core/search_engine.py

> **255 líneas** — Motor maestro de búsqueda. Soporta filtros por nombre, tags, extensiones, IDs, fuente flashcard, con paginación. Incluye `parse_query_string()` para queries inteligentes.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\core\search_engine.py`)*

---

## 5. core/staging_db.py

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
        except Exception:
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
    """Hereda de NexusCRUD pero apunta a la sesion del buffer en G:"""
    def __init__(self):
        self.Session = StagingSessionLocal

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

## 6. ui/dashboard.py

> **1,811 líneas** — Dashboard TUI completo con Rich. Contiene:
> - `show_header()`, `get_stats_panel()` — Componentes visuales
> - `menu_agregar()` — Agregar archivos/URLs/notas/apps/pipeline
> - `menu_gestionar()` — Explorador maestro con paginación, filtros, borrado, vinculación
> - `_show_record_detail()` — Vista detallada con sub-menús (editar, abrir, lectura, IA, mazo, borrar, vínculo, recall)
> - `menu_adelantar_repaso()` — Repaso adelantado con filtros
> - `menu_active_recall()` — Motor Pomodoro SRS con explorador de fuentes
> - `menu_conectar()` — Cockpit de enlaces/vinculación neuronal
> - `menu_estadisticas()` — Métricas + exportación Google Drive
> - `main_loop()` — Bucle principal con Omnibar

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\ui\dashboard.py`)*

---

## 7. modules/analytics.py

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

## 8. modules/file_manager.py

> **96 líneas** — Ingesta de archivos locales: valida existencia, extrae metadatos, lee texto plano (5KB max), inserta en BD con tags.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\modules\file_manager.py`)*

---

## 9. modules/web_scraper.py

> **253 líneas** — Ingesta web: detecta YouTube vs web genérica, extrae transcripciones (youtube_transcript_api), metadatos (yt-dlp), HTML text (BeautifulSoup). Soporta batch ingest y playlists.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\modules\web_scraper.py`)*

---

## 10. modules/pkm_manager.py

> **90 líneas** — Creación de notas: abre notepad bloqueante, lee contenido al cerrar, guarda en BD con ruta lógica `nexus://note/`.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\modules\pkm_manager.py`)*

---

## 11. modules/exporter.py

> **60 líneas** — Exportación a Google Drive (G:): copia física de nexus.db + genera CSV con todos los registros.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\modules\exporter.py`)*

---

## 12. modules/study_engine.py

> **444 líneas** — Motor SRS completo:
> - `SRSEngine.calculate_next_review()` — Algoritmo FSRS/SM-2 con penalización por tiempo
> - `open_source_material()` — Abre web/archivos/notas
> - `get_due_cards()` — Consulta cards pendientes con filtros
> - `start_pomodoro_session()` — Sesión interactiva con renderizado por tipo (MCQ, TF, Cloze, Matching, Factual), edición, eliminación, calificación, y mutador IA

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\modules\study_engine.py`)*

---

## 13. modules/pipeline_manager.py

> **147 líneas** — Pipeline automatizado YouTube: descarga playlist → staging → DeepSeek → Nexus local → elimina de YouTube.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\modules\pipeline_manager.py`)*

---

## 14. modules/youtube_manager.py

> **81 líneas** — YouTube Data API v3: autenticación OAuth, listar/eliminar videos de playlists.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\modules\youtube_manager.py`)*

---

## 15. agents/study_agent.py

> **148 líneas** — Agente pedagógico de extracción: genera flashcards vía Gemini (con fallback mockup inteligente sin API key). Soporta múltiples modelos con retry.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\agents\study_agent.py`)*

---

## 16. agents/summary_agent.py

> **70 líneas** — Agente de síntesis: genera resúmenes ejecutivos vía Gemini con fallback básico.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\agents\summary_agent.py`)*

---

## 17. agents/relationship_agent.py

> **114 líneas** — Agente de Match Forzado: genera flashcards de discriminación cognitiva entre dos registros vía Gemini.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\agents\relationship_agent.py`)*

---

## 18. agents/deepseek_agent.py

> **113 líneas** — Agente DeepSeek: genera resúmenes y flashcards desde transcripciones de YouTube vía DeepSeek API.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\agents\deepseek_agent.py`)*

---

## 19. agents/mutation_agent.py

> **87 líneas** — Agente Mutador: reformula flashcards repasadas para romper habituación cognitiva usando Gemini + pydantic-ai.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\agents\mutation_agent.py`)*

---

## 20. web_server.py

> **215 líneas** — API REST FastAPI con endpoints: `/api/records`, `/api/stats`, `/api/recall/cards`, `/api/pipeline/status`, `/api/ingest`, más UI estática.

*(Archivo completo disponible en: `c:\Users\DELL\Proyectos\nexus\web_server.py`)*

---

## Dependencias (requirements.txt)

```
aiohappyeyeballs==2.6.1
aiohttp==3.13.3
aiosignal==1.4.0
annotated-types==0.7.0
anyio==4.12.1
attrs==25.4.0
certifi==2026.1.4
cffi==2.0.0
charset-normalizer==3.4.4
cryptography==46.0.5
distro==1.9.0
frozenlist==1.8.0
google-auth==2.48.0
google-genai==1.64.0
greenlet==3.3.2
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
markdown-it-py==4.0.0
mdurl==0.1.2
multidict==6.7.1
propcache==0.4.1
pyasn1==0.6.2
pyasn1_modules==0.4.2
pycparser==3.0
pydantic==2.12.5
pydantic_core==2.41.5
Pygments==2.19.2
requests==2.32.5
rich==14.3.3
rsa==4.9.1
sniffio==1.3.1
SQLAlchemy==2.0.46
tenacity==9.1.4
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.6.3
websockets==15.0.1
yarl==1.22.0
python-dotenv
```

---

## Bugs Detectados (ver análisis completo en `docs/` y `logs/cold_run_diagnostic.log`)

| # | Severidad | Archivo | Línea | Descripción |
|---|---|---|:---:|---|
| 1 | 🔴 CRÍTICO | `ui/dashboard.py` | 353 | `from core.database import ..., nx_db, ...` dentro de `menu_agregar()` sombrea import global → `UnboundLocalError` en L179 |
| 2 | 🟠 MEDIO | `ui/dashboard.py` | 259, 306 | `content_raw[:800]` sin verificar `None` → posible `TypeError` |
| 3 | 🟡 BAJO | `ui/dashboard.py` | 51 | `bare except:` captura `KeyboardInterrupt`/`SystemExit` |
| 4 | 🟡 BAJO | `modules/file_manager.py` | varias | `print()` con tags Rich que no se renderizan |
| 5 | 🟡 BAJO | `modules/pkm_manager.py` | varias | `print()` con tags Rich que no se renderizan |
