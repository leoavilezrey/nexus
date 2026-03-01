#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Genera snapshot del codigo completo de Nexus."""
import os, datetime

NEXUS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY_FILES = []
SKIP = {'venv', 'logs', 'docs', '__pycache__', '.git', 'scripts', '.gemini', 'node_modules'}

for dirpath, dirnames, filenames in os.walk(NEXUS_ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP]
    for fn in sorted(filenames):
        if fn.endswith('.py'):
            PY_FILES.append(os.path.join(dirpath, fn))

out_path = os.path.join(NEXUS_ROOT, 'docs', f'codigo_completo_nexus_{datetime.date.today().isoformat()}.md')
with open(out_path, 'w', encoding='utf-8') as out:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    out.write(f'# Codigo Completo Nexus - {ts}\n\n')
    out.write(f'Total archivos: {len(PY_FILES)}\n\n')
    out.write('## Indice\n\n')
    for i, fp in enumerate(PY_FILES, 1):
        rel = os.path.relpath(fp, NEXUS_ROOT).replace(os.sep, '/')
        out.write(f'{i}. `{rel}`\n')
    out.write('\n---\n\n')
    for fp in PY_FILES:
        rel = os.path.relpath(fp, NEXUS_ROOT).replace(os.sep, '/')
        try:
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
            lines = len(code.splitlines())
            out.write(f'## {rel}\n')
            out.write(f'**Lineas: {lines}**\n\n')
            out.write(f'```python\n{code}\n```\n\n---\n\n')
        except Exception as e:
            out.write(f'## {rel}\nError: {e}\n\n---\n\n')

print(f'Generado: {out_path}')
print(f'Archivos: {len(PY_FILES)}')
