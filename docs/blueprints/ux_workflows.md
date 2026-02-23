# Blueprint: Flujos de Usuario (UX Workflows)
Ubicación sugerida: `nexus/modules/` y lógica de UI.

Este documento formaliza las decisiones de diseño sobre cómo el usuario interactúa con Nexus, priorizando el control manual y el ahorro de tokens de IA.

## 1. Sistema de Ingesta (Entrada de Datos)
**Decisión:** Un menú estricto, explícito y sin "adivinanzas" de la IA para ahorrar tokens.
- La IA SOLO se usará cuando el usuario pida explícitamente analizar algo complejo (como generar tarjetas).
- El menú de ingesta debe preguntar qué tipo de recurso se va a añadir:
  1. Añadir Archivo (Local)
  2. Añadir URL (Web/YouTube)
  3. Añadir Aplicación / Herramienta
- La extracción de datos básicos (peso, extensión, título de web) se hará mediante scraping clásico o librerías estándar de Python, reservando Gemini solo para la generación de tarjetas de estudio.

## 2. Repaso Contextual (Contextual Review)
**Decisión:** Experiencia inmersiva abriendo las fuentes originales.
- Durante una sesión de estudio (Pomodoro/Standard), si el usuario pide repasar la fuente original de una tarjeta:
  - **Si es YouTube/URL:** El sistema ejecutará un comando para abrir el enlace directamente en el navegador web predeterminado (ej. usando el módulo `webbrowser` de Python).
  - **Si es Documento Local (PDF/Docx):** Se abrirá en su visor predeterminado o se mostrará la carpeta en el explorador de Windows, tal y como se diseñó en el buscador.
  - **Si es Nota (.md):** Se leerá y mostrará rápidamente en la terminal, o se abrirá en el editor.

## 3. Gestor de Notas (Nexus-PKM)
**Decisión:** Usar el editor favorito del usuario (Notepad / Notepad++ / VSCode).
- Cuando el usuario decida "Crear Nota" o "Editar Nota", Nexus NO intentará emular un editor de texto en la terminal.
- **Flujo técnico:**
  1. Nexus genera un archivo `.md` temporal.
  2. Lanza un subproceso llamando al editor del sistema operativo (por ejemplo, usando `os.startfile()` o `subprocess.run(['notepad', temp_path])`).
  3. La terminal de Nexus entra en modo de espera.
  4. Cuando el usuario cierra el editor, Nexus intercepta el guardado, lee el archivo `.md` temporal, lo inserta en `nexus.db` (en `registry`) y lo borra del almacenamiento temporal (o lo mueve a una carpeta formal de notas).

## Instrucción para el Constructor:
- Aplicar el módulo `webbrowser` para el repaso de YouTube.
- Utilizar rutinas como `subprocess` para el manejo del sistema de notas y apertura de editores externos.
- Mantener la separación de responsabilidades: los Agentes (IA) NO se meterán en la gestión de guardado de archivos, solo procesan texto cuando se les solicita explícitamente.
