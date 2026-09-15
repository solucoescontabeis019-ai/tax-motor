"""
Modelos de dados para Empresas
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class TaxRegimeEnum(str, enum.Enum):
    """Regime tributário"""
    SIMPLES_NACIONAL = "SIMPLES_NACIONAL"
    LUCRO_PRESUMIDO = "LUCRO_PRESUMIDO"
    LUCRO_REAL = "LUCRO_REAL"
    MEI = "MEI"
    ISENTO = "ISENTO"
    INDEFINIDO = "INDEFINIDO"


class SimplesAnexoEnum(str, enum.Enum):
    """Anexos do Simples Nacional"""
    ANEXO_I = "ANEXO_I"
    ANEXO_II = "ANEXO_II"
    ANEXO_III = "ANEXO_III"
    ANEXO_IV = "ANEXO_IV"
    ANEXO_V = "ANEXO_V"
    ANEXO_VI = "ANEXO_VI"
    NAO_APLICAVEL = "NAO_APLICAVEL"


class Company(Base):
    """Tabela de Empresas analisadas"""
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cnpj = Column(String(14), unique=True, nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255), nullable=True)

    # Localização
    uf = Column(String(2), nullable=False)
    municipio = Column(String(100), nullable=False)

    # Atividade
    cnae_principal = Column(String(10), nullable=True)
    cnae_secundarias = Column(Text, nullable=True)  # JSON array

    # Regime tributário
    regime_tributario = Column(Enum(TaxRegimeEnum), nullable=False, default=TaxRegimeEnum.INDEFINIDO)
    simples_anexo = Column(Enum(SimplesAnexoEnum), nullable=True, default=SimplesAnexoEnum.NAO_APLICAVEL)

    # Dados financeiros (2026)
    rbt12 = Column(Numeric(15, 2), nullable=True, comment="Receita Bruta 12 meses - Simples")
    faturamento_mes_referencia = Column(Numeric(15, 2), nullable=True)
    faturamento_anual = Column(Numeric(15, 2), nullable=True)

    # Dados operacionais
    b2b_percentual = Column(Numeric(5, 2), nullable=True, default=0)
    b2c_percentual = Column(Numeric(5, 2), nullable=True, default=0)
    exportacao_percentual = Column(Numeric(5, 2), nullable=True, default=0)

    # Margem e despesas
    margem_operacional = Column(Numeric(5, 2), nullable=True)
    folha_mensal = Column(Numeric(15, 2), nullable=True)
    despesas_administrativas = Column(Numeric(15, 2), nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_referencia = Column(DateTime, nullable=True, comment="Data de referência dos dados")

    # Metadados
    ativa = Column(Boolean, default=True)
    observacoes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Company {self.cnpj} - {self.razao_social}>"
