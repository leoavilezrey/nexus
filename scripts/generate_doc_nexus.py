import os

# Archivos solicitados por el usuario para su revisión
files_to_include = [
    r"c:\Users\DELL\Proyectos\nexus\main.py",
    r"c:\Users\DELL\Proyectos\nexus\ui\dashboard.py",
    r"c:\Users\DELL\Proyectos\nexus\modules\study_engine.py"
]

out_path = r"c:\Users\DELL\Proyectos\nexus\docs\codigo_completo_nexus_2026-02-28_v3.md"

def generate_markdown():
    print(f"Generando documento consolidado en {out_path}...")
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write("# Código Fuente de Nexus para Análisis Pre-Implementación\n\n")
        out_f.write("Este documento contiene el código actualizado de los archivos centrales que serán modificados en el Plan de Implementación.\n\n")
        
        for fp in files_to_include:
            if os.path.exists(fp):
                out_f.write(f"## Archivo: `{os.path.basename(fp)}`\n")
                out_f.write(f"**Ruta:** `{fp}`\n")
                out_f.write("```python\n")
                try:
                    with open(fp, "r", encoding="utf-8") as in_f:
                        out_f.write(in_f.read())
                except Exception as e:
                    out_f.write(f"# Error leyendo el archivo: {e}\n")
                out_f.write("\n```\n\n")
            else:
                out_f.write(f"## Archivo: `{os.path.basename(fp)}` (NO ENCONTRADO)\n\n")
                
    print(f"Documento generado exitosamente. Tamaño: {os.path.getsize(out_path)} bytes.")

if __name__ == "__main__":
    generate_markdown()
