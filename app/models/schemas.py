# app/models/schemas.py

from typing import List, Literal, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# ----------------------------
# Simulação
# ----------------------------

class CreateSimulacao(BaseModel):
    id_usuario: int
    setor: Optional[str] = None
    dificuldade: Optional[str] = None

class SimulacaoOut(BaseModel):
    id_simulacao: UUID
    id_usuario: int
    data_inicio: datetime
    data_fim: Optional[datetime]
    pontuacao_total: Optional[int]
    setor: Optional[str] = None
    dificuldade: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
  
# ----------------------------
# Histórico da Simulação
# ----------------------------

class CreateHistoricoSimulacao(BaseModel):
    id_simulacao: UUID
    mensagens_ia: List[str]
    respostas_usuario: List[str]
    pontuacoes: List[int]
    feedbacks: List[str]

class HistoricoSimulacaoOut(CreateHistoricoSimulacao):
    id_historico: UUID

    model_config = {
        "from_attributes": True
    }
  
# ----------------------------
# Ranking
# ----------------------------

class RankingOut(BaseModel):
    id_ranking: UUID
    id_usuario: int
    posicao: Optional[int]
    pontuacao_acumulada: int
    data_atualizacao: datetime

    model_config = {
        "from_attributes": True
    }
  
# ----------------------------
# Objeções Registradas
# ----------------------------

class RegistrarObjecao(BaseModel):
    id_usuario: int
    setor: str
    mensagem_ia: str

class ObjecaoRegistradaOut(BaseModel):
    id_objecao: UUID
    id_usuario: int
    setor: str
    mensagem_ia: str
    data_criacao: datetime

    model_config = {
        "from_attributes": True
    }

# ----------------------------
# Prompt IA
# ----------------------------

class PromptIAOut(BaseModel):
    id: int
    nome: str
    conteudo: str
    ativo: bool
    data_criacao: datetime

    model_config = {
        "from_attributes": True
    }

# ----------------------------
# Histórico IA
# ----------------------------

class MensagemIA(BaseModel):
    tipo: Literal["user", "ia"]
    conteudo: str

class HistoricoIAOut(BaseModel):
    id: int
    usuario_id: str
    mensagens: List[MensagemIA]
    data_criacao: datetime
    ativo: bool

    model_config = {
        "from_attributes": True
    }