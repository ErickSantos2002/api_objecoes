# app/api/endpoints/objeções.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.models import tables, schemas
from app.models.database import SessionLocal
from app.core.deps import get_db

router = APIRouter(prefix="/objeções", tags=["Objeções"])

# Registrar uma nova objeção usada
@router.post("/registrar", response_model=schemas.ObjecaoRegistradaOut)
def registrar_objecao(data: schemas.RegistrarObjecao, db: Session = Depends(get_db)):
    nova = tables.ObjeçãoRegistrada(
        id_usuario=data.id_usuario,
        setor=data.setor,
        mensagem_ia=data.mensagem_ia
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

# Buscar objeções anteriores por usuário e setor
@router.get("/registradas", response_model=List[schemas.ObjecaoRegistradaOut])
def listar_objecoes_registradas(
    id_usuario: UUID = Query(...),
    setor: str = Query(...),
    db: Session = Depends(get_db)
):
    resultados = (
        db.query(tables.ObjeçãoRegistrada)
        .filter(
            tables.ObjeçãoRegistrada.id_usuario == id_usuario,
            tables.ObjeçãoRegistrada.setor == setor
        )
        .order_by(tables.ObjeçãoRegistrada.data_criacao.desc())
        .all()
    )
    return resultados
