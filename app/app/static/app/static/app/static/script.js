// Configurações
const API_BASE = '/api';
let uploadedFiles = [];
let analysisData = null;

// ===== TAB MANAGEMENT =====
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// ===== FILE UPLOAD MANAGEMENT =====
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const processBtn = document.getElementById('processBtn');
const processingStatus = document.getElementById('processingStatus');

// Click to upload
uploadArea.addEventListener('click', () => fileInput.click());

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#764ba2';
    uploadArea.style.background = '#f0f1ff';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#667eea';
    uploadArea.style.background = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#667eea';
    uploadArea.style.background = 'transparent';

    const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
    addFiles(files);
});

// File input change
fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    addFiles(files);
});

function addFiles(files) {
    uploadedFiles = [...uploadedFiles, ...files];
    updateFileList();
}

function updateFileList() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';

    if (uploadedFiles.length === 0) {
        fileList.innerHTML = '<p style="color: #999;">Nenhum arquivo carregado</p>';
        return;
    }

    uploadedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>📄 ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            <button onclick="removeFile(${index})" style="background: #ff6b6b; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer;">✕</button>
        `;
        fileList.appendChild(fileItem);
    });
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFileList();
}

// ===== PROCESS FILES =====
processBtn.addEventListener('click', async () => {
    if (uploadedFiles.length === 0) {
        showStatus('Por favor, selecione pelo menos um arquivo PDF', 'error');
        return;
    }

    showStatus('Processando documentos... Por favor aguarde.', 'info');
    processBtn.disabled = true;

    try {
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Erro: ${response.statusText}`);
        }

        const data = await response.json();
        analysisData = data;

        showStatus('✓ Documentos processados com sucesso!', 'success');

        // Atualizar dashboard
        updateDashboard(data);

        // Ir para dashboard
        setTimeout(() => switchTab('dashboard'), 1000);

    } catch (error) {
        console.error('Erro ao processar:', error);
        showStatus(`Erro ao processar: ${error.message}`, 'error');
    } finally {
        processBtn.disabled = false;
    }
});

function showStatus(message, type) {
    processingStatus.textContent = message;
    processingStatus.className = `status-message ${type}`;
}

// ===== UPDATE DASHBOARD =====
function updateDashboard(data) {
    // Empresa
    document.getElementById('empresaCNPJ').textContent = data.empresa?.cnpj || '-';
    document.getElementById('empresaRazao').textContent = data.empresa?.razao_social || '-';
    document.getElementById('empresaRegime').textContent = data.empresa?.regime || '-';

    // Receitas
    const vendas = data.receitas?.vendas || 0;
    const servicos = data.receitas?.servicos || 0;
    const totalReceita = vendas + servicos;

    document.getElementById('receitaVendas').textContent = formatCurrency(vendas);
    document.getElementById('receitaServicos').textContent = formatCurrency(servicos);
    document.getElementById('receitaTotal').textContent = formatCurrency(totalReceita);

    // Compras
    const totalCompras = data.compras?.total || 0;
    document.getElementById('comprasTotal').textContent = formatCurrency(totalCompras);
    document.getElementById('numFornecedores').textContent = data.compras?.num_fornecedores || 0;

    // DAS
    const dasPago = data.das?.valor || 0;
    const cargaEfetiva = totalReceita > 0 ? ((dasPago / totalReceita) * 100).toFixed(2) : 0;
    document.getElementById('dasPago').textContent = formatCurrency(dasPago);
    document.getElementById('cargaEfetiva').textContent = `${cargaEfetiva}%`;

    // Cenários
    updateScenarios(data);

    // Fornecedores e Clientes
    updateFornecedoresTable(data.fornecedores || []);
    updateClientesTable(data.clientes || []);

    // Recomendação
    updateRecommendation(data);
}

function updateScenarios(data) {
    const vendas = data.receitas?.vendas || 0;
    const servicos = data.receitas?.servicos || 0;
    const totalReceita = vendas + servicos;
    const dasPago = data.das?.valor || 0;

    // 2026 Real
    const cena2026 = dasPago;
    document.getElementById('cena2026').textContent = formatCurrency(cena2026);

    // 2027 Simples Puro (estimar com mesma alíquota)
    const aliquotaSimples = totalReceita > 0 ? dasPago / totalReceita : 0;
    const cena2027Simples = totalReceita * aliquotaSimples;
    document.getElementById('cenaSimplesPuro').textContent = formatCurrency(cena2027Simples);

    // 2027 Híbrido (estimativa)
    const compras = data.compras?.total || 0;
    const creditoIBS = compras * 0.001; // 0.1% simplificado
    const creditoCBS = compras * 0.088; // 8.8% estimado
    const creditoTotal = creditoIBS + creditoCBS;

    const debitoIBS = totalReceita * 0.001; // 0.1%
    const debitoCBS = totalReceita * 0.088; // 8.8%
    const cena2027Hibrido = Math.max(0, (debitoIBS + debitoCBS) - creditoTotal);

    document.getElementById('cenaHibrido').textContent = formatCurrency(cena2027Hibrido);

    // Créditos
    document.getElementById('creditoIBS').textContent = formatCurrency(creditoIBS);
    document.getElementById('creditoCBS').textContent = formatCurrency(creditoCBS);
    document.getElementById('creditoTotal').textContent = formatCurrency(creditoTotal);

    // Tabela de Comparação
    updateComparisonTable(cena2026, cena2027Simples, cena2027Hibrido, totalReceita);
}

function updateComparisonTable(v2026, vSimples, vHibrido, receita) {
    const tbody = document.getElementById('comparisonTableBody');
    tbody.innerHTML = `
        <tr>
            <td><strong>Carga Tributária</strong></td>
            <td>${formatCurrency(v2026)}</td>
            <td>${formatCurrency(vSimples)}</td>
            <td>${formatCurrency(vHibrido)}</td>
            <td><strong>${formatCurrency(vHibrido - v2026)}</strong></td>
        </tr>
        <tr>
            <td><strong>Percentual da Receita</strong></td>
            <td>${((v2026 / receita) * 100).toFixed(2)}%</td>
            <td>${((vSimples / receita) * 100).toFixed(2)}%</td>
            <td>${((vHibrido / receita) * 100).toFixed(2)}%</td>
            <td><strong>${(((vHibrido - v2026) / receita) * 100).toFixed(2)}%</strong></td>
        </tr>
    `;
}

function updateFornecedoresTable(fornecedores) {
    const container = document.getElementById('topFornecedores');

    if (fornecedores.length === 0) {
        container.innerHTML = '<p>Nenhum fornecedor encontrado</p>';
        return;
    }

    // Ordenar por valor descendente
    const top10 = fornecedores
        .sort((a, b) => (b.total || 0) - (a.total || 0))
        .slice(0, 10);

    let html = '<table><thead><tr><th>#</th><th>Fornecedor</th><th>CNPJ</th><th>Total Comprado</th><th>% do Total</th><th>Regime</th></tr></thead><tbody>';

    const totalCompras = fornecedores.reduce((sum, f) => sum + (f.total || 0), 0);

    top10.forEach((f, i) => {
        const pct = totalCompras > 0 ? ((f.total / totalCompras) * 100).toFixed(2) : 0;
        html += `
            <tr>
                <td>${i + 1}</td>
                <td>${f.nome || '-'}</td>
                <td>${f.cnpj || '-'}</td>
                <td>${formatCurrency(f.total || 0)}</td>
                <td>${pct}%</td>
                <td>${f.regime || 'NÃO VALIDADO'}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function updateClientesTable(clientes) {
    const container = document.getElementById('topClientes');

    if (clientes.length === 0) {
        container.innerHTML = '<p>Nenhum cliente encontrado</p>';
        return;
    }

    // Ordenar por faturamento descendente
    const top10 = clientes
        .sort((a, b) => (b.faturamento || 0) - (a.faturamento || 0))
        .slice(0, 10);

    let html = '<table><thead><tr><th>#</th><th>Cliente</th><th>CNPJ</th><th>Faturamento</th><th>% do Total</th><th>Regime</th><th>Risco</th></tr></thead><tbody>';

    const totalFat = clientes.reduce((sum, c) => sum + (c.faturamento || 0), 0);

    top10.forEach((c, i) => {
        const pct = totalFat > 0 ? ((c.faturamento / totalFat) * 100).toFixed(2) : 0;
        const risco = c.risco || 'MÉDIO';
        let riscoColor = '#ffc107';
        if (risco === 'BAIXO') riscoColor = '#28a745';
        if (risco === 'CRÍTICO') riscoColor = '#dc3545';

        html += `
            <tr>
                <td>${i + 1}</td>
                <td>${c.nome || '-'}</td>
                <td>${c.cnpj || '-'}</td>
                <td>${formatCurrency(c.faturamento || 0)}</td>
                <td>${pct}%</td>
                <td>${c.regime || 'NÃO VALIDADO'}</td>
                <td><span style="background: ${riscoColor}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">${risco}</span></td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function updateRecommendation(data) {
    const vendas = data.receitas?.vendas || 0;
    const servicos = data.receitas?.servicos || 0;
    const totalReceita = vendas + servicos;
    const dasPago = data.das?.valor || 0;
    const compras = data.compras?.total || 0;
    const numClientes = data.clientes ? data.clientes.length : 0;
    const numFornecedores = data.fornecedores ? data.fornecedores.length : 0;

    // Calcular cenários
    const aliquotaSimples = totalReceita > 0 ? dasPago / totalReceita : 0;
    const cena2027Simples = totalReceita * aliquotaSimples;

    const creditoTotal = (compras * 0.001) + (compras * 0.088);
    const cena2027Hibrido = Math.max(0, ((totalReceita * 0.001) + (totalReceita * 0.088)) - creditoTotal);

    const economia = cena2027Simples - cena2027Hibrido;

    // Recomendação
    let recomendacao = '';
    let tipoRecomendacao = '';
    let perfil = [];

    if (economia > 0) {
        recomendacao = '🟢 HÍBRIDO MAIS VANTAJOSO';
        tipoRecomendacao = 'positive';
    } else if (economia < -5000) {
        recomendacao = '🔴 SIMPLES PURO MAIS VANTAJOSO';
        tipoRecomendacao = 'negative';
    } else {
        recomendacao = '🟡 RESULTADO INDEFINIDO';
        tipoRecomendacao = '';
    }

    // Perfil da empresa
    const percB2B = numClientes > 0 ? (data.clientes.filter(c => c.regime !== 'MEI' && c.regime !== 'PJ Simples').length / numClientes) * 100 : 0;

    perfil.push(`Faturamento: R$ ${formatCurrencyShort(totalReceita)}`);
    perfil.push(`Clientes B2B: ${percB2B.toFixed(0)}%`);
    perfil.push(`Fornecedores: ${numFornecedores}`);
    if (compras > 0) {
        perfil.push(`Potencial de Crédito: ${((creditoTotal / totalReceita) * 100).toFixed(1)}%`);
    }

    // Risco comercial
    let riscoComercial = 'BAIXO';
    const topClientePercent = numClientes > 0 ? ((data.clientes[0]?.faturamento || 0) / totalReceita) * 100 : 0;
    if (topClientePercent > 50) {
        riscoComercial = 'CRÍTICO';
    } else if (topClientePercent > 30) {
        riscoComercial = 'ALTO';
    } else if (topClientePercent > 15) {
        riscoComercial = 'MÉDIO';
    }

    // Atualizar UI
    const recBox = document.getElementById('recommendationBox');
    recBox.textContent = recomendacao;
    recBox.className = `recommendation-box ${tipoRecomendacao}`;

    document.getElementById('economiaAnual').textContent = formatCurrency(Math.abs(economia));

    const perfilList = document.getElementById('perfilEmpresa');
    perfilList.innerHTML = perfil.map(p => `<li>${p}</li>`).join('');

    document.getElementById('riscoComercial').innerHTML = `
        <span style="background: ${getRiscoColor(riscoComercial)}; color: white; padding: 4px 12px; border-radius: 4px; display: inline-block;">
            ${riscoComercial}
        </span>
    `;
}

function getRiscoColor(risco) {
    switch(risco) {
        case 'BAIXO': return '#28a745';
        case 'MÉDIO': return '#ffc107';
        case 'ALTO': return '#fd7e14';
        case 'CRÍTICO': return '#dc3545';
        default: return '#6c757d';
    }
}

// ===== UTILITY FUNCTIONS =====
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value || 0);
}

function formatCurrencyShort(value) {
    if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
        return `${(value / 1000).toFixed(1)}K`;
    }
    return `${value.toFixed(0)}`;
}

// Report Generation
document.getElementById('generateReportBtn')?.addEventListener('click', async () => {
    if (!analysisData) {
        alert('Por favor, carregue e processe os documentos primeiro');
        return;
    }
    alert('Relatório em PDF será disponibilizado em breve. Por enquanto, você pode fazer print desta página (Ctrl+P).');
});

// Inicializar
console.log('Motor de Decisão Tributária v0.2.0 carregado');
