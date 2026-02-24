import os

target_files = [
    "ui/dashboard.py",
    "modules/study_engine.py",
    "modules/web_scraper.py",
    "modules/pkm_manager.py",
    "modules/file_manager.py",
    "core/database.py",
    "agents/study_agent.py",
    "agents/relationship_agent.py"
]

for fpath in target_files:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        content = content.replace("[bold red on black]", "[bold white on red]")
        content = content.replace("[bold red]", "[bold white on red]")
        content = content.replace("[/bold red]", "[/]")
        content = content.replace("[red]", "[bold white on red]")
        content = content.replace("[/red]", "[/]")
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

print("Colores corregidos.")
