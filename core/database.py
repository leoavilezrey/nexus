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
    type = Column(String, nullable=False) # file, youtube, note, concept, app, account
    title = Column(Text, nullable=True)
    path_url = Column(Text, nullable=True)
    content_raw = Column(Text, nullable=True)
    
    # Python atributo será 'meta_info', pero en la base de datos se llama 'metadata'
    # Esto previene choques con 'Base.metadata'
    meta_info = Column('metadata', JSON, nullable=True)
    
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

    type: str = Field(..., description="file, youtube, note, concept, app, account")
    title: Optional[str] = None
    path_url: Optional[str] = None
    content_raw: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None

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

# Exportamos la instancia para su uso global si así se requiere
nx_db = NexusCRUD()

if __name__ == "__main__":
    init_db()
