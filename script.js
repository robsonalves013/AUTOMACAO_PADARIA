const API_BASE_URL = 'http://127.0.0.1:5000'; // Endereço da sua API Flask

// Função para buscar o estoque
async function getEstoque() {
    const estoqueDisplay = document.getElementById('estoque-display');
    estoqueDisplay.textContent = 'Carregando...';
    try {
        const response = await fetch(`${API_BASE_URL}/estoque`);
        if (!response.ok) {
            throw new Error('Erro ao buscar o estoque. Verifique se a API está funcionando.');
        }
        const data = await response.json();
        estoqueDisplay.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        estoqueDisplay.textContent = `Erro: ${error.message}`;
        console.error('Erro:', error);
    }
}

// Função para buscar o fluxo de caixa
async function getFluxoCaixa() {
    const fluxoDisplay = document.getElementById('fluxo-caixa-display');
    fluxoDisplay.textContent = 'Carregando...';
    try {
        const response = await fetch(`${API_BASE_URL}/fluxo-caixa`);
        if (!response.ok) {
            throw new Error('Erro ao buscar o fluxo de caixa.');
        }
        const data = await response.json();
        const resumo = `
            Total de Receitas: R$ ${data.total_receitas.toFixed(2)}
            Total de Despesas: R$ ${data.total_despesas.toFixed(2)}
            Saldo Atual: R$ ${data.saldo.toFixed(2)}
        `;
        fluxoDisplay.textContent = resumo;
    } catch (error) {
        fluxoDisplay.textContent = `Erro: ${error.message}`;
        console.error('Erro:', error);
    }
}

// Função para registrar uma venda
async function registrarVenda(event) {
    event.preventDefault(); // Impede o envio padrão do formulário
    
    const vendaForm = document.getElementById('venda-form');
    const vendaStatus = document.getElementById('venda-status');
    const formData = new FormData(vendaForm);

    const data = {
        produto: formData.get('produto').toLowerCase(),
        quantidade: parseInt(formData.get('quantidade')),
        forma_pagamento: formData.get('forma_pagamento')
    };

    try {
        const response = await fetch(`${API_BASE_URL}/venda`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const resultado = await response.json();
        
        if (response.ok) {
            vendaStatus.textContent = resultado.message;
            vendaStatus.className = 'message success';
            vendaForm.reset();
        } else {
            vendaStatus.textContent = resultado.message;
            vendaStatus.className = 'message error';
        }
    } catch (error) {
        vendaStatus.textContent = `Erro: ${error.message}`;
        vendaStatus.className = 'message error';
        console.error('Erro:', error);
    }
}

// Adiciona o listener para o formulário de venda
document.getElementById('venda-form').addEventListener('submit', registrarVenda);
