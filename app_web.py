from flask import Flask, jsonify, request
from flask_cors import CORS
from baker_logic import BakeryData

app = Flask(__name__)
CORS(app)

db = BakeryData()

@app.route('/estoque', methods=['GET'])
def get_estoque():
    """Endpoint para a API web buscar o estoque atual."""
    return jsonify(db.estoque)

@app.route('/estoque/add', methods=['POST'])
def add_produto():
    """Endpoint para adicionar/atualizar um produto via API."""
    data = request.json
    codigo = data.get('codigo')
    descricao = data.get('descricao')
    quantidade = data.get('quantidade')
    valor_unitario = data.get('valor_unitario')
    categoria = data.get('categoria')

    if not all([codigo, descricao, quantidade, valor_unitario]):
        return jsonify({"error": "Dados incompletos"}), 400

    message = db.add_product(codigo, descricao, quantidade, valor_unitario, categoria)
    return jsonify({"message": message})

@app.route('/vendas/direta', methods=['POST'])
def post_venda_direta():
    """Endpoint para registrar uma venda direta via API."""
    data = request.json
    codigo = data.get('codigo')
    quantidade = data.get('quantidade')
    forma_pagamento = data.get('forma_pagamento')

    if not all([codigo, quantidade, forma_pagamento]):
        return jsonify({"error": "Dados de venda incompletos"}), 400
    
    message = db.register_sale(codigo, quantidade, 'direta', {'forma_pagamento': forma_pagamento})
    if "Estoque" in message:
        return jsonify({"error": message}), 400

    return jsonify({"message": message})


@app.route('/vendas/delivery', methods=['POST'])
def post_venda_delivery():
    """Endpoint para registrar uma venda delivery via API."""
    data = request.json
    codigo = data.get('codigo')
    quantidade = data.get('quantidade')
    plataforma = data.get('plataforma')

    if not all([codigo, quantidade, plataforma]):
        return jsonify({"error": "Dados de venda incompletos"}), 400

    message = db.register_sale(codigo, quantidade, 'delivery', {'plataforma_delivery': plataforma})
    if "Estoque" in message:
        return jsonify({"error": message}), 400

    return jsonify({"message": message})

@app.route('/vendas/diarias', methods=['GET'])
def get_vendas_diarias():
    """Endpoint para buscar as vendas diárias."""
    return jsonify(db.receitas)

@app.route('/fluxo_caixa/receita', methods=['POST'])
def add_receita_api():
    """Endpoint para adicionar uma receita manual via API."""
    data = request.json
    descricao = data.get('descricao')
    valor = data.get('valor')

    if not all([descricao, valor]):
        return jsonify({"error": "Dados de receita incompletos"}), 400

    message = db.add_income(descricao, valor, {'forma_pagamento': 'Manual'})
    return jsonify({"message": message})

@app.route('/fluxo_caixa/despesa', methods=['POST'])
def add_despesa_api():
    """Endpoint para adicionar uma despesa via API."""
    data = request.json
    descricao = data.get('descricao')
    valor = data.get('valor')

    if not all([descricao, valor]):
        return jsonify({"error": "Dados de despesa incompletos"}), 400

    message = db.add_expense(descricao, valor)
    return jsonify({"message": message})

@app.route('/vendas/cancelar', methods=['POST'])
def cancelar_venda():
    """Endpoint para cancelar uma venda com senha master."""
    data = request.json
    venda_id = data.get('id')
    senha_master = data.get('senha')
    
    # SENHA MASTER PARA DEMONSTRAÇÃO. EM PRODUÇÃO, USE UM MÉTODO MAIS SEGURO!
    MASTER_PASSWORD = "120724"

    if senha_master != MASTER_PASSWORD:
        return jsonify({"error": "Senha master incorreta"}), 403 # 403 Forbidden

    venda_encontrada = False
    for i, receita in enumerate(db.receitas):
        if str(receita['id']) == str(venda_id):
            db.receitas[i]['status'] = "Cancelada"
            venda_encontrada = True
            break
    
    if venda_encontrada:
        return jsonify({"message": "Venda cancelada com sucesso!"})
    else:
        return jsonify({"error": "Venda não encontrada"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)