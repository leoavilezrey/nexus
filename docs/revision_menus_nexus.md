# 🧠 Guía de Revisión de Menús y UX: Proyecto Nexus (v1.0)

Esta guía adapta la metodología de revisión sistemática al contexto de **Nexus** como un "Cognitive Operating System" basado en terminal (TUI). El objetivo es simplificar la navegación a medida que el sistema escala sus capacidades de IA.

---

## 1. Alcance y Preparación (Contexto Nexus)
**Objetivo:** Evaluar la eficiencia de flujo desde la captura de información hasta la generación de conocimiento.
**Fuentes de revisión:**
- `ui/dashboard.py`: Código maestro de la interfaz.
- Blueprints: `docs/blueprints/ux_workflows.md`.
- **Perfiles:** Usuario "Prosumer" (alto volumen de info) vs Usuario "Estudiante" (foco en SRS).

---

## 2. Dimensiones de Revisión (Adaptadas a TUI/Nexus)

### A. Arquitectura de la Información (IA) - *Agrupación Lógica*
- **Fatiga de Opciones:** ¿Superamos el límite de 7-9 opciones? (Ej: El panel de herramientas de registro ya tiene 9 opciones). 
- **Jerga Nexus:** ¿Términos como "Ingreso Strict", "SRS", "Graph Link" son claros o intimidantes?
- **Consistencia de Teclas:** ¿El '0' siempre vuelve atrás? ¿El 's' siempre es búsqueda?

### B. Estética y UX en Terminal (Rich Framework)
- **Jerarquía Visual:** ¿Los colores (Cyan para IDs, Magenta para IA, Verde para Éxito) ayudan a escanear la pantalla o saturan la vista?
- **Micro-interacciones:** ¿El spinner ('dots') oculta la carga de manera fluida o interrumpe prompts (como el bug de tokens corregido)?
- **Descubribilidad:** ¿Las funciones avanzadas (como la opción 8 de Resumen) están ocultas bajo demasiados niveles de profundidad?

### C. Funcionalidad y Agentes IA
- **Coste de Salida:** ¿El menú previene el gasto accidental de tokens (Confirmación de IA)?
- **Feedback del Sistema:** ¿Nexus comunica claramente el estado de la red neuronal (ej: "Buscando en Súper Schema...")?
- **Fallbacks:** Si la IA falla, ¿el menú permite reintentar o usar el "Safe Mode" sin romper el ciclo del programa?

### D. Microcopia (Copyrighting Técnico)
- **Verbos de Acción:** [1] Inyectar vs [1] Añadir. ¿Usamos un lenguaje que motive la acción?
- **Ayuda Contextual:** ¿Los "TIPS" en los menús de búsqueda son útiles o solo ocupan espacio?

---

## 3. Proceso Paso a Paso para Nexus

1.  **Auditoría de "Cero Clics":** ¿Cuántos pasos toma llegar a estudiar una tarjeta desde que abres la app? (Meta: < 3 pasos).
2.  **Prueba de Tarea Crítica:** Realizar el flujo: *Ingresar URL -> Generar Flashcards -> Revisar en Active Recall*.
3.  **Evaluación de "Menu Growth":** Analizar el menú de `_show_record_detail` (Opción 0-8). 
    - *Hipótesis:* ¿Debería dividirse en "Cerebro (IA)" y "Gestión (CRUD)"?
4.  **Simulación de Error:** Forzar un NameError o una API caída y ver si el menú "sobrevive" o explota.

---

## 4. Estrategia de Optimización (Backlog Nexus)

### Hallazgos Típicos a Resolver:
- **Agrupación de IA:** Mover funciones de "Generar (IA)" a un sub-menú dedicado llamado `[IA] Brain Tools`.
- **Simplificación del Explorador:** Reducir los 10 inputs de búsqueda a una sola línea mágica (Omnibar) si es posible.
- **Acceso Directo:** Implementar comandos rápidos desde cualquier menú (ej: `:q` para salir, `:s` para buscar).

---

## 5. Entregables Esperados
1.  **Refactor de `dashboard.py`**: Limpieza de menús saturados.
2.  **Mapa de Flujos**: Documento visual de cómo se conectan los sub-menús.
3.  **Checklist de validación**: Para cada nueva función que se añada a Nexus.
