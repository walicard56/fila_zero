"""Configuração do banco de dados SQLAlchemy."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Em produção (Render), usa DATABASE_URL. Em local, usa SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./filazero.db")

# Render entrega URLs no formato postgres:// — SQLAlchemy 2.x exige postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency injection do FastAPI para sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
