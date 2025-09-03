# Certifique-se de que esta linha está no topo do seu arquivo para permitir a comunicação
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file

# ... (outras importações e código existente) ...

app = Flask(__name__)
# Adicione esta linha para habilitar o CORS, caso ainda não tenha feito
CORS(app) 
receitas, despesas, estoque = {}, {}, {}  # Variáveis globais para armazenar os dados

# ... (outras funções e rotas existentes, como as de carregamento e salvamento de dados) ...

@app.route('/estoque/add', methods=['POST'])
def add_product():
    """Adiciona ou atualiza um produto no estoque."""
    data = request.json
    codigo = data.get('codigo')
    descricao = data.get('descricao')
    quantidade = data.get('quantidade')
    valor_unitario = data.get('valor_unitario')
    categoria = data.get('categoria')

    if not all([codigo, descricao, quantidade, valor_unitario]):
        return jsonify({"error": "Dados incompletos"}), 400

    estoque[codigo] = {
        'descricao': descricao,
        'quantidade': quantidade,
        'valor_unitario': valor_unitario,
        'categoria': categoria
    }
    _save_data()
    return jsonify({"message": "Produto adicionado/atualizado com sucesso!"})

@app.route('/vendas/direta', methods=['POST'])
def registrar_venda_direta():
    """Registra uma venda direta e atualiza o estoque."""
    data = request.json
    codigo = data.get('codigo')
    quantidade = int(data.get('quantidade'))
    forma_pagamento = data.get('forma_pagamento')

    if codigo not in estoque:
        return jsonify({"error": "Produto não encontrado no estoque."}), 404
    
    if estoque[codigo]['quantidade'] < quantidade:
        return jsonify({"error": "Quantidade insuficiente no estoque."}), 400

    valor_total = estoque[codigo]['valor_unitario'] * quantidade
    receita = {
        'descricao': f"Venda direta: {estoque[codigo]['descricao']}",
        'valor': valor_total,
        'data': datetime.datetime.now().isoformat(),
        'tipo': 'venda_direta',
        'forma_pagamento': forma_pagamento,
        'item_codigo': codigo,
        'quantidade': quantidade
    }
    receitas.append(receita)
    
    estoque[codigo]['quantidade'] -= quantidade
    _save_data()
    return jsonify({"message": "Venda direta registrada com sucesso! Estoque atualizado."})


@app.route('/vendas/delivery', methods=['POST'])
def registrar_venda_delivery():
    """Registra uma venda delivery e atualiza o estoque."""
    data = request.json
    codigo = data.get('codigo')
    quantidade = int(data.get('quantidade'))
    plataforma = data.get('plataforma')

    if codigo not in estoque:
        return jsonify({"error": "Produto não encontrado no estoque."}), 404
    
    if estoque[codigo]['quantidade'] < quantidade:
        return jsonify({"error": "Quantidade insuficiente no estoque."}), 400

    valor_total = estoque[codigo]['valor_unitario'] * quantidade
    receita = {
        'descricao': f"Venda delivery: {estoque[codigo]['descricao']} ({plataforma})",
        'valor': valor_total,
        'data': datetime.datetime.now().isoformat(),
        'tipo': 'venda_delivery',
        'plataforma': plataforma,
        'item_codigo': codigo,
        'quantidade': quantidade
    }
    receitas.append(receita)

    estoque[codigo]['quantidade'] -= quantidade
    _save_data()
    return jsonify({"message": "Venda delivery registrada com sucesso! Estoque atualizado."})


@app.route('/fluxo_caixa/receita', methods=['POST'])
def adicionar_receita():
    """Adiciona uma nova receita manual ao fluxo de caixa."""
    data = request.json
    descricao = data.get('descricao')
    valor = float(data.get('valor'))

    if not all([descricao, valor]):
        return jsonify({"error": "Dados de receita incompletos"}), 400

    nova_receita = {
        'descricao': descricao,
        'valor': valor,
        'data': datetime.datetime.now().isoformat(),
        'tipo': 'receita_manual'
    }
    receitas.append(nova_receita)
    _save_data()
    return jsonify({"message": "Receita adicionada com sucesso!"})

@app.route('/fluxo_caixa/despesa', methods=['POST'])
def adicionar_despesa():
    """Adiciona uma nova despesa ao fluxo de caixa."""
    data = request.json
    descricao = data.get('descricao')
    valor = float(data.get('valor'))

    if not all([descricao, valor]):
        return jsonify({"error": "Dados de despesa incompletos"}), 400

    nova_despesa = {
        'descricao': descricao,
        'valor': valor,
        'data': datetime.datetime.now().isoformat(),
        'tipo': 'despesa'
    }
    despesas.append(nova_despesa)
    _save_data()
    return jsonify({"message": "Despesa adicionada com sucesso!"})