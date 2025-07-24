from openai import OpenAI
from app.core.config import get_settings
from app.models.database import SessionLocal
from pathlib import Path
from sqlalchemy import text
from app.services.embeddings import gerar_embedding
import fitz  # PyMuPDF
import textwrap

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Conecta ao banco
def insert_embedding_chunk(origem, titulo, texto):
    db = SessionLocal()
    try:
        vetor = gerar_embedding(texto)
        db.execute(
            text("""
                INSERT INTO documentos_ia (origem, titulo, conteudo, embedding)
                VALUES (:origem, :titulo, :conteudo, :embedding)
            """),
            {"origem": origem, "titulo": titulo, "conteudo": texto, "embedding": vetor}
        )
        db.commit()
    finally:
        db.close()

# Processa o PDF e insere
def processar_pdf_manual(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    origem = "manual_phoebus"
    for pagina in doc:
        texto = pagina.get_text()
        if not texto.strip():
            continue
        titulo = f"Phoebus - Página {pagina.number + 1}"
        # Divide a página em trechos de ~500 caracteres
        for i, trecho in enumerate(textwrap.wrap(texto, 500)):
            insert_embedding_chunk(origem, f"{titulo} - Parte {i+1}", trecho.strip())

    print("✅ Manual processado e inserido no banco com sucesso.")

if __name__ == "__main__":
    pdf_path = Path(__file__).parent / "Arquivos" / "Manual de Instruções_PHOEBUS.pdf"
    processar_pdf_manual(str(pdf_path))
