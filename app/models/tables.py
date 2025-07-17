# app/models/tables.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.models.database import Base

class Simulacao(Base):
    __tablename__ = "simulacoes"

    id_simulacao = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), nullable=False)  # referência lógica
    data_inicio = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_fim = Column(DateTime, nullable=True)
    pontuacao_total = Column(Integer, nullable=True)

class HistoricoSimulacao(Base):
    __tablename__ = "historico_simulacao"

    id_historico = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_simulacao = Column(UUID(as_uuid=True), ForeignKey("simulacoes.id_simulacao"), nullable=False)
    mensagens_ia = Column(ARRAY(Text), nullable=False)
    respostas_usuario = Column(ARRAY(Text), nullable=False)
    pontuacoes = Column(ARRAY(Integer), nullable=False)
    feedbacks = Column(ARRAY(Text), nullable=False)

class Ranking(Base):
    __tablename__ = "ranking"

    id_ranking = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), nullable=False)
    posicao = Column(Integer, nullable=True)
    pontuacao_acumulada = Column(Integer, nullable=False, default=0)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, nullable=False)

class ObjeçãoRegistrada(Base):
    __tablename__ = "objeções_registradas"

    id_objecao = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), nullable=False)
    setor = Column(String, nullable=False)
    mensagem_ia = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
