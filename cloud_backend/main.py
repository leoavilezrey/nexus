from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from cloud_backend.auth.router import router as auth_router
from cloud_backend.api.router import router as api_router

app = FastAPI(title="Nexus Cloud API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://nexus-tuusuario.railway.app", # Sustituir luego por URL final
        "http://127.0.0.1:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(api_router, prefix="/api")

# Montaremo los estáticos de UI al final para que no solapen los endpoints de API arriba de él
app.mount("/", StaticFiles(directory="cloud_backend/static", html=True))

@app.get("/health")
def health_check():
    return {"status": "Backend Operating System Online"}
