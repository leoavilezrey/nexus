# N E X U S ✦ Cognitive Storage & Active Recall Console

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![Database](https://img.shields.io/badge/Database-SQLite3_WAL-green)
![License](https://img.shields.io/badge/License-MIT-purple)

**Nexus** es un Sistema Operativo Cognitivo de terminal. Nació como respuesta a la fragmentación de la información: una plataforma unificada donde los archivos de tu disco duro, tus enlaces de YouTube, y tus notas reflexivas internas no solo coexisten mediante etiquetas universales (Gestor PKM), sino que son consumidos y entrelazados activamente mediante Inteligencia Artificial y un sistema exigente de *Spaced Repetition* (SRS).

No es para guardar datos temporalmente; **es para integrarlos en tu memoria a largo plazo.**

---

## 🔥 Características de la V1.0 Core

### 1. Unified Súper Schema
Usa `SQLAlchemy` como ORM para mapear cualquier objeto del mundo real hacia un `ResourceRecord` rígido pre-aprobado por `Pydantic`. Nexus jamás inyecta archivos binarios `.mp4` o `.pdf` enteros para evitar corromper la BD; intercepta rutas cruzables `.as_posix()` y lee los primeros 5000 chars si el documento es nativamente de texto plano como `.txt` o `.md` .

### 2. Motor de Relación Excluyente (Gemini IA)
El cerebro interno (Google GenAI API). Puedes forzar un vínculo mediante Inteligencia Artificial enviándole a la IA dos registros de conceptos del disco. En lugar de darte resúmenes aburridos, **el Agente de Relación aplica Pedagogía de Discriminación** forzando el Match: diseña tarjetas de validación que te exijan diferenciar entre ambos conceptos (Ej. *"A diferencia de VirtualBox que hace X, ¿cuál de los dos hace Y?"*). 

### 3. Active Recall y Rescate Contextual
Las Sesiones de Estudio de Nexus rompen la caja negra:
- Las tarjetas están atadas al `id` del material. 
- Durante la sesión (`Pomodoro` o `Standard`), si no recuerdas un concepto, oprimes la tecla **`f`**: si es un archivo se abrirá el Explorador de Windows y te lo iluminará nativamente en azul; si es un link, abrirá Chrome; si es nota PKM, la expulsará formateada en la misma terminal para tu revisión sin salir del entorno.
- Tus fechas de SRS (`next_review`) se evalúan como *Difícil/Bien/Fácil*.

---

## 🛠️ Instalación y Requisitos Previos

- **Python 3.10+** (Recomendado).
- Una **Google API KEY** de Gemini (Models 1.5 y 2.0).

1. **Clona el repositorio** e ingresa en él:
   ```bash
   git clone https://github.com/TU-USUARIO/nexus.git
   cd nexus
   ```

2. **Crea y Activa un Entorno Virtual** local:
   ```bash
   # En Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instala las dependencias principales** obligatorias (Rich, Pydantic, SQLAlchemy, GenAI):
   ```bash
   pip install -r requirements.txt
   ```

4. **Variables de Entorno**:
   Setea temporalmente o dentro de tu equipo global la variable con la llave de acceso a Google:
   * **CMD Windows**: `set GOOGLE_API_KEY=AIzaSy...Tu_Llave_Aqui`
   * **PowerShell**: `$env:GOOGLE_API_KEY="AIzaSy...Tu_Llave_Aqui"`

---

## 📈 Evolución y Herencia

Nexus no empezó en el vacío. Representa la culminación de un proceso de consolidación de datos:
1.  **Versión Legacy**: Basada en `files.db` (gestión de archivos simple) y `ar_console.db` (estudio aislado).
2.  **Migración Maestra (V2.0)**: Ejecutada para unificar 20,000+ registros, reconstruir relaciones mediante `NexusLinks` y rescatar el historial de aprendizaje SRS.
3.  **Estado Actual**: Sistema unificado de grafo neuronal con agentes de IA integrados para la generación y mutación de contenido.

Este proyecto ha sido desarrollado en un entorno de **colaboración avanzada entre Humano y AI (Antigravity)**, demostrando el potencial de la programación asistida para la creación de arquitecturas de software complejas y migraciones de datos de alta integridad.

---

## 🚀 Cómo Iniciar Nexus

El sistema está optimizado para funcionar bajo un punto de entrada inquebrantable (`main.py`), lo que garantiza que las tablas SQLite se compilen con el protocolo WAL (`Write-Ahead Logging`) antes de que veas el primer pixel de luz del menú TUI. 

Ejecútalo estando en la carpeta raíz:
```bash
python main.py
```

*Nota: Al correrlo por primera vez, autogenerará el fichero `nexus.db` donde residirá la red inmaculada de conocimiento de aquí al futuro. Este DB no requiere mantenimiento humano. Módulo UI de Rich preparado para soportar `Charmaps CP-1252` o renderizado UTF-8 en PowerShell nativo de Windows.*
