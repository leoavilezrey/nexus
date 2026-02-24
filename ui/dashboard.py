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

# Tema personalizado para mejorar visibilidad en Windows PowerShell (errores en amarillo)
custom_theme = Theme({
    "prompt.choices": "bold cyan",
    "prompt.default": "bold white",
    "prompt.invalid": "bold yellow",  # Mensajes de error mucho más legibles
    "prompt.invalid.choice": "bold white on red",
})

console = Console(theme=custom_theme)

import os
import subprocess

from modules.file_manager import ingest_local_file
from modules.web_scraper import ingest_web_resource
from modules.pkm_manager import create_note
from core.search_engine import search_registry
from core.database import SessionLocal, nx_db, CardCreate, NexusLinkCreate
from agents.relationship_agent import generate_relationship_cards
from modules.study_engine import start_pomodoro_session, open_source_material
from modules.analytics import get_global_metrics

# ----------------------------------------------------------------------------
# 1. Componentes Visuales del Dashboard
# ----------------------------------------------------------------------------

def show_header():
    """Muestra el banner principal de Nexus."""
    # En Windows PowerShell, console.clear() a veces no blanquea bien el backbuffer
    os.system('cls' if os.name == 'nt' else 'clear')
    title = Text("N E X U S", style="bold cyan", justify="center")
    subtitle = Text("Cognitive Storage & active Recall Console", style="italic cyan", justify="center")
    
    header_content = Text.assemble(title, "\n", subtitle)
    console.print(Panel(header_content, box=box.DOUBLE, border_style="cyan", expand=False))
    console.print()

def get_stats_panel() -> Panel:
    """Retorna un Panel Rich con estadísticas reales consultadas desde la BD."""
    metrics = get_global_metrics()
    
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2))
    table.add_column("Categoría", style="bold")
    table.add_column("Datos")
    
    total_files = metrics["registry_counts"].get("file", 0)
    total_notes = metrics["registry_counts"].get("note", 0)
    total_videos = metrics["registry_counts"].get("youtube", 0)
    total_web = metrics["registry_counts"].get("web", 0)
    total_cards = metrics["srs"]["total_cards"]
    cards_today = metrics["srs"]["due_today"]
    sys_links = metrics["network"]["total_links"]
    tags = metrics["network"]["unique_tags"]

    table.add_row("🗃️ Registro Total:", f"{total_files} Archivos | {total_notes} Notas | {total_videos} Videos | {total_web} Web")
    table.add_row("🧠 Active Recall:", f"{total_cards} Tarjetas Totales | [bold white on red]{cards_today} Listas para Repaso Hoy[/]")
    table.add_row("🔗 Red de Cnx.:", f"{sys_links} Vínculos entre conceptos | {tags} Etiquetas Únicas")

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
    """
    while True:
        console.clear()
        show_header()
        console.print(Panel("[bold yellow]Menú de Ingesta Estricta[/]\nSelecciona el tipo de recurso a indexar:", box=box.ROUNDED))
        
        console.print("  [1] 📄 Añadir Archivo (Local)")
        console.print("  [2] 🌐 Añadir URL (Web/YouTube)")
        console.print("  [3] 📝 Escribir Nota Libre (Abre Editor Externo)")
        console.print("  [4] ⚙️ Añadir Aplicación / Herramienta")
        console.print("  [0] 🔙 Volver al Menú Principal\n")

        opcion = IntPrompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4"], show_choices=False)

        if opcion == 0:
            break

        if opcion == 1:
            while True:
                ruta = Prompt.ask("\n[bold]Ruta absoluta del archivo[/bold]")
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]")
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                resultado = ingest_local_file(ruta, tags_list)
                if resultado is not None:
                    console.print(f"\n[bold green]✅ Archivo indexado correctamente:[/] {resultado.title}")
                else:
                    console.print("\n[bold white on red]❌ No se pudo indexar. Verifica la ruta o los permisos.[/]")
                    
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRO archivo local | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == 2:
            while True:
                url = Prompt.ask("\n[bold]Pega la URL (YouTube o Genérica)[/bold]")
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]")
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                console.print("\n[cyan]Iniciando raspado contextual y transcripción...[/]")
                with console.status("[dim]Descargando Súper Schema de Web, por favor espera...[/dim]", spinner="dots"):
                     resultado = ingest_web_resource(url, tags_list)
                     
                if resultado is True:
                     console.print(f"\n[bold green]✅ Recurso Web indexado exitosamente en la Knowledge Base.[/bold green]")
                else:
                     console.print("\n[bold white on red]❌ Hubo un fallo en la ingesta o no se pudo generar el texto principal de la URL.[/]")
                     
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Indexar OTRA URL | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == 3:
            while True:
                titulo = Prompt.ask("\n[bold]Título de la Nueva Nota[/bold]")
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]")
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                
                console.print("\n[dim]Abriendo el sistema nativo. Al cerrar la ventana, tu nota se guardará automáticamente...[/dim]")
                
                resultado = create_note(titulo, tags_list)
                if resultado is not None:
                    console.print(f"\n[bold green]✅ Nota \"{resultado.title}\" almacenada en Knowledge Base.[/bold green]")
                else:
                    console.print("\n[yellow]⚠️ Nota cancelada. No se guardó nada.[/yellow]")
                    
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Escribir OTRA nota | [2] Volver al Menú de Ingesta | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == 4:
            while True:
                console.print("\n[bold yellow]Añadir Aplicación o Herramienta[/]")
                titulo = Prompt.ask("\n[bold]Nombre de la App / Plataforma[/bold]")
                ruta = Prompt.ask("[bold]Ruta / URL o Comando de Ejecución[/bold]")
                
                # Nuevos campos solicitados por Arquitecto:
                plataforma_input = Prompt.ask("[bold]Plataforma[/] (ej. PC, Android, Web)", default="PC")
                logueo = Prompt.ask("[bold]¿Requiere Credenciales / Logueo?[/] (s/n)", default="n").lower() == 's'
                logueo_str = "Sí" if logueo else "No"
                descripcion = Prompt.ask("[bold]Breve Descripción o Uso Principal[/] (opcional)")
                
                tags_input = Prompt.ask("[bold]Tags (separados por coma)[/bold]")
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


def menu_explorar():
    """Explorador Maestro con Paginación, Panel de Detalles y Repaso."""
    page = 0
    items_per_page = 13 # Paginación física ajustada a la ventana
    
    # Filtros actuales (en blanco significa "traer todo")
    filtros = {
        'inc_name': "", 'exc_name': "", 'inc_tags': "", 'exc_tags': "",
        'inc_exts': "", 'exc_exts': "", 'has_info': "", 'inc_ids': "", 'is_source': ""
    }

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
        title = f"[bold magenta]Explorador Maestro (Pág. {page + 1})[/] | [dim]Filtros Activos: {'Sí' if any(filtros.values()) else 'No'}[/]"
        table = Table(title=title, box=box.ROUNDED, show_lines=True)
        table.add_column("ID Único", justify="right", style="cyan", no_wrap=True)
        table.add_column("Tipo", style="magenta")
        table.add_column("Título", style="bold")
        table.add_column("Ubicación/Desc", style="dim")
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
            ubic_desc = f"{info}\n[dim white]{desc_extract}[/]"
            
            fecha = reg.modified_at.strftime("%y-%m-%d %H:%M") if reg.modified_at else "--/--/--"
            table.add_row(str(reg.id), tipo, reg.title or "N/A", ubic_desc, fecha)

        console.print(table)
        
        # Opciones de Navegación del Explorador
        console.print("\n[bold cyan]Controles del Explorador:[/]")
        console.print("  [bold]n[/] Siguiente Pág. | [bold]p[/] Pág. Anterior")
        console.print("  [bold]s[/] Buscar/Filtrar | [bold]l[/] Limpiar Búsqueda")
        console.print("  [bold]v[ID][/] Ver/Editar Detalles del Registro (ej: [bold]v5[/])")
        console.print("  [bold]del [IDs][/] Borrado en lote (ej: [bold]del 1,2,3-10[/])")
        console.print("  [bold]0[/] Volver al Menú Principal\n")
        
        cmd = Prompt.ask("Comando").strip().lower()
        
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
            console.print("\n[dim]Deja en blanco los campos que no quieras usar. Separa múltiples términos con comas.[/]")
            console.print("[dim]Recordatorio: Para limpiar todos los filtros aplicados usa 'l'. Para eliminar los registros resultantes usa 'del all'.[/dim]")
            console.print("[dim]Tip: Usa el tag especial '__web__' en extensiones para encontrar YouTube o Páginas Web.[/dim]")
            filtros['inc_ids'] = Prompt.ask("IDs a [bold green]INCLUIR[/] (ej. 1, 5, 10-15)", default=filtros['inc_ids'])
            filtros['inc_name'] = Prompt.ask("Nombre o Ruta a [bold green]INCLUIR[/]", default=filtros['inc_name'])
            filtros['exc_name'] = Prompt.ask("Nombre o Ruta a [bold white on red]EXCLUIR[/]", default=filtros['exc_name'])
            filtros['inc_tags'] = Prompt.ask("Etiquetas a [bold green]INCLUIR[/]", default=filtros['inc_tags'])
            filtros['exc_tags'] = Prompt.ask("Etiquetas a [bold white on red]EXCLUIR[/]", default=filtros['exc_tags'])
            filtros['inc_exts'] = Prompt.ask("Extensiones a [bold green]INCLUIR[/] (ej. pdf, md, __web__)", default=filtros['inc_exts'])
            filtros['exc_exts'] = Prompt.ask("Extensiones a [bold white on red]EXCLUIR[/]", default=filtros['exc_exts'])
            filtros['has_info'] = Prompt.ask("¿Tiene info? ([bold]s[/]/[bold]n[/]/[dim]ambos[/])", default=filtros['has_info'])
            filtros['is_source'] = Prompt.ask("¿Es Fuente de Flashcards? ([bold]s[/]/[bold]n[/]/[dim]ambos[/])", default=filtros['is_source'])
            page = 0
        elif cmd.startswith('v') and cmd[1:].isdigit():
            rec_id = int(cmd[1:])
            _show_record_detail(rec_id)
        elif cmd.startswith('del ') or cmd.startswith('borrar '):
            raw_ids = cmd.replace('del ', '').replace('borrar ', '').strip()
            ids_to_delete = []
            
            # 1. Si el usuario pide borrar TODO lo filtrado actualmente en memoria profunda
            if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                if not any(filtros.values()):
                    console.print("[bold white on red]¡Peligro! No tienes ningún filtro aplicado. Debes realizar una búsqueda ('s') antes de usar 'del all' para evitar borrar toda tu base de datos por accidente.[/]")
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
                console.print("[bold white on red]No se detectaron IDs válidos para borrar o la búsqueda arrojó cero resultados.[/]")
                time.sleep(1.5)
            else:
                console.print(f"\n[bold white on red] ⚠️ ADVERTENCIA DE BORRADO MASIVO: {len(ids_to_delete)} REGISTROS ⚠️ [/]")
                if raw_ids.lower() == 'all' or raw_ids.lower() == 'filtrados':
                    console.print("[yellow]Estás a punto de eliminar absolutamente todos los registros (incluso los de las páginas siguientes) que concuerdan con tus filtros actuales bajo esta búsqueda.[/yellow]")
                else:    
                    console.print(f"[bold white on red]Registros implicados:[/] [dim]{str(ids_to_delete[:15])}... (y más)[/dim]" if len(ids_to_delete) > 15 else f"[bold white on red]Registros implicados:[/] {ids_to_delete}")
                
                confirm = Prompt.ask("Escribe [bold white]eliminar lote[/] para confirmar, o presiona Enter para abortar").strip().lower()
                
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
                console.print(f"[bold white on red]❌ Registro con ID {rec_id} no encontrado en la Base de Datos.[/]")
                time.sleep(1.5)
                break
                
            tags_db = db_session.query(Tag).filter(Tag.registry_id == rec_id).all()
            tags_list = [t.value for t in tags_db]
            tags_str = ", ".join(tags_list) if tags_list else "Sin Etiquetas"
            
            panel_text = (
                f"[bold cyan]ID Único:[/] {reg.id}\n"
                f"[bold cyan]Tipo/Clasificación:[/] {reg.type.upper()}\n"
                f"[bold cyan]Es Fuente de Flashcard:[/] {'[green]Sí[/]' if reg.is_flashcard_source else '[yellow]No[/]'}\n"
                f"[bold cyan]Título:[/] {reg.title}\n"
                f"[bold cyan]Ruta/Enlace Físico:[/] {reg.path_url}\n"
                f"[bold cyan]Etiquetas Actuales:[/] [yellow]{tags_str}[/]\n\n"
                f"[bold green]Descripción / Contenido (Metadata de Repaso):[/]\n"
                f"{reg.content_raw}\n"
            )
            console.print(Panel(panel_text, title="🔍 Detalles y Gestión Visual", box=box.HEAVY, border_style="cyan"))
            
            # Sub-Menu Vista Detalle
            console.print("\n[bold]Panel de Herramientas del Registro:[/]")
            console.print("  [1] 📝 Editar Clasificaciones (Etiquetas y Descripción)")
            console.print("  [2] 🚀 Abrir Ubicación Física / Navegar a URL")
            console.print("  [3] 🧠 Entrar a Modo Repaso Interactivo (Foco)")
            console.print("  [4] 🗑️  Eliminar Registro Permanente")
            console.print("  [5] 🤖 Generar Tarjetas con IA (Flashcards)")
            console.print("  [6] 🗂️  Gestionar Tarjetas de Estudio")
            console.print("  [0] 🔙 Volver a la Tabla del Explorador\n")
            
            action = Prompt.ask("Selecciona una opción", choices=["0", "1", "2", "3", "4", "5", "6"], show_choices=False)
            
            if action == '0':
                break
            elif action == '1':
                console.print("\n[dim]Deja un campo vacío si no deseas modificarlo.[/]")
                
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
                    console.print(Panel(
                        f"{reg.content_raw}",
                        title=f"[bold yellow]Modo Enfoque Interactivo - {reg.title} (ID {reg.id})[/]",
                        border_style="yellow", padding=(1, 2)
                    ))
                    
                    enlaces_salientes = db_session.query(NexusLink).filter(NexusLink.source_id == rec_id).all()
                    enlaces_entrantes = db_session.query(NexusLink).filter(NexusLink.target_id == rec_id).all()
                    
                    if enlaces_salientes or enlaces_entrantes:
                        console.print("\n[bold magenta]Nodos Relacionados en la Red Neuronal (Brain Map):[/]")
                        for ln in enlaces_salientes:
                            tg = db_session.query(Registry).filter(Registry.id == ln.target_id).first()
                            if tg: console.print(f"  [cyan]v{tg.id}[/] ➔ {tg.title} [dim]({ln.relation_type})[/dim]")
                        for ln in enlaces_entrantes:
                            src = db_session.query(Registry).filter(Registry.id == ln.source_id).first()
                            if src: console.print(f"  [cyan]v{src.id}[/] ⬅ {src.title} [dim]({ln.relation_type})[/dim]")
                    else:
                        console.print("\n[dim]El registro no tiene ramificaciones en la red neuronal.[/dim]")
                        
                    console.print("\n[dim]Usa vID para saltar a un Nodo Relacionado, o Enter para volver al Menú de Edición.[/dim]")
                    cmd_foco = Prompt.ask("Comando").strip().lower()
                    
                    if not cmd_foco:
                        break  # Termina repaso y vuelve al panel de detalles
                    elif cmd_foco.startswith('v') and cmd_foco[1:].isdigit():
                        salto_id = int(cmd_foco[1:])
                        _show_record_detail(salto_id) # Recursively open nested detail
                        break
                    elif cmd_foco in ['borrar', 'eliminar']:
                        console.print("[yellow]Para eliminar este registro, presiona Enter para volver a la Vista Detalle y selecciona la Opción 4 (Eliminar).[/yellow]")
                        time.sleep(3)
                    else:
                        console.print("[bold white on red]Comando inválido. Usa 'vID' para saltar a un nodo o 'Enter' para salir del Foco.[/]")
                        time.sleep(2.5)
                        
            elif action == '4':
                console.print("\n[bold white on red] ⚠️ ADVERTENCIA DE DESTRUCCIÓN ⚠️ [/]")
                console.print("[bold white on red]Estás a punto de evaporar este registro. Se romperán todos sus vínculos en la red neuronal, etiquetas y Flashcards asociadas.[/]")
                confirm = Prompt.ask("Escribe [bold white]eliminar[/] para confirmar, o presiona Enter para abortar").strip().lower()
                
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
                    
            elif action == '5':
                from core.database import CardCreate
                from agents.study_agent import generate_deck_from_registry
                
                console.print("\n[bold magenta]🤖 Invocando al Agente de Estudio IA...[/]")
                with console.status("[dim]Leyendo metadata y destilando conceptos clave para el SRS...[/dim]", spinner="dots"):
                    cards = generate_deck_from_registry(reg)
                    
                if cards:
                    for card in cards:
                        nx_db.create_card(CardCreate(
                            parent_id=rec_id,
                            question=card.question,
                            answer=card.answer,
                            type=card.card_type
                        ))
                    console.print(f"\n[bold green]✅ ¡Éxito! El Agente extrajo {len(cards)} Flashcards de Alto Rendimiento para este Registro.[/bold green]")
                else:
                    console.print("\n[bold white on red]❌ El Agente no pudo generar tarjetas (Texto insuficiente, error de API de Google, o fallo de abstracción).[/]")
                    
                Prompt.ask("\n[bold]Presiona Enter para volver a la Vista Detalle...[/]")

            elif action == '6':
                from core.database import Card
                while True:
                    console.clear()
                    show_header()
                    console.print(f"[bold cyan]🗂️ Tarjetas de Estudio para:[/] {reg.title}\n")
                    
                    cards_db = db_session.query(Card).filter(Card.parent_id == rec_id).all()
                    
                    if not cards_db:
                        console.print("[yellow]No hay tarjetas asociadas a este registro. Usa la Opción 5 para generarlas con IA.[/yellow]")
                        time.sleep(2)
                        break
                        
                    for i, c in enumerate(cards_db):
                        console.print(f"[bold magenta]Tarjeta #{i+1} (ID: {c.id})[/]")
                        console.print(f"  [bold]Q:[/] {c.question}")
                        console.print(f"  [bold]A:[/] {c.answer}\n")
                    
                    console.print("[bold]Opciones de Gestión:[/]")
                    console.print("  [1] Editar contenido de Tarjeta")
                    console.print("  [2] Eliminar Tarjeta")
                    console.print("  [0] 🔙 Volver a Detalles del Registro")
                    
                    sub_action = Prompt.ask("\nComando", choices=["0", "1", "2"], show_choices=False)
                    
                    if sub_action == '0':
                        break
                    elif sub_action == '1':
                        card_id_str = Prompt.ask("[bold]Ingresa el ID de la Tarjeta a Editar (0 para cancelar)[/]")
                        if card_id_str.isdigit() and card_id_str != '0':
                            cid = int(card_id_str)
                            target_card = db_session.query(Card).filter(Card.id == cid, Card.parent_id == rec_id).first()
                            if target_card:
                                console.print("\n[dim]Presiona Enter dejando casi vacío para no modificar.[/dim]")
                                new_q = Prompt.ask(f"[bold]Nueva Pregunta (Q)[/]", default=target_card.question)
                                new_a = Prompt.ask(f"[bold]Nueva Respuesta (A)[/]", default=target_card.answer)
                                
                                if new_q.strip(): target_card.question = new_q.strip()
                                if new_a.strip(): target_card.answer = new_a.strip()
                                
                                db_session.commit()
                                console.print("\n[green]✅ Tarjeta Actualizada con Éxito.[/]")
                                time.sleep(1)
                            else:
                                console.print("\n[bold white on red]❌ ID de Tarjeta inválido para este registro.[/]")
                                time.sleep(1.5)
                    elif sub_action == '2':
                        card_id_str = Prompt.ask("[bold]Ingresa el ID de la Tarjeta a Eliminar (0 para cancelar)[/]")
                        if card_id_str.isdigit() and card_id_str != '0':
                            cid = int(card_id_str)
                            target_card = db_session.query(Card).filter(Card.id == cid, Card.parent_id == rec_id).first()
                            if target_card:
                                confirm = Prompt.ask(f"¿Estás seguro de eliminar permanentemente la Tarjeta {cid}? (s/n)").lower()
                                if confirm == 's':
                                    db_session.delete(target_card)
                                    db_session.commit()
                                    console.print("\n[green]✅ Tarjeta Eliminada.[/]")
                                    time.sleep(1.5)
                            else:
                                console.print("\n[bold white on red]❌ ID de Tarjeta inválido para este registro.[/]")
                                time.sleep(1.5)

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
                table.add_column("ID", style="cyan")
                table.add_column("Tipo", style="magenta")
                table.add_column("Título", style="bold")
                table.add_column("Tarjetas", justify="center")
                
                with SessionLocal() as db_session:
                    for reg in results:
                        count = db_session.query(func.count(Card.id)).filter(Card.parent_id == reg.id).scalar()
                        table.add_row(str(reg.id), reg.type.upper(), reg.title or "Sin Título", str(count))
                
                console.print(table)
                console.print(f"\n[dim]Página {page+1} | Total temas: {total_count}[/dim]")
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
                console.print(Panel(f"[bold cyan]🔥 Motor Pomodoro Listo:[/] Tienes [bold white on red]{c_total} tarjetas pendientes[/] distribuidas en {len(topics_today)} temas para hoy.", box=box.ROUNDED, border_style="cyan"))
            else:
                console.print(Panel("[green]🎉 Tu mente está al día. No tienes repasos pendientes en la cola del Pomodoro para hoy.[/]", box=box.ROUNDED, border_style="green"))

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
        
        table = Table(title=f"[bold magenta]Selector de Fuentes (Pág. {page + 1})[/] | [dim]Filtros Activos: {'Sí' if any(filtros.values()) else 'No'}[/]", box=box.ROUNDED, show_lines=True)
        table.add_column("ID Único", justify="right", style="cyan", no_wrap=True)
        table.add_column("Título", style="bold")
        table.add_column("Descripción")
        table.add_column("Tags", style="dim")
        table.add_column("Tarjetas (Pend/Tot)", justify="center")

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
                
                # Respetamos el formato original de la DB para título y descripción
                titulo = reg.title if reg.title else ""
                desc = reg.content_raw if reg.content_raw else ""
                
                table.add_row(
                    str(reg.id), 
                    titulo, 
                    desc,
                    tags_str,
                    f"[bold magenta]{pending_cards}[/]/[dim]{total_cards}[/]"
                )

        console.print(table)
        
        # --- 3. Controles del Menú Active Recall ---
        console.print("\n[bold cyan]Opciones de Construcción Lote (Flashcards):[/]")
        console.print("  [bold]ia [IDs][/]  🤖 Crear Flashcards con IA para los IDs dados (ej: [bold]ia 1,2,5-10[/] o [bold]ia all[/] para filtrados)")
        console.print("  [bold]man [ID][/] 📝 Crear Flashcards Manualmente para un ID (ej: [bold]man 5[/])")
        console.print("  [bold]j [ID][/]   🚀 Abrir material fuente (archivo/web/nota) para un ID")
        console.print("  [bold]e [ID][/]   📝 Editar Registro (Título, Descripción, Tags)")
        console.print("  [bold]del [IDs][/] 🗑️  Eliminar Registros de Raíz junto a Flashcards (ej: [bold]del 5[/] o [bold]del all[/])")
        console.print("\n[bold cyan]Opciones del Motor de Estudio:[/]")
        console.print("  [bold]pm[/]       🍅 Iniciar Pomodoro (Repasar todos los pendientes mezclados)")
        console.print("  [bold]pa[/]       ⏩ Adelantar (Menú de temas específicos, Azar y Cantidad)")
        console.print("\n[bold cyan]Filtros:[/]")
        console.print("  [bold]s[/] Filtrar/Buscar | [bold]l[/] Limpiar Filtros | [bold]n/p[/] Pág. Siguiente/Anterior | [bold]0[/] Salir\n")

        cmd = Prompt.ask("Comando").strip().lower()
        
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
            console.print("\n[dim]Deja en blanco los campos que no quieras usar. Separa múltiples términos con comas.[/dim]")
            console.print("[dim]Recordatorio: Usa 'l' para limpiar filtros. Usa 'del all' para borrar resultados filtrados de raíz.[/dim]")
            console.print("[dim]Tip: Usa el tag especial '__web__' en extensiones para encontrar YouTube o Páginas Web.[/dim]")
            filtros['inc_ids'] = Prompt.ask("IDs a [bold green]INCLUIR[/] (ej. 1, 5, 10-15)", default=filtros['inc_ids'])
            filtros['inc_name'] = Prompt.ask("Nombre o Ruta a [bold green]INCLUIR[/]", default=filtros['inc_name'])
            filtros['inc_tags'] = Prompt.ask("Etiquetas a [bold green]INCLUIR[/]", default=filtros['inc_tags'])
            filtros['inc_exts'] = Prompt.ask("Extensiones a [bold green]INCLUIR[/] (ej. pdf, md, __web__)", default=filtros['inc_exts'])
            filtros['exc_exts'] = Prompt.ask("Extensiones a [bold white on red]EXCLUIR[/]", default=filtros['exc_exts'])
            filtros['is_source'] = Prompt.ask("¿Es Fuente de Flashcards? ([bold]s[/]/[bold]n[/]/[dim]ambos[/])", default=filtros['is_source'])
            page = 0
            
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
                    console.print(f"\n[dim]Abriendo fuente para ID {rec_id}: {reg_obj.title}...[/dim]")
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
                    console.print("[dim]Escribe 'salir' en la Pregunta para terminar.[/dim]\n")
                    
                    types_list = ["Factual", "Conceptual", "Reversible", "MCQ", "TF", "Cloze", "Matching", "MAQ"]
                    # Forzamos que el prompt use nuestra consola con el tema de colores corregido
                    t_card_raw = Prompt.ask("[bold magenta]Tipo de Tarjeta[/]", choices=types_list, default="Factual", console=console).strip()
                    
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
                            key = Prompt.ask("[dim]Letra de opción (o Enter para finalizar)[/]")
                            if not key: break
                            val = Prompt.ask(f"Texto para opción {key}")
                            options[key] = val
                        
                        q_json = json.dumps({"prompt": prompt, "options": options})
                        a = Prompt.ask("[bold green]Letra(s) de la respuesta correcta[/] (ej. 'a' o 'a,b')")
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_json, answer=a, type=t_card))

                    elif t_card == "Cloze":
                        console.print("[dim]Usa la sintaxis: La capital de {{c1::Francia}} es {{c2::París}}[/dim]")
                        q = Prompt.ask("[bold cyan]Texto con Huecos[/]")
                        if q.lower() == 'salir': break
                        # Extraer respuestas automáticamente para el campo answer
                        import re
                        matches = re.findall(r"\{\{c\d+::(.*?)\}\}", q)
                        a = ", ".join(matches)
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q, answer=a, type="Cloze"))

                    elif t_card == "Matching":
                        import json
                        console.print("[dim]Ingresa pares de conceptos relacionados.[/dim]")
                        pairs = {}
                        while True:
                            left = Prompt.ask("[dim]Término Izquierda (o Enter para finalizar)[/]")
                            if not left: break
                            right = Prompt.ask(f"Término Derecha para '{left}'")
                            pairs[left] = right
                        
                        q_json = json.dumps({"pairs": pairs})
                        # La respuesta visual es simplemente el listado de pares correctos
                        a_text = "\n".join([f"{k} -> {v}" for k, v in pairs.items()])
                        nx_db.create_card(CardCreate(parent_id=rec_id, question=q_json, answer=a_text, type="Matching"))

                    else:
                        # Factual / Conceptual (Estándar)
                        q = Prompt.ask("[bold cyan]Pregunta (Q)[/]")
                        if q.lower() == 'salir' or not q.strip(): break
                        a = Prompt.ask("[bold green]Respuesta (A)[/]")
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
                        console.print(f"\n[dim]Procesando Registro ID {d_id}: '{reg_obj_ia.title}'[/dim]")
                        # Invocado a IA
                        cards_generated = generate_deck_from_registry(reg_obj_ia)
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
                    console.print(f"[bold white on red]Registros implicados:[/] [dim]{str(ids_to_delete[:15])}... (y más)[/dim]" if len(ids_to_delete) > 15 else f"[bold white on red]Registros implicados:[/] {ids_to_delete}")
                
                confirm = Prompt.ask("Escribe [bold white]eliminar lote[/] para confirmar, o presiona Enter para abortar").strip().lower()
                
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
    """Puente hacia IA o grafos manuales"""
    while True:
        console.clear()
        show_header()
        console.print(Panel("[bold yellow]Menú de Conexiones Semánticas[/]\n[1] Vincular Manualmente\n[2] IA Match Forzado (Generar Tarjetas Excluyentes)\n[0] 🔙 Volver", box=box.ROUNDED))
        
        opcion = IntPrompt.ask("Selecciona una opción", choices=["0", "1", "2"], show_choices=False)
        
        if opcion == 0:
            break
            
        if opcion == 2:
            while True:
                id_a = IntPrompt.ask("\n[bold]Ingresa el ID numérico del Registro A[/]")
                id_b = IntPrompt.ask("[bold]Ingresa el ID numérico del Registro B[/]")
                
                rec_a = nx_db.get_registry(id_a)
                rec_b = nx_db.get_registry(id_b)
                
                if not rec_a or not rec_b:
                    console.print("\n[bold white on red]Error:[/] Uno de los IDs proporcionados no existe en el Core DB del Proyecto.")
                else:
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
                        console.print("\n[bold white on red]❌ El Agente falló durante la discriminación o validación (Fijarse en API KEY).[/]")
                
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Generar OTRO IA Match | [2] Volver al Menú Conectar | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return
                
        elif opcion == 1:
            while True:
                id_a = IntPrompt.ask("\n[bold]Ingresa el ID del Registro Origen (A)[/]")
                id_b = IntPrompt.ask("[bold]Ingresa el ID del Registro Destino (B)[/]")
                relation_type = Prompt.ask("[bold]Tipo de Relación[/] (ej. complementa, comparar, expande)").strip()
                description = Prompt.ask("[bold]Breve nota sobre el vínculo[/] (opcional)").strip()
                
                reg_a = nx_db.get_registry(id_a)
                reg_b = nx_db.get_registry(id_b)
                
                if not reg_a or not reg_b:
                    console.print("\n[bold white on red]Error:[/] Uno o ambos IDs no existen en el Core DB del Proyecto.")
                else:
                    nx_db.create_link(NexusLinkCreate(
                        source_id=id_a, 
                        target_id=id_b, 
                        relation_type=relation_type, 
                        description=description
                    ))
                    console.print(f"\n[bold green]✅ Vínculo manual ({relation_type}) forjado correctamente en Nexus.[/bold green]")
                
                action = IntPrompt.ask("\n¿Qué deseas hacer ahora?\n[bold][1] Forjar OTRO Vínculo Manual | [2] Volver al Menú Conectar | [0] Menú Principal[/bold]", choices=["0", "1", "2"], show_choices=False)
                if action == 1:
                    continue
                elif action == 2:
                    break
                elif action == 0:
                    return

def menu_estadisticas():
    """Puente hacia UI combinada de Data Analytics y Cognitive Analytics"""
    console.clear()
    show_header()
    
    with console.status("[dim]Consultando Súper Schema y Red Neuronal...[/dim]", spinner="dots"):
        metrics = get_global_metrics()
        
    console.print()
    
    # Panel Izquierdo: Composición del Cerebro
    t_reg = Table(title="🗄️ Composición del Cerebro", box=box.ROUNDED, style="cyan")
    t_reg.add_column("Tipo", justify="left")
    t_reg.add_column("Cantidad", justify="right", style="bold")
    
    for r_type, count in metrics["registry_counts"].items():
        if r_type != "total":
            t_reg.add_row(r_type.capitalize(), str(count))
    t_reg.add_section()
    t_reg.add_row("[bold]TOTAL[/]", f"[bold]{metrics['registry_counts']['total']}[/]")
    
    # Panel Derecho: Red Neuronal
    t_net = Table(title="🔗 Red Neuronal", box=box.ROUNDED, style="magenta")
    t_net.add_column("Métrica", justify="left")
    t_net.add_column("Valor", justify="right", style="bold")
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
    t_srs.add_row("Diagnóstico", f"[black on cyan]{metrics['srs']['retention_desc']}[/]")
    
    # Renderizamos las tablas juntas usando columnas
    from rich.columns import Columns
    console.print(Align.center(Columns([Panel(t_reg, border_style="cyan"), Panel(t_net, border_style="magenta")])))
    console.print()
    console.print(Align.center(Panel(t_srs, border_style="green", expand=False)))
    
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
            "  [3] 🧠 [bold white on red]ACTIVE RECALL[/]    (Repaso SRS, Pomodoro)\n"
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
        console.print("\n[bold white on red]Interrupción detectada. Saliendo de Nexus...[/]")
        sys.exit(0)
