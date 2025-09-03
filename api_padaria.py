import datetime
import pandas as pd
import json
import locale
import os
from flask import Flask, request, jsonify, send_file
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

# --- Application Configuration and Data Management ---
# It's a best practice to use environment variables for sensitive data.
# For production, these values should not be hardcoded.
# Use: export EMAIL_REMETENTE='your_email@outlook.com'
# Use: export SENHA_APP='your_app_password'
EMAIL_REMETENTE = os.environ.get('EMAIL_REMETENTE', 'robtechservice@outlook.com')
SENHA_APP = os.environ.get('SENHA_APP', 'ioohmnnkugrsulss')
DIRETORIO_DADOS = "relatorios_padaria"
ASSINATURA = "Sistema desenvolvido por ROBSON ALVES"
ARQUIVO_DADOS = os.path.join(DIRETORIO_DADOS, 'dados_padaria.json')

app = Flask(__name__)
# Global dictionary to hold all application data.
dados = {}

def verificar_diretorio():
    """Ensures the data directory exists."""
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

def carregar_dados():
    """Loads data from the JSON file. Creates a new one with example data if it doesn't exist."""
    global dados
    verificar_diretorio()
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            # Ensure required keys exist
            dados.setdefault('estoque', {})
            dados.setdefault('receitas', [])
            dados.setdefault('despesas', [])
            # Normalize product descriptions to lowercase for consistency
            for item in dados['estoque'].values():
                if 'descricao' in item:
                    item['descricao'] = item['descricao'].lower()
    except FileNotFoundError:
        print("Arquivo de dados não encontrado. Criando um novo com dados de exemplo.")
        dados = {
            'receitas': [],
            'despesas': [],
            'estoque': {
                '123456789': {'descricao': 'pão francês', 'quantidade': 100, 'valor_unitario': 0.50, 'categoria': 'Pães'},
                '987654321': {'descricao': 'pão de queijo', 'quantidade': 50, 'valor_unitario': 3.00, 'categoria': 'Pães'},
                '456789123': {'descricao': 'bolo de chocolate', 'quantidade': 10, 'valor_unitario': 25.00, 'categoria': 'Doces'},
            }
        }
        salvar_dados()
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return False
    return True

def salvar_dados():
    """Saves data to the JSON file."""
    try:
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4)
        print("Dados salvos com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")

# --- Helper Functions ---
def criar_subdiretorio(subpasta):
    """Creates a subdirectory inside the data directory."""
    caminho_completo = os.path.join(DIRETORIO_DADOS, subpasta)
    if not os.path.exists(caminho_completo):
        os.makedirs(caminho_completo)
    return caminho_completo

def formatar_planilha_excel(caminho_arquivo):
    """Formats Excel worksheets for better readability."""
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
                    except (TypeError, ValueError):
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
    """Adds a developer signature to the footer of each worksheet."""
    try:
        workbook = load_workbook(caminho_arquivo)
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            worksheet.oddFooter.right.text = ASSINATURA
            worksheet.oddFooter.center.text = "Página &[Page] de &N"
        workbook.save(caminho_arquivo)
    except Exception as e:
        print(f"Aviso: Não foi possível adicionar a assinatura no relatório. Erro: {e}")

def enviar_email_com_anexo(assunto, corpo, destinatario, caminho_anexo=None):
    """Sends an email with an attachment."""
    if not EMAIL_REMETENTE or not SENHA_APP:
        print("Aviso: Configurações de e-mail incompletas. Não foi possível enviar o e-mail.")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMETENTE
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
            print(f"Aviso: Erro ao anexar o arquivo: {e}")
            return False
            
    try:
        server = smtplib.SMTP_SSL('smtp.outlook.com', 465)
        server.login(EMAIL_REMETENTE, SENHA_APP)
        server.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
        server.quit()
        print(f"E-mail com o relatório enviado para {destinatario} com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")
        return False

# --- Report Generation Functions (backend logic) ---
def gerar_relatorios_estoque_excel():
    """Generates the stock report and returns the file path."""
    dados_estoque = [{'Código de Barras': codigo, 'Produto': dados['estoque'][codigo].get('descricao', codigo).capitalize(), 'Quantidade': dados['estoque'][codigo]['quantidade'], 'Valor Unitário': dados['estoque'][codigo]['valor_unitario'], 'Categoria': dados['estoque'][codigo].get('categoria', 'N/A')} for codigo in dados['estoque'].keys()]
    if not dados_estoque:
        return None
    subpasta = "Estoque"
    caminho_subpasta = criar_subdiretorio(subpasta)
    df_estoque = pd.DataFrame(dados_estoque)
    caminho_arquivo = os.path.join(caminho_subpasta, 'Relatorio_de_Estoque.xlsx')
    df_estoque.to_excel(caminho_arquivo, index=False)
    formatar_planilha_excel(caminho_arquivo)
    adicionar_assinatura_excel(caminho_arquivo)
    return caminho_arquivo

def gerar_relatorio_fluxo_caixa_excel(mes=None, ano=None):
    """Generates the cash flow report and returns the file path."""
    subpasta = "Fluxo_de_Caixa"
    caminho_subpasta = criar_subdiretorio(subpasta)
    receitas_filtradas = [d for d in dados['receitas'] if (not mes or datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").month == mes) and (not ano or datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").year == ano)]
    despesas_filtradas = [d for d in dados['despesas'] if (not mes or datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").month == mes) and (not ano or datetime.datetime.strptime(d['data'], "%d/%m/%Y %H:%M:%S").year == ano)]
    if mes and ano:
        titulo_relatorio = f"Relatorio_de_Fluxo_de_Caixa_{mes:02d}-{ano}.xlsx"
    else:
        titulo_relatorio = "Relatorio_de_Fluxo_de_Caixa_Geral.xlsx"
    df_receitas = pd.DataFrame(receitas_filtradas)
    df_despesas = pd.DataFrame(despesas_filtradas)
    total_receitas = df_receitas['valor'].sum() if not df_receitas.empty else 0
    total_despesas = df_despesas['valor'].sum() if not df_despesas.empty else 0
    saldo = total_receitas - total_despesas
    resumo_dados = {'Métrica': ['Total de Receitas', 'Total de Despesas', 'Saldo em Caixa'], 'Valor': [total_receitas, total_despesas, saldo]}
    df_resumo = pd.DataFrame(resumo_dados)
    caminho_arquivo = os.path.join(caminho_subpasta, titulo_relatorio)
    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
        if not df_receitas.empty:
            df_receitas.to_excel(writer, sheet_name='Receitas', index=False)
        if not df_despesas.empty:
            df_despesas.to_excel(writer, sheet_name='Despesas', index=False)
    formatar_planilha_excel(caminho_arquivo)
    adicionar_assinatura_excel(caminho_arquivo)
    return caminho_arquivo
    
# --- API Routes ---
@app.route('/')
def home():
    """API test route."""
    return jsonify({"message": "API da Padaria Online!"})

# --- Stock Routes ---
@app.route('/estoque', methods=['GET'])
def listar_estoque():
    """Returns the full stock list."""
    return jsonify(dados['estoque'])

@app.route('/estoque/add', methods=['POST'])
def adicionar_produtos():
    """
    Adds or updates one or more products in stock.
    Payload can be a single product dictionary or a list of them.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Dados incompletos."}), 400
    
    produtos_a_adicionar = [data] if isinstance(data, dict) else data
        
    for prod in produtos_a_adicionar:
        if not all(k in prod for k in ('codigo', 'descricao', 'quantidade', 'valor_unitario')):
            return jsonify({"error": f"Dados de produto incompletos: {prod}"}), 400
            
        codigo = str(prod['codigo'])
        quantidade = prod['quantidade']
        descricao = prod['descricao']
        valor_unitario = prod['valor_unitario']
        categoria = prod.get('categoria', 'N/A')
        
        if not isinstance(quantidade, (int, float)) or quantidade <= 0:
            return jsonify({"error": f"Quantidade inválida para o produto '{descricao}'"}), 400

        if codigo in dados['estoque']:
            dados['estoque'][codigo]['quantidade'] += quantidade
            dados['estoque'][codigo]['descricao'] = descricao.lower()
            dados['estoque'][codigo]['valor_unitario'] = valor_unitario
            if categoria != 'N/A':
                dados['estoque'][codigo]['categoria'] = categoria
        else:
            dados['estoque'][codigo] = {
                'descricao': descricao.lower(),
                'quantidade': quantidade,
                'valor_unitario': valor_unitario,
                'categoria': categoria
            }
            
    salvar_dados()
    return jsonify({"message": "Produtos adicionados/atualizados com sucesso!"}), 201

# --- Sales Routes ---
@app.route('/vendas/direta', methods=['POST'])
def registrar_venda_direta():
    """Registers a direct sale, updating stock and revenues."""
    data = request.json
    required_fields = ['codigo', 'quantidade', 'forma_pagamento']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Dados de venda incompletos. 'codigo', 'quantidade' e 'forma_pagamento' são obrigatórios."}), 400
        
    codigo = str(data['codigo'])
    quantidade = data['quantidade']
    forma_pagamento = data['forma_pagamento']
    
    if codigo not in dados['estoque']:
        return jsonify({"error": "Produto não encontrado."}), 404
        
    if not isinstance(quantidade, (int, float)) or quantidade <= 0:
        return jsonify({"error": "Quantidade de venda inválida."}), 400
        
    if dados['estoque'][codigo]['quantidade'] < quantidade:
        return jsonify({"error": "Estoque insuficiente."}), 400
        
    dados['estoque'][codigo]['quantidade'] -= quantidade
    valor_venda = quantidade * dados['estoque'][codigo]['valor_unitario']
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    dados['receitas'].append({
        'descricao': f"Venda de {quantidade} und. de {dados['estoque'][codigo]['descricao']}",
        'valor': valor_venda, 
        'data': agora, 
        'tipo': 'receita', 
        'forma_pagamento': forma_pagamento
    })
    
    salvar_dados()
    return jsonify({"message": "Venda registrada com sucesso!", "total": valor_venda}), 200

@app.route('/vendas/delivery', methods=['POST'])
def registrar_venda_delivery():
    """Registers a delivery sale (without generating revenue) in the system."""
    data = request.json
    if not data or 'codigo' not in data or 'quantidade' not in data or 'plataforma' not in data:
        return jsonify({"error": "Dados de venda incompletos"}), 400
    codigo = data['codigo']
    quantidade = data['quantidade']
    plataforma = data['plataforma']
    if codigo not in dados['estoque']:
        return jsonify({"error": "Produto não encontrado"}), 404
    if dados['estoque'][codigo]['quantidade'] < quantidade:
        return jsonify({"error": "Estoque insuficiente"}), 400
    dados['estoque'][codigo]['quantidade'] -= quantidade
    salvar_dados()
    return jsonify({"message": f"Venda de {quantidade} und. de {dados['estoque'][codigo]['descricao']} (Delivery) registrada no estoque."}), 200

@app.route('/fluxo_caixa/resumo', methods=['GET'])
def ver_resumo_fluxo_caixa():
    """Returns the current cash flow summary."""
    total_receitas = sum(item['valor'] for item in dados['receitas'])
    total_despesas = sum(item['valor'] for item in dados['despesas'])
    saldo = total_receitas - total_despesas
    return jsonify({
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "receitas_detalhes": dados['receitas'],
        "despesas_detalhes": dados['despesas']
    })

@app.route('/fluxo_caixa/receita', methods=['POST'])
def adicionar_receita():
    """Adds a manual revenue to the cash flow."""
    data = request.json
    if not data or 'valor' not in data or 'descricao' not in data:
        return jsonify({"error": "Dados incompletos"}), 400
    valor = data['valor']
    descricao = data['descricao']
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    dados['receitas'].append({'descricao': descricao, 'valor': valor, 'data': agora, 'tipo': 'receita', 'forma_pagamento': 'Manual'})
    salvar_dados()
    return jsonify({"message": f"Receita de {valor} adicionada com sucesso."}), 201

@app.route('/fluxo_caixa/despesa', methods=['POST'])
def adicionar_despesa():
    """Adds an expense to the cash flow."""
    data = request.json
    if not data or 'valor' not in data or 'descricao' not in data:
        return jsonify({"error": "Dados incompletos"}), 400
    valor = data['valor']
    descricao = data['descricao']
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    dados['despesas'].append({'descricao': descricao, 'valor': valor, 'data': agora, 'tipo': 'despesa'})
    salvar_dados()
    return jsonify({"message": f"Despesa de {valor} adicionada com sucesso."}), 201

@app.route('/estoque/mudar_categoria', methods=['POST'])
def mudar_categoria_produto():
    """Changes a product's category in stock."""
    data = request.json
    if not data or 'codigo' not in data or 'nova_categoria' not in data:
        return jsonify({"error": "Dados incompletos"}), 400
    codigo = data['codigo']
    nova_categoria = data['nova_categoria']
    if codigo not in dados['estoque']:
        return jsonify({"error": "Produto não encontrado"}), 404
    dados['estoque'][codigo]['categoria'] = nova_categoria
    salvar_dados()
    return jsonify({"message": f"Categoria de '{dados['estoque'][codigo]['descricao']}' alterada para '{nova_categoria}' com sucesso."}), 200

# --- Report Routes ---
@app.route('/relatorios/estoque', methods=['GET'])
def get_relatorio_estoque():
    """Generates and returns the stock report as an Excel file."""
    caminho_arquivo = gerar_relatorios_estoque_excel()
    if not caminho_arquivo:
        return jsonify({"error": "Estoque vazio. Não foi possível gerar o relatório."}), 404
    return send_file(caminho_arquivo, as_attachment=True, download_name=os.path.basename(caminho_arquivo))

@app.route('/relatorios/fluxo_caixa', methods=['GET'])
def get_relatorio_fluxo_caixa():
    """Generates and returns the cash flow report as an Excel file. Can be filtered by month and year. Ex: /relatorios/fluxo_caixa?mes=9&ano=2024"""
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    caminho_arquivo = gerar_relatorio_fluxo_caixa_excel(mes, ano)
    return send_file(caminho_arquivo, as_attachment=True, download_name=os.path.basename(caminho_arquivo))

@app.route('/relatorios/vendas_diarias', methods=['GET'])
def get_relatorio_vendas_diarias():
    """Generates and returns the daily sales report as an Excel file. Ex: /relatorios/vendas_diarias?data=01-09-2024"""
    data_relatorio_str = request.args.get('data')
    if not data_relatorio_str:
        return jsonify({"error": "Parâmetro 'data' (DD-MM-AAAA) é obrigatório."}), 400
    
    try:
        data_relatorio_obj = datetime.datetime.strptime(data_relatorio_str, "%d-%m-%Y").date()
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use DD-MM-AAAA."}), 400
    
    vendas_dia = [item for item in dados['receitas'] if item.get('tipo') == 'receita' and datetime.datetime.strptime(item['data'], "%d/%m/%Y %H:%M:%S").date() == data_relatorio_obj]
    if not vendas_dia:
        return jsonify({"message": f"Não há vendas registradas para a data {data_relatorio_str}."}), 404

    df_vendas_dia = pd.DataFrame(vendas_dia)
    relatorio_agregado = df_vendas_dia.groupby('forma_pagamento')['valor'].sum().reset_index()
    total_vendas = relatorio_agregado['valor'].sum()
    relatorio_agregado.loc[len(relatorio_agregado)] = ['Total Geral', total_vendas]
    
    subpasta = "Vendas_Diarias"
    caminho_subpasta = criar_subdiretorio(subpasta)
    caminho_arquivo = os.path.join(caminho_subpasta, f"Relatorio_de_Vendas_Diarias_{data_relatorio_str}.xlsx")
    
    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        relatorio_agregado.to_excel(writer, sheet_name='Vendas Diárias', index=False)
        df_vendas_dia.to_excel(writer, sheet_name='Detalhes', index=False)

    formatar_planilha_excel(caminho_arquivo)
    adicionar_assinatura_excel(caminho_arquivo)

    return send_file(caminho_arquivo, as_attachment=True, download_name=os.path.basename(caminho_arquivo))


if __name__ == '__main__':
    # Initialize the app data before the server starts.
    carregar_dados()
    try:
        # Set locale for Brazilian Portuguese
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    
    # The 'debug=True' option is for development purposes only.
    app.run(debug=True)