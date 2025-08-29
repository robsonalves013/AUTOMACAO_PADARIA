# automacao_padaria_transferir_categoria.py

import datetime
import pandas as pd
import json
import locale
import os
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from collections import defaultdict

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

def verificar_diretorio():
    """Cria o diretório de dados se ele não existir."""
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)
        print(f"Diretório '{DIRETORIO_DADOS}' criado com sucesso.")

def carregar_dados():
    """Carrega os dados de um arquivo JSON. Se não existir, cria um com dados de exemplo."""
    verificar_diretorio()
    caminho_arquivo = os.path.join(DIRETORIO_DADOS, 'dados_padaria.json')
    try:
        with open(caminho_arquivo, 'r') as f:
            dados = json.load(f)
            # Adiciona a categoria padrão caso o arquivo exista mas não tenha a categoria
            for item in dados['estoque'].values():
                if 'categoria' not in item:
                    item['categoria'] = 'Outros'
            return dados['receitas'], dados['despesas'], dados['estoque']
    except FileNotFoundError:
        # Dados de exemplo para iniciar o sistema
        receitas_exemplo = []
        despesas_exemplo = []
        estoque_exemplo = {
            'pão francês': {'quantidade': 100, 'valor_unitario': 0.50, 'categoria': 'Pães'},
            'pão de queijo': {'quantidade': 50, 'valor_unitario': 3.00, 'categoria': 'Pães'},
            'bolo de chocolate': {'quantidade': 10, 'valor_unitario': 25.00, 'categoria': 'Doces'},
            'torta de limão': {'quantidade': 8, 'valor_unitario': 30.00, 'categoria': 'Doces'},
            'café expresso': {'quantidade': 100, 'valor_unitario': 4.50, 'categoria': 'Bebidas'},
            'suco de laranja': {'quantidade': 20, 'valor_unitario': 6.00, 'categoria': 'Bebidas'}
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
    print("Alteração salva com sucesso.")

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
                print("Receita adicionada com sucesso!")
            except ValueError:
                print("Valor inválido. Por favor, digite um número.")

        elif escolha == '2':
            try:
                valor = float(input("Digite o valor da despesa: "))
                descricao = input("Digite a descrição da despesa: ")
                agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                despesas.append({'descricao': descricao, 'valor': valor, 'data': agora, 'tipo': 'despesa'})
                salvar_dados(receitas, despesas, estoque)
                print("Despesa adicionada com sucesso!")
            except ValueError:
                print("Valor inválido. Por favor, digite um número.")

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

        elif escolha == '4':
            break

        else:
            print("Opção inválida. Tente novamente.")

def gerenciar_estoque(receitas, despesas, estoque):
    """Gerencia as operações de estoque."""
    while True:
        print(f"\n{AMARELO}#### Gerenciar Estoque ####{RESET}")
        print("1. Adicionar Produto (Entrada)")
        print("2. Ver Estoque Atual")
        print("3. Mudar Categoria de Produto")
        print(f"4. {AZUL}{NEGRITO}Voltar ao Menu Principal{RESET}")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            produto = input("Nome do produto: ").lower()
            try:
                quantidade = int(input("Quantidade a adicionar: "))
                valor_unitario = float(input(f"Valor unitário de '{produto}': "))
                categoria = input(f"Categoria de '{produto}' (ex: Pães, Doces, Bebidas): ")
                
                if produto in estoque:
                    estoque[produto]['quantidade'] += quantidade
                    estoque[produto]['valor_unitario'] = valor_unitario
                    estoque[produto]['categoria'] = categoria
                else:
                    estoque[produto] = {'quantidade': quantidade, 'valor_unitario': valor_unitario, 'categoria': categoria}
                salvar_dados(receitas, despesas, estoque)
                print(f"Entrada de {quantidade} unidades de '{produto}' ({categoria}).")
            except ValueError:
                print("Valor ou quantidade inválido. Por favor, digite números.")

        elif escolha == '2':
            print(f"\n{AMARELO}#### Estoque Atual ####{RESET}")
            if not estoque:
                print("O estoque está vazio.")
            else:
                for produto, dados in estoque.items():
                    valor_unitario_formatado = locale.currency(dados['valor_unitario'], grouping=True)
                    categoria = dados.get('categoria', 'N/A')
                    print(f"- {NEGRITO}{produto.capitalize()}{RESET} ({categoria}): {dados['quantidade']} unidades ({valor_unitario_formatado} cada)")

        elif escolha == '3':
            if not estoque:
                print("O estoque está vazio. Não há produtos para mudar de categoria.")
                continue
            
            produtos_lista = list(estoque.keys())
            print(f"\n{AMARELO}#### Mudar Categoria de Produto ####{RESET}")
            for i, produto in enumerate(produtos_lista, 1):
                categoria_atual = estoque[produto]['categoria']
                print(f"{i}. {produto.capitalize()} (Categoria atual: {categoria_atual})")
                
            try:
                escolha_produto = int(input("\nEscolha o número do produto que deseja mudar: "))
                if 1 <= escolha_produto <= len(produtos_lista):
                    produto_selecionado = produtos_lista[escolha_produto - 1]
                    nova_categoria = input(f"Digite a nova categoria para '{produto_selecionado.capitalize()}': ")
                    
                    estoque[produto_selecionado]['categoria'] = nova_categoria
                    salvar_dados(receitas, despesas, estoque)
                    print(f"A categoria de '{produto_selecionado.capitalize()}' foi alterada para '{nova_categoria}'.")
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")

        elif escolha == '4':
            break

        else:
            print("Opção inválida. Tente novamente.")

def gerenciar_vendas(receitas, despesas, estoque):
    """Gerencia as operações de vendas."""
    while True:
        print(f"\n{AMARELO}#### Menu de Vendas ####{RESET}")
        
        produtos_por_categoria = defaultdict(list)
        for produto, dados in estoque.items():
            categoria = dados.get('categoria', 'Outros')
            produtos_por_categoria[categoria].append((produto, dados))
            
        produtos_flat = []
        if not estoque:
            print("  - Estoque vazio. Não é possível fazer vendas.")
        else:
            item_num = 1
            for categoria, produtos_lista in sorted(produtos_por_categoria.items()):
                print(f"\n{AMARELO}--- {categoria.upper()} ---{RESET}")
                for produto, dados in produtos_lista:
                    produtos_flat.append(produto)
                    valor_formatado = locale.currency(dados['valor_unitario'], grouping=True)
                    print(f"  {item_num}. {produto.capitalize()} ({dados['quantidade']} und.) - {valor_formatado} por und.")
                    item_num += 1
        
        print(f"\n0. {AZUL}{NEGRITO}Voltar ao Menu Principal{RESET}")
        
        try:
            escolha = int(input("\nEscolha um produto (número) para vender ou 0 para voltar: "))
            if escolha == 0:
                break
            
            if 1 <= escolha <= len(produtos_flat):
                produto_selecionado = produtos_flat[escolha - 1]
                
                quantidade = int(input(f"Quantas unidades de '{produto_selecionado.capitalize()}' deseja vender? "))
                
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
                        
                        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        receitas.append({
                            'descricao': f"Venda de {quantidade} und. de {produto_selecionado}",
                            'valor': valor_venda,
                            'data': agora,
                            'tipo': 'receita',
                            'forma_pagamento': forma_pagamento
                        })
                        
                        salvar_dados(receitas, despesas, estoque)
                        valor_venda_formatado = locale.currency(valor_venda, grouping=True)
                        print(f"Venda registrada de {quantidade} unidades de '{produto_selecionado}' no valor total de {valor_venda_formatado} ({forma_pagamento}).")
                        print(f"Estoque atual de '{produto_selecionado}': {estoque[produto_selecionado]['quantidade']}")
                    else:
                        print("Opção de pagamento inválida. Venda cancelada.")
                else:
                    print("Estoque insuficiente para essa venda.")
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

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
            if 'valor' in header:
                col_index = header.index('valor') + 1
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
                    continue
                gerar_relatorios_fluxo_caixa(receitas, despesas, mes, ano)
            except ValueError:
                print("Entrada inválida. Por favor, digite números inteiros.")
        
        elif escolha == '2':
            gerar_relatorios_fluxo_caixa(receitas, despesas)

        elif escolha == '3':
            gerar_relatorios_estoque(estoque)

        elif escolha == '4':
            gerar_relatorio_vendas_diarias(receitas)
            
        elif escolha == '5':
            break
            
        else:
            print("Opção inválida. Tente novamente.")

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
    
    dados_estoque = [{'Produto': produto.capitalize(), 'Quantidade': dados['quantidade'], 'Valor Unitário': dados['valor_unitario'], 'Categoria': dados.get('categoria', 'N/A')} for produto, dados in estoque.items()]
    df_estoque = pd.DataFrame(dados_estoque)
    
    caminho_arquivo = os.path.join(caminho_subpasta, 'Relatorio_de_Estoque.xlsx')
    
    if not df_estoque.empty:
        df_estoque.to_excel(caminho_arquivo, index=False)
        formatar_planilha_excel(caminho_arquivo)
        adicionar_assinatura_excel(caminho_arquivo)
        print(f"Relatório de Estoque gerado com sucesso em '{caminho_arquivo}'")
    else:
        print("O estoque está vazio. Não há dados para gerar o relatório.")

def gerar_relatorio_vendas_diarias(receitas):
    """Gera um relatório de vendas diárias com valores e forma de pagamento."""
    subpasta = "Vendas_Diarias"
    caminho_subpasta = criar_subdiretorio(subpasta)

    try:
        data_relatorio = input("Digite a data do relatório (DD/MM/AAAA): ")
        data_obj = datetime.datetime.strptime(data_relatorio, "%d/%m/%Y").date()
    except ValueError:
        print("Formato de data inválido. Use DD/MM/AAAA.")
        return

    vendas_dia = [
        item for item in receitas
        if item.get('tipo') == 'receita' and 
        datetime.datetime.strptime(item['data'], "%d/%m/%Y %H:%M:%S").date() == data_obj
    ]

    if not vendas_dia:
        print(f"Não há vendas registradas para a data {data_relatorio}.")
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

def main():
    """Função principal que inicia o programa."""
    mostrar_logo_inicial()
    receitas, despesas, estoque = carregar_dados()

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
            print("\n" + "=" * 40)
            print(f"{AZUL}{NEGRITO}{'Obrigado por usar o sistema da padaria. Até logo!':^40}{RESET}")
            print("=" * 40)
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()
