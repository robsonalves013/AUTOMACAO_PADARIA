// script_teste.js
// Variáveis globais para o carrinho de compras e vendas
let carrinho = [];
let vendasDiariasData = []; // Armazena os dados brutos das vendas do dia

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
            
            // NOVO: Adiciona a classe 'low-stock' se a quantidade for menor que 10
            if (produto.quantidade < 10) {
                linha.classList.add('low-stock');
            }
            
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
        vendasDiariasData = await response.json(); // Armazena os dados brutos

        if (vendasDiariasData.length === 0) {
            tabelaVendas.innerHTML = '<tr><td colspan="6">Nenhuma venda registrada hoje.</td></tr>';
            return;
        }

        vendasDiariasData.forEach(venda => {
            const linha = tabelaVendas.insertRow();
            linha.dataset.id = venda.id_transacao; 
            linha.classList.add('expandable-row'); // Adiciona a classe para facilitar
            const isCancelled = venda.descricao.includes("CANCELADA");
            const isDelivery = venda.plataforma_delivery ? true : false;
            
            linha.innerHTML = `
                <td style="${isCancelled ? 'text-decoration: line-through; color: #aaa;' : ''}">${venda.descricao}</td>
                <td style="${isCancelled ? 'text-decoration: line-through; color: #aaa;' : ''}">${isDelivery ? '---' : 'R$ ' + venda.valor.toFixed(2).replace('.', ',')}</td>
                <td style="${isCancelled ? 'text-decoration: line-through; color: #aaa;' : ''}">${venda.forma_pagamento || venda.plataforma_delivery || 'Manual'}</td>
                <td style="${isCancelled ? 'text-decoration: line-through; color: #aaa;' : ''}">${venda.data.split(' ')[1]}</td>
                <td>
                    <button class="cancelar-btn" data-id="${venda.id_transacao}" ${isCancelled ? 'disabled style="background-color: #ccc; cursor: not-allowed;"' : ''}>
                        ${isCancelled ? 'Cancelada' : 'Cancelar'}
                    </button>
                </td>
                <td>
                    ${venda.itens && venda.itens.length > 1 ? `<button class="expandir-btn" data-id="${venda.id_transacao}">+ Detalhes</button>` : '---'}
                </td>
            `;
        });

        // Adiciona o listener de evento para os botões de cancelar
        document.querySelectorAll('.cancelar-btn').forEach(button => {
            button.addEventListener('click', () => {
                const idTransacao = button.dataset.id;
                abrirModalSenha(idTransacao);
            });
        });

        // Adiciona o listener de evento para os novos botões de expandir
        document.querySelectorAll('.expandir-btn').forEach(button => {
            button.addEventListener('click', () => {
                const idTransacao = button.dataset.id;
                toggleDetalhesVenda(idTransacao);
            });
        });

    } catch (error) {
        console.error('Erro ao carregar vendas diárias:', error);
        mostrarFeedback('vendas-diarias-feedback', 'Erro ao carregar vendas diárias.', 'erro');
    }
}

// Função para expandir/ocultar os detalhes de uma venda
function toggleDetalhesVenda(idTransacao) {
    const venda = vendasDiariasData.find(v => v.id_transacao === idTransacao);
    if (!venda || !venda.itens || venda.itens.length <= 1) return;

    const tabelaVendas = document.getElementById('tabela-vendas-diarias').getElementsByTagName('tbody')[0];
    const linhaVenda = tabelaVendas.querySelector(`[data-id='${idTransacao}']`);

    // Remove linhas de detalhes se já existirem
    const linhasExistentes = tabelaVendas.querySelectorAll(`.item-detail-row[data-parent-id='${idTransacao}']`);
    if (linhasExistentes.length > 0) {
        linhasExistentes.forEach(linha => linha.remove());
        // Altera o texto do botão para "Expandir"
        const botaoExpandir = linhaVenda.querySelector('.expandir-btn');
        if (botaoExpandir) botaoExpandir.textContent = '+ Detalhes';
        return;
    }

    // Adiciona as novas linhas de detalhes
    venda.itens.forEach(item => {
        const novaLinha = tabelaVendas.insertRow(linhaVenda.rowIndex);
        novaLinha.classList.add('item-detail-row');
        novaLinha.dataset.parentId = idTransacao;
        novaLinha.innerHTML = `
            <td>- ${item.descricao.charAt(0).toUpperCase() + item.descricao.slice(1)}</td>
            <td>${item.quantidade}</td>
            <td>R$ ${item.valor_unitario.toFixed(2).replace('.', ',')}</td>
            <td colspan="3"></td>
        `;
    });

    // Altera o texto do botão para "Ocultar"
    const botaoExpandir = linhaVenda.querySelector('.expandir-btn');
    if (botaoExpandir) botaoExpandir.textContent = '- Ocultar';
}

// Modal de senha para cancelamento
const modalSenha = document.getElementById('password-modal');
const closeBtnSenha = document.querySelector('.close-btn');
const confirmBtnSenha = document.getElementById('modal-confirm-btn');
let transacaoParaCancelar = null;

function abrirModalSenha(idTransacao) {
    transacaoParaCancelar = idTransacao;
    modalSenha.style.display = 'flex';
}

function fecharModalSenha() {
    modalSenha.style.display = 'none';
    document.getElementById('modal-password').value = '';
    transacaoParaCancelar = null;
}

closeBtnSenha.addEventListener('click', fecharModalSenha);
window.addEventListener('click', (event) => {
    if (event.target === modalSenha) {
        fecharModalSenha();
    }
});

confirmBtnSenha.addEventListener('click', async () => {
    const senha = document.getElementById('modal-password').value;
    if (!senha) return;
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/vendas/cancelar/${transacaoParaCancelar}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ senha: senha })
        });
        const result = await response.json();
        
        if (response.ok) {
            mostrarFeedback('vendas-diarias-feedback', result.message, 'sucesso');
            carregarVendasDiarias(); // Recarrega a tabela de vendas
            carregarEstoque(); // Recarrega o estoque
        } else {
            mostrarFeedback('vendas-diarias-feedback', `Erro: ${result.error}`, 'erro');
        }
        fecharModalSenha();
    } catch (error) {
        console.error('Erro ao cancelar venda:', error);
        mostrarFeedback('vendas-diarias-feedback', 'Erro ao cancelar venda.', 'erro');
        fecharModalSenha();
    }
});

// Modal de Troco
const modalTroco = document.getElementById('troco-modal');
const closeBtnTroco = document.querySelector('.troco-close-btn');
const calcularTrocoBtn = document.getElementById('calcular-troco-btn');
const finalizarTrocoBtn = document.getElementById('finalizar-troco-btn');
const trocoRecebidoInput = document.getElementById('troco-recebido');
const trocoValorSpan = document.getElementById('troco-valor');
let valorVendaTotal = 0;

function abrirModalTroco(total) {
    valorVendaTotal = total;
    document.getElementById('troco-total-venda').textContent = `Total da Venda: R$ ${valorVendaTotal.toFixed(2).replace('.', ',')}`;
    trocoRecebidoInput.value = '';
    trocoValorSpan.textContent = 'R$ 0,00';
    modalTroco.style.display = 'flex';
}

closeBtnTroco.addEventListener('click', () => {
    modalTroco.style.display = 'none';
});

calcularTrocoBtn.addEventListener('click', () => {
    const valorRecebido = parseFloat(trocoRecebidoInput.value);
    if (isNaN(valorRecebido) || valorRecebido < valorVendaTotal) {
        trocoValorSpan.textContent = 'Valor insuficiente!';
        trocoValorSpan.style.color = '#dc3545';
        finalizarTrocoBtn.disabled = true;
    } else {
        const troco = valorRecebido - valorVendaTotal;
        trocoValorSpan.textContent = `R$ ${troco.toFixed(2).replace('.', ',')}`;
        trocoValorSpan.style.color = '#007bff';
        finalizarTrocoBtn.disabled = false;
    }
});

finalizarTrocoBtn.addEventListener('click', () => {
    registrarVendaFinal(carrinho, 'Dinheiro');
    modalTroco.style.display = 'none';
});

// Funções de requisição da API
async function adicionarItemAoCarrinho(event) {
    event.preventDefault();
    const codigo = document.getElementById('venda-codigo-direta').value;
    const quantidade = parseInt(document.getElementById('venda-quantidade-direta').value);

    try {
        const response = await fetch('http://127.0.0.1:5000/estoque');
        const estoque = await response.json();
        
        if (codigo in estoque) {
            const produto = estoque[codigo];
            if (produto.quantidade >= quantidade) {
                const itemExistente = carrinho.find(item => item.codigo === codigo);
                if (itemExistente) {
                    itemExistente.quantidade += quantidade;
                } else {
                    carrinho.push({
                        codigo: codigo,
                        descricao: produto.descricao,
                        quantidade: quantidade,
                        valor_unitario: produto.valor_unitario
                    });
                }
                renderizarCarrinho();
                mostrarFeedback('vendas-feedback', 'Produto adicionado ao carrinho!', 'sucesso');
            } else {
                mostrarFeedback('vendas-feedback', 'Estoque insuficiente para este produto.', 'erro');
            }
        } else {
            mostrarFeedback('vendas-feedback', 'Produto não encontrado no estoque.', 'erro');
        }
        document.getElementById('form-venda-direta').reset();
    } catch (error) {
        console.error('Erro ao adicionar item ao carrinho:', error);
        mostrarFeedback('vendas-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

async function handleFinalizarVenda() {
    const formaPagamento = document.getElementById('forma-pagamento').value;
    if (formaPagamento === 'Dinheiro') {
        const total = carrinho.reduce((sum, item) => sum + (item.quantidade * item.valor_unitario), 0);
        abrirModalTroco(total);
    } else {
        registrarVendaFinal(carrinho, formaPagamento);
    }
}

async function registrarVendaFinal(carrinho, formaPagamento) {
    try {
        const response = await fetch('http://127.0.0.1:5000/multi-venda', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ carrinho: carrinho, forma_pagamento: formaPagamento })
        });
        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('vendas-feedback', result.message, 'sucesso');
            carrinho = []; // Limpa o carrinho
            renderizarCarrinho();
            carregarVendasDiarias(); // Recarrega a tabela de vendas
            carregarEstoque(); // Recarrega o estoque
        } else {
            mostrarFeedback('vendas-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarFeedback('vendas-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

function renderizarCarrinho() {
    const tabelaCarrinho = document.getElementById('tabela-carrinho').getElementsByTagName('tbody')[0];
    tabelaCarrinho.innerHTML = '';
    let total = 0;

    carrinho.forEach((item, index) => {
        const linha = tabelaCarrinho.insertRow();
        const valorTotalItem = item.quantidade * item.valor_unitario;
        total += valorTotalItem;

        linha.innerHTML = `
            <td>${item.descricao.charAt(0).toUpperCase() + item.descricao.slice(1)}</td>
            <td>${item.quantidade}</td>
            <td>R$ ${item.valor_unitario.toFixed(2).replace('.', ',')}</td>
            <td>R$ ${valorTotalItem.toFixed(2).replace('.', ',')}</td>
            <td>
                <button onclick="removerItemCarrinho(${index})">Remover</button>
            </td>
        `;
    });

    document.getElementById('carrinho-total').textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;
    const finalizarBtn = document.getElementById('finalizar-btn');
    const formaPagamentoSelect = document.getElementById('forma-pagamento');
    if (carrinho.length > 0) {
        finalizarBtn.disabled = false;
        formaPagamentoSelect.disabled = false;
    } else {
        finalizarBtn.disabled = true;
        formaPagamentoSelect.disabled = true;
        formaPagamentoSelect.value = '';
    }
}

function removerItemCarrinho(index) {
    carrinho.splice(index, 1);
    renderizarCarrinho();
    mostrarFeedback('vendas-feedback', 'Produto removido do carrinho.', 'sucesso');
}

async function registrarVendaDelivery(event) {
    event.preventDefault();
    const codigo = document.getElementById('venda-codigo-delivery').value;
    const quantidade = parseInt(document.getElementById('venda-quantidade-delivery').value);
    const plataforma = document.getElementById('plataforma-delivery').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/venda', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: codigo,
                quantidade: quantidade,
                plataforma_delivery: plataforma
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('vendas-feedback', result.message, 'sucesso');
            carregarVendasDiarias();
            carregarEstoque();
        } else {
            mostrarFeedback('vendas-feedback', `Erro: ${result.error}`, 'erro');
        }
        document.getElementById('form-venda-delivery').reset();
    } catch (error) {
        console.error('Erro:', error);
        mostrarFeedback('vendas-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

async function adicionarProduto(event) {
    event.preventDefault();
    const codigo = document.getElementById('produto-codigo').value;
    const descricao = document.getElementById('produto-descricao').value;
    const quantidade = document.getElementById('produto-quantidade').value;
    const valor_unitario = document.getElementById('produto-valor').value;
    const categoria = document.getElementById('produto-categoria').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/produto/adicionar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: codigo,
                descricao: descricao,
                quantidade: quantidade,
                valor_unitario: valor_unitario,
                categoria: categoria
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

async function alterarProduto(event) {
    event.preventDefault();
    const codigo = document.getElementById('alterar-codigo').value;
    const nova_quantidade = document.getElementById('alterar-quantidade').value;
    const novo_valor = document.getElementById('alterar-valor').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/produto/alterar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: codigo,
                nova_quantidade: nova_quantidade,
                novo_valor: novo_valor
            })
        });
        const result = await response.json();

        if (response.ok) {
            mostrarFeedback('estoque-feedback', result.message, 'sucesso');
            document.getElementById('form-alterar-produto').reset();
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
    const valor = document.getElementById('receita-valor').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/receita/adicionar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                descricao: descricao,
                valor: valor
            })
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
    const valor = document.getElementById('despesa-valor').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/despesa/adicionar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                descricao: descricao,
                valor: valor
            })
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
    // Evento para adicionar item ao carrinho, não mais para finalizar a venda
    document.getElementById('form-venda-direta').addEventListener('submit', adicionarItemAoCarrinho);
    // Novo: Evento para finalizar a venda a partir do botão
    document.getElementById('finalizar-btn').addEventListener('click', handleFinalizarVenda);
    
    document.getElementById('form-venda-delivery').addEventListener('submit', registrarVendaDelivery);
    document.getElementById('form-adicionar-produto').addEventListener('submit', adicionarProduto);
    document.getElementById('form-adicionar-receita').addEventListener('submit', adicionarReceita);
    document.getElementById('form-adicionar-despesa').addEventListener('submit', adicionarDespesa);

    // NOVO: Event listener para o formulário de alteração de produto
    document.getElementById('form-alterar-produto').addEventListener('submit', alterarProduto);

    // Carrega os dados iniciais
    carregarVendasDiarias();
    carregarEstoque();
});