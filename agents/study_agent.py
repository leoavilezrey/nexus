import os
import json
from typing import List

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[bold white on red]Librería 'google-genai' no encontrada. Verifica si se instaló correctamente.[/]")

from pydantic import TypeAdapter

from core.models import StudyCard
from core.database import Registry

def get_client():
    """Obtiene el cliente estandarizado GenAI agarrando GOOGLE_API_KEY local."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

def generate_deck_from_registry(record: Registry) -> List[StudyCard]:
    """
    Agente Pedagógico de Extracción.
    Genera tarjetas (StudyCard) mediante inteligencia artificial destilando el contenido de un solo registro.
    """
    client = get_client()

    if not client:
        # Mockup Funcional si no hay llave para evitar el Crash Masivo
        print("[yellow]\n[Mockup Mode] Simulación de IA en curso debido a ausencia de API KEY. Generando tarjeta de prueba...[/yellow]")
        return [
            StudyCard(
                parent_id=record.id,
                question=f"¿Cuál es el título o tema principal de este documento abstracto?",
                answer=f"{record.title}",
                card_type="Conceptual"
            )
        ]

    prompt = f"""
    Eres un profesor universitario de alto nivel, experto en pedagogía y Active Recall.
    Tu objetivo es leer el siguiente documento y extraer un mazo de Flashcards de ALTO RENDIMIENTO.

    --- Registro (ID: {record.id}) ---
    Título: {record.title}
    Info Cruda: {record.content_raw}
    Extra Metadatos: {record.meta_info}

    Reglas Mandatorias de Generación:
    1. NIVEL COGNITIVO: Mantén un nivel de complejidad Universitario Media-Alta. No hagas preguntas obvias; busca evaluar comprensión profunda y aplicación.
    2. PARAFRASEO: Nunca copies y pegues texto del documento. Reformula (parafrasea) las ideas para que el estudiante deba procesar el significado y no solo reconocer palabras.
    3. DIVERSIDAD DE FORMATOS: Utiliza una mezcla variada de los siguientes tipos en el campo 'card_type':
       - [Factual/Conceptual]: Preguntas directas o de desarrollo.
       - [Reversible]: Conceptos con definiciones claras.
       - [MCQ]: Opción múltiple (Almacena en 'question' como JSON: {{"prompt": "...", "options": {{"a": "...", "b": "..."}}}} y en 'answer' la letra).
       - [TF]: Verdadero o Falso. (Respuesta 'v' o 'f').
       - [Cloze]: Rellenar huecos usando la sintaxis: "La {{c1::palabra}} es {{c2::importante}}".
       - [Matching]: Emparejamiento (Almacenado como JSON de pares en 'question').
       - [MAQ]: Selección múltiple.
    4. CANTIDAD: Genera entre 3 y 7 tarjetas según la densidad de la información.
    5. REFERENCIA: Asigna 'parent_id' SIEMPRE a {record.id}.

    Retorna estrictamente un ARRAY de objetos JSON que sigan el esquema StudyCard proporcionado.
    """

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[StudyCard],
        temperature=0.3
    )

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            
            if response.text:
                json_data = json.loads(response.text)
                adapter = TypeAdapter(List[StudyCard])
                cards = adapter.validate_python(json_data)
                return cards
                
        except Exception as e:
            if model_name == models_to_try[-1]:
                print(f"[bold white on red]Error Fatal: Todos los modelos de Gemini fallaron. Último intento ({model_name}) dio el error: {e}[/]")
            continue

    return []
