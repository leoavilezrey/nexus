# Análisis de Evolución Frontend: Nexus Hybrid

**Fecha:** 2026-02-25
**Estatus:** Decisión Tomada - Priorización de TUI (Opción A)

## 1. Contexto y Requerimiento
El sistema Nexus requiere una interfaz que sea:
1. **Funcional al 100%:** Todas las capacidades de IA, Red Neuronal y Active Recall disponibles.
2. **Bajo Consumo de Recursos:** Minimizar el uso de RAM y CPU (específicamente evitar el consumo de navegadores modernos).
3. **Eficiencia Operativa:** Velocidad de respuesta instantánea.

## 2. Análisis de Alternativas

| Opción | Tecnología | Ventajas | Desventajas |
| :--- | :--- | :--- | :--- |
| **A. TUI (Terminal)** | Python + Rich / Textual | Consumo casi nulo, velocidad máxima, integración directa con el Core. | Limitación gráfica para contenido multimedia complejo. |
| **B. Web Ligera** | HTMX + Tailwind | Acceso desde cualquier dispositivo, muy ligera para el navegador. | Requiere servidor activo (Uvicorn) y navegador abierto. |
| **C. Desktop App** | Flet / PySide | Experiencia de usuario estándar, acceso a archivos locales nativo. | Mayor peso en el ejecutable y consumo de recursos medios. |

## 3. Decisión: Optimización de TUI (Opción A)
Se ha decidido despriorizar la interfaz Web moderna en favor de la **Terminal User Interface (TUI)**. 

### Justificación:
- Nexus es un "Cerebro Digital" enfocado en la productividad y el estudio. La terminal permite una interacción vía teclado que supera en velocidad a cualquier interfaz de mouse.
- Eliminación total de la dependencia de motores de renderizado web pesados (Chromium/V8).
- Mantenimiento simplificado: la lógica de negocio y la UI residen en el mismo entorno de ejecución.

## 4. Roadmaps de Mejora para la TUI
1. **Refactorización de Flujos:** Hacer los menús aún más ágiles con atajos de una sola tecla (Hotkeys).
2. **Visualización de Contenido:** Mejorar cómo se muestran los extractos de texto largos sin saturar el buffer de la terminal.
3. **Integración de Comandos Rápidos:** Implementar una "Línea de Comandos" global (tipo Omnibar) dentro de la TUI.

---
*Documento generado por Antigravity como referencia para futuros cambios de arquitectura.*
