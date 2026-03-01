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
