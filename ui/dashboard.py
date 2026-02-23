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
import os
import subprocess

from modules.file_manager import ingest_local_file
from modules.pkm_manager import create_note
from core.search_engine import search_registry
from core.database import SessionLocal, nx_db, CardCreate, NexusLinkCreate
from agents.relationship_agent import generate_relationship_cards
from modules.study_engine import get_due_cards, update_card_srs, get_resource_record

console = Console()

# ----------------------------------------------------------------------------
# 1. Componentes Visuales del Dashboard
# ----------------------------------------------------------------------------

def show_header():
    """Muestra el banner principal de Nexus."""
    # En Windows PowerShell, console.clear() a veces no blanquea bien el backbuffer
    os.system('cls' if os.name == 'nt' else 'clear')
    title = Text("N E X U S", style="bold cyan", justify="center")
    subtitle = Text("Cognitive Storage & active Recall Console", style="italic blue", justify="center")
    
    header_content = Text.assemble(title, "\n", subtitle)
    console.print(Panel(header_content, box=box.DOUBLE, border_style="blue", expand=False))
    console.print()

def get_stats_panel() -> Panel:
    """Retorna un Panel Rich con estadísticas (Ficticias por ahora)."""
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2))
    table.add_column("Categoría", style="bold")
    table.add_column("Datos")
    
    # Datos Ficticios (Se conectarán al core/database.py más adelante)
    total_files = 1420
    total_notes = 45
    total_videos = 12
    total_cards = 320
    cards_today = 15
    sys_links = 89

    table.add_row("🗃️ Registro Total:", f"{total_files} Archivos | {total_notes} Notas | {total_videos} Videos")
    table.add_row("🧠 Active Recall:", f"{total_cards} Tarjetas Totales | [bold red]{cards_today} Listas para Repaso Hoy[/]")
    table.add_row("🔗 Red de Cnx.:", f"{sys_links} Vínculos entre conceptos")

    return Panel(
        Align.center(table),
        title="[bold green]Estado Unificado[/]",
        border_style="green",
        expand=False
    )

# ----------------------------------------------------------------------------
# 2. Sub-Menús y Flujos de Usuario
# ----------------------------------------------------------------------------

def menu_ingreso():
    """
    Sub-menú de Ingesta Estricta (Blueprint ux_workflows.md)
    Pregunta explícitamente qué tipo de fuente agregar sin usar IA predictiva.
    """
    console.clear()
    show_header()
    console.print(Panel("[bold yellow]Menú de Ingesta Estricta[/]\nSelecciona el tipo de recurso a indexar:", box=box.ROUNDED))
    
    console.print("  [1] 📄 Añadir Archivo (Local)")
    console.print("  [2] 🌐 Añadir URL (Web/YouTube)")
    console.print("  [3] 📝 Escribir Nota Libre (Abre Editor Externo)")
    console.print("  [4] ⚙️ Añadir Aplicación / Herramienta")
    console.print("  [0] 🔙 Volver al Menú Principal\n")

    opcion = IntPrompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4"], show_choices=False)

    if opcion == 1:
        ruta = Prompt.ask("\n[bold]Ruta absoluta del archivo[/bold]")
        tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]")
        tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
        
        resultado = ingest_local_file(ruta, tags_list)
        if resultado is not None:
            console.print(f"\n[bold green]✅ Archivo indexado correctamente:[/] {resultado.title}")
        else:
            console.print("\n[bold red]❌ No se pudo indexar. Verifica la ruta o los permisos.[/bold red]")
            
        Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")
        
    elif opcion == 2:
        console.print("\n[blue]Preparando extractor de metadatos web...[/] (Módulo en construcción)")
        Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")
        
    elif opcion == 3:
        titulo = Prompt.ask("\n[bold]Título de la Nueva Nota[/bold]")
        tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]")
        tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
        
        console.print("\n[dim]Abriendo el sistema nativo. Al cerrar la ventana, tu nota se guardará automáticamente...[/dim]")
        
        resultado = create_note(titulo, tags_list)
        if resultado is not None:
            console.print(f"\n[bold green]✅ Nota \"{resultado.title}\" almacenada en Knowledge Base.[/bold green]")
        else:
            console.print("\n[yellow]⚠️ Nota cancelada. No se guardó nada.[/yellow]")
            
        Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")
        
    elif opcion == 4:
        console.print("\n[blue]Abriendo formulario de aplicación...[/] (Módulo en construcción)")
        Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")

def menu_explorar():
    """Puente hacia core/search_engine.py integrando la tabla de resultados interactiva."""
    console.clear()
    show_header()
    console.print(Panel("[bold magenta]Explorador Maestro[/bold magenta]\n[dim]Deja en blanco los campos que no quieras usar. Separa múltiples términos con comas.[/dim]", box=box.ROUNDED))

    # Prompts interactivos para inclusión y exclusión (como en tu viejo gestor)
    inc_name = Prompt.ask("Nombre o Ruta a [bold green]INCLUIR[/]", default="")
    exc_name = Prompt.ask("Nombre o Ruta a [bold red]EXCLUIR[/]", default="")
    inc_tags = Prompt.ask("Etiquetas a [bold green]INCLUIR[/]", default="")
    exc_tags = Prompt.ask("Etiquetas a [bold red]EXCLUIR[/]", default="")
    inc_exts_input = Prompt.ask("Extensiones a [bold green]INCLUIR[/] (ej. pdf, md, __web__)", default="")
    exc_exts_input = Prompt.ask("Extensiones a [bold red]EXCLUIR[/]", default="")
    has_info = Prompt.ask("¿Tiene info? ([bold]s[/]/[bold]n[/]/[dim]ambos[/])", default="")

    # Formatear arreglos
    inc_exts = [e.strip() for e in inc_exts_input.split(',')] if inc_exts_input else None
    exc_exts = [e.strip() for e in exc_exts_input.split(',')] if exc_exts_input else None

    # Llamar al Search Engine maestro
    with SessionLocal() as db_session:
        results = search_registry(
            db_session=db_session,
            inc_name_path=inc_name,
            exc_name_path=exc_name,
            inc_tags=inc_tags,
            exc_tags=exc_tags,
            inc_extensions=inc_exts,
            exc_extensions=exc_exts,
            has_info=has_info
        )

    if not results:
        console.print("\n[bold yellow]No se encontraron resultados en el Súper Schema.[/]")
        Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")
        return

    # Bucle de interacción explícito para mostrar la tabla y navegar carpetas locales
    while True:
        console.clear()
        show_header()
        
        table = Table(title="[bold magenta]Resultados de la Búsqueda Nexus[/]", box=box.ROUNDED, show_lines=True)
        table.add_column("Nº", justify="right", style="cyan", no_wrap=True)
        table.add_column("Tipo", style="magenta")
        table.add_column("Título", style="bold")
        table.add_column("Ubicación/Info", style="dim")
        table.add_column("Modific.", style="italic green")

        for i, reg in enumerate(results, start=1):
            # Acortar rutas en pantalla de ser excesivamente largas
            info = reg.path_url
            if info and len(info) > 60:
                info = "..." + info[-57:]
            
            tipo = reg.type
            if reg.metadata_dict and 'extension' in reg.metadata_dict:
                tipo += f" ({reg.metadata_dict['extension']})"

            fecha = reg.modified_at.strftime("%y-%m-%d %H:%M") if reg.modified_at else ""

            table.add_row(str(i), tipo, reg.title, info, fecha)

        console.print(table)
        console.print(f"\n[dim]Mostrando {len(results)} resultados (Límite: 50).[/dim]")
        
        # Opciones de UX Interactivas
        console.print("\n[cyan]Atajos:[/] Escribe [bold]fN[/bold] para abrir la ubicación del archivo N (ej. [bold]f1[/bold]). [dim]Deja vacío para volver.[/dim]")
        
        cmd = Prompt.ask("Selección", default="")
        cmd = cmd.strip().lower()

        if not cmd or cmd == 'q' or cmd == '0':
            break
            
        elif cmd.startswith('f') and cmd[1:].isdigit():
            idx = int(cmd[1:]) - 1
            if 0 <= idx < len(results):
                reg = results[idx]
                if reg.type == 'file' and reg.path_url and not reg.path_url.startswith('nexus://'):
                    path_str = reg.path_url
                    if os.path.exists(path_str):
                        console.print(f"[bold green]Abriendo explorador local en:[/] {path_str}")
                        # Puente nativo bloqueante específico de Windows para marcar archivo
                        if sys.platform == "win32":
                            norm_path = os.path.normpath(path_str)
                            subprocess.Popen(f'explorer /select,"{norm_path}"')
                        time.sleep(1.5)
                    else:
                        console.print(f"[bold red]Ruta extraviada en disco físico:[/] {path_str}")
                        time.sleep(2)
                else:
                    console.print("[yellow]Esta función está reservada para ficheros físicos del PC (no web/pkm).[/]")
                    time.sleep(1.5)
            else:
                console.print("[red]ID numérico fuera de rango visual.[/]")
                time.sleep(1)

def menu_active_recall():
    """Puente hacia módulos de estudio y SRS"""
    console.clear()
    show_header()
    console.print(Panel("[bold red]Motor de Active Recall[/]\n¿Qué modo deseas iniciar?", box=box.ROUNDED))
    console.print("  [1] ⏳ Standard (Repasar todas las pendientes)")
    console.print("  [2] 🍅 Pomodoro (Bloque de 25 min - WIP)")
    console.print("  [0] 🔙 Volver")
    
    opcion = IntPrompt.ask("Selecciona una opción", choices=["0", "1", "2"], show_choices=False)
    
    if opcion == 1:
        due_cards = get_due_cards()
        if not due_cards:
            console.print("\n[green]¡Felicidades! No hay tarjetas listas para repasar hoy.[/green]")
            Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")
            return
            
        for idx, card in enumerate(due_cards, start=1):
            console.clear()
            show_header()
            console.print(f"[bold dim]Tarjeta {idx} de {len(due_cards)} | Tipo: {card.card_type}[/]")
            console.print(Panel(f"[bold cyan]Pregunta:[/] {card.question}", border_style="cyan"))
            
            # UX Loop Contextual Reveal
            while True:
                action = Prompt.ask("\n[dim]Presiona [bold]ENTER[/bold] para Respuesta | Escribe [bold]f[/bold] para abrir la fuente original[/dim]", default="")
                action = action.strip().lower()
                
                if action == "f":
                    reg = get_resource_record(card.parent_id)
                    if reg:
                        if reg.type == 'youtube' or reg.path_url.startswith('http'):
                            import webbrowser
                            console.print(f"[dim]Abriendo youtube o URL en navegador...[/dim]")
                            webbrowser.open(reg.path_url)
                        elif reg.type == 'file' and reg.path_url and not reg.path_url.startswith('nexus://'):
                            if sys.platform == "win32" and os.path.exists(reg.path_url):
                                console.print(f"[dim]Marcando el material en Windows Explorer...[/dim]")
                                norm_path = os.path.normpath(reg.path_url)
                                subprocess.Popen(f'explorer /select,"{norm_path}"')
                            else:
                                console.print("[yellow]Archivo inaccesible en disco.[/yellow]")
                        elif reg.type == 'note':
                            # Notas internas se escupen a la terminal directamente con estilo
                            console.print(Panel(f"[bold]Contenido Original Notas PKM:[/bold]\n\n{reg.content_raw}", border_style="grey50"))
                        else:
                            console.print(f"[yellow]Formato de fuente sin autoapertura instalada: '{reg.title}'[/yellow]")
                    else:
                        console.print("[red]Registro padre no localizado.[/red]")
                else:
                    break
                    
            console.print(Panel(f"[bold green]Respuesta Excluyente:[/]\n{card.answer}", border_style="green"))
            
            # UX Input Retención
            console.print("\n[bold]¿Qué tan difícil fue discriminar este concepto?[/bold]")
            rating = IntPrompt.ask("[1] Difícil (Mañana) | [2] Bien (3 días) | [3] Fácil (1 Semana)", choices=["1", "2", "3"])
            update_card_srs(card.id, rating)
            
        console.print("\n[bold green]🎉 Sesión de Discriminación Cognitiva Finalizada. ¡Buen trabajo![/bold green]")
        
    Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")

def menu_conectar():
    """Puente hacia IA o grafos manuales"""
    console.clear()
    show_header()
    console.print(Panel("[bold yellow]Menú de Conexiones Semánticas[/]\n[1] Vincular Manualmente\n[2] IA Match Forzado (Generar Tarjetas Excluyentes)", box=box.ROUNDED))
    
    opcion = IntPrompt.ask("Selecciona una opción", choices=["0", "1", "2"], show_choices=False)
    
    if opcion == 2:
        id_a = IntPrompt.ask("\n[bold]Ingresa el ID numérico del Registro A[/]")
        id_b = IntPrompt.ask("[bold]Ingresa el ID numérico del Registro B[/]")
        
        rec_a = get_resource_record(id_a)
        rec_b = get_resource_record(id_b)
        
        if not rec_a or not rec_b:
            console.print("\n[bold red]Error:[/] Uno de los IDs proporcionados no existe en el Core DB del Proyecto.")
            Prompt.ask("\n[dim]Presiona ENTER para volver...[/dim]", default="")
            return
            
        # Spinner visual para matar el aburrimiento al llamar a la API
        with console.status("[dim]Cerebro de IA procesando divergencias...[/dim]", spinner="dots"):
            cards = generate_relationship_cards(rec_a, rec_b)
            
        if cards:
            # Crear vinculo abstracto en grafos
            nx_db.create_link(NexusLinkCreate(source_id=id_a, target_id=id_b, relation_type="IA_Match", description="Match Forzado generado IA auto."))
            
            # Anclar sus tarjetas generadas de regreso
            for card in cards:
                nx_db.create_card(CardCreate(
                    parent_id=card.parent_id,
                    question=card.question,
                    answer=card.answer,
                    type=card.card_type
                ))
            console.print(f"\n[bold green]✅ ¡Relación forjada! Se extrajeron {len(cards)} variables de contraste en BD.[/bold green]")
        else:
            console.print("\n[bold red]❌ El Agente falló durante la discriminación o validación (Fijarse en API KEY).[/bold red]")
            
    elif opcion == 1:
        console.print("\n[blue]Vínculo Manual en desarrollo...[/blue]")
        
    Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")

def menu_estadisticas():
    """Puente hacia UI combinada de Data Analytics y Cognitive Analytics"""
    console.clear()
    show_header()
    console.print("\n[green]Calculando métricas globales de Nexus...[/] (Módulo en construcción)")
    Prompt.ask("\n[dim]Presiona ENTER para volver al menú principal...[/dim]", default="")

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
        
        # Menú Principal Interactivo
        menu_text = (
            "[bold]Opciones Principales:[/bold]\n\n"
            "  [1] ➕ [bold cyan]INGRESO[/]          (Escanear PC, Web, Notas)\n"
            "  [2] 🔍 [bold magenta]EXPLORADOR[/]       (Buscador Inclusivo/Exclusivo)\n"
            "  [3] 🧠 [bold red]ACTIVE RECALL[/]    (Repaso SRS, Pomodoro)\n"
            "  [4] 🔗 [bold yellow]CONECTAR[/]         (Correlación Manual/IA)\n"
            "  [5] 📊 [bold green]ESTADÍSTICAS GLOBALES[/]\n\n"
            "  [0] ❌ [bold grey53]Salir de Nexus[/]"
        )
        console.print(Panel(menu_text, title="Navegación", border_style="cyan", expand=False))
        console.print()

        opcion = Prompt.ask("Inicia un comando", choices=["0", "1", "2", "3", "4", "5"], show_choices=False)

        if opcion == "1":
            menu_ingreso()
        elif opcion == "2":
            menu_explorar()
        elif opcion == "3":
            menu_active_recall()
        elif opcion == "4":
            menu_conectar()
        elif opcion == "5":
            menu_estadisticas()
        elif opcion == "0":
            console.print("\n[bold cyan]Cerrando módulos de Nexus... ¡Hasta pronto![/]")
            time.sleep(1)
            sys.exit(0)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupción detectada. Saliendo de Nexus...[/]")
        sys.exit(0)
