from baker_logic import BakeryData
import sys
import time
import os

# Códigos ANSI para cores e estilos
AMARELO = '\033[93m'
AZUL = '\033[94m'
VERDE = '\033[92m'
VERMELHO = '\033[91m'
RESET = '\033[0m'
NEGRITO = '\033[1m'

# Inicializa a lógica de negócio
db = BakeryData()

def formatar_texto(texto, cor=RESET, estilo=RESET):
    """Função centralizada para formatar texto com cores e estilos."""
    return f"{estilo}{cor}{texto}{RESET}"

def limpar_tela():
    """Limpa o console."""
    sys.stdout.write('\033[H\033[J')

def mostrar_logo_inicial():
    """Exibe a mensagem de abertura do script."""
    assinatura = "Sistema desenvolvido por ROBSON ALVES"
    print("=" * 40)
    print(formatar_texto('SISTEMA DE GESTÃO PARA PADARIA', cor=AZUL, estilo=NEGRITO).center(55))
    print("=" * 40)
    print(formatar_texto(assinatura, cor=AZUL, estilo=NEGRITO).center(55))
    print("=" * 40)

def main_menu():
    """Exibe o menu principal e processa as escolhas do usuário."""
    while True:
        limpar_tela()
        mostrar_logo_inicial()
        print(formatar_texto("\n#### Menu Principal ####", cor=AMARELO))
        print("1. Adicionar ou Atualizar Produto")
        print("2. Registrar Venda Direta")
        print("3. Registrar Venda por Delivery")
        print("4. Adicionar Receita Manual")
        print("5. Adicionar Despesa Manual")
        print(formatar_texto("6. Sair", cor=VERMELHO, estilo=NEGRITO))
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            adicionar_produto_terminal()
        elif escolha == '2':
            registrar_venda_direta_terminal()
        elif escolha == '3':
            registrar_venda_delivery_terminal()
        elif escolha == '4':
            adicionar_receita_terminal()
        elif escolha == '5':
            adicionar_despesa_terminal()
        elif escolha == '6':
            print("Encerrando o programa.")
            break
        else:
            print(formatar_texto("Opção inválida. Tente novamente.", cor=VERMELHO))
        
        input(formatar_texto("\nPressione Enter para continuar...", cor=AZUL, estilo=NEGRITO))

def adicionar_produto_terminal():
    """Adiciona ou atualiza um produto no estoque via terminal."""
    codigo = input("Digite o código do produto (código de barras): ")
    descricao = input("Digite a descrição do produto: ")
    try:
        quantidade = int(input("Digite a quantidade a ser adicionada: "))
        valor_unitario = float(input("Digite o valor unitário: "))
    except ValueError:
        print(formatar_texto("Entrada inválida para quantidade ou valor. Tente novamente.", cor=VERMELHO))
        return
    categoria = input("Digite a categoria do produto: ")
    
    message = db.add_product(codigo, descricao, quantidade, valor_unitario, categoria)
    print(formatar_texto(message, cor=VERDE))

def registrar_venda_direta_terminal():
    """Registra uma venda direta a partir do terminal."""
    codigo = input("Digite o código do produto vendido: ")
    try:
        quantidade = int(input("Digite a quantidade vendida: "))
    except ValueError:
        print(formatar_texto("Quantidade inválida. Tente novamente.", cor=VERMELHO))
        return

    forma_pagamento = input("Digite a forma de pagamento (ex: 'Cartão', 'Dinheiro', 'PIX'): ")
    
    message = db.register_sale(codigo, quantidade, 'direta', {'forma_pagamento': forma_pagamento})
    print(formatar_texto(message, cor=VERDE if "sucesso" in message else VERMELHO))

def registrar_venda_delivery_terminal():
    """Registra uma venda por delivery a partir do terminal."""
    codigo = input("Digite o código do produto vendido: ")
    try:
        quantidade = int(input("Digite a quantidade vendida: "))
    except ValueError:
        print(formatar_texto("Quantidade inválida. Tente novamente.", cor=VERMELHO))
        return
        
    plataforma = input("Digite a plataforma de delivery (ex: 'iFood', 'Rappi'): ")
    
    message = db.register_sale(codigo, quantidade, 'delivery', {'plataforma_delivery': plataforma})
    print(formatar_texto(message, cor=VERDE if "sucesso" in message else VERMELHO))

def adicionar_receita_terminal():
    """Adiciona uma receita manual ao fluxo de caixa."""
    descricao = input("Descrição da receita: ")
    try:
        valor = float(input("Valor da receita: "))
    except ValueError:
        print(formatar_texto("Valor inválido. Tente novamente.", cor=VERMELHO))
        return
    
    message = db.add_income(descricao, valor, {'forma_pagamento': 'Manual'})
    print(formatar_texto(message, cor=VERDE))

def adicionar_despesa_terminal():
    """Adiciona uma despesa manual ao fluxo de caixa."""
    descricao = input("Descrição da despesa: ")
    try:
        valor = float(input("Valor da despesa: "))
    except ValueError:
        print(formatar_texto("Valor inválido. Tente novamente.", cor=VERMELHO))
        return
    
    message = db.add_expense(descricao, valor)
    print(formatar_texto(message, cor=VERDE))

if __name__ == "__main__":
    main_menu()