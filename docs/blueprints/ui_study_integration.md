# Blueprint: Integración de Conectar (UI) y Motor de Estudio
Ubicación: `nexus/ui/dashboard.py` y `nexus/modules/study_engine.py`

## 1. Conectar (Opción 4 del Dashboard)
Cuando el usuario elija "CONECTAR", el sistema debe:
1. Abrir un submenú simple: "1. Crear Vínculo Manual | 2. IA Match (Auto-Tarjetas)".
2. En la Opción 2:
   - Pedir ID o Buscar el Registro A.
   - Pedir ID o Buscar el Registro B.
   - Llamar a `relationship_agent.generate_relationship_cards()`.
   - Mostrar un spinner o mensaje de "Cerebro pensando..."
   - Al recibir las tarjetas, insertarlas en la BD (`cards` y `nexus_links` para registrar la sinergia) y decirle al usuario cuántas se crearon en verde.

## 2. Active Recall (Opción 3 del Dashboard)
Cuando el usuario elija "ACTIVE RECALL":
1. Crear un archivo corto en `nexus/modules/study_engine.py` (si no existe) que contenga la lógica para "obtener tarjetas pendientes". (Tarjetas cuya fecha `next_review` sea menor o igual a HOY, o que nunca se hayan repasado).
2. Preguntar: "¿Modo Standard o Pomodoro 25min?".
3. **Flujo de Tarjeta (UX)**:
   - Mostrar la "Pregunta" en panel Azul.
   - Mostrar un prompt `[Enter para ver Respuesta | f para ver material fuente]`.
   - Si presiona `f`, abrir contexto. Si Enter, mostrar Respuesta en panel Verde.
   - Preguntar botón de retención SRS: `[1] Difícil [2] Bien [3] Fácil`.
4. Actualizar las fechas de la tarjeta en BD simulando el avance y volver al Panel General al terminar.

## Instrucción para el Constructor:
- Desarrollar este nudo final importando el nuevo agente en tu UI.
- Crear la mínima lógica SRS/Pomodoro posible en el módulo de estudio para que fluya con naturalidad la recolección y revisión de cartas.
- ¡Mantén el `console.clear()` pulcro al navegar esto!
