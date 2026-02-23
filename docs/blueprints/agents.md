# Blueprint: Agentes de Inteligencia Artificial (Nexus Core Agents)
Ubicación sugerida: `nexus/agents/`

En Nexus, los agentes son módulos aislados que utilizan Google GenAI (Gemini) para transformar datos crudos en conocimiento. Se basarán fuertemente en prompts estructurados y usarán `Pydantic` para garantizar que devuelvan JSON válido.

## 1. El Agente de Relaciones (`nexus/agents/relationship_agent.py`)
Misión: Conectar el 'Registro A' con el 'Registro B' y extraer valor de aprendizaje.

### Directrices para el Prompteador (LLM):
- **Tono**: Pedagógico de universidad, directo.
- **Formato**: Devolver una lista de objetos `StudyCard` usando JSON estructurado.
- **Enfoque de Análisis (Match Forzado)**:
  La IA DEBE crear tarjetas que fuercen al usuario a distinguir claramente entre los dos conceptos proporcionados.
  - **Preguntas de Identificación**: Presentar una característica, ventaja o caso de uso, y preguntar a CUÁL de los dos conceptos pertenece. (Ej. "Frente a ti tienes Docker y Podman. ¿Cuál de los dos no requiere un demonio en segundo plano (rootless)?").
  - **Preguntas de Contraste Rápido**: Preguntar por la diferencia principal y excluyente entre el Concepto A y el Concepto B respecto a un tema específico.
  - Evitar preguntas genéricas o resúmenes; enfocarse en la discriminación cognitiva.

Manejar el fallback de modelos (usar `gemini-3-flash-preview` por defecto, bajar a versiones 1.5 si hay error).

## Instrucción para el Constructor:
Implementar la llamada a la API usando `google.genai` con el parámetro `response_schema` apuntando al modelo Pydantic de `StudyCard` para que el JSON siempre venga perfecto.
