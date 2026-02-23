from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

# Definición de tipos permitidos para el registro
ResourceType = Literal['file', 'youtube', 'note', 'concept', 'app', 'account']

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
    metadata_dict: Dict[str, Any] = Field(default_factory=dict, description="Metadatos en formato JSON")
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
