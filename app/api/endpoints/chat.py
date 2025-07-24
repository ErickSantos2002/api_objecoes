from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, constr
from typing import List, Literal
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage
from app.services.retrieval import buscar_contexto_relevante

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

def buscar_prompt_por_nome(db: Session, nome: str) -> str:
    prompt = db.query(PromptIA).filter(PromptIA.nome == nome).first()
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt '{nome}' não encontrado.")
    return prompt.conteudo

# ----------------------------
# ENDPOINT PRINCIPAL
# ----------------------------

@router.post("/", response_model=ChatResponse)
async def responder_chat(
    req: ChatRequest,
    prompt: str = Query(..., description="Nome do prompt a ser utilizado"),  # obrigatório
    db: Session = Depends(get_db)
):
    try:
        settings = get_settings()

        # 1. Busca prompt do banco
        prompt_text = buscar_prompt_por_nome(db, prompt)

        # 2. Constrói mensagens com histórico e prompt
        mensagens = construir_mensagens(prompt_text, req.historico)
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

@router.post("/historico", response_model=ChatResponse)
async def responder_com_historico_salvo(
    req: ChatRequest,
    prompt: str = Query(..., description="Nome do prompt a ser utilizado"),
    db: Session = Depends(get_db)
):
    try:
        settings = get_settings()

        # 1. Busca prompt do banco
        prompt_text = buscar_prompt_por_nome(db, prompt)

        # 2. Recupera histórico salvo para o usuário (últimos 60)
        if not req.usuario_id:
            raise HTTPException(status_code=400, detail="Usuário não autenticado.")

        historico_salvo = (
            db.query(HistoricoIA)
            .filter(HistoricoIA.usuario_id == req.usuario_id)
            .order_by(HistoricoIA.data_criacao.desc())
            .limit(1)
            .first()
        )

        mensagens_anteriores: List[Mensagem] = []
        if historico_salvo:
            mensagens_anteriores = [Mensagem(**m) for m in historico_salvo.mensagens][-60:]

        # 3. Adiciona nova mensagem do usuário
        mensagens = construir_mensagens(prompt_text, mensagens_anteriores)
        mensagens.append(HumanMessage(content=req.mensagem))

        # 4. Chama o LLM
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        resposta: AIMessage = llm.invoke(mensagens)

        # 5. Atualiza histórico
        historico_atualizado = mensagens_anteriores + [
            Mensagem(tipo="user", conteudo=req.mensagem),
            Mensagem(tipo="ia", conteudo=resposta.content),
        ]
        if len(historico_atualizado) > 60:
            historico_atualizado = historico_atualizado[-60:]

        # 6. Salva novo histórico no banco
        novo = HistoricoIA(
            usuario_id=req.usuario_id,
            mensagens=[m.model_dump() for m in historico_atualizado],
            ativo=True
        )
        db.add(novo)
        db.commit()

        return {"resposta": resposta.content, "historico": historico_atualizado}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no agente IA (com histórico): {str(e)}")

@router.get("/historico/{usuario_id}", response_model=List[Mensagem])
async def buscar_historico_usuario(
    usuario_id: str,
    db: Session = Depends(get_db)
):
    try:
        historico = (
            db.query(HistoricoIA)
            .filter(HistoricoIA.usuario_id == usuario_id)
            .order_by(HistoricoIA.data_criacao.desc())
            .limit(1)
            .first()
        )

        if not historico:
            return []

        mensagens = [Mensagem(**m) for m in historico.mensagens][-60:]
        return mensagens

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {str(e)}")

@router.post("/vetorizado", response_model=ChatResponse)
async def responder_com_rag(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        settings = get_settings()

        # 1. Buscar contexto vetorizado (por similaridade)
        contexto = buscar_contexto_relevante(req.mensagem, origem="manual_phoebus", top_k=5)
        trechos = "\n\n".join([f"{titulo}:\n{conteudo}" for titulo, conteudo in contexto])

        # 2. Montar prompt com contexto
        prompt_text = (
            f"Você é uma IA de suporte técnico. Responda com base nas informações abaixo, "
            f"referentes ao manual técnico do aparelho Phoebus:\n\n{trechos}"
        )

        mensagens = construir_mensagens(prompt_text, req.historico)
        mensagens.append(HumanMessage(content=req.mensagem))

        # 3. Chamar modelo
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.5,
            openai_api_key=settings.OPENAI_API_KEY
        )
        resposta: AIMessage = llm.invoke(mensagens)

        # 4. Atualiza histórico
        historico_atualizado = req.historico + [
            Mensagem(tipo="user", conteudo=req.mensagem),
            Mensagem(tipo="ia", conteudo=resposta.content),
        ]
        if len(historico_atualizado) > 60:
            historico_atualizado = historico_atualizado[-60:]

        # 5. Salvar no banco, se quiser
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
        raise HTTPException(status_code=500, detail=f"Erro na IA com vetorização: {str(e)}")