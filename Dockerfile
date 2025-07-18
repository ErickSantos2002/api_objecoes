# Etapa 1: Imagem base leve com Python
FROM python:3.11-slim

# Etapa 2: Define diretório de trabalho
WORKDIR /app

# Etapa 3: Copia os arquivos para o container
COPY . .

# Etapa 4: Instala dependências
RUN pip install --upgrade pip \
    && pip install "uvicorn[standard]" gunicorn \
    && pip install -r requirements.txt

# Etapa 5: Variáveis de ambiente (opcional)
ENV PORT=7070

# Etapa 6: Comando para rodar Gunicorn com UvicornWorker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:7070", "--workers", "2"]

