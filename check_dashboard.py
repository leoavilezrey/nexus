
import ast

with open(r'c:\Users\DELL\Proyectos\nexus\ui\dashboard.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'menu_ingreso':
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.ImportFrom):
                for alias in subnode.names:
                    if alias.name == 'Panel' or alias.asname == 'Panel':
                        print(f"Found Panel import in menu_ingreso at line {subnode.lineno}")
                    if alias.name == 'Text' or alias.asname == 'Text':
                        print(f"Found Text import in menu_ingreso at line {subnode.lineno}")
            if isinstance(subnode, ast.Assign):
                for target in subnode.targets:
                    if isinstance(target, ast.Name) and target.id == 'Panel':
                        print(f"Found Panel assignment in menu_ingreso at line {subnode.lineno}")
                    if isinstance(target, ast.Name) and target.id == 'Text':
                        print(f"Found Text assignment in menu_ingreso at line {subnode.lineno}")
