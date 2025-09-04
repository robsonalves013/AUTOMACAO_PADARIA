import datetime
import json
import os
import locale
import sys

# Configura o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

class BakeryData:
    """Gerencia o carregamento, salvamento e manipulação de dados."""
    def __init__(self, data_dir="relatorios_padaria"):
        self.data_dir = data_dir
        self.data_path = os.path.join(self.data_dir, 'dados_padaria.json')
        self.receitas, self.despesas, self.estoque = self._load_data()

    def _load_data(self):
        """Carrega os dados de um arquivo JSON. Se não existir, cria um novo."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return dados['receitas'], dados['despesas'], dados['estoque']
        except (FileNotFoundError, json.JSONDecodeError):
            print("Arquivo de dados não encontrado ou corrompido. Criando um novo com dados de exemplo...")
            self._save_data({}, [], []) # Salva um arquivo vazio para iniciar
            return [], [], self._create_example_stock()

    def _save_data(self, receitas=None, despesas=None, estoque=None):
        """Salva os dados em um arquivo JSON."""
        dados = {
            'receitas': receitas if receitas is not None else self.receitas,
            'despesas': despesas if despesas is not None else self.despesas,
            'estoque': estoque if estoque is not None else self.estoque
        }
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar os dados: {e}")
            return False

    def _create_example_stock(self):
        return {
            '123456789': {'descricao': 'pão francês', 'quantidade': 100, 'valor_unitario': 0.50, 'categoria': 'Pães'},
            '987654321': {'descricao': 'pão de queijo', 'quantidade': 50, 'valor_unitario': 3.00, 'categoria': 'Pães'},
            '456789123': {'descricao': 'bolo de chocolate', 'quantidade': 10, 'valor_unitario': 25.00, 'categoria': 'Doces'},
        }

    def add_product(self, codigo, descricao, quantidade, valor_unitario, categoria):
        """Adiciona ou atualiza um produto no estoque."""
        if codigo in self.estoque:
            self.estoque[codigo]['quantidade'] += quantidade
            message = "Produto atualizado com sucesso!"
        else:
            self.estoque[codigo] = {
                'descricao': descricao.lower(),
                'quantidade': quantidade,
                'valor_unitario': valor_unitario,
                'categoria': categoria
            }
            message = "Produto adicionado com sucesso!"
        self._save_data()
        return message

    def register_sale(self, codigo, quantidade, sale_type, details):
        """Registra uma venda."""
        if codigo not in self.estoque or self.estoque[codigo]['quantidade'] < quantidade:
            return "Estoque insuficiente ou produto não encontrado."

        valor_unitario = self.estoque[codigo]['valor_unitario']
        self.estoque[codigo]['quantidade'] -= quantidade
        valor_total = quantidade * valor_unitario

        entry = {
            'descricao': f"Venda de {quantidade} und. de {self.estoque[codigo]['descricao']}",
            'valor': valor_total,
            'data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'tipo': 'receita',
            'forma_pagamento': details.get('forma_pagamento', 'N/A'),
            'plataforma_delivery': details.get('plataforma_delivery', 'N/A')
        }
        self.receitas.append(entry)
        self._save_data()
        return f"Venda de {valor_total:,.2f} registrada com sucesso!"

    def add_income(self, descricao, valor, details):
        """Adiciona uma receita manual."""
        entry = {
            'descricao': descricao,
            'valor': valor,
            'data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'tipo': 'receita',
            'forma_pagamento': details.get('forma_pagamento', 'Manual')
        }
        self.receitas.append(entry)
        self._save_data()
        return "Receita adicionada com sucesso!"

    def add_expense(self, descricao, valor):
        """Adiciona uma despesa manual."""
        entry = {
            'descricao': descricao,
            'valor': valor,
            'data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'tipo': 'despesa'
        }
        self.despesas.append(entry)
        self._save_data()
        return "Despesa adicionada com sucesso!"