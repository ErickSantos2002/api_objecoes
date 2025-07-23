from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, constr
from typing import List, Literal
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage

from app.models.database import SessionLocal
from app.models.tables import PromptIA, HistoricoIA
from app.core.config import get_settings

router = APIRouter(prefix="/chat", tags=["Chat IA"])

# ----------------------------
# MODELOS DE REQUISIÇÃO E RESPOSTA
# ----------------------------

class Mensagem(BaseModel):
    tipo: Literal["user", "ia"]
    conteudo: str = constr(strip_whitespace=True, min_length=1)

class ChatRequest(BaseModel):
    mensagem: str
    historico: List[Mensagem]
    usuario_id: str | None = None  # vem da authapi

class ChatResponse(BaseModel):
    resposta: str
    historico: List[Mensagem]

# ----------------------------
# DEPENDÊNCIA DE BANCO
# ----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# FUNÇÕES AUXILIARES
# ----------------------------

def construir_mensagens(prompt: str, historico: List[Mensagem]) -> List[BaseMessage]:
    mensagens: List[BaseMessage] = [SystemMessage(content=prompt)]
    for msg in historico:
        if msg.tipo == "user":
            mensagens.append(HumanMessage(content=msg.conteudo))
        else:
            mensagens.append(AIMessage(content=msg.conteudo))
    return mensagens

def buscar_prompt_ativo(db: Session) -> str:
    prompt = db.query(PromptIA).filter_by(ativo=True).first()
    if not prompt:
        raise HTTPException(status_code=500, detail="Nenhum prompt ativo encontrado.")
    return prompt.conteudo

# ----------------------------
# ENDPOINT PRINCIPAL
# ----------------------------

@router.post("/", response_model=ChatResponse)
async def responder_chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        settings = get_settings()

        # 1. Busca prompt do banco
        prompt = buscar_prompt_ativo(db)

        # 2. Constrói mensagens com histórico e prompt
        mensagens = construir_mensagens(prompt, req.historico)
        mensagens.append(HumanMessage(content=req.mensagem))

        # 3. Chama o modelo com a chave vinda do .env
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        resposta: AIMessage = llm.invoke(mensagens)

        # 4. Atualiza histórico local
        historico_atualizado = req.historico + [
            Mensagem(tipo="user", conteudo=req.mensagem),
            Mensagem(tipo="ia", conteudo=resposta.content),
        ]
        if len(historico_atualizado) > 60:
            historico_atualizado = historico_atualizado[-60:]

        # 5. Salva no banco, se for usuário autenticado
        if req.usuario_id:
            historico_model = HistoricoIA(
                usuario_id=req.usuario_id,
                mensagens=[m.model_dump() for m in historico_atualizado],
                ativo=True
            )
            db.add(historico_model)
            db.commit()

        return {"resposta": resposta.content, "historico": historico_atualizado}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no agente IA: {str(e)}")
