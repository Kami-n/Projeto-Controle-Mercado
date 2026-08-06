import json 
import os
from datetime import datetime

ARQUIVO = 'compras.json'

def carregar_dados():
    try:
        with open(ARQUIVO, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_dados(dados):  
    with open(ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=4)

def adicionar_compra(produto, data=None):
    dados = carregar_dados()
    compra_id = len(dados) + 1
    if not data:
        data = datetime.now().strftime("%Y-%m-%d")
    for p in produtos:
        p["total"] = p["quantidade"] * p["preco_unitario"]

    nova_compra = {
        "id": compra_id,
        "data": data,
        "produtos": produtos,
    }   

    dados.append(nova_compra)
    salvar_dados(dados)

def gastos_mensais():
    dados = carregar_dados()
    resumo = {}
    for compra in dados:
        mes = compra["data"][:7]  # Extrai o ano e mês
        total_compra = sum(p["total"] for p in compra["produtos"])
        resumo[mes] = resumo.get(mes, 0) + total_compra
    return resumo

def editar_compra(index, produtos, data=None):
    dados = carregar_dados()
    if data is None:
        data = dados[index]['data']  # Mantém a data original se não for fornecida

    for p  in produtos:
        p["total"] = p["quantidade"] * p["preco_unitario"]
    
    dados[index] = {
            'compra_id': dados[index]['compra_id'],
            'produtos': produtos,
            'data': dados[index]['data']  # Mantém a data original
    }
    salvar_dados(dados)

def excluir_compra(index):
    dados = carregar_dados()
    dados.pop(index)
    salvar_dados(dados)



def atualizar_categorias(produto, categoria, arquivo = 'categorias.json'):
    """
    Adiciona um novo produto à categoria informada dentro do arquivo categorias.json. Se a categoria não existir, cria uma nova.
    """
    
    # Se o arquivo não existir, cria um novo com um dicionário vazio
    if not os.path.exists(arquivo):
        categorias = {}
    else:
        with open(arquivo, 'r', encoding='utf-8') as f:
            categorias = json.load(f)

    #Normaliza o nome do produto para minusculas
    produto = produto.lower().strip()

    # Se a categoria não existir, cria uma nova categoria
    if categoria not in categorias:
        categorias[categoria] = []

    # Adicionar o produto à categoria correspondente sem duplicações
    if produto not in categorias[categoria]:
        categorias[categoria].append(produto)
    
    #Salva de volta no arquivo JSON, garantindo que o produto seja adicionado à categoria correta, sem duplicações
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(categorias, f, ensure_ascii=False, indent=4)

    return f"Produto '{produto}' adicionado à categoria '{categoria}' com sucesso!"