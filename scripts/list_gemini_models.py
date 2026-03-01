
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Falta GOOGLE_API_KEY")
        return
    
    client = genai.Client(api_key=api_key)
    print("Modelos disponibles:")
    for model in client.models.list():
        print(f" - {model.name}")

if __name__ == "__main__":
    list_models()
