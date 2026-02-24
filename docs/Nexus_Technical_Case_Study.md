# Nexus: De Fragmentos a una Red Neuronal (Technical Case Study)

## 📌 Resumen del Proyecto
**Nexus** es un Sistema Operativo Cognitivo (Cognitive OS) basado en terminal, diseñado para unificar la gestión de archivos locales, marcadores web y notas personales en un grafo de conocimiento activo. A diferencia de un gestor de archivos tradicional, Nexus transforma cada dato en un recurso de aprendizaje mediante Inteligencia Artificial y Repetición Espaciada (SRS).

## 🚀 El Desafío: El Problema de la Fragmentación
Antes de Nexus, la información del usuario residía en dos sistemas aislados:
1.  **Legacy Files DB**: Una base de datos SQLite con miles de registros de archivos y enlaces, pero sin contexto pedagógico.
2.  **AR-Console**: Un sistema de flashcards independiente con notas desconectadas de sus fuentes originales.

El objetivo fue realizar una **migración masiva y transformacional** hacia un "Súper Schema" único (`nexus.db`) capaz de soportar la interconexión de estos mundos.

## 🛠️ Proceso de Ingeniería y Evolución

### Fase 1: Ingeniería Reversa y Extracción (V1.0)
Se desarrollaron scripts de migración (`migracion_v1_0.py`) para mapear tipos de datos legados hacia modelos de datos estrictos validados con **Pydantic**. Se implementó **SQLAlchemy** para manejar las relaciones complejas entre los registros (`Registry`) y sus etiquetas (`Tag`).

### Fase 2: Reconstrucción del Grafo Neuronal (V2.0)
Este fue el punto crítico del proyecto. No bastaba con mover datos; era necesario reconstruir las relaciones.
*   **NexusLinks**: Se creó un puente de mapeo de IDs para recrear vínculos entre notas y archivos que se habían perdido en sistemas anteriores.
*   **Ingesta Multimedia**: Se integraron módulos de scraping (`web_scraper.py`) para extraer transcripciones de YouTube y contenido de páginas web, transformando URLs estáticas en fuentes de texto vivo para la IA.

### Fase 3: Integración de IA y Active Recall
Se implementaron agentes especializados:
*   **Agente de Estudio**: Destila el contenido crudo (`content_raw`) para generar flashcards automáticamente usando la API de **Google Gemini**.
*   **Agente de Mutación**: Parafrasea radicalmente las tarjetas existentes para combatir la memoria muscular y asegurar el aprendizaje conceptual.

## 🤝 Colaboración Humano-IA
Este proyecto es el resultado de un trabajo intensivo en pareja (**Pair Programming**) entre el **Usuario** y el asistente **Antigravity (AI)**. 
*   **Usuario**: Lideró la visión estratégica, definió los requisitos de negocio y supervisó la integridad de la base de datos histórica.
*   **AI (Antigravity)**: Ejecutó la implementación técnica, resolvió conflictos de codificación (UTF-8/charmap), optimizó las consultas SQL y diseñó la arquitectura del motor pedagógico.

## 📊 Resultados Actuales
*   **Unicidad**: 20,000+ registros unificados en un solo grafo.
*   **Multimedia**: 200+ videos de YouTube convertidos en recursos de estudio activos.
*   **Aprendizaje**: Sistema SRS totalmente funcional con persistencia de historial de dificultad y estabilidad.

## 🧪 Stack Tecnológico
*   **Lenguaje**: Python 3.10+
*   **Persistencia**: SQLite (WAL Mode) / SQLAlchemy ORM.
*   **Validación**: Pydantic V2.
*   **Interfaz**: Rich (TUI - Terminal User Interface).
*   **IA**: Google GenAI (Gemini 2.0/1.5).

---
*Este documento técnico sirve como testimonio de un flujo de trabajo moderno de desarrollo asistido por IA, priorizando la arquitectura limpia y la migración de datos de alta fidelidad.*
