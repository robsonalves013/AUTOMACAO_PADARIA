// Função para exibir mensagens de feedback na interface
function mostrarFeedback(containerId, mensagem, tipo) {
    const container = document.getElementById(containerId);
    container.textContent = mensagem;
    container.className = `feedback-container ${tipo}`;
    container.style.display = 'block';
    setTimeout(() => {
        container.style.display = 'none';
    }, 5000);
}

// Função para buscar e renderizar o estoque na tabela
async function carregarEstoque() {
    const tabelaEstoque = document.getElementById('tabela-estoque').getElementsByTagName('tbody')[0];
    tabelaEstoque.innerHTML = ''; // Limpa a tabela antes de carregar

    try {
        const response = await fetch('http://127.0.0.1:5000/estoque');
        const estoque = await response.json();

        for (const codigo in estoque) {
            const produto = estoque[codigo];
            const linha = tabelaEstoque.insertRow();
            linha.innerHTML = `
                <td>${codigo}</td>
                <td>${produto.descricao.charAt(0).toUpperCase() + produto.descricao.slice(1)}</td>
                <td>${produto.quantidade}</td>
                <td>R$ ${produto.valor_unitario.toFixed(2).replace('.', ',')}</td>
                <td>${produto.categoria}</td>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar estoque:', error);
        mostrarFeedback('estoque-feedback', 'Erro ao carregar estoque.', 'erro');
    }
}

// Função para buscar e renderizar as vendas diárias
async function carregarVendasDiarias() {
    const tabelaVendas = document.getElementById('tabela-vendas-diarias').getElementsByTagName('tbody')[0];
    tabelaVendas.innerHTML = ''; // Limpa a tabela antes de carregar

    try {
        const response = await fetch('http://127.0.0.1:5000/vendas/diarias');
        const vendas = await response.json();

        if (vendas.length === 0) {
            tabelaVendas.innerHTML = '<tr><td colspan="5">Nenhuma venda registrada hoje.</td></tr>';
            return;
        }

        vendas.forEach(venda => {
            const linha = tabelaVendas.insertRow();
            // Salva o ID da transação no próprio elemento da linha
            linha.dataset.id = venda.id_transacao; 
            linha.innerHTML = `
                <td>${venda.descricao}</td>
                <td>R$ ${venda.valor.toFixed(2).replace('.', ',')}</td>
                <td>${venda.forma_pagamento || venda.plataforma_delivery || 'Manual'}</td>
                <td>${venda.data.split(' ')[1]}</td>
                <td><button class="cancelar-btn" data-id="${venda.id_transacao}">Cancelar</button></td>
            `;
        });

        // Adiciona o listener de evento para os botões de cancelar
        document.querySelectorAll('.cancelar-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const idTransacao = event.target.dataset.id;
                const senha = prompt("Digite a senha master para cancelar a venda:");
                
                if (senha) {
                    await cancelarVenda(idTransacao, senha);
                } else {
                    mostrarFeedback('vendas-feedback', 'Cancelamento abortado.', 'aviso');
                }
            });
        });

    } catch (error) {
        console.error('Erro ao carregar vendas diárias:', error);
        mostrarFeedback('vendas-diarias-feedback', 'Erro ao carregar vendas diárias.', 'erro');
    }
}

// Função para cancelar uma venda
async function cancelarVenda(id, senha) {
    try {
        const response = await fetch('http://127.0.0.1:5000/vendas/cancelar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_transacao: id,
                senha_master: senha
            })
        });

        const result = await response.json();

        if (response.ok) {
            mostrarFeedback('vendas-feedback', result.message, 'sucesso');
            carregarVendasDiarias(); // Atualiza a tabela de vendas
            carregarEstoque(); // Atualiza a tabela de estoque
        } else {
            mostrarFeedback('vendas-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro ao cancelar a venda:', error);
        mostrarFeedback('vendas-feedback', 'Erro ao se conectar com a API.', 'erro');
    }
}

// --- Funções para registrar formulários ---

async function registrarVendaDireta(event) {
    event.preventDefault();
    const codigo = document.getElementById('venda-direta-codigo').value;
    const quantidade = parseInt(document.getElementById('venda-direta-quantidade').value);
    const formaPagamento = document.getElementById('venda-direta-pagamento').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/vendas/direta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ codigo, quantidade, forma_pagamento: formaPagamento })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('vendas-feedback', result.message, 'sucesso');
            document.getElementById('form-venda-direta').reset();
            carregarVendasDiarias();
            carregarEstoque();
        } else {
            mostrarFeedback('vendas-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarFeedback('vendas-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

async function registrarVendaDelivery(event) {
    event.preventDefault();
    const codigo = document.getElementById('venda-delivery-codigo').value;
    const quantidade = parseInt(document.getElementById('venda-delivery-quantidade').value);
    const plataforma = document.getElementById('venda-delivery-plataforma').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/vendas/delivery', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ codigo, quantidade, plataforma })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('vendas-feedback', result.message, 'sucesso');
            document.getElementById('form-venda-delivery').reset();
            carregarVendasDiarias();
            carregarEstoque();
        } else {
            mostrarFeedback('vendas-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarFeedback('vendas-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

async function adicionarProduto(event) {
    event.preventDefault();
    const codigo = document.getElementById('add-codigo').value;
    const descricao = document.getElementById('add-descricao').value;
    const quantidade = parseInt(document.getElementById('add-quantidade').value);
    const valorUnitario = parseFloat(document.getElementById('add-valor').value);
    const categoria = document.getElementById('add-categoria').value;
    
    try {
        const response = await fetch('http://127.0.0.1:5000/estoque/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo,
                descricao,
                quantidade,
                valor_unitario: valorUnitario,
                categoria
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('estoque-feedback', result.message, 'sucesso');
            document.getElementById('form-adicionar-produto').reset();
            carregarEstoque();
        } else {
            mostrarFeedback('estoque-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarFeedback('estoque-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

async function adicionarReceita(event) {
    event.preventDefault();
    const descricao = document.getElementById('receita-descricao').value;
    const valor = parseFloat(document.getElementById('receita-valor').value);

    try {
        const response = await fetch('http://127.0.0.1:5000/fluxo_caixa/receita', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ descricao, valor })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('fluxo-caixa-feedback', result.message, 'sucesso');
            document.getElementById('form-adicionar-receita').reset();
        } else {
            mostrarFeedback('fluxo-caixa-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarFeedback('fluxo-caixa-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

async function adicionarDespesa(event) {
    event.preventDefault();
    const descricao = document.getElementById('despesa-descricao').value;
    const valor = parseFloat(document.getElementById('despesa-valor').value);

    try {
        const response = await fetch('http://127.0.0.1:5000/fluxo_caixa/despesa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ descricao, valor })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('fluxo-caixa-feedback', result.message, 'sucesso');
            document.getElementById('form-adicionar-despesa').reset();
        } else {
            mostrarFeedback('fluxo-caixa-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarFeedback('fluxo-caixa-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

// Event Listeners para os formulários
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('form-venda-direta').addEventListener('submit', registrarVendaDireta);
    document.getElementById('form-venda-delivery').addEventListener('submit', registrarVendaDelivery);
    document.getElementById('form-adicionar-produto').addEventListener('submit', adicionarProduto);
    document.getElementById('form-adicionar-receita').addEventListener('submit', adicionarReceita);
    document.getElementById('form-adicionar-despesa').addEventListener('submit', adicionarDespesa);

    // Carrega os dados iniciais
    carregarVendasDiarias();
    carregarEstoque();
});