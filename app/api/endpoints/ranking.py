# app/api/endpoints/ranking.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.models import tables, schemas
from app.core.deps import get_db

router = APIRouter(prefix="/ranking", tags=["Ranking"])

# Atualizar ou criar ranking de um usuário
@router.post("/atualizar")
def atualizar_ranking(id_usuario: UUID, nova_pontuacao: int, db: Session = Depends(get_db)):
    ranking = db.query(tables.Ranking).filter(tables.Ranking.id_usuario == id_usuario).first()

    if ranking:
        ranking.pontuacao_acumulada += nova_pontuacao
        ranking.data_atualizacao = datetime.utcnow()
    else:
        ranking = tables.Ranking(
            id_usuario=id_usuario,
            pontuacao_acumulada=nova_pontuacao,
            data_atualizacao=datetime.utcnow()
        )
        db.add(ranking)

    db.commit()

    # Atualiza posições no ranking
    rankings = db.query(tables.Ranking).order_by(tables.Ranking.pontuacao_acumulada.desc()).all()
    for posicao, item in enumerate(rankings, start=1):
        item.posicao = posicao
    db.commit()

    return {"msg": "Ranking atualizado com sucesso."}

# Obter o ranking completo
@router.get("/", response_model=list[schemas.RankingOut])
def obter_ranking(db: Session = Depends(get_db)):
    return db.query(tables.Ranking).order_by(tables.Ranking.posicao.asc()).all()
