from flask import Flask, jsonify, request
from flask_cors import CORS
from baker_logic import BakeryData
import uuid
import datetime

app = Flask(__name__)
CORS(app)

db = BakeryData()

# SENHA MASTER PARA DEMONSTRAÇÃO. EM PRODUÇÃO, USE UM MÉTODO MAIS SEGURO!
MASTER_PASSWORD = "120724"

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
    
    # Registra a venda na lista de receitas com os detalhes do item
    item_vendido = {
        'id': str(uuid.uuid4()), # id único para cada venda
        'descricao': db.estoque[codigo]['descricao'],
        'valor': db.estoque[codigo]['valor_unitario'] * quantidade,
        'quantidade': quantidade,
        'codigo': codigo,
        'forma_pagamento': forma_pagamento,
        'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'Concluída'
    }
    db.receitas.append(item_vendido)
    
    return jsonify({"message": "Venda registrada com sucesso!"})

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
    
    # Registra a venda na lista de receitas com os detalhes do item
    item_vendido = {
        'id': str(uuid.uuid4()), # id único para cada venda
        'descricao': db.estoque[codigo]['descricao'],
        'valor': db.estoque[codigo]['valor_unitario'] * quantidade,
        'quantidade': quantidade,
        'codigo': codigo,
        'plataforma_delivery': plataforma,
        'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'Concluída'
    }
    db.receitas.append(item_vendido)

    return jsonify({"message": "Venda registrada com sucesso!"})

@app.route('/vendas/diarias', methods=['GET'])
def get_vendas_diarias():
    """Endpoint para buscar as vendas diárias."""
    return jsonify(db.receitas)

@app.route('/vendas/cancelar', methods=['POST'])
def cancelar_venda():
    """Endpoint para cancelar uma venda com senha master."""
    data = request.json
    venda_id = data.get('id')
    senha_master = data.get('senha')
    
    if senha_master != MASTER_PASSWORD:
        return jsonify({"error": "Senha master incorreta"}), 403

    venda_encontrada = False
    for i, receita in enumerate(db.receitas):
        if str(receita['id']) == str(venda_id):
            if receita['status'] == "Cancelada":
                return jsonify({"error": "Esta venda já foi cancelada."}), 400
            
            # 1. Devolver o produto para o estoque
            codigo_produto = receita['codigo']
            quantidade_devolvida = receita['quantidade']
            if codigo_produto in db.estoque:
                db.estoque[codigo_produto]['quantidade'] += quantidade_devolvida
            else:
                return jsonify({"error": "Produto do estoque não encontrado para devolução."}), 404

            # 2. Registrar um ajuste negativo no fluxo de caixa
            valor_venda = receita['valor']
            db.add_expense(f"Cancelamento de venda ID: {venda_id}", valor_venda)

            # 3. Alterar o status da venda para 'Cancelada'
            db.receitas[i]['status'] = "Cancelada"
            venda_encontrada = True
            break
    
    if venda_encontrada:
        return jsonify({"message": "Venda cancelada com sucesso!"})
    else:
        return jsonify({"error": "Venda não encontrada"}), 404

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)