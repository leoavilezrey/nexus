
import ast

with open(r'c:\Users\DELL\Proyectos\nexus\ui\dashboard.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

class PanelFinder(ast.NodeVisitor):
    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == 'Panel' or alias.asname == 'Panel':
                print(f"ImportFrom: Panel at line {node.lineno}")
            if alias.name == 'Text' or alias.asname == 'Text':
                print(f"ImportFrom: Text at line {node.lineno}")
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'Panel':
                print(f"Assign: Panel at line {node.lineno}")
            if isinstance(target, ast.Name) and target.id == 'Text':
                print(f"Assign: Text at line {node.lineno}")

    def visit_FunctionDef(self, node):
        if node.name == 'Panel' or node.name == 'Text':
            print(f"FunctionDef: {node.name} at line {node.lineno}")
        self.generic_visit(node)

finder = PanelFinder()
finder.visit(tree)
