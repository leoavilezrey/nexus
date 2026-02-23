# Blueprint: Súper Schema de Base de Datos - Nexus

Diseño de base de datos unificada para eliminar la fragmentación entre archivos y estudio.

## Tabla 1: `registry` (El Corazón)
Almacena CUALQUIER tipo de recurso indexado.
*   `id`: INTEGER PRIMARY KEY
*   `type`: TEXT (file, youtube, note, concept, app, account)
*   `title`: TEXT (Nombre del archivo, título del video o de la nota)
*   `path_url`: TEXT (Ruta física en el disco local o URL externa. NUNCA se almacenan binarios.)
*   `content_raw`: TEXT (Contenido extraído de texto, transcripción de youtube o cuerpo de la nota PKM)
*   `metadata`: JSON (Dict para campos específicos como extension, duration, username, etc.)
*   `created_at`: DATETIME
*   `modified_at`: DATETIME

## Tabla 2: `tags`
*   `registry_id`: INTEGER (FK registry.id)
*   `value`: TEXT (La etiqueta)
*   PRIMARY KEY (registry_id, value)

## Tabla 3: `nexus_links` (Grafos de Relación)
Conecta cualquier par de registros.
*   `id`: INTEGER PRIMARY KEY
*   `source_id`: INTEGER (FK registry.id)
*   `target_id`: INTEGER (FK registry.id)
*   `relation_type`: TEXT (ej: "complementa", "referencia", "comparar")
*   `description`: TEXT (Notas sobre la relación)

## Tabla 4: `cards` (Sistema de Aprendizaje)
Preguntas asociadas a registros.
*   `id`: INTEGER PRIMARY KEY
*   `parent_id`: INTEGER (FK registry.id - De dónde salió la pregunta)
*   `question`: TEXT
*   `answer`: TEXT
*   `type`: TEXT (Factual, Conceptual, Relacional)
*   `difficulty`: FLOAT (Algoritmo SRS)
*   `stability`: FLOAT (Algoritmo SRS)
*   `last_review`: DATETIME
*   `next_review`: DATETIME

---
## Instrucción para el Constructor:
Implementar esta base de datos utilizando `Sqlite3` en modo `WAL`. Crear un módulo `nexus/core/database.py` que proporcione métodos CRUD básicos.
