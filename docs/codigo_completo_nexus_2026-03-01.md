# Codigo Completo Nexus - 2026-03-01 16:53

Total archivos: 26

## Indice

1. `check_dashboard.py`
2. `check_dashboard_full.py`
3. `main.py`
4. `test_yt.py`
5. `test_yt_v2.py`
6. `verify_fix.py`
7. `web_server.py`
8. `agents/deepseek_agent.py`
9. `agents/mutation_agent.py`
10. `agents/relationship_agent.py`
11. `agents/study_agent.py`
12. `agents/summary_agent.py`
13. `core/database.py`
14. `core/models.py`
15. `core/search_engine.py`
16. `core/staging_db.py`
17. `modules/analytics.py`
18. `modules/exporter.py`
19. `modules/file_manager.py`
20. `modules/pipeline_manager.py`
21. `modules/pkm_manager.py`
22. `modules/study_engine.py`
23. `modules/web_scraper.py`
24. `modules/youtube_manager.py`
25. `ui/dashboard.py`
26. `ui/dashboard_v1_backup.py`

---

## check_dashboard.py
**Lineas: 21**

```python

import ast

with open(r'c:\Users\DELL\Proyectos\nexus\ui\dashboard.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'menu_ingreso':
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.ImportFrom):
                for alias in subnode.names:
                    if alias.name == 'Panel' or alias.asname == 'Panel':
                        print(f"Found Panel import in menu_ingreso at line {subnode.lineno}")
                    if alias.name == 'Text' or alias.asname == 'Text':
                        print(f"Found Text import in menu_ingreso at line {subnode.lineno}")
            if isinstance(subnode, ast.Assign):
                for target in subnode.targets:
                    if isinstance(target, ast.Name) and target.id == 'Panel':
                        print(f"Found Panel assignment in menu_ingreso at line {subnode.lineno}")
                    if isinstance(target, ast.Name) and target.id == 'Text':
                        print(f"Found Text assignment in menu_ingreso at line {subnode.lineno}")

```

---

## check_dashboard_full.py
**Lineas: 28**

```python

import ast

with open(r'c:\Users\DELL\Proyectos\nexus\ui\dashboard.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

class PanelFinder(ast.NodeVisitor):
    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == 'Panel' or alias.asname == 'Panel':
                print(f"ImportFrom: Panel at line {node.lineno}")
            if alias.name == 'Text' or alias.asname == 'Text':
                print(f"ImportFrom: Text at line {node.lineno}")
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'Panel':
                print(f"Assign: Panel at line {node.lineno}")
            if isinstance(target, ast.Name) and target.id == 'Text':
                print(f"Assign: Text at line {node.lineno}")

    def visit_FunctionDef(self, node):
        if node.name == 'Panel' or node.name == 'Text':
            print(f"FunctionDef: {node.name} at line {node.lineno}")
        self.generic_visit(node)

finder = PanelFinder()
finder.visit(tree)

```

---

## main.py
**Lineas: 27**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Punto de Entrada Oficial para Nexus
"""

import sys
import os

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH para las importaciones relativas.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ui.dashboard import main_loop
from core.database import init_db

if __name__ == "__main__":
    # Asegurar que la base de datos y sus tablas estén creadas antes de arrancar.
    init_db()
    
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nSaliendo de Nexus desde main.py...")
        sys.exit(0)

```

---

## test_yt.py
**Lineas: 17**

```python

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    video_id = "DrkDfUxl_EM" # The one from the user request
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_generated_transcript(['es', 'en'])
    full_transcript = transcript.fetch()
    print(f"Type of full_transcript: {type(full_transcript)}")
    if len(full_transcript) > 0:
        print(f"Type of first item: {type(full_transcript[0])}")
        print(f"First item: {full_transcript[0]}")
        try:
            print(f"First item ['text']: {full_transcript[0]['text']}")
        except Exception as e:
            print(f"Error accessing ['text']: {e}")
except Exception as e:
    print(f"Global error: {e}")

```

---

## test_yt_v2.py
**Lineas: 27**

```python

import youtube_transcript_api
print(f"Library contents: {dir(youtube_transcript_api)}")
from youtube_transcript_api import YouTubeTranscriptApi
print(f"YouTubeTranscriptApi contents: {dir(YouTubeTranscriptApi)}")
try:
    video_id = "DrkDfUxl_EM"
    # Try the way it's used in the app
    ytt_api = YouTubeTranscriptApi()
    print(f"Instance created: {ytt_api}")
    transcript_list = ytt_api.list(video_id)
    print(f"Transcript list found: {transcript_list}")
    transcript = transcript_list.find_generated_transcript(['es', 'en'])
    print(f"Transcript object: {transcript}")
    full_transcript = transcript.fetch()
    print(f"Type of full_transcript: {type(full_transcript)}")
    if full_transcript:
        item = full_transcript[0]
        print(f"Type of item: {type(item)}")
        print(f"Item contents: {item}")
        try:
            print(f"item['text'] = {item['text']}")
        except Exception as e:
            print(f"Error accessing ['text']: {e}")
            print(f"Item attributes: {dir(item)}")
except Exception as e:
    print(f"Execution error: {e}")

```

---

## verify_fix.py
**Lineas: 30**

```python

from youtube_transcript_api import YouTubeTranscriptApi
import sys

def test_logic(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        try:
            transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
        except Exception:
            transcript = transcript_list.find_generated_transcript(['es', 'en'])
            
        full_transcript = transcript.fetch()
        
        # The new logic
        text_fragments = [item.text if hasattr(item, "text") else item["text"] for item in full_transcript]
        content_raw = " ".join(text_fragments)
        
        print(f"Successfully extracted {len(content_raw)} characters.")
        print(f"Snippet: {content_raw[:100]}...")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    video_id = "DrkDfUxl_EM"
    test_logic(video_id)

```

---

## web_server.py
**Lineas: 214**

```python

import os
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.database import SessionLocal, Registry, Card, Tag, nx_db
from core.search_engine import search_registry, parse_query_string

app = FastAPI(title="Nexus Hybrid API")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/api/records")
async def get_records(q: str = ""):
    db = SessionLocal()
    try:
        filtros = parse_query_string(q)
        # Convertir filtros de string a listas si es necesario (el search_engine lo hace por dentro)
        results = search_registry(
            db_session=db,
            inc_name_path=filtros.get('inc_name'),
            exc_name_path=filtros.get('exc_name'),
            inc_tags=filtros.get('inc_tags'),
            exc_tags=filtros.get('exc_tags'),
            limit=50
        )
        return results
    finally:
        db.close()

@app.get("/api/records/{record_id}")
async def get_record(record_id: int):
    db = SessionLocal()
    try:
        reg = db.query(Registry).filter(Registry.id == record_id).first()
        if not reg:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        # Obtener tags
        tags = db.query(Tag).filter(Tag.registry_id == record_id).all()
        # Obtener cards
        cards = db.query(Card).filter(Card.parent_id == record_id).all()
        
        return {
            "id": reg.id,
            "type": reg.type,
            "title": reg.title,
            "path_url": reg.path_url,
            "content_raw": reg.content_raw,
            "summary": reg.summary,
            "meta_info": reg.meta_info,
            "tags": [t.value for t in tags],
            "cards": [{"id": c.id, "question": c.question, "answer": c.answer} for c in cards]
        }
    finally:
        db.close()

@app.get("/api/stats")
async def get_stats():
    db = SessionLocal()
    try:
        total_records = db.query(Registry).count()
        total_cards = db.query(Card).count()
        # Contar videos con IA (resumen)
        processed_ai = db.query(Registry).filter(
            Registry.type == 'youtube',
            Registry.summary != None,
            Registry.summary != '',
            ~Registry.summary.like('Sin resumen%')
        ).count()
        
        # Simulación de progreso de estudio (en una versión real consultaría los registros de repaso)
        study_progress = {
            "total_reviewed": 124, 
            "mastered": 45,
            "pending": total_cards - 45
        }
        
        return {
            "total_records": total_records,
            "total_cards": total_cards,
            "processed_ai": processed_ai,
            "study_progress": study_progress,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    finally:
        db.close()

@app.get("/api/recall/cards")
async def get_recall_cards(limit: int = 10):
    db = SessionLocal()
    try:
        # Por ahora, simplemente obtener tarjetas aleatorias o próximas a revisión
        # Primero intentamos las que tienen next_review vencido o nulo
        cards = db.query(Card).order_by(Card.next_review.asc()).limit(limit).all()
        
        result = []
        for c in cards:
            # Obtener el registro padre para contexto
            parent = db.query(Registry).filter(Registry.id == c.parent_id).first()
            result.append({
                "id": c.id,
                "question": c.question,
                "answer": c.answer,
                "parent_title": parent.title if parent else "Desconocido",
                "difficulty": c.difficulty
            })
        return result
    finally:
        db.close()

@app.post("/api/recall/answer")
async def post_recall_answer(card_id: int, quality: int):
    """
    quality: 0 (olvidado), 1 (difícil), 2 (bien), 3 (fácil)
    """
    db = SessionLocal()
    try:
        card = db.query(Card).filter(Card.id == card_id).first()
        if not card:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
        
        # Lógica simplificada de Spaced Repetition (después podemos meter FSRS o Anki logic)
        card.last_review = datetime.now()
        
        # Ajuste básico de estabilidad (días hasta el próximo repaso)
        days = 1
        if quality == 3: days = 4
        elif quality == 2: days = 2
        elif quality == 1: days = 1
        else: days = 0 # Repasar hoy mismo
        
        from datetime import timedelta
        card.next_review = datetime.now() + timedelta(days=days)
        
        db.commit()
        return {"status": "ok", "next_review": card.next_review}
    finally:
        db.close()

@app.get("/api/pipeline/status")
async def get_pipeline_status():
    from core.staging_db import StagingSessionLocal, staging_engine
    
    status = {
        "staging_connected": False,
        "queue_count": 0,
        "blocked_count": 0,
        "ready_count": 0
    }
    
    if staging_engine and StagingSessionLocal:
        db = StagingSessionLocal()
        try:
            status["staging_connected"] = True
            # Contar videos con error de IP
            status["blocked_count"] = db.query(Registry).filter(Registry.content_raw.like('%IpBlocked%')).count()
            # Contar videos listos para migrar (con transcripcion y sin error)
            status["ready_count"] = db.query(Registry).filter(
                Registry.content_raw != None,
                Registry.content_raw != '',
                ~Registry.content_raw.like('%IpBlocked%')
            ).count()
            # Total en cola
            status["queue_count"] = db.query(Registry).count()
        except Exception as e:
            print(f"Error accediendo a Staging DB: {e}")
        finally:
            db.close()
    
    return status

@app.post("/api/ingest")
async def post_ingest(data: dict):
    url = data.get("url")
    tags = data.get("tags", [])
    if not url:
        raise HTTPException(status_code=400, detail="URL requerida")
    
    from modules.web_scraper import ingest_web_resource
    
    try:
        # Procesar recurso
        reg = ingest_web_resource(url, tags)
        if reg:
            return {
                "status": "ok", 
                "id": reg.id, 
                "title": reg.title,
                "message": "Recurso indexado correctamente."
            }
        else:
            return {"status": "error", "message": "No se pudo procesar el recurso. Verifica la URL."}
    except Exception as e:
        return {"status": "error", "message": f"Error interno: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

---

## agents/deepseek_agent.py
**Lineas: 115**

```python

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

```

---

## agents/mutation_agent.py
**Lineas: 86**

```python
import json
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from core.database import nx_db, Card
from rich.console import Console
from rich.panel import Panel

console = Console()

class MutatedCard(BaseModel):
    id: int = Field(description="El ID original de la tarjeta a modificar.")
    question: str = Field(description="La nueva pregunta reformulada o en nuevo formato (JSON si es MCQ/Matching).")
    answer: str = Field(description="La nueva respuesta adaptada.")
    card_type: str = Field(description="El nuevo tipo de tarjeta (Factual, Conceptual, MCQ, TF, Cloze, Matching, MAQ).")

class MutatedDeck(BaseModel):
    cards: list[MutatedCard] = Field(description="Lista de tarjetas reformuladas.")

# Agente mutador. Utilizamos gemini-2.0-flash como modelo estándar (más rápido para mutaciones).
mutator_agent = Agent(
    'google-gla:gemini-2.0-flash',
    output_type=MutatedDeck,
    system_prompt='''Eres el Ingeneiro de Mutación Cognitiva de Nexus.
Tu objetivo es destruir la memorización por habituación (cuando el estudiante reconoce la forma de la pregunta pero no el fondo).

RECIBIRÁS: Un listado de tarjetas que el usuario ha repasado.

TU TAREA:
1. PARAFRASEO RADICAL: Reescribe la pregunta y respuesta desde cero. Mantén el significado pero usa sinónimos y estructuras diferentes.
2. NIVEL UNIVERSITARIO: Asegura que la complejidad sea Media-Alta.
3. TRANSFORMACIÓN DE FORMATO: Cambia el tipo de la tarjeta original a uno nuevo si es posible.
   Tipos permitidos en 'card_type':
   - [Factual/Conceptual]: Preguntas directas.
   - [MCQ]: Opción múltiple (Pregunta como JSON: {"prompt": "...", "options": {"a": "...", "b": "..."}}).
   - [TF]: Verdadero/Falso (Respuesta 'v' o 'f').
   - [Cloze]: Rellenar huecos (Sintaxis: "La {{c1::palabra}} es...").
   - [Matching]: Emparejamiento (JSON de pares en question).
   - [MAQ]: Selección múltiple.
4. INTEGRIDAD: No inventes información. La respuesta debe seguir siendo válida según el conocimiento original.
'''
)

def mutate_cards(card_ids: list[int]):
    """
    Toma una lista de IDs de tarjetas, consulta su texto original,
    los envía a Gemini para que los re-formule en memoria, y actualiza la Base de Datos.
    """
    if not card_ids:
        return
        
    console.print(f"\n[bold magenta]🧠 Agente Mutador Iniciado...[/]")
    console.print(f"[dim]Analizando {len(card_ids)} tarjetas difíciles para reescribirlas y romper tu adaptación estática...[/dim]")
    
    with nx_db.Session() as session:
        cards_to_mutate = session.query(Card).filter(Card.id.in_(card_ids)).all()
        
        if not cards_to_mutate:
            return
            
        # Preparar el payload
        prompt_content = "Tarjetas a reformular:\n\n"
        for c in cards_to_mutate:
            prompt_content += f"--- TARJETA ID {c.id} ---\nPregunta Original: {c.question}\nRespuesta Original: {c.answer}\n\n"
            
        console.print("[dim]Conectándose a Gemini AI para reformulación cognitiva...[/dim]")
        
        try:
            result = mutator_agent.run_sync(prompt_content)
            mutated_deck = result.data
            
            # Sobreescribir las tarjetas
            mutades_count = 0
            for mut_card in mutated_deck.cards:
                local_card = session.query(Card).get(mut_card.id)
                if local_card:
                    # Registramos el éxito
                    local_card.question = mut_card.question
                    local_card.answer = mut_card.answer
                    local_card.type = mut_card.card_type
                    mutades_count += 1
            
            session.commit()
            console.print(Panel(f"[bold green]¡Mutación Completada![/]\nSe han reformulado {mutades_count} Flashcards.\nMañana te sorprenderán con ángulos totalmente nuevos.", title="🧬 Mutación de Aprendizaje", border_style="green"))
            
        except Exception as e:
            console.print(f"\n[bold white on red]Error al contactar con la IA para la mutación: {e}[/]")

```

---

## agents/relationship_agent.py
**Lineas: 114**

```python
import os
import json
from typing import List

try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

from pydantic import TypeAdapter

from core.models import StudyCard
# Importamos la abstracción de SQLalchemy (Record) directamente, ya que el dashboard nos arroja un Registry.
from core.database import Registry

from rich.console import Console
console = Console()
from rich.prompt import Confirm
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def get_client():
    """Obtiene el cliente estandarizado GenAI agarrando GOOGLE_API_KEY local."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

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
        console.print("[yellow]\n[Mockup Mode] Simulación de IA en curso debido a ausencia de API KEY. Generando tarjeta de prueba...[/yellow]")
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
                console.print(f"[bold white on red]Error Fatal: Todos los modelos de Gemini fallaron. Último intento ({model_name}) dio el error: {e}[/]")
            continue

    return []

if __name__ == "__main__":
    pass

```

---

## agents/study_agent.py
**Lineas: 150**

```python
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

```

---

## agents/summary_agent.py
**Lineas: 69**

```python

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

```

---

## core/database.py
**Lineas: 273**

```python
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, JSON, 
    DateTime, ForeignKey, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.engine import Engine
from pydantic import BaseModel, Field, ConfigDict
from rich.console import Console

console = Console()

# ----------------------------------------------------------------------------
# 1. SQLAlchemy / Database Setup
# ----------------------------------------------------------------------------

# Ruta de la base de datos: En la raíz de Nexus (un nivel arriba de /core)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'nexus.db')

# Asegurarse de que el directorio padre existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Crear el engine usando SQLite
engine = create_engine(f"sqlite:///{DB_PATH}")

# Escuchar en la conexión para habilitar las opciones como WAL
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Modo WAL para alto rendimiento y concurrencia
    cursor.execute("PRAGMA journal_mode=WAL")
    # Activar el soporte para Foreign Keys (constraints)
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------------------------------------------------------------------
# 2. SQLAlchemy Models
# ----------------------------------------------------------------------------

class Registry(Base):
    """
    Tabla 1: registry (El Corazón)
    Almacena CUALQUIER tipo de recurso indexado.
    """
    __tablename__ = 'registry'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False) # file, youtube, web, note, concept, app, account
    title = Column(Text, nullable=True)
    path_url = Column(Text, nullable=True)
    content_raw = Column(Text, nullable=True)
    summary = Column(Text, nullable=True) # Resumen destilado por IA
    
    # Python atributo será 'meta_info', pero en la base de datos se llama 'metadata'
    # Esto previene choques con 'Base.metadata'
    meta_info = Column('metadata', JSON, nullable=True)
    
    is_flashcard_source = Column(Integer, default=0) # 0=False, 1=True
    
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # --- Relaciones ---
    tags = relationship("Tag", back_populates="registry", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="registry", cascade="all, delete-orphan")
    
    links_out = relationship(
        "NexusLink",
        foreign_keys='NexusLink.source_id',
        back_populates="source",
        cascade="all, delete-orphan"
    )
    links_in = relationship(
        "NexusLink",
        foreign_keys='NexusLink.target_id',
        back_populates="target",
        cascade="all, delete-orphan"
    )

class Tag(Base):
    """
    Tabla 2: tags
    Modelo tag-a-registro (uno a muchos)
    """
    __tablename__ = 'tags'
    
    registry_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), primary_key=True)
    value = Column(String, primary_key=True)
    
    registry = relationship("Registry", back_populates="tags")

class NexusLink(Base):
    """
    Tabla 3: nexus_links (Grafos de Relación)
    Conecta cualquier par de registros.
    """
    __tablename__ = 'nexus_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), nullable=False)
    relation_type = Column(String, nullable=True) # ej: "complementa", "referencia", "comparar"
    description = Column(Text, nullable=True)
    
    source = relationship("Registry", foreign_keys=[source_id], back_populates="links_out")
    target = relationship("Registry", foreign_keys=[target_id], back_populates="links_in")

class Card(Base):
    """
    Tabla 4: cards (Sistema de Aprendizaje)
    Preguntas del sistema de repetición espaciada asociadas a registros.
    """
    __tablename__ = 'cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('registry.id', ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    type = Column(String, nullable=True) # Factual, Conceptual, Relacional
    difficulty = Column(Float, default=0.0)
    stability = Column(Float, default=0.0)
    last_review = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    
    registry = relationship("Registry", back_populates="cards")

# ----------------------------------------------------------------------------
# 3. Pydantic Schemas (Data Validation)
# ----------------------------------------------------------------------------

class RegistryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str = Field(..., description="file, youtube, web, note, concept, app, account")
    title: Optional[str] = None
    path_url: Optional[str] = None
    content_raw: Optional[str] = None
    summary: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None
    is_flashcard_source: bool = False

class TagCreate(BaseModel):
    value: str

class NexusLinkCreate(BaseModel):
    source_id: int
    target_id: int
    relation_type: Optional[str] = None
    description: Optional[str] = None

class CardCreate(BaseModel):
    parent_id: int
    question: str
    answer: str
    type: str = "Factual"
    difficulty: float = 0.0
    stability: float = 0.0

# ----------------------------------------------------------------------------
# 4. CRUD Operations
# ----------------------------------------------------------------------------

def init_db():
    """Crea las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)
    console.print(f"[bold green]✓ Base de datos Nexus (SQLite WAL) inicializada correctamente en:[/] {DB_PATH}")

class NexusCRUD:
    """Clase principal de abstracción para realizar operaciones CRUD básicas."""
    
    def __init__(self):
        self.Session = SessionLocal
        
    def create_registry(self, data: RegistryCreate) -> Registry:
        """Crea un nuevo registro usando los esquemas de Pydantic."""
        with self.Session() as session:
            # Validación: Evitar duplicados por path_url (excepto notas donde path_url puede ser nulo, pero si existe se bloquea)
            if data.path_url:
                existing = session.query(Registry).filter(Registry.path_url == data.path_url).first()
                if existing:
                    console.print(f"[bold white on red]❌ Error de Duplicado:[/] El registro con la ruta/URL '{data.path_url}' ya existe en el Súper Schema (ID {existing.id}). Operación bloqueada.")
                    raise ValueError(f"Registro Duplicado: {data.path_url}")

            # Validación: Descripción obligatoria
            if not data.content_raw or not data.content_raw.strip():
                console.print("[yellow]Aviso: No se proporcionó descripción. Usando título como descripción básica requerida.[/yellow]")
                data.content_raw = f"(Auto-Descripción) Título: {data.title} | Ruta: {data.path_url}"

            # Usar model_dump() de Pydantic v2
            reg = Registry(**data.model_dump())
            session.add(reg)
            session.commit()
            session.refresh(reg)
            console.print(f"[blue]Registry creado:[/] ID {reg.id} (Tipo: {reg.type})")
            return reg
            
    def get_registry(self, registry_id: int) -> Optional[Registry]:
        """Obtiene un registro a partir de su ID."""
        from sqlalchemy.orm import joinedload
        with self.Session() as session:
            # Devolvemos el registro separado pero cargado
            # (Ten en cuenta que usar las relaciones fuera de sesión puede requerir eager_loading)
            reg = session.query(Registry).options(
                joinedload(Registry.tags)
            ).filter(Registry.id == registry_id).first()
            if reg:
                session.expunge(reg)
            return reg
            
    def add_tag(self, registry_id: int, tag_data: TagCreate) -> Tag:
        """Añade una única etiqueta al registro."""
        with self.Session() as session:
            tag = Tag(registry_id=registry_id, value=tag_data.value)
            session.merge(tag)
            session.commit()
            return tag
            
    def create_link(self, link_data: NexusLinkCreate) -> NexusLink:
        """Crea una relación entre dos registros."""
        with self.Session() as session:
            link = NexusLink(**link_data.model_dump())
            session.add(link)
            session.commit()
            session.refresh(link)
            console.print(f"[magenta]Link Creado:[/] Entre {link.source_id} y {link.target_id}")
            return link

    def create_card(self, card_data: CardCreate) -> Card:
        """Adiciona una nueva flashcard."""
        with self.Session() as session:
            card = Card(**card_data.model_dump())
            session.add(card)
            session.commit()
            session.refresh(card)
            console.print(f"[yellow]Card Creada:[/] Asociada al registro ID {card.parent_id}")
            return card

    def delete_registry(self, registry_id: int) -> bool:
        """Elimina un registro física y lógicamente de la Base de Datos, destruyendo dependencias por si SQLite no activó el PRAGMA CASCADE."""
        with self.Session() as session:
            from sqlalchemy import or_
            # Eliminación explícita defensiva 
            session.query(Tag).filter(Tag.registry_id == registry_id).delete(synchronize_session=False)
            session.query(NexusLink).filter(or_(NexusLink.source_id == registry_id, NexusLink.target_id == registry_id)).delete(synchronize_session=False)
            session.query(Card).filter(Card.parent_id == registry_id).delete(synchronize_session=False)
            
            # Matar registro principal
            deleted = session.query(Registry).filter(Registry.id == registry_id).delete(synchronize_session=False)
            session.commit()
            return deleted > 0

    def update_summary(self, registry_id: int, summary_text: str) -> bool:
        """Actualiza el resumen de un registro."""
        with self.Session() as session:
            rows = session.query(Registry).filter(Registry.id == registry_id).update({
                Registry.summary: summary_text
            })
            session.commit()
            return rows > 0

# Exportamos la instancia para su uso global si así se requiere
nx_db = NexusCRUD()

if __name__ == "__main__":
    init_db()

```

---

## core/models.py
**Lineas: 47**

```python
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

# Definición de tipos permitidos para el registro
ResourceType = Literal['file', 'youtube', 'web', 'note', 'concept', 'app', 'account']

class ResourceRecord(BaseModel):
    """
    Espejo de la tabla 'registry'.
    Almacena los datos maestros de cualquier recurso indexado.
    """
    id: Optional[int] = None
    type: ResourceType = Field(..., description="Tipo de recurso")
    title: str = Field(..., description="Nombre o título del recurso")
    path_url: str = Field(..., description="Ruta física local o URL externa")
    content_raw: Optional[str] = Field(default=None, description="Contenido extraído o notas")
    summary: Optional[str] = Field(default=None, description="Resumen destilado por IA")
    metadata_dict: Dict[str, Any] = Field(default_factory=dict, description="Metadatos en formato JSON")
    is_flashcard_source: bool = Field(default=False, description="¿Marcado como fuente de flashcards?")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)


class NexusLink(BaseModel):
    """
    Representa un grafo de relaciones entre dos ResourceRecords.
    """
    source_id: int = Field(..., description="ID del recurso origen")
    target_id: int = Field(..., description="ID del recurso destino")
    relation_type: str = Field(..., description="Tipo de relación (ej. complementa, referencia)")
    description: str = Field(..., description="Notas sobre la relación")


class StudyCard(BaseModel):
    """
    Representa una tarjeta de estudio estilo Spaced Repetition System.
    """
    id: Optional[int] = None
    parent_id: int = Field(..., description="ID del ResourceRecord del cual proviene esta pregunta")
    question: str = Field(..., description="Pregunta a evaluar")
    answer: str = Field(..., description="Respuesta a la pregunta")
    card_type: str = Field(..., description="Tipo de carta (Factual, Conceptual, Relacional)")
    srs_data: Dict[str, Any] = Field(
        default_factory=lambda: {"difficulty": 0.0, "stability": 0.0, "last_review": None, "next_review": None},
        description="Datos requeridos por el algoritmo de repetición espaciada"
    )

```

---

## core/search_engine.py
**Lineas: 260**

```python
from typing import Optional, List
from sqlalchemy import or_, and_, not_, func
from sqlalchemy.orm import Session

from core.database import Registry, Tag
from core.models import ResourceRecord

def search_registry(
    db_session: Session,
    type_filter: Optional[str] = None,
    inc_name_path: Optional[str] = None,
    exc_name_path: Optional[str] = None,
    inc_tags: Optional[str] = None,
    exc_tags: Optional[str] = None,
    inc_extensions: Optional[List[str]] = None,
    exc_extensions: Optional[List[str]] = None,
    has_info: Optional[str] = None,
    record_ids_str: Optional[str] = None,
    is_flashcard_source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[ResourceRecord]:
    """
    Motor maestro de búsqueda para Nexus.
    Retorna siempre una lista de instancias Pydantic ResourceRecord.
    Soporta Inclusión, Exclusión, tags especiales (__web__) y filtros de contenido.
    """
    query = db_session.query(Registry)

    # 1. Filtro estricto por Tipo (file, youtube, note, etc.)
    if type_filter:
        query = query.filter(Registry.type == type_filter)

    # 2. Búsqueda en Nombre y Ruta (Inclusiones y Exclusiones)
    # Soporte para múltiples términos separados por coma.
    if inc_name_path:
        for term in [t.strip() for t in inc_name_path.split(',') if t.strip()]:
            query = query.filter(
                or_(
                    Registry.title.ilike(f"%{term}%"),
                    Registry.path_url.ilike(f"%{term}%")
                )
            )

    if exc_name_path:
        for term in [t.strip() for t in exc_name_path.split(',') if t.strip()]:
            query = query.filter(
                not_(
                    or_(
                        Registry.title.ilike(f"%{term}%"),
                        Registry.path_url.ilike(f"%{term}%")
                    )
                )
            )

    # 3. Etiquetas (Inclusiones y Exclusiones)
    # Se usan Subqueries IN() y NOT IN() hacia la tabla Tag para máxima optimización y precisión
    if inc_tags:
        for term in [t.strip() for t in inc_tags.split(',') if t.strip()]:
            subquery = db_session.query(Tag.registry_id).filter(Tag.value.ilike(f"%{term}%"))
            query = query.filter(Registry.id.in_(subquery))

    if exc_tags:
        for term in [t.strip() for t in exc_tags.split(',') if t.strip()]:
            subquery = db_session.query(Tag.registry_id).filter(Tag.value.ilike(f"%{term}%"))
            query = query.filter(not_(Registry.id.in_(subquery)))

    # 4. Extensiones + Soporte para el tag especial '__web__'
    if inc_extensions:
        inc_exts_clean = [e.strip().lower() for e in inc_extensions if e.strip()]
        if inc_exts_clean:
            conditions = []
            has_web = False
            # Mapeo de conveniencia: Si el usuario escribe 'web' o 'youtube' en el campo de extensión,
            # lo interpretamos como el tag especial de búsqueda web.
            web_aliases = {'__web__', 'web', 'youtube', 'yt'}
            if any(alias in inc_exts_clean for alias in web_aliases):
                has_web = True
                for alias in web_aliases:
                    if alias in inc_exts_clean: inc_exts_clean.remove(alias)

            for ext in inc_exts_clean:
                ext_no_dot = ext.lstrip('.')
                ext_dot = f".{ext_no_dot}"
                # Buscar en la URL/Path físico, o usando el casteo JSON de SQLAlchemy de 'meta_info'
                conditions.append(Registry.path_url.ilike(f"%{ext_dot}"))
                conditions.append(func.json_extract(Registry.meta_info, '$.extension').ilike(ext_no_dot))

            if has_web:
                # El tag __web__ busca explícitamente recursos que viven en la red o son de plataforma web
                conditions.append(Registry.type.in_(['youtube', 'web', 'account']))
                conditions.append(Registry.path_url.ilike("http%"))

            if conditions:
                query = query.filter(or_(*conditions))

    if exc_extensions:
        exc_exts_clean = [e.strip().lower() for e in exc_extensions if e.strip()]
        if exc_exts_clean:
            conditions = []
            has_web = False
            web_aliases = {'__web__', 'web', 'youtube', 'yt'}
            if any(alias in exc_exts_clean for alias in web_aliases):
                has_web = True
                for alias in web_aliases:
                    if alias in exc_exts_clean: exc_exts_clean.remove(alias)

            for ext in exc_exts_clean:
                ext_no_dot = ext.lstrip('.')
                ext_dot = f".{ext_no_dot}"
                conditions.append(Registry.path_url.ilike(f"%{ext_dot}"))
                conditions.append(func.json_extract(Registry.meta_info, '$.extension').ilike(ext_no_dot))

            if has_web:
                conditions.append(Registry.type.in_(['youtube', 'web', 'account']))
                conditions.append(Registry.path_url.ilike("http%"))

            if conditions:
                query = query.filter(not_(or_(*conditions)))

    # 5. Tiene Información (has_info) -> 's' o 'n'
    if has_info:
        has_info_val = has_info.lower().strip()
        if has_info_val == 's':
            # 's': Obliga a que tenga 'content_raw' y no esté vacío, O tenga alguna etiqueta asociada en Tag.
            # Según tu Blueprint es "Registros que sí tengan content_raw o metadata de tags"
            query = query.filter(
                or_(
                    and_(Registry.content_raw.isnot(None), Registry.content_raw != ""),
                    Registry.id.in_(db_session.query(Tag.registry_id))
                )
            )
        elif has_info_val == 'n':
            # 'n': Son únicamente archivos de indexado rápido "crudos", sin raw description ni tags.
            query = query.filter(
                and_(
                    or_(Registry.content_raw.is_(None), Registry.content_raw == ""),
                    not_(Registry.id.in_(db_session.query(Tag.registry_id)))
                )
            )

    # 6. Filtrado por IDs específicos (Misma lógica csv / rangos que dashboard)
    if record_ids_str:
        ids_to_search = []
        for part in record_ids_str.split(','):
            part = part.strip()
            if '-' in part and not part.startswith('-'):
                try:
                    s_id, e_id = part.split('-')
                    ids_to_search.extend(range(min(int(s_id), int(e_id)), max(int(s_id), int(e_id)) + 1))
                except ValueError:
                    pass
            else:
                try:
                    if part: ids_to_search.append(int(part))
                except ValueError:
                    pass
        if ids_to_search:
            query = query.filter(Registry.id.in_(list(set(ids_to_search))))

    # 7. Es Fuente de Flashcard -> 's' o 'n'
    if is_flashcard_source:
        from core.database import Card
        f_val = is_flashcard_source.lower().strip()
        if f_val == 's':
            # Se devuelven los que tengan el check = 1 explícito, o que implícitamente YA tengan tarjetas hijas en la BD
            query = query.filter(or_(
                Registry.is_flashcard_source == 1,
                Registry.id.in_(db_session.query(Card.parent_id))
            ))
        elif f_val == 'n':
            # Solo registros sin el flag explícito, y que TAMPOCO tengan tarjetas hijas
            query = query.filter(and_(
                or_(Registry.is_flashcard_source == 0, Registry.is_flashcard_source.is_(None)),
                not_(Registry.id.in_(db_session.query(Card.parent_id)))
            ))

    # 8. Paginador y Orden (Siempre el modificado recientemente de primero)
    query = query.order_by(Registry.modified_at.desc()).limit(limit).offset(offset)
    
    # 9. Ejecución SQL
    results = query.all()
    
    # 10. Mapeo estricto a Pydantic (Tal y como nos pidió la Base)
    pydantic_results: List[ResourceRecord] = []
    for row in results:
        # Algunos registros podrían no tener diccionario json si fueron inserts manuales parciales SQLite
        meta = row.meta_info if row.meta_info else {}
        rr = ResourceRecord(
            id=row.id,
            type=row.type,
            title=row.title or "",
            path_url=row.path_url or "",
            content_raw=row.content_raw,
            metadata_dict=meta,
            is_flashcard_source=bool(row.is_flashcard_source),
            created_at=row.created_at,
            modified_at=row.modified_at
        )
        pydantic_results.append(rr)

    return pydantic_results

def parse_query_string(query_str: str) -> dict:
    """
    Parses a smart query string into a dict of filters for search_registry.
    Example: 'python t:docs e:pdf -t:old i:1-50'
    - Default/No prefix: inc_name
    - t: Tag to include
    - -t: Tag to exclude
    - e: Extension to include
    - -e: Extension to exclude
    - i: IDs or ID range
    - s: Source (s:y, s:n)
    """
    filters = {
        'inc_name': [], 'exc_name': [], 
        'inc_tags': [], 'exc_tags': [],
        'inc_exts': [], 'exc_exts': [],
        'inc_ids': "", 'is_source': "",
        'has_info': ""
    }
    
    parts = query_str.split()
    for p in parts:
        if p.startswith('t:'):
            filters['inc_tags'].append(p[2:])
        elif p.startswith('-t:'):
            filters['exc_tags'].append(p[3:])
        elif p.startswith('e:'):
            filters['inc_exts'].append(p[2:])
        elif p.startswith('-e:'):
            filters['exc_exts'].append(p[3:])
        elif p.startswith('i:'):
            filters['inc_ids'] = p[2:]
        elif p.startswith('s:'):
            val = p[2:].lower()
            if val in ['s', 'y', '1', 'true']: filters['is_source'] = 's'
            elif val in ['n', '0', 'false']: filters['is_source'] = 'n'
        elif p.startswith('h:'):
            val = p[2:].lower()
            if val in ['s', 'y', '1', 'true']: filters['has_info'] = 's'
            elif val in ['n', '0', 'false']: filters['has_info'] = 'n'
            else: filters['has_info'] = val
        elif p.startswith('-'):
            filters['exc_name'].append(p[1:])
        else:
            filters['inc_name'].append(p)
            
    return {
        'inc_name': ",".join(filters['inc_name']),
        'exc_name': ",".join(filters['exc_name']),
        'inc_tags': ",".join(filters['inc_tags']),
        'exc_tags': ",".join(filters['exc_tags']),
        'inc_exts': ",".join(filters['inc_exts']),
        'exc_exts': ",".join(filters['exc_exts']),
        'inc_ids': filters['inc_ids'],
        'is_source': filters['is_source'],
        'has_info': filters['has_info']
    }

```

---

## core/staging_db.py
**Lineas: 84**

```python

import os
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from core.database import Base, NexusCRUD, Registry, RegistryCreate, nx_db
from rich.console import Console

console = Console()

# 1. Definir la ruta en G: (Google Drive)
STAGING_DB_DIR = r"G:\Mi unidad\Nexus_Staging"
STAGING_DB_PATH = os.path.join(STAGING_DB_DIR, "staging_buffer.db")

# Crear el engine para el buffer de G:
def get_staging_engine():
    if not os.path.exists(STAGING_DB_DIR):
        try:
            os.makedirs(STAGING_DB_DIR, exist_ok=True)
        except Exception as e:
            # Fallback a local si G: no esta montado
            console.print(f"[bold yellow]⚠ Buffer Google Drive (G:) no disponible. Operando en modo local.[/] ({e})")
            return None
    return create_engine(f"sqlite:///{STAGING_DB_PATH}")

staging_engine = get_staging_engine()

# Configurar PRAGMAs para el buffer
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session y CRUD para Staging
if staging_engine:
    StagingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=staging_engine)
else:
    StagingSessionLocal = None

class StagingCRUD(NexusCRUD):
    """
    Hereda de NexusCRUD pero apunta a la sesion del buffer en G:
    """
    def __init__(self):
        self.Session = StagingSessionLocal

    def _check_available(self):
        """Verifica que el Staging DB esté operativo antes de cualquier operación."""
        if self.Session is None:
            console.print("[bold yellow]⚠ Staging DB no disponible (G: no montado). Operación cancelada.[/]")
            return False
        return True

    def create_registry(self, data):
        if not self._check_available():
            return None
        return super().create_registry(data)

    def get_registry(self, registry_id):
        if not self._check_available():
            return None
        return super().get_registry(registry_id)

    def init_staging(self):
        if staging_engine:
            Base.metadata.create_all(bind=staging_engine)
            return True
        return False

# Instancia global del buffer
staging_db = StagingCRUD()

def get_current_db(mode="local"):
    """
    Retorna la instancia de DB activa.
    'local' -> nexus.db (SSD)
    'staging' -> staging_buffer.db (G: Drive)
    """
    if mode == "staging" and staging_engine:
        return staging_db
    return nx_db

```

---

## modules/analytics.py
**Lineas: 64**

```python
from datetime import datetime, timezone
from core.database import SessionLocal, Registry, Card, NexusLink, Tag
from sqlalchemy import func

def get_global_metrics():
    """Calcula y devuelve las métricas globales del sistema Nexus."""
    metrics = {
        "registry_counts": {
            "file": 0, "youtube": 0, "web": 0, "note": 0, "concept": 0, "app": 0, "account": 0, "total": 0
        },
        "network": {
            "total_links": 0,
            "unique_tags": 0
        },
        "srs": {
            "total_cards": 0,
            "due_today": 0,
            "due_future": 0,
            "avg_difficulty": 0.0,
            "avg_stability": 0.0,
            "retention_desc": "N/A"
        }
    }
    
    with SessionLocal() as session:
        # 1. Composición del Cerebro (Registros)
        registry_stats = session.query(Registry.type, func.count(Registry.id)).group_by(Registry.type).all()
        for r_type, count in registry_stats:
            metrics["registry_counts"][r_type] = count
            metrics["registry_counts"]["total"] += count
            
        # 2. Red Neuronal (Vínculos y Tags)
        metrics["network"]["total_links"] = session.query(func.count(NexusLink.id)).scalar() or 0
        metrics["network"]["unique_tags"] = session.query(func.count(func.distinct(Tag.value))).scalar() or 0
        
        # 3. Madurez Cognitiva (SRS)
        now = datetime.now(timezone.utc)
        
        total_cards = session.query(func.count(Card.id)).scalar() or 0
        metrics["srs"]["total_cards"] = total_cards
        
        if total_cards > 0:
            due_today = session.query(func.count(Card.id)).filter(
                (Card.next_review == None) | (Card.next_review <= now)
            ).scalar() or 0
            
            metrics["srs"]["due_today"] = due_today
            metrics["srs"]["due_future"] = total_cards - due_today
            
            avg_diff = session.query(func.avg(Card.difficulty)).filter(Card.difficulty > 0).scalar() or 0.0
            avg_stab = session.query(func.avg(Card.stability)).filter(Card.stability > 0).scalar() or 0.0
            
            metrics["srs"]["avg_difficulty"] = float(avg_diff)
            metrics["srs"]["avg_stability"] = float(avg_stab)
            
            # Interpretar dificultad (1-10 por SM-2/FSRS adaptado)
            if avg_diff < 3.0:
                metrics["srs"]["retention_desc"] = "Alta (Fácil)"
            elif 3.0 <= avg_diff <= 6.0:
                metrics["srs"]["retention_desc"] = "Media (Estable)"
            else:
                metrics["srs"]["retention_desc"] = "Baja (Difícil)"

    return metrics

```

---

## modules/exporter.py
**Lineas: 59**

```python

import os
import csv
import sqlite3
import shutil
from datetime import datetime
from core.database import nx_db, SessionLocal, Registry, Tag

def export_to_google_drive():
    """
    Exporta la base de datos actual y genera un reporte CSV en Google Drive (Unidad G:).
    """
    # 1. Definir rutas en G:
    g_drive_base = r"G:\Mi unidad\Nexus_Data"
    if not os.path.exists(r"G:\Mi unidad"):
        return False, "No se detecto la unidad Google Drive (G:). Asegura que el cliente de escritorio este abierto."

    if not os.path.exists(g_drive_base):
        os.makedirs(g_drive_base)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_export_path = os.path.join(g_drive_base, f"nexus_backup_{timestamp}.db")
    csv_export_path = os.path.join(g_drive_base, f"nexus_registros_{timestamp}.csv")

    try:
        # --- A. Exportar Base de Datos (Copia Fisica) ---
        # Cerramos conexiones/flushing no es necesario con copy2 si no es vital, 
        # pero es mejor copiar el archivo nexus.db de la raiz.
        source_db = r"c:\Users\DELL\Proyectos\nexus\nexus.db"
        if os.path.exists(source_db):
            shutil.copy2(source_db, db_export_path)
            
        # --- B. Exportar a CSV (Para lectura facil/descarga) ---
        with SessionLocal() as session:
            registries = session.query(Registry).all()
            
            with open(csv_export_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
                fieldnames = ['id', 'tipo', 'titulo', 'url_ruta', 'resumen', 'contenido_raw', 'tags', 'fecha_creacion']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for r in registries:
                    # Obtener tags
                    tags = ", ".join([t.value for t in r.tags])
                    
                    writer.writerow({
                        'id': r.id,
                        'tipo': r.type,
                        'titulo': r.title,
                        'url_ruta': r.path_url,
                        'resumen': r.summary if r.summary else "",
                        'contenido_raw': r.content_raw if r.content_raw else "",
                        'tags': tags,
                        'fecha_creacion': r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
                    })

        return True, g_drive_base
    except Exception as e:
        return False, str(e)

```

---

## modules/file_manager.py
**Lineas: 98**

```python
import os
from pathlib import Path
from typing import List, Optional

from core.database import nx_db, RegistryCreate, TagCreate
from core.models import ResourceRecord
from rich.console import Console

console = Console()

# Definimos extensiones que consideramos texto plano directamente legible
TEXT_EXTENSIONS = {'.txt', '.md', '.csv', '.json', '.xml', '.py', '.js', '.html', '.css', '.ini', '.yaml', '.yml'}

def ingest_local_file(filepath: str, tags: List[str]) -> Optional[ResourceRecord]:
    """
    Ingesta un archivo local en la base de datos maestra de Nexus.
    Extrae metadatos y, si es texto plano, una vista previa del contenido.
    No almacena binarios bajo ninguna circunstancia.
    """
    file_path_obj = Path(filepath)
    
    # 1. Validación de existencia
    if not file_path_obj.exists() or not file_path_obj.is_file():
        console.print(f"[bold white on red]Error:[/] El archivo no existe o no es un archivo válido: {filepath}")
        return None

    # 2. Extracción de Metadatos Base
    title = file_path_obj.name
    absolute_posix_path = file_path_obj.absolute().as_posix() # Ruta multiplataforma
    ext = file_path_obj.suffix.lower()
    
    try:
        size_bytes = file_path_obj.stat().st_size
    except Exception as e:
        console.print(f"[yellow]Advertencia:[/] No se pudo obtener el tamaño de {filepath}. Error: {e}")
        size_bytes = 0

    # 3. Manejo de Texto Plano (Lectura Rápida)
    content_raw = None
    if ext in TEXT_EXTENSIONS:
        try:
            # Leemos los primeros 5000 caracteres para evitar saturar la base de datos
            # con archivos de texto masivos (ej. logs gigantes)
            with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                content_raw = f.read(5000)
                if len(content_raw) == 5000:
                    content_raw += "\n...[Contenido truncado]"
        except Exception as e:
            console.print(f"[yellow]Advertencia:[/] No se pudo extraer texto parcial de {filepath}. Error: {e}")

    # Estructura del diccionario JSON para el campo 'meta_info' (metadatos base)
    meta_info = {
        "extension": ext.lstrip('.'),
        "size_bytes": size_bytes,
        "source": "local_file_manager"
    }

    # 4. Inserción estricta en la Base de Datos a través del ORM (Pydantic Mapped)
    file_record_data = RegistryCreate(
        type="file",
        title=title,
        path_url=absolute_posix_path,
        content_raw=content_raw,
        meta_info=meta_info
    )

    try:
        # Inyectar registro maestro en el Core DB
        reg = nx_db.create_registry(file_record_data)
        
        # Inyectar las etiquetas vinculadas (limpiando espacios)
        for tag_val in tags:
            tag_clean = tag_val.strip().lower()
            if tag_clean:
                nx_db.add_tag(reg.id, TagCreate(value=tag_clean))
        
        # Empaquetamos al modelo maestro Pydantic para devolver el ResourceRecord
        rr = ResourceRecord(
            id=reg.id,
            type=reg.type,
            title=reg.title or "",
            path_url=reg.path_url or "",
            content_raw=reg.content_raw,
            metadata_dict=reg.meta_info if reg.meta_info else {},
            created_at=reg.created_at,
            modified_at=reg.modified_at
        )
        
        print(f"✅ Archivo '{title}' indexado exitosamente (ID: {reg.id}).")
        return rr
        
    except Exception as e:
        console.print(f"[bold white on red]Error fatal al intentar guardar en la base de datos:[/] {e}")
        return None

if __name__ == "__main__":
    # Test rápido de compilación
    pass

```

---

## modules/pipeline_manager.py
**Lineas: 146**

```python

import os
import json
import time
from datetime import datetime
from modules.web_scraper import get_playlist_video_urls, ingest_web_resource
from agents.deepseek_agent import deepseek_agent
from core.database import nx_db, RegistryCreate, CardCreate, TagCreate
from core.staging_db import staging_db
from rich.console import Console
from rich.progress import Progress

console = Console()

QUEUE_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_queue.txt"
HISTORY_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_history.json"

from modules.youtube_manager import YouTubeManager

def run_youtube_pipeline():
    """
    Ejecuta el plan de trabajo automatizado para playlists:
    1. Lee cola de playlists.
    2. Descarga a Staging (G:).
    3. Procesa con DeepSeek.
    4. Mueve a Nexus Local.
    5. Opcional: Elimina el video de la playlist de YouTube (via API).
    """
    # Asegurar que el Buffer de Staging esté inicializado
    staging_db.init_staging()

    yt_manager = None
    if os.path.exists('client_secrets.json'):
        try:
            # Forzamos un timeout corto para no bloquear el inicio si no hay red
            with console.status("[dim]Estableciendo conexión con YouTube API...[/dim]", spinner="dots"):
                yt_manager = YouTubeManager()
                console.print("[bold green]✓ Conexión con YouTube API establecida (Modo Gestión Activo).[/bold green]")
        except Exception as e:
            console.print(f"[yellow]Aviso: No se pudo conectar con YouTube API. Se usará Modo Scraping (Modo Rescate). {e}[/yellow]")
            yt_manager = None

    if not os.path.exists(QUEUE_FILE):
        console.print(f"[yellow]Aviso: No se encontro el archivo de cola en {QUEUE_FILE}[/yellow]")
        return

    # Cargar historial
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)

    with open(QUEUE_FILE, 'r') as f:
        playlists_urls = [line.strip() for line in f if line.strip() and line.strip() not in history]

    if not playlists_urls:
        console.print("[green]No hay nuevas playlists para procesar en la cola.[/green]")
        return

    console.print(f"[bold cyan]🚀 Iniciando Pipeline para {len(playlists_urls)} playlists...[/bold cyan]")

    for p_url in playlists_urls:
        console.print(f"\n[bold yellow]📂 Procesando Playlist:[/] {p_url}")
        
        videos_to_process = []
        playlist_id = None
        
        # Intentar obtener videos via API oficial si esta disponible
        if yt_manager:
            playlist_id = yt_manager.get_playlist_id_from_url(p_url)
            if playlist_id:
                videos_to_process = yt_manager.get_playlist_items(playlist_id)
        
        # Fallback a yt-dlp si la API fallo o no esta disponible
        if not videos_to_process:
            raw_urls = get_playlist_video_urls(p_url)
            if raw_urls:
                videos_to_process = [{'url': u, 'title': u, 'playlist_item_id': None} for u in raw_urls]
            else:
                # Si no es playlist, es un video individual. Lo agregamos para procesar.
                videos_to_process = [{'url': p_url, 'title': p_url, 'playlist_item_id': None}]

        console.print(f"   • {len(videos_to_process)} recursos detectados para procesar.")
        
        for v_data in videos_to_process:
            v_url = v_data['url']
            v_item_id = v_data['playlist_item_id']
            
            console.print(f"\n   [cyan]»[/] Procesando: [italic]{v_data['title']}[/italic]")
            
            # 2. Descarga masiva a Staging (G:)
            reg_staging = ingest_web_resource(v_url, ["pipeline_staging"], db_target=staging_db)
            
            if reg_staging:
                # 3. Procesamiento Inteligente con DeepSeek
                console.print(f"     • Generando Inteligencia con DeepSeek...")
                resumen, cards = deepseek_agent.process_content(reg_staging.title, reg_staging.content_raw)
                
                # 4. Centralizacion en Nexus (Local SSD)
                try:
                    data_final = RegistryCreate(
                        type="youtube",
                        title=reg_staging.title,
                        path_url=reg_staging.path_url,
                        content_raw=reg_staging.content_raw,
                        summary=resumen,
                        meta_info=reg_staging.meta_info,
                        is_flashcard_source=True
                    )
                    reg_nexus = nx_db.create_registry(data_final)
                    
                    # Agregar tags y cards
                    nx_db.add_tag(reg_nexus.id, TagCreate(value="YouTube_Pipeline"))
                    for c in cards:
                        nx_db.create_card(CardCreate(
                            parent_id=reg_nexus.id,
                            question=c['question'],
                            answer=c['answer'],
                            type="DeepSeek_AI"
                        ))
                    
                    console.print(f"     [bold green]✅ Centralizado en Nexus ID {reg_nexus.id}[/bold green]")
                    
                    # 5. ELIMINACIÓN DEL HISTORIAL DE YOUTUBE (Gestión de Cola)
                    if yt_manager and v_item_id:
                        if yt_manager.remove_video_from_playlist(v_item_id):
                            console.print(f"     [bold blue]🗑️  Video eliminado de la playlist de YouTube (Cola despejada).[/bold blue]")
                        else:
                            console.print(f"     [yellow]⚠️ No se pudo eliminar de YouTube, pero el dato ya esta en Nexus.[/yellow]")

                except Exception as e:
                    console.print(f"     [bold red]❌ Error moviendo a Nexus: {e}[/bold red]")
            else:
                console.print(f"     [bold red]⚠️  Fallo ingesta de video {v_url}[/bold red]")
            
            # Pequeña pausa para mitigar bloqueos de IP (Rate Limiting)
            time.sleep(2)

        # Actualizar historial local
        history.append(p_url)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        
        console.print(f"[green]✓ Playlist {p_url} completada.[/green]")

    console.print("\n[bold green]🏁 Pipeline finalizado con exito.[/bold green]")

```

---

## modules/pkm_manager.py
**Lineas: 90**

```python
import os
import tempfile
import subprocess
from typing import List, Optional

from core.database import nx_db, RegistryCreate, TagCreate, SessionLocal
from core.models import ResourceRecord
from rich.console import Console

console = Console()

def create_note(title: str, tags: List[str]) -> Optional[ResourceRecord]:
    """
    Inicia el flujo de creación de una Nota (PKM).
    Abre el bloc de notas (notepad), espera a que el usuario termine la edición,
    cierra el editor y guarda el contenido en la base de datos maestra.
    """
    # 1. Crear un archivo temporal con extensión .md
    fd, temp_path = tempfile.mkstemp(suffix=".md", prefix="nexus_note_", text=True)
    
    # Escribir un encabezado opcional inicial
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\nEscribe tu nota aquí...\n")

    try:
        # 2. Abrir el editor de texto nativo de forma bloqueante
        console.print(f"\n[bold cyan]Abriendo editor para la nota:[/bold cyan] '{title}'...")
        console.print("[yellow]La terminal está en espera. Cierra el bloc de notas para guardar...[/yellow]\n")
        
        # subprocess.run es bloqueante por defecto
        subprocess.run(['notepad', temp_path], check=True)
        
    except Exception as e:
        console.print(f"[bold white on red]Error al intentar abrir el editor:[/] {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None
        
    # 3. Leer el contenido modificado tras cerrar el editor
    with open(temp_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        
    # 4. Limpieza: Borrar el archivo temporal (no almacenamos binarios)
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    # Si la nota quedó vacía o con el texto por defecto, la abortamos para no ensuciar la BD
    if not content or content == f"# {title}\n\nEscribe tu nota aquí...":
        console.print("[bold white on red]La nota está vacía o sin cambios. Abortando guardado.[/]")
        return None
        
    # 5. Mapear los datos al esquema de Pydantic y guardarlos a la BD
    note_data = RegistryCreate(
        type="note",
        title=title,
        # Path URI lógico en lugar de físico, ya que su info resida en la DB directamente.
        path_url=f"nexus://note/{title.replace(' ', '_').lower()}",
        content_raw=content,
        meta_info={"extension": "md", "source": "pkm_manager"}
    )
    
    # Inyectar a la base de datos usando nuestro CRUD
    reg = nx_db.create_registry(note_data)
    
    # Inyectar las etiquetas asociadas (Asegurando limpiar mayúsculas y espacios)
    for tag_val in tags:
        tag_clean = tag_val.strip().lower()
        if tag_clean:
            nx_db.add_tag(reg.id, TagCreate(value=tag_clean))
            
    # Empaquetamos al modelo maestro Pydantic (basado en el Blueprint)
    rr = ResourceRecord(
        id=reg.id,
        type=reg.type,
        title=reg.title or "",
        path_url=reg.path_url or "",
        content_raw=reg.content_raw,
        metadata_dict=reg.meta_info if reg.meta_info else {},
        created_at=reg.created_at,
        modified_at=reg.modified_at
    )
    
    console.print(f"✅ Nota '{title}' guardada exitosamente en la DB con el ID {reg.id} y {len(tags)} etiqueta(s).")
    return rr

if __name__ == "__main__":
    # Prueba de compilación directa y bloqueo
    # Descomentar para probar sin llamar desde el dashboard
    # create_note("Mi Primera Nota Nexus", ["pkm", "test", "zettelkasten"])
    pass

```

---

## modules/study_engine.py
**Lineas: 443**

```python
import time
import os
import subprocess
import webbrowser
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Asumiendo que el script principal establece la raíz del proyecto para importaciones
from core.database import nx_db, Card, Registry

from rich.theme import Theme

# Tema de alto contraste para visibilidad absoluta
custom_theme = Theme({
    "dim": "bright_white",
    "cyan": "bright_cyan",
    "magenta": "yellow",
    "blue": "bright_blue",
})

console = Console(theme=custom_theme)

class SRSEngine:
    def __init__(self):
        pass

    def calculate_next_review(self, card: Card, grade: int, elapsed_seconds: float):
        """
        Calcula y actualiza los factores SRS de la tarjeta (stability, difficulty, dates)
        incorporando el tiempo de respuesta. Si el usuario tardó mucho pero marcó 'Fácil', 
        se penaliza la respuesta para no incrementar tanto el intervalo de retención.
        """
        # Grade: 1 (Difícil), 2 (Bien), 3 (Fácil)
        # Ajuste penalizando 'Fácil' si tomó mucho tiempo (ej > 15 segs)
        if grade == 3 and elapsed_seconds > 15.0:
            # Penalizar convirtiendo en un "Bien" virtual para el cálculo de estabilidad
            grade_calc = 2.5
        else:
            grade_calc = float(grade)
        
        # Algoritmo simple inspirado en FSRS/SM-2
        
        if card.stability == 0.0 or card.stability is None:
             # Valores iniciales (en días)
             initial_stability = {1: 1.0, 2: 3.0, 3: 5.0, 2.5: 4.0}
             card.stability = initial_stability.get(grade_calc, 3.0)
             card.difficulty = 5.0 - grade_calc # 1 -> 4, 2 -> 3, 3 -> 2
        else:
             modifier = {1: 0.5, 2: 1.5, 2.5: 1.8, 3: 2.5}.get(grade_calc, 1.5)
             card.stability = max(1.0, card.stability * modifier)
             card.difficulty = max(1.0, min(10.0, card.difficulty + (2.0 - grade_calc) * 0.5))

        # Calcular próxima fecha
        interval_days = card.stability
        card.last_review = datetime.now(timezone.utc)
        card.next_review = card.last_review + timedelta(days=interval_days)


def open_source_material(registry):
    """
    Abre o muestra el material fuente asociado a un registro cruzando local y web.
    """
    path_or_url = str(registry.path_url).strip() if registry.path_url else ""
    
    # 1. Si es un Link de Internet (YouTube/Web) -> Navegador Default
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        import webbrowser
        webbrowser.open(path_or_url)
    
    # 2. Si es una Ruta Física Local (Archivo PDF/Nota) -> Lanzar programa local
    elif path_or_url and os.path.exists(path_or_url):
        try:
            if os.name == 'nt':
                os.startfile(os.path.normpath(path_or_url))  # Intento normal en Windows
            else:
                import subprocess
                subprocess.run(['xdg-open', path_or_url]) 
        except Exception as e:
            # Fallback para WinError 1155 (Sin asociación) o errores similares
            if os.name == 'nt':
                console.print(f"[yellow]Aviso: No hay una app predeterminada para este archivo. Abriendo selector...[/]")
                os.system(f'rundll32.exe shell32.dll,OpenAs_RunDLL {os.path.normpath(path_or_url)}')
            else:
                console.print(f"[bold red]Error al abrir el archivo:[/] {e}")
                time.sleep(2)
            
    # 3. Si no tiene archivo físico sino que es una mera "Nota" de texto en la Base de Datos
    elif registry.content_raw and registry.content_raw.strip():
        import tempfile
        import subprocess
        
        # Crear un archivo markdown temporal para que el OS lo abra
        fd, temp_path = tempfile.mkstemp(suffix=".md", prefix="nota_virtual_")
        
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(f"# {registry.title}\n\n")
            f.write(registry.content_raw)
            
        try:
            if os.name == 'nt':
                console.print(f"[bold cyan]Forzando la selección de visor de Markdown para '{registry.title}'...[/]")
                console.print("[dim]Por favor, selecciona 'Markdown Viewer' (o tu app preferida) en la ventana que aparecerá y marca 'Siempre usar esta aplicación' para que en el futuro sea automático.[/dim]")
                time.sleep(1)
                
                # Invoca el cuadro de "Abrir con..." nativo de Windows para forzar la vinculación
                os.system(f'rundll32.exe shell32.dll,OpenAs_RunDLL {temp_path}')
            else:
                import subprocess
                subprocess.run(['xdg-open', temp_path])
        except Exception as e:
            console.print(f"[bold red]Aviso: No se pudo abrir la app. Error: {e}[/]")
            console.print(Panel(registry.content_raw[:1500] + ("..." if len(registry.content_raw) > 1500 else ""), title=f"Nota Virtual: {registry.title}", border_style="yellow"))
        
    else:
        console.print("[bold white on red]Este Registro no tiene archivo físico local, Ni un link Web, Ni contenido de texto.[/]")
        
    Prompt.ask("\n[bold]Presiona Enter para continuar con la sesión...[/]", console=console)

def get_due_cards(session, adelantar=False, topic_id=None, shuffled=False, card_limit=None):
    """
    Obtiene las tarjetas programadas para repaso, filtrando opcionalmente por un Registro/Tema.
    """
    now = datetime.now(timezone.utc)
    query = session.query(Card)
    if topic_id is not None:
        query = query.filter(Card.parent_id == topic_id)
        
    if not adelantar:
        # Filtra las que no tengan fecha o cuya fecha esté en el pasado/presente
        query = query.filter((Card.next_review == None) | (Card.next_review <= now))
    
    if shuffled:
        import random
        cards = query.all()
        random.shuffle(cards)
    else:
        cards = query.order_by(Card.next_review).all()

    if card_limit and card_limit > 0:
        cards = cards[:card_limit]
        
    return cards

def start_pomodoro_session(pomodoro_minutes: int = 25, adelantar: bool = False, topic_id: int = None, skip_first_source_prompt: bool = False, shuffled: bool = False, card_limit: int = None):
    """
    Inicia una sesión de Active Recall bajo el método Pomodoro.
    """
    srs = SRSEngine()
    start_time = time.time()
    duration_secs = pomodoro_minutes * 60
    
    with nx_db.Session() as session:
        cards = get_due_cards(session, adelantar=adelantar, topic_id=topic_id, shuffled=shuffled, card_limit=card_limit)
        
        if not cards:
            if session.query(Card).count() == 0:
                console.print("\n[bold white on red]¡Tu Sistema no tiene Flashcards![/]")
                console.print("[yellow]Aún no has generado ninguna tarjeta de estudio en toda la base de datos.[/]")
                console.print("[bright_cyan]Idea:[/] Ve al Menú Explorador (Opción 2), abre un registro con [bold]vID[/bold] y usa el agente de IA para generar un mazo de cartas de ese documento.\n")
            else:
                console.print("\n[yellow]No hay tarjetas pendientes para repasar hoy.[/]")
                if not adelantar:
                     console.print("Utiliza la opción 'Adelantar Tarjetas' en el menú principal si quieres forzar la cola de estudio.\n")
            return

        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(f"[bold yellow]🚀 Iniciando Sesión Active Recall (Pomodoro: {pomodoro_minutes} min)[/]\n")
        time.sleep(1.5)

        total_cards = len(cards)
        last_topic_id = None
        cards_to_mutate = []
        for idx, card in enumerate(cards, 1):
            current_time = time.time()
            if current_time - start_time >= duration_secs:
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print(Panel("[bold white on red]¡Tiempo de Pomodoro agotado![/]\n\n"
                                    f"Has estudiado intensamente durante {pomodoro_minutes} minutos.\n"
                                    "¡Toma un descanso y procesa lo aprendido!", 
                                    title="🍅 Pomodoro Finalizado", border_style="red"))
                break
            
            console.clear()
            # Mostrar progreso de tiempo limpio desde cero
            time_left = duration_secs - (current_time - start_time)
            mins, secs = divmod(int(max(0, time_left)), 60)
            
            # Chromatic visual para el tiempo
            color_time = "bright_cyan" if time_left > 300 else "bold white on red"
            
            # Obtener contexto
            reg = session.query(Registry).get(card.parent_id)
            source_title = reg.title if reg else "Desconocido"
            source_url = reg.path_url if reg and reg.path_url else "Sin URL física o Web"
            
            # Formateamos URL para terminales modernas si es link
            disp_url = f"[link={source_url}]{source_url}[/link]" if str(source_url).startswith("http") else source_url
            
            is_new_topic = (card.parent_id != last_topic_id)
            
            # 1. Función Interna para repintar la Cabecera limpidamente y evitar Overlaps
            def draw_header():
                os.system('cls' if os.name == 'nt' else 'clear') # Hard clear en OS
                console.print(f"[{color_time}]⏳ Tiempo restante: {mins:02d}:{secs:02d}[/]  |  [bold yellow]🗂️ Tarjeta {idx} de {total_cards}[/]\n")
                if is_new_topic:
                    console.print(Panel(f"[bold bright_cyan]Tema de Estudio:[/] {source_title}\n[bold bright_cyan]Ubicación/Enlace:[/] {disp_url}\n[yellow](Para navegar hasta esta ubicación, escribe la tecla 'f' en el menú de abajo, o haz Ctrl+Click si la URL es azul)[/yellow]", title="📚 Contexto de la Tarjeta", border_style="bright_cyan"))
                else:
                    console.print(f"[white]📚 Repasando:[/] [bold bright_cyan]{source_title}[/]\n")
                
            draw_header()
            
            # 2. Bucle interactivo para Material Fuente (SOLO si es un tema nuevo en la cola actual)
            if is_new_topic:
                # Si venimos del menú 2 y ya abrimos la fuente antes del pomodoro, omitimos esta molestia en la 1ra tarjeta
                if skip_first_source_prompt and last_topic_id is None:
                    pass
                else:
                    while True:
                        action = Prompt.ask("\n[yellow]¿Deseas leer el tema fuente ahora? ([bold]f[/] para abrir / [bold]Enter[/] para saltar a la Pregunta)[/]", console=console).strip().lower()
                        if action == 'f':
                            if reg:
                                console.print("\n[bright_white]Abriendo material fuente en segundo plano...[/bright_white]")
                                open_source_material(reg)
                                draw_header() # Redibujamos cabecera tras volver
                            else:
                                console.print("[bold white on red]Registro huérfano o no encontrado en la base de datos.[/]")
                                time.sleep(1.5)
                                draw_header()
                        else:
                            break
                # Guardar el tema actual como "último visto"
                last_topic_id = card.parent_id
            
            # 3. Mostrar Pregunta (Lógica de Renderizado Dinámico por Tipo)
            draw_header()
            console.print("")
            
            card_type = str(card.type).lower()
            auto_graded = False
            correct_answer = card.answer
            user_attempt = None

            # --- RENDERIZADO POR TIPO ---
            if "cloze" in card_type or "hueco" in card_type:
                import re
                display_q = re.sub(r"\{\{c\d+::(.*?)\}\}", "[...]", card.question)
                console.print(Panel(display_q, title="❓ Rellenar Huecos", border_style="bright_blue"))
            
            elif "mcq" in card_type or "opcion multiple" in card_type:
                try:
                    import json
                    data = json.loads(card.question)
                    prompt_text = data.get("prompt", "Selecciona la opción correcta:")
                    options = data.get("options", {})
                    console.print(Panel(prompt_text, title="❓ Opción Múltiple", border_style="bright_blue"))
                    for k, v in options.items():
                        console.print(f"  [bold yellow]{k})[/] {v}")
                    auto_graded = True
                except:
                    console.print(Panel(card.question, title="❓ Opción Múltiple (Formato Simple)", border_style="blue"))
            
            elif "tf" in card_type or "verdadero" in card_type:
                console.print(Panel(card.question, title="❓ ¿Verdadero o Falso?", border_style="bright_blue"))
                console.print("  [bold bright_cyan]v)[/] Verdadero")
                console.print("  [bold bright_cyan]f[/]) Falso")
                auto_graded = True

            elif "matching" in card_type or "emparejar" in card_type:
                try:
                    import json
                    data = json.loads(card.question) # p.ej {"pairs": {"Perú": "Lima", "Chile": "Santiago"}}
                    pairs = data.get("pairs", {})
                    left = list(pairs.keys())
                    right = list(pairs.values())
                    import random
                    random.shuffle(right)
                    
                    console.print(Panel("Empareja los términos de la izquierda con la derecha:", title="❓ Emparejamiento", border_style="bright_blue"))
                    for idx, val in enumerate(left, 1):
                        console.print(f"  {idx}. [bold bright_cyan]{val}[/]  <--->  [bold yellow]{chr(96+idx)})[/] {right[idx-1]}")
                    auto_graded = True
                except:
                    console.print(Panel(card.question, title="❓ Emparejamiento", border_style="bright_blue"))

            else:
                # Caso por defecto: Factual/Normal
                console.print(Panel(card.question, title="❓ Pregunta a Resolver", border_style="bright_blue"))
            
            action_start_time = time.time()
            card_needs_grading = True
            
            while True:
                prompt_msg = "\n[yellow]Respuesta (Enter), 'editar', 'eliminar' o 'atras'[/]"
                if auto_graded:
                    prompt_msg = "\n[bold yellow]Tu Elección (ej. 'a', 'b' o 'v'):[/]"
                
                user_answer = Prompt.ask(prompt_msg, console=console)
                u_ans_lower = user_answer.strip().lower()

                if u_ans_lower in ['salir', 'atras', 'regresar']:
                    console.print("\n[yellow]Saliendo de la sesión de Active Recall...[/]")
                    time.sleep(1)
                    card_needs_grading = False
                    break
                
                elif u_ans_lower == 'eliminar':
                    confirm = Prompt.ask("¿Seguro que deseas [bold red]ELIMINAR[/] esta Flashcard permanentemente? (s/n)", console=console).strip().lower()
                    if confirm == 's':
                        session.delete(card)
                        session.commit()
                        console.print("[bold green]✔ Tarjeta eliminada.[/]")
                        time.sleep(1)
                        card_needs_grading = False
                        break
                    else:
                        draw_header()
                        # Re-mostrar
                        continue
                
                elif u_ans_lower == 'editar':
                    console.print("\n[bold bright_cyan]--- Modificando Tarjeta ---[/]")
                    new_q = Prompt.ask("Nueva Pregunta o JSON", default=card.question, console=console).strip()
                    new_a = Prompt.ask("Nueva Respuesta", default=card.answer, console=console).strip()
                    if new_q: card.question = new_q
                    if new_a: card.answer = new_a
                    session.commit()
                    console.print("[bold green]✔ Actualizada.[/]")
                    time.sleep(1)
                    draw_header()
                    continue
                
                else:
                    user_attempt = user_answer
                    break
            
            if not card_needs_grading:
                if u_ans_lower in ['salir', 'atras', 'regresar']:
                    break
                continue 
            
            elapsed_seconds = time.time() - action_start_time
            
            # 4. Mostrar Respuesta y Calificar
            console.print("")
            if user_attempt and user_attempt.strip():
                console.print(f"[bold bright_blue]Tú escribiste/elegiste:[/] {user_attempt}\n")
            
            # Verificación automática
            is_correct = None
            if auto_graded and user_attempt:
                if u_ans_lower == str(card.answer).strip().lower():
                    is_correct = True
                    console.print("[bold green]✅ ¡Correcto![/]")
                else:
                    is_correct = False
                    console.print(f"[bold red]❌ Incorrecto. La respuesta era: {card.answer}[/]")

            console.print(Panel(card.answer, title="💡 Respuesta Correcta", border_style="green"))
            
            # 5. Calificación
            if is_correct is True:
                grade_str = "3" # Fácil
            elif is_correct is False:
                grade_str = "1" # Malo
            else:
                grade_str = Prompt.ask("\nCalifica tu nivel de recuerdo:\n [1] [bold red]Malo/Olvidado[/] \n [2] [bold green]Bueno/Correcto[/] \n [3] [bold bright_cyan]Fácil/Perfecto[/]\n Elije un número", choices=["1", "2", "3"], default="2", console=console)
            
            agrade = {"1": "Malo (Re-estudio)", "2": "Bueno (Repaso normal)", "3": "Fácil (Salto largo)"}[grade_str]
            grade = int(grade_str)
            
            # 6. Actualizar BD
            srs.calculate_next_review(card, grade, elapsed_seconds)
            cards_to_mutate.append(card.id) 
            session.commit()
            
            console.print(f"\n[bold green]✔ Hecho! Próximo repaso: {card.next_review.strftime('%Y-%m-%d %H:%M')}[/]")
            time.sleep(1.5) 
            
        else:
            # Si culminó el loop de tarjetas sin interrupción de tiempo
            os.system('cls' if os.name == 'nt' else 'clear')
            time_total = int(time.time() - start_time)
            mins, secs = divmod(time_total, 60)
            console.print(Panel(f"[bold green]¡Has terminado todas las tarjetas en la cola actual![/]\n\n"
                                f"Tiempo invertido: {mins:02d}m {secs:02d}s",
                                title="🏆 Cola Completada", border_style="green"))

        # ---------------------------------------------------------------------
        # FASE FINAL: Intervención del Agente Mutador (IA) (Acumulación >= 20)
        # ---------------------------------------------------------------------
        if cards_to_mutate:
            import json
            # Definir locación para acumular las tarjetas repasadas
            pending_mutations_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'pending_mutations.json')
            
            # Cargar pendientes anteriores si existen
            pending_cards = []
            if os.path.exists(pending_mutations_file):
                try:
                    with open(pending_mutations_file, 'r', encoding='utf-8') as f:
                        pending_cards = json.load(f)
                except Exception:
                    pass
            
            # Agregar nuevas y quitar duplicados (para no acumular la misma tarjeta en varias sesiones seguidas)
            pending_cards.extend(cards_to_mutate)
            pending_cards = list(set(pending_cards))
            
            # Chequear si llegamos a la meta de al menos 20
            if len(pending_cards) >= 20:
                run_m = Prompt.ask(
                    f"\n[bold yellow]🤖 Has alcanzado el límite para el Mutador ({len(pending_cards)} tarjetas acumuladas).\n"
                    "¿Deseas activar el Agente Mutador de IA para analizarlas y reformularlas (rompiendo la memorización sistemática)?[/] (s/n)",
                    choices=["s", "n"], default="n", console=console
                ).strip().lower()
                
                if run_m == 's':
                    from agents.mutation_agent import mutate_cards
                    mutate_cards(pending_cards)
                    # Tras correr el mutador, vaciamos el acumulador
                    if os.path.exists(pending_mutations_file):
                        os.remove(pending_mutations_file)
                else:
                    # El usuario dijo 'n', guardamos el acumulado para la próxima sesión
                    os.makedirs(os.path.dirname(pending_mutations_file), exist_ok=True)
                    with open(pending_mutations_file, 'w', encoding='utf-8') as f:
                        json.dump(pending_cards, f)
            else:
                # Si no llegó a 20, grabamos el progreso para que se acumulen sin molestar aún
                console.print(f"\n[white]Se han guardado estas tarjetas para futura mutación de la IA (Total acumulado: {len(pending_cards)}/20).[/white]")
                os.makedirs(os.path.dirname(pending_mutations_file), exist_ok=True)
                with open(pending_mutations_file, 'w', encoding='utf-8') as f:
                    json.dump(pending_cards, f)

if __name__ == '__main__':
    # Punto de prueba aislado para testing rápido
    try:
        start_pomodoro_session(25, adelantar=False)
    except KeyboardInterrupt:
        console.clear()
        console.print("[yellow]Sesión interrumpida por el usuario.[/yellow]")

```

---

## modules/web_scraper.py
**Lineas: 267**

```python
import re
from urllib.parse import urlparse, parse_qs
from core.database import nx_db, RegistryCreate, TagCreate
from rich.console import Console

console = Console()

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

def ingest_web_resource(url: str, tags: list[str], db_target=nx_db):
    """
    Determina si la URL es de YouTube o una página web genérica,
    extrae el contenido y lo guarda en la base de datos especificada (Local o Staging).
    """
    if not requests or not BeautifulSoup:
        console.print("[bold white on red]Faltan librerías. Por favor instala: requests y beautifulsoup4[/]")
        return None

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    if "youtube.com" in domain or "youtu.be" in domain:
        try:
            return _ingest_youtube(url, parsed_url, tags, db_target)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  Descarga de YouTube interrumpida (Ctrl+C).[/bold yellow]")
            return None
    else:
        try:
            return _ingest_generic_web(url, tags, db_target)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  Descarga web interrumpida (Ctrl+C).[/bold yellow]")
            return None

def _get_youtube_video_id(url: str, parsed_url) -> str:
    """Extrae el ID del video de YouTube a partir de la URL."""
    if "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip('/')
    if "youtube.com" in parsed_url.netloc:
        qs = parse_qs(parsed_url.query)
        if 'v' in qs:
            return qs['v'][0]
    return ""

def _ingest_youtube(url: str, parsed_url, tags: list[str], db_target):
    """Extrae título y subtítulos de un video de YouTube."""
    if not YouTubeTranscriptApi or not yt_dlp:
        console.print("[bold white on red]Faltan librerías para YouTube. Instala: youtube-transcript-api y yt-dlp[/]")
        return None
        
    video_id = _get_youtube_video_id(url, parsed_url)
    if not video_id:
        console.print(f"[yellow]No se pudo extraer de ID de video de YouTube para: {url}[/yellow]")
        return None
        
    title = f"YouTube Video ({video_id})"
    content_raw = ""
    
    # Intentar obtener métricas y metadatos usando yt-dlp
    meta_info = {"video_id": video_id, "platform": "youtube"}
    try:
        class MyLogger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        ydl_opts = {
            'quiet': True, 
            'no_warnings': True, 
            'logger': MyLogger(),
            'extract_flat': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict:
                title = info_dict.get('title', title)
                meta_info.update({
                    "channel": info_dict.get('uploader'),
                    "duration": info_dict.get('duration'),
                    "view_count": info_dict.get('view_count'),
                    "upload_date": info_dict.get('upload_date'),
                    "description": info_dict.get('description', '')[:500] # Primeras lineas
                })
    except Exception as e:
        # Fallback silencioso para el título si yt-dlp falla
        pass

    # Obtener transcripción
    try:
        # Intenta primero español, luego inglés si falla u otros.
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        # Buscar transcript manual antes de los generados (idioma es o en)
        try:
            transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
        except Exception:
            # Si no encuentra manual, agarrar cualquiera o el generado
            try:
                transcript = transcript_list.find_generated_transcript(['es', 'en'])
            except:
                # Si no hay es/en, agarrar el primero disponible
                transcript = next(iter(transcript_list))
            
        full_transcript = transcript.fetch()
        
        text_fragments = [item.text if hasattr(item, "text") else item["text"] for item in full_transcript]
        content_raw = " ".join(text_fragments)
        
        if len(content_raw) > 50000:
            content_raw = content_raw[:49997] + "..."
            
    except Exception as e:
        error_msg = str(e).split('\n')[0] or type(e).__name__
        console.print(f"[yellow]Aviso: No se pudo obtener la transcripción. Se guardará sin texto base. ({error_msg})[/yellow]")
        content_raw = "(Video guardado sin Transcripción Disponible)."

    # Insertar en BD
    try:
        data = RegistryCreate(
            type="youtube",
            title=title,
            path_url=url,
            content_raw=content_raw,
            meta_info=meta_info
        )
        reg = db_target.create_registry(data)
        
        # Asociar tags
        for t in tags:
            db_target.add_tag(reg.id, TagCreate(value=t))
            
        return reg
    except Exception as e:
        console.print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return None

def get_playlist_video_urls(playlist_url: str):
    """
    Usa yt-dlp para obtener todas las URLs de videos de una playlist.
    """
    urls = []
    try:
        class MyLogger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'logger': MyLogger(),
            'extract_flat': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            if 'entries' in playlist_info:
                for entry in playlist_info['entries']:
                    if entry.get('url'):
                        # yt-dlp a veces devuelve solo el ID o el path, aseguramos URL completa
                        video_url = entry['url']
                        if not video_url.startswith('http'):
                            video_url = f"https://www.youtube.com/watch?v={video_url}"
                        urls.append(video_url)
    except Exception as e:
        console.print(f"[red]Error extrayendo playlist: {e}[/]")
    return urls

def batch_ingest_urls(urls_list: list[str], tags: list[str], db_target=nx_db):
    """
    Procesa un lote de URLs secuencialmente.
    Retorna (un proceso exitoso, un proceso fallido).
    """
    total = len(urls_list)
    success = []
    failed = []
    
    try:
        for i, url in enumerate(urls_list):
            url = url.strip()
            if not url: continue
            
            console.print(f"\n[bold cyan][{i+1}/{total}][/] Procesando: [dim]{url}[/]")
            reg = ingest_web_resource(url, tags, db_target=db_target)
            if reg:
                success.append(reg)
            else:
                failed.append(url)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⚠️  Proceso de ingesta por lote interrumpido por el usuario (Ctrl+C).[/bold yellow]")
        console.print(f"[white]Se han guardado {len(success)}/{(i+1) if 'i' in locals() else len(urls_list)} registros procesados hasta ahora.[/white]")
            
    return success, failed


def _ingest_generic_web(url: str, tags: list[str], db_target):
    """Extrae título y párrafos limpiados de una página web."""
    try:
        # Añadir cabeceras comunes para evitar bloqueos básicos de web servers (403 Prohibidden)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        console.print(f"[yellow]Aviso: Ocurrió un error conectando a la página (puede requerir JS o estar bloqueada). Se guardará la URL huérfana. Error: {str(e)}[/yellow]")
        # Guardado básico de rescate para url
        try:
            reg = db_target.create_registry(RegistryCreate(
                type="web", title=url, path_url=url, content_raw="Error al raspar el contenido web."
            ))
            for t in tags:
                db_target.add_tag(reg.id, TagCreate(value=t))
            return reg
        except:
             return None
             
    soup = BeautifulSoup(res.text, 'html.parser')

    # Obtener el Título
    title = soup.title.string.strip() if soup.title and soup.title.string else url

    # Limpiar tags basura que no aportan al raw text
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()

    # Extraer texto de párrafos y divs de manera legible
    paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
    content_raw = "\n\n".join([p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    if len(content_raw) > 50000:
            content_raw = content_raw[:49997] + "..."
            
    try:
        data = RegistryCreate(
            type="web",
            title=title,
            path_url=url,
            content_raw=content_raw,
            meta_info={"platform": "web"}
        )
        reg = db_target.create_registry(data)
        
        for t in tags:
            db_target.add_tag(reg.id, TagCreate(value=t))
            
        return reg
    except Exception as e:
        console.print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return None

```

---

## modules/youtube_manager.py
**Lineas: 80**

```python

import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Permisos necesarios para gestionar playlists (Lectura y Escritura)
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

class YouTubeManager:
    """
    Gestor oficial de YouTube via Data API v3.
    Permite leer, listar y ELIMINAR videos de playlists (limpieza de cola).
    """
    def __init__(self, credentials_path='client_secrets.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.youtube = self._authenticate()

    def _authenticate(self):
        creds = None
        # El archivo token.pickle almacena los tokens de acceso y refresco del usuario
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales validas, pedir login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"No se encontro '{self.credentials_path}'. Necesitas descargar este archivo desde Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('youtube', 'v3', credentials=creds)

    def get_playlist_items(self, playlist_id):
        """Lista todos los videos (IDs y URLs) de una playlist."""
        videos = []
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            playlist_item_id = item['id'] # Necesario para eliminarlo luego
            title = item['snippet']['title']
            videos.append({
                'id': video_id,
                'playlist_item_id': playlist_item_id,
                'title': title,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            })
        return videos

    def remove_video_from_playlist(self, playlist_item_id):
        """Elimina un video de la playlist usando su ID de item (no el ID de video)."""
        try:
            self.youtube.playlistItems().delete(id=playlist_item_id).execute()
            return True
        except Exception as e:
            print(f"Error al eliminar video de la playlist: {e}")
            return False

    def get_playlist_id_from_url(self, url):
        """Extrae el ID de la playlist de una URL."""
        from urllib.parse import urlparse, parse_qs
        query = urlparse(url).query
        params = parse_qs(query)
        return params.get('list', [None])[0]

```

---

## ui/dashboard.py
**Lineas: 1874**

```python
import sys
import time

# Forzar salida en UTF-8 para evitar errores de renderizado de Emojis en la terminal de Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.align import Align
from rich import box
from rich.text import Text
from rich.theme import Theme

# Tema personalizado de ALTO CONTRASTE para visibilidad total en terminales azules/oscuras
custom_theme = Theme({
    "dim": "bright_white",
    "cyan": "bright_cyan",
    "magenta": "yellow",
    "blue": "bright_blue",
    "prompt.choices": "bold yellow",
    "prompt.default": "bold bright_white",
    "prompt.invalid": "bold red",
    "prompt.invalid.choice": "bold white on red",
})

console = Console(theme=custom_theme)

import os
import subprocess
import msvcrt

def get_key() -> str:
    """Captura un solo carácter del teclado sin esperar a Enter (Solo Windows).
    Retorna 'left' / 'right' para teclas de flecha, o el carácter en minúsculas.
    """
    if sys.platform == "win32":
        try:
            char = msvcrt.getch()
            # Secuencias de escape: flechas devuelven 0x00 o 0xE0 + código
            if char in [b'\x00', b'\xe0']:
                ext = msvcrt.getch()
                if ext == b'K': return "left"   # Flecha izquierda
                if ext == b'M': return "right"  # Flecha derecha
                if ext == b'H': return "up"     # Flecha arriba
                if ext == b'P': return "down"   # Flecha abajo
                return ""  # Otro código especial ignorado
            return char.decode('utf-8').lower()
        except Exception:
            return ""
    return ""

from modules.file_manager import ingest_local_file
from modules.web_scraper import ingest_web_resource
from modules.pkm_manager import create_note
from core.search_engine import search_registry, parse_query_string
from core.database import SessionLocal, nx_db, CardCreate, NexusLinkCreate
from agents.relationship_agent import generate_relationship_cards
from modules.study_engine import start_pomodoro_session, open_source_material
from modules.analytics import get_global_metrics
from modules.exporter import export_to_google_drive
from core.staging_db import staging_db, STAGING_DB_PATH
from modules.pipeline_manager import run_youtube_pipeline

import logging

logging.basicConfig(
    filename="nexus.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexus.ui")


class ReturnToMain(Exception):
    """Señal de navegación para volver al menú principal desde cualquier profundidad."""
    pass

# ----------------------------------------------------------------------------
# 1. Componentes Visuales del Dashboard
# ----------------------------------------------------------------------------

def show_header():
    """Muestra el banner principal de Nexus."""
    os.system('cls' if os.name == 'nt' else 'clear')
    title = Text("N E X U S", style="bold bright_cyan", justify="center")
    subtitle = Text("Cognitive Storage & active Recall Console", style="italic bright_white", justify="center")
    
    header_content = Text.assemble(title, "\n", subtitle)
    console.print(Panel(header_content, box=box.DOUBLE, border_style="bright_cyan", expand=False))
    console.print()

def get_stats_panel(active_filters: str = "") -> Panel:
    """Retorna un Panel Rich con estadísticas reales consultadas desde la BD."""
    metrics = get_global_metrics()
    
    from rich.columns import Columns
    
    total_raw = metrics["registry_counts"].get("total", 0)
    cards_today = metrics["srs"]["due_today"]
    sys_links = metrics["network"]["total_links"]
    retention = metrics["srs"]["retention_desc"]

    filter_display = f"[bold yellow]{active_filters}[/]" if active_filters else "[bright_white]Ninguno[/]"

    stats_cols = Columns([
        Panel(f" [bold bright_cyan]{total_raw}[/]\n [white]Recursos[/]", title="🗄️ Cerebro", border_style="bright_cyan", padding=(1, 2)),
        Panel(f" [bold white on red] {cards_today} [/]\n [white]Repasos Hoy[/]", title="🧠 Foco", border_style="red", padding=(1, 2)),
        Panel(f" [bold yellow]{sys_links}[/]\n [white]Vínculos[/]", title="🔗 Red", border_style="yellow", padding=(1, 2)),
        Panel(f" [bold green]{retention}[/]\n [white]Madurez[/]", title="📈 Estado", border_style="green", padding=(1, 2)),
        Panel(f" {filter_display}\n [white]Filtro Activo[/]", title="🔍 Filtro", border_style="white", padding=(1, 2)),
    ], align="center", expand=False)

    return Panel(
        Align.center(stats_cols),
        title="[bold white]CUADRO DE MANDO COGNITIVO[/]",
        border_style="white",
        expand=True
    )


# ----------------------------------------------------------------------------
# 2. Sub-Menús y Flujos de Usuario
# ----------------------------------------------------------------------------

def menu_agregar():
    """
    [1] AGREGAR ARCHIVOS A LA BD
    Captura y almacena nuevo contenido en la base de datos.
    """
    current_target = "local"
    
    while True:
        console.clear()
        show_header()
        
        target_color = "green" if current_target == "local" else "bold white on gold3"
        target_name = "CORE (Local SSD)" if current_target == "local" else f"BUFFER (Nube G: {STAGING_DB_PATH})"
        
        # Resumen de filtros permanentes en el header
        console.print(Align.center(get_stats_panel()))
        console.print()
        console.print(Panel(
            f"[bold yellow]📂 AGREGAR ARCHIVOS A LA BD[/]\n"
            f"Destino Actual: [{target_color}]{target_name}[/]\n\n"
            f"Selecciona el tipo de recurso a indexar:", 
            box=box.ROUNDED,
            title="[bold bright_cyan]Componente 1[/]"
        ))
        
        console.print("  [bold bright_cyan][1][/] 📄 Añadir Archivo Local [dim](manual / Lote desde archivo .txt)[/]")
        console.print("  [bold bright_cyan][2][/] 🌐 Añadir URL (Web/YouTube) [dim](manual / Lote de URLs)[/]")
        console.print("  [bold bright_cyan][3][/] 📝 Escribir Nota Libre [dim](abre editor externo)[/]")
        console.print("  [bold bright_cyan][4][/] ⚙️  Añadir Aplicación / Herramienta")
        console.print("  [bold bright_cyan][6][/] 🤖 Pipeline Automatizado (YouTube) [dim](playlists, descarga, resumen, flashcards)[/]")
        console.print(f"  [bold yellow][S][/] Cambiar Destino → {'Buffer G:' if current_target=='local' else 'Nexus Core'}")
        console.print("  [bold white][0][/] 🔙 Volver al Menú Principal\n")

        opcion = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4", "6", "s", "S"], show_choices=False, console=console).lower()

        if opcion == "0":
            break
            
        if opcion == "s":
            if current_target == "local":
                if staging_db.init_staging():
                    current_target = "staging"
                    console.print("[bold yellow]🚀 ¡Modo STAGING Activado! Los datos irán a la unidad G:[/]")
                else:
                    console.print("[bold red]Error: No se puede activar Staging. ¿Está el drive G: montado?[/]")
            else:
                current_target = "local"
                console.print("[bold green]Modo CORE Local reactivado.[/]")
            time.sleep(1.2)
            continue

        db_active = nx_db if current_target == "local" else staging_db

        if opcion == "1":
            while True:
                try:
                    ruta = Prompt.ask("\n[bold]Ruta absoluta del archivo[/bold]", console=console)
                    if not ruta.strip():
                        console.print("[yellow]⚠ Ruta vacía. Operación cancelada.[/yellow]")
                        time.sleep(1)
                        continue
                    tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                    tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                    
                    # Note: Local files always go to Local Core for now as path references are local
                    try:
                        resultado = ingest_local_file(ruta, tags_list)
                    except Exception as e:
                        console.print(f"\n[bold red]❌ Error de ingestión:[/] {e}")
                        logger.exception("Fallo en ingest_local_file")
                        resultado = None
                    if resultado is not None:
                        console.print(f"\n[bold green]✅ Archivo indexado correctamente:[/] {resultado.title}")
                        
                        summary_text = Text()
                        summary_text.append(f"ID: ", style="bold bright_cyan")
                        summary_text.append(f"{resultado.id}\n", style="white")
                        summary_text.append(f"Tipo: ", style="bold bright_cyan")
                        summary_text.append(f"{resultado.type}\n", style="white")
                        summary_text.append(f"Título: ", style="bold bright_cyan")
                        summary_text.append(f"{resultado.title}\n", style="white")
                        summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                        summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                        
                        if resultado.content_raw:
                            content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                            summary_text.append(f"Vista Previa del Contenido:\n", style="bold green")
                            summary_text.append(content_preview, style="white")
                        else:
                            summary_text.append(f"Contenido: ", style="bold green")
                            summary_text.append("No se pudo extraer texto (Archivo binario o ilegible).", style="white italic")

                        console.print(Panel(summary_text, title="Detalles del Archivo", border_style="green"))
                        
                        if Prompt.ask("\n¿Deseas editar o ver los detalles completos de este registro ahora? (s/n)", choices=["s", "n"], default="n") == 's':
                            _show_record_detail(resultado.id)
                    else:
                        console.print("\n[bold white on red]❌ No se pudo indexar. Verifica la ruta o los permisos.[/]")
                        
                    action_str = Prompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRO archivo local | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False, console=console)
                    action = int(action_str)
                    if action == 1:
                        continue
                    elif action == 2:
                        break
                    elif action == 0:
                        return
                except (KeyboardInterrupt, EOFError):
                    console.print("\n[yellow]Operación abortada por usuario -> Redireccionando...[/yellow]")
                    time.sleep(1)
                    break
                
        elif opcion == "2":
            while True:
                try:
                    url = Prompt.ask("\n[bold]Pega la URL (YouTube o Genérica)[/bold]", console=console)
                    if not url.strip():
                        console.print("[yellow]⚠ URL vacía. Operación cancelada.[/yellow]")
                        time.sleep(1)
                        continue
                    tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                    tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                    
                    console.print(f"\n[bright_cyan]Iniciando raspado contextual y transcripción hacia {current_target.upper()}...[/]")
                    try:
                        with console.status("[bright_white]Descargando Súper Schema de Web, por favor espera...[/bright_white]", spinner="dots"):
                             resultado = ingest_web_resource(url, tags_list, db_target=db_active)
                    except Exception as e:
                        console.print(f"\n[bold red]❌ Error de ingestión web:[/] {e}")
                        logger.exception("Fallo en ingest_web_resource")
                        resultado = None
                         
                    if resultado is not None:
                         console.print(f"\n[bold green]✅ Recurso Web indexado exitosamente en la Knowledge Base.[/bold green]")
                         
                         # Mostrar lo descargado al usuario
                         summary_text = Text()
                         summary_text.append(f"ID: ", style="bold bright_cyan")
                         summary_text.append(f"{resultado.id}\n", style="white")
                         summary_text.append(f"Tipo: ", style="bold bright_cyan")
                         summary_text.append(f"{resultado.type}\n", style="white")
                         summary_text.append(f"Título: ", style="bold bright_cyan")
                         summary_text.append(f"{resultado.title}\n", style="white")
                         summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                         summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                         
                         if resultado.content_raw:
                             content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                             summary_text.append(f"Contenido Extraído:\n", style="bold green")
                             summary_text.append(content_preview, style="white")
                         else:
                             summary_text.append("Contenido: ", style="bold green")
                             summary_text.append("No se pudo extraer contenido de esta URL.", style="white italic")
                         
                         console.print(Panel(summary_text, title="Detalles de Ingesta", border_style="green"))
                         
                         if Prompt.ask("\n¿Deseas editar o ver los detalles completos de este registro ahora? (s/n)", choices=["s", "n"], default="n", console=console) == 's':
                             _show_record_detail(resultado.id)
    
                    else:
                         console.print("\n[bold white on red]❌ Hubo un fallo en la ingesta o no se pudo generar el texto principal de la URL.[/]")
                         
                    action_str = Prompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRA URL | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False, console=console)
                    action = int(action_str)
                    if action == 1:
                        continue
                    elif action == 2:
                        break
                    elif action == 0:
                        return
                except (KeyboardInterrupt, EOFError):
                    console.print("\n[yellow]Operación abortada por usuario -> Redireccionando...[/yellow]")
                    time.sleep(1)
                    break
                
        elif opcion == "3":
            while True:
                try:
                    titulo = Prompt.ask("\n[bold]Título de la Nueva Nota[/bold]", console=console)
                    tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                    tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                    
                    console.print("\n[bright_white]Abriendo el sistema nativo. Al cerrar la ventana, tu nota se guardará automáticamente...[/bright_white]")
                    
                    try:
                        resultado = create_note(titulo, tags_list)
                    except Exception as e:
                        console.print(f"\n[bold red]❌ Error al crear nota:[/] {e}")
                        logger.exception("Fallo en create_note")
                        resultado = None
                    if resultado is not None:
                        console.print(f"\n[bold green]✅ Nota \"{resultado.title}\" almacenada en Knowledge Base.[/bold green]")
                        
                        summary_text = Text()
                        summary_text.append(f"ID: ", style="bold bright_cyan")
                        summary_text.append(f"{resultado.id}\n", style="white")
                        summary_text.append(f"Tipo: ", style="bold bright_cyan")
                        summary_text.append(f"nota_libre\n", style="white") # create_note returns a Registry object usually, check it
                        summary_text.append(f"Título: ", style="bold bright_cyan")
                        summary_text.append(f"{resultado.title}\n", style="white")
                        summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                        summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                        
                        if resultado.content_raw:
                            content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                            summary_text.append(f"Contenido de la Nota:\n", style="bold green")
                            summary_text.append(content_preview, style="white")
                        else:
                            summary_text.append("Nota: ", style="bold green")
                            summary_text.append("Sin contenido capturado.", style="white italic")
                        
                        console.print(Panel(summary_text, title="Detalles de la Nota", border_style="green"))
                        
                        if Prompt.ask("\n¿Deseas editar o ver los detalles completos de esta nota ahora? (s/n)", choices=["s", "n"], default="n") == 's':
                            _show_record_detail(resultado.id)
                    else:
                        console.print("\n[yellow]⚠️ Nota cancelada. No se guardó nada.[/yellow]")
                        
                    action_str = Prompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Escribir OTRA nota | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                    action = int(action_str)
                    if action == 1:
                        continue
                    elif action == 2:
                        break
                    elif action == 0:
                        return
                except (KeyboardInterrupt, EOFError):
                    console.print("\n[yellow]Operación abortada por usuario -> Redireccionando...[/yellow]")
                    time.sleep(1)
                    break
                
        elif opcion == "6":
            # 1.6 Pipeline Automatizado (YouTube)
            console.print("\n[bold bright_cyan]Iniciando Pipeline Automatizado de YouTube...[/]")
            try:
                with console.status("[white]Procesando playlists en cola...[/white]", spinner="dots"):
                    run_youtube_pipeline()
            except Exception as e:
                console.print(f"\n[bold red]❌ Error en pipeline YouTube:[/] {e}")
                logger.exception("Fallo en run_youtube_pipeline")
            Prompt.ask("\n[bold]Pipeline finalizado. Enter para continuar...[/bold]", console=console)


        elif opcion == "4":
            while True:
                try:
                    console.print("\n[bold yellow]Añadir Aplicación o Herramienta[/]")
                    titulo = Prompt.ask("\n[bold]Nombre de la App / Plataforma[/bold]", console=console)
                    ruta = Prompt.ask("[bold]Ruta / URL o Comando de Ejecución[/bold]", console=console)
                    
                    # Nuevos campos solicitados por Arquitecto:
                    plataforma_input = Prompt.ask("[bold]Plataforma[/] (ej. PC, Android, Web)", default="PC", console=console)
                    logueo = Prompt.ask("[bold]¿Requiere Credenciales / Logueo?[/] (s/n)", default="n", console=console).lower() == 's'
                    logueo_str = "Sí" if logueo else "No"
                    descripcion = Prompt.ask("[bold]Breve Descripción o Uso Principal[/] (opcional)", console=console)
                    
                    tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                    tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                    
                    try:
                        from core.database import RegistryCreate, TagCreate
                        
                        # Construir bloque de texto para Active Recall 
                        content_blob = (
                            f"Herramienta o Aplicación: {titulo}\n"
                            f"Plataforma: {plataforma_input.strip()}\n"
                            f"Requiere Logueo: {logueo_str}\n"
                            f"Ruta o Comando: {ruta}\n"
                        )
                        if descripcion:
                            content_blob += f"Descripción: {descripcion.strip()}\n"
    
                        data = RegistryCreate(
                            type="app",
                            title=titulo,
                            path_url=ruta,
                            content_raw=content_blob,
                            meta_info={
                                "platform_type": plataforma_input.strip(),
                                "requires_login": logueo,
                                "app_description": descripcion.strip() if descripcion else ""
                            }
                        )
                        reg = nx_db.create_registry(data)
                        for t in tags_list:
                            nx_db.add_tag(reg.id, TagCreate(value=t))
                        console.print(f"\n[bold green]✅ Aplicación '{titulo}' (ID {reg.id}) registrada correctamente en la base de datos.[/bold green]")
                    except Exception as e:
                        console.print(f"\n[bold white on red]❌ Error al guardar la aplicación: {str(e)}[/]")
    
                    action_str = Prompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Añadir OTRA Aplicación | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                    action = int(action_str)
                    if action == 1:
                        continue
                    elif action == 2:
                        break
                    elif action == 0:
                        return
                except (KeyboardInterrupt, EOFError):
                    console.print("\n[yellow]Operación abortada por usuario -> Redireccionando...[/yellow]")
                    time.sleep(1)
                    break

# Alias de compatibilidad (por si algún módulo importa el nombre antiguo)
def menu_ingreso():
    menu_agregar()

def menu_explorar(initial_query: str = ""):
    """Alias de compatibilidad — redirige a menu_gestionar."""
    menu_gestionar(initial_query=initial_query)

def menu_gestionar(initial_query: str = ""):
    """[2] GESTIONAR ARCHIVOS EN LA BD
    Explorador Maestro con paginación, filtros, tabla extendida, detalle de registro
    y red neuronal integrada (vincular registros).
    Controles: ←/→ págs | Q filtrar | L limpiar | [ID] ver detalle | del borrar | m/ia vincular
    """
    page = 0
    items_per_page = 10  # Reducido para acomodar más columnas

    filtros = {
        'inc_name': "", 'exc_name': "", 'inc_tags': "", 'exc_tags': "",
        'inc_exts': "", 'exc_exts': "", 'has_info': "", 'inc_ids': "", 'is_source': ""
    }

    if initial_query:
        filtros = parse_query_string(initial_query)

    while True:
        console.clear()
        show_header()

        # Header con filtros activos
        filtro_str = initial_query or " | ".join(f"{k}={v}" for k, v in filtros.items() if v) or ""
        console.print(Align.center(get_stats_panel(active_filters=filtro_str)))
        console.print()

        inc_exts_list = [e.strip() for e in filtros['inc_exts'].split(',')] if filtros['inc_exts'] else None
        exc_exts_list = [e.strip() for e in filtros['exc_exts'].split(',')] if filtros['exc_exts'] else None

        with SessionLocal() as db_session:
            # Evaluate bounds first if we are deep in paging
            # We must count to clamp max_pages dynamically to fix out of bounds crashes
            limit_var = items_per_page + 1
            offset_var = page * items_per_page
            
            results = search_registry(
                db_session=db_session,
                inc_name_path=filtros['inc_name'],
                exc_name_path=filtros['exc_name'],
                inc_tags=filtros['inc_tags'],
                exc_tags=filtros['exc_tags'],
                inc_extensions=inc_exts_list,
                exc_extensions=exc_exts_list,
                has_info=filtros['has_info'],
                record_ids_str=filtros['inc_ids'],
                is_flashcard_source=filtros['is_source'],
                limit=limit_var,
                offset=offset_var
            )
            
            # Auto-revert logic: if empty results and page > 0, rewind by 1 and re-fetch.
            if len(results) == 0 and page > 0:
                page -= 1
                continue

        has_next = len(results) > items_per_page
        display_results = results[:items_per_page]

        # ── Tabla extendida: ID | Tipo | Título | d(Descripción) | i(Info/Ruta) | m(Modificado) | e(Estado) | Tags | Área
        filtros_activos_str = 'Sí' if any(filtros.values()) else 'No'
        title_str = (
            f"[bold bright_cyan]\ud83d\uddc2\ufe0f GESTIONAR ARCHIVOS (Pág. {page + 1})[/] "
            f"| Filtros: [yellow]{filtros_activos_str}[/] "
            f"| [white]\u2190\u2192 Navegar \u2502 Q Filtrar \u2502 L Limpiar \u2502 [ID] Detalle \u2502 0 Salir[/]"
        )
        table = Table(title=title_str, box=box.ROUNDED, show_lines=True, expand=True)
        table.add_column("ID",    justify="right",  style="bold bright_cyan",  no_wrap=True, width=6)
        table.add_column("Tipo",  style="yellow",   no_wrap=True, width=10)
        table.add_column("Título",style="bold bright_white", ratio=3)
        table.add_column("d",     style="white",    ratio=2)        # Descripción (content_raw preview)
        table.add_column("i",     style="bright_white", ratio=2)    # Info / Ruta-URL
        table.add_column("m",     style="italic green", no_wrap=True, width=12)  # Modificado
        table.add_column("e",     justify="center", no_wrap=True, width=4)       # Estado (recall)
        table.add_column("Tags",  style="yellow",   ratio=2)
        table.add_column("Área",  style="bright_blue", ratio=1)

        with SessionLocal() as s_tags:
            from core.database import Tag as TagModel
            for reg in display_results:
                tag_objs = s_tags.query(TagModel).filter(TagModel.registry_id == reg.id).all()
                tags_str  = ", ".join(t.value for t in tag_objs) if tag_objs else ""
                tags_disp = (tags_str[:28] + "…") if len(tags_str) > 28 else tags_str

                # Área: busca una tag que parezca tema (sin ":", puro texto)
                area_tags = [t.value for t in tag_objs if ":" not in t.value and len(t.value) > 2]
                area_disp = area_tags[0] if area_tags else ""

                d_desc = (reg.content_raw or "").replace("\n", " ")[:40]
                if len(reg.content_raw or "") > 40: d_desc += "…"

                i_info = reg.path_url or ""
                if len(i_info) > 38: i_info = "…" + i_info[-35:]

                m_date = reg.modified_at.strftime("%y-%m-%d") if reg.modified_at else "--"
                e_state = "[green]✓[/]" if reg.is_flashcard_source else "[red]✗[/]"

                tipo = reg.type
                if reg.metadata_dict and 'extension' in reg.metadata_dict:
                    tipo += f"({reg.metadata_dict['extension']})"

                table.add_row(
                    str(reg.id), tipo,
                    (reg.title or "N/A")[:50],
                    d_desc, i_info, m_date, e_state,
                    tags_disp, area_disp
                )

        console.print(table)
        console.print(
            "\n[bold yellow]Comandos:[/] "
            "[bold]← →[/] Págs  [bold]Q[/] Filtrar  [bold]L[/] Limpiar  "
            "[bold][ID][/] Detalle  [bold]del [IDs][/] Borrar  "
            "[bold]m ID1 ID2[/] Vínculo Manual  [bold]ia ID1 ID2[/] IA Match  "
            "[bold]0[/] Menú Principal\n"
        )

        cmd = Prompt.ask("[bold bright_cyan]Gestor ▶[/]", console=console).strip()
        cmd_lower = cmd.lower()

        if cmd_lower == '0':
            break

        # ── Paginación con flechas (get_key no aplica aquí; usamos Prompt + detección de texto)
        elif cmd_lower in ('→', 'right', 'n', '>'):
            if has_next: page += 1
            else:
                console.print("[yellow]Ya estás en la última página.[/]")
                time.sleep(0.8)
        elif cmd_lower in ('←', 'left', 'p', '<'):
            if page > 0: page -= 1

        # ── Filtros
        elif cmd_lower == 'q':
            console.print("\n[bold yellow]🔍 Filtro Inteligente[/]")
            console.print("[white]t:etiqueta  e:ext  i:ID  s:y(solo recall)  -excluir  término(título)[/white]")
            query = Prompt.ask("[bold bright_cyan]Filtrar[/]", default="", console=console)
            if query.strip():
                filtros = parse_query_string(query)
                initial_query = query
                page = 0
            else:
                for k in filtros: filtros[k] = ""
                initial_query = ""
        elif cmd_lower == 'l':
            for k in filtros: filtros[k] = ""
            initial_query = ""
            page = 0

        # ── Borrado en lote
        elif cmd_lower.startswith('del ') or cmd_lower.startswith('borrar '):
            raw_ids = cmd_lower.replace('del ', '').replace('borrar ', '').strip()
            ids_to_delete = []
            if raw_ids.lower() in ('all', 'filtrados'):
                if not any(filtros.values()):
                    console.print("[bold yellow]⚠ Sin filtros activos: usa Q para filtrar primero.[/bold yellow]")
                    time.sleep(2.5)
                    continue
                with SessionLocal() as curr_session:
                    all_filtered = search_registry(
                        db_session=curr_session,
                        inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                        inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                        inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                        has_info=filtros['has_info'], limit=None, offset=0
                    )
                    ids_to_delete = [r.id for r in all_filtered]
            else:
                for part in raw_ids.split(','):
                    part = part.strip()
                    if '-' in part and not part.startswith('-'):
                        try:
                            s, e = part.split('-'); ids_to_delete.extend(range(int(s), int(e)+1))
                        except ValueError: pass
                    elif part.isdigit():
                        ids_to_delete.append(int(part))

            ids_to_delete = list(set(ids_to_delete))
            if not ids_to_delete:
                console.print("[bold yellow]No se encontraron IDs válidos.[/]"); time.sleep(1.5)
            else:
                console.print(f"\n[bold white on red] ⚠️ BORRADO: {len(ids_to_delete)} REGISTROS ⚠️ [/]")
                console.print(f"IDs: {ids_to_delete[:15]}{'...' if len(ids_to_delete)>15 else ''}")
                confirm = Prompt.ask("Escribe [bold white]eliminar lote[/] para confirmar", console=console).strip().lower()
                if confirm == 'eliminar lote':
                    with console.status(f"[dim]Eliminando {len(ids_to_delete)} registros...[/dim]", spinner="dots"):
                        ok = sum(1 for d_id in ids_to_delete if nx_db.delete_registry(d_id))
                    console.print(f"[bold green]✅ {ok}/{len(ids_to_delete)} eliminados.[/]")
                    time.sleep(2); page = 0
                else:
                    console.print("[yellow]Borrado cancelado.[/]"); time.sleep(1)

        # ── Vinculación de registros (2.3 — integrado desde menu_conectar)
        elif cmd_lower.startswith('m ') or cmd_lower.startswith('ia '):
            mode = 'ia' if cmd_lower.startswith('ia ') else 'm'
            parts = cmd_lower.split()
            if len(parts) < 3:
                console.print("[bold red]Uso: m ID1 ID2  ó  ia ID1 ID2[/]"); time.sleep(1.5); continue
            try:
                id_a, id_b = int(parts[1]), int(parts[2])
                rec_a = nx_db.get_registry(id_a)
                rec_b = nx_db.get_registry(id_b)
                if not rec_a or not rec_b:
                    console.print("[bold red]Uno o ambos IDs no existen.[/]"); time.sleep(1.5); continue

                console.clear(); show_header()
                from rich.columns import Columns as RichColumns
                sum_a = rec_a.summary or "[white]Sin resumen[/white]"
                sum_b = rec_b.summary or "[white]Sin resumen[/white]"
                cont_a = (rec_a.content_raw or "")[:250] + "…"
                cont_b = (rec_b.content_raw or "")[:250] + "…"
                console.print(RichColumns([
                    Panel(f"[bold bright_cyan]ID {id_a} | {rec_a.type.upper()}[/]\n\n[bold green]Resumen:[/]\n{sum_a}\n\n[white]Contenido:[/]\n{cont_a}",
                          title=f"📦 {rec_a.title}", border_style="bright_cyan", padding=(1,2)),
                    Panel(f"[bold yellow]ID {id_b} | {rec_b.type.upper()}[/]\n\n[bold green]Resumen:[/]\n{sum_b}\n\n[white]Contenido:[/]\n{cont_b}",
                          title=f"📦 {rec_b.title}", border_style="yellow", padding=(1,2)),
                ]))

                if mode == 'm':
                    rel = Prompt.ask("\n[bold]Tipo de relación[/] (ej. complementa, refuta, referencia)", default="relacionado", console=console)
                    desc = Prompt.ask("[bold]Notas sobre la relación[/] (opcional)", default="", console=console)
                    nx_db.create_link(NexusLinkCreate(source_id=id_a, target_id=id_b, relation_type=rel, description=desc))
                    console.print(f"[bold green]✅ Vínculo '{rel}' creado entre ID {id_a} ↔ ID {id_b}[/]")
                    time.sleep(1.5)
                else:
                    # IA Match
                    console.print("\n[bold yellow]🤖 IA Match: Analizando y generando vínculos + tarjetas de contraste...[/]")
                    with console.status("[dim]Procesando con agente de relaciones...[/dim]", spinner="dots"):
                        cards = generate_relationship_cards(rec_a, rec_b)
                    if cards:
                        rel = "ia_match"
                        nx_db.create_link(NexusLinkCreate(source_id=id_a, target_id=id_b, relation_type=rel, description="Vínculo generado por IA"))
                        for card in cards:
                            nx_db.create_card(CardCreate(parent_id=id_a, question=card.question, answer=card.answer, type=card.card_type))
                        console.print(f"[bold green]✅ Vínculo IA creado ({len(cards)} flashcards de contraste generadas).[/]")
                    else:
                        console.print("[bold red]La IA no pudo generar tarjetas de contraste.[/]")
                    time.sleep(2)
            except (ValueError, Exception) as link_err:
                console.print(f"[bold red]Error: {link_err}[/]"); time.sleep(1.5)

        # ── Selección por ID numérico puro → detalle de registro
        elif cmd.strip().isdigit() or (cmd.startswith('-') and cmd[1:].isdigit()):
            rec_id = int(cmd)
            try:
                _show_record_detail(rec_id)
            except ReturnToMain:
                return

        else:
            console.print("[bold white on red]Comando no reconocido. Usa ← → Q L [ID] del m ia 0[/]")
            time.sleep(1)

def _show_record_detail(rec_id: int):
    """Vista detallada de un Registro. P=volver lista, 0=menú principal."""
    from core.database import Tag, Registry, NexusLink
    
    try:
      while True:
        console.clear()
        show_header()
        
        with SessionLocal() as db_session:
            reg = nx_db.get_registry(rec_id)
            if not reg:
                console.print(f"[bold yellow]❌ Registro con ID {rec_id} no encontrado en la Base de Datos.[/bold yellow]")
                time.sleep(1.5)
                break
                
            tags_db = db_session.query(Tag).filter(Tag.registry_id == rec_id).all()
            tags_list = [t.value for t in tags_db]
            tags_str = ", ".join(tags_list) if tags_list else "Sin Etiquetas"
            
            # Preparar metadatos extendidos si existen
            extra_meta = ""
            if reg.meta_info and reg.type == "youtube":
                m = reg.meta_info
                extra_meta = f"\n[bold yellow]📊 Metadatos YouTube:[/]\n"
                if m.get('channel'): extra_meta += f"  • Canal: {m['channel']}\n"
                if m.get('duration'): extra_meta += f"  • Duración: {m['duration'] // 60} min {m['duration'] % 60} seg\n"
                if m.get('view_count'): extra_meta += f"  • Vistas: {m['view_count']:,}\n"
                if m.get('upload_date'): extra_meta += f"  • Fecha Upload: {m['upload_date']}\n"

            # Truncado agresivo para garantizar visibilidad vertical total
            def tiny_trunc(text, limit=75):
                if not text: return "[white]N/A[/white]"
                text = text.replace('\n', ' ').strip()
                return (text[:limit-3] + "...") if len(text) > limit else text

            panel_text = (
                f"[bold white]ID:[/] [bright_cyan]{reg.id}[/] | "
                f"[bold white]Tipo:[/] [yellow]{reg.type.upper()}[/] | "
                f"[bold white]Recall:[/] {'[green]SÍ[/]' if reg.is_flashcard_source else '[red]NO[/]'} │ "
                f"[bold white]Área/Tema:[/] [bright_blue]{tiny_trunc(tags_str.split(',')[0] if tags_str != 'Sin Etiquetas' else '', 30)}[/]\n"
                f"[bold white]Título:[/] [bright_white]{tiny_trunc(reg.title, 90)}[/]\n"
                f"[bold white]Ruta/URL:[/] [white]{tiny_trunc(reg.path_url, 90)}[/]\n"
                f"[bold white]Tags:[/] [yellow]{tiny_trunc(tags_str, 90)}[/]\n"
                f"{tiny_trunc(extra_meta, 120)}\n"
                f"[bold green]✨ Resumen (IA):[/] {tiny_trunc(reg.summary, 150)}\n"
                f"[bold green]📝 Contenido/Transcripción:[/] {tiny_trunc(reg.content_raw, 150)}\n\n"
                f"[yellow]P = Lista anterior │ 0 = Menú principal │ 1 Editar │ 2 Abrir │ 3 Lectura │ 4 IA │ 5 Mazo │ 6 Borrar │ 7 Vínculo │ 8 Recall[/]"
            )
            console.print(Panel(panel_text, title="🔍 Ficha Técnica Completa", box=box.HEAVY, border_style="bright_cyan"))
            
            # Sub-Menú Vista Detalle — Arquitectura 5 componentes
            console.print("\n[bold yellow]Gestión del Registro (tecla rápida):[/]")
            console.print("  [1] 📝 Editar Metadatos         [2] 🚀 Abrir Archivo/Web")
            console.print("  [3] 🧠 Enfoque (Lectura/Resumen/Transcripción)")
            console.print("  [4] 🤖 Cerebro IA (Flashcards+Resumen)   [5] 🗂️  Mazo de Estudio")
            console.print("  [6] 🗑️  Eliminar Registro     [7] 🔗 Agregar Vínculo  [8] ➕ Agregar a Recall")
            console.print("  [P] ↩  Volver a la Lista   [0] 🔙 Menú Principal\n")
            
            action = get_key()
            if action == 'p':
                break  # volver al listado anterior
            elif action == '0':
                # Volver directo al menú principal cerrando todas las capas
                raise ReturnToMain()
            elif action == '1':
                console.print("\n[white]Deja un campo vacío para no modificar ese campo.[/white]")
                
                n_source = Prompt.ask("[bold]¿Es fuente de Flashcards?[/] (s/n/Enter para omitir)", default="")
                if n_source.strip().lower() in ['s', 'n']:
                    db_session.query(Registry).filter(Registry.id == rec_id).update({
                        Registry.is_flashcard_source: 1 if n_source.strip().lower() == 's' else 0
                    })

                n_tags = Prompt.ask("[bold]Nuevas Etiquetas[/] (separadas por coma, Enter para omitir)")
                if n_tags.strip():
                    db_session.query(Tag).filter(Tag.registry_id == rec_id).delete()
                    for t in n_tags.split(','):
                        if t.strip():
                            db_session.add(Tag(registry_id=rec_id, value=t.strip()))

                n_tema = Prompt.ask("[bold]Área o Tema[/] (Enter para omitir)")
                if n_tema.strip():
                    # El tema se guarda como meta_info['topic']
                    meta_actual = reg.meta_info or {}
                    meta_actual['topic'] = n_tema.strip()
                    db_session.query(Registry).filter(Registry.id == rec_id).update({
                        Registry.meta_info: meta_actual
                    })

                n_desc = Prompt.ask("[bold]Nueva Descripción (content_raw)[/] (Enter para omitir)")
                if n_desc.strip():
                    db_session.query(Registry).filter(Registry.id == rec_id).update({
                        Registry.content_raw: n_desc.strip()
                    })

                n_summary = Prompt.ask("[bold]Nuevo Resumen[/] (Enter para omitir)")
                if n_summary.strip():
                    db_session.query(Registry).filter(Registry.id == rec_id).update({
                        Registry.summary: n_summary.strip()
                    })

                db_session.commit()
                    
                console.print("[green]Cambios guardados con éxito en la Base de Datos.[/]")

                time.sleep(1.5)
                
            elif action == '2':
                path_str = reg.path_url
                if not path_str:
                    console.print("[bold white on red]Este registro no dispone de una ubicación física o URL.[/]")
                    time.sleep(1.5)
                    continue
                    
                if reg.type == 'app':
                    import subprocess
                    console.print(f"[bold magenta]🚀 Lanzando Aplicación / Comando...[/] {path_str}")
                    try:
                        subprocess.Popen(path_str, shell=True)
                    except Exception as e:
                        console.print(f"[yellow]Fallo de ejecución directa. Intentando entorno gráfico... {e}[/yellow]")
                        if sys.platform == "win32":
                            os.system(f'rundll32.exe shell32.dll,OpenAs_RunDLL {os.path.normpath(path_str)}')
                    time.sleep(1.5)
                elif path_str.startswith("http"):
                    import webbrowser
                    console.print(f"[green]Navegando a Web:[/] {path_str}")
                    webbrowser.open(path_str)
                    time.sleep(1)
                elif reg.type == 'file' and not path_str.startswith('nexus://'):
                    if os.path.exists(path_str):
                        console.print(f"[bold green]Abriendo explorador local en:[/] {path_str}")
                        if sys.platform == "win32":
                            norm_path = os.path.normpath(path_str)
                            import subprocess
                            subprocess.Popen(f'explorer /select,"{norm_path}"')
                        time.sleep(1.5)
                    else:
                        console.print(f"[bold white on red]Directorio o Archivo extraviado en el PC:[/] {path_str}")
                        time.sleep(2.5)
                else:
                    console.print("[yellow]No admite lanzar entorno gráfico. (Puede ser una nota nativa o path virtual).[/yellow]")
                    time.sleep(2)
                    
            elif action == '3':
                # Modo Repaso Interactivo con Nodos y Salto
                while True:
                    console.clear()
                    show_header()
                    content_panel = Panel(
                        f"{reg.content_raw}",
                        title=f"[bold yellow]📖 Modo Lectura - {reg.title}[/]",
                        border_style="bright_yellow", padding=(1, 4),
                        subtitle="[white]Pulsa 'Enter' para salir o 'vID' para saltar a un nodo relacionado[/white]"
                    )
                    console.print(content_panel)
                    
                    enlaces_salientes = db_session.query(NexusLink).filter(NexusLink.source_id == rec_id).all()
                    enlaces_entrantes = db_session.query(NexusLink).filter(NexusLink.target_id == rec_id).all()
                    
                    if enlaces_salientes or enlaces_entrantes:
                        console.print("\n[bold yellow]🕸️ Red Neuronal (Vínculos Directos):[/]")
                        for ln in enlaces_salientes:
                            tg = db_session.query(Registry).filter(Registry.id == ln.target_id).first()
                            if tg: console.print(f"  [bright_cyan]v{tg.id}[/] ➔ {tg.title} [white]({ln.relation_type})[/white]")
                        for ln in enlaces_entrantes:
                            src = db_session.query(Registry).filter(Registry.id == ln.source_id).first()
                            if src: console.print(f"  [bright_cyan]v{src.id}[/] ⬅ {src.title} [white]({ln.relation_type})[/white]")
                    
                    cmd_foco = Prompt.ask("\n[bold bright_cyan]Acción[/]", console=console).strip().lower()
                    
                    if not cmd_foco:
                        break  # Termina repaso
                    elif cmd_foco.startswith('v') and cmd_foco[1:].isdigit():
                        salto_id = int(cmd_foco[1:])
                        _show_record_detail(salto_id) # Salto recursivo
                        break
                    else:
                        continue
                        
            elif action == '6':
                console.print("\n[bold white on red] ⚠️ ADVERTENCIA DE DESTRUCCIÓN ⚠️ [/]")
                console.print("[bold white on red]Estás a punto de evaporar este registro. Se romperán todos sus vínculos en la red neuronal, etiquetas y Flashcards asociadas.[/]")
                confirm = Prompt.ask("Escribe [bold white]eliminar[/] para confirmar, o presiona Enter para abortar", console=console).strip().lower()
                
                if confirm == 'eliminar':
                    success = nx_db.delete_registry(rec_id)
                    if success:
                        console.print("\n[bold green]✅ Registro evaporado con éxito de la base de datos.[/]")
                    else:
                        console.print("\n[bold white on red]❌ Hubo un error al intentar borrar el registro físico de la base de datos.[/]")
                    time.sleep(1.5)
                    break
                else:
                    console.print("\n[yellow]Operación de borrado cancelada. Sobrevivió un día más.[/yellow]")
                    time.sleep(1.5)

            elif action == '4':
                # SUB-MENÚ CEREBRO IA
                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold yellow]🧠 Herramientas de IA para:[/] {reg.title}", border_style="yellow"))
                    console.print("\n  [1] 🤖 Generar Flashcards IA (Extraer Conceptos)")
                    console.print("  [2] 📝 Generar Resumen IA (Síntesis Ejecutiva)")
                    console.print("  [0] 🔙 Volver al Panel de Registro\n")
                    
                    sub_ia = Prompt.ask("Selecciona herramienta IA", choices=["0", "1", "2"], show_choices=False, console=console)
                    
                    if sub_ia == '0': break
                    
                    if sub_ia == '1':
                        from core.database import CardCreate
                        from agents.study_agent import generate_deck_from_registry, get_client
                        from rich.prompt import Confirm
                        
                        mockup_only = False
                        if get_client():
                            console.print(f"\n[bold yellow]⚠️  AVISO DE CONSUMO DE TOKENS[/bold yellow]")
                            if not Confirm.ask("[bold white]¿Confirmas envío a Gemini para flashcards?[/bold white]"):
                                console.print("[yellow]Modo seguro activado.[/yellow]")
                                mockup_only = True

                        console.print("\n[bold yellow]🤖 Destilando conceptos...[/]")
                        with console.status("[dim]Procesando...[/dim]", spinner="dots"):
                            cards = generate_deck_from_registry(reg, mockup_only=mockup_only)
                        
                        if cards:
                            for card in cards:
                                nx_db.create_card(CardCreate(parent_id=rec_id, question=card.question, answer=card.answer, type=card.card_type))
                            console.print(f"\n[bold green]✅ ¡Éxito! {len(cards)} tarjetas nuevas en el sistema.[/bold green]")
                            
                            post_ia = Prompt.ask("\n[bold][v][/] Ver/Editar tarjetas ahora | [bold][Enter][/] Volver", default="", console=console)
                            if post_ia.lower() == 'v':
                                # Saltamos al menú de gestión (acción 5 del menú principal de detalle)
                                action = '5'
                                break # Rompemos el bucle del sub-menú IA para que el bucle superior procese action='5'
                        else:
                            console.print("\n[bold red]❌ Falló la generación.[/]")
                            time.sleep(2)
                            
                    elif sub_ia == '2':
                        from agents.summary_agent import generate_summary_from_registry
                        console.print("\n[bold yellow]🤖 Sintetizando ideas...[/]")
                        with console.status("[dim]Analizando...[/dim]", spinner="dots"):
                            summary = generate_summary_from_registry(reg)
                        if summary:
                            nx_db.update_summary(rec_id, summary)
                            console.print(f"\n[bold green]✅ Resumen actualizado.[/bold green]")
                            console.print(Panel(summary, title="Resumen IA", border_style="green"))
                            Prompt.ask("\n[bold]Enter para continuar...[/]")
                        else:
                            console.print("\n[bold red]❌ Falló la síntesis.[/]")
                            time.sleep(2)

            elif action == '5':
                # SUB-MENÚ MAZO DE ESTUDIO
                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold bright_cyan]🗂️ Gestión del Mazo para:[/] {reg.title}", border_style="bright_cyan"))
                    console.print("\n  [1] 👀 Ver/Gestionar Tarjetas Actuales")
                    console.print("  [2] ✍️  Añadir Tarjeta Manualmente")
                    console.print("  [0] 🔙 Volver al Panel de Registro\n")
                    
                    sub_mz = Prompt.ask("Selecciona acción", choices=["0", "1", "2"], show_choices=False, console=console)
                    if sub_mz == '0': break

                    if sub_mz == '2':
                        console.print("\n[bold yellow]✍️  Creación Manual[/]")
                        q = Prompt.ask("[bold bright_cyan]Pregunta[/] (o 'cancelar')", console=console)
                        if q.strip().lower() not in ['cancelar', '']:
                            a = Prompt.ask("[bold green]Respuesta[/]")
                            t = Prompt.ask("[bold]Tipo[/]", choices=["Factual", "Conceptual", "Cloze"], default="Factual")
                            nx_db.create_card(CardCreate(parent_id=rec_id, question=q.strip(), answer=a.strip(), type=t))
                            console.print("\n[bold green]✅ Tarjeta vinculada.[/bold green]")
                            time.sleep(1.5)
                    
                    elif sub_mz == '1':
                        from core.database import Card
                        while True:
                            console.clear()
                            show_header()
                            cards_db = db_session.query(Card).filter(Card.parent_id == rec_id).all()
                            if not cards_db:
                                console.print("[yellow]Mazo vacío.[/yellow]")
                                time.sleep(1.5); break
                            
                            total_cards = len(cards_db)
                            for i, c in enumerate(cards_db):
                                idx = i + 1
                                console.print(f"\n[bold yellow]🗂️ Tarjeta {idx} de {total_cards}[/]")
                                console.print(f"  [bright_cyan]Q:[/] {c.question}")
                                console.print(f"  [green]A:[/] {c.answer}")
                                console.print("-" * 40)
                            
                            console.print("\n[1] Editar  [2] Eliminar  [0] Atrás")
                            cmd = Prompt.ask("Comando", choices=["0", "1", "2"], show_choices=False)
                            if cmd == '0': break
                            elif cmd == '2':
                                cid_del = IntPrompt.ask("ID de tarjeta a borrar")
                                target = db_session.query(Card).filter(Card.id == cid_del, Card.parent_id == rec_id).first()
                                if target:
                                    db_session.delete(target); db_session.commit()
                                    console.print("[green]Borrado exitoso.[/]")
                                    time.sleep(1)
                            elif cmd == '1':
                                cid_ed = IntPrompt.ask("ID de tarjeta a editar")
                                target = db_session.query(Card).filter(Card.id == cid_ed, Card.parent_id == rec_id).first()
                                if target:
                                    target.question = Prompt.ask("Q", default=target.question)
                                    target.answer = Prompt.ask("A", default=target.answer)
                                    db_session.commit()
                                    console.print("[green]Actualizado.[/]")
                                    time.sleep(1)

            elif action == '7':
                # Agregar vínculo rápido desde el detalle
                console.print("\n[bold yellow]🔗 Agregar Vínculo[/]")
                try:
                    id_b_str = Prompt.ask("[bold]ID del registro a vincular con este (ID2)[/]", console=console)
                    id_b = int(id_b_str.strip())
                    rec_b = nx_db.get_registry(id_b)
                    if not rec_b:
                        console.print("[bold red]Registro destino no encontrado.[/]"); time.sleep(1.5)
                    else:
                        rel = Prompt.ask("[bold]Tipo de relación[/] (ej. complementa, refuta)", default="relacionado", console=console)
                        desc_v = Prompt.ask("[bold]Notas[/] (opcional)", default="", console=console)
                        nx_db.create_link(NexusLinkCreate(source_id=rec_id, target_id=id_b, relation_type=rel, description=desc_v))
                        console.print(f"[bold green]✅ Vínculo '{rel}' creado: ID {rec_id} ↔ ID {id_b}[/]")
                        time.sleep(1.5)
                except (ValueError, Exception) as ve:
                    console.print(f"[bold red]Error: {ve}[/]"); time.sleep(1.5)

            elif action == '8':
                # Agregar a Active Recall (marcar como fuente)
                console.print("\n[bold bright_cyan]➕ Agregar a Active Recall[/]")
                opcion_recall = Prompt.ask(
                    "[1] Solo marcar como fuente  [2] Marcar + Generar Flashcards con IA  [0] Cancelar",
                    choices=["0", "1", "2"], show_choices=False, console=console
                )
                if opcion_recall == "1" or opcion_recall == "2":
                    db_session.query(Registry).filter(Registry.id == rec_id).update({
                        Registry.is_flashcard_source: 1
                    })
                    db_session.commit()
                    console.print("[green]✅ Marcado como fuente de Recall.[/]")
                    if opcion_recall == "2":
                        from agents.study_agent import generate_deck_from_registry, get_client
                        mockup_only = not bool(get_client())
                        console.print("[yellow]🤖 Generando flashcards...[/]")
                        with console.status("[dim]Procesando...[/dim]", spinner="dots"):
                            cards_gen = generate_deck_from_registry(reg, mockup_only=mockup_only)
                        if cards_gen:
                            for card_g in cards_gen:
                                nx_db.create_card(CardCreate(parent_id=rec_id, question=card_g.question, answer=card_g.answer, type=card_g.card_type))
                            console.print(f"[bold green]✅ {len(cards_gen)} flashcards generadas.[/]")
                        else:
                            console.print("[yellow]No se generaron flashcards.[/]")
                    time.sleep(1.5)

    except ReturnToMain:
        raise  # propagamos para salir al main_loop


def menu_adelantar_repaso():
    """Sub-menú para adelantar repasos con opciones de filtrado y cantidad."""
    from core.database import Registry, Card, Tag
    from sqlalchemy import func
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_header()
        
        console.print(Panel("[bold yellow]Menú: Adelantar Repaso (Flashcards)[/]\n\n"
                            "  [1] 📋 Repaso de Tema Específico (Lista y Filtros)\n"
                            "  [2] 🎲 Repaso al Azar (Mezclar todo el mazo)\n"
                            "  [3] 🔢 Cantidad de Tarjetas a Repasar (Fijar límite)\n"
                            "  [0] 🔙 Regresar al menú anterior", 
                            title="Estudio Intensivo / Adelantar", border_style="yellow"))
        
        opcion = Prompt.ask("\nSelecciona una opción", choices=["0", "1", "2", "3"], show_choices=False)
        
        if opcion == "0":
            break
        
        elif opcion == "1":
            # Repaso de tema específico con filtros
            page = 0
            items_per_page = 10
            filtros_tema = {'name': "", 'tag': ""}
            
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                show_header()
                console.print(f"[bold cyan]🔍 Selección de Tema Específico[/] | Filtros: {filtros_tema}\n")
                
                with SessionLocal() as db_session:
                    # Buscamos registros que tengan tarjetas asociadas
                    query = db_session.query(Registry).join(Card, Card.parent_id == Registry.id).group_by(Registry.id)
                    
                    if filtros_tema['name']:
                        query = query.filter(Registry.title.ilike(f"%{filtros_tema['name']}%"))
                    if filtros_tema['tag']:
                        query = query.join(Tag, Tag.registry_id == Registry.id).filter(Tag.value.ilike(f"%{filtros_tema['tag']}%"))
                    
                    total_count = query.count()
                    results = query.limit(items_per_page).offset(page * items_per_page).all()
                
                table = Table(title="Temas Disponibles con Flashcards", box=box.ROUNDED)
                table.add_column("ID", style="bright_cyan")
                table.add_column("Tipo", style="yellow")
                table.add_column("Título", style="bold bright_white")
                table.add_column("Tarjetas", justify="center")
                
                with SessionLocal() as db_session:
                    for reg in results:
                        count = db_session.query(func.count(Card.id)).filter(Card.parent_id == reg.id).scalar()
                        table.add_row(str(reg.id), reg.type.upper(), reg.title or "Sin Título", str(count))
                
                console.print(table)
                console.print(f"\n[white]Página {page+1} | Total temas: {total_count}[/white]")
                console.print("\n[bold cyan]Controles:[/]")
                console.print("  [bold]ID[/] Seleccionar Tema | [bold]f[/] Cambiar Filtros | [bold]n/p[/] Pags | [bold]0[/] Atras")
                
                cmd = Prompt.ask("\nComando").strip().lower()
                
                if cmd == '0':
                    break
                elif cmd == 'n' and (page + 1) * items_per_page < total_count:
                    page += 1
                elif cmd == 'p' and page > 0:
                    page -= 1
                elif cmd == 'f':
                    filtros_tema['name'] = Prompt.ask("Filtrar por Título", default=filtros_tema['name'])
                    filtros_tema['tag'] = Prompt.ask("Filtrar por Etiqueta", default=filtros_tema['tag'])
                    page = 0
                elif cmd.isdigit():
                    tid = int(cmd)
                    start_pomodoro_session(pomodoro_minutes=25, adelantar=True, topic_id=tid)
                    Prompt.ask("\n[bold]Sesión Finalizada. Presiona Enter para volver...[/]")
                    break

        elif opcion == "2":
            # Repaso al azar
            start_pomodoro_session(pomodoro_minutes=25, adelantar=True, shuffled=True)
            Prompt.ask("\n[bold]Sesión Aleatoria Finalizada. Presiona Enter para volver...[/]")
            
        elif opcion == "3":
            # Cantidad de tarjetas
            limit = IntPrompt.ask("\n¿Cuántas tarjetas deseas repasar hoy en total?", default=20)
            shuff = Prompt.ask("¿Quieres que el orden sea aleatorio? ([bold]s[/]/[bold]n[/])", choices=["s", "n"], default="s") == 's'
            start_pomodoro_session(pomodoro_minutes=60, adelantar=True, shuffled=shuff, card_limit=limit)
            Prompt.ask("\n[bold]Sesión Personalizada Finalizada. Presiona Enter para volver...[/]")

def menu_active_recall():
    """Puente hacia módulos de estudio y SRS, fusionado con un Explorador Gestor de Flashcards (Lotes)"""
    from core.database import Registry, Card
    from sqlalchemy import func
    from datetime import datetime, timezone
    from agents.study_agent import generate_deck_from_registry
    
    page = 0
    items_per_page = 8
    filtros = {
        'inc_name': "", 'exc_name': "", 'inc_tags': "", 'exc_tags': "",
        'inc_exts': "", 'exc_exts': "", 'has_info': "", 'inc_ids': "", 'is_source': ""
    }

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_header()
        
        # --- 1. Banner Superior: Status de Pomodoros Pendientes ---
        now = datetime.now(timezone.utc)
        with nx_db.Session() as db_session:
            due_cards = db_session.query(Card).filter((Card.next_review == None) | (Card.next_review <= now)).subquery()
            topics_today = db_session.query(Registry.id, Registry.title, func.count(due_cards.c.id)).join(
                due_cards, due_cards.c.parent_id == Registry.id
            ).group_by(Registry.id).all()
            
            if topics_today:
                c_total = sum([c for _, _, c in topics_today])
                console.print(Panel(f"[bold bright_cyan]🔥 Motor Pomodoro Listo:[/] Tienes [bold white on red]{c_total} tarjetas pendientes[/] distribuidas en {len(topics_today)} temas para hoy.", box=box.ROUNDED, border_style="bright_cyan"))
            else:
                console.print(Panel("[green]🎉 Tu mente está al día. No tienes repasos pendientes hoy.[/]", box=box.ROUNDED, border_style="green"))

        # --- 2. Explorador de Fuentes de Flashcards ---
        # Si el usuario NO tiene filtros activos, forzamos mostrar solo los temas pendientes para hacer Pomodoro hoy
        filtro_vacio = not any(filtros.values())
        ids_a_buscar = filtros['inc_ids']
        if filtro_vacio:
            if topics_today:
                ids_a_buscar = ",".join(str(tid) for tid, _, _ in topics_today)
            else:
                ids_a_buscar = "-1" # Invalid ID list para forzar a que no aparezca nada

        inc_exts_list = [e.strip() for e in filtros['inc_exts'].split(',')] if filtros['inc_exts'] else None
        exc_exts_list = [e.strip() for e in filtros['exc_exts'].split(',')] if filtros['exc_exts'] else None
        
        with SessionLocal() as curr_session:
            results = search_registry(
                db_session=curr_session,
                inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                has_info=filtros['has_info'], record_ids_str=ids_a_buscar,
                is_flashcard_source=filtros['is_source'], limit=items_per_page + 1, offset=page * items_per_page
            )
            
        has_next = len(results) > items_per_page
        display_results = results[:items_per_page]
        
        table = Table(
            title=f"[bold yellow]🧠 ACTIVE RECALL — Selector de Fuentes (Pág. {page + 1})[/] | Filtros: {'Sí' if any(filtros.values()) else 'No'}  │  ←→ Navegar  Q Filtrar  L Limpiar  0 Salir",
            box=box.ROUNDED, show_lines=True, expand=True
        )
        table.add_column("ID",    justify="right", style="bright_cyan", no_wrap=True, width=6)
        table.add_column("Título", style="bold bright_white", ratio=3)
        table.add_column("Descripción",  style="white", ratio=2)
        table.add_column("Tags",          style="yellow", ratio=2)
        table.add_column("Pend/Tot",      justify="center", no_wrap=True, width=10)  # d
        table.add_column("💳 Flashcard a Evaluar", justify="left", style="bright_yellow", ratio=4)  # columna nueva

        with nx_db.Session() as s_aux:
            for reg in display_results:
                from core.database import Tag
                tag_list = s_aux.query(Tag).filter(Tag.registry_id == reg.id).all()
                tags_str = ", ".join([t.value for t in tag_list]) if tag_list else ""
                
                total_cards = s_aux.query(func.count(Card.id)).filter(Card.parent_id == reg.id).scalar()
                pending_cards = s_aux.query(func.count(Card.id)).filter(
                    Card.parent_id == reg.id,
                    (Card.next_review == None) | (Card.next_review <= now)
                ).scalar()
                
                titulo_list = (reg.title[:40] + "...") if len(reg.title or "") > 40 else (reg.title or "")
                desc_list = (reg.content_raw.replace('\n', ' ')[:45] + "...") if len(reg.content_raw or "") > 45 else (reg.content_raw or "")
                tags_list_view = (tags_str[:28] + "...") if len(tags_str) > 28 else tags_str

                # Obtener la primera flashcard pendiente como preview
                flashcard_preview = ""
                first_card = s_aux.query(Card).filter(
                    Card.parent_id == reg.id,
                    (Card.next_review == None) | (Card.next_review <= now)
                ).first()
                if first_card:
                    q_disp = (first_card.question[:60] + "...") if len(first_card.question or "") > 60 else (first_card.question or "")
                    flashcard_preview = f"[bold]Q:[/] {q_disp}"

                table.add_row(
                    str(reg.id),
                    titulo_list,
                    desc_list,
                    tags_list_view,
                    f"[bold yellow]{pending_cards}[/]/[white]{total_cards}[/]",
                    flashcard_preview
                )

        console.print(table)
        
        # --- 3. Controles del Menú Active Recall (Arquitectura 5 componentes) ---
        console.print(
            "\n[bold bright_cyan]Comandos:[/] "
            "[bold]← →[/] Págs  [bold]Q[/] Filtrar  [bold]L[/] Limpiar  "
            "[bold]•[ID][/] Entrar al registro  "
            "[bold]ia [IDs][/] Flashcards IA  [bold]man [ID][/] Manual  "
            "[bold]pm[/] Pomodoro  [bold]pa[/] Adelantar  "
            "[bold]del [IDs][/] Borrar  [bold]0[/] Salir\n"
        )

        cmd = Prompt.ask("[bold bright_cyan]Recall ►[/]", console=console).strip()
        cmd_lower = cmd.lower()
        
        if cmd_lower == '0':
            break
        elif cmd_lower in ('→', 'right', 'n', '>'):
            if has_next: page += 1
            else:
                console.print("[yellow]Ya estás en la última página.[/]")
                time.sleep(0.8)
        elif cmd_lower in ('←', 'left', 'p', '<'):
            if page > 0: page -= 1
        elif cmd_lower == 'l':
            for k in filtros: filtros[k] = ""
            page = 0
        elif cmd_lower == 'q':
            console.print("\n[bold yellow]🔍 Filtro Inteligente (Recall)[/]")
            console.print("[white]t:etiqueta  e:ext  i:ID  s:y(solo recall)  término[/white]")
            query = Prompt.ask("[bold bright_cyan]Filtrar[/]", default="", console=console)
            if query.strip():
                filtros = parse_query_string(query)
                page = 0
            else:
                for k in filtros: filtros[k] = ""
                time.sleep(1)
            
        elif cmd_lower == 'pm':
            start_pomodoro_session(pomodoro_minutes=25, adelantar=False, topic_id=None)
            Prompt.ask("\n[bold]Sesión Finalizada. Presiona Enter para volver a Active Recall...[/]")

            
        elif cmd == 'pa':
            menu_adelantar_repaso()

        elif cmd.startswith('e ') or cmd.startswith('edit '):
            raw_id = cmd.replace('edit ', '').replace('e ', '').strip()
            if raw_id.isdigit():
                rec_id = int(raw_id)
                _show_record_detail(rec_id)
            else:
                console.print("[bold white on red]Uso: e [ID] (ej. e 5)[/]")
                time.sleep(1)

        elif cmd.startswith('j '):
            raw_id = cmd.replace('j ', '').strip()
            if raw_id.isdigit():
                rec_id = int(raw_id)
                reg_obj = nx_db.get_registry(rec_id)
                if reg_obj:
                    console.print(f"\n[bright_white]Abriendo fuente para ID {rec_id}: {reg_obj.title}...[/bright_white]")
                    open_source_material(reg_obj)
                else:
                    console.print("[bold white on red]Registro no encontrado en DB.[/]")
                    time.sleep(1.5)
            else:
                console.print("[bold white on red]Uso: j [ID] (ej. j 5)[/]")
                time.sleep(1)

        elif cmd.startswith('man '):
            raw_id = cmd.replace('man ', '').strip()
            if raw_id.isdigit():
                rec_id = int(raw_id)
                reg_obj = nx_db.get_registry(rec_id)
                if not reg_obj:
                    console.print("[bold white on red]Registro no encontrado en DB.[/]")
                    time.sleep(1.5)
                    continue
                
                # Opción de navegar a la fuente antes de crear
                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold yellow]Preparación: Creación Manual[/]\nTema: [bold]{reg_obj.title}[/]", box=box.ROUNDED))
                    action_prep = Prompt.ask("\n¿Deseas abrir el material fuente para visualizar contenido? ([bold]f[/] abrir / [bold]Enter[/] ir a creación)").strip().lower()
                    if action_prep == 'f':
                        open_source_material(reg_obj)
                    else:
                        break

                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold yellow]Creación Manual Flashcards[/]\nCreando tarjetas para: [bold]{reg_obj.title}[/]", box=box.ROUNDED))
                    console.print("[white]Escribe 'salir' en la Pregunta para terminar.[/white]\n")
                    
                    types_list = ["Factual", "Conceptual", "Reversible", "MCQ", "TF", "Cloze", "Matching", "MAQ"]
                    # Forzamos que el prompt use nuestra consola con el tema de colores corregido
                    t_card_raw = Prompt.ask("[bold yellow]Tipo de Tarjeta[/]", choices=types_list, default="Factual", console=console).strip()
                    
                    # Mapeo manual para asegurar que acepte minúsculas aunque el 'choices' sea en Mayúsculas
                    # (Rich por defecto es estricto con las choices)
                    t_card = "Factual"
                    for t in types_list:
                        if t_card_raw.lower() == t.lower():
                            t_card = t
                            break
                    
                    q = ""
                    a = ""
                    
                    if t_card == "Reversible":
                        q_side = Prompt.ask("[bold cyan]Lado A[/]")
                        if q_side.lower() == 'salir': break
                        a_side = Prompt.ask("[bold green]Lado B[/]")
                        # Crear las dos variantes
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_side, answer=a_side, type="Factual"))
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=a_side, answer=q_side, type="Factual"))
                        console.print("[yellow]✅ ¡Dos tarjetas (A->B y B->A) creadas![/yellow]")
                    
                    elif t_card == "TF":
                        q = Prompt.ask("[bold cyan]Afirmación[/]")
                        if q.lower() == 'salir': break
                        a = Prompt.ask("[bold green]¿Es Verdadera?[/] (v/f)", choices=["v", "f"])
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q, answer=a, type="TF"))
                    
                    elif t_card == "MCQ" or t_card == "MAQ":
                        import json
                        prompt = Prompt.ask("[bold cyan]Pregunta / Enunciado[/]")
                        if prompt.lower() == 'salir': break
                        options = {}
                        while True:
                            key = Prompt.ask("[white]Letra de opción (o Enter para finalizar)[/white]", console=console)
                            if not key: break
                            val = Prompt.ask(f"Texto para opción {key}", console=console)
                            options[key] = val
                        
                        q_json = json.dumps({"prompt": prompt, "options": options})
                        a = Prompt.ask("[bold green]Letra(s) de la respuesta correcta[/] (ej. 'a' o 'a,b')")
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_json, answer=a, type=t_card))

                    elif t_card == "Cloze":
                        console.print("[white]Uso la sintaxis: La capital de {{c1::Francia}} es {{c2::París}}[/white]")
                        q = Prompt.ask("[bold bright_cyan]Texto con Huecos[/]", console=console)
                        if q.lower() == 'salir': break
                        # Extraer respuestas automáticamente para el campo answer
                        import re
                        matches = re.findall(r"\{\{c\d+::(.*?)\}\}", q)
                        a = ", ".join(matches)
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q, answer=a, type="Cloze"))

                    elif t_card == "Matching":
                        import json
                        console.print("[white]Ingresa pares de conceptos relacionados.[/white]")
                        pairs = {}
                        while True:
                            left = Prompt.ask("[white]Término Izquierda (o Enter para finalizar)[/white]", console=console)
                            if not left: break
                            right = Prompt.ask(f"Término Derecha para '{left}'", console=console)
                            pairs[left] = right
                        
                        q_json = json.dumps({"pairs": pairs})
                        # La respuesta visual es simplemente el listado de pares correctos
                        a_text = "\n".join([f"{k} -> {v}" for k, v in pairs.items()])
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_json, answer=a_text, type="Matching"))

                    else:
                        # Factual / Conceptual (Estándar)
                        q = Prompt.ask("[bold bright_cyan]Pregunta (Q)[/]", console=console)
                        if q.lower() == 'salir' or not q.strip(): break
                        a = Prompt.ask("[bold green]Respuesta (A)[/]", console=console)
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q, answer=a, type=t_card))
                    
                    console.print("[yellow]✅ Operación de creación finalizada.[/yellow]")
                    cont = Prompt.ask("\n¿Deseas añadir otra tarjeta a este tema? ([bold]s[/]/[bold]n[/])", choices=["s", "n"], default="s").lower()
                    if cont == 'n':
                        break
            else:
                console.print("[bold white on red]Ingresa un ID numérico válido para creación manual.[/]")
                time.sleep(1)

        elif cmd.startswith('ia '):
            raw_ids = cmd.replace('ia ', '').strip()
            target_ids = []
            
            if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                with SessionLocal() as curr_session:
                    all_filtered = search_registry(
                        db_session=curr_session,
                        inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                        inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                        inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                        has_info=filtros['has_info'], record_ids_str=filtros['inc_ids'],
                        is_flashcard_source=filtros['is_source'], limit=None, offset=0
                    )
                    target_ids = [r.id for r in all_filtered]
            else:
                for part in raw_ids.split(','):
                    part = part.strip()
                    if '-' in part:
                        try:
                            start_str, end_str = part.split('-')
                            s_id, e_id = int(start_str), int(end_str)
                            target_ids.extend(range(min(s_id, e_id), max(s_id, e_id) + 1))
                        except ValueError:
                            pass
                    else:
                        if part.isdigit(): target_ids.append(int(part))
                        
            target_ids = list(set(target_ids))
            
            if not target_ids:
                console.print("[bold white on red]No se detectaron IDs válidos o la búsqueda está vacía.[/]")
                time.sleep(2)
                continue
                
            console.print(f"\n[bold yellow]🤖 ATENCIÓN: El Agente IA procesará un lote de {len(target_ids)} registros.[/]")
            confirm = Prompt.ask("¿Confirmas la generación masiva de este lote pagando con tus Tokens API? (s/n)").strip().lower()
            if confirm == 's':
                success_generations = 0
                total_cards_made = 0
                for d_id in target_ids:
                    reg_obj_ia = nx_db.get_registry(d_id)
                    if reg_obj_ia:
                        console.print(f"\n[white]Procesando Registro ID {d_id}: '{reg_obj_ia.title}'[/white]")
                        # Invocado a IA (Mockup solo si el cliente no está disponible, ya confirmamos el lote arriba)
                        cards_generated = generate_deck_from_registry(reg_obj_ia, mockup_only=False)
                        if cards_generated:
                            for card in cards_generated:
                                nx_db.create_card(CardCreate(parent_id=d_id, question=card.question, answer=card.answer, type=card.card_type))
                            success_generations += 1
                            total_cards_made += len(cards_generated)
                            console.print(f"[bold green]✓ {len(cards_generated)} tarjetas anidadas a ID {d_id}[/bold green]")
                        else:
                            console.print(f"[yellow]⚠ IA omitió ID {d_id} (Falta de info o error API).[/yellow]")
                
                console.print(f"\n[bold magenta]🎉 OPERACIÓN IA LOTE FINALIZADA:[/]\n  ‣ Registros Exitosos: {success_generations}/{len(target_ids)}\n  ‣ Total Flashcards Agregadas al Sistema: {total_cards_made}")
                Prompt.ask("\n[bold]Presiona Enter para continuar...[/]")
            else:
                console.print("[yellow]Operación omitida.[/yellow]")
                time.sleep(1)

        elif cmd.startswith('del ') or cmd.startswith('borrar '):
            raw_ids = cmd.replace('del ', '').replace('borrar ', '').strip()
            ids_to_delete = []
            
            # 1. Si el usuario pide borrar TODO lo filtrado
            if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                if not any(filtros.values()):
                    console.print("[bold white on red]¡Peligro! No tienes ningún filtro aplicado. Debes realizar una búsqueda ('s') primero para evitar borrar toda tu base de datos accidentalmente.[/]")
                    time.sleep(3.5)
                    continue
                else:
                    with SessionLocal() as curr_session:
                        all_filtered = search_registry(
                            db_session=curr_session,
                            inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                            inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                            inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                            has_info=filtros['has_info'], record_ids_str=filtros['inc_ids'],
                            is_flashcard_source=filtros['is_source'], limit=None, offset=0
                        )
                        ids_to_delete = [r.id for r in all_filtered]
                        
            # 2. Si el usuario dio IDs estandar manuales (ej: 1,2,3-10)
            else:
                for part in raw_ids.split(','):
                    part = part.strip()
                    if '-' in part and not part.startswith('-'):
                        try:
                            start_str, end_str = part.split('-')
                            start_id = int(start_str)
                            end_id = int(end_str)
                            ids_to_delete.extend(range(min(start_id, end_id), max(start_id, end_id) + 1))
                        except ValueError:
                            pass
                    else:
                        if part.isdigit():
                            ids_to_delete.append(int(part))
            
            ids_to_delete = list(set(ids_to_delete))
            if not ids_to_delete:
                console.print("[bold white on red]No se detectaron IDs válidos para borrar o la búsqueda arrojó cero resultados.[/]")
                time.sleep(1.5)
            else:
                console.print(f"\n[bold white on red] ⚠️ ADVERTENCIA DE BORRADO MASIVO: {len(ids_to_delete)} REGISTROS DE RAÍZ ⚠️ [/]")
                if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                    console.print("[yellow]Estás a punto de eliminar permanentemente todos los registros base y TUS TARJETAS DE ESTUDIO de este lote filtrado.[/yellow]")
                else:    
                    console.print(f"[bold white on red]Registros implicados:[/] [white]{str(ids_to_delete[:15])}... (y más)[/white]" if len(ids_to_delete) > 15 else f"[bold white on red]Registros implicados:[/] {ids_to_delete}")
                
                confirm = Prompt.ask("Escribe [bold white]eliminar lote[/] para confirmar, o presiona Enter para abortar", console=console).strip().lower()
                
                if confirm == 'eliminar lote':
                    with console.status(f"[dim]Destruyendo {len(ids_to_delete)} registros y sus flashcards heredadas...[/dim]", spinner="dots"):
                        success_count = 0
                        for d_id in ids_to_delete:
                            if nx_db.delete_registry(d_id):
                                success_count += 1
                        console.print(f"\n[bold green]✅ Lote evaporado: {success_count}/{len(ids_to_delete)} registros y flashcards eliminados permanentemente.[/]")
                    time.sleep(2.5)
                    page = 0
                else:
                    console.print("\n[yellow]Operación de borrado en lote abortada.[/yellow]")
                    time.sleep(1.5)

        else:
            console.print("[bold white on red]Comando no reconocido.[/]")
            time.sleep(1)


def menu_conectar():
    """Centro de Vinculación Neuronal (Cockpit de Enlaces)"""
    page = 0
    items_per_page = 10
    filtros = {
        'inc_name': "", 'exc_name': "", 'inc_tags': "", 'exc_tags': "",
        'inc_exts': "", 'exc_exts': "", 'has_info': "", 'inc_ids': "", 'is_source': ""
    }

    while True:
        console.clear()
        show_header()
        
        # 1. Búsqueda de registros para referencia
        inc_exts_list = [e.strip() for e in filtros['inc_exts'].split(',')] if filtros['inc_exts'] else None
        exc_exts_list = [e.strip() for e in filtros['exc_exts'].split(',')] if filtros['exc_exts'] else None
        
        with SessionLocal() as db_session:
            results = search_registry(
                db_session=db_session,
                inc_name_path=filtros['inc_name'],
                inc_tags=filtros['inc_tags'],
                inc_extensions=inc_exts_list,
                limit=items_per_page + 1,
                offset=page * items_per_page
            )
            
        has_next = len(results) > items_per_page
        display_results = results[:items_per_page]
        
        # 2. Render de la Tabla de Referencia
        table = Table(title="🔗 Cockpit de Enlaces (Identifica IDs para Conectar)", box=box.ROUNDED, border_style="yellow")
        table.add_column("ID", justify="right", style="bright_cyan")
        table.add_column("Título", style="bold bright_white")
        table.add_column("Tipo", style="yellow")
        table.add_column("Contenido (Preview)", style="italic green")
        
        for reg in display_results:
            preview = (reg.content_raw or "").replace('\n', ' ')[:50] + "..."
            table.add_row(str(reg.id), reg.title or "N/A", reg.type, preview)
            
        console.print(table)
        
        # 3. Controles
        console.print("\n[bold yellow]Comandos de Conexión:[/]")
        console.print("  [bold]ia ID1 ID2[/] 🤖 IA Match (Crea vínculo + tarjetas comparativas)")
        console.print("  [bold]m ID1 ID2[/]  🔗 Vínculo Manual (Crea relación simple)")
        console.print("  [bold]s [query][/]  🔍 Filtrar lista | [bold]n/p[/] Pág | [bold]0[/] Volver al Menú Principal\n")
        
        cmd = Prompt.ask("Nexus Linker", console=console).strip().lower()
        
        if cmd == '0':
            break
        elif cmd == 'n' and has_next: page += 1
        elif cmd == 'p' and page > 0: page -= 1
        elif cmd == 's':
            query = Prompt.ask("[bold yellow]Filtrar registros[/]", console=console)
            if query.strip():
                filtros = parse_query_string(query)
                page = 0
            else:
                for k in filtros: filtros[k] = ""
        
        # LÓGICA DE VINCULACIÓN
        elif cmd.startswith('m ') or cmd.startswith('ia '):
            mode = 'ia' if cmd.startswith('ia ') else 'm'
            parts = cmd.split()
            if len(parts) < 3:
                console.print("[bold red]Error: Debes proporcionar dos IDs. Ej: ia 5 10[/]")
                time.sleep(1.5)
                continue
            
            try:
                id_a, id_b = int(parts[1]), int(parts[2])
                rec_a = nx_db.get_registry(id_a)
                rec_b = nx_db.get_registry(id_b)
                
                if not rec_a or not rec_b:
                    console.print("[bold red]Uno o ambos IDs no existen.[/]")
                    time.sleep(1.5)
                    continue

                # --- VISTA DE COMPARACIÓN VISUAL ENRIQUECIDA ---
                console.clear()
                show_header()
                from rich.columns import Columns
                
                # Preparar datos A
                sum_a = rec_a.summary if rec_a.summary else "[white]Sin resumen (Usa Cerebro IA para generarlo)[/white]"
                url_a = rec_a.path_url if rec_a.path_url else "[white]Sin enlace[/white]"
                cont_a = (rec_a.content_raw or "[white]Sin descripción[/white]")[:300] + "..."
                
                # Preparar datos B
                sum_b = rec_b.summary if rec_b.summary else "[white]Sin resumen (Usa Cerebro IA para generarlo)[/white]"
                url_b = rec_b.path_url if rec_b.path_url else "[white]Sin enlace[/white]"
                cont_b = (rec_b.content_raw or "[white]Sin descripción[/white]")[:300] + "..."

                comp_view = Columns([
                    Panel(
                        f"[bold bright_cyan]ID {id_a} | {rec_a.type.upper()}[/]\n\n"
                        f"[bold green]✨ RESUMEN IA:[/]\n{sum_a}\n\n"
                        f"[bold bright_blue]🔗 ENLACE ORIGIN:[/] {url_a}\n\n"
                        f"[white]📄 CONTENIDO:[/]\n{cont_a}",
                        title=f"📦 {rec_a.title}", border_style="bright_cyan", padding=(1,2)
                    ),
                    Panel(
                        f"[bold yellow]ID {id_b} | {rec_b.type.upper()}[/]\n\n"
                        f"[bold green]✨ RESUMEN IA:[/]\n{sum_b}\n\n"
                        f"[bold bright_blue]🔗 ENLACE ORIGIN:[/] {url_b}\n\n"
                        f"[white]📄 CONTENIDO:[/]\n{cont_b}",
                        title=f"📦 {rec_b.title}", border_style="yellow", padding=(1,2)
                    )
                ], expand=True)
                
                console.print(Panel(comp_view, title="🔍 Comparación de Registros para Vinculación", border_style="white"))

                if mode == 'm':
                    console.print("\n[bold]Estableciendo Vínculo Manual:[/]")
                    rel = Prompt.ask("Define el Tipo de Relación (ej. complementa, refuta, mismo_tema)", default="relacionado")
                    desc = Prompt.ask("Nota de contexto (opcional)", default="")
                    nx_db.create_link(NexusLinkCreate(source_id=id_a, target_id=id_b, relation_type=rel, description=desc))
                    console.print(f"\n[bold green]✅ ¡Vínculo forjado! Red neuronal actualizada.[/bold green]")
                else:
                    from rich.prompt import Confirm
                    console.print(f"\n[bold yellow]🤖 MODO IA MATCH ACTIVADO[/bold yellow]")
                    console.print(f"[white]Gemini analizará ambos contenidos para encontrar divergencias y crear flashcards de contraste.[/white]")
                    if not Confirm.ask(f"\n[bold white]¿Confirmas envío a Gemini?[/bold white]"):
                        console.print("[yellow]Operación cancelada.[/yellow]")
                        time.sleep(1)
                        continue

                    console.print(f"\n[bold yellow]🤖 Iniciando IA Match entre {id_a} y {id_b}...[/]")
                    with console.status("[white]Cerebro de IA procesando divergencias...[/white]", spinner="dots"):
                        cards = generate_relationship_cards(rec_a, rec_b)
                    
                    if cards:
                        nx_db.create_link(NexusLinkCreate(source_id=id_a, target_id=id_b, relation_type="IA_Match"))
                        for c in cards:
                            nx_db.create_card(CardCreate(parent_id=c.parent_id, question=c.question, answer=c.answer, type=c.card_type))
                        console.print(f"[bold green]✅ Relación forjada. {len(cards)} tarjetas creadas.[/bold green]")
                    else:
                        console.print("[bold red]El agente IA no devolvió resultados.[/]")
                
                Prompt.ask("\n[bold]Presiona Enter para continuar...[/bold]", console=console)
            except ValueError:
                console.print("[bold red]Los IDs deben ser números.[/]")
                time.sleep(1.5)

def menu_estadisticas():
    """[4] ESTADÍSTICAS
    Visualizar salud del sistema, composición de la base de conocimiento y métricas de aprendizaje.
    G=Sincronizar con Google Drive | S=Filtrar por área/tag | Enter=Volver
    """
    filtro_activo = ""
    
    while True:
        console.clear()
        show_header()

        console.print(Align.center(get_stats_panel(active_filters=filtro_activo)))
        console.print()

        with console.status("[white]Consultando datos...[/white]", spinner="dots"):
            metrics = get_global_metrics()

        # Panel 4.1: Composición del Cerebro
        t_reg = Table(title="🗄️ 4.1 Composición del Cerebro", box=box.ROUNDED, style="bright_cyan")
        t_reg.add_column("Tipo", justify="left")
        t_reg.add_column("Cantidad", justify="right", style="bold white")
        for r_type, count in metrics["registry_counts"].items():
            if r_type != "total":
                t_reg.add_row(r_type.capitalize(), str(count))
        t_reg.add_section()
        t_reg.add_row("[bold white]TOTAL[/]", f"[bold yellow]{metrics['registry_counts']['total']}[/]")

        # Panel 4.2: Red Neuronal
        t_net = Table(title="🔗 4.2 Red Neuronal", box=box.ROUNDED, style="yellow")
        t_net.add_column("Métrica", justify="left")
        t_net.add_column("Valor", justify="right", style="bold white")
        t_net.add_row("Vínculos (Grafos)", str(metrics["network"]["total_links"]))
        t_net.add_row("Etiquetas Únicas", str(metrics["network"]["unique_tags"]))

        # Panel 4.3: Madurez Cognitiva (SRS)
        t_srs = Table(title="🧠 4.3 Madurez Cognitiva (SRS)", box=box.ROUNDED, style="green")
        t_srs.add_column("Indicador", justify="left")
        t_srs.add_column("Estado", justify="right", style="bold yellow")
        t_srs.add_row("Tarjetas Totales", str(metrics["srs"]["total_cards"]))
        t_srs.add_row("Para Repaso Hoy", f"[bold white on red]{metrics['srs']['due_today']}[/]")
        t_srs.add_row("Programadas Futuro", str(metrics["srs"]["due_future"]))
        t_srs.add_row("Dificultad Prom.", f"{metrics['srs']['avg_difficulty']:.2f}")
        t_srs.add_row("Estabilidad Prom.", f"{metrics['srs']['avg_stability']:.2f} días")
        t_srs.add_row("Diagnóstico", f"[white on bright_cyan]{metrics['srs']['retention_desc']}[/]")

        from rich.columns import Columns
        console.print(Align.center(Columns([Panel(t_reg, border_style="bright_cyan"), Panel(t_net, border_style="yellow")])))
        console.print()
        console.print(Align.center(Panel(t_srs, border_style="green", expand=False)))
        console.print()

        if filtro_activo:
            console.print(f"[yellow]🔍 Filtro activo: {filtro_activo}[/yellow]")

        action = Prompt.ask(
            "\n[bold][G][/] Sincronizar Google Drive  [bold][S][/] Filtrar por área/tag  [bold][Enter][/] Volver",
            choices=["g", "G", "s", "S", ""], show_choices=False, default="", console=console
        ).lower()

        if action == "g":
            # 4.4 Sincronización
            console.print("\n[bright_cyan]Iniciando exportación a Google Drive...[/]")
            try:
                with console.status("[white]Copiando base de datos y generando CSV en G:/Mi unidad/Nexus_Data...[/white]", spinner="dots"):
                    success, message = export_to_google_drive()
            except Exception as e:
                success, message = False, str(e)
                logger.exception("Fallo en export_to_google_drive")
            if success:
                console.print(f"\n[bold green]✅ ¡Sincronización Exitosa![/bold green]")
                console.print(f"[white]Tus datos están en: {message}[/white]")
            else:
                console.print(f"\n[bold white on red]❌ Error: {message}[/]")
            Prompt.ask("\n[white]Presiona ENTER para continuar...[/white]", default="")

        elif action == "s":
            # Filtrar estadísticas por área / tag
            filtro_activo = Prompt.ask(
                "[bold]Área, tag o tipo para filtrar[/] (Enter para ver todo)",
                default="", console=console
            ).strip()

        else:  # Enter → volver
            break



# ----------------------------------------------------------------------------
# 3. Menú Principal (Dashboard)
# ----------------------------------------------------------------------------

def main_loop():
    """Bucle infinito del Dashboard Principal — Arquitectura de 5 Componentes."""
    while True:
        console.clear()
        show_header()
        
        console.print(Align.center(get_stats_panel()))
        console.print()
        
        # Menú Principal — grid 5 componentes
        grid = Table.grid(expand=True, padding=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)

        grid.add_row(
            Panel("[bold bright_cyan][1] ➕ AGREGAR[/]\n[white]Archivos a la BD", border_style="bright_cyan", title="Captura"),
            Panel("[bold yellow][2] 🗂️ GESTIONAR[/]\n[bold bright_white]Explorar, Editar, Vincular", border_style="yellow", title="Mente"),
            Panel("[bold white on red][3] 🧠 RECALL[/]\n[bold yellow]Sesión Pomodoro SRS", border_style="red", title="Entreno")
        )
        grid.add_row(
            Panel("[bold green][4] 📊 ESTADÍSTICAS[/]\n[white]Métricas + Exportar", border_style="green", title="Análisis"),
            Panel("[bold white][5] ❌ SALIR[/]\n[white]Cerrar Nexus", border_style="white", title="Nexus"),
            Panel("[bold bright_white]🔍 OMNIBAR[/]\n[white]Escribe cualquier término para buscar", border_style="bright_white", title="Búsqueda"),
        )

        console.print(grid)
        
        help_content = (
            "[bold bright_cyan]1[/] Agregar │ [bold yellow]2[/] Gestionar │ [bold white on red]3[/] Recall │ "
            "[bold green]4[/] Estadísticas │ [bold white]5[/] Salir\n"
            "[bold white]Gestor:[/][yellow] ←/→ Págs │ Q Filtrar │ L Limpiar │ [ID] Ver detalle │ del [IDs] Borrar │ m/ia ID1 ID2 Vincular[/yellow]"
        )
        console.print(Panel(help_content, title="[white]COMANDOS RÁPIDOS[/]", border_style="white", padding=(0, 1)))
        console.print()

        user_input = Prompt.ask("[bold bright_cyan]Nexus ▶[/]", console=console).strip()

        try:
            if user_input == "1":
                menu_agregar()
            elif user_input == "2":
                menu_gestionar()
            elif user_input == "3":
                menu_active_recall()
            elif user_input == "4":
                menu_estadisticas()
            elif user_input in ["5", "0"] or user_input.lower() in ["q", "exit", "quit"]:
                console.print("\n[bold bright_cyan]Cerrando módulos de Nexus... ¡Hasta pronto![/]")
                time.sleep(1)
                sys.exit(0)
            elif user_input:
                if user_input.startswith(":"):
                    console.print(f"[yellow]Comando desconocido: {user_input}[/]")
                    time.sleep(1)
                    continue
                console.print(f"\n[bright_cyan]🔍 Omnibar: Saltando al Gestor con '[bold]{user_input}[/]'...[/]")
                time.sleep(0.5)
                menu_gestionar(initial_query=user_input)
        except ReturnToMain:
            continue
        except Exception as e:
            console.print(f"\n[bold red]❌ Error crítico en módulo:[/] {e}")
            logger.exception("Error en main_loop")
            Prompt.ask("[white]Enter para continuar...[/]")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold white on red]Interrupción detectada. Saliendo de Nexus...[/]")
        sys.exit(0)


```

---

## ui/dashboard_v1_backup.py
**Lineas: 1632**

```python
import sys
import time

# Forzar salida en UTF-8 para evitar errores de renderizado de Emojis en la terminal de Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.layout import Layout
from rich.table import Table
from rich.align import Align
from rich import box
from rich.text import Text
from rich.theme import Theme

# Tema personalizado de ALTO CONTRASTE para visibilidad total en terminales azules/oscuras
custom_theme = Theme({
    "dim": "bright_white",
    "cyan": "bright_cyan",
    "magenta": "yellow",
    "blue": "bright_blue",
    "prompt.choices": "bold yellow",
    "prompt.default": "bold bright_white",
    "prompt.invalid": "bold red",
    "prompt.invalid.choice": "bold white on red",
})

console = Console(theme=custom_theme)

import os
import subprocess
import msvcrt

def get_key() -> str:
    """Captura un solo carácter del teclado sin esperar a Enter (Solo Windows)."""
    if sys.platform == "win32":
        try:
            char = msvcrt.getch()
            # Manejar caracteres especiales (como flechas que devuelven dos bytes)
            if char in [b'\x00', b'\xe0']:
                msvcrt.getch()
                return ""
            return char.decode('utf-8').lower()
        except:
            return ""
    return ""

from modules.file_manager import ingest_local_file
from modules.web_scraper import ingest_web_resource, batch_ingest_urls
from modules.pkm_manager import create_note
from core.search_engine import search_registry, parse_query_string
from core.database import SessionLocal, nx_db, CardCreate, NexusLinkCreate
from agents.relationship_agent import generate_relationship_cards
from modules.study_engine import start_pomodoro_session, open_source_material
from modules.analytics import get_global_metrics
from modules.exporter import export_to_google_drive
from core.staging_db import staging_db, STAGING_DB_PATH
from modules.pipeline_manager import run_youtube_pipeline

# ----------------------------------------------------------------------------
# 1. Componentes Visuales del Dashboard
# ----------------------------------------------------------------------------

def show_header():
    """Muestra el banner principal de Nexus."""
    os.system('cls' if os.name == 'nt' else 'clear')
    title = Text("N E X U S", style="bold bright_cyan", justify="center")
    subtitle = Text("Cognitive Storage & active Recall Console", style="italic bright_white", justify="center")
    
    header_content = Text.assemble(title, "\n", subtitle)
    console.print(Panel(header_content, box=box.DOUBLE, border_style="bright_cyan", expand=False))
    console.print()

def get_stats_panel() -> Panel:
    """Retorna un Panel Rich con estadísticas reales consultadas desde la BD."""
    metrics = get_global_metrics()
    
    from rich.columns import Columns
    
    total_raw = metrics["registry_counts"].get("total", 0)
    cards_today = metrics["srs"]["due_today"]
    sys_links = metrics["network"]["total_links"]
    retention = metrics["srs"]["retention_desc"]

    stats_cols = Columns([
        Panel(f" [bold bright_cyan]{total_raw}[/]\n [white]Recursos[/]", title="🗄️ Cerebro", border_style="bright_cyan", padding=(1, 2)),
        Panel(f" [bold white on red] {cards_today} [/]\n [white]Repasos Hoy[/]", title="🧠 Foco", border_style="red", padding=(1, 2)),
        Panel(f" [bold yellow]{sys_links}[/]\n [white]Vínculos[/]", title="🔗 Red", border_style="yellow", padding=(1, 2)),
        Panel(f" [bold green]{retention}[/]\n [white]Madurez[/]", title="📈 Estado", border_style="green", padding=(1, 2))
    ], align="center", expand=False)

    return Panel(
        Align.center(stats_cols),
        title="[bold white]CUADRO DE MANDO COGNITIVO[/]",
        border_style="white",
        expand=True
    )

# ----------------------------------------------------------------------------
# 2. Sub-Menús y Flujos de Usuario
# ----------------------------------------------------------------------------

def menu_ingreso():
    """
    Sub-menú de Ingesta Estricta (Blueprint ux_workflows.md)
    """
    global Panel, Text
    # Estado local para este menu: el target de ingesta
    current_target = "local"
    
    while True:
        console.clear()
        show_header()
        
        target_color = "green" if current_target == "local" else "bold white on gold"
        target_name = "CORE (Local SSD)" if current_target == "local" else f"BUFFER (Nube G: {STAGING_DB_PATH})"
        
        console.print(Panel(
            f"[bold yellow]Menú de Ingesta Estricta[/]\n"
            f"Destino Actual: [{target_color}]{target_name}[/]\n\n"
            f"Selecciona el tipo de recurso a indexar:", 
            box=box.ROUNDED
        ))
        
        console.print("  [1] 📄 Añadir Archivo (Local)")
        console.print("  [2] 🌐 Añadir URL (Web/YouTube)")
        console.print("  [3] 📝 Escribir Nota Libre (Abre Editor Externo)")
        console.print("  [4] ⚙️ Añadir Aplicación / Herramienta")
        console.print("  [5] 🚀 Ingesta por Lote (Lote de URLs)")
        console.print(f"  [S] CAMBIAR DESTINO -> {'Buffer G:' if current_target=='local' else 'Nexus Core'}")
        console.print("  [0] 🔙 Volver al Menú Principal\n")

        opcion = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4", "5", "s", "S"], show_choices=False, console=console).lower()

        if opcion == "0":
            break
            
        if opcion == "s":
            if current_target == "local":
                if staging_db.init_staging():
                    current_target = "staging"
                    console.print("[bold yellow]🚀 ¡Modo STAGING Activado! Los datos irán a la unidad G:[/]")
                else:
                    console.print("[bold red]Error: No se puede activar Staging. ¿Está el drive G: montado?[/]")
            else:
                current_target = "local"
                console.print("[bold green]Modo CORE Local reactivado.[/]")
            time.sleep(1.2)
            continue

        db_active = nx_db if current_target == "local" else staging_db

        if opcion == "1":
            while True:
                ruta = Prompt.ask("\n[bold]Ruta absoluta del archivo[/bold]", console=console)
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                # Note: Local files always go to Local Core for now as path references are local
                resultado = ingest_local_file(ruta, tags_list)
                if resultado is not None:
                    console.print(f"\n[bold green]✅ Archivo indexado correctamente:[/] {resultado.title}")
                    
                    summary_text = Text()
                    summary_text.append(f"ID: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.id}\n", style="white")
                    summary_text.append(f"Tipo: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.type}\n", style="white")
                    summary_text.append(f"Título: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.title}\n", style="white")
                    summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                    summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                    
                    if resultado.content_raw:
                        content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                        summary_text.append(f"Vista Previa del Contenido:\n", style="bold green")
                        summary_text.append(content_preview, style="white")
                    else:
                        summary_text.append(f"Contenido: ", style="bold green")
                        summary_text.append("No se pudo extraer texto (Archivo binario o ilegible).", style="white italic")

                    console.print(Panel(summary_text, title="Detalles del Archivo", border_style="green"))
                    
                    if Prompt.ask("\n¿Deseas editar o ver los detalles completos de este registro ahora? (s/n)", choices=["s", "n"], default="n") == 's':
                        _show_record_detail(resultado.id)
                else:
                    console.print("\n[bold white on red]❌ No se pudo indexar. Verifica la ruta o los permisos.[/]")
                    
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRO archivo local | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False, console=console)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == 2:
            while True:
                url = Prompt.ask("\n[bold]Pega la URL (YouTube o Genérica)[/bold]", console=console)
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                console.print(f"\n[bright_cyan]Iniciando raspado contextual y transcripción hacia {current_target.upper()}...[/]")
                with console.status("[bright_white]Descargando Súper Schema de Web, por favor espera...[/bright_white]", spinner="dots"):
                     resultado = ingest_web_resource(url, tags_list, db_target=db_active)
                     
                if resultado is not None:
                     console.print(f"\n[bold green]✅ Recurso Web indexado exitosamente en la Knowledge Base.[/bold green]")
                     
                     # Mostrar lo descargado al usuario
                     summary_text = Text()
                     summary_text.append(f"ID: ", style="bold bright_cyan")
                     summary_text.append(f"{resultado.id}\n", style="white")
                     summary_text.append(f"Tipo: ", style="bold bright_cyan")
                     summary_text.append(f"{resultado.type}\n", style="white")
                     summary_text.append(f"Título: ", style="bold bright_cyan")
                     summary_text.append(f"{resultado.title}\n", style="white")
                     summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                     summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                     
                     content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                     summary_text.append(f"Contenido Extraído:\n", style="bold green")
                     summary_text.append(content_preview, style="white")
                     
                     console.print(Panel(summary_text, title="Detalles de Ingesta", border_style="green"))
                     
                     if Prompt.ask("\n¿Deseas editar o ver los detalles completos de este registro ahora? (s/n)", choices=["s", "n"], default="n", console=console) == 's':
                         _show_record_detail(resultado.id)

                else:
                     console.print("\n[bold white on red]❌ Hubo un fallo en la ingesta o no se pudo generar el texto principal de la URL.[/]")
                     
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRA URL | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False, console=console)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == 3:
            while True:
                titulo = Prompt.ask("\n[bold]Título de la Nueva Nota[/bold]", console=console)
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                console.print("\n[bright_white]Abriendo el sistema nativo. Al cerrar la ventana, tu nota se guardará automáticamente...[/bright_white]")
                
                resultado = create_note(titulo, tags_list)
                if resultado is not None:
                    console.print(f"\n[bold green]✅ Nota \"{resultado.title}\" almacenada en Knowledge Base.[/bold green]")
                    
                    summary_text = Text()
                    summary_text.append(f"ID: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.id}\n", style="white")
                    summary_text.append(f"Tipo: ", style="bold bright_cyan")
                    summary_text.append(f"nota_libre\n", style="white") # create_note returns a Registry object usually, check it
                    summary_text.append(f"Título: ", style="bold bright_cyan")
                    summary_text.append(f"{resultado.title}\n", style="white")
                    summary_text.append(f"Ubicación: ", style="bold bright_cyan")
                    summary_text.append(f"Nexus Database (nexus.db -> registros)\n\n", style="white")
                    
                    content_preview = resultado.content_raw[:800] + ("..." if len(resultado.content_raw) > 800 else "")
                    summary_text.append(f"Contenido de la Nota:\n", style="bold green")
                    summary_text.append(content_preview, style="white")
                    
                    console.print(Panel(summary_text, title="Detalles de la Nota", border_style="green"))
                    
                    if Prompt.ask("\n¿Deseas editar o ver los detalles completos de esta nota ahora? (s/n)", choices=["s", "n"], default="n") == 's':
                        _show_record_detail(resultado.id)
                else:
                    console.print("\n[yellow]⚠️ Nota cancelada. No se guardó nada.[/yellow]")
                    
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Escribir OTRA nota | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == 5:
            while True:
                console.print("\n[bold yellow]🚀 Ingesta Masiva de Nexus[/]")
                console.print("[dim]Puedes pegar múltiples URLs separadas por coma, o la ruta de un archivo .txt con una URL por línea.[/dim]")
                
                entrada = Prompt.ask("\n[bold]URLs o Ruta de Archivo[/bold]")
                tags_input = Prompt.ask("[bold]Tags para todo el lote[/bold]")
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []

                urls_to_process = []
                # Detectar si es un archivo o una lista de texto
                if os.path.isfile(entrada):
                    try:
                        with open(entrada, 'r', encoding='utf-8') as f:
                            urls_to_process = [line.strip() for line in f if line.strip()]
                    except Exception as e:
                        console.print(f"[red]Error leyendo archivo: {e}[/]")
                else:
                    urls_to_process = [u.strip() for u in entrada.split(',') if u.strip()]

                if not urls_to_process:
                    console.print("[yellow]No se encontraron URLs válidas para procesar.[/yellow]")
                else:
                    console.print(f"\n[cyan]Iniciando proceso por lote hacia {current_target.upper()} ({len(urls_to_process)} recursos)...[/]")
                    success, failed = batch_ingest_urls(urls_to_process, tags_list, db_target=db_active)
                    
                    console.print(f"\n[bold green]📊 Resumen de Lote:[/]")
                    console.print(f"  ✅ [bold green]Exitosos:[/] {len(success)}")
                    console.print(f"  ❌ [bold red]Fallidos:[/] {len(failed)}")
                    
                    if failed:
                        console.print("\n[bold red]URLs que dieron error:[/]")
                        for f_url in failed[:10]:
                            console.print(f"  - {f_url}")
                        if len(failed) > 10: console.print(f"  ... y {len(failed)-10} más.")

                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Iniciar OTRO lote | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return

        elif opcion == 4:
            while True:
                console.print("\n[bold yellow]Añadir Aplicación o Herramienta[/]")
                titulo = Prompt.ask("\n[bold]Nombre de la App / Plataforma[/bold]", console=console)
                ruta = Prompt.ask("[bold]Ruta / URL o Comando de Ejecución[/bold]", console=console)
                
                # Nuevos campos solicitados por Arquitecto:
                plataforma_input = Prompt.ask("[bold]Plataforma[/] (ej. PC, Android, Web)", default="PC", console=console)
                logueo = Prompt.ask("[bold]¿Requiere Credenciales / Logueo?[/] (s/n)", default="n", console=console).lower() == 's'
                logueo_str = "Sí" if logueo else "No"
                descripcion = Prompt.ask("[bold]Breve Descripción o Uso Principal[/] (opcional)", console=console)
                
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]", console=console)
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                try:
                    from core.database import RegistryCreate, nx_db, TagCreate
                    
                    # Construir bloque de texto para Active Recall 
                    content_blob = (
                        f"Herramienta o Aplicación: {titulo}\n"
                        f"Plataforma: {plataforma_input.strip()}\n"
                        f"Requiere Logueo: {logueo_str}\n"
                        f"Ruta o Comando: {ruta}\n"
                    )
                    if descripcion:
                        content_blob += f"Descripción: {descripcion.strip()}\n"

                    data = RegistryCreate(
                        type="app",
                        title=titulo,
                        path_url=ruta,
                        content_raw=content_blob,
                        meta_info={
                            "platform_type": plataforma_input.strip(),
                            "requires_login": logueo,
                            "app_description": descripcion.strip() if descripcion else ""
                        }
                    )
                    reg = nx_db.create_registry(data)
                    for t in tags_list:
                        nx_db.add_tag(reg.id, TagCreate(value=t))
                    console.print(f"\n[bold green]✅ Aplicación '{titulo}' (ID {reg.id}) registrada correctamente en la base de datos.[/bold green]")
                except Exception as e:
                    console.print(f"\n[bold white on red]❌ Error al guardar la aplicación: {str(e)}[/]")

                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Añadir OTRA Aplicación | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return


def menu_explorar(initial_query: str = ""):
    """Explorador Maestro con Paginación, Panel de Detalles y Repaso."""
    page = 0
    items_per_page = 13 # Paginación física ajustada a la ventana
    
    # Filtros actuales (en blanco significa "traer todo")
    filtros = {
        'inc_name': "", 'exc_name': "", 'inc_tags': "", 'exc_tags': "",
        'inc_exts': "", 'exc_exts': "", 'has_info': "", 'inc_ids': "", 'is_source': ""
    }

    if initial_query:
        filtros = parse_query_string(initial_query)

    while True:
        console.clear()
        show_header()
        
        # Procesar extensiones para el Search Engine
        inc_exts_list = [e.strip() for e in filtros['inc_exts'].split(',')] if filtros['inc_exts'] else None
        exc_exts_list = [e.strip() for e in filtros['exc_exts'].split(',')] if filtros['exc_exts'] else None
        
        with SessionLocal() as db_session:
            results = search_registry(
                db_session=db_session,
                inc_name_path=filtros['inc_name'],
                exc_name_path=filtros['exc_name'],
                inc_tags=filtros['inc_tags'],
                exc_tags=filtros['exc_tags'],
                inc_extensions=inc_exts_list,
                exc_extensions=exc_exts_list,
                has_info=filtros['has_info'],
                record_ids_str=filtros['inc_ids'],
                is_flashcard_source=filtros['is_source'],
                limit=items_per_page + 1, # Truco para detectar página siguiente
                offset=page * items_per_page
            )
            
        has_next = len(results) > items_per_page
        display_results = results[:items_per_page]
        
        # Dibujar Tabla Principal garantizando todas las columnas
        title = f"[bold bright_cyan]Explorador Maestro (Pág. {page + 1})[/] | [white]Filtros Activos: {'Sí' if any(filtros.values()) else 'No'}[/]"
        table = Table(title=title, box=box.ROUNDED, show_lines=True)
        table.add_column("ID Único", justify="right", style="bright_cyan", no_wrap=True)
        table.add_column("Tipo", style="yellow")
        table.add_column("Título", style="bold bright_white")
        table.add_column("Ubicación/Desc", style="white")
        table.add_column("Modificado", style="italic green")

        for reg in display_results:
            info = reg.path_url or ""
            if len(info) > 35: info = "..." + info[-32:]
            
            tipo = reg.type
            if reg.metadata_dict and 'extension' in reg.metadata_dict:
                tipo += f" ({reg.metadata_dict['extension']})"

            desc_extract = ""
            if reg.content_raw: desc_extract = reg.content_raw.replace('\n', ' ')[:30] + "..."
            
            # Unir información visual forzando que aparezca siempre
            ubic_desc = f"{info}\n[white]{desc_extract}[/]"
            
            fecha = reg.modified_at.strftime("%y-%m-%d %H:%M") if reg.modified_at else "--/--/--"
            table.add_row(str(reg.id), tipo, reg.title or "N/A", ubic_desc, fecha)

        console.print(table)
        
        # Opciones de Navegación del Explorador
        console.print("\n[bold bright_cyan]Controles del Explorador:[/]")
        console.print("  [bold]n[/] Siguiente Pág. | [bold]p[/] Pág. Anterior")
        console.print("  [bold]s[/] Buscar/Filtrar | [bold]l[/] Limpiar Búsqueda")
        console.print("  [bold]v[ID][/] Ver/Editar Detalles del Registro (ej: [bold]v5[/])")
        console.print("  [bold]del [IDs][/] Borrado en lote (ej: [bold]del 1,2,3-10[/])")
        console.print("  [bold]0[/] Volver al Menú Principal\n")
        
        cmd = Prompt.ask("Comando", console=console).strip().lower()
        
        if cmd == '0' or cmd == 'q':
            break
        elif cmd == 'n':
            if has_next: page += 1
            else:
                console.print("[yellow]Ya estás en la última página de resultados.[/]")
                time.sleep(1)
        elif cmd == 'p':
            if page > 0: page -= 1
        elif cmd == 'l':
            for k in filtros: filtros[k] = ""
            page = 0
        elif cmd == 's':
            console.print("\n[bold yellow]🔍 Smart Omnibar[/]")
            # Guía rápida de sintaxis para el usuario:
            # palabra -> busca en título/ruta | t:tag -> busca etiqueta
            # -palabra -> excluye | e:ext -> busca extensión (pdf, jpg, yt/web)
            # i:1-50 -> rango IDs | s:y -> solo con flashcards
            console.print("[white]Uso: [bright_white]término[/] [bright_cyan]t:[/]etiqueta [yellow]e:[/]ext [bright_white]i:[/]ID [green]s:y[/] (o [red]-[/]término para excluir)[/white]")
            query = Prompt.ask("[bold bright_cyan]Búsqueda[/]", default="", console=console)
            if query.strip():
                filtros = parse_query_string(query)
                page = 0
            else:
                console.print("[yellow]Búsqueda vacía. Mostrando todo.[/yellow]")
                for k in filtros: filtros[k] = ""
                time.sleep(1)
        elif cmd.startswith('v') and cmd[1:].isdigit():
            rec_id = int(cmd[1:])
            _show_record_detail(rec_id)
        elif cmd.startswith('del ') or cmd.startswith('borrar '):
            raw_ids = cmd.replace('del ', '').replace('borrar ', '').strip()
            ids_to_delete = []
            
            # 1. Si el usuario pide borrar TODO lo filtrado actualmente en memoria profunda
            if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                if not any(filtros.values()):
                    console.print("[bold yellow]Aviso: No tienes ningún filtro aplicado. Debes realizar una búsqueda ('s') antes de usar 'del all' para evitar borrar toda tu base de datos por accidente.[/bold yellow]")
                    time.sleep(3.5)
                    continue
                else:
                    # Traemos absolutamente todos los resultados que concuerdan con la métrica sin el límite de paginación
                    with SessionLocal() as curr_session:
                        all_filtered = search_registry(
                            db_session=curr_session,
                            inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                            inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                            inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                            has_info=filtros['has_info'], limit=None, offset=0
                        )
                        ids_to_delete = [r.id for r in all_filtered]
                        
            # 2. Si el usuario dio IDs estandar manuales (ej: 1,2,3-10)
            else:
                for part in raw_ids.split(','):
                    part = part.strip()
                    if '-' in part:
                        try:
                            start_str, end_str = part.split('-')
                            start_id = int(start_str)
                            end_id = int(end_str)
                            ids_to_delete.extend(range(min(start_id, end_id), max(start_id, end_id) + 1))
                        except ValueError:
                            pass
                    else:
                        if part.isdigit():
                            ids_to_delete.append(int(part))
            
            ids_to_delete = list(set(ids_to_delete))
            if not ids_to_delete:
                console.print("[bold yellow]No se detectaron IDs válidos para borrar o la búsqueda arrojó cero resultados.[/bold yellow]")
                time.sleep(1.5)
            else:
                console.print(f"\n[bold yellow] ⚠️ ADVERTENCIA DE BORRADO MASIVO: {len(ids_to_delete)} REGISTROS ⚠️ [/bold yellow]")
                if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                    console.print("[yellow]Estás a punto de eliminar absolutamente todos los registros (incluso los de las páginas siguientes) que concuerdan con tus filtros actuales bajo esta búsqueda.[/yellow]")
                else:    
                    console.print(f"[bold yellow]Registros implicados:[/] [white]{str(ids_to_delete[:15])}... (y más)[/white]" if len(ids_to_delete) > 15 else f"[bold yellow]Registros implicados:[/] {ids_to_delete}")
                
                confirm = Prompt.ask("Escribe [bold white]eliminar lote[/] para confirmar, o presiona Enter para abortar", console=console).strip().lower()
                
                if confirm == 'eliminar lote':
                    with console.status(f"[dim]Destruyendo {len(ids_to_delete)} registros y sus dependencias (tags, flashcards)...[/dim]", spinner="dots"):
                        success_count = 0
                        for d_id in ids_to_delete:
                            if nx_db.delete_registry(d_id):
                                success_count += 1
                        console.print(f"\n[bold green]✅ Lote evaporado: {success_count}/{len(ids_to_delete)} registros eliminados de la DB.[/]")
                    time.sleep(2.5)
                    # Forzar recarga de la página si se borraron elementos
                    page = 0
                else:
                    console.print("\n[yellow]Operación de borrado en lote cancelada.[/yellow]")
                    time.sleep(1.5)
        else:
            console.print("[bold white on red]Comando no reconocido.[/]")
            time.sleep(1)

def _show_record_detail(rec_id: int):
    """Vista detallada de un Registro con Opciones de Edición, Apertura Física y Repaso Interactivo."""
    from core.database import Tag, Registry, NexusLink
    
    while True:
        console.clear()
        show_header()
        
        with SessionLocal() as db_session:
            reg = nx_db.get_registry(rec_id)
            if not reg:
                console.print(f"[bold yellow]❌ Registro con ID {rec_id} no encontrado en la Base de Datos.[/bold yellow]")
                time.sleep(1.5)
                break
                
            tags_db = db_session.query(Tag).filter(Tag.registry_id == rec_id).all()
            tags_list = [t.value for t in tags_db]
            tags_str = ", ".join(tags_list) if tags_list else "Sin Etiquetas"
            
            # Preparar metadatos extendidos si existen
            extra_meta = ""
            if reg.meta_info and reg.type == "youtube":
                m = reg.meta_info
                extra_meta = f"\n[bold yellow]📊 Metadatos YouTube:[/]\n"
                if m.get('channel'): extra_meta += f"  • Canal: {m['channel']}\n"
                if m.get('duration'): extra_meta += f"  • Duración: {m['duration'] // 60} min {m['duration'] % 60} seg\n"
                if m.get('view_count'): extra_meta += f"  • Vistas: {m['view_count']:,}\n"
                if m.get('upload_date'): extra_meta += f"  • Fecha Upload: {m['upload_date']}\n"

            # Truncado agresivo para garantizar visibilidad vertical total
            def tiny_trunc(text, limit=75):
                if not text: return "[white]N/A[/white]"
                text = text.replace('\n', ' ').strip()
                return (text[:limit-3] + "...") if len(text) > limit else text

            panel_text = (
                f"[bold white]ID:[/] [bright_cyan]{reg.id}[/] | "
                f"[bold white]Tipo:[/] [yellow]{reg.type.upper()}[/] | "
                f"[bold white]Recall:[/] {'[green]SÍ[/]' if reg.is_flashcard_source else '[red]NO[/]'}\n"
                f"[bold white]Título:[/] [bright_white]{tiny_trunc(reg.title, 80)}[/]\n"
                f"[bold white]Ruta:[/] [white]{tiny_trunc(reg.path_url, 80)}[/]\n"
                f"[bold white]Tags:[/] [yellow]{tiny_trunc(tags_str, 80)}[/]\n"
                f"{tiny_trunc(extra_meta, 120)}\n"
                f"[bold green]✨ Resumen (IA):[/] {tiny_trunc(reg.summary, 140)}\n"
                f"[bold green]📄 Contenido:[/] {tiny_trunc(reg.content_raw, 140)}\n\n"
                f"[yellow]Tip: Pulsa [bold]3[/] para lectura completa o [bold]2[/] para abrir fuente.[/]"
            )
            console.print(Panel(panel_text, title="🔍 Ficha Técnica Compacta", box=box.HEAVY, border_style="bright_cyan"))
            
            # Sub-Menu Vista Detalle (Refactorizado v2.0 - Hotkeys habilitadas)
            console.print("\n[bold yellow]Menú de Gestión y Cognición (Presiona una tecla):[/]")
            console.print("  [1] 📝 Editar Metadatos         [2] 🚀 Abrir Archivo/Web")
            console.print("  [3] 🧠 Enfoque (Modo Lectura)   [4] 🤖 Cerebro IA (Menú)")
            console.print("  [5] 🗂️  Mazo de Estudio (Menú)  [6] 🗑️  Eliminar Registro")
            console.print("  [0] 🔙 Volver al Explorador\n")
            
            action = get_key()
            if action == '0':
                break
            elif action == '1':
                console.print("\n[white]Deja un campo vacío si no deseas modificarlo.[/white]")
                
                n_source = Prompt.ask("[bold]¿Es fuente de Flashcards?[/] (s/n/Enter para omitir)", default="")
                if n_source.strip().lower() in ['s', 'n']:
                    db_session.query(Registry).filter(Registry.id == rec_id).update({
                        Registry.is_flashcard_source: 1 if n_source.strip().lower() == 's' else 0
                    })

                n_tags = Prompt.ask("[bold]Nuevas Etiquetas[/] (separadas por coma)")
                if n_tags.strip():
                    db_session.query(Tag).filter(Tag.registry_id == rec_id).delete()
                    for t in n_tags.split(','):
                        if t.strip():
                            # Se inserta bajo la misma sesión SQLite sin recursar la conexión nx_db
                            db_session.add(Tag(registry_id=rec_id, value=t.strip()))
                            
                n_desc = Prompt.ask("[bold]Nueva Descripción o Correcciones de Texto[/]")
                if n_desc.strip():
                    db_session.query(Registry).filter(Registry.id == rec_id).update({
                        Registry.content_raw: n_desc.strip()
                    })
                    
                db_session.commit()
                    
                console.print("[green]Cambios guardados con éxito en la Base de Datos.[/]")
                time.sleep(1.5)
                
            elif action == '2':
                path_str = reg.path_url
                if not path_str:
                    console.print("[bold white on red]Este registro no dispone de una ubicación física o URL.[/]")
                    time.sleep(1.5)
                    continue
                    
                if path_str.startswith("http"):
                    import webbrowser
                    console.print(f"[green]Navegando a Web:[/] {path_str}")
                    webbrowser.open(path_str)
                    time.sleep(1)
                elif reg.type == 'file' and not path_str.startswith('nexus://'):
                    if os.path.exists(path_str):
                        console.print(f"[bold green]Abriendo explorador local en:[/] {path_str}")
                        if sys.platform == "win32":
                            norm_path = os.path.normpath(path_str)
                            import subprocess
                            subprocess.Popen(f'explorer /select,"{norm_path}"')
                        time.sleep(1.5)
                    else:
                        console.print(f"[bold white on red]Directorio o Archivo extraviado en el PC:[/] {path_str}")
                        time.sleep(2.5)
                else:
                    console.print("[yellow]No admite lanzar entorno gráfico. (Puede ser una nota nativa o comando bash).[/yellow]")
                    time.sleep(2)
                    
            elif action == '3':
                # Modo Repaso Interactivo con Nodos y Salto
                while True:
                    console.clear()
                    show_header()
                    content_panel = Panel(
                        f"{reg.content_raw}",
                        title=f"[bold yellow]📖 Modo Lectura - {reg.title}[/]",
                        border_style="bright_yellow", padding=(1, 4),
                        subtitle="[white]Pulsa 'Enter' para salir o 'vID' para saltar a un nodo relacionado[/white]"
                    )
                    console.print(content_panel)
                    
                    enlaces_salientes = db_session.query(NexusLink).filter(NexusLink.source_id == rec_id).all()
                    enlaces_entrantes = db_session.query(NexusLink).filter(NexusLink.target_id == rec_id).all()
                    
                    if enlaces_salientes or enlaces_entrantes:
                        console.print("\n[bold yellow]🕸️ Red Neuronal (Vínculos Directos):[/]")
                        for ln in enlaces_salientes:
                            tg = db_session.query(Registry).filter(Registry.id == ln.target_id).first()
                            if tg: console.print(f"  [bright_cyan]v{tg.id}[/] ➔ {tg.title} [white]({ln.relation_type})[/white]")
                        for ln in enlaces_entrantes:
                            src = db_session.query(Registry).filter(Registry.id == ln.source_id).first()
                            if src: console.print(f"  [bright_cyan]v{src.id}[/] ⬅ {src.title} [white]({ln.relation_type})[/white]")
                    
                    cmd_foco = Prompt.ask("\n[bold bright_cyan]Acción[/]", console=console).strip().lower()
                    
                    if not cmd_foco:
                        break  # Termina repaso
                    elif cmd_foco.startswith('v') and cmd_foco[1:].isdigit():
                        salto_id = int(cmd_foco[1:])
                        _show_record_detail(salto_id) # Salto recursivo
                        break
                    else:
                        continue
                        
            elif action == '6':
                console.print("\n[bold white on red] ⚠️ ADVERTENCIA DE DESTRUCCIÓN ⚠️ [/]")
                console.print("[bold white on red]Estás a punto de evaporar este registro. Se romperán todos sus vínculos en la red neuronal, etiquetas y Flashcards asociadas.[/]")
                confirm = Prompt.ask("Escribe [bold white]eliminar[/] para confirmar, o presiona Enter para abortar", console=console).strip().lower()
                
                if confirm == 'eliminar':
                    success = nx_db.delete_registry(rec_id)
                    if success:
                        console.print("\n[bold green]✅ Registro evaporado con éxito de la base de datos.[/]")
                    else:
                        console.print("\n[bold white on red]❌ Hubo un error al intentar borrar el registro físico de la base de datos.[/]")
                    time.sleep(1.5)
                    break
                else:
                    console.print("\n[yellow]Operación de borrado cancelada. Sobrevivió un día más.[/yellow]")
                    time.sleep(1.5)

            elif action == '4':
                # SUB-MENÚ CEREBRO IA
                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold yellow]🧠 Herramientas de IA para:[/] {reg.title}", border_style="yellow"))
                    console.print("\n  [1] 🤖 Generar Flashcards IA (Extraer Conceptos)")
                    console.print("  [2] 📝 Generar Resumen IA (Síntesis Ejecutiva)")
                    console.print("  [0] 🔙 Volver al Panel de Registro\n")
                    
                    sub_ia = Prompt.ask("Selecciona herramienta IA", choices=["0", "1", "2"], show_choices=False, console=console)
                    
                    if sub_ia == '0': break
                    
                    if sub_ia == '1':
                        from core.database import CardCreate
                        from agents.study_agent import generate_deck_from_registry, get_client
                        from rich.prompt import Confirm
                        
                        mockup_only = False
                        if get_client():
                            console.print(f"\n[bold yellow]⚠️  AVISO DE CONSUMO DE TOKENS[/bold yellow]")
                            if not Confirm.ask("[bold white]¿Confirmas envío a Gemini para flashcards?[/bold white]"):
                                console.print("[yellow]Modo seguro activado.[/yellow]")
                                mockup_only = True

                        console.print("\n[bold yellow]🤖 Destilando conceptos...[/]")
                        with console.status("[dim]Procesando...[/dim]", spinner="dots"):
                            cards = generate_deck_from_registry(reg, mockup_only=mockup_only)
                        
                        if cards:
                            for card in cards:
                                nx_db.create_card(CardCreate(parent_id=rec_id, question=card.question, answer=card.answer, type=card.card_type))
                            console.print(f"\n[bold green]✅ ¡Éxito! {len(cards)} tarjetas nuevas en el sistema.[/bold green]")
                            
                            post_ia = Prompt.ask("\n[bold][v][/] Ver/Editar tarjetas ahora | [bold][Enter][/] Volver", default="", console=console)
                            if post_ia.lower() == 'v':
                                # Saltamos al menú de gestión (acción 5 del menú principal de detalle)
                                action = '5'
                                break # Rompemos el bucle del sub-menú IA para que el bucle superior procese action='5'
                        else:
                            console.print("\n[bold red]❌ Falló la generación.[/]")
                            time.sleep(2)
                            
                    elif sub_ia == '2':
                        from agents.summary_agent import generate_summary_from_registry
                        console.print("\n[bold yellow]🤖 Sintetizando ideas...[/]")
                        with console.status("[dim]Analizando...[/dim]", spinner="dots"):
                            summary = generate_summary_from_registry(reg)
                        if summary:
                            nx_db.update_summary(rec_id, summary)
                            console.print(f"\n[bold green]✅ Resumen actualizado.[/bold green]")
                            console.print(Panel(summary, title="Resumen IA", border_style="green"))
                            Prompt.ask("\n[bold]Enter para continuar...[/]")
                        else:
                            console.print("\n[bold red]❌ Falló la síntesis.[/]")
                            time.sleep(2)

            elif action == '5':
                # SUB-MENÚ MAZO DE ESTUDIO
                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold bright_cyan]🗂️ Gestión del Mazo para:[/] {reg.title}", border_style="bright_cyan"))
                    console.print("\n  [1] 👀 Ver/Gestionar Tarjetas Actuales")
                    console.print("  [2] ✍️  Añadir Tarjeta Manualmente")
                    console.print("  [0] 🔙 Volver al Panel de Registro\n")
                    
                    sub_mz = Prompt.ask("Selecciona acción", choices=["0", "1", "2"], show_choices=False, console=console)
                    if sub_mz == '0': break

                    if sub_mz == '2':
                        console.print("\n[bold yellow]✍️  Creación Manual[/]")
                        q = Prompt.ask("[bold bright_cyan]Pregunta[/] (o 'cancelar')", console=console)
                        if q.strip().lower() not in ['cancelar', '']:
                            a = Prompt.ask("[bold green]Respuesta[/]")
                            t = Prompt.ask("[bold]Tipo[/]", choices=["Factual", "Conceptual", "Cloze"], default="Factual")
                            nx_db.create_card(CardCreate(parent_id=rec_id, question=q.strip(), answer=a.strip(), type=t))
                            console.print("\n[bold green]✅ Tarjeta vinculada.[/bold green]")
                            time.sleep(1.5)
                    
                    elif sub_mz == '1':
                        from core.database import Card
                        while True:
                            console.clear()
                            show_header()
                            cards_db = db_session.query(Card).filter(Card.parent_id == rec_id).all()
                            if not cards_db:
                                console.print("[yellow]Mazo vacío.[/yellow]")
                                time.sleep(1.5); break
                            
                            total_cards = len(cards_db)
                            for i, c in enumerate(cards_db):
                                idx = i + 1
                                console.print(f"\n[bold yellow]🗂️ Tarjeta {idx} de {total_cards}[/]")
                                console.print(f"  [bright_cyan]Q:[/] {c.question}")
                                console.print(f"  [green]A:[/] {c.answer}")
                                console.print("-" * 40)
                            
                            console.print("\n[1] Editar  [2] Eliminar  [0] Atrás")
                            cmd = Prompt.ask("Comando", choices=["0", "1", "2"], show_choices=False)
                            if cmd == '0': break
                            elif cmd == '2':
                                cid_del = IntPrompt.ask("ID de tarjeta a borrar")
                                target = db_session.query(Card).filter(Card.id == cid_del, Card.parent_id == rec_id).first()
                                if target:
                                    db_session.delete(target); db_session.commit()
                                    console.print("[green]Borrado exitoso.[/]")
                                    time.sleep(1)
                            elif cmd == '1':
                                cid_ed = IntPrompt.ask("ID de tarjeta a editar")
                                target = db_session.query(Card).filter(Card.id == cid_ed, Card.parent_id == rec_id).first()
                                if target:
                                    target.question = Prompt.ask("Q", default=target.question)
                                    target.answer = Prompt.ask("A", default=target.answer)
                                    db_session.commit()
                                    console.print("[green]Actualizado.[/]")
                                    time.sleep(1)


def menu_adelantar_repaso():
    """Sub-menú para adelantar repasos con opciones de filtrado y cantidad."""
    from core.database import Registry, Card, Tag
    from sqlalchemy import func
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_header()
        
        console.print(Panel("[bold yellow]Menú: Adelantar Repaso (Flashcards)[/]\n\n"
                            "  [1] 📋 Repaso de Tema Específico (Lista y Filtros)\n"
                            "  [2] 🎲 Repaso al Azar (Mezclar todo el mazo)\n"
                            "  [3] 🔢 Cantidad de Tarjetas a Repasar (Fijar límite)\n"
                            "  [0] 🔙 Regresar al menú anterior", 
                            title="Estudio Intensivo / Adelantar", border_style="yellow"))
        
        opcion = Prompt.ask("\nSelecciona una opción", choices=["0", "1", "2", "3"], show_choices=False)
        
        if opcion == "0":
            break
        
        elif opcion == "1":
            # Repaso de tema específico con filtros
            page = 0
            items_per_page = 10
            filtros_tema = {'name': "", 'tag': ""}
            
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                show_header()
                console.print(f"[bold cyan]🔍 Selección de Tema Específico[/] | Filtros: {filtros_tema}\n")
                
                with SessionLocal() as db_session:
                    # Buscamos registros que tengan tarjetas asociadas
                    query = db_session.query(Registry).join(Card, Card.parent_id == Registry.id).group_by(Registry.id)
                    
                    if filtros_tema['name']:
                        query = query.filter(Registry.title.ilike(f"%{filtros_tema['name']}%"))
                    if filtros_tema['tag']:
                        query = query.join(Tag, Tag.registry_id == Registry.id).filter(Tag.value.ilike(f"%{filtros_tema['tag']}%"))
                    
                    total_count = query.count()
                    results = query.limit(items_per_page).offset(page * items_per_page).all()
                
                table = Table(title="Temas Disponibles con Flashcards", box=box.ROUNDED)
                table.add_column("ID", style="bright_cyan")
                table.add_column("Tipo", style="yellow")
                table.add_column("Título", style="bold bright_white")
                table.add_column("Tarjetas", justify="center")
                
                with SessionLocal() as db_session:
                    for reg in results:
                        count = db_session.query(func.count(Card.id)).filter(Card.parent_id == reg.id).scalar()
                        table.add_row(str(reg.id), reg.type.upper(), reg.title or "Sin Título", str(count))
                
                console.print(table)
                console.print(f"\n[white]Página {page+1} | Total temas: {total_count}[/white]")
                console.print("\n[bold cyan]Controles:[/]")
                console.print("  [bold]ID[/] Seleccionar Tema | [bold]f[/] Cambiar Filtros | [bold]n/p[/] Pags | [bold]0[/] Atras")
                
                cmd = Prompt.ask("\nComando").strip().lower()
                
                if cmd == '0':
                    break
                elif cmd == 'n' and (page + 1) * items_per_page < total_count:
                    page += 1
                elif cmd == 'p' and page > 0:
                    page -= 1
                elif cmd == 'f':
                    filtros_tema['name'] = Prompt.ask("Filtrar por Título", default=filtros_tema['name'])
                    filtros_tema['tag'] = Prompt.ask("Filtrar por Etiqueta", default=filtros_tema['tag'])
                    page = 0
                elif cmd.isdigit():
                    tid = int(cmd)
                    start_pomodoro_session(pomodoro_minutes=25, adelantar=True, topic_id=tid)
                    Prompt.ask("\n[bold]Sesión Finalizada. Presiona Enter para volver...[/]")
                    break

        elif opcion == "2":
            # Repaso al azar
            start_pomodoro_session(pomodoro_minutes=25, adelantar=True, shuffled=True)
            Prompt.ask("\n[bold]Sesión Aleatoria Finalizada. Presiona Enter para volver...[/]")
            
        elif opcion == "3":
            # Cantidad de tarjetas
            limit = IntPrompt.ask("\n¿Cuántas tarjetas deseas repasar hoy en total?", default=20)
            shuff = Prompt.ask("¿Quieres que el orden sea aleatorio? ([bold]s[/]/[bold]n[/])", choices=["s", "n"], default="s") == 's'
            start_pomodoro_session(pomodoro_minutes=60, adelantar=True, shuffled=shuff, card_limit=limit)
            Prompt.ask("\n[bold]Sesión Personalizada Finalizada. Presiona Enter para volver...[/]")

def menu_active_recall():
    """Puente hacia módulos de estudio y SRS, fusionado con un Explorador Gestor de Flashcards (Lotes)"""
    from core.database import Registry, Card
    from sqlalchemy import func
    from datetime import datetime, timezone
    from agents.study_agent import generate_deck_from_registry
    
    page = 0
    items_per_page = 8
    filtros = {
        'inc_name': "", 'exc_name': "", 'inc_tags': "", 'exc_tags': "",
        'inc_exts': "", 'exc_exts': "", 'has_info': "", 'inc_ids': "", 'is_source': ""
    }

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_header()
        
        # --- 1. Banner Superior: Status de Pomodoros Pendientes ---
        now = datetime.now(timezone.utc)
        with nx_db.Session() as db_session:
            due_cards = db_session.query(Card).filter((Card.next_review == None) | (Card.next_review <= now)).subquery()
            topics_today = db_session.query(Registry.id, Registry.title, func.count(due_cards.c.id)).join(
                due_cards, due_cards.c.parent_id == Registry.id
            ).group_by(Registry.id).all()
            
            if topics_today:
                c_total = sum([c for _, _, c in topics_today])
                console.print(Panel(f"[bold bright_cyan]🔥 Motor Pomodoro Listo:[/] Tienes [bold white on red]{c_total} tarjetas pendientes[/] distribuidas en {len(topics_today)} temas para hoy.", box=box.ROUNDED, border_style="bright_cyan"))
            else:
                console.print(Panel("[green]🎉 Tu mente está al día. No tienes repasos pendientes hoy.[/]", box=box.ROUNDED, border_style="green"))

        # --- 2. Explorador de Fuentes de Flashcards ---
        # Si el usuario NO tiene filtros activos, forzamos mostrar solo los temas pendientes para hacer Pomodoro hoy
        filtro_vacio = not any(filtros.values())
        ids_a_buscar = filtros['inc_ids']
        if filtro_vacio:
            if topics_today:
                ids_a_buscar = ",".join(str(tid) for tid, _, _ in topics_today)
            else:
                ids_a_buscar = "-1" # Invalid ID list para forzar a que no aparezca nada

        inc_exts_list = [e.strip() for e in filtros['inc_exts'].split(',')] if filtros['inc_exts'] else None
        exc_exts_list = [e.strip() for e in filtros['exc_exts'].split(',')] if filtros['exc_exts'] else None
        
        with SessionLocal() as curr_session:
            results = search_registry(
                db_session=curr_session,
                inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                has_info=filtros['has_info'], record_ids_str=ids_a_buscar,
                is_flashcard_source=filtros['is_source'], limit=items_per_page + 1, offset=page * items_per_page
            )
            
        has_next = len(results) > items_per_page
        display_results = results[:items_per_page]
        
        table = Table(title=f"[bold yellow]Selector de Fuentes (Pág. {page + 1})[/] | [dim]Filtros Activos: {'Sí' if any(filtros.values()) else 'No'}[/]", box=box.ROUNDED, show_lines=True)
        table.add_column("ID Único", justify="right", style="bright_cyan", no_wrap=True)
        table.add_column("Título", style="bold bright_white")
        table.add_column("Descripción (Compacta)")
        table.add_column("Tags", style="yellow")
        table.add_column("Pend/Tot", justify="center")

        with nx_db.Session() as s_aux:
            for reg in display_results:
                from core.database import Tag
                tag_list = s_aux.query(Tag).filter(Tag.registry_id == reg.id).all()
                tags_str = ", ".join([t.value for t in tag_list]) if tag_list else ""
                
                total_cards = s_aux.query(func.count(Card.id)).filter(Card.parent_id == reg.id).scalar()
                pending_cards = s_aux.query(func.count(Card.id)).filter(
                    Card.parent_id == reg.id,
                    (Card.next_review == None) | (Card.next_review <= now)
                ).scalar()
                
                # Truncado agresivo para la tabla de selección
                titulo_list = (reg.title[:40] + "...") if len(reg.title or "") > 40 else (reg.title or "")
                desc_list = (reg.content_raw.replace('\n', ' ')[:50] + "...") if len(reg.content_raw or "") > 50 else (reg.content_raw or "")
                tags_list_view = (tags_str[:30] + "...") if len(tags_str) > 30 else tags_str

                table.add_row(
                    str(reg.id), 
                    titulo_list, 
                    desc_list,
                    tags_list_view,
                    f"[bold yellow]{pending_cards}[/]/[white]{total_cards}[/]"
                )

        console.print(table)
        
        # --- 3. Controles del Menú Active Recall ---
        console.print("\n[bold bright_cyan]Opciones de Construcción Lote (Flashcards):[/]")
        console.print("  [bold]ia [IDs][/]  🤖 Crear Flashcards con IA para los IDs dados (ej: [bold]ia 1,2,5-10[/] o [bold]ia all[/] para filtrados)")
        console.print("  [bold]man [ID][/] 📝 Crear Flashcards Manualmente para un ID (ej: [bold]man 5[/])")
        console.print("  [bold]j [ID][/]   🚀 Abrir material fuente (archivo/web/nota) para un ID")
        console.print("  [bold]e [ID][/]   📝 Editar Registro (Título, Descripción, Tags)")
        console.print("  [bold]del [IDs][/] 🗑️  Eliminar Registros de Raíz junto a Flashcards (ej: [bold]del 5[/] o [bold]del all[/])")
        console.print("\n[bold bright_cyan]Opciones del Motor de Estudio:[/]")
        console.print("  [bold]pm[/]       🍅 Iniciar Pomodoro (Repasar todos los pendientes mezclados)")
        console.print("  [bold]pa[/]       ⏩ Adelantar (Menú de temas específicos, Azar y Cantidad)")
        console.print("\n[bold bright_cyan]Filtros:[/]")
        console.print("  [bold]s[/] Filtrar/Buscar | [bold]l[/] Limpiar Filtros | [bold]n/p[/] Pág. Siguiente/Anterior | [bold]0[/] Salir\n")

        cmd = Prompt.ask("Comando", console=console).strip().lower()
        
        if cmd == '0' or cmd == 'q':
            break
        elif cmd == 'n':
            if has_next: page += 1
            else:
                console.print("[yellow]Ya estás en la última página de resultados.[/]")
                time.sleep(1)
        elif cmd == 'p':
            if page > 0: page -= 1
        elif cmd == 'l':
            for k in filtros: filtros[k] = ""
            page = 0
        elif cmd == 's':
            console.print("\n[bold yellow]🔍 Smart Omnibar (Recall Filter)[/]")
            console.print("[bright_white]Usa [white]t:tag e:ext i:ids s:y[/white] para filtrar fuentes de estudio.[/bright_white]")
            query = Prompt.ask("[bold bright_cyan]Filtrar[/]", default="", console=console)
            if query.strip():
                filtros = parse_query_string(query)
                page = 0
            else:
                for k in filtros: filtros[k] = ""
                time.sleep(1)
            
        elif cmd == 'pm':
            start_pomodoro_session(pomodoro_minutes=25, adelantar=False, topic_id=None)
            Prompt.ask("\n[bold]Sesión Finalizada. Presiona Enter para volver a Active Recall...[/]")
            
        elif cmd == 'pa':
            menu_adelantar_repaso()

        elif cmd.startswith('e ') or cmd.startswith('edit '):
            raw_id = cmd.replace('edit ', '').replace('e ', '').strip()
            if raw_id.isdigit():
                rec_id = int(raw_id)
                _show_record_detail(rec_id)
            else:
                console.print("[bold white on red]Uso: e [ID] (ej. e 5)[/]")
                time.sleep(1)

        elif cmd.startswith('j '):
            raw_id = cmd.replace('j ', '').strip()
            if raw_id.isdigit():
                rec_id = int(raw_id)
                reg_obj = nx_db.get_registry(rec_id)
                if reg_obj:
                    console.print(f"\n[bright_white]Abriendo fuente para ID {rec_id}: {reg_obj.title}...[/bright_white]")
                    open_source_material(reg_obj)
                else:
                    console.print("[bold white on red]Registro no encontrado en DB.[/]")
                    time.sleep(1.5)
            else:
                console.print("[bold white on red]Uso: j [ID] (ej. j 5)[/]")
                time.sleep(1)

        elif cmd.startswith('man '):
            raw_id = cmd.replace('man ', '').strip()
            if raw_id.isdigit():
                rec_id = int(raw_id)
                reg_obj = nx_db.get_registry(rec_id)
                if not reg_obj:
                    console.print("[bold white on red]Registro no encontrado en DB.[/]")
                    time.sleep(1.5)
                    continue
                
                # Opción de navegar a la fuente antes de crear
                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold yellow]Preparación: Creación Manual[/]\nTema: [bold]{reg_obj.title}[/]", box=box.ROUNDED))
                    action_prep = Prompt.ask("\n¿Deseas abrir el material fuente para visualizar contenido? ([bold]f[/] abrir / [bold]Enter[/] ir a creación)").strip().lower()
                    if action_prep == 'f':
                        open_source_material(reg_obj)
                    else:
                        break

                while True:
                    console.clear()
                    show_header()
                    console.print(Panel(f"[bold yellow]Creación Manual Flashcards[/]\nCreando tarjetas para: [bold]{reg_obj_ia.title}[/]", box=box.ROUNDED))
                    console.print("[white]Escribe 'salir' en la Pregunta para terminar.[/white]\n")
                    
                    types_list = ["Factual", "Conceptual", "Reversible", "MCQ", "TF", "Cloze", "Matching", "MAQ"]
                    # Forzamos que el prompt use nuestra consola con el tema de colores corregido
                    t_card_raw = Prompt.ask("[bold yellow]Tipo de Tarjeta[/]", choices=types_list, default="Factual", console=console).strip()
                    
                    # Mapeo manual para asegurar que acepte minúsculas aunque el 'choices' sea en Mayúsculas
                    # (Rich por defecto es estricto con las choices)
                    t_card = "Factual"
                    for t in types_list:
                        if t_card_raw.lower() == t.lower():
                            t_card = t
                            break
                    
                    q = ""
                    a = ""
                    
                    if t_card == "Reversible":
                        q_side = Prompt.ask("[bold cyan]Lado A[/]")
                        if q_side.lower() == 'salir': break
                        a_side = Prompt.ask("[bold green]Lado B[/]")
                        # Crear las dos variantes
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_side, answer=a_side, type="Factual"))
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=a_side, answer=q_side, type="Factual"))
                        console.print("[yellow]✅ ¡Dos tarjetas (A->B y B->A) creadas![/yellow]")
                    
                    elif t_card == "TF":
                        q = Prompt.ask("[bold cyan]Afirmación[/]")
                        if q.lower() == 'salir': break
                        a = Prompt.ask("[bold green]¿Es Verdadera?[/] (v/f)", choices=["v", "f"])
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q, answer=a, type="TF"))
                    
                    elif t_card == "MCQ" or t_card == "MAQ":
                        import json
                        prompt = Prompt.ask("[bold cyan]Pregunta / Enunciado[/]")
                        if prompt.lower() == 'salir': break
                        options = {}
                        while True:
                            key = Prompt.ask("[white]Letra de opción (o Enter para finalizar)[/white]", console=console)
                            if not key: break
                            val = Prompt.ask(f"Texto para opción {key}", console=console)
                            options[key] = val
                        
                        q_json = json.dumps({"prompt": prompt, "options": options})
                        a = Prompt.ask("[bold green]Letra(s) de la respuesta correcta[/] (ej. 'a' o 'a,b')")
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_json, answer=a, type=t_card))

                    elif t_card == "Cloze":
                        console.print("[white]Uso la sintaxis: La capital de {{c1::Francia}} es {{c2::París}}[/white]")
                        q = Prompt.ask("[bold bright_cyan]Texto con Huecos[/]", console=console)
                        if q.lower() == 'salir': break
                        # Extraer respuestas automáticamente para el campo answer
                        import re
                        matches = re.findall(r"\{\{c\d+::(.*?)\}\}", q)
                        a = ", ".join(matches)
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q, answer=a, type="Cloze"))

                    elif t_card == "Matching":
                        import json
                        console.print("[white]Ingresa pares de conceptos relacionados.[/white]")
                        pairs = {}
                        while True:
                            left = Prompt.ask("[white]Término Izquierda (o Enter para finalizar)[/white]", console=console)
                            if not left: break
                            right = Prompt.ask(f"Término Derecha para '{left}'", console=console)
                            pairs[left] = right
                        
                        q_json = json.dumps({"pairs": pairs})
                        # La respuesta visual es simplemente el listado de pares correctos
                        a_text = "\n".join([f"{k} -> {v}" for k, v in pairs.items()])
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_json, answer=a_text, type="Matching"))

                    else:
                        # Factual / Conceptual (Estándar)
                        q = Prompt.ask("[bold bright_cyan]Pregunta (Q)[/]", console=console)
                        if q.lower() == 'salir' or not q.strip(): break
                        a = Prompt.ask("[bold green]Respuesta (A)[/]", console=console)
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q, answer=a, type=t_card))
                    
                    console.print("[yellow]✅ Operación de creación finalizada.[/yellow]")
                    cont = Prompt.ask("\n¿Deseas añadir otra tarjeta a este tema? ([bold]s[/]/[bold]n[/])", choices=["s", "n"], default="s").lower()
                    if cont == 'n':
                        break
            else:
                console.print("[bold white on red]Ingresa un ID numérico válido para creación manual.[/]")
                time.sleep(1)

        elif cmd.startswith('ia '):
            raw_ids = cmd.replace('ia ', '').strip()
            target_ids = []
            
            if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                with SessionLocal() as curr_session:
                    all_filtered = search_registry(
                        db_session=curr_session,
                        inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                        inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                        inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                        has_info=filtros['has_info'], record_ids_str=filtros['inc_ids'],
                        is_flashcard_source=filtros['is_source'], limit=None, offset=0
                    )
                    target_ids = [r.id for r in all_filtered]
            else:
                for part in raw_ids.split(','):
                    part = part.strip()
                    if '-' in part:
                        try:
                            start_str, end_str = part.split('-')
                            s_id, e_id = int(start_str), int(end_str)
                            target_ids.extend(range(min(s_id, e_id), max(s_id, e_id) + 1))
                        except ValueError:
                            pass
                    else:
                        if part.isdigit(): target_ids.append(int(part))
                        
            target_ids = list(set(target_ids))
            
            if not target_ids:
                console.print("[bold white on red]No se detectaron IDs válidos o la búsqueda está vacía.[/]")
                time.sleep(2)
                continue
                
            console.print(f"\n[bold yellow]🤖 ATENCIÓN: El Agente IA procesará un lote de {len(target_ids)} registros.[/]")
            confirm = Prompt.ask("¿Confirmas la generación masiva de este lote pagando con tus Tokens API? (s/n)").strip().lower()
            if confirm == 's':
                success_generations = 0
                total_cards_made = 0
                for d_id in target_ids:
                    reg_obj_ia = nx_db.get_registry(d_id)
                    if reg_obj_ia:
                        console.print(f"\n[white]Procesando Registro ID {d_id}: '{reg_obj_ia.title}'[/white]")
                        # Invocado a IA (Mockup solo si el cliente no está disponible, ya confirmamos el lote arriba)
                        cards_generated = generate_deck_from_registry(reg_obj_ia, mockup_only=False)
                        if cards_generated:
                            for card in cards_generated:
                                nx_db.create_card(CardCreate(parent_id=d_id, question=card.question, answer=card.answer, type=card.card_type))
                            success_generations += 1
                            total_cards_made += len(cards_generated)
                            console.print(f"[bold green]✓ {len(cards_generated)} tarjetas anidadas a ID {d_id}[/bold green]")
                        else:
                            console.print(f"[yellow]⚠ IA omitió ID {d_id} (Falta de info o error API).[/yellow]")
                
                console.print(f"\n[bold magenta]🎉 OPERACIÓN IA LOTE FINALIZADA:[/]\n  ‣ Registros Exitosos: {success_generations}/{len(target_ids)}\n  ‣ Total Flashcards Agregadas al Sistema: {total_cards_made}")
                Prompt.ask("\n[bold]Presiona Enter para continuar...[/]")
            else:
                console.print("[yellow]Operación omitida.[/yellow]")
                time.sleep(1)

        elif cmd.startswith('del ') or cmd.startswith('borrar '):
            raw_ids = cmd.replace('del ', '').replace('borrar ', '').strip()
            ids_to_delete = []
            
            # 1. Si el usuario pide borrar TODO lo filtrado
            if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                if not any(filtros.values()):
                    console.print("[bold white on red]¡Peligro! No tienes ningún filtro aplicado. Debes realizar una búsqueda ('s') primero para evitar borrar toda tu base de datos accidentalmente.[/]")
                    time.sleep(3.5)
                    continue
                else:
                    with SessionLocal() as curr_session:
                        all_filtered = search_registry(
                            db_session=curr_session,
                            inc_name_path=filtros['inc_name'], exc_name_path=filtros['exc_name'],
                            inc_tags=filtros['inc_tags'], exc_tags=filtros['exc_tags'],
                            inc_extensions=inc_exts_list, exc_extensions=exc_exts_list,
                            has_info=filtros['has_info'], record_ids_str=filtros['inc_ids'],
                            is_flashcard_source=filtros['is_source'], limit=None, offset=0
                        )
                        ids_to_delete = [r.id for r in all_filtered]
                        
            # 2. Si el usuario dio IDs estandar manuales (ej: 1,2,3-10)
            else:
                for part in raw_ids.split(','):
                    part = part.strip()
                    if '-' in part and not part.startswith('-'):
                        try:
                            start_str, end_str = part.split('-')
                            start_id = int(start_str)
                            end_id = int(end_str)
                            ids_to_delete.extend(range(min(start_id, end_id), max(start_id, end_id) + 1))
                        except ValueError:
                            pass
                    else:
                        if part.isdigit():
                            ids_to_delete.append(int(part))
            
            ids_to_delete = list(set(ids_to_delete))
            if not ids_to_delete:
                console.print("[bold white on red]No se detectaron IDs válidos para borrar o la búsqueda arrojó cero resultados.[/]")
                time.sleep(1.5)
            else:
                console.print(f"\n[bold white on red] ⚠️ ADVERTENCIA DE BORRADO MASIVO: {len(ids_to_delete)} REGISTROS DE RAÍZ ⚠️ [/]")
                if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                    console.print("[yellow]Estás a punto de eliminar permanentemente todos los registros base y TUS TARJETAS DE ESTUDIO de este lote filtrado.[/yellow]")
                else:    
                    console.print(f"[bold white on red]Registros implicados:[/] [white]{str(ids_to_delete[:15])}... (y más)[/white]" if len(ids_to_delete) > 15 else f"[bold white on red]Registros implicados:[/] {ids_to_delete}")
                
                confirm = Prompt.ask("Escribe [bold white]eliminar lote[/] para confirmar, o presiona Enter para abortar", console=console).strip().lower()
                
                if confirm == 'eliminar lote':
                    with console.status(f"[dim]Destruyendo {len(ids_to_delete)} registros y sus flashcards heredadas...[/dim]", spinner="dots"):
                        success_count = 0
                        for d_id in ids_to_delete:
                            if nx_db.delete_registry(d_id):
                                success_count += 1
                        console.print(f"\n[bold green]✅ Lote evaporado: {success_count}/{len(ids_to_delete)} registros y flashcards eliminados permanentemente.[/]")
                    time.sleep(2.5)
                    page = 0
                else:
                    console.print("\n[yellow]Operación de borrado en lote abortada.[/yellow]")
                    time.sleep(1.5)

        else:
            console.print("[bold white on red]Comando no reconocido.[/]")
            time.sleep(1)


def menu_conectar():
    """Centro de Vinculación Neuronal (Cockpit de Enlaces)"""
    page = 0
    items_per_page = 10
    filtros = {
        'inc_name': "", 'exc_name': "", 'inc_tags': "", 'exc_tags': "",
        'inc_exts': "", 'exc_exts': "", 'has_info': "", 'inc_ids': "", 'is_source': ""
    }

    while True:
        console.clear()
        show_header()
        
        # 1. Búsqueda de registros para referencia
        inc_exts_list = [e.strip() for e in filtros['inc_exts'].split(',')] if filtros['inc_exts'] else None
        exc_exts_list = [e.strip() for e in filtros['exc_exts'].split(',')] if filtros['exc_exts'] else None
        
        with SessionLocal() as db_session:
            results = search_registry(
                db_session=db_session,
                inc_name_path=filtros['inc_name'],
                inc_tags=filtros['inc_tags'],
                inc_extensions=inc_exts_list,
                limit=items_per_page + 1,
                offset=page * items_per_page
            )
            
        has_next = len(results) > items_per_page
        display_results = results[:items_per_page]
        
        # 2. Render de la Tabla de Referencia
        table = Table(title="🔗 Cockpit de Enlaces (Identifica IDs para Conectar)", box=box.ROUNDED, border_style="yellow")
        table.add_column("ID", justify="right", style="bright_cyan")
        table.add_column("Título", style="bold bright_white")
        table.add_column("Tipo", style="yellow")
        table.add_column("Contenido (Preview)", style="italic green")
        
        for reg in display_results:
            preview = (reg.content_raw or "").replace('\n', ' ')[:50] + "..."
            table.add_row(str(reg.id), reg.title or "N/A", reg.type, preview)
            
        console.print(table)
        
        # 3. Controles
        console.print("\n[bold yellow]Comandos de Conexión:[/]")
        console.print("  [bold]ia ID1 ID2[/] 🤖 IA Match (Crea vínculo + tarjetas comparativas)")
        console.print("  [bold]m ID1 ID2[/]  🔗 Vínculo Manual (Crea relación simple)")
        console.print("  [bold]s [query][/]  🔍 Filtrar lista | [bold]n/p[/] Pág | [bold]0[/] Volver al Menú Principal\n")
        
        cmd = Prompt.ask("Nexus Linker", console=console).strip().lower()
        
        if cmd == '0':
            break
        elif cmd == 'n' and has_next: page += 1
        elif cmd == 'p' and page > 0: page -= 1
        elif cmd == 's':
            query = Prompt.ask("[bold yellow]Filtrar registros[/]", console=console)
            if query.strip():
                filtros = parse_query_string(query)
                page = 0
            else:
                for k in filtros: filtros[k] = ""
        
        # LÓGICA DE VINCULACIÓN
        elif cmd.startswith('m ') or cmd.startswith('ia '):
            mode = 'ia' if cmd.startswith('ia ') else 'm'
            parts = cmd.split()
            if len(parts) < 3:
                console.print("[bold red]Error: Debes proporcionar dos IDs. Ej: ia 5 10[/]")
                time.sleep(1.5)
                continue
            
            try:
                id_a, id_b = int(parts[1]), int(parts[2])
                rec_a = nx_db.get_registry(id_a)
                rec_b = nx_db.get_registry(id_b)
                
                if not rec_a or not rec_b:
                    console.print("[bold red]Uno o ambos IDs no existen.[/]")
                    time.sleep(1.5)
                    continue

                # --- VISTA DE COMPARACIÓN VISUAL ENRIQUECIDA ---
                console.clear()
                show_header()
                from rich.columns import Columns
                
                # Preparar datos A
                sum_a = rec_a.summary if rec_a.summary else "[white]Sin resumen (Usa Cerebro IA para generarlo)[/white]"
                url_a = rec_a.path_url if rec_a.path_url else "[white]Sin enlace[/white]"
                cont_a = (rec_a.content_raw or "[white]Sin descripción[/white]")[:300] + "..."
                
                # Preparar datos B
                sum_b = rec_b.summary if rec_b.summary else "[white]Sin resumen (Usa Cerebro IA para generarlo)[/white]"
                url_b = rec_b.path_url if rec_b.path_url else "[white]Sin enlace[/white]"
                cont_b = (rec_b.content_raw or "[white]Sin descripción[/white]")[:300] + "..."

                comp_view = Columns([
                    Panel(
                        f"[bold bright_cyan]ID {id_a} | {rec_a.type.upper()}[/]\n\n"
                        f"[bold green]✨ RESUMEN IA:[/]\n{sum_a}\n\n"
                        f"[bold bright_blue]🔗 ENLACE ORIGIN:[/] {url_a}\n\n"
                        f"[white]📄 CONTENIDO:[/]\n{cont_a}",
                        title=f"📦 {rec_a.title}", border_style="bright_cyan", padding=(1,2)
                    ),
                    Panel(
                        f"[bold yellow]ID {id_b} | {rec_b.type.upper()}[/]\n\n"
                        f"[bold green]✨ RESUMEN IA:[/]\n{sum_b}\n\n"
                        f"[bold bright_blue]🔗 ENLACE ORIGIN:[/] {url_b}\n\n"
                        f"[white]📄 CONTENIDO:[/]\n{cont_b}",
                        title=f"📦 {rec_b.title}", border_style="yellow", padding=(1,2)
                    )
                ], expand=True)
                
                console.print(Panel(comp_view, title="🔍 Comparación de Registros para Vinculación", border_style="white"))

                if mode == 'm':
                    console.print("\n[bold]Estableciendo Vínculo Manual:[/]")
                    rel = Prompt.ask("Define el Tipo de Relación (ej. complementa, refuta, mismo_tema)", default="relacionado")
                    desc = Prompt.ask("Nota de contexto (opcional)", default="")
                    nx_db.create_link(NexusLinkCreate(source_id=id_a, target_id=id_b, relation_type=rel, description=desc))
                    console.print(f"\n[bold green]✅ ¡Vínculo forjado! Red neuronal actualizada.[/bold green]")
                else:
                    from rich.prompt import Confirm
                    console.print(f"\n[bold yellow]🤖 MODO IA MATCH ACTIVADO[/bold yellow]")
                    console.print(f"[white]Gemini analizará ambos contenidos para encontrar divergencias y crear flashcards de contraste.[/white]")
                    if not Confirm.ask(f"\n[bold white]¿Confirmas envío a Gemini?[/bold white]"):
                        console.print("[yellow]Operación cancelada.[/yellow]")
                        time.sleep(1)
                        continue

                    console.print(f"\n[bold yellow]🤖 Iniciando IA Match entre {id_a} y {id_b}...[/]")
                    with console.status("[white]Cerebro de IA procesando divergencias...[/white]", spinner="dots"):
                        cards = generate_relationship_cards(rec_a, rec_b)
                    
                    if cards:
                        nx_db.create_link(NexusLinkCreate(source_id=id_a, target_id=id_b, relation_type="IA_Match"))
                        for c in cards:
                            nx_db.create_card(CardCreate(parent_id=c.parent_id, question=c.question, answer=c.answer, type=c.card_type))
                        console.print(f"[bold green]✅ Relación forjada. {len(cards)} tarjetas creadas.[/bold green]")
                    else:
                        console.print("[bold red]El agente IA no devolvió resultados.[/]")
                
                Prompt.ask("\n[bold]Presiona Enter para continuar...[/bold]", console=console)
            except ValueError:
                console.print("[bold red]Los IDs deben ser números.[/]")
                time.sleep(1.5)

def menu_estadisticas():
    """Puente hacia UI combinada de Data Analytics y Cognitive Analytics"""
    console.clear()
    show_header()
    
    with console.status("[white]Consultando Súper Schema y Red Neuronal...[/white]", spinner="dots"):
        metrics = get_global_metrics()
        
    console.print()
    
    # Panel Izquierdo: Composición del Cerebro
    t_reg = Table(title="🗄️ Composición del Cerebro", box=box.ROUNDED, style="bright_cyan")
    t_reg.add_column("Tipo", justify="left")
    t_reg.add_column("Cantidad", justify="right", style="bold white")
    
    for r_type, count in metrics["registry_counts"].items():
        if r_type != "total":
            t_reg.add_row(r_type.capitalize(), str(count))
    t_reg.add_section()
    t_reg.add_row("[bold white]TOTAL[/]", f"[bold yellow]{metrics['registry_counts']['total']}[/]")
    
    # Panel Derecho: Red Neuronal
    t_net = Table(title="🔗 Red Neuronal", box=box.ROUNDED, style="yellow")
    t_net.add_column("Métrica", justify="left")
    t_net.add_column("Valor", justify="right", style="bold white")
    t_net.add_row("Vínculos (Grafos)", str(metrics["network"]["total_links"]))
    t_net.add_row("Etiquetas Únicas", str(metrics["network"]["unique_tags"]))
    
    # Panel Inferior: Active Recall & Madurez
    t_srs = Table(title="🧠 Madurez Cognitiva (SRS)", box=box.ROUNDED, style="green")
    t_srs.add_column("Indicador", justify="left")
    t_srs.add_column("Estado", justify="right", style="bold yellow")
    
    t_srs.add_row("Tarjetas Totales", str(metrics["srs"]["total_cards"]))
    t_srs.add_row("Para Repaso Hoy", f"[bold white on red]{metrics['srs']['due_today']}[/]")
    t_srs.add_row("Programadas Futuro", str(metrics["srs"]["due_future"]))
    t_srs.add_row("Dificultad Prom.", f"{metrics['srs']['avg_difficulty']:.2f}")
    t_srs.add_row("Estabilidad Prom.", f"{metrics['srs']['avg_stability']:.2f} días")
    t_srs.add_row("Diagnóstico", f"[white on bright_cyan]{metrics['srs']['retention_desc']}[/]")
    
    # Renderizamos las tablas juntas usando columnas
    from rich.columns import Columns
    console.print(Align.center(Columns([Panel(t_reg, border_style="bright_cyan"), Panel(t_net, border_style="yellow")])))
    console.print()
    console.print(Align.center(Panel(t_srs, border_style="green", expand=False)))
    
    action = Prompt.ask("\n[bold][e][/] Sincronizar con Google Drive (G:) | [bold][Enter][/] Volver", choices=["e", ""], show_choices=False, default="", console=console)
    
    if action == "e":
        console.print("\n[bright_cyan]Iniciando exportacion a Google Drive...[/]")
        with console.status("[white]Copiando base de datos y generando CSV en G:/Mi unidad/Nexus_Data...[/white]", spinner="dots"):
            success, message = export_to_google_drive()
            
        if success:
            console.print(f"\n[bold green]✅ ¡Sincronizacion Exitosa![/bold green]")
            console.print(f"[white]Tus datos estan listos para descargar en: {message}[/white]")
        else:
            console.print(f"\n[bold white on red]❌ Error en la sincronizacion: {message}[/]")
            
        Prompt.ask("\n[white]Presiona ENTER para continuar...[/white]", default="")

# ----------------------------------------------------------------------------
# 3. Menú Principal (Dashboard)
# ----------------------------------------------------------------------------

def main_loop():
    """Bucle infinito del Dashboard Principal."""
    while True:
        console.clear()
        show_header()
        
        # Muestra las de estadísticas globales fusionadas
        console.print(Align.center(get_stats_panel()))
        console.print()
        
        # Menú Principal Interactivo (GRID DE ALTO RENDIMIENTO)
        grid = Table.grid(expand=True, padding=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="center", ratio=1)

        grid.add_row(
            Panel("[bold bright_cyan][1] ➕ INGRESO[/]\n[white]PC, Web y Notas", border_style="bright_cyan", title="Captura"),
            Panel("[bold yellow][2] 🔍 EXPLORADOR[/]\n[bold bright_white]Gestión Universal", border_style="yellow", title="Mente"),
            Panel("[bold white on red][3] 🧠 RECALL[/]\n[bold yellow]Sesión Pomodoro", border_style="red", title="Entreno")
        )
        grid.add_row(
            Panel("[bold yellow][4] 🔗 CONECTAR[/]\n[white]Red Neuronal", border_style="yellow", title="Grafos"),
            Panel("[bold green][5] 📊 MÉTRICAS[/]\n[white]Data Analytics", border_style="green", title="Logros"),
            Panel("[bold bright_blue][6] 🚀 PIPELINE[/]\n[white]YouTube Automation", border_style="bright_blue", title="Power")
        )
        grid.add_row(
            Panel("[bold white][0] ❌ SALIR[/]\n[white]Cerrar Sistema", border_style="white", title="Nexus"),
            None,
            None
        )

        console.print(grid)
        
        # Chuleta de Comandos (Cheat Sheet) solicitada por el usuario
        help_content = (
            "[bold bright_cyan]:i[/] Ingesta   [bold yellow]:r[/] Recall   [bold green]:m[/] Métricas   [bold yellow][palabra][/] Buscar\n"
            "[bold white]Hotkeys (Detalle):[/] [white]2[/] Abrir [white]3[/] Lectura [white]4[/] IA [white]5[/] Mazo [white]0[/] Atrás\n"
            "[bold white]Explorador:[/][yellow] vID Ver | s Buscar | n/p Pags | t:tag e:ext -exc[/yellow]"
        )
        console.print(Panel(help_content, title="[white]CHULETA DE COMANDOS RÁPIDOS[/]", border_style="white", padding=(0, 1)))
        console.print()

        user_input = Prompt.ask("[bold bright_cyan]Nexus Command / Omnibar[/]", console=console).strip()

        if user_input == "1" or user_input.lower().startswith(":i"):
            menu_ingreso()
        elif user_input == "2":
            menu_explorar()
        elif user_input == "3" or user_input.lower().startswith(":r"):
            menu_active_recall()
        elif user_input == "4":
            menu_conectar()
        elif user_input == "5" or user_input.lower().startswith(":m"):
            menu_estadisticas()
        elif user_input == "6":
            run_youtube_pipeline()
            Prompt.ask("\n[bold]Pipeline finalizado. Enter para volver al Dashboard...[/bold]", console=console)
        elif user_input == "0" or user_input.lower() in ["q", "exit", "quit"]:
            console.print("\n[bold bright_cyan]Cerrando módulos de Nexus... ¡Hasta pronto![/]")
            time.sleep(1)
            sys.exit(0)
        elif user_input:
            # Lógica de Omnibar Global
            # Detectar comandos especiales o tratar como búsqueda
            if user_input.startswith(":"):
                console.print(f"[yellow]Comando desconocido: {user_input}[/]")
                time.sleep(1)
                continue
                
            console.print(f"\n[bright_cyan]🔍 Omnibar: Saltando al Explorador con '[bold]{user_input}[/]'...[/]")
            time.sleep(0.5)
            menu_explorar(initial_query=user_input)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold white on red]Interrupción detectada. Saliendo de Nexus...[/]")
        sys.exit(0)

```

---

