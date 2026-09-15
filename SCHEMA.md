# Esquema de Banco de Dados - Motor de Decisão Tributária

## Diagrama Entidade-Relacionamento (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MOTOR DE DECISÃO TRIBUTÁRIA                         │
│                      PostgreSQL Data Model (Etapa 2)                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │    companies    │
                              │   (EMPRESA)     │
                              ├─────────────────┤
                              │ id (UUID, PK)   │
                              │ cnpj (UNIQUE)   │
                              │ razao_social    │
                              │ regime_tributario
                              │ rbt12           │
                              │ faturamento_*   │
                              └────────┬────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
                ▼                      ▼                      ▼
        ┌────────────────┐    ┌─────────────────┐   ┌──────────────────┐
        │    suppliers   │    │   customers     │   │    documents     │
        │ (FORNECEDORES) │    │   (CLIENTES)    │   │  (PDFS, XMLs)    │
        ├────────────────┤    ├─────────────────┤   ├──────────────────┤
        │ id (UUID, PK)  │    │ id (UUID, PK)   │   │ id (UUID, PK)    │
        │ cnpj (INDEX)   │    │ cnpj (INDEX)    │   │ tipo_documento   │
        │ regime         │    │ regime          │   │ nome_arquivo     │
        │ total_comprado │    │ total_faturamento
        │ credito_*      │    │ credito_*       │   │ conteudo_extraido
        └────────────────┘    └─────────────────┘   └──────────┬───────┘
                │                     │                         │
                │                     │                         │
                └─────────────────────┼────────────────────────┘
                                      ▼
                            ┌──────────────────┐
                            │    invoices      │
                            │ (NOTAS FISCAIS)  │
                            ├──────────────────┤
                            │ id (UUID, PK)    │
                            │ numero_nf        │
                            │ direcao          │
                            │ cnpj_emitente    │
                            │ cnpj_destinatario│
                            │ valor_total      │
                            │ valor_ibs/cbs    │
                            └────────┬─────────┘
                                     │
                                     ▼
                        ┌──────────────────────┐
                        │   invoice_items      │
                        │  (ITENS DE NOTAS)    │
                        ├──────────────────────┤
                        │ id (UUID, PK)        │
                        │ numero_item          │
                        │ descricao            │
                        │ ncm, cfop            │
                        │ valor_total          │
                        │ aliquota_icms/iss    │
                        └──────────────────────┘

                    ┌───────────────────────────────┐
                    │      TAX RULES & RATES         │
                    │  (MOTOR DE LEGISLAÇÃO)        │
                    ├───────────────────────────────┤
        ┌──────────▶ │  tax_rules                    │
        │            │  (Regras tributárias)        │
        │            ├───────────────────────────────┤
        │            │ codigo_regra                  │
        │            │ tipo_tributo                  │
        │            │ fonte_legal (LC 227, EC 132) │
        │            │ status (OFICIAL/ESTIMADA)    │
        │            └───────────┬───────────────────┘
        │                        │
        │                        ▼
        │            ┌──────────────────────┐
        │            │   tax_rates          │
        │            │ (ALÍQUOTAS)          │
        │            ├──────────────────────┤
        │            │ codigo_aliquota      │
        │            │ aliquota_nominal     │
        │            │ parcela_deducao      │
        │            │ composicao_tributos  │
        │            └──────────────────────┘
        │                        │
        │                        ▼
        │            ┌──────────────────────┐
        │            │ ibs_cbs_rate_scenarios
        │            │ (CENÁRIOS IBS/CBS)   │
        │            ├──────────────────────┤
        │            │ nome_cenario         │
        │            │ aliquota_ibs_*       │
        │            │ aliquota_cbs         │
        │            │ tipo_cenario         │
        │            └──────────────────────┘
        │
        └─────────────────┐
                          │
                ┌─────────▼──────────────┐
                │   simulations          │
                │ (SIMULAÇÕES)           │
                ├────────────────────────┤
                │ id (UUID, PK)          │
                │ company_id (FK)        │
                │ tipo_cenario           │
                │ faturamento_simulado   │
                │ compras_simuladas      │
                │ tributo_total_simulado │
                │ credito_ibs/cbs_total  │
                │ nivel_confianca        │
                └────────┬───────────────┘
                         │
              ┌──────────┼──────────────┐
              │          │              │
              ▼          ▼              ▼
        ┌──────────┐ ┌──────────┐ ┌─────────────────┐
        │ credits  │ │ debits   │ │commercial_risks │
        │(CRÉDITOS)│ │(DÉBITOS) │ │  (RISCO COMERCIAL)
        ├──────────┤ ├──────────┤ ├─────────────────┤
        │ id (PK)  │ │ id (PK)  │ │ id (PK)         │
        │ tipo_*   │ │ tipo_*   │ │ nivel_risco     │
        │ valor_*  │ │ valor_*  │ │ percentual_*    │
        │ regime_* │ │ regime_* │ │ potencial_*     │
        └──────────┘ └──────────┘ └─────────────────┘

                    ┌──────────────────────────┐
                    │  calculation_memory      │
                    │ (RASTREABILIDADE)        │
                    ├──────────────────────────┤
                    │ id (UUID, PK)            │
                    │ simulation_id (FK)       │
                    │ tipo_calculo             │
                    │ valor_base               │
                    │ formula                  │
                    │ operacoes (JSON)         │
                    │ valor_resultado          │
                    └──────────────────────────┘

                    ┌──────────────────────────┐
                    │      alerts              │
                    │ (SISTEMA DE ALERTAS)     │
                    ├──────────────────────────┤
                    │ id (UUID, PK)            │
                    │ nivel_severidade         │
                    │ tipo_alerta              │
                    │ descricao                │
                    │ referencia_id            │
                    │ resolvido                │
                    └──────────────────────────┘

                    ┌──────────────────────────┐
                    │     audit_logs           │
                    │ (AUDITORIA)              │
                    ├──────────────────────────┤
                    │ id (UUID, PK)            │
                    │ tipo_acao                │
                    │ entidade_tipo            │
                    │ usuario                  │
                    │ dados_anteriores (JSON)  │
                    │ dados_novos (JSON)       │
                    │ sucesso                  │
                    └──────────────────────────┘
```

---

## Fluxo de Dados

### 1. **Importação de Documentos**
```
PDF/XML/Planilha
    ↓
[documents] ← Upload e metadados
    ↓
Extração e parsing
    ↓
[invoices] ← Notas consolidadas
    ↓
[invoice_items] ← Itens detalhados
    ↓
[suppliers] ← Fornecedores agregados por CNPJ
[customers] ← Clientes agregados por CNPJ
```

### 2. **Validação de Regime**
```
[suppliers/customers] (regime = INDEFINIDO)
    ↓
Consulta CNPJ API
    ↓
[suppliers/customers] (regime = SIMPLES_NACIONAL | LUCRO_REAL | ...)
[regime_validacao_status] = VALIDADO
```

### 3. **Cálculo de Créditos (Híbrido)**
```
[invoices] (tipo = ENTRADA, SAIDA)
    ↓
Consultar [suppliers] regime
    ↓
Aplicar [tax_rules] + [tax_rates]
    ↓
[credits] ← Crédito calculado por operação
    ↓
[simulation] → Agregar créditos por simulation_id
[calculation_memory] → Rastrear cada cálculo
```

### 4. **Análise de Risco Comercial**
```
[customers] (percentual_faturamento > 5%)
    ↓
Consultar regime
    ↓
Calcular potencial_credito_annual
    ↓
[commercial_risks] ← Classificar BAIXO/MEDIO/ALTO/CRITICO
    ↓
[alerts] ← Gerar alerta se ALTO ou CRITICO
```

### 5. **Simulação de Cenários**
```
Cenário: REAL_2026 / SIMPLES_PURO_2027 / SIMPLES_HIBRIDO_2027
    ↓
[simulations] ← Criar registro
    ↓
Buscar [invoices] da empresa
    ↓
Aplicar [tax_rules] do cenário
    ↓
Calcular [credits] e [debits]
    ↓
Agregar valores → [simulations].tributo_total_simulado
    ↓
[calculation_memory] ← Registrar cada passo
    ↓
[simulations].nivel_confianca ← Calcular % baseado em validação
```

---

## Índices e Constraints

### Índices (Otimização)
```sql
-- Lookup rápido por CNPJ
CREATE INDEX idx_suppliers_cnpj ON suppliers(cnpj);
CREATE INDEX idx_customers_cnpj ON customers(cnpj);

-- Queries por empresa
CREATE INDEX idx_suppliers_company_id ON suppliers(company_id);
CREATE INDEX idx_customers_company_id ON customers(company_id);
CREATE INDEX idx_invoices_company_id ON invoices(company_id);

-- Queries por simulação
CREATE INDEX idx_credits_simulation_id ON credits(simulation_id);
CREATE INDEX idx_debits_simulation_id ON debits(simulation_id);

-- Busca por data
CREATE INDEX idx_invoices_competencia ON invoices(data_competencia);
CREATE INDEX idx_documents_upload ON documents(data_upload);

-- Lookup de regras
CREATE INDEX idx_tax_rules_codigo ON tax_rules(codigo_regra);
CREATE INDEX idx_tax_rates_codigo ON tax_rates(codigo_aliquota);
```

### Foreign Keys
```sql
-- Fornecedores → Empresas
ALTER TABLE suppliers ADD CONSTRAINT fk_suppliers_company 
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

-- Clientes → Empresas
ALTER TABLE customers ADD CONSTRAINT fk_customers_company 
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

-- Notas → Empresas
ALTER TABLE invoices ADD CONSTRAINT fk_invoices_company 
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

-- Simulações → Empresas
ALTER TABLE simulations ADD CONSTRAINT fk_simulations_company 
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

-- Créditos → Simulações
ALTER TABLE credits ADD CONSTRAINT fk_credits_simulation 
  FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE;
```

---

## Tipos de Dados Customizados

### ENUM: Regime Tributário
```python
class TaxRegimeEnum(str, enum.Enum):
    SIMPLES_NACIONAL = "SIMPLES_NACIONAL"
    LUCRO_PRESUMIDO = "LUCRO_PRESUMIDO"
    LUCRO_REAL = "LUCRO_REAL"
    MEI = "MEI"
    ISENTO = "ISENTO"
    INDEFINIDO = "INDEFINIDO"
```

### ENUM: Tipo de Tributo
```python
class TaxTypeEnum(str, enum.Enum):
    IRPJ = "IRPJ"
    CSLL = "CSLL"
    PIS = "PIS"
    COFINS = "COFINS"
    ICMS = "ICMS"
    ISS = "ISS"
    IBS = "IBS"
    CBS = "CBS"
    # ... outros
```

### JSON: Composição de Tributos (Simples)
```json
{
  "IRPJ": 4.00,
  "CSLL": 3.50,
  "COFINS": 12.82,
  "PIS": 2.78,
  "INSS": 43.40,
  "ISS": 0.00
}
```

### JSON: Parâmetros de Simulação
```json
{
  "faturamento_simulado": 2500000.00,
  "compras_simuladas": 500000.00,
  "percentual_b2b": 75.0,
  "aliquota_cbs_estimada": 8.80,
  "cenario": "SIMPLES_HIBRIDO_2027"
}
```

---

## Exemplo de Query - Análise de Fornecedores

### Top 10 Fornecedores por Crédito Potencial
```sql
SELECT 
    cnpj,
    razao_social,
    regime_tributario,
    total_comprado,
    credito_ibs_confirmado,
    credito_cbs_confirmado,
    (credito_ibs_confirmado + credito_cbs_confirmado) as credito_total,
    percentual_compras,
    (credito_ibs_confirmado + credito_cbs_confirmado) / total_comprado * 100 as taxa_efetiva_credito
FROM suppliers
WHERE company_id = $1
  AND regime_validacao_status = 'VALIDADO'
  AND total_comprado > 0
ORDER BY (credito_ibs_confirmado + credito_cbs_confirmado) DESC
LIMIT 10;
```

### Análise de Risco Comercial - Clientes
```sql
SELECT 
    c.cnpj,
    c.razao_social,
    c.regime_tributario,
    c.total_faturamento,
    c.percentual_faturamento,
    c.credito_ibs_gerado_potencial + c.credito_cbs_gerado_potencial as credito_potencial_annual,
    CASE 
        WHEN c.percentual_faturamento > 30 THEN 'CRITICO'
        WHEN c.percentual_faturamento > 15 THEN 'ALTO'
        WHEN c.percentual_faturamento > 5 THEN 'MEDIO'
        ELSE 'BAIXO'
    END as nivel_risco
FROM customers c
WHERE c.company_id = $1
  AND c.regime_tributario = 'LUCRO_REAL'
ORDER BY c.percentual_faturamento DESC;
```

### Cálculo Agregado de Créditos por Simulation
```sql
SELECT 
    s.tipo_cenario,
    SUM(cr.valor_credito) as credito_ibs_total
FROM simulations s
LEFT JOIN credits cr ON s.id = cr.simulation_id 
                     AND cr.tipo_credito = 'IBS'
WHERE s.company_id = $1
  AND s.tipo_cenario IN ('SIMPLES_PURO_2027', 'SIMPLES_HIBRIDO_2027', 'LUCRO_REAL_2027')
GROUP BY s.tipo_cenario;
```

---

## Exemplo de Inserção de Dados

### 1. Criar Empresa
```sql
INSERT INTO companies (id, cnpj, razao_social, regime_tributario, uf, municipio, rbt12, faturamento_anual, simples_anexo)
VALUES (
    uuid_generate_v4(),
    '04286335000179',
    'WASHINGTON L LOPES COSMOPOLIS',
    'SIMPLES_NACIONAL',
    'SP',
    'Cosmópolis',
    2236444.92,
    2236444.92,
    'ANEXO_III'
);
```

### 2. Adicionar Fornecedor
```sql
INSERT INTO suppliers (id, company_id, cnpj, razao_social, regime_tributario, total_comprado, regime_validacao_status)
VALUES (
    uuid_generate_v4(),
    (SELECT id FROM companies WHERE cnpj = '04286335000179'),
    '10567953000190',
    'AUTO POSTO MP FERNANDES',
    'SIMPLES_NACIONAL',
    145907.57,
    'VALIDADO'
);
```

### 3. Registrar Crédito IBS
```sql
INSERT INTO credits (id, simulation_id, supplier_id, tipo_credito, base_calculo, aliquota, valor_credito, tipo_classificacao)
VALUES (
    uuid_generate_v4(),
    (SELECT id FROM simulations WHERE tipo_cenario = 'SIMPLES_HIBRIDO_2027' LIMIT 1),
    (SELECT id FROM suppliers WHERE cnpj = '10567953000190'),
    'IBS',
    145907.57,
    0.10,
    145.91,
    'CREDITO_INTEGRAL'
);
```

### 4. Registrar Cálculo na Memória
```sql
INSERT INTO calculation_memory (id, simulation_id, tipo_calculo, valor_base, formula, valor_resultado)
VALUES (
    uuid_generate_v4(),
    (SELECT id FROM simulations WHERE tipo_cenario = 'SIMPLES_HIBRIDO_2027' LIMIT 1),
    'CREDITO_IBS',
    145907.57,
    'valor_compra × aliquota_ibs',
    145.91
);
```

---

## Padrões e Convenções

### Nomenclatura de Campos
- `*_id` → Foreign keys
- `data_*` → Timestamps
- `valor_*` → Valores monetários (NUMERIC 15,2)
- `aliquota_*` → Percentuais (NUMERIC 5,2)
- `percentual_*` → Percentuais (NUMERIC 5,2)
- `*_status` → Status strings ou enums
- `tem_*` → Booleanos

### Padrão de Soft Delete
```python
# Usar campo 'ativa' em vez de DELETE
suppliers.ativa = False
```

### Versionamento de Regras Tributárias
```python
# tax_rules e tax_rates têm versão e data_vigencia
# Quando uma regra muda, criar novo registro, não atualizar
TaxRule(
    codigo_regra="SIMPLES_ANEXO_III_FAIXA_5_2026",
    versao=1,
    data_vigencia_inicio=datetime(2026, 1, 1),
    data_vigencia_fim=datetime(2026, 12, 31)
)

TaxRule(
    codigo_regra="SIMPLES_ANEXO_III_FAIXA_5_2027",  # Novo código
    versao=1,
    data_vigencia_inicio=datetime(2027, 1, 1),
    data_vigencia_fim=None
)
```

---

## Próximas Etapas

### Etapa 3: Schemas Pydantic
- Validação de entrada
- Serialização de saída
- Documentação automática

### Etapa 4: Services (Lógica de Negócio)
- Motor Simples Nacional
- Motor de créditos
- Análise comercial

### Etapa 5: API Endpoints
- RESTful routers
- Logging e auditoria

### Etapa 6: Importação de Dados
- Parsers de PDFs, XMLs
- Consolidação por CNPJ

---

**Versão**: 0.2.0  
**Status**: ✓ Completo  
**Próxima**: Etapa 3 - Schemas Pydantic
