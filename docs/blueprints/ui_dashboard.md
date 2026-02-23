# Blueprint: Dashboard unificado y Menús (UI/UX)
Ubicación sugerida: `nexus/ui/dashboard.py`

El motor de interfaz (UI) de Nexus usará tabulaciones limpias, paneles (usando la librería 'rich') y menús interactivos, consolidando todas las funciones del gestor antiguo con las de AR-Console.

## 1. El Dashboard Principal (Inicio de Nexus)
Al arrancar el sistema, el usuario no debe ver solo opciones, sino información clave de ambos mundos (Archivos y Estudio):

**[Panel de Estado Unificado]**
- 🗃️ Registro Total: [X] Archivos, [Y] Notas, [Z] Videos.
- 🧠 Active Recall: [A] Tarjetas Totales, [B] Listas para Repaso Hoy.
- 🔗 Red de Conocimiento: [C] Vínculos entre conceptos.

**[Menú Interactivo]**
1. ➕ **INGRESAR** (Escanear PC, Añadir Video, Escribir Nota Libre).
2. 🔍 **EXPLORADOR** (El buscador maestro con Inclusión/Exclusión para TODO el registro).
3. 🧠 **ACTIVE RECALL** (Iniciar Sesión Pomodoro o Repaso Rápido).
4. 🔗 **CONECTAR** (Crear relaciones manuales o correr el Motor de IA).
5. 📊 **ESTADÍSTICAS GLOBALES**.
0. ❌ Salir.

## 2. Unificación del Menú de Estadísticas (Opción 5)
El módulo de estadísticas (`nexus/ui/stats.py`) ahora debe ser una pantalla rica con dos columnas o un panel amplio:

**Sección A: Data Analytics (Antiguo Gestor)**
- Desglose por `type`: Cuántos PDF, DOCX, MP4, enlaces web.
- Top Tags más usados en toda la base de datos.
- Archivos sin procesar (Sin tags ni descripción).

**Sección B: Cognitive Analytics (Antiguo AR-Console)**
- Tasa de retención general (Algoritmo SRS).
- Gráfico/Listado de días de racha de estudio.
- Distribución de tarjetas por tipo (Concepto, Relación, Factual).

## Instrucción para el Constructor:
- Todas las salidas a consola deben usar `Console` de `rich`.
- Las pantallas no deben limpiarse usando `os.system("cls")` crudo si es posible evitarlo; usar los mecanismos propios de TUI o `console.clear()`.
- Crear el módulo `nexus/ui/menus.py` para la lógica de navegación.
