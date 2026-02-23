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
