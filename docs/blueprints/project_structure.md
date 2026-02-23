# Blueprint: Arquitectura de Carpetas - Nexus V1.0

Este documento define la estructura en la que debe construirse el proyecto para asegurar modularidad y evitar dependencias circulares.

## Directorios y Propósito

*   **/core**: Contiene el motor base. Conexión a BD, modelos de datos (Pydantic), y utilidades globales. **Nada** aquí depende de otros módulos.
*   **/modules**: Contiene la lógica de negocio de alto nivel dividida por dominios:
    *   `file_manager/`: Indexación, búsqueda y gestión de archivos.
    *   `study_engine/`: Algoritmos SRS, sesiones Pomodoro y lógica de repasos.
    *   `pkm/`: Gestión de notas, links bidireccionales y grafos de conocimiento.
*   **/agents**: Lógica de integración con LLMs. Cada agente (Extractor, Generator, Evaluator) debe estar aquí.
*   **/ui**: Componentes visuales (Rich/Textual). Tablas de búsqueda, menús y dashboards estadísticos.
*   **/data**: Donde residirá la base de datos `nexus.db` y archivos de configuración.
*   **/docs/blueprints**: Instrucciones detalladas del Arquitecto para el Constructor.

## Reglas de Oro para el Constructor:
1.  **Tipado**: Usar `typing` en todas las funciones.
2.  **Modelos**: Las tablas de la BD deben tener un modelo de Pydantic espejo en `core/models.py`.
3.  **Logs**: Implementar logging desde el inicio en `core/logger.py`.
