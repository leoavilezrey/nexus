from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from cloud_backend.database import get_db
from cloud_backend.auth.jwt import verify_token
# Imports de funcionalidad de Búsqueda movidos al Root de la jerarquía modular
from core.search_engine import parse_query_string, search_registry
from core.models import ResourceRecord
from core.database import Registry, Tag

router = APIRouter(tags=["data"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Pydantic Schemas base para el backend Web

class RecordCreateWeb(BaseModel):
    title: str
    description: str | None = None
    type: str # nota, web, youtube
    content_raw: str | None = None
    is_flashcard_source: bool = False
    tags: list[str] = []

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o ha expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

@router.get("/records/")
def list_records(
    q: str = "",
    limit: int = 50,
    offset: int = 0,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista iterativa con soporte transparente a prefijos h: e: t: o:vdesc, etc.
    """
    filters = parse_query_string(q)
    return search_registry(db, **filters, limit=limit, offset=offset)

@router.post("/records/")
def create_record(
    data: RecordCreateWeb,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creación estricta en la nube. Aisla rutas locales, prohibe 'file'
    """
    if data.type.lower() == 'file':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo 'file' no está soportado en la nube para mantener aislamiento del disco local."
        )

    # Validaciones Anti-Windows Paths inyectados
    if data.content_raw and (data.content_raw.startswith("C:\\") or data.content_raw.startswith("D:\\")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
             detail="Rutas locales de sistema operativo rechazadas en Cloud Backend."
        )

    new_reg = Registry(
        title=data.title,
        description=data.description,
        type=data.type,
        content_raw=data.content_raw,
        is_flashcard_source=data.is_flashcard_source,
    )
    db.add(new_reg)
    db.flush()

    # Manejar las etiquetas limpias
    for tag_name in data.tags:
        clean_tag = tag_name.lower().strip()
        if clean_tag:
             db.add(Tag(registry_id=new_reg.id, name=clean_tag))

    db.commit()
    db.refresh(new_reg)
    return {"message": "Registro subido a la nube correctamente", "id": new_reg.id}
