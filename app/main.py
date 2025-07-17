# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import simulacoes, historico, objeções

app = FastAPI(
    title="HealthScore API",
    version="1.0.0"
)

# CORS – ajuste conforme sua origem (ex: frontend local ou domínio futuro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção: especifique domínios seguros
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar os endpoints
app.include_router(simulacoes.router)
app.include_router(historico.router)
app.include_router(objeções.router)

# Rota básica para teste
@app.get("/")
def read_root():
    return {"msg": "HealthScore API rodando com sucesso 🚀"}
