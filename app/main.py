# app/main.py

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import simulacoes, historico, objeções, ranking
from app.core.deps import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import SecuritySchemeType
from app.core.auth import get_current_user, TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://authapi.healthsafetytech.com/login")

app = FastAPI(
    title="HealthScore API",
    version="1.0.0",
    openapi_tags=[{"name": "Simulações"}, {"name": "Ranking"}],
    dependencies=[Depends(oauth2_scheme)]  # ← todas as rotas exigirão token
)

# CORS – ajuste conforme sua origem (ex: frontend local ou domínio futuro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://datacorehs.healthsafetytech.com",
        "https://tinyapi.healthsafetytech.com/",
        "https://healthsafetytech.com",
        "https://scoreapi.healthsafetytech.com",
        "https://healthscore.healthsafetytech.com",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar os endpoints
app.include_router(simulacoes.router)
app.include_router(historico.router)
app.include_router(objeções.router)
app.include_router(ranking.router)

# Rota básica para teste
@app.get("/me", tags=["Autenticação"])
def read_me(user: TokenData = Depends(get_current_user)):
    return {"user_id": user.user_id}
