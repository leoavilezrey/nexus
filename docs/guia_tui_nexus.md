# Nexus TUI: Guía Rápida de Operaciones (v2.0)

**Propósito:** Centro de mando de alto rendimiento para el Cerebro Digital Nexus. Optimizado para velocidad y bajo consumo.

## 0. Cómo Iniciar Nexus (Primer Paso)
Para abrir tu centro de mando desde cualquier terminal (PowerShell o CMD):

1.  **Navega a la carpeta:** `cd C:\Users\DELL\Proyectos\nexus`
2.  **Ejecuta el comando:** `.\venv\Scripts\python.exe main.py`

*Tip: Puedes crear un acceso directo en tu escritorio que ejecute este comando para abrir Nexus con un solo click.*

## 1. El Omnibar Global (Dashboard Principal)
Desde el menú principal, el prompt `Nexus Command / Omnibar` acepta tres tipos de entrada:

| Tipo | Entrada | Acción |
| :--- | :--- | :--- |
| **Numérico** | `1` a `6` | Abre el menú correspondiente. |
| **Comando `:`** | `:i`, `:r`, `:m` | Salto instantáneo a Ingesta, Recall o Métricas. |
| **Búsqueda** | `término` | Abre el Explorador filtrando por ese nombre/título. |

## 2. Navegación Instantánea (Hotkeys)
En la **Vista de Detalle** de cualquier registro, no necesitas pulsar `Enter`. Solo toca la tecla:

*   `2`: **Abrir Fuente** (Lanza el PDF, Word, URL o Nota de una vez).
*   `3`: **Modo Lectura** (Interfaz limpia para estudiar el contenido).
*   `4`: **Cerebro IA** (Generar resúmenes o flashcards).
*   `5`: **Mazo** (Gestionar tarjetas).
*   `0`: **Volver** (Regresar al explorador).

## 3. Comandos del Explorador / Recall
Dentro de las listas de registros, puedes usar:

*   `v[ID]`: (ej. `v23794`) Ver detalles del registro.
*   `s`: Iniciar búsqueda avanzada (Omnibar interna).
*   `del [ID]`: Eliminar un registro.
*   `ia [ID]`: Generar tarjetas automáticas (solo en menú Active Recall).
*   `pm`: ¡Iniciar sesión de estudio Pomodoro!

## 4. Búsqueda Avanzada (Sintaxis Smart)
En cualquier barra de búsqueda puedes combinar:
*   `t:tag` -> Filtrar por etiqueta.
*   `e:pdf` -> Filtrar por extensión.
*   `-termino` -> Excluir registros que contengan esa palabra.

---
*Documento guardado en Nexus para consulta rápida.*
