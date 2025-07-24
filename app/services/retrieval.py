# app/services/retrieval.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.database import SessionLocal
from app.services.embeddings import gerar_embedding

def buscar_contexto_relevante(pergunta: str, origem: str = "manual_phoebus", top_k: int = 5):
    db: Session = SessionLocal()
    embedding = gerar_embedding(pergunta)

    query = text("""
        SELECT titulo, conteudo
        FROM documentos_ia
        WHERE origem = :origem
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
    """)

    resultados = db.execute(query, {
        "origem": origem,
        "embedding": embedding,
        "top_k": top_k
    }).fetchall()

    db.close()
    return resultados
