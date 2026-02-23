# Blueprint: Integración de Ingesta en el Dashboard (UI)
Ubicación: `nexus/ui/dashboard.py` (Líneas del Menú de Ingreso)

Este blueprint detalla cómo conectar las opciones visuales del submenú de "INGRESAR" con los módulos lógicos (`file_manager` y `pkm_manager`) recién implementados.

## Módulo: `menu_ingresar()`
Cuando el usuario seleccione la opción `1` (INGRESAR) en el menú principal, se desplegará el siguiente flujo:

### 1. Opción "Añadir Archivo Local"
- Pedir al usuario: `Ruta absoluta del archivo:` (Usar `rich.prompt.Prompt` o similar).
- Pedir al usuario: `Tags (separados por coma):`.
- Limpiar y separar los tags en una lista de strings `['tag1', 'tag2']`.
- Llamar a la función: `file_manager.ingest_local_file(ruta, tags)`.
- Si retorna un registro exitoso, mostrar en verde: `[bold green]✅ Archivo indexado correctamente: {titulo}[/bold green]`.
- En caso de error (o ruta no encontrada), mostrar en rojo: `[bold red]❌ No se pudo indexar. Verifica la ruta.[/bold red]`.

### 2. Opción "Escribir Nota PKM"
- Pedir al usuario: `Título de la Nueva Nota:`.
- Pedir al usuario: `Tags (separados por coma):`.
- Dividir los tags.
- Mostrar mensaje: `[dim]Abriendo el sistema nativo. Al cerrar la ventana, tu nota se guardará automáticamente...[/dim]`
- Llamar a la función: `pkm_manager.create_note(titulo, tags)`.
- Mostrar animación de progreso de `rich` o texto temporal mientras la función bloqueante del Notepad está activa.
- Al retorno, si es un registro válido: `[bold green]✅ Nota "{titulo}" almacenada en Knowledge Base.[/bold green]`. Si no escribió nada: `[yellow]⚠️ Nota cancelada. No se guardó nada.[/yellow]`.

## Instrucción para el Constructor:
- Importar ambas funciones (`ingest_local_file` y `create_note`) en `dashboard.py`.
- Integrarlas al bloque bloque lógico de decisiones del menú de ingesta.
- Cuidar la visualización del usuario (que la terminal no escupa errores de importación crudos sino paneles atractivos).
- (Punto Extra): De la validación base, invitar al usuario a volver al Dashboard general oprimiendo ENTER.
