import datetime
import pandas as pd
import json
import locale
import os
import time
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from collections import defaultdict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

# --- Códigos ANSI para cores ---
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
EMAIL_REMETENTE = 'robtechservice@outlook.com'  # Troque pelo seu e-mail
SENHA_APP = 'ioohmnnkugrsulss'                  # Troque pela sua senha de app

def verificar_diretorio():
    """Cria o diretório de dados se ele não existir."""
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)
        print(f"Diretório '{DIRETORIO_DADOS}' criado com sucesso.")

def limpar_tela():
    """Limpa o console, compatível com diferentes sistemas operacionais."""
    os.system('cls' if os.name == 'nt' else 'clear')

def carregar_dados():
    """Carrega os dados de um arquivo JSON. Se não existir, cria um com dados de exemplo."""
    verificar_diretorio()
    caminho_arquivo = os.path.join(DIRETORIO_DADOS, 'dados_padaria.json')
    try:
        with open(caminho_arquivo, 'r') as f:
            dados = json.load(f)
            # Adiciona 'descricao' se não existir para compatibilidade
            for key in dados['estoque'].keys():
                if 'descricao' not in dados['estoque'][key]:
                    dados['estoque'][key]['descricao'] = key
            return dados['receitas'], dados['despesas'], dados['estoque']
    except FileNotFoundError:
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
        print("Arquivo de dados não encontrado. Criando um novo com dados de exemplo...")
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
    with open(caminho_arquivo, 'w') as f:
        json.dump(dados, f, indent=4)
    print(f"{VERDE}{NEGRITO}Alteração salva com sucesso.{RESET}")

def mostrar_logo_inicial():
    """Exibe a mensagem de abertura do script."""
    print("=" * 40)
    print(f"{AZUL}{NEGRITO}{'SISTEMA DE GESTÃO PARA PADARIA':^40}{RESET}")
    print("=" * 40)
    print(f"{AZUL}{NEGRITO}{ASSINATURA:^40}{RESET}")
    print("=" * 40)

def mostrar_menu():
    """Exibe o menu de opções para o usuário."""
    print(f"\n{AMARELO}### Menu da Padaria ###{RESET}")
    print("1. Gerenciar Fluxo de Caixa")
    print("2. Gerenciar Estoque")
    print("3. Menu de Vendas")
    print("4. Gerar Relatórios")
    print(f"5. {VERMELHO}{NEGRITO}Sair{RESET}")
    print("-----------------------")

def gerenciar_fluxo_caixa(receitas, despesas, estoque):
    """Gerencia as operações de fluxo de caixa."""
    while True:
        limpar_tela()
        print(f"\n{AMARELO}#### Gerenciar Fluxo de Caixa ####{RESET}")
        print("1. Adicionar Receita (Manual)")
        print("2. Adicionar Despesa")
        print("3. Ver Resumo do Fluxo de Caixa")
        print(f"4. {AZUL}{NEGRITO}Voltar ao Menu Principal{RESET}")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            try:
                valor = float(input("Digite o valor da receita: "))
                descricao = input("Digite a descrição da receita: ")
                agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                receitas.append({'descricao': descricao, 'valor': valor, 'data': agora, 'tipo': 'receita', 'forma_pagamento': 'Manual'})
                salvar_dados(receitas, despesas, estoque)
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
            except ValueError:
                print("Valor inválido. Por favor, digite um número.")
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '2':
            try:
                valor = float(input("Digite o valor da despesa: "))
                descricao = input("Digite a descrição da despesa: ")
                agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                despesas.append({'descricao': descricao, 'valor': valor, 'data': agora, 'tipo': 'despesa'})
                salvar_dados(receitas, despesas, estoque)
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
            except ValueError:
                print("Valor inválido. Por favor, digite um número.")
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '3':
            total_receitas = sum(item['valor'] for item in receitas)
            total_despesas = sum(item['valor'] for item in despesas)
            saldo = total_receitas - total_despesas

            print(f"\n{AMARELO}#### Resumo do Fluxo de Caixa ####{RESET}")
            print("Receitas:")
            for item in sorted(receitas, key=lambda x: datetime.datetime.strptime(x['data'], "%d/%m/%Y %H:%M:%S")):
                valor_formatado = locale.currency(item['valor'], grouping=True)
                pagamento = item.get('forma_pagamento', 'N/A')
                print(f"  - {item['descricao']} ({AZUL}{NEGRITO}{item['data']}{RESET}) - Entrada: {AMARELO}{NEGRITO}{valor_formatado}{RESET} ({pagamento})")
            print("\nDespesas:")
            for item in sorted(despesas, key=lambda x: datetime.datetime.strptime(x['data'], "%d/%m/%Y %H:%M:%S")):
                valor_formatado = locale.currency(item['valor'], grouping=True)
                print(f"  - {item['descricao']} ({AZUL}{NEGRITO}{item['data']}{RESET}) - Saída: {AMARELO}{NEGRITO}{valor_formatado}{RESET}")
            
            saldo_formatado = locale.currency(saldo, grouping=True)
            if saldo >= 0:
                saldo_cor = f"{VERDE}{NEGRITO}{saldo_formatado}{RESET}"
            else:
                saldo_cor = f"{VERMELHO}{NEGRITO}{saldo_formatado}{RESET}"

            print(f"\n{NEGRITO}Total de Receitas: {locale.currency(total_receitas, grouping=True)}{RESET}")
            print(f"{NEGRITO}Total de Despesas: {locale.currency(total_despesas, grouping=True)}{RESET}")
            print(f"{NEGRITO}Saldo Atual:{RESET} {saldo_cor}")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '4':
            break

        else:
            print("Opção inválida. Tente novamente.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def adicionar_multiplos_produtos(receitas, despesas, estoque):
    """Permite adicionar vários produtos ao estoque de uma só vez."""
    print(f"\n{AMARELO}#### Adicionar Múltiplos Produtos ####{RESET}")
    print("Digite 'sair' a qualquer momento para finalizar o cadastro.")

    while True:
        codigo_barras = input("\nCódigo de Barras do produto: ").strip()
        if codigo_barras.lower() == 'sair':
            break

        try:
            descricao = input(f"Descrição do produto (ex: Pão Francês): ")
            quantidade = int(input("Quantidade a adicionar: "))
            if quantidade <= 0:
                print("Quantidade inválida. Tente novamente.")
                continue

            valor_unitario = float(input(f"Valor unitário de '{descricao}': "))
            categoria = input(f"Categoria de '{descricao}': ")

            if codigo_barras in estoque:
                estoque[codigo_barras]['quantidade'] += quantidade
                estoque[codigo_barras]['valor_unitario'] = valor_unitario
                estoque[codigo_barras]['categoria'] = categoria
                estoque[codigo_barras]['descricao'] = descricao.lower()
            else:
                estoque[codigo_barras] = {'descricao': descricao.lower(), 'quantidade': quantidade, 'valor_unitario': valor_unitario, 'categoria': categoria}
            
            print(f"Produto '{descricao}' adicionado/atualizado com sucesso!")
        except ValueError:
            print(f"{VERMELHO}Entrada inválida. Por favor, use números para quantidade e valor.{RESET}")
        
    salvar_dados(receitas, despesas, estoque)
    input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def adicionar_produto_por_codigo(receitas, despesas, estoque):
    """Permite adicionar um novo produto ao estoque usando um leitor de código de barras."""
    limpar_tela()
    print(f"\n{AMARELO}#### Adicionar Produto por Código de Barras ####{RESET}")
    print("Bipe o código de barras do produto ou digite-o manualmente.")
    print("Digite 'sair' a qualquer momento para voltar.")

    codigo_barras = input("\nCódigo de Barras: ").strip()
    if codigo_barras.lower() == 'sair':
        return

    # A chave do dicionário será o próprio código de barras
    if codigo_barras in estoque:
        print(f"\n{VERMELHO}{NEGRITO}Este produto já está cadastrado no estoque!{RESET}")
        descricao_produto = estoque[codigo_barras].get('descricao', 'N/A')
        print(f"Produto: {descricao_produto}")
        print(f"Quantidade atual: {estoque[codigo_barras]['quantidade']}")
        print(f"Valor: {locale.currency(estoque[codigo_barras]['valor_unitario'], grouping=True)}")

        resposta = input("Deseja apenas atualizar a quantidade? (s/n): ").lower()
        if resposta == 's':
            try:
                quantidade_adicional = int(input("Digite a quantidade a ser adicionada: "))
                if quantidade_adicional > 0:
                    estoque[codigo_barras]['quantidade'] += quantidade_adicional
                    salvar_dados(receitas, despesas, estoque)
                    print(f"\n{VERDE}Quantidade atualizada com sucesso!{RESET}")
                else:
                    print(f"{VERMELHO}Quantidade inválida.{RESET}")
            except ValueError:
                print(f"{VERMELHO}Entrada inválida. Por favor, digite um número inteiro.{RESET}")
    else:
        print(f"\n{AZUL}Código de barras '{codigo_barras}' não encontrado. Iniciando novo cadastro...{RESET}")
        try:
            descricao = input("Descrição do produto: ")
            quantidade = int(input("Quantidade inicial em estoque: "))
            valor_unitario = float(input("Valor unitário: "))
            categoria = input("Categoria (ex: Pães, Doces, Bebidas): ")

            estoque[codigo_barras] = {
                'descricao': descricao.lower(),
                'quantidade': quantidade,
                'valor_unitario': valor_unitario,
                'categoria': categoria
            }
            salvar_dados(receitas, despesas, estoque)
            print(f"\n{VERDE}Produto '{descricao}' cadastrado com sucesso!{RESET}")
        except ValueError:
            print(f"{VERMELHO}Entrada inválida. Por favor, use números para quantidade e valor.{RESET}")

    input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def gerenciar_estoque(receitas, despesas, estoque):
    """Gerencia as operações de estoque."""
    while True:
        limpar_tela()
        print(f"\n{AMARELO}#### Gerenciar Estoque ####{RESET}")
        print("1. Adicionar Produto (Entrada Individual)")
        print("2. Adicionar Múltiplos Produtos (Entrada em Lote)")
        print("3. Ver Estoque Atual")
        print("4. Mudar Categoria de Produto")
        print("5. Adicionar Novo Produto (com Código de Barras)")
        print(f"6. {AZUL}{NEGRITO}Voltar ao Menu Principal{RESET}")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            codigo_barras = input("Código de Barras do produto: ").strip()
            if codigo_barras not in estoque:
                print(f"Produto com código '{codigo_barras}' não encontrado. Use a opção 5 para um novo cadastro.")
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
                continue
            
            try:
                quantidade = int(input("Quantidade a adicionar: "))
                valor_unitario = float(input(f"Valor unitário de '{estoque[codigo_barras]['descricao']}': "))
                categoria = input(f"Categoria de '{estoque[codigo_barras]['descricao']}' (ex: Pães, Doces, Bebidas): ")
                
                estoque[codigo_barras]['quantidade'] += quantidade
                estoque[codigo_barras]['valor_unitario'] = valor_unitario
                estoque[codigo_barras]['categoria'] = categoria
                salvar_dados(receitas, despesas, estoque)
                print(f"Entrada de {quantidade} unidades de '{estoque[codigo_barras]['descricao']}' ({categoria}).")
            except ValueError:
                print("Valor ou quantidade inválido. Por favor, digite números.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '2':
            adicionar_multiplos_produtos(receitas, despesas, estoque)

        elif escolha == '3':
            print(f"\n{AMARELO}#### Estoque Atual ####{RESET}")
            if not estoque:
                print("O estoque está vazio.")
            else:
                for codigo, dados in estoque.items():
                    descricao = dados.get('descricao', codigo)
                    valor_unitario_formatado = locale.currency(dados['valor_unitario'], grouping=True)
                    categoria = dados.get('categoria', 'N/A')
                    
                    if dados['quantidade'] <= 10:
                        print(f"- {VERMELHO}{NEGRITO}{descricao.capitalize()}{RESET} ({codigo}) ({categoria}): {dados['quantidade']} unidades ({valor_unitario_formatado} cada)")
                    else:
                        print(f"- {NEGRITO}{descricao.capitalize()}{RESET} ({codigo}) ({categoria}): {dados['quantidade']} unidades ({valor_unitario_formatado} cada)")

            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '4':
            if not estoque:
                print("O estoque está vazio. Não há produtos para mudar de categoria.")
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
                continue
            
            produtos_lista = list(estoque.keys())
            print(f"\n{AMARELO}#### Mudar Categoria de Produto ####{RESET}")
            for i, codigo in enumerate(produtos_lista, 1):
                descricao = estoque[codigo].get('descricao', codigo)
                categoria_atual = estoque[codigo]['categoria']
                print(f"{i}. {descricao.capitalize()} (Código: {codigo}, Categoria atual: {categoria_atual})")
                
            try:
                escolha_produto = int(input("\nEscolha o número do produto que deseja mudar: "))
                if 1 <= escolha_produto <= len(produtos_lista):
                    codigo_selecionado = produtos_lista[escolha_produto - 1]
                    nova_categoria = input(f"Digite a nova categoria para '{estoque[codigo_selecionado]['descricao'].capitalize()}': ")
                    
                    estoque[codigo_selecionado]['categoria'] = nova_categoria
                    salvar_dados(receitas, despesas, estoque)
                    print(f"A categoria de '{estoque[codigo_selecionado]['descricao'].capitalize()}' foi alterada para '{nova_categoria}'.")
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '5':
            adicionar_produto_por_codigo(receitas, despesas, estoque)
        
        elif escolha == '6':
            break

        else:
            print("Opção inválida. Tente novamente.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def registrar_venda_delivery(receitas, despesas, estoque, plataforma):
    """
    Lança uma venda de delivery apenas na contagem do estoque, sem afetar receitas.
    Agora exibe a lista de produtos para seleção.
    """
    while True:
        limpar_tela()
        print(f"\n{AMARELO}#### Venda Delivery ({plataforma}) ####{RESET}")
        
        produtos_por_categoria = defaultdict(list)
        for codigo, dados in estoque.items():
            categoria = dados.get('categoria', 'Outros')
            produtos_por_categoria[categoria].append((codigo, dados))
        
        produtos_flat = []
        if not estoque:
            print("  - Estoque vazio. Não é possível fazer vendas.")
        else:
            item_num = 1
            for categoria, produtos_lista in sorted(produtos_por_categoria.items()):
                print(f"\n{AMARELO}--- {categoria.upper()} ---{RESET}")
                for codigo, dados in produtos_lista:
                    produtos_flat.append(codigo)
                    descricao = dados.get('descricao', 'N/A').capitalize()
                    print(f"  {item_num}. {descricao} ({dados['quantidade']} und.)")
                    item_num += 1
        
        print(f"\n0. {AZUL}{NEGRITO}Finalizar Venda Delivery{RESET}")
        print("\nOu digite o Código de Barras diretamente para vender.")
        
        try:
            escolha = input("\nEscolha um produto (número ou código de barras): ")
            
            if escolha == '0':
                salvar_dados(receitas, despesas, estoque)
                print("Vendas delivery finalizadas.")
                return
            
            produto_selecionado = None
            if escolha.isdigit() and int(escolha) > 0 and int(escolha) <= len(produtos_flat):
                produto_selecionado = produtos_flat[int(escolha) - 1]
            elif escolha in estoque:
                produto_selecionado = escolha
            else:
                print("Opção inválida. Tente novamente.")
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
                continue

            dados_produto = estoque[produto_selecionado]
            descricao_produto = dados_produto.get('descricao', 'N/A').capitalize()
            
            quantidade = int(input(f"Quantas unidades de '{descricao_produto}' foram vendidas? "))
            
            if quantidade <= 0:
                print("Quantidade inválida.")
            elif quantidade <= dados_produto['quantidade']:
                estoque[produto_selecionado]['quantidade'] -= quantidade
                print(f"Venda de {quantidade} unidades de '{descricao_produto}' registrada no estoque ({plataforma}).")
                print(f"Estoque atual: {estoque[produto_selecionado]['quantidade']}.")
                salvar_dados(receitas, despesas, estoque) # Salva a cada venda para evitar perdas
            else:
                print(f"{VERMELHO}Estoque insuficiente para essa venda. Disponível: {dados_produto['quantidade']}{RESET}")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número inteiro.")
            
        input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def gerenciar_vendas(receitas, despesas, estoque):
    """Gerencia as operações de vendas."""
    while True:
        limpar_tela()
        print(f"\n{AMARELO}#### Menu de Vendas ####{RESET}")
        print("1. Venda Direta (Com registro de receita)")
        print("2. Venda Delivery (Apenas controle de estoque)")
        print(f"3. {AZUL}{NEGRITO}Voltar ao Menu Principal{RESET}")
        
        escolha = input("\nEscolha uma opção: ")

        if escolha == '1':
            realizar_venda_direta(receitas, despesas, estoque)
        elif escolha == '2':
            menu_venda_delivery(receitas, despesas, estoque)
        elif escolha == '3':
            break
        else:
            print("Opção inválida. Tente novamente.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def realizar_venda_direta(receitas, despesas, estoque):
    """Função para a venda de balcão (direta), com registro de receita."""
    while True:
        limpar_tela()
        print(f"\n{AMARELO}#### Venda Direta ####{RESET}")
        
        produtos_por_categoria = defaultdict(list)
        for codigo, dados in estoque.items():
            categoria = dados.get('categoria', 'Outros')
            produtos_por_categoria[categoria].append((codigo, dados))
        
        produtos_flat = []
        if not estoque:
            print("  - Estoque vazio. Não é possível fazer vendas.")
        else:
            item_num = 1
            for categoria, produtos_lista in sorted(produtos_por_categoria.items()):
                print(f"\n{AMARELO}--- {categoria.upper()} ---{RESET}")
                for codigo, dados in produtos_lista:
                    produtos_flat.append(codigo)
                    descricao = dados.get('descricao', 'N/A').capitalize()
                    valor_formatado = locale.currency(dados['valor_unitario'], grouping=True)
                    print(f"  {item_num}. {descricao} ({dados['quantidade']} und.) - {valor_formatado} por und.")
                    item_num += 1
        
        print(f"\n0. {AZUL}{NEGRITO}Finalizar Venda{RESET}")
        print("\nOu digite o Código de Barras diretamente para vender.")

        try:
            escolha = input("\nEscolha um produto (número ou código de barras): ")

            if escolha == '0':
                return

            produto_selecionado = None
            if escolha.isdigit() and int(escolha) > 0 and int(escolha) <= len(produtos_flat):
                produto_selecionado = produtos_flat[int(escolha) - 1]
            elif escolha in estoque:
                produto_selecionado = escolha
            else:
                print("Opção inválida. Tente novamente.")
                input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
                continue

            dados_produto = estoque[produto_selecionado]
            descricao_produto = dados_produto.get('descricao', produto_selecionado).capitalize()
            
            quantidade = int(input(f"Quantas unidades de '{descricao_produto}' deseja vender? "))
            
            if quantidade <= 0:
                print("Quantidade inválida.")
            elif quantidade <= estoque[produto_selecionado]['quantidade']:
                print(f"\n{AMARELO}#### Formas de Pagamento ####{RESET}")
                metodos_pagamento = ['Dinheiro', 'Cartão de Débito', 'Cartão de Crédito', 'PIX']
                for i, metodo in enumerate(metodos_pagamento, 1):
                    print(f"  {i}. {metodo}")
                
                escolha_pagamento = int(input("Escolha a forma de pagamento (número): "))
                if 1 <= escolha_pagamento <= len(metodos_pagamento):
                    forma_pagamento = metodos_pagamento[escolha_pagamento - 1]
                    
                    estoque[produto_selecionado]['quantidade'] -= quantidade
                    valor_venda = quantidade * estoque[produto_selecionado]['valor_unitario']

                    if forma_pagamento == 'Dinheiro':
                        try:
                            valor_recebido = float(input(f"Valor recebido do cliente: "))
                            troco = valor_recebido - valor_venda
                            troco_formatado = locale.currency(troco, grouping=True)
                            print(f"{AMARELO}{NEGRITO}Troco a ser devolvido: {troco_formatado}{RESET}")
                        except ValueError:
                            print(f"{VERMELHO}{NEGRITO}Valor recebido inválido. Troco não calculado.{RESET}")
                            
                    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    receitas.append({
                        'descricao': f"Venda de {quantidade} und. de {descricao_produto}",
                        'valor': valor_venda,
                        'data': agora,
                        'tipo': 'receita',
                        'forma_pagamento': forma_pagamento
                    })
                    
                    salvar_dados(receitas, despesas, estoque)
                    valor_venda_formatado = locale.currency(valor_venda, grouping=True)
                    
                    print(f"\n{AMARELO}{NEGRITO}Venda registrada de {quantidade} unidades de '{descricao_produto}' no valor total de {valor_venda_formatado} ({forma_pagamento}).{RESET}")
                    print(f"{AMARELO}{NEGRITO}Estoque atual de '{descricao_produto}': {estoque[produto_selecionado]['quantidade']}{RESET}")
                else:
                    print("Opção de pagamento inválida. Venda cancelada.")
            else:
                print("Estoque insuficiente para essa venda.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
        
        input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def menu_venda_delivery(receitas, despesas, estoque):
    """Sub-menu para vendas delivery."""
    while True:
        limpar_tela()
        print(f"\n{AMARELO}#### Venda Delivery ####{RESET}")
        print("1. Ifood")
        print("2. 99food")
        print(f"3. {AZUL}{NEGRITO}Voltar ao Menu Anterior{RESET}")
        
        escolha = input("\nEscolha uma plataforma: ")
        
        if escolha == '1':
            registrar_venda_delivery(receitas, despesas, estoque, 'Ifood')
        elif escolha == '2':
            registrar_venda_delivery(receitas, despesas, estoque, '99food')
        elif escolha == '3':
            break
        else:
            print("Opção inválida. Tente novamente.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

def enviar_email_com_anexo(assunto, corpo, destinatario, caminho_anexo):
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
                part = MIMEMultipart._Message() # Corrigido o tipo para MIMEMultipart
                part.set_payload(anexo.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(caminho_anexo)}"')
            msg.attach(part)
        except Exception as e:
            print(f"{VERMELHO}Aviso: Erro ao anexar o arquivo: {e}{RESET}")
    elif caminho_anexo:
        print(f"{VERMELHO}Aviso: Arquivo de anexo não encontrado: {caminho_anexo}{RESET}")
        
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(remetente_email, remetente_senha)
        server.sendmail(remetente_email, destinatario, msg.as_string())
        server.quit()
        print(f"{VERDE}E-mail com o relatório enviado para {destinatario} com sucesso.{RESET}")
    except Exception as e:
        print(f"{VERMELHO}Erro ao enviar o e-mail: {e}{RESET}")
        print("Verifique suas credenciais de e-mail e as configurações de segurança.")

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
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
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
            last_row = worksheet.max_row + 2
            worksheet[f'A{last_row}'] = ASSINATURA
            worksheet[f'A{last_row}'].font = Font(size=8, italic=True, color="A0A0A0")
            worksheet[f'A{last_row}'].alignment = Alignment(horizontal='left')
        workbook.save(caminho_arquivo)
    except Exception as e:
        print(f"Aviso: Não foi possível adicionar a assinatura no relatório. Erro: {e}")

def filtrar_dados_por_mes(dados, mes, ano):
    """Filtra uma lista de dicionários por mês e ano."""
    return [d for d in dados if datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").month == mes and datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").year == ano]

def menu_gerar_relatorio(receitas, despesas, estoque):
    """Menu para seleção de relatórios."""
    while True:
        limpar_tela()
        print(f"\n{AMARELO}#### Gerar Relatórios ####{RESET}")
        print("1. Relatório de Fluxo de Caixa (Mensal)")
        print("2. Relatório de Fluxo de Caixa (Geral)")
        print("3. Relatório de Estoque")
        print("4. Relatório de Vendas Diárias")
        print(f"5. {AZUL}{NEGRITO}Voltar ao Menu Principal{RESET}")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            try:
                mes = int(input("Digite o número do mês (1-12): "))
                ano = int(input("Digite o ano (ex: 2024): "))
                if not (1 <= mes <= 12):
                    print("Mês inválido. Por favor, digite um número entre 1 e 12.")
                    input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
                    continue
                gerar_relatorios_fluxo_caixa(receitas, despesas, mes, ano)
            except ValueError:
                print("Entrada inválida. Por favor, digite números inteiros.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
        
        elif escolha == '2':
            gerar_relatorios_fluxo_caixa(receitas, despesas)
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '3':
            gerar_relatorios_estoque(estoque)
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

        elif escolha == '4':
            gerar_relatorio_vendas_diarias(receitas, enviar_automatico=False)
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
            
        elif escolha == '5':
            break
            
        else:
            print("Opção inválida. Tente novamente.")
            input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")

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
        receitas_filtradas = filtrar_dados_por_mes(receitas, mes, ano)
        despesas_filtradas = filtrar_dados_por_mes(despesas, mes, ano)
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

def verificar_e_enviar_alerta_estoque(estoque):
    """
    Verifica o estoque e envia um e-mail de alerta para itens com quantidade baixa.
    O e-mail é enviado se a quantidade de um produto for menor ou igual a 10.
    """
    itens_em_falta = []
    for codigo, dados in estoque.items():
        if dados['quantidade'] <= 10:
            descricao = dados.get('descricao', codigo)
            itens_em_falta.append(f"{descricao.capitalize()} ({dados['quantidade']} unidades)")

    if itens_em_falta:
        destinatario = 'padariamajurak@gmail.com'  # Troque pelo seu e-mail
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

def mostrar_alerta_estoque_baixo(estoque):
    """
    Exibe um alerta visual com a lista de produtos com estoque baixo (<= 10).
    """
    itens_em_falta = []
    for codigo, dados in estoque.items():
        if dados['quantidade'] <= 10:
            descricao = dados.get('descricao', codigo)
            itens_em_falta.append(f"{descricao.capitalize()} ({dados['quantidade']} unidades)")

    if itens_em_falta:
        print(f"\n{VERMELHO}{NEGRITO}======================================={RESET}")
        print(f"{VERMELHO}{NEGRITO}  ATENÇÃO: PRODUTOS COM ESTOQUE BAIXO  {RESET}")
        print(f"{VERMELHO}{NEGRITO}======================================={RESET}")
        for item in itens_em_falta:
            print(f"- {item}")
        print(f"{VERMELHO}{NEGRITO}======================================={RESET}\n")

def main():
    """Função principal que inicia o programa."""
    limpar_tela()
    mostrar_logo_inicial()
    receitas, despesas, estoque = carregar_dados()

    # --- Lógica de Alerta de Estoque ---
    mostrar_alerta_estoque_baixo(estoque)
    hoje = datetime.date.today()
    if hoje.weekday() in [1, 3]:  # 1 = Terça-feira, 3 = Quinta-feira
        print("\nVerificando estoque para alertas por e-mail...")
        verificar_e_enviar_alerta_estoque(estoque)
    # --- Fim da Lógica de Alerta ---
    
    input(f"\n{AZUL}{NEGRITO}Pressione Enter para continuar...{RESET}")
    limpar_tela()

    while True:
        mostrar_menu()
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            gerenciar_fluxo_caixa(receitas, despesas, estoque)
        elif escolha == '2':
            gerenciar_estoque(receitas, despesas, estoque)
        elif escolha == '3':
            gerenciar_vendas(receitas, despesas, estoque)
        elif escolha == '4':
            menu_gerar_relatorio(receitas, despesas, estoque)
        elif escolha == '5':
            limpar_tela()
            print(f"{VERDE}{NEGRITO}Saindo do sistema. Obrigado por usar nosso software!{RESET}")
            break
        else:
            print(f"{VERMELHO}Opção inválida. Tente novamente.{RESET}")
            time.sleep(2)
            limpar_tela()

if __name__ == "__main__":
    main()
