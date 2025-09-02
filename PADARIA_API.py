# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import gestao_padaria  # Importa o seu script original

app = FastAPI()

# Definição dos modelos de dados para as requisições
class ProdutoEntrada(BaseModel):
    produto: str
    quantidade: int
    valor_unitario: float
    categoria: str

class Venda(BaseModel):
    produto: str
    quantidade: int
    forma_pagamento: str

# Carrega os dados uma única vez na inicialização da API
receitas, despesas, estoque = gestao_padaria.carregar_dados()

@app.get("/")
def home():
    return {"mensagem": "API de Gestão da Padaria está online!"}

# --- Endpoints de Estoque ---
@app.get("/estoque/")
def get_estoque():
    return {"estoque": estoque}

@app.post("/estoque/adicionar_individual/")
def adicionar_produto_individual(item: ProdutoEntrada):
    try:
        produto_nome = item.produto.lower()
        if produto_nome in estoque:
            estoque[produto_nome]['quantidade'] += item.quantidade
            estoque[produto_nome]['valor_unitario'] = item.valor_unitario
            estoque[produto_nome]['categoria'] = item.categoria
        else:
            estoque[produto_nome] = {
                'quantidade': item.quantidade,
                'valor_unitario': item.valor_unitario,
                'categoria': item.categoria
            }
        gestao_padaria.salvar_dados(receitas, despesas, estoque)
        return {"status": "sucesso", "mensagem": f"Produto '{produto_nome.capitalize()}' adicionado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar produto: {e}")

# --- Endpoint de Vendas ---
@app.post("/vendas/registrar/")
def registrar_venda(venda: Venda):
    try:
        produto_nome = venda.produto.lower()
        if produto_nome not in estoque or estoque[produto_nome]['quantidade'] < venda.quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente.")
        
        # Lógica de venda
        estoque[produto_nome]['quantidade'] -= venda.quantidade
        valor_venda = venda.quantidade * estoque[produto_nome]['valor_unitario']
        
        agora = gestao_padaria.datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        receitas.append({
            'descricao': f"Venda de {venda.quantidade} und. de {produto_nome}",
            'valor': valor_venda,
            'data': agora,
            'tipo': 'receita',
            'forma_pagamento': venda.forma_pagamento
        })

        gestao_padaria.salvar_dados(receitas, despesas, estoque)
        return {"status": "sucesso", "mensagem": "Venda registrada com sucesso.", "valor_total": valor_venda}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar venda: {e}")
