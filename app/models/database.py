# app/models/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

# Pega a URI do banco a partir do config.py
settings = get_settings()
DATABASE_URL = settings.sqlalchemy_uri

# Criação do engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Criação da session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base usada para os models (tabelas)
Base = declarative_base()
