import sys
import time
import msvcrt

print("--- DIAGNÓSTICO INTERACTIVO (USUARIO) ---")
print("Este test registrará sus pulsaciones para diagnosticar fallos de teclado en Nexus.\n")

print("1. TEST DE FLECHAS DIRECCIONALES (Arrow Keys)")
print("Por favor, presiona las 4 flechas (Arriba, Abajo, Izquierda, Derecha).")
print("Luego presiona la tecla 'q' para terminar esta primera prueba.\n")

with open("diagnostics_user.log", "w", encoding="utf-8") as f:
    f.write("--- Log de Diagnóstico del Usuario ---\n")
    f.write("1. Prueba de teclado (msvcrt):\n")
    
    while True:
        char = msvcrt.getch()
        if char in [b'\x00', b'\xe0']:
            ext = msvcrt.getch()
            msg = f"  -> Detectado código especial: {char} + {ext}"
            print(msg)
            f.write(msg + "\n")
        else:
            msg = f"  -> Detectado carácter normal: {char}"
            print(msg)
            f.write(msg + "\n")
            if char.lower() == b'q':
                break

print("\n[✔] Prueba de teclado finalizada.")
print("\n2. EXPLICACIÓN DE FALLOS DETECTADOS PREVIAMENTE:")
print("- Tiempo de Carga: Nexus importa módulos de IA pesados al arrancar en el scope global.")
print("- Flechas rotas: El menú visual (Prompt.ask) ignora la intercepción de teclado nativo y espera la tecla Enter.")
print("- Opción 3 (Vista Detalle Rota): Falta procesar el comando ID en la consola, y la vista usa '.tiny_trunc' a 75 caracteres.")
print("- Navegación Flashcards: Los comandos 'Siguiente' y 'Menú Principal' no fueron programados en el bucle del motor.")
print("\nPor favor, adjunta el archivo 'diagnostics_user.log' generado en el directorio para evaluarlo.")
