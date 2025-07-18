# app/api/endpoints/simulacoes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.models import tables, schemas
from app.models.database import SessionLocal
from app.core.deps import get_db
from app.core.auth import get_current_user, TokenData  # ← Importa a autenticação

router = APIRouter(prefix="/simulacoes", tags=["Simulações"])

# Criar uma nova simulação (protegida por token)
@router.post("/", response_model=schemas.SimulacaoOut)
def criar_simulacao(
    simulacao: schemas.CreateSimulacao,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user)  # ← Aqui exige o token
):
    if str(simulacao.id_usuario) != str(user.user_id):
        raise HTTPException(status_code=403, detail="Usuário não autorizado para essa simulação")
    nova = tables.Simulacao(
        id_usuario=simulacao.id_usuario
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

# Listar simulações (proteção opcional)
@router.get("/", response_model=list[schemas.SimulacaoOut])
def listar_simulacoes(
    id_usuario: UUID = None,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user)
):
    query = db.query(tables.Simulacao)
    if id_usuario:
        if str(id_usuario) != str(user.user_id):
            raise HTTPException(status_code=403, detail="Acesso negado ao histórico de outro usuário.")
        query = query.filter(tables.Simulacao.id_usuario == id_usuario)
    return query.all()

# Finalizar uma simulação (proteção básica)
@router.post("/{id_simulacao}/finalizar", response_model=schemas.SimulacaoOut)
def finalizar_simulacao(
    id_simulacao: UUID,
    pontuacao_total: int,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user)
):
    sim = db.query(tables.Simulacao).filter(tables.Simulacao.id_simulacao == id_simulacao).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulação não encontrada")
    if str(sim.id_usuario) != str(user.user_id):
        raise HTTPException(status_code=403, detail="Você não pode finalizar simulações de outro usuário")
    sim.data_fim = datetime.utcnow()
    sim.pontuacao_total = pontuacao_total
    db.commit()
    db.refresh(sim)
    return sim
