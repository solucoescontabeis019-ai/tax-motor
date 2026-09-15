"""
Modelos de Fornecedores e Clientes
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base
from app.models.company import TaxRegimeEnum


class RegimeValidationStatusEnum(str, enum.Enum):
    """Status da validação de regime"""
    VALIDADO = "VALIDADO"
    NAO_VALIDADO = "NAO_VALIDADO"
    EM_CONSULTA = "EM_CONSULTA"
    INCONSISTENTE = "INCONSISTENTE"


class Supplier(Base):
    """Tabela de Fornecedores"""
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    cnpj = Column(String(14), nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)

    # Regime tributário
    regime_tributario = Column(Enum(TaxRegimeEnum), nullable=False)
    regime_validacao_status = Column(Enum(RegimeValidationStatusEnum), default=RegimeValidationStatusEnum.NAO_VALIDADO)
    data_validacao_regime = Column(DateTime, nullable=True)
    fonte_validacao_regime = Column(String(100), nullable=True)  # API, Consulta manual, etc

    # Dados consolidados de compras
    total_comprado = Column(Numeric(15, 2), default=0, nullable=False)
    quantidade_notas = Column(String(20), default="0", nullable=False)  # JSON array count

    # Créditos potenciais (Simples Híbrido)
    credito_ibs_potencial = Column(Numeric(15, 2), default=0, nullable=False)
    credito_cbs_potencial = Column(Numeric(15, 2), default=0, nullable=False)

    # Créditos confirmados
    credito_ibs_confirmado = Column(Numeric(15, 2), default=0, nullable=False)
    credito_cbs_confirmado = Column(Numeric(15, 2), default=0, nullable=False)

    # Percentual do faturamento
    percentual_compras = Column(Numeric(5, 2), default=0, nullable=False)

    # Tipos de operação
    tem_mercadoria = Column(Boolean, default=False)
    tem_servico = Column(Boolean, default=False)
    tem_ativo_imobilizado = Column(Boolean, default=False)

    # UF e natureza
    uf = Column(String(2), nullable=True)
    natureza_principal = Column(String(100), nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_primeira_operacao = Column(DateTime, nullable=True)
    data_ultima_operacao = Column(DateTime, nullable=True)

    # Metadados
    observacoes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Supplier {self.cnpj} - {self.razao_social}>"


class Customer(Base):
    """Tabela de Clientes"""
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    cnpj = Column(String(14), nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)

    # Regime tributário
    regime_tributario = Column(Enum(TaxRegimeEnum), nullable=False)
    regime_validacao_status = Column(Enum(RegimeValidationStatusEnum), default=RegimeValidationStatusEnum.NAO_VALIDADO)
    data_validacao_regime = Column(DateTime, nullable=True)

    # Dados consolidados de vendas
    total_faturamento = Column(Numeric(15, 2), default=0, nullable=False)
    quantidade_notas = Column(String(20), default="0", nullable=False)
    percentual_faturamento = Column(Numeric(5, 2), default=0, nullable=False)
    ticket_medio = Column(Numeric(15, 2), nullable=True)

    # Tipos de operação
    tem_mercadoria = Column(Boolean, default=False)
    tem_servico = Column(Boolean, default=False)

    # Potencial de crédito (o quanto este cliente pode usar de IBS/CBS)
    credito_ibs_gerado_potencial = Column(Numeric(15, 2), default=0, nullable=False)
    credito_cbs_gerado_potencial = Column(Numeric(15, 2), default=0, nullable=False)

    # UF e natureza
    uf = Column(String(2), nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_primeira_operacao = Column(DateTime, nullable=True)
    data_ultima_operacao = Column(DateTime, nullable=True)

    # Metadados
    observacoes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Customer {self.cnpj} - {self.razao_social}>"
