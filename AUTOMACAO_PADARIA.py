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

# --- CÓDIGO DA API FLASK ---
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

# Diretório para salvar os arquivos e subpastas
DIRETORIO_DADOS = "relatorios_padaria"
ASSINATURA = "Sistema desenvolvido por ROBSON ALVES"

# --- Configurações do e-mail (ATUALIZAR COM SUAS INFORMAÇÕES) ---
EMAIL_REMETENTE = 'robtechservice@outlook.com'
# **ATENÇÃO: Mude para a senha de aplicativo gerada no Outlook.**
# Vá nas configurações de segurança da sua conta Microsoft para gerar a senha.
SENHA_APP = 'ioohmnnkugrsulss' 

# ----------------------------------------
# --- FUNÇÕES DE LÓGICA DO NEGÓCIO ---
# ----------------------------------------
def formatar_texto(texto, cor=RESET, estilo=RESET):
    """Função centralizada para formatar texto com cores e estilos."""
    return f"{estilo}{cor}{texto}{RESET}"

def verificar_diretorio():
    """Cria o diretório de dados se ele não existir."""
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

def carregar_dados():
    """Carrega os dados de um arquivo JSON. Se não existir, cria um com dados de exemplo."""
    verificar_diretorio()
    caminho_arquivo = os.path.join(DIRETORIO_DADOS, 'dados_padaria.json')
    try:
        with open(caminho_arquivo, 'r') as f:
            dados = json.load(f)
            return dados['receitas'], dados['despesas'], dados['estoque']
    except FileNotFoundError:
        print(formatar_texto("Arquivo de dados não encontrado. Criando um novo com dados de exemplo...", cor=AMARELO))
        receitas_exemplo = []
        despesas_exemplo = []
        estoque_exemplo = {
            '123456789': {'descricao': 'pão francês', 'quantidade': 100, 'valor_unitario': 0.50, 'categoria': 'Pães'},
            '987654321': {'descricao': 'pão de queijo', 'quantidade': 50, 'valor_unitario': 3.00, 'categoria': 'Pães'},
            '456789123': {'descricao': 'bolo de chocolate', 'quantidade': 10, 'valor_unitario': 25.00, 'categoria': 'Doces'},
            '789123456': {'descricao': 'torta de limão', 'quantidade': 8, 'valor_unitario': 30.00, 'categoria': 'Doces'},
            '111222333': {'descricao': 'café expresso', 'quantidade': 100, 'valor_unitario': 4.50, 'categoria': 'Bebidas'},
            '444555666': {'descricao': 'suco de laranja', 'quantidade': 20, 'valor_unitario': 6.00, 'categoria': 'Bebidas'}
        }
        salvar_dados(receitas_exemplo, despesas_exemplo, estoque_exemplo)
        return receitas_exemplo, despesas_exemplo, estoque_exemplo

def salvar_dados(receitas, despesas, estoque):
    """Salva os dados em um arquivo JSON e exibe uma mensagem de sucesso."""
    verificar_diretorio()
    caminho_arquivo = os.path.join(DIRETORIO_DADOS, 'dados_padaria.json')
    dados = {
        'receitas': receitas,
        'despesas': despesas,
        'estoque': estoque
    }
    try:
        with open(caminho_arquivo, 'w') as f:
            json.dump(dados, f, indent=4)
        print(formatar_texto("Dados salvos com sucesso!", cor=VERDE))
    except Exception as e:
        print(formatar_texto(f"Erro ao salvar os dados: {e}", cor=VERMELHO))

def adicionar_produto_estoque(estoque):
    """Permite adicionar ou atualizar um produto no estoque via terminal."""
    codigo = input("Digite o código do produto (código de barras): ")
    descricao = input("Digite a descrição do produto: ")
    try:
        quantidade = int(input("Digite a quantidade a ser adicionada: "))
        valor_unitario = float(input("Digite o valor unitário: "))
    except ValueError:
        print(formatar_texto("Entrada inválida para quantidade ou valor. Tente novamente.", cor=VERMELHO))
        return
    categoria = input("Digite a categoria do produto: ")

    if codigo in estoque:
        estoque[codigo]['quantidade'] += quantidade
        print(formatar_texto("Produto atualizado com sucesso!", cor=VERDE))
    else:
        estoque[codigo] = {
            'descricao': descricao.lower(),
            'quantidade': quantidade,
            'valor_unitario': valor_unitario,
            'categoria': categoria
        }
        print(formatar_texto("Produto adicionado com sucesso!", cor=VERDE))

def registrar_venda_direta(receitas, estoque):
    """Registra uma venda direta a partir do terminal."""
    codigo = input("Digite o código do produto vendido: ")
    try:
        quantidade = int(input("Digite a quantidade vendida: "))
    except ValueError:
        print(formatar_texto("Quantidade inválida. Tente novamente.", cor=VERMELHO))
        return

    if codigo not in estoque or estoque[codigo]['quantidade'] < quantidade:
        print(formatar_texto("Estoque insuficiente ou produto não encontrado.", cor=VERMELHO))
        return

    forma_pagamento = input("Digite a forma de pagamento (ex: 'Cartão', 'Dinheiro', 'PIX'): ")
    
    valor_unitario = estoque[codigo]['valor_unitario']
    valor_total = quantidade * valor_unitario
    
    estoque[codigo]['quantidade'] -= quantidade
    
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    receitas.append({
        'descricao': f"Venda de {quantidade} und. de {estoque[codigo]['descricao']}",
        'valor': valor_total,
        'data': agora,
        'tipo': 'receita',
        'forma_pagamento': forma_pagamento
    })
    
    print(formatar_texto(f"Venda de {valor_total:,.2f} registrada com sucesso!", cor=VERDE))

def registrar_venda_delivery(receitas, estoque):
    """Registra uma venda por delivery a partir do terminal."""
    codigo = input("Digite o código do produto vendido: ")
    try:
        quantidade = int(input("Digite a quantidade vendida: "))
    except ValueError:
        print(formatar_texto("Quantidade inválida. Tente novamente.", cor=VERMELHO))
        return

    if codigo not in estoque or estoque[codigo]['quantidade'] < quantidade:
        print(formatar_texto("Estoque insuficiente ou produto não encontrado.", cor=VERMELHO))
        return
        
    plataforma = input("Digite a plataforma de delivery (ex: 'iFood', 'Rappi'): ")
    
    valor_unitario = estoque[codigo]['valor_unitario']
    valor_total = quantidade * valor_unitario
    
    estoque[codigo]['quantidade'] -= quantidade
    
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    receitas.append({
        'descricao': f"Venda de {quantidade} und. de {estoque[codigo]['descricao']} (Delivery)",
        'valor': valor_total,
        'data': agora,
        'tipo': 'receita',
        'plataforma_delivery': plataforma
    })
    
    print(formatar_texto(f"Venda por delivery de {valor_total:,.2f} registrada com sucesso!", cor=VERDE))

def adicionar_receita(receitas):
    """Adiciona uma receita manual ao fluxo de caixa."""
    descricao = input("Descrição da receita: ")
    try:
        valor = float(input("Valor da receita: "))
    except ValueError:
        print(formatar_texto("Valor inválido. Tente novamente.", cor=VERMELHO))
        return

    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    receitas.append({
        'descricao': descricao,
        'valor': valor,
        'data': agora,
        'tipo': 'receita',
        'forma_pagamento': 'Manual'
    })
    print(formatar_texto("Receita adicionada com sucesso!", cor=VERDE))

def adicionar_despesa(despesas):
    """Adiciona uma despesa manual ao fluxo de caixa."""
    descricao = input("Descrição da despesa: ")
    try:
        valor = float(input("Valor da despesa: "))
    except ValueError:
        print(formatar_texto("Valor inválido. Tente novamente.", cor=VERMELHO))
        return

    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    despesas.append({
        'descricao': descricao,
        'valor': valor,
        'data': agora,
        'tipo': 'despesa'
    })
    print(formatar_texto("Despesa adicionada com sucesso!", cor=VERDE))

# ----------------------------------------
# --- FUNÇÕES DE API (FLASK) ---
# ----------------------------------------
app = Flask(__name__)
CORS(app)

@app.route('/estoque', methods=['GET'])
def get_estoque():
    """Endpoint para a API web buscar o estoque atual."""
    receitas, despesas, estoque = carregar_dados()
    return jsonify(estoque)

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

    receitas, despesas, estoque = carregar_dados()
    if codigo in estoque:
        estoque[codigo]['quantidade'] += quantidade
        estoque[codigo]['valor_unitario'] = valor_unitario
        estoque[codigo]['categoria'] = categoria
        message = "Produto atualizado com sucesso!"
    else:
        estoque[codigo] = {
            'descricao': descricao.lower(),
            'quantidade': quantidade,
            'valor_unitario': valor_unitario,
            'categoria': categoria
        }
        message = "Produto adicionado com sucesso!"

    salvar_dados(receitas, despesas, estoque)
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

    receitas, despesas, estoque = carregar_dados()
    if codigo not in estoque or estoque[codigo]['quantidade'] < quantidade:
        return jsonify({"error": "Estoque insuficiente ou produto não encontrado"}), 400

    valor_unitario = estoque[codigo]['valor_unitario']
    estoque[codigo]['quantidade'] -= quantidade
    valor_venda = quantidade * valor_unitario

    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    receitas.append({
        'descricao': f"Venda de {quantidade} und. de {estoque[codigo]['descricao']}",
        'valor': valor_venda,
        'data': agora,
        'tipo': 'receita',
        'forma_pagamento': forma_pagamento
    })

    salvar_dados(receitas, despesas, estoque)
    return jsonify({"message": "Venda direta registrada com sucesso!"})

@app.route('/vendas/delivery', methods=['POST'])
def post_venda_delivery():
    """Endpoint para registrar uma venda delivery via API."""
    data = request.json
    codigo = data.get('codigo')
    quantidade = data.get('quantidade')
    plataforma = data.get('plataforma')

    if not all([codigo, quantidade, plataforma]):
        return jsonify({"error": "Dados de venda incompletos"}), 400

    receitas, despesas, estoque = carregar_dados()
    if codigo not in estoque or estoque[codigo]['quantidade'] < quantidade:
        return jsonify({"error": "Estoque insuficiente ou produto não encontrado"}), 400

    estoque[codigo]['quantidade'] -= quantidade
    salvar_dados(receitas, despesas, estoque)
    return jsonify({"message": "Venda delivery registrada com sucesso!"})

@app.route('/fluxo_caixa/receita', methods=['POST'])
def add_receita_api():
    """Endpoint para adicionar uma receita manual via API."""
    data = request.json
    descricao = data.get('descricao')
    valor = data.get('valor')

    if not all([descricao, valor]):
        return jsonify({"error": "Dados de receita incompletos"}), 400

    receitas, despesas, estoque = carregar_dados()
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    receitas.append({
        'descricao': descricao,
        'valor': valor,
        'data': agora,
        'tipo': 'receita',
        'forma_pagamento': 'Manual'
    })
    salvar_dados(receitas, despesas, estoque)
    return jsonify({"message": "Receita adicionada com sucesso!"})

@app.route('/fluxo_caixa/despesa', methods=['POST'])
def add_despesa_api():
    """Endpoint para adicionar uma despesa via API."""
    data = request.json
    descricao = data.get('descricao')
    valor = data.get('valor')

    if not all([descricao, valor]):
        return jsonify({"error": "Dados de despesa incompletos"}), 400

    receitas, despesas, estoque = carregar_dados()
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    despesas.append({
        'descricao': descricao,
        'valor': valor,
        'data': agora,
        'tipo': 'despesa'
    })
    salvar_dados(receitas, despesas, estoque)
    return jsonify({"message": "Despesa adicionada com sucesso!"})

@app.route('/vendas/diarias', methods=['GET'])
def get_vendas_diarias():
    """Endpoint para a API web buscar as vendas do dia."""
    receitas, _, _ = carregar_dados()
    hoje = datetime.date.today()
    vendas_hoje = [
        item for item in receitas
        if item.get('tipo') == 'receita' and 
           datetime.datetime.strptime(item['data'], "%d/%m/%Y %H:%M:%S").date() == hoje
    ]
    return jsonify(vendas_hoje)

# ----------------------------------------
# --- FUNÇÕES DE RELATÓRIOS E TERMINAL ---
# ----------------------------------------
def limpar_tela():
    """
    Limpa o console de uma forma mais segura usando códigos ANSI.
    Substitui a versão anterior baseada em os.system() para evitar travamentos.
    """
    sys.stdout.write('\033[H\033[J')

def mostrar_logo_inicial():
    """Exibe a mensagem de abertura do script."""
    print("=" * 40)
    print(formatar_texto('SISTEMA DE GESTÃO PARA PADARIA', cor=AZUL, estilo=NEGRITO).center(55))
    print("=" * 40)
    print(formatar_texto(ASSINATURA, cor=AZUL, estilo=NEGRITO).center(55))
    print("=" * 40)

def menu_gerar_relatorio(receitas, despesas, estoque):
    """Menu para seleção de relatórios."""
    while True:
        limpar_tela()
        print(formatar_texto("\n#### Gerar Relatórios ####", cor=AMARELO))
        print("1. Relatório de Fluxo de Caixa (Mensal)")
        print("2. Relatório de Fluxo de Caixa (Geral)")
        print("3. Relatório de Estoque")
        print("4. Relatório de Vendas Diárias")
        print(formatar_texto("5. Voltar ao Menu Principal", cor=AZUL, estilo=NEGRITO))
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            try:
                mes = int(input("Digite o número do mês (1-12): "))
                ano = int(input("Digite o ano (ex: 2024): "))
                if not (1 <= mes <= 12):
                    print("Mês inválido. Por favor, digite um número entre 1 e 12.")
                    input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))
                    continue
                gerar_relatorios_fluxo_caixa(receitas, despesas, mes, ano)
            except ValueError:
                print("Entrada inválida. Por favor, digite números inteiros.")
            input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))
        
        elif escolha == '2':
            gerar_relatorios_fluxo_caixa(receitas, despesas)
            input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))

        elif escolha == '3':
            gerar_relatorios_estoque(estoque)
            input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))

        elif escolha == '4':
            gerar_relatorio_vendas_diarias(receitas, enviar_automatico=False)
            input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))
            
        elif escolha == '5':
            break
            
        else:
            print("Opção inválida. Tente novamente.")
            input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))

def criar_subdiretorio(subpasta):
    """Cria um subdiretório dentro do diretório de dados se ele não existir."""
    caminho_completo = os.path.join(DIRETORIO_DADOS, subpasta)
    if not os.path.exists(caminho_completo):
        os.makedirs(caminho_completo)
    return caminho_completo

def gerar_relatorios_fluxo_caixa(receitas, despesas, mes=None, ano=None):
    """Gera o relatório de fluxo de caixa, podendo ser geral ou mensal."""
    subpasta = "Fluxo_de_Caixa"
    caminho_subpasta = criar_subdiretorio(subpasta)

    if mes and ano:
        receitas_filtradas = [d for d in receitas if datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").month == mes and datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").year == ano]
        despesas_filtradas = [d for d in despesas if datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").month == mes and datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").year == ano]
        titulo_relatorio = f"Relatorio_de_Fluxo_de_Caixa_{mes:02d}-{ano}.xlsx"
    else:
        receitas_filtradas = receitas
        despesas_filtradas = despesas
        titulo_relatorio = "Relatorio_de_Fluxo_de_Caixa_Geral.xlsx"

    df_receitas = pd.DataFrame(receitas_filtradas)
    df_despesas = pd.DataFrame(despesas_filtradas)

    total_receitas = df_receitas['valor'].sum() if not df_receitas.empty else 0
    total_despesas = df_despesas['valor'].sum() if not df_despesas.empty else 0
    saldo = total_receitas - total_despesas
    
    resumo_dados = {
        'Métrica': ['Total de Receitas', 'Total de Despesas', 'Saldo em Caixa'],
        'Valor': [total_receitas, total_despesas, saldo]
    }
    df_resumo = pd.DataFrame(resumo_dados)

    caminho_arquivo = os.path.join(caminho_subpasta, titulo_relatorio)

    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
        if not df_receitas.empty:
            df_receitas.to_excel(writer, sheet_name='Receitas', index=False)
        if not df_despesas.empty:
            df_despesas.to_excel(writer, sheet_name='Despesas', index=False)
    
    formatar_planilha_excel(caminho_arquivo)
    
    try:
        workbook = load_workbook(caminho_arquivo)
        sheet = workbook['Resumo']
        for cell in sheet['B'][1:]:
            cell.number_format = 'R$ #,##0.00'
        
        if saldo >= 0:
            fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        else:
            fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        
        for row in sheet.iter_rows():
            for cell in row:
                if 'Saldo' in str(cell.value):
                    saldo_row_index = cell.row
                    sheet[f'A{saldo_row_index}'].fill = fill
                    sheet[f'B{saldo_row_index}'].fill = fill
        workbook.save(caminho_arquivo)
    except Exception as e:
        print(f"Aviso: Não foi possível formatar a aba de resumo no Excel. Erro: {e}")

    adicionar_assinatura_excel(caminho_arquivo)
    print(f"Relatório '{titulo_relatorio}' gerado com sucesso em '{caminho_arquivo}'")

def formatar_planilha_excel(caminho_arquivo):
    """Formata as planilhas do Excel para melhor visualização."""
    try:
        workbook = load_workbook(caminho_arquivo)
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        cell_value = str(cell.value)
                        if len(cell_value) > max_length:
                            max_length = len(cell_value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            header = [cell.value for cell in worksheet[1]]
            if 'valor' in header or 'Valor' in header:
                try:
                    col_index = header.index('valor') + 1
                except ValueError:
                    col_index = header.index('Valor') + 1
                for row in worksheet.iter_rows(min_row=2, max_col=col_index, max_row=worksheet.max_row):
                    cell = row[col_index - 1]
                    cell.number_format = 'R$ #,##0.00'
        workbook.save(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao formatar o arquivo Excel: {e}")

def adicionar_assinatura_excel(caminho_arquivo):
    """Adiciona a assinatura de desenvolvimento no rodapé de cada planilha."""
    try:
        workbook = load_workbook(caminho_arquivo)
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            worksheet.oddFooter.right.text = ASSINATURA
            worksheet.oddFooter.center.text = "Página &[Page] de &N"
        workbook.save(caminho_arquivo)
    except Exception as e:
        print(formatar_texto(f"Aviso: Não foi possível adicionar a assinatura no relatório. Erro: {e}", cor=VERMELHO))

def gerar_relatorios_estoque(estoque):
    """Gera o relatório de estoque."""
    subpasta = "Estoque"
    caminho_subpasta = criar_subdiretorio(subpasta)
    
    dados_estoque = [{'Código de Barras': codigo, 'Produto': dados.get('descricao', codigo).capitalize(), 'Quantidade': dados['quantidade'], 'Valor Unitário': dados['valor_unitario'], 'Categoria': dados.get('categoria', 'N/A')} for codigo, dados in estoque.items()]
    df_estoque = pd.DataFrame(dados_estoque)
    
    caminho_arquivo = os.path.join(caminho_subpasta, 'Relatorio_de_Estoque.xlsx')
    
    if not df_estoque.empty:
        df_estoque.to_excel(caminho_arquivo, index=False)
        formatar_planilha_excel(caminho_arquivo)
        adicionar_assinatura_excel(caminho_arquivo)
        print(f"Relatório de Estoque gerado com sucesso em '{caminho_arquivo}'")
    else:
        print("O estoque está vazio. Não há dados para gerar o relatório.")

def gerar_relatorio_vendas_diarias(receitas, enviar_automatico=False):
    """Gera um relatório de vendas diárias e, opcionalmente, o envia por e-mail."""
    subpasta = "Vendas_Diarias"
    caminho_subpasta = criar_subdiretorio(subpasta)

    if enviar_automatico:
        data_relatorio_obj = datetime.date.today() - datetime.timedelta(days=1)
        data_relatorio = data_relatorio_obj.strftime("%d/%m/%Y")
        print(f"Gerando relatório automático para o dia {data_relatorio}...")
    else:
        try:
            data_relatorio = input("Digite a data do relatório (DD/MM/AAAA): ")
            data_relatorio_obj = datetime.datetime.strptime(data_relatorio, "%d/%m/%Y").date()
        except ValueError:
            print("Formato de data inválido. Use DD/MM/AAAA.")
            return

    vendas_dia = [
        item for item in receitas
        if item.get('tipo') == 'receita' and 
        datetime.datetime.strptime(item['data'], "%d/%m/%Y %H:%M:%S").date() == data_relatorio_obj
    ]

    if not vendas_dia:
        print(f"Não há vendas registradas para a data {data_relatorio}.")
        if enviar_automatico:
            print(f"E-mail automático não será enviado, pois não há vendas para {data_relatorio}.")
        return

    df_vendas_dia = pd.DataFrame(vendas_dia)
    
    relatorio_agregado = df_vendas_dia.groupby('forma_pagamento')['valor'].sum().reset_index()
    
    total_vendas = relatorio_agregado['valor'].sum()
    relatorio_agregado.loc[len(relatorio_agregado)] = ['Total Geral', total_vendas]

    caminho_arquivo = os.path.join(caminho_subpasta, f"Relatorio_de_Vendas_Diarias_{data_relatorio.replace('/', '-')}.xlsx")

    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        relatorio_agregado.to_excel(writer, sheet_name='Vendas Diárias', index=False)
        df_vendas_dia.to_excel(writer, sheet_name='Detalhes', index=False)

    formatar_planilha_excel(caminho_arquivo)
    adicionar_assinatura_excel(caminho_arquivo)

    print(f"Relatório de vendas diárias para {data_relatorio} gerado com sucesso em '{caminho_arquivo}'")

    if not enviar_automatico:
        enviar_agora = input("Deseja enviar este relatório por e-mail agora? (s/n): ").lower()
        if enviar_agora == 's':
            destinatario = input("Digite o e-mail do destinatário: ")
            assunto = f"Relatório de Vendas Diárias - {data_relatorio}"
            corpo = f"""
Prezado(a),

Segue em anexo o relatório de vendas diárias da padaria referente ao dia {data_relatorio}.

Atenciosamente,
Robson Alves - Gerente
"""
            enviar_email_com_anexo(assunto, corpo, destinatario, caminho_arquivo)

def enviar_email_com_anexo(assunto, corpo, destinatario, caminho_anexo=None):
    """
    Envia um e-mail com anexo.
    Atenção: Requer a configuração de uma senha de app para o e-mail remetente.
    """
    remetente_email = EMAIL_REMETENTE
    remetente_senha = SENHA_APP

    msg = MIMEMultipart()
    msg['From'] = remetente_email
    msg['To'] = destinatario
    msg['Subject'] = assunto

    msg.attach(MIMEText(corpo, 'plain'))

    if caminho_anexo and os.path.exists(caminho_anexo):
        try:
            with open(caminho_anexo, 'rb') as anexo:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(anexo.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(caminho_anexo)}"')
            msg.attach(part)
        except Exception as e:
            print(formatar_texto(f"Aviso: Erro ao anexar o arquivo: {e}", cor=VERMELHO))
    elif caminho_anexo:
        print(formatar_texto(f"Aviso: Arquivo de anexo não encontrado: {caminho_anexo}", cor=VERMELHO))
        
    try:
        # Adicione 'timeout=30' para definir um tempo limite de 30 segundos
        server = smtplib.SMTP_SSL('smtp.outlook.com', 465, timeout=30)
        server.login(remetente_email, remetente_senha)
        server.sendmail(remetente_email, destinatario, msg.as_string())
        server.quit()
        print(formatar_texto(f"E-mail com o relatório enviado para {destinatario} com sucesso.", cor=VERDE))
    except Exception as e:
        print(formatar_texto(f"Erro ao enviar o e-mail: {e}", cor=VERMELHO))
        print("Verifique suas credenciais de e-mail, as configurações de segurança e a conexão com a internet.")
        print(f"Detalhes do erro: {e}")

def mostrar_alerta_popup(itens):
    """Exibe um popup com a lista de itens com estoque baixo."""
    mensagem = "Os seguintes itens precisam de reposição:\n\n"
    mensagem += "\n".join(itens)
    messagebox.showwarning("ALERTA DE ESTOQUE BAIXO", mensagem)

def verificar_e_enviar_alerta_estoque(estoque):
    """
    Verifica o estoque e envia um e-mail de alerta para itens com quantidade baixa.
    Agora também exibe um popup de aviso.
    """
    itens_em_falta = []
    for codigo, dados in estoque.items():
        if dados['quantidade'] <= 10:
            descricao = dados.get('descricao', codigo)
            itens_em_falta.append(f"{descricao.capitalize()} ({dados['quantidade']} unidades)")

    if itens_em_falta:
        # Exibir o popup de alerta
        mostrar_alerta_popup(itens_em_falta)

        # Enviar e-mail de alerta
        destinatario = 'padariamajurak@gmail.com'
        assunto = "ALERTA DE REPOSIÇÃO DE ESTOQUE"
        corpo = f"""
Prezado(a),
Segue a lista de itens que precisam de reposição, pois o estoque está baixo (<= 10 unidades):
{'\n'.join(itens_em_falta)}
Por favor, providencie a reposição o mais breve possível.
Atenciosamente,
Sistema de Gestão
"""
        enviar_email_com_anexo(assunto, corpo, destinatario, None)
    else:
        print("Nenhum alerta de estoque necessário no momento.")

# ----------------------------------------
# --- FUNÇÃO PRINCIPAL (CONSOLE) ---
# ----------------------------------------
def menu_principal():
    """Função principal para o menu do terminal."""
    receitas, despesas, estoque = carregar_dados()
    mostrar_logo_inicial()
    
    while True:
        print(formatar_texto("\n#### MENU PRINCIPAL ####", cor=VERDE))
        print("1. Gerar Relatórios")
        print("2. Registrar Receita")
        print("3. Registrar Despesa")
        print("4. Adicionar/Atualizar Produto no Estoque")
        print("5. Registrar Venda Direta")
        print("6. Registrar Venda Delivery")
        print("7. Verificar Estoque e Enviar Alerta")
        print(formatar_texto("8. Sair", cor=VERMELHO, estilo=NEGRITO))
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            menu_gerar_relatorio(receitas, despesas, estoque)
        elif escolha == '2':
            adicionar_receita(receitas)
        elif escolha == '3':
            adicionar_despesa(despesas)
        elif escolha == '4':
            adicionar_produto_estoque(estoque)
        elif escolha == '5':
            registrar_venda_direta(receitas, estoque)
        elif escolha == '6':
            registrar_venda_delivery(receitas, estoque)
        elif escolha == '7':
            verificar_e_enviar_alerta_estoque(estoque)
        elif escolha == '8':
            print("Salvando dados...")
            salvar_dados(receitas, despesas, estoque)
            print("Encerrando o programa.")
            break
        else:
            print(formatar_texto("Opção inválida. Tente novamente.", cor=VERMELHO))
        
        input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))
        limpar_tela()

if __name__ == "__main__":
    # Inicializa o tkinter em uma janela oculta para permitir o uso de popups
    root = tk.Tk()
    root.withdraw()
    
    # Para rodar a versão de terminal, descomente a linha abaixo.
    menu_principal()

    # Para rodar a versão de API, descomente a linha abaixo e comente a linha acima.
    # app.run(debug=True)