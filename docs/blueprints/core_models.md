# Blueprint: Modelos de Datos Maestro (Pydantic)
Ubicación sugerida: `nexus/core/models.py`

Este archivo asegurará que el Constructor use un tipado estricto, evitando que el sistema falle por datos mal formados.

## 1. ResourceRecord
Espejo de la tabla 'registry'.
- id: Optional[int]
- type: str (Enum: file, youtube, note, concept, app, account)
- title: str
- path_url: str
- content_raw: Optional[str] = None
- metadata_dict: dict = Field(default_factory=dict)
- created_at: datetime
- modified_at: datetime

## 2. NexusLink
- source_id: int
- target_id: int
- relation_type: str
- description: str

## 3. StudyCard
- id: Optional[int]
- parent_id: int
- question: str
- answer: str
- card_type: str
- srs_data: dict (Para dificultad, estabilidad, etc.)

## Instrucción para el Constructor:
Instalar 'pydantic' en el venv y crear el archivo 'core/models.py'. Estos modelos deben usarse en el CRUD de la base de datos para validar los registros.
