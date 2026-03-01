
import os
import sys

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if sys.platform == "win32":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

from modules.file_manager import ingest_local_file

def main():
    path = os.path.abspath("docs/analisis_frontend.md")
    tags = ["arquitectura", "frontend", "decisión", "documentación"]
    
    print(f"Indexando: {path}")
    reg = ingest_local_file(path, tags)
    
    if reg:
        print(f"✅ Documento indexado con ID: {reg.id}")
        print(f"Título: {reg.title}")
    else:
        print("❌ Error al indexar el documento.")

if __name__ == "__main__":
    main()
