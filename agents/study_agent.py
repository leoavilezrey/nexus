import os
import json
from typing import List

try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

from rich.console import Console
console = Console()

from pydantic import TypeAdapter, BaseModel

from core.models import StudyCard
from core.database import Registry

from rich.prompt import Confirm
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

def get_client():
    """Obtiene el cliente estandarizado GenAI agarrando GOOGLE_API_KEY local."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

def generate_deck_from_registry(record: Registry, mockup_only: bool = False) -> List[StudyCard]:
    """
    Agente Pedagógico de Extracción.
    Genera tarjetas (StudyCard) mediante inteligencia artificial destilando el contenido de un solo registro.
    """
    if mockup_only:
        return [
            StudyCard(
                parent_id=record.id,
                question=f"¿Cuál es el tema principal de '{record.title}'?",
                answer=f"{record.title}",
                card_type="Conceptual"
            )
        ]

    client = get_client()
    if not client:
        # Mockup Inteligente (Heurístico) para cuando no hay API KEY
        cards = []
        # Tarjeta 1: Identificación y Tipo
        cards.append(StudyCard(
            parent_id=record.id,
            question=f"¿Cuál es el propósito o tema del registro '{record.title}' y qué tipo de recurso es?",
            answer=f"El tema es '{record.title}' y está clasificado como {record.type.upper()}.",
            card_type="Conceptual"
        ))
        
        # Tarjeta 2: Fragmento de contenido (si existe)
        if record.content_raw and len(record.content_raw.strip()) > 15:
            # Limpiar un poco el texto para la pregunta
            clean_text = record.content_raw.replace('\n', ' ').strip()
            cards.append(StudyCard(
                parent_id=record.id,
                question=f"Basado en la descripción de '{record.title}', completa el siguiente fragmento:\n\"{clean_text[:60]}...\"",
                answer=f"{clean_text[:120]}",
                card_type="Cloze"
            ))
            
        # Tarjeta 3: Referencia
        if record.path_url:
            cards.append(StudyCard(
                parent_id=record.id,
                question=f"¿Cuál es la ubicación física o enlace asociado al registro '{record.title}'?",
                answer=record.path_url,
                card_type="Factual"
            ))
            
        return cards

    # Definimos esquema simplificado para evitar errores de 'additionalProperties' en la API de Gemini
    class SimplifiedStudyCard(BaseModel):
        parent_id: int
        question: str
        answer: str
        card_type: str

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
        response_schema=list[SimplifiedStudyCard],
        temperature=0.3
    )

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash"
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
                # Convertimos de SimplifiedStudyCard a StudyCard real
                final_cards = []
                for item in json_data:
                    final_cards.append(StudyCard(
                        parent_id=item['parent_id'],
                        question=item['question'],
                        answer=item['answer'],
                        card_type=item['card_type']
                    ))
                return final_cards
                
        except Exception as e:
            if model_name == models_to_try[-1]:
                console.print(f"[bold white on red]Error Fatal: Todos los modelos de Gemini fallaron. Último intento ({model_name}) dio el error: {e}[/]")
            continue

    return []
