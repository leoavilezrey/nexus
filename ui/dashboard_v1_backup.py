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
