# Nexus: Manual Maestro de Estrategia y Operaciones v1.0

Este documento consolida las lecciones aprendidas durante la transición al Súper Schema de Nexus y define los pilares para transformar la gestión de archivos en una Red Neuronal de Conocimiento.

## 🧠 1. El Gran Cambio: De "Contenedores" a "Contenido"

Nexus no es un explorador de archivos; es un sistema de digestión de información.
*   **La Regla de Oro**: Un registro sin `content_raw` (descripción o texto base) es "ruido". El valor de Nexus crece proporcionalmente a la densidad de texto en sus registros.
*   **Prioridad de Ingesta**: No indices todo tu disco duro. Ingesta solo aquello que merezca ser recordado (Active Recall).
*   **Fuentes de Texto**: Nexus extrae automáticamente texto de archivos `.txt`, `.md`, `.py` y transcripciones de YouTube. Para otros archivos, usa el comando `e [ID]` para pegar un resumen manual.

## 🎥 2. Gestión Inteligente de Multimedia (YouTube y Nube)

Tras la migración de los 200+ registros de caché JSON, el sistema ahora distingue entre un enlace muerto y un **Recurso Activo**.
*   **Clasificación `youtube`**: Estos registros permiten al Agente de Estudio interactuar con la API de transcripciones.
*   **Reclasificación Operativa**: Si un video se importa erróneamente como `file`, el script de migración ahora lo detecta, lo corrige a `youtube` y le asigna etiquetas de `video` automáticamente.
*   **Metadatos de Seguimiento**: Los campos `id_legacy` y `original_cache` preservan el linaje de tus datos antiguos, permitiendo auditorías de duplicados.

## 🕸️ 3. Construcción de la Red Neuronal (NexusLinks)

El conocimiento no es lineal, es relacional.
*   **Vínculos Migrados**: Se han recuperado las "notas de relación" históricas. Úsalas como ejemplo para conectar nuevos recursos.
*   **Estrategia de Conexión**: Vincula siempre una **Nota Teórica** (`note`) con su **Fuente de Evidencia** (`file` o `youtube`). Esto permite que, al repasar la teoría, Nexus te ofrezca abrir el material original instantáneamente.

## 🎓 4. El Ciclo de Dominio (Active Recall & SRS)

Nexus protege tu memoria contra la curva del olvido y la habituación.
*   **Mutación contra la Memoria Muscular**: El **Agente Mutador** reformula tus tarjetas periódicamente. Si sientes que respondes por "eco" y no por comprensión, fuerza una mutación.
*   **Calificación SRS Honesta**: Usa `[1] Malo`, `[2] Bueno`, `[3] Fácil`. El sistema ahora muestra colores para evitar confusiones al calificar.
*   **Nivel Universitario**: Las tarjetas generadas por IA están configuradas con complejidad media-alta y parafraseo radical para evitar la repetición literal.

## 🛠️ 5. Recordatorios Técnicos para el Constructor

*   **Integridad de Datos**: Al añadir etiquetas programáticamente, usa siempre una verificación de existencia previa para evitar errores de tipo `UNIQUE constraint failed`.
*   **UTF-8 en Windows**: Para evitar errores de renderizado de Emojis en la terminal, los scripts deben forzar la reconfiguración de `sys.stdout` a UTF-8.
*   **Exclusión de Notas Virtuales**: Durante las migraciones, las notas temporales o "virtuales" deben ser filtradas por nombre (`title.lower()`) para mantener limpia la base de conocimiento real.

---
*Documento registrado en la Base de Datos Maestro de Nexus.*
