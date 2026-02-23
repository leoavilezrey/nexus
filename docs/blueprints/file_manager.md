# Blueprint: Gestor de Archivos (Local File Manager)
Ubicación sugerida: `nexus/modules/file_manager.py`

Este módulo se encarga de procesar un archivo físico local y registrar su existencia en el Súper Schema de Nexus, permitiendo al buscador encontrarlo.

## 1. Función `ingest_local_file(filepath: str, tags: List[str]) -> Optional[ResourceRecord]`
Esta función recibe una ruta del PC y realiza la inyección a la base de datos `registry`.

### Lógica Requerida:
1. **Validación**: Comprobar usando `pathlib.Path` si el archivo existe. Si no, retornar None o lanzar una excepción clara.
2. **Extracción de Metadatos Base**:
   - `title`: `Path(filepath).name` (El nombre del archivo con extensión).
   - `path`: `Path(filepath).absolute().as_posix()` (Rendimiento garantizado cruzando OS).
   - `ext`: `Path(filepath).suffix.lower()`.
   - `size`: Tamaño en bytes (para el dictionary JSON `metadata`).
3. **Manejo de Texto Plano (Modo Lectura Rápida)**:
   - Si la extensión es `.md`, `.txt`, `.csv` u otro archivo puramente legible, la función debe leer los primeros X caracteres del archivo y guardarlos en el campo `content_raw` del registro.
   - Si es binario (como `.mp4`, `.pdf`, `.docx` sin extractor complejo), `content_raw` queda vacío (NULL). NUNCA guardar bytes.
4. **Inserción en Base de Datos**:
   - Tipo de registro: `'file'`.
   - Usar el motor SQLAlchemy (o equivalente) escrito previamente en `core/database.py` asegurándose de respetar los modelos de Pydantic.
   - Insertar las etiquetas (tags) vinculadas a este registro.

## Instrucción para el Constructor:
Implementar esta lógica manteniendo un acoplamiento flojo con la UI. Esta función recibe parámetros directos y devuelve el registro guardado o un error manejable. La importación de SQLAlchemy debe manejarse desde la capa Core, no instanciar conexiones huérfanas aquí.
