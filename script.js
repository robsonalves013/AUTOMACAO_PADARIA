document.addEventListener('DOMContentLoaded', () => {
    const apiURL = 'http://127.0.0.1:5000'; // Endereço da sua API
    
    const formAdicionarProduto = document.getElementById('form-adicionar-produto');
    const tabelaEstoqueBody = document.querySelector('#tabela-estoque tbody');

    // Função para carregar e exibir o estoque na tabela
    async function carregarEstoque() {
        try {
            const response = await fetch(`${apiURL}/estoque`);
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
            alert('Erro ao conectar com a API. Verifique se o servidor está rodando.');
        }
    }

    // Função para lidar com o envio do formulário de adicionar produto
    formAdicionarProduto.addEventListener('submit', async (event) => {
        event.preventDefault(); // Impede o envio padrão do formulário

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
            const response = await fetch(`${apiURL}/estoque/add_unico`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(produtoData),
            });

            const result = await response.json();
            alert(result.message);
            
            // Recarrega o estoque para mostrar a alteração
            carregarEstoque();
            
            // Limpa o formulário
            formAdicionarProduto.reset();
        } catch (error) {
            console.error('Erro ao adicionar o produto:', error);
            alert('Erro ao conectar com a API ou dados inválidos.');
        }
    });

    // Chama a função para carregar o estoque quando a página é carregada
    carregarEstoque();
});