# Motor de Decisão Tributária Brasileira

**Etapa 2: PostgreSQL Data Model + FastAPI Base**

## Visão Geral

Este projeto implementa um **motor profissional de decisão tributária** capaz de analisar empresas brasileiras e determinar o regime tributário mais vantajoso para 2027:

- ✓ Simples Nacional Puro
- ✓ Simples Híbrido (Simples + IBS/CBS Regular)
- ✓ Regime Regular (Lucro Real/Presumido)

**NÃO é uma simples calculadora de alíquota.**

É um **MOTOR DE LEGISLAÇÃO** + **MOTOR DE CRÉDITOS** + **MOTOR DE DECISÃO** + **ANÁLISE COMERCIAL**.

---

## Estrutura do Projeto

```
tax-motor/
├── app/
│   ├── core/                    # Configuração e banco de dados
│   │   ├── __init__.py
│   │   ├── config.py           # Settings Pydantic
│   │   └── database.py         # SQLAlchemy setup
│   ├── models/                  # Modelos SQLAlchemy (Etapa 2)
│   │   ├── __init__.py
│   │   ├── company.py          # Empresas
│   │   ├── supplier_customer.py # Fornecedores/Clientes
│   │   ├── document.py         # Documentos fiscais
│   │   ├── tax_rules.py        # Motor de legislação
│   │   ├── simulation.py       # Simulações e créditos/débitos
│   │   └── audit.py            # Auditoria e alertas
│   ├── schemas/                 # Schemas Pydantic (TODO)
│   │   └── __init__.py
│   ├── services/                # Lógica de negócio (TODO)
│   │   └── __init__.py
│   ├── api/                     # Endpoints FastAPI (TODO)
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py                  # Aplicação FastAPI
├── migrations/                  # Alembic migrations (TODO)
├── tests/                       # Testes automáticos (TODO)
├── logs/                        # Arquivos de log
├── .env                         # Variáveis de ambiente (criar)
├── requirements.txt             # Dependências
└── README.md                    # Este arquivo
```

---

## Modelo de Dados (Etapa 2)

### 1. **companies** - Empresas Analisadas
- `id` (UUID, PK)
- `cnpj` (String 14, UNIQUE, INDEX)
- `razao_social`, `nome_fantasia`
- `uf`, `municipio`
- `cnae_principal`, `cnae_secundarias`
- `regime_tributario` (ENUM: SIMPLES_NACIONAL, LUCRO_PRESUMIDO, LUCRO_REAL, MEI, ISENTO)
- `simples_anexo` (ENUM: ANEXO_I a VI)
- `rbt12` (RBT 12 meses - Simples)
- `faturamento_mes_referencia`, `faturamento_anual`
- `b2b_percentual`, `b2c_percentual`, `exportacao_percentual`
- `margem_operacional`, `folha_mensal`, `despesas_administrativas`
- `data_criacao`, `data_atualizacao`, `data_referencia`
- `ativa`, `observacoes`

### 2. **suppliers** - Fornecedores
- `id` (UUID, PK)
- `company_id` (FK → companies)
- `cnpj` (String 14, INDEX)
- `razao_social`
- `regime_tributario` (ENUM)
- `regime_validacao_status` (VALIDADO, NAO_VALIDADO, EM_CONSULTA, INCONSISTENTE)
- `data_validacao_regime`, `fonte_validacao_regime`
- `total_comprado`, `quantidade_notas`
- `credito_ibs_potencial`, `credito_cbs_potencial`
- `credito_ibs_confirmado`, `credito_cbs_confirmado`
- `percentual_compras`
- `tem_mercadoria`, `tem_servico`, `tem_ativo_imobilizado`
- `uf`, `natureza_principal`
- `data_criacao`, `data_atualizacao`
- `data_primeira_operacao`, `data_ultima_operacao`
- `observacoes`

### 3. **customers** - Clientes
- `id` (UUID, PK)
- `company_id` (FK → companies)
- `cnpj` (String 14, INDEX)
- `razao_social`
- `regime_tributario` (ENUM)
- `regime_validacao_status`
- `total_faturamento`, `quantidade_notas`, `percentual_faturamento`
- `ticket_medio`
- `tem_mercadoria`, `tem_servico`
- `credito_ibs_gerado_potencial`, `credito_cbs_gerado_potencial`
- `uf`
- `data_criacao`, `data_atualizacao`
- `data_primeira_operacao`, `data_ultima_operacao`
- `observacoes`

### 4. **documents** - Documentos (PDFs, XMLs, Acompanhamentos)
- `id` (UUID, PK)
- `company_id` (FK → companies)
- `tipo_documento` (ENUM: NF-E, NFC-E, NFS-E, CT-E, MDF-E, PDF, SIMPLES_PDF, PLANILHA)
- `nome_arquivo`, `hash_arquivo`
- `conteudo_extraido`, `extracao_status`, `extracao_metodo`
- `competencia`, `data_emissao`
- `data_referencia_inicio`, `data_referencia_fim`
- `data_upload`, `data_processamento`
- `observacoes`, `divergencias_encontradas`, `divergencias_descricao`

### 5. **invoices** - Notas Fiscais/Documentos Extraídos
- `id` (UUID, PK)
- `company_id` (FK → companies)
- `document_id` (FK → documents)
- `numero_nf`, `chave_nf`, `serie`
- `direcao` (ENTRADA, SAIDA, DEVOLUCAO, AJUSTE)
- `tipo_operacao` (MERCADORIA, SERVICO, IMOBILIZADO, DESPESA, OUTRO)
- `cnpj_emitente`, `nome_emitente`
- `cnpj_destinatario`, `nome_destinatario`
- `valor_total`
- `valor_base_icms`, `valor_icms`
- `valor_base_ibs`, `valor_ibs`
- `valor_base_cbs`, `valor_cbs`
- `valor_iss`, `valor_pis`, `valor_cofins`
- `cfop`, `ncm`, `cst`, `csosn`
- `data_emissao`, `data_competencia`
- `validada`, `observacoes`, `duplicada`

### 6. **invoice_items** - Itens das Notas
- `id` (UUID, PK)
- `invoice_id` (FK → invoices)
- `numero_item`, `descricao`
- `ncm`, `cfop`
- `quantidade`, `valor_unitario`, `valor_total`
- `aliquota_icms`, `valor_icms`
- `aliquota_iss`, `valor_iss`
- `aliquota_pis`, `valor_pis`
- `aliquota_cofins`, `valor_cofins`
- `cst`, `csosn`

### 7. **tax_rules** - Motor de Legislação
- `id` (UUID, PK)
- `codigo_regra` (String 50, UNIQUE)
- `descricao`
- `tipo_tributo` (ENUM: IRPJ, CSLL, PIS, COFINS, IPI, ICMS, ISS, INSS, CPP, IBS, CBS)
- `regime_aplicavel`
- `numero_lei`, `numero_artigo`, `paragrafo_inciso`
- `fonte_legal` (CONSTITUICAO, EC_132_2023, LC_214_2025, LC_227_2026, etc)
- `url_fonte`
- `data_publicacao`, `data_vigencia_inicio`, `data_vigencia_fim`
- `status` (OFICIAL, PROVISORIA, ESTIMADA, REVOGADA)
- `versao`
- `conteudo_regra`, `observacoes`
- `data_criacao`, `data_atualizacao`

### 8. **tax_rates** - Alíquotas Tributárias
- `id` (UUID, PK)
- `codigo_aliquota` (String 50, UNIQUE)
- `descricao`
- `tipo_tributo` (ENUM)
- `regime_tributario`, `anexo_simples`
- `faixa_rbt` (ex: "1.800.000,01 - 3.600.000,00")
- `aliquota_nominal`
- `parcela_deducao` (para Simples)
- `composicao_tributos` (JSON: {"IRPJ": 4, "CSLL": 3.5, ...})
- `data_vigencia_inicio`, `data_vigencia_fim`
- `status`, `versao`
- `data_criacao`, `data_atualizacao`

### 9. **ibs_cbs_rate_scenarios** - Cenários IBS/CBS
- `id` (UUID, PK)
- `nome_cenario`, `descricao`
- `aliquota_ibs_estadual`, `aliquota_ibs_municipal`
- `aliquota_cbs`
- `tipo_cenario` (OFICIAL, ESTIMADA, OTIMISTA, CONSERVADORA)
- `data_vigencia_inicio`, `data_vigencia_fim`

### 10. **tax_sources** - Fontes de Dados
- `id` (UUID, PK)
- `nome` (UNIQUE)
- `url`
- `tipo` (OFICIAL, MATERIAL_APOIO, SIMULACAO)
- `descricao`
- `data_acesso`, `data_criacao`

### 11. **simulations** - Simulações Tributárias
- `id` (UUID, PK)
- `company_id` (FK → companies)
- `nome`, `descricao`
- `tipo_cenario` (REAL_2026, SIMPLES_PURO_2027, SIMPLES_HIBRIDO_2027, LUCRO_REAL_2027)
- `faturamento_simulado`, `compras_simuladas`
- `percentual_b2b`, `aliquota_cbs_estimada`
- `tributo_total_simulado`
- `credito_ibs_total`, `credito_cbs_total`
- `debito_ibs_total`, `debito_cbs_total`
- `carga_tributaria_efetiva`, `diferenca_scenario_anterior`
- `percentual_diferenca`
- `nivel_confianca` (ALTA, MEDIA, BAIXA, INSUFICIENTE)
- `percentual_confianca`
- `observacoes`, `parametros_entrada` (JSON)
- `data_criacao`, `data_calculo`

### 12. **credits** - Créditos IBS/CBS
- `id` (UUID, PK)
- `simulation_id`, `invoice_id`, `supplier_id` (FKs)
- `tipo_credito` (IBS, CBS, ISS, etc)
- `base_calculo`, `aliquota`, `valor_credito`
- `tipo_classificacao` (INTEGRAL, PARCIAL, PRESUMIDO, CONDICIONADO, SEM_CREDITO, NAO_VALIDADO)
- `regime_fornecedor`
- `artigo_lei`, `legislacao`, `observacoes`
- `data_criacao`

### 13. **debits** - Débitos IBS/CBS
- `id` (UUID, PK)
- `simulation_id`, `invoice_id`, `customer_id` (FKs)
- `tipo_debito`
- `base_calculo`, `aliquota`, `valor_debito`
- `observacoes`
- `data_criacao`

### 14. **commercial_risks** - Análise de Risco Comercial
- `id` (UUID, PK)
- `company_id`, `simulation_id`, `customer_id` (FKs)
- `nivel_risco` (BAIXO, MEDIO, ALTO, CRITICO)
- `percentual_faturamento`
- `regime_cliente`
- `potencial_credito_annual`
- `importancia_estrategica`
- `motivo_risco`, `impacto_estimado`, `recomendacao`
- `data_criacao`, `data_atualizacao`

### 15. **calculation_memory** - Rastreabilidade de Cálculos
- `id` (UUID, PK)
- `simulation_id` (FK → simulations)
- `tipo_calculo` (DAS_SIMPLES_2026, CREDITO_IBS, DEBITO_CBS, ALIQUOTA_EFETIVA)
- `valor_base`
- `parametros` (JSON)
- `formula`, `regra_tributaria_id`, `aliquota_id`
- `operacoes` (JSON - passo a passo)
- `valor_resultado`
- `invoice_id`, `documento_referencia`
- `data_calculo`

### 16. **alerts** - Alertas do Sistema
- `id` (UUID, PK)
- `company_id` (FK)
- `nivel_severidade` (CRITICA 🔴, ALTA 🟠, MEDIA 🟡, BAIXA 🔵)
- `tipo_alerta` (CLIENTE_IMPACTADO, FORNECEDOR_SEM_REGIME, DOCUMENTO_INCOMPLETO, NOVA_LEGISLACAO)
- `titulo`, `descricao`, `acao_recomendada`
- `referencia_id`, `referencia_tipo`
- `resolvido`, `data_resolucao`
- `data_criacao`

### 17. **audit_logs** - Auditoria
- `id` (UUID, PK)
- `usuario`, `sessao_id`
- `tipo_acao` (CREATE, READ, UPDATE, DELETE, SIMULATE, CALCULATE, IMPORT, EXPORT)
- `entidade_tipo`, `entidade_id`
- `descricao`
- `dados_anteriores` (JSON)
- `dados_novos` (JSON)
- `sucesso`, `erro_mensagem`
- `data_acao`

---

## Setup e Instalação

### 1. Pré-requisitos
- Python 3.10+
- PostgreSQL 13+
- Git

### 2. Instalação
```bash
# Clonar repositório
git clone <repo>
cd tax-motor

# Criar virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar Banco de Dados
```bash
# Criar arquivo .env
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/tax_motor
API_V1_STR=/api/v1
PROJECT_NAME=Motor de Decisão Tributária
PROJECT_VERSION=0.2.0
LOG_LEVEL=INFO
CNPJ_API_ENABLED=true
CNPJ_API_TIMEOUT=5
EOF
```

### 4. Criar banco PostgreSQL
```bash
# No PostgreSQL
createdb tax_motor
```

### 5. Inicializar tabelas
```bash
# Python
python -c "from app.core.database import init_db; init_db()"
```

### 6. Executar aplicação
```bash
python app/main.py
```

A API estará disponível em: **http://localhost:8000**

---

## Documentação da API

### Endpoints (TODO - Etapas 3+)

#### Empresas
- `POST /api/v1/companies` - Criar empresa
- `GET /api/v1/companies/{company_id}` - Obter empresa
- `PUT /api/v1/companies/{company_id}` - Atualizar empresa
- `GET /api/v1/companies` - Listar empresas

#### Fornecedores
- `POST /api/v1/companies/{company_id}/suppliers` - Adicionar fornecedor
- `GET /api/v1/companies/{company_id}/suppliers` - Listar fornecedores
- `GET /api/v1/companies/{company_id}/suppliers/summary` - Matriz de fornecedores

#### Clientes
- `POST /api/v1/companies/{company_id}/customers` - Adicionar cliente
- `GET /api/v1/companies/{company_id}/customers` - Listar clientes
- `GET /api/v1/companies/{company_id}/customers/risk-analysis` - Análise de risco

#### Simulações
- `POST /api/v1/companies/{company_id}/simulations` - Criar simulação
- `GET /api/v1/companies/{company_id}/simulations/{sim_id}` - Obter resultados
- `POST /api/v1/companies/{company_id}/simulations/{sim_id}/compare` - Comparar cenários

#### Motor Tributário
- `GET /api/v1/tax/simples-2026` - Calcular Simples 2026
- `GET /api/v1/tax/simples-puro-2027` - Projetar Simples Puro 2027
- `GET /api/v1/tax/hibrido-2027` - Projetar Simples Híbrido 2027
- `GET /api/v1/tax/credits` - Calcular créditos

#### Documentos
- `POST /api/v1/companies/{company_id}/documents/upload` - Upload PDF/XML
- `GET /api/v1/companies/{company_id}/documents` - Listar documentos

#### Regras Tributárias
- `GET /api/v1/tax-rules` - Listar regras
- `POST /api/v1/tax-rules` - Criar regra
- `GET /api/v1/tax-rules/{rule_id}/versions` - Histórico de versões

---

## Etapas de Desenvolvimento

### ✓ Etapa 1: Mapear documentos
- Extrair dados de PDFs (PGDAS-D, Entradas, Saídas, Serviços)
- Validar motor Simples 2026
- Identificar fornecedores/clientes

### ✓ Etapa 2: PostgreSQL Data Model (ATUAL)
- Criar tabelas SQLAlchemy
- Configurar FastAPI
- Preparar estrutura de API

### Etapa 3: Schemas Pydantic
- Request/response schemas para cada entidade
- Validação de entrada

### Etapa 4: Services (Lógica de Negócio)
- Motor Simples Nacional
- Motor de créditos IBS/CBS
- Motor de débitos
- Análise comercial
- Cálculo memória

### Etapa 5: API Endpoints
- Routers FastAPI
- Autenticação (opcional)
- Logging e auditoria

### Etapa 6: Importação de Dados
- Parser de PDFs
- Parser de XMLs (NF-e, NFS-e, CT-e)
- Consolidação por CNPJ

### Etapa 7: Dashboard/Interface
- Baseado em Econet (modelo de referência)
- Visualização de cenários
- Análise interativa

### Etapa 8: Testes
- Testes unitários
- Testes de integração
- Validação com dados reais

---

## Validação com Dados Reais (WASHINGTON L LOPES)

Empresa testada:
- **CNPJ**: 04.286.335/0001-79
- **RBT12**: R$ 2.236.444,92
- **DAS Real 2026**: R$ 18.607,42
- **Motor Validado**: ✓ Diferença R$ 0,01 (arredondamento)

---

## Regras Críticas do Projeto

### ❌ NUNCA fazer:
1. Inventar dados
2. Inventar alíquota
3. Assumir que fornecedor Simples = X% de crédito
4. Assumir que toda despesa gera crédito
5. Recomendar sem dados suficientes

### ✓ SEMPRE fazer:
1. Marcar como "NÃO VALIDADO" quando faltam informações
2. Identificar claramente:
   - "REGRA LEGAL"
   - "DADO REAL DO DOCUMENTO"
   - "ESTIMATIVA"
3. Rastrear cálculo passo a passo
4. Citar legislação oficial
5. Priorizar fontes oficiais

---

## Contato e Documentação

**Desenvolvido por**: Priscila Videschi
**Email**: priscila.videschi@aplicativo.net
**Projeto**: Motor de Decisão Tributária Brasileira
**Versão Atual**: 0.2.0 (Etapa 2: PostgreSQL + FastAPI Base)

---

**Status**: 🟡 Em desenvolvimento - Etapa 2 concluída
**Próximo**: Etapa 3 - Schemas Pydantic + Services
