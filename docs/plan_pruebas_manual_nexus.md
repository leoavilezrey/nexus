# 📋 Plan de Pruebas Manual — Nexus Dashboard

**Fecha**: ___/___/2026 &nbsp;&nbsp; **Tester**: _________________ &nbsp;&nbsp; **Versión**: Post-Corrección v2

**Cómo ejecutar**: `.\venv\Scripts\python.exe main.py`

---

## PASO 0 — Arranque

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 0.1 | Ejecutar `main.py`                        |            |                  |             |
| 0.2 | Se muestra banner "NEXUS"                 |            |                  |             |
| 0.3 | Panel de estadísticas visible             |            |                  |             |
| 0.4 | Grilla de 6 paneles de menú visible       |            |                  |             |
| 0.5 | Barra de comandos rápidos visible         |            |                  |             |

---

## MENÚ 1 — AGREGAR

> Presionar **1** desde el menú principal

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 1.0 | Entra al submenú Agregar                  |            |                  |             |
| 1.1 | Muestra opciones (1,2,3,4,6,S,0)         |            |                  |             |
| 1.2 | Destino dice "CORE (Local SSD)"          |            |                  |             |

### 1.1 — Añadir Archivo Local

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 1.1.1 | Presionar **1**, pide ruta              |            |                  |             |
| 1.1.2 | Ingresar ruta válida                    |            |                  |             |
| 1.1.3 | Ingresar tags: `test, prueba`           |            |                  |             |
| 1.1.4 | Muestra "✅ Archivo indexado"           |            |                  |             |
| 1.1.5 | Panel de detalles visible               |            |                  |             |
| 1.1.6 | Vista previa del contenido              |            |                  |             |
| 1.1.7 | Preguntan editar → resp. **n**          |            |                  |             |
| 1.1.8 | Elegir **2** (volver a ingesta)         |            |                  |             |
| 1.1.9 | Repetir con ruta **inválida**           |            |                  |             |
| 1.1.10| Error controlado, sin crash             |            |                  |             |

### 1.2 — Añadir URL (Web/YouTube)

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 1.2.1 | Presionar **2**, pide URL               |            |                  |             |
| 1.2.2 | Ingresar URL web genérica               |            |                  |             |
| 1.2.3 | Ingresar tags: `web, test`              |            |                  |             |
| 1.2.4 | Spinner "Descargando..." visible        |            |                  |             |
| 1.2.5 | Resultado ✅ o mensaje de fallo         |            |                  |             |
| 1.2.6 | Panel con contenido extraído            |            |                  |             |
| 1.2.7 | Elegir **2** para volver                |            |                  |             |
| 1.2.8 | Probar con URL de **YouTube**           |            |                  |             |
| 1.2.9 | Transcripción extraída                  |            |                  |             |
| 1.2.10| Elegir **2** para volver                |            |                  |             |

### 1.3 — Escribir Nota Libre

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 1.3.1 | Presionar **3**, pide título            |            |                  |             |
| 1.3.2 | Título: `Nota de Prueba`               |            |                  |             |
| 1.3.3 | Tags: `prueba, manual`                  |            |                  |             |
| 1.3.4 | Se abre Bloc de notas                   |            |                  |             |
| 1.3.5 | Escribir algo, guardar y cerrar         |            |                  |             |
| 1.3.6 | Muestra "✅ Nota almacenada"           |            |                  |             |
| 1.3.7 | Panel con contenido visible             |            |                  |             |
| 1.3.8 | Elegir **2** para volver                |            |                  |             |
| 1.3.9 | Repetir: cerrar bloc SIN escribir       |            |                  |             |
| 1.3.10| Muestra "Nota vacía. Abortando"         |            |                  |             |

### 1.4 — Añadir App / Herramienta

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 1.4.1 | Presionar **4**, pide nombre            |            |                  |             |
| 1.4.2 | Nombre: `VS Code`                      |            |                  |             |
| 1.4.3 | Ruta/Comando: `code`                   |            |                  |             |
| 1.4.4 | Plataforma: `PC`                       |            |                  |             |
| 1.4.5 | Requiere logueo: `n`                   |            |                  |             |
| 1.4.6 | Descripción: `Editor principal`        |            |                  |             |
| 1.4.7 | Tags: `herramienta, dev`               |            |                  |             |
| 1.4.8 | Muestra "✅ App registrada"            |            |                  |             |
| 1.4.9 | Elegir **2** para volver                |            |                  |             |

### 1.6 — Pipeline YouTube

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 1.6.1 | Presionar **6**, inicia pipeline        |            |                  |             |
| 1.6.2 | Se ejecuta sin crash                    |            |                  |             |
| 1.6.3 | Muestra "Enter para continuar"          |            |                  |             |

### 1.S — Cambiar Destino

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 1.S.1 | Presionar **S** → cambia a Buffer      |            |                  |             |
| 1.S.2 | Muestra "STAGING Activado"              |            |                  |             |
| 1.S.3 | Presionar **S** → vuelve a CORE        |            |                  |             |
| 1.S.4 | Muestra "CORE reactivado"              |            |                  |             |

### 1.0 — Volver

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 1.0.1 | Presionar **0** → menú principal        |            |                  |             |

---

## MENÚ 2 — GESTIONAR (Explorador)

> Presionar **2** desde el menú principal

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 2.0 | Entra al Explorador Maestro               |            |                  |             |
| 2.1 | Tabla con: ID, Tipo, Título, Tags, FC     |            |                  |             |
| 2.2 | Presionar **→** → siguiente página        |            |                  |             |
| 2.3 | Presionar **←** → página anterior         |            |                  |             |

### 2.F — Filtros

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 2.F.1 | Presionar **Q** → filtro rápido         |            |                  |             |
| 2.F.2 | Escribir: `python` → filtra nombre      |            |                  |             |
| 2.F.3 | Tabla filtrada correctamente             |            |                  |             |
| 2.F.4 | Presionar **L** → limpiar filtros        |            |                  |             |
| 2.F.5 | **Q** → `t:YouTube_Pipeline`            |            |                  |             |
| 2.F.6 | Filtra por tag correctamente             |            |                  |             |
| 2.F.7 | **L** → limpiar                          |            |                  |             |
| 2.F.8 | **Q** → `e:pdf`                          |            |                  |             |
| 2.F.9 | Filtra por extensión                     |            |                  |             |
| 2.F.10| **L** → limpiar                          |            |                  |             |
| 2.F.11| **Q** → `i:1-10`                         |            |                  |             |
| 2.F.12| Muestra solo IDs 1-10                    |            |                  |             |
| 2.F.13| **L** → limpiar definitivo               |            |                  |             |

### 2.D — Vista Detallada

| #      | Acción a realizar                      | ¿Funciona? | Mensaje de Error | Comentarios |
|:------:|----------------------------------------|:----------:|------------------|-------------|
| 2.D.1  | Escribir un **ID** → Enter             |            |                  |             |
| 2.D.2  | Panel detalle completo visible         |            |                  |             |
| 2.D.3  | **e** → menú edición de campo          |            |                  |             |
| 2.D.4  | Editar un campo (ej. tags)             |            |                  |             |
| 2.D.5  | **sum** → generar resumen IA           |            |                  |             |
| 2.D.6  | Resumen generado o fallback            |            |                  |             |
| 2.D.7  | **fc** → generar flashcards IA         |            |                  |             |
| 2.D.8  | Flashcards generadas o mockup          |            |                  |             |
| 2.D.9  | **fc+** → flashcard manual             |            |                  |             |
| 2.D.10 | Ingresar pregunta y respuesta          |            |                  |             |
| 2.D.11 | "Flashcard creada" confirmado          |            |                  |             |
| 2.D.12 | **ver fc** → lista de flashcards       |            |                  |             |
| 2.D.13 | Flashcards visibles en tabla           |            |                  |             |
| 2.D.14 | **links** → conexiones neuronales      |            |                  |             |
| 2.D.15 | **abrir** → abre recurso original      |            |                  |             |
| 2.D.16 | Recurso abierto en sistema             |            |                  |             |
| 2.D.17 | **p** → volver a lista                 |            |                  |             |

### 2.X — Eliminar Registro

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 2.X.1 | `del [ID de prueba]`                    |            |                  |             |
| 2.X.2 | Confirmación de eliminación             |            |                  |             |
| 2.X.3 | Registro eliminado correctamente        |            |                  |             |

### 2.V — Vincular Registros

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 2.V.1 | `m [ID1] [ID2]` → vincular             |            |                  |             |
| 2.V.2 | Vínculo creado exitosamente             |            |                  |             |
| 2.V.3 | **0** → volver al menú principal        |            |                  |             |

---

## MENÚ 3 — ACTIVE RECALL

> Presionar **3** desde el menú principal

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 3.0 | Entra a Active Recall                     |            |                  |             |
| 3.1 | Panel "Motor Pomodoro Listo" visible      |            |                  |             |
| 3.2 | Tabla de fuentes con cards pendientes     |            |                  |             |

### 3.N — Navegación y Filtros

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 3.N.1 | **→** → siguiente página                |            |                  |             |
| 3.N.2 | **←** → página anterior                 |            |                  |             |
| 3.N.3 | **Q** → filtro inteligente               |            |                  |             |
| 3.N.4 | Escribir: `s:y` → solo con FC           |            |                  |             |
| 3.N.5 | **L** → limpiar filtros                  |            |                  |             |

### 3.P — Sesión Pomodoro

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 3.P.1 | **pm** → inicia Pomodoro 25min          |            |                  |             |
| 3.P.2 | Primera pregunta visible                |            |                  |             |
| 3.P.3 | Enter → muestra respuesta               |            |                  |             |
| 3.P.4 | Calificar (1-4) → actualiza SRS         |            |                  |             |
| 3.P.5 | Avanza a siguiente pregunta             |            |                  |             |
| 3.P.6 | **q** o **0** → terminar sesión         |            |                  |             |
| 3.P.7 | Resumen final de la sesión              |            |                  |             |

### 3.A — Adelantar Repasos

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 3.A.1 | **pa** → menú adelantar                 |            |                  |             |
| 3.A.2 | Configurar filtros y cantidad            |            |                  |             |
| 3.A.3 | Sesión inicia con cards elegidas         |            |                  |             |
| 3.A.4 | Salir y volver                           |            |                  |             |

### 3.G — Generar Flashcards

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 3.G.1 | `ia [ID]` → flashcards con IA           |            |                  |             |
| 3.G.2 | Genera o muestra mockup                  |            |                  |             |
| 3.G.3 | `man [ID]` → flashcard manual            |            |                  |             |
| 3.G.4 | Solicita pregunta y respuesta            |            |                  |             |

### 3.D — Eliminar Flashcards

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 3.D.1 | `del [ID flashcard]` → eliminar         |            |                  |             |
| 3.D.2 | Confirmación y eliminación               |            |                  |             |
| 3.0.1 | **0** → volver al menú principal         |            |                  |             |

---

## MENÚ 4 — ESTADÍSTICAS

> Presionar **4** desde el menú principal

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 4.0 | Entra a Estadísticas                      |            |                  |             |
| 4.1 | Panel 4.1: Composición del Cerebro        |            |                  |             |
| 4.2 | Panel 4.2: Red Neuronal                   |            |                  |             |
| 4.3 | Panel 4.3: Madurez Cognitiva SRS          |            |                  |             |

### 4.G — Sincronizar Google Drive

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 4.G.1 | **G** → inicia exportación              |            |                  |             |
| 4.G.2 | Spinner "Copiando BD..." visible         |            |                  |             |
| 4.G.3 | Resultado ✅ o ❌ con mensaje            |            |                  |             |
| 4.G.4 | Enter para continuar                     |            |                  |             |

### 4.S — Filtrar por Área/Tag

| #     | Acción a realizar                       | ¿Funciona? | Mensaje de Error | Comentarios |
|:-----:|-----------------------------------------|:----------:|------------------|-------------|
| 4.S.1 | **S** → solicita filtro                 |            |                  |             |
| 4.S.2 | Ingresar tag (ej. `youtube`)            |            |                  |             |
| 4.S.3 | Estadísticas actualizadas               |            |                  |             |
| 4.S.4 | **S** → Enter vacío → limpiar           |            |                  |             |
| 4.0.1 | **Enter** → menú principal              |            |                  |             |

---

## MENÚ 5 — SALIR

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 5.1 | Escribir **5** → cierre limpio           |            |                  |             |
| 5.2 | Mensaje "Cerrando módulos..."             |            |                  |             |
| 5.3 | Terminal libre, sin errores               |            |                  |             |

---

## OMNIBAR — Búsqueda Directa

> Reiniciar: `.\venv\Scripts\python.exe main.py`

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 6.1 | Escribir `python` en menú principal       |            |                  |             |
| 6.2 | "Saltando al Gestor con 'python'"         |            |                  |             |
| 6.3 | Gestor muestra resultados filtrados       |            |                  |             |
| 6.4 | **0** → volver al menú principal          |            |                  |             |
| 6.5 | Escribir `:invalido`                      |            |                  |             |
| 6.6 | "Comando desconocido" en amarillo         |            |                  |             |

---

## CTRL+C — Interrupción Segura

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 7.1 | **Ctrl+C** en cualquier menú              |            |                  |             |
| 7.2 | "Interrupción detectada. Saliendo..."     |            |                  |             |
| 7.3 | Terminal limpia, sin traceback            |            |                  |             |

---

## LIMPIEZA POST-PRUEBA

| #   | Acción a realizar                         | ¿Funciona? | Mensaje de Error | Comentarios |
|:---:|-------------------------------------------|:----------:|------------------|-------------|
| 8.1 | Menú 2 → buscar registros de prueba      |            |                  |             |
| 8.2 | `del [IDs]` → eliminar los de prueba     |            |                  |             |
| 8.3 | Buscar de nuevo → ya no aparecen         |            |                  |             |

---

## RESUMEN GENERAL

| Sección              | Items | Pasaron | Fallaron |
|----------------------|:-----:|:-------:|:--------:|
| 0. Arranque          |   5   |         |          |
| 1. Agregar           |  30   |         |          |
| 2. Gestionar         |  22   |         |          |
| 3. Active Recall     |  22   |         |          |
| 4. Estadísticas      |  10   |         |          |
| 5. Salir             |   3   |         |          |
| 6. Omnibar           |   6   |         |          |
| 7. Ctrl+C            |   3   |         |          |
| 8. Limpieza          |   3   |         |          |
| **TOTAL**            |**104**|         |          |

**Observaciones Finales**:

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________

**Firma**: _________________ &nbsp;&nbsp; **Fecha**: _________________
