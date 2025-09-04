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
const passwordInput = document.getElementById('modal-password');
let idTransacaoGlobal = null;

function abrirModalSenha(idTransacao) {
    idTransacaoGlobal = idTransacao;
    passwordInput.value = '';
    modalSenha.style.display = 'flex';
    passwordInput.focus();
}

closeBtnSenha.addEventListener('click', () => {
    modalSenha.style.display = 'none';
});

confirmBtnSenha.addEventListener('click', () => {
    const senha = passwordInput.value;
    if (senha) {
        cancelarVenda(idTransacaoGlobal, senha);
        modalSenha.style.display = 'none';
    } else {
        mostrarFeedback('vendas-feedback', 'Senha não pode ser vazia.', 'erro');
    }
});

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

// Novo Modal para o troco
const modalTroco = document.getElementById('troco-modal');
const closeBtnTroco = document.querySelector('.troco-close-btn');
const recebidoInput = document.getElementById('troco-recebido');
const trocoValorSpan = document.getElementById('troco-valor');
const confirmBtnTroco = document.getElementById('troco-confirm-btn');
const totalVendaDisplay = document.getElementById('troco-total-venda');

let totalVendaGlobal = 0;
let vendaDataGlobal = null;

// Função para abrir o modal do troco
function abrirModalTroco(totalVenda) {
    totalVendaGlobal = totalVenda;
    totalVendaDisplay.textContent = `Total da Venda: R$ ${totalVenda.toFixed(2).replace('.', ',')}`;
    recebidoInput.value = '';
    trocoValorSpan.textContent = 'R$ 0,00';
    modalTroco.style.display = 'flex';
    recebidoInput.focus();
}

// Event listener para calcular o troco em tempo real
recebidoInput.addEventListener('input', () => {
    const valorRecebido = parseFloat(recebidoInput.value) || 0;
    const troco = valorRecebido - totalVendaGlobal;
    trocoValorSpan.textContent = `R$ ${Math.max(0, troco).toFixed(2).replace('.', ',')}`;
});

// Event listener para o botão de confirmação do troco
confirmBtnTroco.addEventListener('click', () => {
    if (recebidoInput.value && parseFloat(recebidoInput.value) >= totalVendaGlobal) {
        modalTroco.style.display = 'none';
        processarVendaDiretaAPI('Dinheiro');
    } else {
        mostrarFeedback('vendas-feedback', 'Valor recebido insuficiente ou inválido.', 'erro');
    }
});

// Fecha o modal do troco
closeBtnTroco.addEventListener('click', () => {
    modalTroco.style.display = 'none';
});

// Fecha modais ao clicar fora deles
window.addEventListener('click', (event) => {
    if (event.target === modalSenha) {
        modalSenha.style.display = 'none';
    }
    if (event.target === modalTroco) {
        modalTroco.style.display = 'none';
    }
});

// --- Funções para registrar formulários ---

// Novo: Adiciona item ao carrinho
async function adicionarItemAoCarrinho(event) {
    event.preventDefault();
    const codigo = document.getElementById('venda-direta-codigo').value;
    const quantidade = parseInt(document.getElementById('venda-direta-quantidade').value);

    if (!codigo || !quantidade) {
        mostrarFeedback('vendas-feedback', 'Por favor, preencha o código e a quantidade.', 'erro');
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/estoque`);
        const estoque = await response.json();
        const produto = estoque[codigo];

        if (!produto) {
            mostrarFeedback('vendas-feedback', 'Produto não encontrado no estoque.', 'erro');
            return;
        }

        if (produto.quantidade < quantidade) {
            mostrarFeedback('vendas-feedback', `Estoque insuficiente! Disponível: ${produto.quantidade}.`, 'erro');
            return;
        }

        // Verifica se o item já está no carrinho e atualiza
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
        
        mostrarFeedback('vendas-feedback', `Item ${produto.descricao} adicionado ao carrinho.`, 'sucesso');
        renderizarCarrinho();
        document.getElementById('form-venda-direta').reset();
    } catch (error) {
        console.error('Erro ao adicionar item:', error);
        mostrarFeedback('vendas-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

// Novo: Renderiza o carrinho na interface
function renderizarCarrinho() {
    const tabelaCarrinho = document.getElementById('tabela-carrinho').getElementsByTagName('tbody')[0];
    const carrinhoTotalDisplay = document.getElementById('carrinho-total');
    const finalizarContainer = document.getElementById('finalizar-venda-container');
    const finalizarBtn = document.getElementById('finalizar-btn');
    tabelaCarrinho.innerHTML = '';
    
    let total = 0;
    carrinho.forEach(item => {
        const subtotal = item.quantidade * item.valor_unitario;
        total += subtotal;
        const linha = tabelaCarrinho.insertRow();
        linha.innerHTML = `
            <td>${item.descricao.charAt(0).toUpperCase() + item.descricao.slice(1)}</td>
            <td>${item.quantidade}</td>
            <td>R$ ${subtotal.toFixed(2).replace('.', ',')}</td>
        `;
    });

    carrinhoTotalDisplay.textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;

    if (carrinho.length > 0) {
        finalizarContainer.style.display = 'block';
        finalizarBtn.disabled = false;
    } else {
        finalizarContainer.style.display = 'none';
        finalizarBtn.disabled = true;
    }
}

// Novo: Finaliza a venda enviando o carrinho para a API
async function processarVendaDiretaAPI(formaPagamento) {
    if (carrinho.length === 0) {
        mostrarFeedback('vendas-feedback', 'Carrinho vazio. Adicione itens para finalizar a venda.', 'erro');
        return;
    }
    
    try {
        const response = await fetch('http://127.0.0.1:5000/vendas/direta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                carrinho: carrinho.map(item => ({
                    codigo: item.codigo,
                    quantidade: item.quantidade
                })),
                forma_pagamento: formaPagamento
            })
        });

        const result = await response.json();
        if (response.ok) {
            mostrarFeedback('vendas-feedback', result.message, 'sucesso');
            carrinho = []; // Limpa o carrinho após a venda
            renderizarCarrinho();
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

// Novo: Lógica para finalizar a venda com base na forma de pagamento
function handleFinalizarVenda() {
    const formaPagamento = document.getElementById('venda-direta-pagamento').value;
    const totalVenda = carrinho.reduce((acc, item) => acc + (item.quantidade * item.valor_unitario), 0);

    if (formaPagamento === 'Dinheiro') {
        abrirModalTroco(totalVenda);
    } else {
        processarVendaDiretaAPI(formaPagamento);
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
    // Evento para adicionar item ao carrinho, não mais para finalizar a venda
    document.getElementById('form-venda-direta').addEventListener('submit', adicionarItemAoCarrinho);
    // Novo: Evento para finalizar a venda a partir do botão
    document.getElementById('finalizar-btn').addEventListener('click', handleFinalizarVenda);
    
    document.getElementById('form-venda-delivery').addEventListener('submit', registrarVendaDelivery);
    document.getElementById('form-adicionar-produto').addEventListener('submit', adicionarProduto);
    document.getElementById('form-adicionar-receita').addEventListener('submit', adicionarReceita);
    document.getElementById('form-adicionar-despesa').addEventListener('submit', adicionarDespesa);

    // Carrega os dados iniciais
    carregarVendasDiarias();
    carregarEstoque();
});