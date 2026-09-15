"""
Configuração do banco de dados PostgreSQL - SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Criar engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Mudar para True para debug SQL
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Criar session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base para os modelos
Base = declarative_base()


def get_db():
    """Dependência para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar banco de dados - criar todas as tabelas"""
    Base.metadata.create_all(bind=engine)
