# app/models/tables.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, ARRAY, Boolean, JSON, text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.models.database import Base

class Simulacao(Base):
    __tablename__ = "simulacoes"

    id_simulacao = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(Integer, nullable=False)
    setor = Column(String, nullable=True)
    dificuldade = Column(String, nullable=True)
    data_inicio = Column(DateTime(timezone=True), server_default=text("NOW() - INTERVAL '3 hours'"), nullable=False)
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
    id_usuario = Column(Integer, nullable=False)
    posicao = Column(Integer, nullable=True)
    pontuacao_acumulada = Column(Integer, nullable=False, default=0)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, nullable=False)

class ObjeçãoRegistrada(Base):
    __tablename__ = "objeções_registradas"

    id_objecao = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(Integer, nullable=False)
    setor = Column(String, nullable=False)
    mensagem_ia = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)

class PromptIA(Base):
    __tablename__ = "prompt_ia"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, unique=True, nullable=False)
    conteudo = Column(Text, nullable=False)
    ativo = Column(Boolean, default=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)

class HistoricoIA(Base):
    __tablename__ = "historico_ia"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(String, nullable=False)
    mensagens = Column(JSON, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    ativo = Column(Boolean, default=True)