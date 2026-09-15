"""
Modelos de Documentos Fiscais e Notas
"""

from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class DocumentTypeEnum(str, enum.Enum):
    """Tipo de documento fiscal"""
    NF_E = "NF-E"
    NFC_E = "NFC-E"
    NFS_E = "NFS-E"
    CT_E = "CT-E"
    MDF_E = "MDF-E"
    PDF = "PDF"
    SIMPLES_PDF = "SIMPLES_PDF"
    PLANILHA = "PLANILHA"
    OUTRO = "OUTRO"


class DocumentDirectionEnum(str, enum.Enum):
    """Direção do documento"""
    ENTRADA = "ENTRADA"  # Compra
    SAIDA = "SAIDA"      # Venda
    DEVOLUCAO = "DEVOLUCAO"
    AJUSTE = "AJUSTE"


class OperationTypeEnum(str, enum.Enum):
    """Tipo de operação"""
    MERCADORIA = "MERCADORIA"
    SERVICO = "SERVICO"
    IMOBILIZADO = "IMOBILIZADO"
    DESPESA = "DESPESA"
    OUTRO = "OUTRO"


class Document(Base):
    """Tabela de Documentos (PDFs, XMLs, acompanhamentos)"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Identificação
    tipo_documento = Column(Enum(DocumentTypeEnum), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    hash_arquivo = Column(String(64), nullable=True, unique=True)

    # Conteúdo extraído
    conteudo_extraido = Column(Text, nullable=True)
    extracao_status = Column(String(50), nullable=True)  # SUCESSO, ERRO, PARCIAL
    extracao_metodo = Column(String(100), nullable=True)  # pdftotext, xml_parse, manual

    # Período/Competência
    competencia = Column(DateTime, nullable=True)
    data_emissao = Column(DateTime, nullable=True)
    data_referencia_inicio = Column(DateTime, nullable=True)
    data_referencia_fim = Column(DateTime, nullable=True)

    # Timestamps
    data_upload = Column(DateTime, default=datetime.utcnow)
    data_processamento = Column(DateTime, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # Metadados
    notas_extracao = Column(Text, nullable=True)
    divergencias_encontradas = Column(Boolean, default=False)
    divergencias_descricao = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Document {self.tipo_documento} - {self.nome_arquivo}>"


class Invoice(Base):
    """Tabela de Notas Fiscais/Documentos extraídos"""
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)

    # Identificação
    numero_nf = Column(String(50), nullable=True)
    chave_nf = Column(String(44), nullable=True, unique=True)
    serie = Column(String(5), nullable=True)

    # Direção e tipo
    direcao = Column(Enum(DocumentDirectionEnum), nullable=False)
    tipo_operacao = Column(Enum(OperationTypeEnum), nullable=False)

    # Emitente/Remetente
    cnpj_emitente = Column(String(14), nullable=False, index=True)
    nome_emitente = Column(String(255), nullable=True)

    # Destinatário/Tomador
    cnpj_destinatario = Column(String(14), nullable=False, index=True)
    nome_destinatario = Column(String(255), nullable=True)

    # Valores
    valor_total = Column(Numeric(15, 2), nullable=False)
    valor_base_icms = Column(Numeric(15, 2), default=0)
    valor_icms = Column(Numeric(15, 2), default=0)
    valor_base_ibs = Column(Numeric(15, 2), default=0)
    valor_ibs = Column(Numeric(15, 2), default=0)
    valor_base_cbs = Column(Numeric(15, 2), default=0)
    valor_cbs = Column(Numeric(15, 2), default=0)
    valor_iss = Column(Numeric(15, 2), default=0)
    valor_pis = Column(Numeric(15, 2), default=0)
    valor_cofins = Column(Numeric(15, 2), default=0)

    # Natureza da operação
    cfop = Column(String(5), nullable=True)
    ncm = Column(String(10), nullable=True)

    # Classificações
    cst = Column(String(3), nullable=True)  # PIS/COFINS
    csosn = Column(String(3), nullable=True)  # ICMS Simples

    # Timestamps
    data_emissao = Column(DateTime, nullable=False)
    data_competencia = Column(DateTime, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)

    # Validação
    validada = Column(Boolean, default=False)
    observacoes = Column(Text, nullable=True)
    duplicada = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Invoice {self.numero_nf} - {self.valor_total}>"


class InvoiceItem(Base):
    """Itens/Linhas de Notas Fiscais"""
    __tablename__ = "invoice_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)

    # Identificação do item
    numero_item = Column(Integer, nullable=False)
    descricao = Column(String(255), nullable=True)
    ncm = Column(String(10), nullable=True)
    cfop = Column(String(5), nullable=True)

    # Quantidade e valores
    quantidade = Column(Numeric(15, 4), nullable=True)
    valor_unitario = Column(Numeric(15, 4), nullable=True)
    valor_total = Column(Numeric(15, 2), nullable=False)

    # Tributos
    aliquota_icms = Column(Numeric(5, 2), nullable=True)
    valor_icms = Column(Numeric(15, 2), default=0)
    aliquota_iss = Column(Numeric(5, 2), nullable=True)
    valor_iss = Column(Numeric(15, 2), default=0)
    aliquota_pis = Column(Numeric(5, 2), nullable=True)
    valor_pis = Column(Numeric(15, 2), default=0)
    aliquota_cofins = Column(Numeric(5, 2), nullable=True)
    valor_cofins = Column(Numeric(15, 2), default=0)

    # Classificações
    cst = Column(String(3), nullable=True)
    csosn = Column(String(3), nullable=True)

    def __repr__(self):
        return f"<InvoiceItem {self.numero_item} - {self.valor_total}>"
