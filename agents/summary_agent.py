
import os
import json
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

from core.database import Registry

load_dotenv()

def get_client():
    """Obtiene el cliente GenAI."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

def generate_summary_from_registry(record: Registry) -> Optional[str]:
    """
    Agente de Síntesis.
    Genera un resumen ejecutivo y estructurado de todas las ideas del registro.
    """
    client = get_client()

    if not client:
        return f"Resumen básico de '{record.title}': Este recurso de tipo {record.type} contiene información sobre {record.title}. (Instala GOOGLE_API_KEY para un resumen profesional)."

    prompt = f"""
    Eres un experto en síntesis de información y gestión del conocimiento (PKM).
    Tu objetivo es leer el siguiente documento y crear un RESUMEN EJECUTIVO DE ALTO NIVEL.

    --- Registro (ID: {record.id}) ---
    Título: {record.title}
    Contenido: {record.content_raw}
    Metadatos: {record.meta_info}

    Reglas del Resumen:
    1. ESTRUCTURA: Usa viñetas para los puntos clave.
    2. BREVEDAD: No más de 300 palabras.
    3. VALOR: Enfócate en las ideas más importantes y conclusiones "accionables".
    4. TONO: Profesional, claro y directo.

    Responde únicamente con el texto del resumen en formato Markdown. No añadidas introducciones como "Aquí está el resumen".
    """

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
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )
            
            if response.text:
                return response.text.strip()
                
        except Exception as e:
            continue

    return None
