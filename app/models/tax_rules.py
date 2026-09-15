"""
Modelos de Regras Tributárias e Taxas
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class TaxTypeEnum(str, enum.Enum):
    """Tipo de tributo"""
    IRPJ = "IRPJ"
    CSLL = "CSLL"
    PIS = "PIS"
    COFINS = "COFINS"
    IPI = "IPI"
    ICMS = "ICMS"
    ISS = "ISS"
    INSS = "INSS"
    CPP = "CPP"
    IBS = "IBS"
    CBS = "CBS"
    OUTRA = "OUTRA"


class TaxRuleStatusEnum(str, enum.Enum):
    """Status da regra tributária"""
    OFICIAL = "OFICIAL"
    PROVISORIA = "PROVISORIA"
    ESTIMADA = "ESTIMADA"
    REVOGADA = "REVOGADA"
    TESTE = "TESTE"


class TaxSourceEnum(str, enum.Enum):
    """Fonte legal da regra"""
    CONSTITUICAO_FEDERAL = "CONSTITUICAO_FEDERAL"
    EC_132_2023 = "EC_132_2023"
    LC_214_2025 = "LC_214_2025"
    LC_227_2026 = "LC_227_2026"
    RESOLUCAO_CGSN = "RESOLUCAO_CGSN"
    RESOLUCAO_CGIBS = "RESOLUCAO_CGIBS"
    RECEITA_FEDERAL = "RECEITA_FEDERAL"
    MINISTÉRIO_FAZENDA = "MINISTÉRIO_FAZENDA"
    REGULAMENTACAO = "REGULAMENTACAO"
    OUTRO = "OUTRO"


class TaxRule(Base):
    """Tabela de Regras Tributárias - motor de legislação"""
    __tablename__ = "tax_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificação
    codigo_regra = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(500), nullable=False)

    # Classificação
    tipo_tributo = Column(Enum(TaxTypeEnum), nullable=False)
    regime_aplicavel = Column(String(100), nullable=False)  # SIMPLES_NACIONAL, LUCRO_REAL, etc

    # Legislação
    numero_lei = Column(String(50), nullable=True)
    numero_artigo = Column(String(20), nullable=True)
    paragrafo_inciso = Column(String(100), nullable=True)
    fonte_legal = Column(Enum(TaxSourceEnum), nullable=False)
    url_fonte = Column(String(500), nullable=True)

    # Vigência
    data_publicacao = Column(DateTime, nullable=True)
    data_vigencia_inicio = Column(DateTime, nullable=False)
    data_vigencia_fim = Column(DateTime, nullable=True)

    # Status
    status = Column(Enum(TaxRuleStatusEnum), nullable=False, default=TaxRuleStatusEnum.OFICIAL)
    versao = Column(Integer, default=1)

    # Conteúdo
    conteudo_regra = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TaxRule {self.codigo_regra} - {self.tipo_tributo}>"


class TaxRate(Base):
    """Tabela de Alíquotas Tributárias - parametrização"""
    __tablename__ = "tax_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificação
    codigo_aliquota = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=False)
    tipo_tributo = Column(Enum(TaxTypeEnum), nullable=False)

    # Regime e contexto
    regime_tributario = Column(String(100), nullable=False)
    anexo_simples = Column(String(20), nullable=True)  # ANEXO_I, ANEXO_II, etc
    faixa_rbt = Column(String(100), nullable=True)  # "1.800.000,01 - 3.600.000,00"

    # Valores de alíquota
    aliquota_nominal = Column(Numeric(5, 2), nullable=False)
    parcela_deducao = Column(Numeric(15, 2), nullable=True)  # Para Simples

    # Composição (para Simples)
    composicao_tributos = Column(JSON, nullable=True)  # ex: {"IRPJ": 4, "CSLL": 3.5, ...}

    # Vigência
    data_vigencia_inicio = Column(DateTime, nullable=False)
    data_vigencia_fim = Column(DateTime, nullable=True)

    # Status
    status = Column(Enum(TaxRuleStatusEnum), nullable=False, default=TaxRuleStatusEnum.OFICIAL)
    versao = Column(Integer, default=1)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TaxRate {self.codigo_aliquota} - {self.aliquota_nominal}%>"


class IBSCBSRateScenario(Base):
    """Cenários de Alíquotas IBS/CBS - para simulação"""
    __tablename__ = "ibs_cbs_rate_scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificação
    nome_cenario = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)

    # Alíquotas
    aliquota_ibs_estadual = Column(Numeric(5, 4), nullable=False)
    aliquota_ibs_municipal = Column(Numeric(5, 4), nullable=False)
    aliquota_cbs = Column(Numeric(5, 2), nullable=False)

    # Classificação
    tipo_cenario = Column(String(50), nullable=False)  # OFICIAL, ESTIMADA, OTIMISTA, CONSERVADORA

    # Vigência
    data_vigencia_inicio = Column(DateTime, nullable=False)
    data_vigencia_fim = Column(DateTime, nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<IBSCBSRateScenario {self.nome_cenario} - CBS {self.aliquota_cbs}%>"


class TaxSource(Base):
    """Tabela de Fontes de Dados - rastreabilidade"""
    __tablename__ = "tax_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificação
    nome = Column(String(100), nullable=False, unique=True)
    url = Column(String(500), nullable=True)
    tipo = Column(String(50), nullable=False)  # OFICIAL, MATERIAL_APOIO, SIMULACAO

    # Conteúdo
    descricao = Column(Text, nullable=True)

    # Timestamps
    data_acesso = Column(DateTime, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TaxSource {self.nome}>"
