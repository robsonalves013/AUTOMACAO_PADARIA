# AUTOMACAO_PADARIA_TERMINAL copy.py
import datetime
import pandas as pd
import json
import locale
import os
import time
import sys
from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins
from collections import defaultdict
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import tkinter as tk
from tkinter import messagebox
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- Códigos ANSI para cores e estilos ---
AMARELO = '\033[93m'
AZUL = '\033[94m'
VERDE = '\033[92m'
VERMELHO = '\033[91m'
RESET = '\033[0m'
NEGRITO = '\033[1m'

# Configura o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

# Diretório para os dados
DATA_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'GestaoPadaria')
ESTOQUE_FILE = os.path.join(DATA_DIR, 'estoque.json')
RECEITAS_FILE = os.path.join(DATA_DIR, 'receitas.json')
DESPESAS_FILE = os.path.join(DATA_DIR, 'despesas.json')
VENDAS_RELATORIO_FILE = os.path.join(DATA_DIR, 'relatorio_vendas.xlsx')
LOG_FILE = os.path.join(DATA_DIR, 'log.txt')

# Cria o diretório se não existir
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Inicializa o Flask e CORS
app = Flask(__name__)
CORS(app)  # Permite requisições de outras origens

# Variáveis globais para dados
estoque = {}
receitas = {}
despesas = {}

# --- FUNÇÕES DE ARQUIVO E LOG ---
def registrar_log(mensagem):
    """Registra uma mensagem com data e hora em um arquivo de log."""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensagem}\n")

def carregar_dados():
    """Carrega os dados do estoque, receitas e despesas dos arquivos JSON."""
    global estoque, receitas, despesas
    try:
        if os.path.exists(ESTOQUE_FILE):
            with open(ESTOQUE_FILE, 'r', encoding='utf-8') as f:
                estoque = json.load(f)
        if os.path.exists(RECEITAS_FILE):
            with open(RECEITAS_FILE, 'r', encoding='utf-8') as f:
                receitas = json.load(f)
        if os.path.exists(DESPESAS_FILE):
            with open(DESPESAS_FILE, 'r', encoding='utf-8') as f:
                despesas = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        registrar_log(f"Erro ao carregar dados: {e}")
        print(f"Erro ao carregar dados: {e}")

def salvar_dados(receitas, despesas, estoque):
    """Salva os dados do estoque, receitas e despesas nos arquivos JSON."""
    try:
        with open(ESTOQUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(estoque, f, indent=4)
        with open(RECEITAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(receitas, f, indent=4)
        with open(DESPESAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(despesas, f, indent=4)
    except IOError as e:
        registrar_log(f"Erro ao salvar dados: {e}")
        print(f"Erro ao salvar dados: {e}")

# --- FUNÇÕES DE UTILIDADE ---
def formatar_texto(texto, cor=RESET, estilo=RESET):
    """Formata o texto com cores e estilos ANSI."""
    return f"{estilo}{cor}{texto}{RESET}"

def formatar_moeda(valor):
    """Formata um valor numérico para o formato de moeda brasileira."""
    try:
        return locale.currency(valor, grouping=True, symbol=True)
    except (TypeError, ValueError):
        return "R$ 0,00"

def gerar_uuid():
    """Gera um UUID v4 (Identificador Universal Único)."""
    return str(uuid.uuid4())

def get_data_atual_formatada():
    """Retorna a data e hora atuais formatadas."""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def obter_dia_atual():
    """Retorna a data atual no formato 'AAAA-MM-DD'."""
    return datetime.date.today().strftime('%Y-%m-%d')

# --- FUNÇÕES DE NEGÓCIO ---
def adicionar_produto_estoque(estoque):
    """Função para adicionar um produto via terminal."""
    while True:
        try:
            print(formatar_texto("\n--- Adicionar Produto ao Estoque ---", cor=AZUL, estilo=NEGRITO))
            codigo = input("Digite o código do produto: ")
            if not codigo:
                print(formatar_texto("Código não pode ser vazio.", cor=VERMELHO))
                continue
            
            descricao = input("Digite a descrição do produto: ").strip().lower()
            if not descricao:
                print(formatar_texto("Descrição não pode ser vazia.", cor=VERMELHO))
                continue

            quantidade_str = input("Digite a quantidade: ")
            if not quantidade_str.isdigit() or int(quantidade_str) <= 0:
                print(formatar_texto("Quantidade inválida.", cor=VERMELHO))
                continue
            quantidade = int(quantidade_str)

            valor_str = input("Digite o valor unitário: ")
            valor_unitario = float(valor_str.replace(',', '.'))
            if valor_unitario <= 0:
                print(formatar_texto("Valor unitário inválido.", cor=VERMELHO))
                continue

            categoria = input("Digite a categoria do produto (ex: pão, bolo, salgado): ").strip().lower()

            if codigo in estoque:
                estoque[codigo]['quantidade'] += quantidade
                print(formatar_texto(f"Quantidade do produto '{descricao}' atualizada para {estoque[codigo]['quantidade']}.", cor=VERDE))
            else:
                estoque[codigo] = {
                    'descricao': descricao,
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'categoria': categoria
                }
                print(formatar_texto(f"Produto '{descricao}' adicionado com sucesso!", cor=VERDE))
            break
        except ValueError:
            print(formatar_texto("Entrada inválida. Por favor, digite um número para a quantidade e o valor.", cor=VERMELHO))

# ... (outras funções, como alterar_produto_estoque, visualizar_estoque, etc.)

# --- ROTAS DA API FLASK ---
@app.route('/')
def home():
    return "API da Gestão de Padaria está no ar!"

@app.route('/estoque', methods=['GET', 'POST'])
def handle_estoque():
    global estoque
    if request.method == 'POST':
        try:
            dados_produto = request.get_json()
            codigo = dados_produto.get('codigo')
            descricao = dados_produto.get('descricao')
            quantidade = int(dados_produto.get('quantidade'))
            valor_unitario = float(dados_produto.get('valor_unitario'))
            categoria = dados_produto.get('categoria')

            if not codigo or not descricao or quantidade is None or valor_unitario is None:
                return jsonify({"error": "Dados inválidos."}), 400

            if codigo in estoque:
                estoque[codigo]['quantidade'] += quantidade
                salvar_dados(receitas, despesas, estoque)
                registrar_log(f"Produto atualizado (API): Cód {codigo}, Desc: {descricao}, Qtd adicionada: {quantidade}")
                return jsonify({"message": "Produto atualizado com sucesso!"}), 200
            else:
                estoque[codigo] = {
                    'descricao': descricao.lower(),
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'categoria': categoria
                }
                salvar_dados(receitas, despesas, estoque)
                registrar_log(f"Produto adicionado (API): Cód {codigo}, Desc: {descricao}, Qtd: {quantidade}")
                return jsonify({"message": "Produto adicionado com sucesso!"}), 201

        except Exception as e:
            registrar_log(f"Erro na API ao adicionar produto: {e}")
            return jsonify({"error": f"Erro interno: {e}"}), 500

    return jsonify(estoque)

@app.route('/vendas_diarias', methods=['GET'])
def get_vendas_diarias():
    """Retorna as vendas do dia atual para a API."""
    dia_atual = obter_dia_atual()
    vendas_dia = receitas.get('vendas', {}).get(dia_atual, {})
    return jsonify(vendas_dia)

# ... (outras rotas da API)

# Função principal (mantida para a interface de terminal)
def main():
    """Função principal para execução da interface de terminal."""
    carregar_dados()
    while True:
        # ... (código do menu do terminal)
        pass

if __name__ == "__main__":
    # Inicia a aplicação Flask em uma thread separada ou no modo de debug
    app.run(debug=True)
    # ou
    # if len(sys.argv) > 1 and sys.argv[1] == 'terminal':
    #     main()
    # else:
    #     print(formatar_texto("Iniciando o servidor Flask...", cor=AZUL))
    #     app.run(debug=True)