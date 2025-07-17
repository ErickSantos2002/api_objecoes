# app/api/endpoints/historico.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import tables, schemas
from app.models.database import SessionLocal
from app.core.deps import get_db

router = APIRouter(prefix="/historico", tags=["Histórico"])

# Registrar o histórico completo da simulação
@router.post("/", response_model=schemas.HistoricoSimulacaoOut)
def registrar_historico(data: schemas.CreateHistoricoSimulacao, db: Session = Depends(get_db)):
    novo_historico = tables.HistoricoSimulacao(
        id_simulacao=data.id_simulacao,
        mensagens_ia=data.mensagens_ia,
        respostas_usuario=data.respostas_usuario,
        pontuacoes=data.pontuacoes,
        feedbacks=data.feedbacks
    )
    db.add(novo_historico)
    db.commit()
    db.refresh(novo_historico)
    return novo_historico

# Obter histórico por simulação
@router.get("/{id_simulacao}", response_model=schemas.HistoricoSimulacaoOut)
def consultar_historico(id_simulacao: UUID, db: Session = Depends(get_db)):
    historico = (
        db.query(tables.HistoricoSimulacao)
        .filter(tables.HistoricoSimulacao.id_simulacao == id_simulacao)
        .first()
    )
    if not historico:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")
    return historico
