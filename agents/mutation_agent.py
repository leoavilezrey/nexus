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
    result_type=MutatedDeck,
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
