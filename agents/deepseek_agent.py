
import os
import json
from typing import List, Optional
from pydantic import BaseModel
from core.database import Registry, CardCreate

try:
    import requests
except ImportError:
    requests = None

from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
console = Console()

class DeepSeekCard(BaseModel):
    question: str
    answer: str

class DeepSeekAgent:
    """
    Agente especializado en usar DeepSeek para transformar transcripciones 
    en resúmenes concisos y flashcards.
    """
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com" # URL base oficial

    def process_content(self, title: str, content: str):
        """
        Genera un resumen y un conjunto de flashcards usando DeepSeek.
        """
        if not self.api_key:
            return None, []

        # No procesar si no hay contenido útil (evitar gasto de tokens en errores)
        if "Transcripción Disponible" in content or "Error al raspar" in content or len(content) < 100:
            return f"Sin resumen: No hay suficiente contenido base para analizar '{title}'.", []

        prompt = f"""
        Analiza el siguiente contenido extraído de un video de YouTube titulado "{title}".
        
        1. Genera un RESUMEN EJECUTIVO de no más de 3 párrafos.
        2. Genera 5 Flashcards de estudio en formato JSON exacto:
           [{{"question": "...", "answer": "..."}}, ...]

        Contenido:
        {content[:15000]} # Limitamos para evitar contexto excesivo en V1
        
        Responde estrictamente en este formato:
        RESUMEN: [Tu resumen aquí]
        FLASHCARDS: [Tu JSON de flashcards aquí]
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            full_text = result['choices'][0]['message']['content']
            
            # Parsing más robusto
            resumen = ""
            cards_json = []
            
            # Intentar extraer el resumen
            if "RESUMEN:" in full_text:
                if "FLASHCARDS:" in full_text:
                    resumen = full_text.split("RESUMEN:")[1].split("FLASHCARDS:")[0].strip()
                else:
                    resumen = full_text.split("RESUMEN:")[1].strip()
            
            # Intentar extraer las flashcards (JSON)
            if "FLASHCARDS:" in full_text:
                json_part = full_text.split("FLASHCARDS:")[1].strip()
                # Limpiar bloques de código markdown si existen
                if "```json" in json_part:
                    json_part = json_part.split("```json")[1].split("```")[0].strip()
                elif "```" in json_part:
                    json_part = json_part.split("```")[1].split("```")[0].strip()
                
                try:
                    cards_json = json.loads(json_part)
                except Exception as je:
                    console.print(f"[yellow]Error parseando JSON de DeepSeek: {je}[/yellow]")
                    # Intento desesperado: buscar el primer '[' y el último ']'
                    import re
                    match = re.search(r'\[\s*\{.*\}\s*\]', json_part, re.DOTALL)
                    if match:
                        try:
                            cards_json = json.loads(match.group())
                        except:
                            pass
            
            return resumen, cards_json
            
        except Exception as e:
            console.print(f"[red]Error en DeepSeek API: {e}[/]")
            return None, []

deepseek_agent = DeepSeekAgent()
