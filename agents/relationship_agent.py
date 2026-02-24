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
# Importamos la abstracción de SQLalchemy (Record) directamente, ya que el dashboard nos arroja un Registry.
from core.database import Registry

def get_client():
    """Obtiene el cliente estandarizado GenAI agarrando GOOGLE_API_KEY local."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[yellow]Advertencia: No se encontró GOOGLE_API_KEY en variables de entorno. Las llamadas fallarán si no se setea.[/yellow]")
    return genai.Client(api_key=api_key)

def generate_relationship_cards(record_a: Registry, record_b: Registry) -> List[StudyCard]:
    """
    Agente Pedagógico Match Forzado.
    Genera tarjetas (StudyCard) mediante inteligencia artificial centradas en la diferenciación 
    excluyente entre dos conceptos (Registro A vs Registro B).
    """
    client = get_client()

    prompt = f"""
    Eres un profesor de universidad riguroso diseñando material de estudio enfocado en la "Discriminación Cognitiva" (Match Forzado).
    Tu objetivo es leer un 'Registro A' y un 'Registro B', identificar la frontera, paradigma divergente o caso de uso distintivo entre ambos, y generar tarjetas de estudio de contraste rápido.

    --- Registro A (ID Ficticio o Real: {record_a.id}) ---
    Título: {record_a.title}
    Info Cruda: {record_a.content_raw}
    Extra Metadatos: {record_a.meta_info}

    --- Registro B (ID Ficticio o Real: {record_b.id}) ---
    Título: {record_b.title}
    Info Cruda: {record_b.content_raw}
    Extra Metadatos: {record_b.meta_info}

    Reglas de Diseño (IMPORTANTE):
    1. Preguntas de Identificación: Presenta una característica, ventaja o desventaja y pregunta a CUÁL de los dos conceptos pertenece. 
    2. Preguntas de Contraste: Pregunta por la diferencia radical entre A y B.
    3. Evita resúmenes genéricos "Concepto A es X, Concepto B es Y". 
    4. Usa "Relacional" o "Conceptual" estrictamente en el campo 'card_type'.
    5. Asigna el campo 'parent_id' EXACTAMENTE ya sea en {record_a.id} si la respuesta es principalmente sobre A, o {record_b.id} si defiende o se enfoca en B.

    Retorna únicamente el array con los objetos válidos que encajen exhaustivamente en este esquema.
    """

    # Forzar el output a un array estructurado (List[StudyCard]) via JSON
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[StudyCard],
        temperature=0.3
    )

    if not os.environ.get("GOOGLE_API_KEY"):
        # Mockup Funcional si no hay llave para evitar el Crash Masivo
        print("[yellow]\n[Mockup Mode] Simulación de IA en curso debido a ausencia de API KEY. Generando tarjeta de prueba...[/yellow]")
        return [
            StudyCard(
                parent_id=record_a.id,
                question=f"A diferencia del registro '{record_b.title}', ¿qué característica exclusiva tiene '{record_a.title}'?",
                answer=f"(Generado por MockIA) - El concepto A resalta por atributos no compartidos con B.",
                card_type="Relacional"
            )
        ]

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    for model_name in models_to_try:
        try:
            # print() desactivado aquí si queremos mantener la pureza en el dashboard
            # Pero podemos usar rich si es invocado directamente.
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            
            if response.text:
                json_data = json.loads(response.text)
                # Validar la salida de nuevo contra nuestro Core Pydantic para eliminar la posibilidad de disonancia
                adapter = TypeAdapter(List[StudyCard])
                cards = adapter.validate_python(json_data)
                return cards
                
        except Exception as e:
            # Silenciar error para intentar el próximo modelo silenciosamente como pidió el blueprint
            # pero imprimir la excepcion si es el ultimo modelo
            if model_name == models_to_try[-1]:
                print(f"[bold white on red]Error Fatal: Todos los modelos de Gemini fallaron. Último intento ({model_name}) dio el error: {e}[/]")
            continue

    return []

if __name__ == "__main__":
    pass
