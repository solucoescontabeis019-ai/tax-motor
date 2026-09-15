"""
Modelos de Auditoria e Logs
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ActionTypeEnum(str, enum.Enum):
    """Tipo de ação registrada"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SIMULATE = "SIMULATE"
    CALCULATE = "CALCULATE"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    VALIDATE = "VALIDATE"


class Alert(Base):
    """Tabela de Alertas do Sistema"""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)

    # Classificação
    nivel_severidade = Column(String(50), nullable=False)
    # CRITICA (🔴), ALTA (🟠), MEDIA (🟡), BAIXA (🔵)

    tipo_alerta = Column(String(100), nullable=False)
    # ex: CLIENTE_IMPACTADO, FORNECEDOR_SEM_REGIME, DOCUMENTO_INCOMPLETO, NOVA_LEGISLACAO, etc

    # Conteúdo
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    acao_recomendada = Column(Text, nullable=True)

    # Referências
    referencia_id = Column(UUID(as_uuid=True), nullable=True)
    referencia_tipo = Column(String(50), nullable=True)  # customer, supplier, document, etc

    # Status
    resolvido = Column(Boolean, default=False)
    data_resolucao = Column(DateTime, nullable=True)

    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Alert {self.nivel_severidade} - {self.tipo_alerta}>"


class AuditLog(Base):
    """Tabela de Auditoria - rastreamento de operações do sistema"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Usuário/Sessão
    usuario = Column(String(100), nullable=True)
    sessao_id = Column(String(100), nullable=True)

    # Ação
    tipo_acao = Column(Enum(ActionTypeEnum), nullable=False)
    entidade_tipo = Column(String(50), nullable=False)  # company, supplier, invoice, etc
    entidade_id = Column(UUID(as_uuid=True), nullable=True)

    # Conteúdo
    descricao = Column(Text, nullable=True)
    dados_anteriores = Column(JSON, nullable=True)  # Para updates
    dados_novos = Column(JSON, nullable=True)  # Para creates/updates

    # Status
    sucesso = Column(Boolean, default=True)
    erro_mensagem = Column(Text, nullable=True)

    # Timestamps
    data_acao = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.tipo_acao} - {self.entidade_tipo}>"
