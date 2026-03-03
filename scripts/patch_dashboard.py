import os
import re

DASHBOARD_PATH = r"c:\Users\DELL\Proyectos\nexus\ui\dashboard.py"

NEW_FUNCTION = r"""def _show_record_detail(rec_id: int):
    \"\"\"Vista detallada de un Registro. P=volver lista, 0=menú principal.\"\"\"
    from core.database import Tag, Registry, NexusLink, CardCreate
    
    try:
      with SessionLocal() as db_session:
        while True:
            # Prevención Integral de Stale Objects (limpia cache para read-consistency)
            db_session.expire_all()
            
            console.clear()
            show_header()
            
            # Usar la sesión inyectada
            reg = nx_db.get_registry_in_session(db_session, rec_id)
            
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

            # Truncado solo para campos de una línea (rutas cortas, metadata de tabla superficial)
            def tiny_trunc(text, limit=75):
                if not text: return "[white]N/A[/white]"
                text = text.replace('\n', ' ').strip()
                return (text[:limit-3] + "...") if len(text) > limit else text

            panel_text = (
                f"[bold white]ID:[/] [bright_cyan]{reg.id}[/] | "
                f"[bold white]Tipo:[/] [yellow]{reg.type.upper()}[/] | "
                f"[bold white]Recall:[/] {'[green]SÍ[/]' if reg.is_flashcard_source else '[red]NO[/]'} │ "
                f"[bold white]Área/Tema:[/] [bright_blue]{tiny_trunc(tags_str.split(',')[0] if tags_str != 'Sin Etiquetas' else '', 30)}[/]\n"
                f"[bold white]Título:[/] [bright_white]{reg.title or 'N/A'}[/]\n"
                f"[bold white]Ruta/URL:[/] [white]{reg.path_url or 'N/A'}[/]\n"
                f"[bold white]Tags:[/] [yellow]{tags_str}[/]\n"
                f"{extra_meta}\n"
                f"[bold green]✨ Resumen (IA):[/]\n{reg.summary or '[white]Sin resumen generado.[/white]'}\n\n"
                f"[bold green]📝 Contenido/Transcripción:[/]\n{reg.content_raw or '[white]Sin contenido disponible.[/white]'}\n\n"
                f"[yellow]P = Lista anterior │ 0 = Menú principal │ 1 Editar │ 2 Abrir │ 3 Lectura │ 4 IA │ 5 Mazo │ 6 Borrar │ 7 Vínculo │ 8 Recall[/]"
            )
            # Rich maneja por defecto el wrap (ajuste de línea) permitiendo vista detallada ilimitada dentro del ancho de consola
            console.print(Panel(panel_text, title="🔍 Ficha Técnica Completa", box=box.HEAVY, border_style="bright_cyan", expand=False))
            
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
                try:
                    console.print("\n[white]Deja un campo vacío para no modificar ese campo.[/white]")
                    
                    n_source = Prompt.ask("[bold]¿Es fuente de Flashcards?[/] (s/n/Enter para omitir)", default="")
                    if n_source.strip().lower() in ['s', 'n']:
                        reg.is_flashcard_source = 1 if n_source.strip().lower() == 's' else 0

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
                        # Necesitamos setearlo así explícitamente y usar flag_modified si sqlalchemy no capta cambios en dict
                        from sqlalchemy.orm.attributes import flag_modified
                        reg.meta_info = meta_actual
                        flag_modified(reg, "meta_info")

                    n_desc = Prompt.ask("[bold]Nueva Descripción (content_raw)[/] (Enter para omitir)")
                    if n_desc.strip():
                        reg.content_raw = n_desc.strip()

                    n_summary = Prompt.ask("[bold]Nuevo Resumen[/] (Enter para omitir)")
                    if n_summary.strip():
                        reg.summary = n_summary.strip()

                    db_session.commit()
                    console.print("[green]Cambios guardados con éxito en la Base de Datos.[/]")
                    time.sleep(1.5)
                except Exception as e:
                    db_session.rollback()
                    db_session.expire_all()
                    console.print(f"[bold red]Error al guardar: {e}[/]")
                    time.sleep(2)
                
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
                # Modo Repaso Interactivo con Nodos y Salto (READ ONLY - SEGURA DENTRO DE SESION A)
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
                    try:
                        success = nx_db.delete_registry_in_session(db_session, rec_id)
                        db_session.commit()
                        if success:
                            console.print("\n[bold green]✅ Registro evaporado con éxito de la base de datos.[/]")
                        else:
                            console.print("\n[bold white on red]❌ Hubo un error al intentar borrar el registro físico de la base de datos.[/]")
                        time.sleep(1.5)
                        break  # ES VITAL ROMPER EL BUCLE, el registro ha muerto (evita DetachedInstanceError)
                    except Exception as e:
                        db_session.rollback()
                        db_session.expire_all()
                        console.print(f"\n[bold red]Error interno eliminando registro: {e}[/]")
                        time.sleep(2)
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
                        from agents.study_agent import generate_deck_from_registry, get_client
                        from rich.prompt import Confirm
                        
                        mockup_only = False
                        if get_client():
                            console.print(f"\n[bold yellow]⚠️  AVISO DE CONSUMO DE TOKENS[/bold yellow]")
                            if not Confirm.ask("[bold white]¿Confirmas envío a Gemini para flashcards?[/bold white]"):
                                console.print("[yellow]Modo seguro activado.[/yellow]")
                                mockup_only = True

                        console.print("\n[bold yellow]🤖 Destilando conceptos...[/]")
                        try:
                            with console.status("[dim]Procesando...[/dim]", spinner="dots"):
                                cards = generate_deck_from_registry(reg, mockup_only=mockup_only)
                            
                            if cards:
                                for card in cards:
                                    nx_db.create_card_in_session(db_session, CardCreate(parent_id=rec_id, question=card.question, answer=card.answer, type=card.card_type))
                                db_session.commit()
                                console.print(f"\n[bold green]✅ ¡Éxito! {len(cards)} tarjetas nuevas en el sistema.[/bold green]")
                                
                                post_ia = Prompt.ask("\n[bold][v][/] Ver/Editar tarjetas ahora | [bold][Enter][/] Volver", default="", console=console)
                                if post_ia.lower() == 'v':
                                    action = '5'
                                    break
                            else:
                                console.print("\n[bold red]❌ Falló la generación. La IA no devolvió matriz de conceptos.[/]")
                                time.sleep(2)
                        except Exception as e:
                            db_session.rollback()
                            db_session.expire_all()
                            console.print(f"\n[bold red]Error en transacción IA: {e}[/]")
                            time.sleep(2)
                            
                    elif sub_ia == '2':
                        from agents.summary_agent import generate_summary_from_registry
                        console.print("\n[bold yellow]🤖 Sintetizando ideas...[/]")
                        try:
                            with console.status("[dim]Analizando...[/dim]", spinner="dots"):
                                summary = generate_summary_from_registry(reg)
                            if summary:
                                nx_db.update_summary_in_session(db_session, rec_id, summary)
                                db_session.commit()
                                console.print(f"\n[bold green]✅ Resumen actualizado en Base de Datos.[/bold green]")
                                console.print(Panel(summary, title="Resumen IA", border_style="green"))
                                Prompt.ask("\n[bold]Enter para continuar...[/]")
                            else:
                                console.print("\n[bold red]❌ Falló la síntesis.[/]")
                                time.sleep(2)
                        except Exception as e:
                            db_session.rollback()
                            db_session.expire_all()
                            console.print(f"\n[bold red]Error actualizando resumen: {e}[/]")
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
                            try:
                                a = Prompt.ask("[bold green]Respuesta[/]")
                                t = Prompt.ask("[bold]Tipo[/]", choices=["Factual", "Conceptual", "Cloze"], default="Factual")
                                nx_db.create_card_in_session(db_session, CardCreate(parent_id=rec_id, question=q.strip(), answer=a.strip(), type=t))
                                db_session.commit()
                                console.print("\n[bold green]✅ Tarjeta vinculada y comiteada al mazo.[/bold green]")
                                time.sleep(1.5)
                            except Exception as e:
                                db_session.rollback()
                                db_session.expire_all()
                                console.print(f"[bold red]Error de BD añadiendo tarjeta: {e}[/]")
                                time.sleep(2)
                    
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
                                    try:
                                        db_session.delete(target)
                                        db_session.commit()
                                        console.print("[green]Borrado exitoso.[/]")
                                        time.sleep(1)
                                    except Exception as e:
                                        db_session.rollback()
                                        db_session.expire_all()
                                        console.print(f"[red]Fallo al borrar la tarjeta: {e}[/]")
                                        time.sleep(1.5)
                            elif cmd == '1':
                                cid_ed = IntPrompt.ask("ID de tarjeta a editar")
                                target = db_session.query(Card).filter(Card.id == cid_ed, Card.parent_id == rec_id).first()
                                if target:
                                    try:
                                        target.question = Prompt.ask("Q", default=target.question)
                                        target.answer = Prompt.ask("A", default=target.answer)
                                        db_session.commit()
                                        console.print("[green]Tarjeta Actualizada en Sesión.[/]")
                                        time.sleep(1)
                                    except Exception as e:
                                        db_session.rollback()
                                        db_session.expire_all()
                                        console.print(f"[red]Fallo en la actualización BD: {e}[/]")
                                        time.sleep(1.5)

            elif action == '7':
                # Agregar vínculo rápido desde el detalle
                console.print("\n[bold yellow]🔗 Agregar Vínculo[/]")
                try:
                    id_b_str = Prompt.ask("[bold]ID del registro a vincular con este (ID2)[/]", console=console)
                    id_b = int(id_b_str.strip())
                    rec_b = nx_db.get_registry_in_session(db_session, id_b)
                    if not rec_b:
                        console.print("[bold red]Registro destino no encontrado en la Base de Datos.[/]"); time.sleep(1.5)
                    else:
                        rel = Prompt.ask("[bold]Tipo de relación[/] (ej. complementa, refuta)", default="relacionado", console=console)
                        desc_v = Prompt.ask("[bold]Notas[/] (opcional)", default="", console=console)
                        nx_db.create_link_in_session(db_session, NexusLinkCreate(source_id=rec_id, target_id=id_b, relation_type=rel, description=desc_v))
                        db_session.commit()
                        console.print(f"[bold green]✅ Vínculo '{rel}' creado: ID {rec_id} ↔ ID {id_b}[/]")
                        time.sleep(1.5)
                except ValueError:
                    console.print("[bold red]Entrada de ID inválida.[/]"); time.sleep(1)
                except Exception as ve:
                    db_session.rollback()
                    db_session.expire_all()
                    console.print(f"[bold red]Error fatal gestionando relación: {ve}[/]"); time.sleep(1.5)

            elif action == '8':
                # Agregar a Active Recall (marcar como fuente)
                console.print("\n[bold bright_cyan]➕ Agregar a Active Recall[/]")
                opcion_recall = Prompt.ask(
                    "[1] Solo marcar como fuente  [2] Marcar + Generar Flashcards con IA  [0] Cancelar",
                    choices=["0", "1", "2"], show_choices=False, console=console
                )
                if opcion_recall == "1" or opcion_recall == "2":
                    try:
                        reg.is_flashcard_source = 1
                        db_session.commit()
                        console.print("[green]✅ Marcado como fuente de Recall en Base de Datos.[/]")
                        if opcion_recall == "2":
                            from agents.study_agent import generate_deck_from_registry, get_client
                            mockup_only = not bool(get_client())
                            console.print("[yellow]🤖 Generando flashcards...[/]")
                            with console.status("[dim]Procesando...[/dim]", spinner="dots"):
                                cards_gen = generate_deck_from_registry(reg, mockup_only=mockup_only)
                            if cards_gen:
                                for card_g in cards_gen:
                                    nx_db.create_card_in_session(db_session, CardCreate(parent_id=rec_id, question=card_g.question, answer=card_g.answer, type=card_g.card_type))
                                db_session.commit()
                                console.print(f"[bold green]✅ {len(cards_gen)} flashcards generadas y acopladas a la DB.[/]")
                            else:
                                console.print("[yellow]No se generaron flashcards.[/]")
                        time.sleep(1.5)
                    except Exception as e:
                        db_session.rollback()
                        db_session.expire_all()
                        console.print(f"[bold red]Error atómico conectando a SQLite: {e}[/]")
                        time.sleep(2)

    except ReturnToMain:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación interrumpida por el usuario (Ctrl + C). Liberamos memoria local.[/yellow]")
        raise
"""

with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"def _show_record_detail\(rec_id: int\):.*?def menu_adelantar_repaso\(\):"
new_content = re.sub(pattern, lambda _: NEW_FUNCTION + "\n\n\ndef menu_adelantar_repaso():", content, flags=re.DOTALL)

with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Patched {DASHBOARD_PATH} successfully with robust lambda string matching.")
