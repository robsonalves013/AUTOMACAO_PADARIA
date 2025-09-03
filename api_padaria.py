import os
import json
import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# --- Configurações do Flask e dados ---
app = Flask(__name__)
CORS(app)

# Variáveis globais para armazenar os dados em memória
estoque = {}
receitas = []
despesas = []

# --- Funções de Carregamento e Salvamento de Dados ---
def _save_data():
    """Salva os dados de estoque, receitas e despesas em arquivos JSON."""
    with open('estoque.json', 'w', encoding='utf-8') as f:
        json.dump(estoque, f, ensure_ascii=False, indent=4)
    with open('receitas.json', 'w', encoding='utf-8') as f:
        json.dump(receitas, f, ensure_ascii=False, indent=4)
    with open('despesas.json', 'w', encoding='utf-8') as f:
        json.dump(despesas, f, ensure_ascii=False, indent=4)

def _load_data():
    """Carrega os dados dos arquivos JSON, se existirem."""
    global estoque, receitas, despesas
    if os.path.exists('estoque.json'):
        with open('estoque.json', 'r', encoding='utf-8') as f:
            estoque = json.load(f)
    if os.path.exists('receitas.json'):
        with open('receitas.json', 'r', encoding='utf-8') as f:
            receitas = json.load(f)
    if os.path.exists('despesas.json'):
        with open('despesas.json', 'r', encoding='utf-8') as f:
            despesas = json.load(f)

# Carrega os dados na inicialização
_load_data()

# --- Rotas da API ---

@app.route('/')
def home():
    """Serve o arquivo HTML da interface do usuário."""
    return send_file('index.html')

@app.route('/estoque', methods=['GET'])
def get_estoque():
    """Retorna todos os itens do estoque."""
    return jsonify(estoque)

@app.route('/estoque/add', methods=['POST'])
def add_product():
    """Adiciona ou atualiza um produto no estoque."""
    data = request.json
    codigo = data.get('codigo')
    descricao = data.get('descricao')
    quantidade = int(data.get('quantidade'))
    valor_unitario = float(data.get('valor_unitario'))
    categoria = data.get('categoria')

    if not all([codigo, descricao, quantidade, valor_unitario]):
        return jsonify({"error": "Dados incompletos"}), 400

    estoque[codigo] = {
        'descricao': descricao,
        'quantidade': estoque.get(codigo, {}).get('quantidade', 0) + quantidade,
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

@app.route('/fluxo_caixa/resumo', methods=['GET'])
def get_fluxo_caixa():
    """Retorna um resumo do fluxo de caixa."""
    total_receitas = sum(r['valor'] for r in receitas)
    total_despesas = sum(d['valor'] for d in despesas)
    saldo = total_receitas - total_despesas
    
    return jsonify({
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "receitas_detalhes": receitas,
        "despesas_detalhes": despesas
    })

if __name__ == '__main__':
    app.run(debug=True)