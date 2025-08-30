# APP_AUTOMACAO_PADARIA_GUI.py

import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import locale
import sys
import os
import datetime

# --- Importa todas as suas funções do script original ---
try:
    from AUTOMACAO_PADARIA import carregar_dados, salvar_dados, gerar_relatorios_fluxo_caixa, gerar_relatorios_estoque
except ImportError:
    messagebox.showerror("Erro de Importação", "Não foi possível encontrar o arquivo 'AUTOMACAO_PADARIA.py'. Certifique-se de que ele está no mesmo diretório.")
    sys.exit()

# --- Variáveis Globais (Dados do sistema) ---
receitas, despesas, estoque = carregar_dados()

# Configura o locale para o formato de moeda
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

# --- Funções de Interface Gráfica ---

def limpar_frame(frame):
    """Destrói todos os widgets de um frame para "limpar" a tela."""
    for widget in frame.winfo_children():
        widget.destroy()

def atualizar_dados():
    """Recarrega os dados do arquivo para garantir que a GUI esteja sincronizada."""
    global receitas, despesas, estoque
    receitas, despesas, estoque = carregar_dados()

def mostrar_tela_principal():
    """Cria a janela principal com os botões de menu."""
    limpar_frame(main_frame)
    
    # Título
    titulo = tk.Label(main_frame, text="SISTEMA DE GESTÃO PARA PADARIA", font=("Helvetica", 18, "bold"), fg="blue")
    titulo.pack(pady=40)
    
    # Botões para os menus principais
    btn_estoque = tk.Button(main_frame, text="Gerenciar Estoque", font=("Helvetica", 12, "bold"), command=mostrar_tela_estoque)
    btn_estoque.pack(pady=10, ipadx=60, ipady=10)

    btn_vendas = tk.Button(main_frame, text="Menu de Vendas", font=("Helvetica", 12, "bold"), command=mostrar_tela_vendas)
    btn_vendas.pack(pady=10, ipadx=60, ipady=10)

    btn_fluxo_caixa = tk.Button(main_frame, text="Gerenciar Fluxo de Caixa", font=("Helvetica", 12, "bold"), command=mostrar_tela_fluxo_caixa)
    btn_fluxo_caixa.pack(pady=10, ipadx=60, ipady=10)

    btn_relatorios = tk.Button(main_frame, text="Gerar Relatórios", font=("Helvetica", 12, "bold"), command=mostrar_tela_relatorios)
    btn_relatorios.pack(pady=10, ipadx=60, ipady=10)
    
    # Botão de Sair
    btn_sair = tk.Button(main_frame, text="Sair", font=("Helvetica", 12, "bold"), command=janela_principal.destroy, bg="red", fg="white")
    btn_sair.pack(pady=40, ipadx=60, ipady=10)

# --- Telas de Gerenciamento ---

def mostrar_tela_estoque():
    """Cria a tela para gerenciar o estoque."""
    limpar_frame(main_frame)
    
    tk.Label(main_frame, text="Menu de Estoque", font=("Helvetica", 14, "bold")).pack(pady=20)

    btn_ver_estoque = tk.Button(main_frame, text="Ver Estoque Atual", font=("Helvetica", 12, "bold"), command=ver_estoque_atual_gui)
    btn_ver_estoque.pack(pady=10, ipadx=50, ipady=5)

    btn_adicionar_produto = tk.Button(main_frame, text="Adicionar Produto", font=("Helvetica", 12, "bold"), command=mostrar_tela_adicionar_produto)
    btn_adicionar_produto.pack(pady=10, ipadx=50, ipady=5)
    
    btn_voltar = tk.Button(main_frame, text="Voltar ao Menu Principal", font=("Helvetica", 12, "bold"), command=mostrar_tela_principal)
    btn_voltar.pack(pady=30, ipadx=50, ipady=5)

def mostrar_tela_vendas():
    """Cria a tela para registrar uma nova venda."""
    limpar_frame(main_frame)
    
    tk.Label(main_frame, text="Menu de Vendas", font=("Helvetica", 14, "bold")).pack(pady=20)

    btn_venda_balcao = tk.Button(main_frame, text="Venda no Balcão", font=("Helvetica", 12, "bold"), command=venda_balcao_gui)
    btn_venda_balcao.pack(pady=10, ipadx=50, ipady=5)

    btn_venda_delivery = tk.Button(main_frame, text="Venda por Delivery", font=("Helvetica", 12, "bold"), command=venda_delivery_gui)
    btn_venda_delivery.pack(pady=10, ipadx=50, ipady=5)
    
    btn_voltar = tk.Button(main_frame, text="Voltar ao Menu Principal", font=("Helvetica", 12, "bold"), command=mostrar_tela_principal)
    btn_voltar.pack(pady=30, ipadx=50, ipady=5)

def mostrar_tela_fluxo_caixa():
    """Cria a tela para gerenciar o fluxo de caixa."""
    limpar_frame(main_frame)
    
    tk.Label(main_frame, text="Fluxo de Caixa", font=("Helvetica", 14, "bold")).pack(pady=20)
    
    btn_add_receita = tk.Button(main_frame, text="Adicionar Receita Manual", font=("Helvetica", 12, "bold"), command=adicionar_receita_manual_gui)
    btn_add_receita.pack(pady=10, ipadx=50, ipady=5)

    btn_add_despesa = tk.Button(main_frame, text="Adicionar Despesa", font=("Helvetica", 12, "bold"), command=adicionar_despesa_gui)
    btn_add_despesa.pack(pady=10, ipadx=50, ipady=5)
    
    btn_ver_resumo = tk.Button(main_frame, text="Ver Resumo do Fluxo", font=("Helvetica", 12, "bold"), command=ver_resumo_fluxo_gui)
    btn_ver_resumo.pack(pady=10, ipadx=50, ipady=5)

    btn_voltar = tk.Button(main_frame, text="Voltar ao Menu Principal", font=("Helvetica", 12, "bold"), command=mostrar_tela_principal)
    btn_voltar.pack(pady=30, ipadx=50, ipady=5)

def mostrar_tela_relatorios():
    """Cria a tela para gerar relatórios."""
    limpar_frame(main_frame)
    
    tk.Label(main_frame, text="Gerar Relatórios", font=("Helvetica", 14, "bold")).pack(pady=20)
    
    btn_fluxo_geral = tk.Button(main_frame, text="Fluxo de Caixa Geral (Excel)", font=("Helvetica", 12, "bold"), command=lambda: gerar_relatorios_fluxo_caixa(receitas, despesas))
    btn_fluxo_geral.pack(pady=10, ipadx=50, ipady=5)

    btn_fluxo_mensal = tk.Button(main_frame, text="Fluxo de Caixa Mensal (Excel)", font=("Helvetica", 12, "bold"), command=gerar_relatorio_fluxo_mensal_gui)
    btn_fluxo_mensal.pack(pady=10, ipadx=50, ipady=5)

    btn_estoque = tk.Button(main_frame, text="Relatório de Estoque (Excel)", font=("Helvetica", 12, "bold"), command=lambda: gerar_relatorios_estoque(estoque))
    btn_estoque.pack(pady=10, ipadx=50, ipady=5)
    
    btn_voltar = tk.Button(main_frame, text="Voltar ao Menu Principal", font=("Helvetica", 12, "bold"), command=mostrar_tela_principal)
    btn_voltar.pack(pady=30, ipadx=50, ipady=5)

# --- Funções que interagem com o script original ---

def ver_estoque_atual_gui():
    """Exibe o estoque atual em uma nova janela de texto."""
    janela_ver_estoque = tk.Toplevel(janela_principal)
    janela_ver_estoque.title("Estoque Atual")
    janela_ver_estoque.geometry("500x400")

    texto_estoque = scrolledtext.ScrolledText(janela_ver_estoque, width=60, height=20, font=("Courier", 10))
    texto_estoque.pack(padx=10, pady=10)

    texto_estoque.insert(tk.END, "#### ESTOQUE ATUAL ####\n\n")

    for produto, dados in sorted(estoque.items()):
        quantidade = dados['quantidade']
        valor = locale.currency(dados['valor_unitario'], grouping=True)
        categoria = dados.get('categoria', 'N/A')
        
        texto_produto = f"- {produto.capitalize()} ({categoria}): {quantidade} unidades ({valor} cada)\n"
        
        texto_estoque.insert(tk.END, texto_produto)
        
        if quantidade <= 10:
            texto_estoque.tag_configure("destaque", foreground="red", font=("Courier", 10, "bold"))
            texto_estoque.tag_add("destaque", "end-2c linestart", "end-1c")

    texto_estoque.config(state=tk.DISABLED)

def mostrar_tela_adicionar_produto():
    """Abre uma nova janela para adicionar um produto ao estoque."""
    janela_adicionar = tk.Toplevel(janela_principal)
    janela_adicionar.title("Adicionar Produto")
    janela_adicionar.geometry("350x300")
    
    tk.Label(janela_adicionar, text="Nome do Produto:").pack(pady=5)
    entry_nome = tk.Entry(janela_adicionar)
    entry_nome.pack(pady=5)
    
    tk.Label(janela_adicionar, text="Quantidade:").pack(pady=5)
    entry_quantidade = tk.Entry(janela_adicionar)
    entry_quantidade.pack(pady=5)
    
    tk.Label(janela_adicionar, text="Valor Unitário:").pack(pady=5)
    entry_valor = tk.Entry(janela_adicionar)
    entry_valor.pack(pady=5)
    
    tk.Label(janela_adicionar, text="Categoria:").pack(pady=5)
    entry_categoria = tk.Entry(janela_adicionar)
    entry_categoria.pack(pady=5)
    
    def salvar_produto():
        try:
            produto = entry_nome.get().lower()
            quantidade = int(entry_quantidade.get())
            valor_unitario = float(entry_valor.get())
            categoria = entry_categoria.get().capitalize()
            
            if produto in estoque:
                estoque[produto]['quantidade'] += quantidade
                estoque[produto]['valor_unitario'] = valor_unitario
                estoque[produto]['categoria'] = categoria
            else:
                estoque[produto] = {'quantidade': quantidade, 'valor_unitario': valor_unitario, 'categoria': categoria}
            
            salvar_dados(receitas, despesas, estoque)
            messagebox.showinfo("Sucesso", f"{quantidade} unidades de '{produto.capitalize()}' adicionadas ao estoque.")
            janela_adicionar.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e Valor devem ser números válidos.")
            
    btn_salvar = tk.Button(janela_adicionar, text="Salvar Produto", command=salvar_produto)
    btn_salvar.pack(pady=10)

def adicionar_receita_manual_gui():
    """Adiciona uma receita manual através da GUI."""
    janela_receita = tk.Toplevel(janela_principal)
    janela_receita.title("Adicionar Receita")
    janela_receita.geometry("300x200")
    
    tk.Label(janela_receita, text="Valor:").pack(pady=5)
    entry_valor = tk.Entry(janela_receita)
    entry_valor.pack(pady=5)
    
    tk.Label(janela_receita, text="Descrição:").pack(pady=5)
    entry_descricao = tk.Entry(janela_receita)
    entry_descricao.pack(pady=5)
    
    def salvar():
        try:
            valor = float(entry_valor.get())
            descricao = entry_descricao.get()
            agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            receitas.append({'descricao': descricao, 'valor': valor, 'data': agora, 'tipo': 'receita', 'forma_pagamento': 'Manual'})
            salvar_dados(receitas, despesas, estoque)
            messagebox.showinfo("Sucesso", "Receita adicionada com sucesso!")
            janela_receita.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Digite um número.")
            
    btn_salvar = tk.Button(janela_receita, text="Salvar Receita", command=salvar)
    btn_salvar.pack(pady=10)

def adicionar_despesa_gui():
    """Adiciona uma despesa através da GUI."""
    janela_despesa = tk.Toplevel(janela_principal)
    janela_despesa.title("Adicionar Despesa")
    janela_despesa.geometry("300x200")
    
    tk.Label(janela_despesa, text="Valor:").pack(pady=5)
    entry_valor = tk.Entry(janela_despesa)
    entry_valor.pack(pady=5)
    
    tk.Label(janela_despesa, text="Descrição:").pack(pady=5)
    entry_descricao = tk.Entry(janela_despesa)
    entry_descricao.pack(pady=5)
    
    def salvar():
        try:
            valor = float(entry_valor.get())
            descricao = entry_descricao.get()
            agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            despesas.append({'descricao': descricao, 'valor': valor, 'data': agora, 'tipo': 'despesa'})
            salvar_dados(receitas, despesas, estoque)
            messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso!")
            janela_despesa.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Digite um número.")
            
    btn_salvar = tk.Button(janela_despesa, text="Salvar Despesa", command=salvar)
    btn_salvar.pack(pady=10)

def ver_resumo_fluxo_gui():
    """Exibe o resumo do fluxo de caixa em uma nova janela."""
    janela_resumo = tk.Toplevel(janela_principal)
    janela_resumo.title("Resumo do Fluxo de Caixa")
    janela_resumo.geometry("400x300")

    total_receitas = sum(item['valor'] for item in receitas)
    total_despesas = sum(item['valor'] for item in despesas)
    saldo = total_receitas - total_despesas

    tk.Label(janela_resumo, text="#### Resumo do Fluxo de Caixa ####", font=("Helvetica", 12, "bold")).pack(pady=10)
    
    receitas_formatado = locale.currency(total_receitas, grouping=True)
    despesas_formatado = locale.currency(total_despesas, grouping=True)
    saldo_formatado = locale.currency(saldo, grouping=True)

    tk.Label(janela_resumo, text=f"Total de Receitas: {receitas_formatado}", fg="green").pack(pady=5)
    tk.Label(janela_resumo, text=f"Total de Despesas: {despesas_formatado}", fg="red").pack(pady=5)
    
    saldo_cor = "green" if saldo >= 0 else "red"
    tk.Label(janela_resumo, text=f"Saldo Atual: {saldo_formatado}", fg=saldo_cor, font=("Helvetica", 11, "bold")).pack(pady=10)

def gerar_relatorio_fluxo_mensal_gui():
    """Pede o mês e ano e gera o relatório mensal."""
    mes = simpledialog.askinteger("Mês", "Digite o número do mês (1-12):")
    if mes is None:
        return
    ano = simpledialog.askinteger("Ano", "Digite o ano (ex: 2024):")
    if ano is None:
        return
    
    if 1 <= mes <= 12 and ano > 0:
        gerar_relatorios_fluxo_caixa(receitas, despesas, mes, ano)
        messagebox.showinfo("Sucesso", f"Relatório mensal de {mes}/{ano} gerado com sucesso!")
    else:
        messagebox.showerror("Erro", "Mês ou ano inválido.")

def venda_balcao_gui():
    """Inicia o processo de venda no balcão em uma única janela."""
    limpar_frame(main_frame)
    
    carrinho = {}
    
    tk.Label(main_frame, text="Venda no Balcão", font=("Helvetica", 14, "bold")).pack(pady=10)
    
    # Frame para os widgets de venda
    venda_frame = tk.Frame(main_frame)
    venda_frame.pack(pady=10)

    # Widgets para selecionar produto
    tk.Label(venda_frame, text="Produto:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=5)
    produtos_disponiveis = [produto.capitalize() for produto in estoque.keys()]
    lista_produtos_var = tk.StringVar(venda_frame)
    if produtos_disponiveis:
        lista_produtos_var.set(produtos_disponiveis[0])
        menu_produtos = tk.OptionMenu(venda_frame, lista_produtos_var, *produtos_disponiveis)
        menu_produtos.config(font=("Helvetica", 10))
        menu_produtos.grid(row=0, column=1, padx=5, pady=5)
    else:
        tk.Label(venda_frame, text="Nenhum produto no estoque.").grid(row=0, column=1, padx=5, pady=5)

    tk.Label(venda_frame, text="Quantidade:", font=("Helvetica", 11)).grid(row=1, column=0, padx=5, pady=5)
    entry_quantidade = tk.Entry(venda_frame)
    entry_quantidade.grid(row=1, column=1, padx=5, pady=5)

    btn_adicionar_carrinho = tk.Button(venda_frame, text="Adicionar ao Carrinho", font=("Helvetica", 11, "bold"))
    btn_adicionar_carrinho.grid(row=2, column=0, columnspan=2, pady=10, ipadx=10, ipady=5)

    # Widgets para exibir o carrinho
    tk.Label(main_frame, text="--- Carrinho de Compras ---", font=("Helvetica", 12, "bold")).pack(pady=10)
    lista_produtos_text = scrolledtext.ScrolledText(main_frame, width=40, height=10, font=("Courier", 10))
    lista_produtos_text.pack(pady=5)
    
    total_venda_label = tk.Label(main_frame, text="Total Provisório: R$ 0,00", font=("Helvetica", 12, "bold"))
    total_venda_label.pack(pady=10)

    # Botões de ação
    btn_finalizar = tk.Button(main_frame, text="Finalizar Venda", font=("Helvetica", 12, "bold"))
    btn_finalizar.pack(pady=10, ipadx=50, ipady=5)

    btn_voltar = tk.Button(main_frame, text="Voltar ao Menu Principal", font=("Helvetica", 12, "bold"), command=mostrar_tela_principal)
    btn_voltar.pack(pady=10, ipadx=50, ipady=5)
    
    def atualizar_carrinho():
        lista_produtos_text.delete('1.0', tk.END)
        total_provisorio = 0
        if not carrinho:
            lista_produtos_text.insert(tk.END, "Carrinho vazio.")
        else:
            for produto, dados in carrinho.items():
                valor_item = dados['quantidade'] * estoque[produto]['valor_unitario']
                total_provisorio += valor_item
                lista_produtos_text.insert(tk.END, f"{dados['quantidade']}x {produto.capitalize()} ({locale.currency(valor_item, grouping=True)})\n")
        total_venda_label.config(text=f"Total Provisório: {locale.currency(total_provisorio, grouping=True)}")

    def adicionar_ao_carrinho():
        produto_selecionado = lista_produtos_var.get().lower()
        if not produto_selecionado:
            return messagebox.showerror("Erro", "Selecione um produto.")
        
        try:
            quantidade = int(entry_quantidade.get())
            if quantidade <= 0:
                return messagebox.showerror("Erro", "Quantidade inválida.")
            if quantidade > estoque[produto_selecionado]['quantidade']:
                return messagebox.showerror("Erro", "Estoque insuficiente.")

            if produto_selecionado in carrinho:
                carrinho[produto_selecionado]['quantidade'] += quantidade
            else:
                carrinho[produto_selecionado] = {'quantidade': quantidade}
            
            entry_quantidade.delete(0, tk.END) # Limpa o campo de quantidade
            atualizar_carrinho()
            messagebox.showinfo("Sucesso", f"{quantidade} unidades de '{produto_selecionado.capitalize()}' adicionadas.")
        except (ValueError, TypeError):
            messagebox.showerror("Erro", "Entrada inválida.")

    def finalizar_venda():
        if not carrinho:
            return messagebox.showerror("Erro", "Carrinho vazio.")
        
        metodos = ['Dinheiro', 'Cartão de Débito', 'Cartão de Crédito', 'PIX']
        
        forma_pagamento_idx = simpledialog.askinteger("Forma de Pagamento", "Escolha a forma de pagamento:\n1. Dinheiro\n2. Cartão de Débito\n3. Cartão de Crédito\n4. PIX")
        
        try:
            forma_pagamento = metodos[forma_pagamento_idx-1]
        except (ValueError, IndexError):
            return messagebox.showerror("Erro", "Forma de pagamento inválida.")

        total_venda = sum(dados['quantidade'] * estoque[produto]['valor_unitario'] for produto, dados in carrinho.items())
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Se for dinheiro, calcula troco
        if forma_pagamento == 'Dinheiro':
            try:
                valor_recebido = float(simpledialog.askstring("Dinheiro", "Digite o valor recebido:"))
                troco = valor_recebido - total_venda
                messagebox.showinfo("Troco", f"Troco a ser devolvido: {locale.currency(troco, grouping=True)}")
            except (ValueError, TypeError):
                messagebox.showerror("Erro", "Valor recebido inválido. Troco não calculado.")

        # Registra a receita
        receitas.append({
            'descricao': "Venda Balcão",
            'valor': total_venda,
            'data': agora,
            'tipo': 'receita',
            'forma_pagamento': forma_pagamento
        })

        # Subtrai do estoque
        for produto, dados in carrinho.items():
            estoque[produto]['quantidade'] -= dados['quantidade']
        
        salvar_dados(receitas, despesas, estoque)
        
        messagebox.showinfo("Venda Finalizada", f"Venda de {locale.currency(total_venda, grouping=True)} finalizada com sucesso!")
        mostrar_tela_principal()

    btn_adicionar_carrinho.config(command=adicionar_ao_carrinho)
    btn_finalizar.config(command=finalizar_venda)

def venda_delivery_gui():
    """Inicia o processo de venda de delivery em uma única janela."""
    limpar_frame(main_frame)
    
    carrinho = {}
    
    tk.Label(main_frame, text="Venda por Delivery", font=("Helvetica", 14, "bold")).pack(pady=10)
    
    # Frame para os widgets de venda
    venda_frame = tk.Frame(main_frame)
    venda_frame.pack(pady=10)

    # Widgets para selecionar produto
    tk.Label(venda_frame, text="Produto:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=5)
    produtos_disponiveis = [produto.capitalize() for produto in estoque.keys()]
    lista_produtos_var = tk.StringVar(venda_frame)
    if produtos_disponiveis:
        lista_produtos_var.set(produtos_disponiveis[0])
        menu_produtos = tk.OptionMenu(venda_frame, lista_produtos_var, *produtos_disponiveis)
        menu_produtos.config(font=("Helvetica", 10))
        menu_produtos.grid(row=0, column=1, padx=5, pady=5)
    else:
        tk.Label(venda_frame, text="Nenhum produto no estoque.").grid(row=0, column=1, padx=5, pady=5)

    tk.Label(venda_frame, text="Quantidade:", font=("Helvetica", 11)).grid(row=1, column=0, padx=5, pady=5)
    entry_quantidade = tk.Entry(venda_frame)
    entry_quantidade.grid(row=1, column=1, padx=5, pady=5)

    btn_adicionar_carrinho = tk.Button(venda_frame, text="Adicionar ao Carrinho", font=("Helvetica", 11, "bold"))
    btn_adicionar_carrinho.grid(row=2, column=0, columnspan=2, pady=10, ipadx=10, ipady=5)

    # Widgets para exibir o carrinho
    tk.Label(main_frame, text="--- Itens no Carrinho ---", font=("Helvetica", 12, "bold")).pack(pady=10)
    lista_produtos_text = scrolledtext.ScrolledText(main_frame, width=40, height=10, font=("Courier", 10))
    lista_produtos_text.pack(pady=5)
    
    # Botões de ação
    btn_finalizar = tk.Button(main_frame, text="Finalizar Venda", font=("Helvetica", 12, "bold"))
    btn_finalizar.pack(pady=10, ipadx=50, ipady=5)

    btn_voltar = tk.Button(main_frame, text="Voltar ao Menu Principal", font=("Helvetica", 12, "bold"), command=mostrar_tela_principal)
    btn_voltar.pack(pady=10, ipadx=50, ipady=5)
    
    def atualizar_carrinho_delivery():
        lista_produtos_text.delete('1.0', tk.END)
        if not carrinho:
            lista_produtos_text.insert(tk.END, "Carrinho vazio.")
        else:
            for produto, dados in carrinho.items():
                lista_produtos_text.insert(tk.END, f"{dados['quantidade']}x {produto.capitalize()}\n")

    def adicionar_ao_carrinho_delivery():
        produto_selecionado = lista_produtos_var.get().lower()
        if not produto_selecionado:
            return messagebox.showerror("Erro", "Selecione um produto.")

        try:
            quantidade = int(entry_quantidade.get())
            if quantidade <= 0:
                return messagebox.showerror("Erro", "Quantidade inválida.")
            if quantidade > estoque[produto_selecionado]['quantidade']:
                return messagebox.showerror("Erro", "Estoque insuficiente.")

            if produto_selecionado in carrinho:
                carrinho[produto_selecionado]['quantidade'] += quantidade
            else:
                carrinho[produto_selecionado] = {'quantidade': quantidade}

            entry_quantidade.delete(0, tk.END)
            atualizar_carrinho_delivery()
            messagebox.showinfo("Sucesso", f"{quantidade} unidades de '{produto_selecionado.capitalize()}' adicionadas.")
        except (ValueError, TypeError):
            messagebox.showerror("Erro", "Entrada inválida.")
    
    def finalizar_venda_delivery():
        if not carrinho:
            return messagebox.showerror("Erro", "Carrinho vazio.")
        
        plataformas = ['Ifood', '99food']
        plataforma_escolha = simpledialog.askinteger("Plataforma", "Escolha a plataforma:\n1. Ifood\n2. 99food")
        
        try:
            forma_pagamento = plataformas[plataforma_escolha-1]
        except (ValueError, IndexError):
            return messagebox.showerror("Erro", "Plataforma inválida.")
        
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Registra a receita (valor 0)
        receitas.append({
            'descricao': "Venda Delivery",
            'valor': 0.0,
            'data': agora,
            'tipo': 'receita',
            'forma_pagamento': forma_pagamento
        })

        # Subtrai do estoque
        for produto, dados in carrinho.items():
            estoque[produto]['quantidade'] -= dados['quantidade']
        
        salvar_dados(receitas, despesas, estoque)
        
        messagebox.showinfo("Venda Finalizada", f"Venda de delivery ({forma_pagamento}) registrada com sucesso!")
        mostrar_tela_principal()

    btn_adicionar_carrinho.config(command=adicionar_ao_carrinho_delivery)
    btn_finalizar.config(command=finalizar_venda_delivery)


def iniciar_gui():
    """Função principal que inicia a interface gráfica."""
    global janela_principal, main_frame
    janela_principal = tk.Tk()
    janela_principal.title("Sistema de Gestão - Padaria Majurak")
    
    # Inicia a janela em tela cheia
    janela_principal.state('zoomed')
    
    main_frame = tk.Frame(janela_principal)
    main_frame.pack(fill="both", expand=True)

    # Rodapé com a assinatura
    footer_frame = tk.Frame(janela_principal)
    footer_frame.pack(side="bottom", fill="x")
    assinatura = tk.Label(footer_frame, text="SISTEMA DESENVOLVIDO POR ROBSON ALVES", font=("Arial", 9), fg="black")
    assinatura.pack(pady=5)
    
    mostrar_tela_principal()
    
    janela_principal.mainloop()

if __name__ == "__main__":
    iniciar_gui()