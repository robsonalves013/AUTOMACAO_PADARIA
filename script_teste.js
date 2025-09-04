// script_teste.js
let carrinho = [];
let vendasDiariasData = [];

function mostrarFeedback(containerId, mensagem, tipo) {
    const container = document.getElementById(containerId);
    container.textContent = mensagem;
    container.className = `feedback-container ${tipo}`;
    container.style.display = 'block';
    setTimeout(() => {
        container.style.display = 'none';
    }, 5000);
}

async function carregarEstoque() {
    const tabelaEstoque = document.getElementById('tabela-estoque').getElementsByTagName('tbody')[0];
    tabelaEstoque.innerHTML = '';

    try {
        const response = await fetch('http://127.0.0.1:5000/estoque');
        const estoque = await response.json();

        for (const codigo in estoque) {
            const produto = estoque[codigo];
            const linha = tabelaEstoque.insertRow();
            
            if (produto.quantidade < 10) {
                linha.classList.add('low-stock');
            }
            
            linha.innerHTML = `
                <td>${codigo}</td>
                <td>${produto.descricao}</td>
                <td>${produto.quantidade}</td>
                <td>R$ ${produto.valor_unitario.toFixed(2).replace('.', ',')}</td>
                <td>${produto.categoria}</td>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar o estoque:', error);
        mostrarFeedback('estoque-feedback', 'Erro ao carregar o estoque.', 'erro');
    }
}

// *** Funções de manipulação do carrinho de vendas (mantidas) ***

// Função adicionada para adicionar um novo produto via API
async function adicionarProduto(event) {
    event.preventDefault();

    const form = document.getElementById('form-adicionar-produto');
    const codigo = form.querySelector('#codigo_produto').value;
    const descricao = form.querySelector('#descricao_produto').value;
    const quantidade = form.querySelector('#quantidade_produto').value;
    const valor_unitario = form.querySelector('#valor_produto').value;
    const categoria = form.querySelector('#categoria_produto').value;

    const produto = {
        codigo: codigo,
        descricao: descricao,
        quantidade: parseInt(quantidade),
        valor_unitario: parseFloat(valor_unitario),
        categoria: categoria
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/estoque', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(produto)
        });

        const result = await response.json();

        if (response.ok) {
            mostrarFeedback('estoque-feedback', result.message, 'sucesso');
            form.reset();
            carregarEstoque();
        } else {
            mostrarFeedback('estoque-feedback', `Erro: ${result.error}`, 'erro');
        }
    } catch (error) {
        console.error('Erro ao adicionar produto:', error);
        mostrarFeedback('estoque-feedback', 'Erro ao conectar com a API.', 'erro');
    }
}

// *** Funções de alteração e relatório (mantidas) ***

document.addEventListener('DOMContentLoaded', () => {
    // Vincula a função adicionarProduto ao formulário de cadastro
    document.getElementById('form-adicionar-produto').addEventListener('submit', adicionarProduto);

    // Carrega os dados iniciais
    carregarEstoque();
    // ... outros carregamentos (vendas, receitas, despesas)
});