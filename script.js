document.addEventListener('DOMContentLoaded', () => {
    const apiURL = 'http://127.0.0.1:5000'; // Endereço da sua API
    
    // Formulários e elementos existentes
    const formAdicionarProduto = document.getElementById('form-adicionar-produto');
    const tabelaEstoqueBody = document.querySelector('#tabela-estoque tbody');

    // Novos formulários
    const formVendaDireta = document.getElementById('form-venda-direta');
    const formVendaDelivery = document.getElementById('form-venda-delivery');
    const formAdicionarReceita = document.getElementById('form-adicionar-receita');
    const formAdicionarDespesa = document.getElementById('form-adicionar-despesa');

    // Elementos de feedback
    const vendasFeedback = document.getElementById('vendas-feedback');
    const estoqueFeedback = document.getElementById('estoque-feedback');
    const fluxoCaixaFeedback = document.getElementById('fluxo-caixa-feedback');

    function showFeedback(element, message, isSuccess = true) {
        element.textContent = message;
        element.style.color = isSuccess ? 'green' : 'red';
        setTimeout(() => {
            element.textContent = '';
        }, 5000); // A mensagem desaparece após 5 segundos
    }

    // Função para carregar e exibir o estoque na tabela
    async function carregarEstoque() {
        try {
            const response = await fetch(`${apiURL}/estoque`);
            if (!response.ok) {
                throw new Error('Erro ao carregar o estoque. Status: ' + response.status);
            }
            const estoque = await response.json();
            
            tabelaEstoqueBody.innerHTML = ''; // Limpa a tabela antes de preencher
            
            for (const codigo in estoque) {
                const produto = estoque[codigo];
                const row = document.createElement('tr');
                
                // Adiciona uma classe para produtos com estoque baixo
                if (produto.quantidade <= 10) {
                    row.classList.add('estoque-baixo');
                }
                
                row.innerHTML = `
                    <td>${codigo}</td>
                    <td>${produto.descricao}</td>
                    <td>${produto.quantidade}</td>
                    <td>R$ ${produto.valor_unitario.toFixed(2)}</td>
                    <td>${produto.categoria}</td>
                `;
                tabelaEstoqueBody.appendChild(row);
            }
        } catch (error) {
            console.error('Erro ao carregar o estoque:', error);
            showFeedback(estoqueFeedback, 'Erro ao conectar com a API. Verifique se o servidor está rodando.', false);
        }
    }

    // --- Funções de Submissão de Formulário ---

    // Adicionar/Atualizar Produto
    formAdicionarProduto.addEventListener('submit', async (event) => {
        event.preventDefault();

        const codigo = document.getElementById('codigo').value;
        const descricao = document.getElementById('descricao').value;
        const quantidade = parseInt(document.getElementById('quantidade').value);
        const valorUnitario = parseFloat(document.getElementById('valor_unitario').value);
        const categoria = document.getElementById('categoria').value;

        const produtoData = {
            codigo,
            descricao,
            quantidade,
            valor_unitario: valorUnitario,
            categoria
        };

        try {
            const response = await fetch(`${apiURL}/estoque/add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(produtoData),
            });
            const result = await response.json();
            
            if (response.ok) {
                showFeedback(estoqueFeedback, result.message, true);
                carregarEstoque();
                formAdicionarProduto.reset();
            } else {
                showFeedback(estoqueFeedback, result.error, false);
            }
        } catch (error) {
            console.error('Erro ao adicionar o produto:', error);
            showFeedback(estoqueFeedback, 'Erro ao conectar com a API ou dados inválidos.', false);
        }
    });

    // Venda Direta
    formVendaDireta.addEventListener('submit', async (event) => {
        event.preventDefault();

        const codigo = document.getElementById('venda-direta-codigo').value;
        const quantidade = parseInt(document.getElementById('venda-direta-quantidade').value);
        const formaPagamento = document.getElementById('venda-direta-pagamento').value;

        const vendaData = {
            codigo,
            quantidade,
            forma_pagamento: formaPagamento
        };

        try {
            const response = await fetch(`${apiURL}/vendas/direta`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(vendaData),
            });
            const result = await response.json();
            
            if (response.ok) {
                showFeedback(vendasFeedback, result.message, true);
                carregarEstoque();
                formVendaDireta.reset();
            } else {
                showFeedback(vendasFeedback, result.error, false);
            }
        } catch (error) {
            console.error('Erro ao registrar a venda direta:', error);
            showFeedback(vendasFeedback, 'Erro ao conectar com a API ou dados inválidos.', false);
        }
    });

    // Venda Delivery
    formVendaDelivery.addEventListener('submit', async (event) => {
        event.preventDefault();

        const codigo = document.getElementById('venda-delivery-codigo').value;
        const quantidade = parseInt(document.getElementById('venda-delivery-quantidade').value);
        const plataforma = document.getElementById('venda-delivery-plataforma').value;

        const vendaData = {
            codigo,
            quantidade,
            plataforma
        };

        try {
            const response = await fetch(`${apiURL}/vendas/delivery`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(vendaData),
            });
            const result = await response.json();
            
            if (response.ok) {
                showFeedback(vendasFeedback, result.message, true);
                carregarEstoque();
                formVendaDelivery.reset();
            } else {
                showFeedback(vendasFeedback, result.error, false);
            }
        } catch (error) {
            console.error('Erro ao registrar a venda delivery:', error);
            showFeedback(vendasFeedback, 'Erro ao conectar com a API ou dados inválidos.', false);
        }
    });

    // Adicionar Receita
    formAdicionarReceita.addEventListener('submit', async (event) => {
        event.preventDefault();

        const descricao = document.getElementById('receita-descricao').value;
        const valor = parseFloat(document.getElementById('receita-valor').value);

        const receitaData = {
            descricao,
            valor
        };

        try {
            const response = await fetch(`${apiURL}/fluxo_caixa/receita`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(receitaData),
            });
            const result = await response.json();
            
            if (response.ok) {
                showFeedback(fluxoCaixaFeedback, result.message, true);
                formAdicionarReceita.reset();
            } else {
                showFeedback(fluxoCaixaFeedback, result.error, false);
            }
        } catch (error) {
            console.error('Erro ao adicionar receita:', error);
            showFeedback(fluxoCaixaFeedback, 'Erro ao conectar com a API ou dados inválidos.', false);
        }
    });

    // Adicionar Despesa
    formAdicionarDespesa.addEventListener('submit', async (event) => {
        event.preventDefault();

        const descricao = document.getElementById('despesa-descricao').value;
        const valor = parseFloat(document.getElementById('despesa-valor').value);

        const despesaData = {
            descricao,
            valor
        };

        try {
            const response = await fetch(`${apiURL}/fluxo_caixa/despesa`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(despesaData),
            });
            const result = await response.json();
            
            if (response.ok) {
                showFeedback(fluxoCaixaFeedback, result.message, true);
                formAdicionarDespesa.reset();
            } else {
                showFeedback(fluxoCaixaFeedback, result.error, false);
            }
        } catch (error) {
            console.error('Erro ao adicionar despesa:', error);
            showFeedback(fluxoCaixaFeedback, 'Erro ao conectar com a API ou dados inválidos.', false);
        }
    });

    // Chama a função para carregar o estoque quando a página é carregada
    carregarEstoque();
});