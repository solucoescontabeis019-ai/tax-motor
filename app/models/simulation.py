"""
Modelos de Simulações e Cenários
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ScenarioTypeEnum(str, enum.Enum):
    """Tipo de cenário"""
    REAL_2026 = "REAL_2026"
    SIMPLES_PURO_2027 = "SIMPLES_PURO_2027"
    SIMPLES_HIBRIDO_2027 = "SIMPLES_HIBRIDO_2027"
    LUCRO_REAL_2027 = "LUCRO_REAL_2027"


class ConfidenceLevelEnum(str, enum.Enum):
    """Nível de confiança da simulação"""
    ALTA = "ALTA"        # 90-100%
    MEDIA = "MEDIA"      # 70-89%
    BAIXA = "BAIXA"      # 50-69%
    INSUFICIENTE = "INSUFICIENTE"  # <50%


class Simulation(Base):
    """Tabela de Simulações Tributárias"""
    __tablename__ = "simulations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Identificação
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)

    # Cenário
    tipo_cenario = Column(Enum(ScenarioTypeEnum), nullable=False)

    # Parâmetros de entrada
    faturamento_simulado = Column(Numeric(15, 2), nullable=True)
    compras_simuladas = Column(Numeric(15, 2), nullable=True)
    percentual_b2b = Column(Numeric(5, 2), nullable=True)
    aliquota_cbs_estimada = Column(Numeric(5, 2), nullable=True)

    # Resultados calculados
    tributo_total_simulado = Column(Numeric(15, 2), nullable=True)
    credito_ibs_total = Column(Numeric(15, 2), default=0)
    credito_cbs_total = Column(Numeric(15, 2), default=0)
    debito_ibs_total = Column(Numeric(15, 2), default=0)
    debito_cbs_total = Column(Numeric(15, 2), default=0)

    # Análise comparativa
    carga_tributaria_efetiva = Column(Numeric(5, 2), nullable=True)
    diferenca_scenario_anterior = Column(Numeric(15, 2), nullable=True)
    percentual_diferenca = Column(Numeric(5, 2), nullable=True)

    # Confiança
    nivel_confianca = Column(Enum(ConfidenceLevelEnum), default=ConfidenceLevelEnum.INSUFICIENTE)
    percentual_confianca = Column(Numeric(5, 2), default=0)

    # Metadados
    observacoes = Column(Text, nullable=True)
    parametros_entrada = Column(JSON, nullable=True)  # Backup dos parâmetros usados

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_calculo = Column(DateTime, nullable=True)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Simulation {self.tipo_cenario} - {self.company_id}>"


class Credit(Base):
    """Tabela de Créditos de IBS/CBS identificados"""
    __tablename__ = "credits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)

    # Identificação
    tipo_credito = Column(String(50), nullable=False)  # IBS, CBS, ISS, etc

    # Valores
    base_calculo = Column(Numeric(15, 2), nullable=False)
    aliquota = Column(Numeric(5, 2), nullable=False)
    valor_credito = Column(Numeric(15, 2), nullable=False)

    # Classificação
    tipo_classificacao = Column(String(50), nullable=False)
    # CREDITO_INTEGRAL, CREDITO_PARCIAL, CREDITO_PRESUMIDO, CREDITO_CONDICIONADO, SEM_CREDITO, NAO_VALIDADO

    # Regime do fornecedor
    regime_fornecedor = Column(String(50), nullable=False)

    # Base legal
    artigo_lei = Column(String(100), nullable=True)
    legislacao = Column(String(100), nullable=True)
    observacoes = Column(Text, nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Credit {self.tipo_credito} - {self.valor_credito}>"


class Debit(Base):
    """Tabela de Débitos de IBS/CBS gerados"""
    __tablename__ = "debits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)

    # Identificação
    tipo_debito = Column(String(50), nullable=False)  # IBS, CBS, ISS, etc

    # Valores
    base_calculo = Column(Numeric(15, 2), nullable=False)
    aliquota = Column(Numeric(5, 2), nullable=False)
    valor_debito = Column(Numeric(15, 2), nullable=False)

    # Observações
    observacoes = Column(Text, nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Debit {self.tipo_debito} - {self.valor_debito}>"


class CommercialRisk(Base):
    """Tabela de Análise de Risco Comercial - impacto por concentração/regime"""
    __tablename__ = "commercial_risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)

    # Classificação
    nivel_risco = Column(String(50), nullable=False)  # BAIXO, MEDIO, ALTO, CRITICO

    # Dados
    percentual_faturamento = Column(Numeric(5, 2), nullable=False)
    regime_cliente = Column(String(50), nullable=False)
    potencial_credito_annual = Column(Numeric(15, 2), nullable=True)
    importancia_estrategica = Column(String(100), nullable=True)

    # Análise
    motivo_risco = Column(Text, nullable=True)
    impacto_estimado = Column(Numeric(15, 2), nullable=True)
    recomendacao = Column(Text, nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CommercialRisk {self.nivel_risco} - {self.percentual_faturamento}%>"


class CalculationMemory(Base):
    """Tabela de Rastreabilidade de Cálculos - auditoria e transparência"""
    __tablename__ = "calculation_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False)

    # Identificação do cálculo
    tipo_calculo = Column(String(100), nullable=False)
    # ex: DAS_SIMPLES_2026, CREDITO_IBS, DEBITO_CBS, ALIQUOTA_EFETIVA

    # Dados de entrada
    valor_base = Column(Numeric(15, 2), nullable=False)
    parametros = Column(JSON, nullable=True)

    # Fórmula/regra utilizada
    formula = Column(Text, nullable=True)
    regra_tributaria_id = Column(UUID(as_uuid=True), ForeignKey("tax_rules.id"), nullable=True)
    aliquota_id = Column(UUID(as_uuid=True), ForeignKey("tax_rates.id"), nullable=True)

    # Cálculo
    operacoes = Column(JSON, nullable=True)  # Passo a passo do cálculo
    valor_resultado = Column(Numeric(15, 2), nullable=False)

    # Referências
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    documento_referencia = Column(String(100), nullable=True)

    # Timestamps
    data_calculo = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CalculationMemory {self.tipo_calculo} = {self.valor_resultado}>"
