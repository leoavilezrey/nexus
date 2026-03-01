import os
import sys
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

def test_connection():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] No se encontro GOOGLE_API_KEY en el archivo .env")
        return

    print(f"[OK] Key detectada (Longitud: {len(api_key)})")
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        print("[...] Probando llamada minima a Gemini 2.0 Flash...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Hola, responde solo con la palabra 'LISTO' si recibes esto."
        )
        
        if response.text and "LISTO" in response.text.upper():
            print("[EXITO] Conexion establecida y tokens disponibles.")
        else:
            print(f"[!] Respuesta inesperada: {response.text}")
            
    except Exception as e:
        if "429" in str(e):
            print("[ERROR] 429: Cuota agotada (Rate Limit exceeded).")
        elif "403" in str(e) or "401" in str(e):
            print("[ERROR] 403/401: API Key invalida o sin permisos.")
        else:
            print(f"[ERROR] Inesperado: {str(e)}")

if __name__ == "__main__":
    test_connection()
