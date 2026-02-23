# Blueprint: Motor de Búsqueda (Search Engine)
Ubicación sugerida: `nexus/core/search.py`

El motor de búsqueda maestror será la única forma de consultar la base de datos `registry`.
Debe soportar inclusión y exclusión por diseño, y paginación.

## Funciones Core a implementar:

### 1. `search_registry`
Firma sugerida:
```python
def search_registry(
    db_session,
    type_filter: Optional[str] = None, # 'file', 'youtube', 'app', 'account'
    inc_name_path: Optional[str] = None,
    exc_name_path: Optional[str] = None,
    inc_tags: Optional[str] = None,
    exc_tags: Optional[str] = None,
    inc_extensions: Optional[List[str]] = None,
    exc_extensions: Optional[List[str]] = None, # Soporte para '__web__'
    has_info: Optional[str] = None, # 's', 'n' o None (Ambos)
    limit: int = 50,
    offset: int = 0
) -> List[ResourceRecord]:
```
Lógica esperada basada en el gestor anterior:
1.  **Nombre/Ruta**: Combinar el filtro para que busque en `title` o `path_url`.
2.  **Inclusiones (`inc_...`)**: Operadores `LIKE` convencionales.
3.  **Exclusiones (`exc_...`)**: Usar `NOT LIKE`. Para tags excluidos, usar subqueries o `NOT IN` para asegurar que el registro NO tenga ese tag específico.
4.  **Extensiones especiales (`__web__`)**: Si llega `__web__` en las extensiones a incluir, filtrar registros donde `type == 'youtube'` (o webs genéricas) OR `extension IN (...)`.
5.  **Tiene Info (`has_info`)**: 's' -> Registros que sí tengan `content_raw` o metadata de tags. 'n' -> Solo registros "crudos" sin contexto.
6.  Retornar lista de instancias `ResourceRecord`.

### Instrucción para el Constructor:
Implementar esta función en `core/search_engine.py` (o `core/database.py`). Esta es la copia exacta de la lógica de inclusión/exclusión que validamos exitosamente en los proyectos pasados. Usa SQLAlchemy.
