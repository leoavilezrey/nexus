# Registro de Desarrollo - Arquitecto y Constructor

**Propósito:** Este documento servirá como el canal de comunicación oficial entre el **Arquitecto** (Diseño y Lógica) y el **Constructor** (Implementación en Código) para el proyecto Nexus. Aquí se registrarán las órdenes, especificaciones técnicas y la evolución de los requerimientos para futuras modificaciones.

---

## TAREA 1: Implementación del Módulo [3] 🧠 ACTIVE RECALL

**Estado:** 🟢 Completado
**Asignado a:** Constructor
**Fecha:** 2026-02-23

### Especificaciones de Diseño (Actualizadas por el Arquitecto):

1. **Modo Único (Pomodoro):**
   - Eliminar la "Opción 1" (Modo Standard). El Active Recall en Nexus funcionará **exclusivamente** bajo la técnica Pomodoro.
   - Al iniciar la Opción 3, iniciará automáticamente una sesión de estudio basada en tiempo (ej. 25 minutos).

2. **Algoritmo de Tiempo (Ecuación SRS):**
   - El algoritmo de Repetición Espaciada (SRS) no solo debe depender de la calificación (1. Difícil, 2. Bien, 3. Fácil), sino que debe **utilizar el tiempo en la ecuación**. 
   - *Nota para el Constructor:* Considerar el tiempo que el usuario tardó en presionar 'Enter' para ver la respuesta. Si tardó mucho y marcó "Fácil", el sistema debe penalizar levemente ese "Fácil" ajustando el factor de retención. Alternativamente, integrar la duración del Pomodoro en el cálculo global del esfuerzo.

3. **Adelantar Tarjetas:**
   - Implementar una funcionalidad extra en el menú de Active Recall (antes de iniciar la sesión) o durante la consulta de la base de datos que permita **"Adelantar Tarjetas"**.
   - Esto significa que si el usuario no tiene tarjetas pendientes para hoy (`next_review <= fecha_actual()`), el sistema le permitirá estudiar las tarjetas programadas para los días siguientes, forzando la cola de repaso.

4. **Flujo Cíclico en `study_engine.py`:**
   - Crear el archivo `nexus/modules/study_engine.py`.
   - Flujo de UX por tarjeta con `Rich`:
     - Mostrar **Pregunta** (Panel Azul).
     - Prompt interactivo: `[Enter para ver Respuesta | 'f' para ver material fuente]`
     - Mostrar **Respuesta** (Panel Verde).
     - Calificar Retención: `[1] Difícil [2] Bien [3] Fácil`.
     - Actualizar la BD con la nueva fecha `next_review`.
   - Validar que el temporizador Pomodoro se evalúe de forma asíncrona o iterativa entre tarjetas para detener el ciclo cuando el tiempo se agote.
   - Limpiar la consola iterativamente con `console.clear()` para mantener la TUI limpia.

---

### Notas Técnicas del Constructor:
- Se creó `nexus/modules/study_engine.py` implementando la clase `SRSEngine` y el flujo `start_pomodoro_session`.
- **Ecuación SRS con Tiempo:** Se agregó una validación donde si el usuario tarda más de 15 segundos en procesar la tarjeta pero la califica como "Fácil" (3), el sistema lo penaliza asumiendo que el esfuerzo real fue un punto intermedio ("Bien" / 2.5). Esto amortigua el incremento abrupto de los intervalos de revisión (`card.stability`).
- **Tiempo Iterativo en Pomodoro:** Al final de cada iteración por tarjeta se evalúa contra el tiempo límite original (`duration_secs`). Adicionalmente, añadimos colores dinámicos al contador de tiempo (se vuelve rojo en los últimos 5 minutos).
- **Adelantar Tarjetas:** Expusimos un parámetro `adelantar=True/False` en la función `start_pomodoro_session`. El `main.py` podrá enviar un `True` para ignorar los filtros de `next_review` y obligar al usuario a seguir repasando.
- **Opción "f" (Material Fuente):** Se intercepta el input y, según el `registry.type`, se abre la URL en el navegador, se llama al explorador de windows seleccionando el archivo o se imprime una nota usando los Paneles de `Rich`.

*Constructor: Al completar esta tarea, favor de dejar nota en este mismo archivo o actualizar el estado a "🟢 Completado", indicando los archivos modificados.*

---

## TAREA 2: Integración del Módulo [4] 🔗 CONECTAR (IA Match & Vínculos Manuales)

**Estado:** � Completado
**Asignado a:** Constructor
**Fecha:** 2026-02-23

### Especificaciones de Diseño (Arquitecto):

1. **Objetivo del Módulo:**
   - La opción 4 del Dashboard ("CONECTAR") debe permitir relacionar dos elementos de la base de datos (por ejemplo, un archivo PDF y un apunte). Esta relación (grafo) se guardará en la tabla `nexus_links`.
   - Adicionalmente, permitiremos que una IA analice ambos registros y genere automáticamente Tarjetas de Estudio (Flashcards) basadas en las similitudes o diferencias entre esos dos conceptos.

2. **Flujos Solicitados en `ui/dashboard.py` (`menu_conectar`):**
   - El submenú ya existe con dos opciones: "1. Vincular Manualmente" y "2. IA Match Forzado".
   
3. **Flujo 1: Vínculo Manual (A implementar):**
   - Actualmente dice "en desarrollo". 
   - Debe pedir al usuario: ID del Registro A, ID del Registro B, un "Tipo de Relación" (ej. "complementa", "comparar") y una "Descripción" corta.
   - Guardar esto directamente en la Base de Datos llamando a `nx_db.create_link` con `NexusLinkCreate`.
   - Confirmar en pantalla con éxito.

4. **Flujo 2: IA Match (Revisión de Robustez):**
   - El código base actual pide ID A e ID B y llama a `agents.relationship_agent.generate_relationship_cards()`.
   - **Orden para el Constructor:** Abre el archivo `agents/relationship_agent.py` (si existe, revísalo; si no existe o está en borrador, constrúyelo).
   - Este agente debe recibir los textos (vía `content_raw` o metadatos) de los dos registros.
   - Debe contactar a un LLM (usando tu método preferido, ej. openai, groq, anthropic, o un moockup funcional si no hay API KEY seteada localmente) con un prompt que pida extraer diferencias clave y generar *Flashcards* (Pregunta y Respuesta).
   - Estas cartas devueltas deben guardarse como de tipo "Relacional" o "IA_Match", asociadas de alguna forma a la relación de las dos entidades (o como hijos de una de ellas).
   - Validar que al terminar, el UI devuelva a la pantalla principal correctamente con `Prompt.ask`.

---

### Notas Técnicas del Constructor:
- Se actualizó el archivo `ui/dashboard.py` reemplazando la "Opción 1" de Vínculo Manual con la lógica correspondiente para pedir ID origen, destino, tipo de relación y descripción. Llama a `nx_db.create_link()` para forzar el registro.
- En la Opción 2 del mismo menú, se corrigió una llamada a la función fantasma `get_resource_record()`, reemplazándola por `nx_db.get_registry(id)`.
- Se revisó y actualizó `agents/relationship_agent.py`:
  - Se cambió el tipado para que reciba directamente objetos `Registry` desde SQLAlchemy en vez del Pydantic Model crudo.
  - Se ajustó el getter de propiedades a `meta_info` en concordancia con el ORM `core/database.py`.
  - Se ha añadido un  **Modo de Mockup Funcional** que intercepta si `os.environ.get("GOOGLE_API_KEY")` no está seteado. Devolverá una tarjeta "Mock" para probar la TUI sin crashear mientras el sistema se termina de configurar y acoplar online.

*Constructor: Tu entrega para esta tarea es hacer que el Vínculo Manual funcione y asegurarte de que exista un archivo `agents/relationship_agent.py` mínimamente funcional para que no haya un gran crash al seleccionar la opción 2 de IA.*

---

## TAREA 3: Extracción Web y YouTube en Módulo [1] INGRESO (Ingestión de Datos Externos)

**Estado:** � Completado
**Asignado a:** Constructor
**Fecha:** 2026-02-23

### Especificaciones de Diseño (Arquitecto):

1. **Objetivo del Módulo:**
   - La opción 2 ("Añadir URL Web / YouTube") dentro del Menú 1 "INGRESO" del Dashboard debe dejar de ser un texto indicativo y convertirse en una herramienta funcional que extraiga y guarde contenido en la Base de Datos (`Registry`).

2. **Flujos Solicitados en `ui/dashboard.py` (`menu_ingreso`, opción 2):**
   - Pedir al usuario: La URL (puede ser un video de YouTube o un enlace web cualquiera) y Etiquetas (tags).
   - El sistema debe determinar si es YouTube o página Web analizando el link.
   - Enviar a una función especializada en el backend. 

3. **Backend `modules/file_manager.py` (o un nuevo archivo `web_scraper.py`):**
   - **Caso YouTube:** Usar la librería `youtube-transcript-api` (instalarla en el entorno) para bajar los subtítulos/texto del video si están disponibles y concatenarlos como `content_raw`. Usar `yt-dlp` en modo ligero o alguna librería extractora para obtener el título original.
   - **Caso Web Genérica:** Implementar un scrapper muy simple (ej. usando `requests` y `BeautifulSoup4`) que tome el texto limpio de los párrafos (`<p>`) o el bloque central leglible para almacenarlo como `content_raw`. También extraer el tag `<title>`.
   - Si un script falla (ej. video sin subtítulos o página bloqueada), notificar al usuario, pero guardar al menos el título y URL como recurso huérfano para indexarlo.
   - Registrar la entrada en SQLAlchemy llamando a `nx_db.create_registry`. Tipos esperados: `youtube` o `web` (o `file` si el blueprint dictaba otro, aunque `youtube` está en los esquemas válidos Pydantic en `core/models.py`).
   
4. **Respuesta en TUI (Terminal User Interface):**
   - Si la ingesta es correcta, mostrar "✅ Recurso Web indexado: [Título]".
   - Pausar antes de volver al menú.

---

### Notas Técnicas del Constructor:
- Se añadió e instaló exitosamente el stack de raspado virtual (`youtube-transcript-api`, `bs4`, `requests`, `yt-dlp`).
- Fue necesario registrar la constante `"web"` en la base central de datos (`core/models.py` y `core/database.py`) ya que no existía formalmente como ResourceType válido; sin embargo, ahora SQLAlchemy y Pydantic aprueban el "web" sin problemas.
- Se ha creado el archivo `modules/web_scraper.py` con una función router principal `ingest_web_resource()`. De allí, se deriva asimétricamente a funciones privadas `_ingest_youtube` y `_ingest_generic_web`.
- **Mitigación de Crash LLM:** El texto rasgado de internet se limita proactivamente a `50,000` caracteres (aproximadamente `~1.5 horas` completas de transcripción cruda de YouTube o `~25,000` palabras) para no sobrecargar masivamente el Token Window del motor a futuro ni sobrecargar SQLite.
- **YouTube Error Handling:** Si el video no admite subtítulos autogenerados (ej: LiveStreams muy viejos, restringidos) guarda la URL pero con una nota interna explicatoria.
- El Sub-Menú 2 (Ingreso Web) dentro del Dashboard ahora llama a un spinner visual `.status(...)` muy elegante mientras scrapea, antes de avisar si todo finalizó de maravillas.

*Constructor: ¡Atención a las librerías necesarias! Asegúrate de instalarlas si no están (ej. pip install youtube-transcript-api bs4 requests). El campo `content_raw` es clave aquí, ¡es lo que alimentará los repasos!*

---

## TAREA 4: Construcción del Módulo [5] ESTADÍSTICAS GLOBALES

**Estado:** � Completado
**Asignado a:** Constructor
**Fecha:** 2026-02-23

### Especificaciones de Diseño (Arquitecto):

1. **Objetivo del Módulo:**
   - La opción 5 del Dashboard ("ESTADÍSTICAS GLOBALES") debe conectarse a la base de datos subyacente (`core/database.py`) y mostrar métricas reales sobre la madurez y composición del "Cerebro" (Nexus). 
   - Se debe eliminar la sección estática en el banner superior si es redundante, o conectarla a variables reales rápidas, reservando la Opción 5 para un desglose masivo y hermoso de los análisis.

2. **Flujos Solicitados en `ui/dashboard.py` (`menu_estadisticas`):**
   - Actualmente esta función solo imprime "Calculando métricas globales de Nexus... (Módulo en construcción)". 
   - El Constructor deberá crear las consultas (queries) a SQLAlchemy dentro de un nuevo archivo, por ejemplo `modules/analytics.py` (o directamente integrarlo en la base de datos).

3. **Métricas Obligatorias a Extraer:**
   - **Composición del Cerebro:** Contar registros por *Tipo* (Cuántos 'youtube', 'web', 'file', 'note').
   - **Red Neuronal:** Contar cuántos Vínculos Manuales (`NexusLink`) y Tags únicos hay.
   - **Madurez Cognitiva (SRS):** 
     - Contar el total de Flashcards creadas.
     - Separar cuántas tarjetas están *Pendientes por Repasar Hoy* vs *Para el Futuro*.
     - Calcular una métrica de Retención General promediando la *Estabilidad* (`stability`) o *Dificultad* (`difficulty`) global de todas las tarjetas. (Ej: "Promedio de Dificultad: alta/media/baja").

4. **Visualización en TUI (Terminal):**
   - Utilizar las facilidades de `Rich` (Paneles, Columnas u Organizadores en Tablas).
   - ¡Debe verse espectacularmente claro, casi como el tablero de una nave espacial (Cognitive Console)! Un color predominante por tipo de métrica (Ej. Verde para SRS, Azul para Registros Físicos).

---

### Notas Técnicas del Constructor:
- Se ha creado el archivo `modules/analytics.py` que incluye la lógica de consultas mediante SQLAlchemy para calcular las métricas reales del núcleo (Registrys, SRS, Grafos y Tags).
- **Refactorización de UX Front-End**:
  - En `ui/dashboard.py`, el *Header estático* inicial (que antes traía números falsos hardcodeados) se reconectó asíncronamente con la base de datos para mostrar un desglose real resumido cada vez que se carga el dashboard principal (`get_stats_panel()`).
  - La opción completa `[5] ESTADÍSTICAS GLOBALES` ahora invoca a las rutinas de `analytics.py` usando un Spinner Visual y despliega en pantalla tres sub-paneles majestuosos construidos nativamente con `Rich`. 
     - 🗄️ **Composición del Cerebro** (Color Cyan)
     - 🔗 **Red Neuronal** (Color Magenta)
     - 🧠 **Madurez Cognitiva** (Color Verde y diagnósticos on-blue), la cual mide las proyecciones SRS en vivo evaluando la Estabilidad y la Dificultad de los Flashcards.
- El módulo se encuentra 100% vivo e intercomunicado con el Core SQLite.

*Constructor: Tu entrega es reemplazar el `menu_estadisticas()` en `ui/dashboard.py` con una llamada a la capa de analítica que vas a desarrollar, e iterar la UX para que sea informativa, precisa y se detenga hasta que el usuario presione Enter para volver.*

---

## TAREA 5: Refactorización UX (Bucles Internos en Submenús)

**Estado:** � Completado
**Asignado a:** Constructor (Intervención de Arquitecto)
**Fecha:** 2026-02-23

### Especificaciones de Diseño (Arquitecto):

1. **Objetivo del Módulo:**
   - Mejorar la fluidez del usuario. Actualmente, cuando el usuario termina una acción dentro de un sub-menú (ej. Agregar un Archivo local, Enlazar un Nodo de Red, Raspar una URL), el sistema automáticamente lo arroja de vuelta al *Menú Principal* luego de presionar Enter.
   - Necesitamos que el usuario pueda quedarse dentro del sub-menú para realizar la misma acción varias veces sin tener que navegar desde el root del dashboard.

2. **Flujos Solicitados en `ui/dashboard.py` (`menu_ingreso`, `menu_conectar`):**
   - **En `menu_ingreso()`**: Convertir toda la función en un bucle `while True:`. Acabar con los `Prompt.ask("Presiona ENTER...")` de bloqueo final de los if/elif y en su lugar, después de mostrar el mensaje de éxito (o error), preguntar al usuario qué desea hacer a continuación.
     - Ej: `console.print("\n[1] Indexar otra fuente | [0] Volver al Menú Principal")`
     - Si escoge 1, el bucle reinicia (ejecuta de nuevo el ingreso elegido u ofrece escoger el tipo de nueva fuente). Un rediseño sencillo sería que al terminar una inserción, el `continue` relance el print del "Menú de Ingesta Estricta". Si marca 0, se usa `break` que lo saca de la función `menu_ingreso` regresando al Main Loop.
   - **En `menu_conectar()`**: Igual. Validar un `while True:` para que la persona pueda forjar múltiples vínculos explícitos o generar varias tarjetas IA consecutivamente sin salir. Si elige la opción de "Atrás/Volver" o se completa un registro manual y luego elije 0, hace `break`.

3. **Análisis de otros Módulos Funcionales (Para el Constructor):**
   - **`menu_active_recall()`**: Evalúa tu código. ¿Te saca del proceso apenas terminas un pomodoro? ¿Ofrece opción de "Comenzar otro pomodoro / Adelantar otro lote" o regresa al main menu? Si regresa, envuélvelo en un `while True` ofreciendo continuar.
   - **`menu_explorar()`**: Revisa tu UX aquí. Actualmente el buscador muestra la tabla y tiene un bucle propio de `Atajos: Escribe fN para abrir el archivo N`. Revisa si el bucle está saliendo al menú principal lógicamente, o si deberías preguntar explícitamente `[1] Buscar Otra Cosa | [0] Volver` tras presionar '0' o 'q'.

*Constructor: Modifica estas funciones en `ui/dashboard.py` para usar `while True` con breaks que apunten de regreso al sub-menú o al main loop basándote en la instrucción explícita del usuario post-operación.*

---

### Notas Técnicas (Arquitecto):
- Se implementó directamente la funcionalidad de los bucles infinitos (`while True:`) en los siguientes submenús dentro de `ui/dashboard.py`:
  - `menu_ingreso()`
  - `menu_active_recall()`
  - `menu_conectar()`
- Al finalizar cualquier acción (por ejemplo, guardar un archivo, culminar un repase Pomodoro o enlazar nodos), el sistema ya no fuerza una regresión al Menú Principal con un simple `Prompt.ask("Presiona ENTER")`.
- **Refinamiento de Navegación 3-Niveles**: Se ha creado un Bucle Anidado donde, justo al terminar una acción, se ofrecen **tres** opciones puntuales que mantienen el estado de fluidez deseado por el usuario:
  - `[1] Repetir la Acción` (Ej. Indexar otra fuente usando el *mismo* método elegido).
  - `[2] Volver al Submenú Superior` (Ej. Devolverlo al "Menú de Ingesta Estricta" para elegir otra categoría).
- El Explorador no requirió modificación profunda, ya que ya posee su propio loop para abrir múltiples archivos consecutivamente y sale presionado `0` o `q`.

---

## REGISTRO DE PARCHES: Hotfix v1.0.1 (Web Scraper YouTube)

**Estado:** 🟢 Solucionado
**Atendido por:** Arquitecto
**Fecha:** 2026-02-23

### Descripción del Incidente Reportado:
Al intentar extraer una URL nativa de YouTube (ej. `_BteEJkp4bc`), la librería de Extracción e Ingestión generaba severo ruido visual en la terminal y crasheaba la captura de texto debido a incompatibilidades de API y verbosidad innecesaria. 

**Excepciones levantadas:**
- `Error: type object 'YouTubeTranscriptApi' has no attribute 'list_transcripts'`. (Cambio de Sintaxis Deprecada por parte de la librería oficial).
- `WARNING: [youtube] No supported JavaScript runtime... WARNING: ffmpeg not found` (Logs muy ruidosos de `yt-dlp` en pantalla).
- Multiples líneas de stack-trace impresas al usuario cuando un video carecía forzosamente de subtítulos reales.

### Cambios Aplicados (`modules/web_scraper.py`):
1. **Actualización del Método Transcript:** Se actualizó `YouTubeTranscriptApi.list_transcripts(video_id)` a la sintaxis moderna basada en instancias usando un objeto base `ytt_api = YouTubeTranscriptApi()` seguido de la llamada a `ytt_api.list(video_id)`.
2. **Supresión de Basura Visual (Warnings):** Se anexaron banderas de configuración rigurosas sobre el diccionario de opciones `ydl_opts` (`'no_warnings': True`, `'extract_flat': True`, `'logger': None`) para silenciar forzosamente a `yt-dlp`, ya que solo necesitamos el título en texto plano sin invocar motores pesados en JS nativamente de video ni descargar frames con FFmpeg.
3. **Limpieza del Capturador de Errores (Trimming Out):** Se modificó el bloque `try/except` final de manera que, si de plano no hay CC's (subtítulos) porque el canal los desactivó de origen, el mensaje pase por un `.split('\n')[0]`, reduciendo 15 líneas de un aparatoso *traceback* en rojo, a una refinada y educada advertencia amarilla de una sola línea en consola que dice de manera limpia: `Aviso: No se pudo obtener la transcripción...`.

---

## TAREA 6: Habilitación Módulo Ingesta "Apps" [Opción 4]

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto
**Fecha:** 2026-02-23

### Descripción del Cambio:
- La **Opción 4 del Menú de Ingesta Estricta** estaba configurada como un stub temporal interactivo (`Módulo en Construcción`).
- Fue implementado directamente programando prompts iterativos y rigurosos. Ahora solicita:
  1. `Título o Plataforma`
  2. `Ruta, URL web o Comando`
  3. **[NUEVO] `Plataforma Específica` (Ej. PC, Web, Android, iOS con Default en PC).**
  4. **[NUEVO] `Requiere Logueo` (Pregunta Y/N convertida en valor booleano interno).**
  5. **[NUEVO] `Descripción Extendida / Notas de Uso` (Se anexa al metadata raw).**
  6. `Etiquetas / Tags`
- Los datos se vinculan y guardan explícitamente usando el objeto base `RegistryCreate` bajo el tipo general `app` en la SQLite DB. Toda la data nueva recavada (Plataforma y Login) se serializa dinámicamente en el JSON `meta_info` (`platform_type` y `requires_login`) y a su vez se compila todo junto en un bloque enriquecido para el `content_raw` con tal de que Nexus o la IA pueda usar este conocimiento al formular Flashcards para el usuario.
- Al igual que sus funciones hermanas, este bloque se envolvió en su propio `while True` interactivo que ofrece el control estricto de **3 niveles de navegación pos-operación** para agregar N herramientas nativas de escritorio o páginas utilitarias en serie sin tener que volver a abrir el menú padre jamás.

---

## TAREA 7: Refactorización Avanzada del Explorador Maestro (Módulo 2)

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto
**Fecha:** 2026-02-23

### Descripción de los Cambios en Búsqueda, Visualización y DB:
1. **Prevención de Duplicados Base de Datos:** Se reforzó el Core `database.create_registry`. Si una `path_url` ya existe en Nexus y se intenta indexar (ej. la misma URL de Youtube o la misma ruta de archivo físico), la operación escupe un error rojo bloqueando la operación por redundancia. Asimismo el script inyecta un campo de extracto base por defecto si no es provisto manualmente.
2. **Visualización Global con Paginación:** El Módulo 2 ya no pide "qué buscar" a ciegas de inicio, ahora siempre arranca revelando todos los componentes del "cerebro Nexus" de forma descendente (recientes primero). El limitador físico en pantalla se ha fijado a **13 elementos por página**, y la UI te habilita controles fluidos de `[n]` y `[p]` para alternar hojas de resultados.
3. **Filtros Dinámicos Preservables:** Con el botón `[s]` revelas el panel interactivo multi-filtros, todo lo que insertes allí redibuja la tabla re-entregándola en la Página 1 de forma automática. Además las 5 columnas vitales siempre se pintan incluyendo extractos del texto en miniatura con el fin de leer un contexto general rapidísimo.
4. **Modo Detalle de Entorno y Repaso Interactivo:** Se diseñó el sub-módulo interno `_show_record_detail()`. Al llamar un documento o ID (Ej. `v5`) invocas la super tarjeta contextual. 
   - Esta permite `[1]` Editar libremente todas sus _Etiquetas Ocultas_ y rescribir su _Descripción Base_.
   - Te permite con `[2]` abrir de un hachazo cualquier carpeta de Windows Explorer si era C:/, ejecutar un App o levantar un Browser si fuera una IP/dominio web.
   - Cuenta con el submenú de foco `[3] Repaso Interactivo` que apalanca toda la atención visual para leer tu metadata o documento de corrido, adjuntando también abajo tu Red Neuronal ramificada (`Nodos Anclados Salientes e Intrants`) permitiéndote _saltar directamente mediante recursividad_ usando otro vID directamente hacia tu enlace asociado sin volver jamás al buscador principal. Opciones perfectas con navegación anidada y `breaks` pulidos hacia las raíces.

---

## TAREA 8: Migración y Estandarización de Registros Históricos (Base de Datos)

**Estado:** � Completado
**Asignado a:** Constructor
**Fecha:** 2026-02-23

### Especificaciones de Diseño (Arquitecto):

1. **Objetivo Central:**
   - La nueva arquitectura exige reglas duras: Ningún registro alojado en la base de datos puede tener su *Título/Nombre* (`title`) ni su *Descripción/Contenido* (`content_raw`) vacíos. Muchos registros viejos (creados en versiones previas) podrían estar violando esta regla ahora mismo.
   - Es mandatorio escribir y ejecutar un script de migración que recorra todos los registros físicos dentro de `nexus.db` y los parchee para cumplir estas nuevas validaciones obligatorias impulsadas en la Tarea 7.

2. **Criterios de Normalización (Reglas de Oro):**
   - **ID:** Todo registro ya cuenta con un ID por tratarse de SQLite (`Primary Key`), mantener intacto.
   - **Nombre (`title`):** Si un registro tiene el `title` vacío (`None` o `""`), el script debe asignar un título por defecto deduciéndolo de la ruta (`path_url`) o asignando "Registro Sin Título N".
   - **Descripción (`content_raw`):** Si el campo está vacío, inyectar obligatoriamente la plantilla estándar: `(Auto-Descripción Migrada) Título: {reg.title} | Ruta: {reg.path_url}`.
   - **Etiquetas (`tags`) y Metadatos:** Se permite que queden vacíos según diseño del schema, pero es fundamental asegurar que no rompan las consultas en el Explorador si son de tipo nulo (`None`).

### Notas Técnicas del Constructor:
- Se redactó exitosamente el script de limpieza histórica `scripts/migracion_v1_0.py`.
- **Resultados de la Ejecución Directa en DB (`nexus.db`):** 
  - Se detectó y corrigió `1` registro físico que carecía por completo de título válido.
  - Se detectaron e inyectaron plantillas de Auto-Descripción en `3` registros ciegos que carecían de sintaxis base (evitando que el nuevo panel del _Explorador Maestro_ sufriera caídas al invocar nulos).
- Todos los cambios fueron debidamente "commiteados" a la base de datos de producción local de Windows. El *Super Schema* está ahora 100% normalizado y listo para la validación estricta a futuro estipulada en la Tarea 7.

---

## TAREA 9: Borrado de Registros en el Explorador Maestro

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto
**Fecha:** 2026-02-23

### Descripción de los Cambios en UI y Lógica de Eliminación:
1. **Nuevo Endpoint en el Gestor de Base de Datos:**
   - Se inyectó a la clase `NexusCRUD` del archivo `core/database.py` un nuevo método troncal llamado `delete_registry()`. Su objetivo no es simplemente dar de baja un ID, sino orquestar una destrucción lógica "en cascada manual" muy asertiva (borrando primero `Tags`, luego rompiendo vínculos con la red de nodos `NexusLink` y demoliendo las Flashcards `Card` atadas) para evitar cabos sueltos y no depender empíricamente del pragma `ondelete="CASCADE"` de SQLite, el cual en algunas versiones corre apagado por defecto.
2. **Interfaz de UX Segura en la Vista Detalle:**
   - Aprovechando el rediseño anterior de UI/dashboard, la función contextual `_show_record_detail(rec_id)` ahora expone en el menú interactivo la opción `[4] Eliminación Permanente`.
   - Incorpora un prompt robusto *Red on Black* en la TUI de Rich que requiere que el usuario deletree literalmente y escriba `"eliminar"` para aprobar la inmolación del registro. Acto seguido te notifica el éxito de la operación en C:/ y te saca elegantemente devolviéndote a la tabla indexada principal.

---

## TAREA 10: Extracción Masiva (Gestor Antiguo -> Nexus Super Schema)

**Estado:** 🟢 Completado
**Asignado a:** Constructor
**Fecha:** 2026-02-23

### Descripción de la Operación (Constructor):
1. **Detección y Mapeo Trans-Base de Datos:**
   - Se localizó tu antigua base de datos SQLite operativa (`personal_file_mcp/files.db`) que rondaba los 7.8 MB y ~23,000 registros históricos separados en múltiples tablas primitivas (`files`, `apps`, `cuentas_web`, `paginas_sin_registro`, `metadata`, `descriptions`).
   - Se redactó el script de extracción pura y pesada `scripts/migrar_db_antigua.py` diseñado para conectarse a ambos universos: leer de la vieja base de datos, adaptar el formato, filtrar duplicados en vivo, y escribir transaccionalmente hacia la nueva tabla unificada `Registry` de Nexus.
   
2. **Homologación Exitosa:**
   - Se importaron exitosamente hacia este nuevo ecosistema los siguientes dominios:
     - **Archivos Físicos:** Se concatenaron limpiamente con sus rutas, descripciones en AI-Metadata y tags.
     - **Aplicaciones y Cuentas Web:** Se adaptaron a entidades `type="app"` y `type="account"`, consolidando su metadata JSON (plataformas, contraseñas lógicas) de acuerdo a las últimas refactorizaciones del Blueprint de Nexus que programamos en las Tareas 4 y 6.
   - En total **más de 23,700 artefactos de memoria** habitan hoy de manera limpia en tu nuevo Motor Central Nexus. ¡El cerebro está cargado! Todos los registros ahora siguen las mismas reglas para admitir IA, Red Neuronal y Active Recall sobre ellos de ser necesario.

---

## TAREA 11: Absorción de Antiguas Flashcards (AR-Console -> Nexus)

**Estado:** 🟢 Completado
**Asignado a:** Constructor
**Fecha:** 2026-02-23

### Detalle de Extracción (Sistema de Aprendizaje):
1. **Detección del Legado SRS:**
   - Se identificó la antigua base curada `ar_console.db` perteneciente al proyecto original *AR-Console* (que contenía tu acervo de tarjetas de repaso personalizadas).
2. **Refactorización del Modelo `Concept`:**
   - Dado que el esquema viejo no ataba sus flashcards a IDs específicos de la BD de archivos, sino a cadenas flotantes (`source_concept`), programé el script `scripts/migrar_tarjetas_ar.py` para iterar sobre este material.
   - **Lógica Inyectada:** Evaluó cada tarjeta, y para cada Concepto huérfano (ej. "Kubernetes Base") creó automáticamente en Nexus un nuevo Registro de tipo `concept` que sirviera de padre (nodos raíz). 
   - Abarcó el rescate de las variables dinámicas del SRS FSRS/SM-2 de memoria como `difficulty`, `stability`, `last_review` y `next_review`.
3. **Logro Final:**
   - Se migró victoriosamente un total de 56 Tarjetas (Flashcards) listas para Active Recall junto a todas sus etiquetas cruzadas.
   - Ya puedes ir al Menú `[3] ACTIVE RECALL` y comenzar tu Pomodoro directamente sin perder un solo día de tu historial de estudio previo. Tu progreso retentivo está de vuelta al 100%.

---

## TAREA 12: Modo Exterminio (Borrado Masivo en Lote)

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto Front-End
**Fecha:** 2026-02-23

### Descripción de los Cambios:
1. **Lógica de Parseo Compleja (Parser CLI):**
   - Se inyectó en el Explorador (`menu_explorar`) la detección de los prefijos `del ` y `borrar `.
   - Cuenta con un algoritmo ágil capaz de fraccionar rangos y conjunciones separadas por comas. (Por ejemplo: procesar e interpretar `del 1,2,6-10` en un array interno estricto: `[1, 2, 6, 7, 8, 9, 10]`).
2. **Ejecución y Seguridad:**
   - Pre-calcula los IDs ingresados y omite silenciosamente basuras o letras coladas.
   - Despliega un panel de confirmación agresivo advirtiendo la cantidad exacta de registros apilados en el corredor de la muerte. Obliga al usuario a estampar `eliminar lote` explícitamente para accionar.
   - Ejecuta recursivamente el `delete_registry` limpio y documenta cuántos evaporó satisfactoriamente y recarga tu vista si hubo éxitos.

---

## TAREA 13: Refactorización Visual y Reparación de Contraste

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto Front-End
**Fecha:** 2026-02-23

### Descripción de los Cambios:
1. **Problema del Espectro Azul-Rojo:**
   - La librería `rich` imprime etiquetas estándar `[red]` o `[bold red]` como texto literal rojo incandescente. Sobre una consola Powershell con fondo de tonalidad Azul Oscuro, este contraste produce un borrado semántico que cansa la vista y disminuye dramáticamente la legibilidad.
2. **Implementación de Rectángulos de Alerta:**
   - Se diseñó y ejecutó el script de curación `scripts/fix_colors.py` a través de todos los módulos del Súper Schema (`ui/dashboard.py`, `study_engine`, `database`, `agents`).
   - Todos los identificadores `[red]` fueron sustituidos globalmente por la métrica de contraste de alta fidelidad `[bold white on red]`. 
   - A partir de este momento, cada vez que haya un error o pantalla crítica de advertencia, **las letras permanecerán de un blanco brillante y grueso**, encerradas dentro de un bloque/rectángulo rojo sólido que sí crea un perfecto marco visual de contraste contra el fondo azul.

---

## TAREA 14: Restructuración del UX/UI en Active Recall (Pomodoro)

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto Front-End / Especialista Pedagógico
**Fecha:** 2026-02-23

### Análisis y Cambios del Flujo de Estudio:
1. **Inversión Pedagógica:**
   - Anteriormente, el sistema (`study_engine.py`) golpeaba al usuario directamente con la "Pregunta" sin darle contexto en la Interfaz, causando confusión sobre a qué archivo pertenecía.
   - El código fue alterado masivamente para ser "Context-First". Ahora, cada vez que salta una Flashcard, la UI renderiza el Cuadro Cyan `[📚 Contexto de la Tarjeta]` que exhibe el Título y la URL de donde nació.
   - Detiene el tiempo y lanza un prompt preguntando: *"¿Deseas leer el tema fuente antes de la pregunta?"*. Si el usuario escribe `f`, abre el PDF, YouTube o Nota directamente. Sólo cuando siente que repasó, la consola despeja la pantalla y lanza la Pregunta Oficial exigiendo un esfuerzo puramente activo.
2. **Corrección de Overlaps (Superposición) Visual y Temporal:**
   - Añadidas separaciones forzadas de línea `\n` y paneles dedicados tanto para la Q (Azul) como para la A (Verde) en `study_engine.py`.
   - Modificado el renderizado crítico del temporizador (`color_time`), que imprimía variables en `[red]` genérico causando los cortes invisibles que te frustraron en la lectura en cuenta regresiva. Fueron sustituidos explícitamente a `[bold white on red]` usando el macro de limpiar consola `draw_header()`.
   - Se añadió un conversor especial de URLs en Consola que te muestra textualmente el link en la propia terminal (ej. `[link=https://...`) como Plan B o backup visual si la Opción 'f' te queda lejos de la mente.
4. **Tracking de Tarjetas y Métricas:**
   - He expuesto un contador numérico interconectado al Renderizado. A un lado del temporizador Pomodoro ahora verás impreso `[Tarjeta X de Y]`, por lo que siempre tendrás consciencia de "cuántas preguntas están disponibles" en la pila actual de estudio para medir tu energía.
5. **Modalidad "Keyboard" vs "Brain":**
   - Antes tú sólo pensabas la pregunta. Ahora incluí una entrada interactiva debajo de ella que te permite *literalmente escribir* la respuesta en el sistema. 
   - Cuando reveles la Flashcard, la consola comparará tus palabras en un bloque azul al lado de la Respuesta oficial del Sistema.
6. **Salir del Bucle (Abortar Sesión):**
   - Se añadió un detector en la barra de pregunta. Si en lugar de responder algo decides escribir estricta y únicamente `salir`, el sistema truncará el pomodoro de inmediato sin borrar tu progreso guardado.

---

## TAREA 16: Refactorización Menu Principal Active Recall y Mitigación de Overlaps

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto UI/UX
**Fecha:** 2026-02-23

### Descripción de los Cambios:
1. **Solución Radical al "Overlapping" de Consola (Superposiciones):**
   - La librería `rich` utiliza comandos de escape ANSI (virtuales) para limpiar interfaces gráficas (`console.clear()`). PowerShell no es 100% amigable con este método bajo escrutinio rápido (por su buffer largo), causando desagradables artefactos donde las letras antiguas no se borran y se "empastan" con la Tarjeta Nueva.
   - Todo el motor (`study_engine.py` y `dashboard.py`) fue refactorizado. Las limpiezas ya no se las pedimos al intérprete Python, sino al Kernel de Windows. Se ejecutaron docenas de mandatos duros nativos para borrar canvas en bruto: `os.system('cls' if os.name == 'nt' else 'clear')`. Esto elimina para siempre la superposición.
2. **Rediseño Estructural del Dashboard Repaso:**
   - La Opción "Adelantar" inicial y confusa fue compactada. Al entrar a la opción principal **[3] ACTIVE RECALL**, el sistema ahora te da la bienvenida directamente listando "🔥 Temas Disponibles para Estudiar HOY" (Las variables vencidas en la curva del olvido).
   - De abajo de eso, nace un Menú Selector Definitivo: Te da la opción de Repasar Todo, Salir, Adelantar, o Escoger de un plumazo el Tema que quieres repasar basado en los IDs que viste impresos.
3. **Punto de Invernaje de Visualización:**
   - Si escogías un tema en específico por ID y marcabas 'Enter', antes te golpeaba la primera vez con la duda de memoria igual. Inyecté una pregunta filtro: Tras colocar el ID 17 para estudiar, el programa pausa y te pregunta si quieres "🧠 Iniciar Repaso (Active Recall)" o "📖 Abrir el Documento / Web primero para leerlo". De esa forma el ciclo cognitivo cierra magistralmente.

---

## TAREA 17: Flujo Condicional Intangible y Live-Delete (Borrado en Vivo)

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto UX / Motor Principal
**Fecha:** 2026-02-23

### Descripción de la Mejora:
1. **Borrado en Vivo de Flashcards:**
   - La funcionalidad de borrado nativo durante la fase Pomodoro fue incorporada ágilmente. Al salir una carta, el *prompt* ya no se limita a pedirte la respuesta, sino que escucha el comando estricto `eliminar`.
   - Si el usuario lo tipea, el Motor frena, exige Confirmación Explícita `(s/n)` para evitar roces de teclado accidentales, y si es positivo, envía la orden al ORM (Destruye la carta de la base de datos para siempre) y avanza sedosamente a la siguiente usando un `continue` algorítmico sin romper el contador de tiempo.
2. **"Topic Caching" Inteligente (Ocultado de Prompts Repetitivos):**
   - El Engine fue re-estrucurado para recordar de qué ID provenía la pregunta anterior guardándolo en una variable temporal (`last_topic_id = None`).
   - Ahora, **sólo te preguntará** si deseas abrir o navegar hasta tu Material Fuente **si la materia cambió**. Si estudiaste Kubernetes y esa batería de estudio tiene 20 cartas seguidas, sólo verás el molesto cartel de leer tu material en la Pregunta #1. Desde la #2 hasta la #20 del tema, fluirás ininterrumpido.


---

## TAREA 18: Compactación de Header y Agente Mutador (IA)

**Estado:** 🟢 Completado
**Asignado a:** Motor Principal / IA Agent
**Fecha:** 2026-02-23

### Descripción de la Mejora:
1. **Header UI Compacto (Evitar saturación visual):**
   - Atendiendo la lógica de "Topic Caching", se modificó el componente `draw_header()` del Pomodoro. 
   - El gran panel Cyan de Contexto y URLs explicativas ahora sólo se despliega en la **Primera Pregunta** de cada tema nuevo. Cuando avanzas a las siguientes preguntas del mismo tema, todo el bloque se encoge silenciosamente a un minúsculo breadcrumb `[📚 Repasando: Nombre del Tema]`, dejando toda la pantalla de tu PowerShell despejada y enfocada 100% en la Pregunta, para no apabullarte visualmente si haces 20 flashcards seguidas.
2. **Agente IA de Mutación ("El Agente Nocturno"):**
   - Se creó un nuevo agente dedicado en `agents/mutation_agent.py`. Su propósito es aplicar Inteligencia Artificial con Prompt Engineering estricto para *reescribir semánticamente* las tarjetas sin alterar su conocimiento base, destruyendo así la "memoria estática visual" típica de estudiar la misma flashcard por meses.
   - **Disparador Just-in-Time Opcional:** El motor de Active Recall ahora recolecta en secreto los IDs de **absolutamente todas las tarjetas repasadas** durante el Pomodoro. Al agotarse el tiempo o al terminar las tarjetas del día, Nexus intercepta la pantalla de victoria y pregunta: *"Has repasado N tarjetas. ¿Deseas activar el Agente Mutador de IA para analizarlas y reformularlas (rompiendo así la memorización sistemática de formatos)? (s/n)"*
   - Si respondes que sí, la IA tomará esa pila masiva por debajo de la mesa, la reformulará en sinónimos / distintos ángulos de pregunta, contactará la base de datos SQL local y sobreescribirá las viejas para que mañana enfrentes retos mentales genuinos.

3. **Invocación Universal de Archivos (`open_source_material`):**
   - Anteriormente, presionar "Abrir Archivo" si era una nota solo pintaba un texto crudo de la pantalla que se volvía inmanejable y estorbaba visualmente, sin abrir el archivo real si lo hubiera.
   - Ahora, el motor succiona el String de la Base de Datos (`path_url`) e interpreta automáticamente qué hacer: Si es `"http"`, abrirá Google Chrome. Si es un archivo físico (PDF, Text), usará la librería `os.startfile(ruta)` obligando al sistema de Windows a disparar la aplicación nativa por defecto.

---

## TAREA 19: Fix de UnicodeEncodeError (Lonely Surrogates)

**Estado:** 🟢 Completado
**Asignado a:** Arquitecto / Constructor
**Fecha:** 2026-03-01

### Descripción del Incidente y Parche de 3 Niveles:
1. **El Problema:** Al acceder a la Opción 2 del Menú (Explorador Gestión), la aplicación colapsaba completamente (`UnicodeEncodeError: 'utf-8' codec can't encode characters... surrogates not allowed`). Esto se debía a que la terminal estricta de Windows fallaba masivamente al intentar decodificar y dibujar "lonely surrogates" (caracteres Unicode corruptos o mitades de emojis) insertados dinámicamente o codificados en el script mediante la librería `rich`.
2. **Fix de Entorno (Config Global):** Se forzó a la Terminal de Consola y a `Rich` a renderizar un UTF-8 a prueba de fallas. Se agregó `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` en `dashboard.py` y se inicializó la `Console(force_terminal=True, legacy_windows=False)`.
3. **Fix de Render (Capa UI):** Se inyectó una función higienizadora `_safe(text)` en `menu_gestionar()`. Cada texto extraído de la BD para la Tabla ahora pasa por `.encode('utf-8', 'replace').decode('utf-8')` antes de chocar con `table.add_row()`. Además, se eliminó un emoji codificado como un literal problemático (`\ud83d\uddc2\ufe0f`) sustituyéndolo por su literal visual 🗂️.
4. **Fix Preventivo de Ingesta (Capa DB):** A nivel del CORE (`core/database.py`), interceptamos `NexusCRUD.create_registry` y `add_tag`. Todo string crudo entrante (`title`, `content_raw`, `summary`, `tag.value`) ahora se somete al embudo sanitizador `sanitize_db_string` previniendo a futuro que se guarde texto alienígena injertado por web scraping sucio o nombres de archivo defectuosos de C:/.
