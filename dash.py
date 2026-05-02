import pandas as pd
import streamlit as st
import importlib

import json #para ler e escrever arquivos JSON
import compras #importa as funções de compras.py


import plotly.express as px #Biblioteca para gráficos

#CSS
st.markdown("""
<style>
/* Botões arredondados e coloridos */
.stButton > button {
    background-color: #4CAF50; /* Verde */
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
}

/* Métricas com fundo suave */
.stMetric {
    background-color: #2D2D2D;
    color: #FFFFFF;
    padding: 10px;
    border-radius: 10px;
}

/* Títulos centralizados */
h1, h2, h3 {
    text-align: center;
    color: #4CAF50;
}

/* Rodapé */
footer {
    visibility: hidden;
}
reportview-container::after {
    content: "Desenvolvido Kamine - App de Mercado";
    display: block;
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #2D2D2D;
    color: #888;
    padding: 20px;
    text-align: center;
}
</style>
""",
  unsafe_allow_html=True)




#Abrir o arquivo JSON para ler os dados de compras
with open('categorias.json', 'r', encoding='utf-8') as f:
    categorias = json.load(f)

#Histórico e Dashboard de compras

mes_selecionado = "Todos"

aba_lista, aba_dashboard = st.tabs(["📋 Lista de Mercado", "📊 Dashboard de Mercado"])

with aba_lista:
    # Lista de compras com checkbox
    st.title("📋 Lista de Mercado")

    if "lista" not in st.session_state:
        st.session_state.lista = []

    with st.form("forms_lista"):
        produto = st.text_input("Produto")
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        preco_unitario = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")

        #Campo de categoria (opcional)
        categoria = st.selectbox(
            "Categoria", ["Frutas", "Verduras", "Carnes", "Laticínios", "Congelados", "Bebidas", "Padaria", "Limpeza", "Higiene Pessoal", 
                          "Frios", "Mercearia", "Outros"]
        )
        adicionar = st.form_submit_button("Adicionar à Lista")
        
        if adicionar and produto:
            if preco_unitario <= 0.0:
                st.warning("⚠️ O preço unitário é zero. Por favor, insira um valor válido.")
            else:
                st.session_state.lista.append({
                    "produto": produto, 
                    "quantidade": quantidade,
                    "preco_unitario": preco_unitario,
                    "total": quantidade * preco_unitario,
                    "pego": False,
                    "adicionado": False
                })
                st.success(f"{quantidade} x {produto} adicionado à lista!")
    
    #Atualiza categorias automaticamente
    compras.atualizar_categorias(produto, categoria="Outros")  # Adiciona o produto à categoria "Outros" por padrão

    # Dentro do Loop dos checks
    st.subheader("📋 Itens da Lista")
    for i, item in enumerate(st.session_state.lista):
        checked = st.checkbox(f"{item['quantidade']} x {item['produto']}", value=item["pego"], key=f"check_{i}")
        st.session_state.lista[i]["pego"] = checked

        # Se o usuário marcar o item como pego, adiciona ao histórico de compras
        if checked and not item.get("adicionado", False):
            compras.adicionar_compra(item['produto'], item['quantidade'], item['preco_unitario'])
            st.session_state.lista[i]["adicionado"] = True  # Marca como adicionado para não duplicar
            st.success(f"{item['quantidade']} x {item['produto']} adicionado ao histórico de compras!")
            st.rerun()  # Atualiza a página para refletir as mudanças
    
    pegos = [f"{i['quantidade']} x {i['produto']}"  for i in st.session_state.lista if i["pego"]]
    nao_pegos = [f"{i['quantidade']} x {i['produto']}" for i in st.session_state.lista if not i["pego"]]

    if pegos:
        st.success("✅ Já pegos:\n" + "\n".join(f"- {item}" for item in pegos))
    else:
        st.info("Nenhum item marcado como pego ainda.")

    if nao_pegos:
        st.warning("❌ Ainda faltam:\n" + "\n".join(f"- {item}" for item in nao_pegos))
    else:
        st.success("Todos os itens já foram pegos!")

    # Total (R$) da Lista
    total_lista = sum(i['quantidade'] * i.get('preco_unitario', 0) for i in st.session_state.lista)
    st.metric("💰 Total (R$) da Lista:", f"R${total_lista:.2f}")

    # Finalizar a lista
    st.subheader("🛒 Finalizar Lista")
    with st.expander("Limpar a lista"):
        if st.button("Limpar Lista"):
            st.session_state.lista = []  # Limpa a lista
            st.success("Lista finalizada e limpa!")
            st.rerun()  # Atualiza a página para refletir as mudanças




with aba_dashboard:
    st.title("📊 Dashboard de Mercado Mensal")

    #Histórico de compras e edição
    dados = compras.carregar_dados()

    if dados:
        st.subheader("📋 Histórico de Compras")
        st.dataframe(dados) #tabela interativa para mostrar os dados

        #Selecionar item para editar ou excluir
        index = st.selectbox("Selecione a compra para editar ou excluir", range(len(dados)))
        item = dados[index]

        st.write(f"Selecionado: {item['quantidade']} x {item['produto']} - Total: R${item['total']:.2f} ({item['data']})")

        novo_produto = st.text_input("Produto", value=item["produto"])
        nova_quantidade = st.number_input("Quantidade", min_value=1, step=1, value=item['quantidade'])
        novo_preco_unitario = st.number_input(f"Preço Unitário (R$)", min_value=0.0, format="%.2f", value=item['preco_unitario'])

    
        col1, col2 = st.columns(2)
        if col1.button("✏️ Editar"):
            compras.editar_compra(index, novo_produto, nova_quantidade, novo_preco_unitario)
            st.success("Compra editada com sucesso!")
            st.rerun()  # Atualiza a página para refletir as mudanças
        
        if col2.button("🗑️ Excluir"):
            compras.excluir_compra(index)
            st.warning("Compra excluída!")
            st.rerun()  # Atualiza a página para refletir as mudanças

        else:
            st.info("Clique em 'Editar' para modificar ou 'Excluir' para remover a compra.")

    # Gastos mensais

    aba1, aba2, aba3, aba4 = st.tabs(["📋 Histórico de Compras", "📈 Gastos Mensais", "🥧 Proporção por produto", "📊 Relatório Mensal"])

    with aba1:
        st.subheader("📋 Histórico de Compras")
        st.dataframe(dados) #tabela interativa para mostrar os dados

    with aba2:
        st.subheader("📈 Gastos Mensais")
        resumo = compras.gastos_mensais()
        if resumo:
            meses = list(resumo.keys())
            valores = list(resumo.values())
            fig = px.bar(x=meses, y=valores, labels={'x': 'Mês', 'y': 'Gasto Total (R$)'},
                         title="Gastos Mensais", text=valores)
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            st.plotly_chart(fig, user_container_width=True)
        else:
            st.info("Nenhuma compra registrada para mostrar os gastos mensais.")

    # Descrição de Categoria por Produto
    categorias = {
    "Frutas": ["banana", "maçã", "laranja", "uva", "abacaxi", "melão", "manga", "melancia", "kiwi"],
    "Verduras": ["alface", "tomate", "espinafre", "rúcula", "salsinha", "cebolinha", "agrião", "cebola", "pimentão", "cenoura", "batata", "batata doce", 
                 "chuchu", "brocolis", "repolho"],
    "Carnes": ["frango", "carne bovina", "carne suína", "peixe", "carne moída"],
    "Laticínios": ["leite", "queijo", "iogurte", "manteiga", "creme de leite", "requeijão", "leite condensado"],
    "Congelados": ["sorvete", "açai"],
    "Bebidas": ["água", "suco", "cerveja", "vinho", "energético", "espumante"],
    "Padaria": ["pão", "bolo", "sonho", "croissant", "bolacha", "cuca"],
    "Limpeza": ["detergente", "sabão líquido", "amaciante", "desinfetante", "esponja", "vassoura", "pá", "alvejante", "tira manchas", "Desengordurante", 
                "Saponáceo", "Pato", "Água sanitária", "Limpador multiuso", "Pastilha para o vaso", "Alcool", "Cera", "Odorizador", "Luvas de borracha"],
    "Higiene Pessoal": ["sabonete", "shampoo", "condicionador", "pasta de dente", "desodorante", "papel higiênico", "absorvente", "gilete", "creme de barbear", 
                        "protetor solar", "creme corporal", "enxaguante bucal", "cotonete", "algodão", "acetona"],
    "Frios": ["presunto", "mortadela", "salame", "peito de peru"],
    "Mercearia": ["arroz", "feijão", "massa", "aveia", "lentilha", "óleo", "vinagre", "sal", "açúcar", "farinha", "fermento químico", "café", "chá", 
                  "fermento biológico", "nescau", "leite em pó", "mel", "chimia", "mumu", "atum", "sardinha", "pepino em conserva", "extrato de tomate", 
                  "maionese", "mostarda", "ketchup", "molho inglês", "shoyu", "óleo", "temperos", "canela em pó", "chocolate"]
    }

    with aba3:
        st.subheader("🥧 Proporção por Produto")
        #Filtro por mês
        meses_disponiveis = sorted(set(compra['data'][:7] for compra in dados)) if dados else []
        mes_selecionado = st.selectbox("Filtrar por mês", ["Todos"] + meses_disponiveis)

        #Filtro por categoria
        categorias_disponiveis = list(categorias.keys())
        categoria_selecionada = st.selectbox("Filtrar por categoria", ["Todas"] + categorias_disponiveis)

        dados_filtrados = dados

        #Filtra por mês
        if mes_selecionado != "Todos":
            dados_filtrados = [c for c in dados_filtrados if c['data'][:7] == mes_selecionado]

        #Filtra por categoria
        if categoria_selecionada != "Todas":
            dados_filtrados = [c for c in dados_filtrados 
                               if c['produto'].lower().strip() in [p.lower() for p in categorias[categoria_selecionada]]]

        categorias_totais = {}
        for compra in dados_filtrados:
            produto = compra['produto'].lower().strip()
            categoria = "Outros"
            for nome_categoria, lista_produtos in categorias.items():
                if produto in [p.lower() for p in lista_produtos]:
                    categoria = nome_categoria
                    break
            categorias_totais[categoria] = categorias_totais.get(categoria, 0) + compra['total']
                                       
        if categorias_totais:
            px = importlib.import_module("plotly.express")
            fig = px.pie(values=categorias_totais.values(), names=categorias_totais.keys(), title="Proporção de Gastos por Categoria")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, user_container_width=True)
        else:
            st.info("Nenhuma compra registrada para mostrar a proporção por categoria.")
    
    with aba4:
        st.subheader("📊 Relatório Mensal")

        df = pd.DataFrame(dados)

        if not df.empty:
            df['mes'] = df['data'].str[:7]  # Extrai o ano e mês
            
            mes_selecionado = st.selectbox("Selecione o mês para o Relatório", sorted(df['mes'].unique()))

            df_mes = df[df['mes'] == mes_selecionado]

            total_mes = df_mes['total'].sum()
            st.metric(f"💰 Total gasto em {mes_selecionado}:", f"R${total_mes: .2f}")

            #Top 5 produtos mais comprados
            top_produtos = df_mes.groupby('produto')['total'].sum().sort_values(ascending=False).head(5)
            st.bar_chart(top_produtos)

            #Top 3 categorias mais compradas
            categorias_totais = {}
            for _, compra in df_mes.iterrows():
                produto = compra['produto'].lower().strip()
                categoria = "Outros"
                for nome_categoria, lista_produtos in categorias.items():
                    if produto in [p.lower() for p in lista_produtos]:
                        categoria = nome_categoria
                        break
                categorias_totais[categoria] = categorias_totais.get(categoria, 0) + compra['total']

            top_categorias = dict(sorted(categorias_totais.items(), key=lambda x: x[1], reverse=True)[:3])
            fig = px.pie(values=top_categorias.values(), names=top_categorias.keys(), title=f"Top 3 Categorias em {mes_selecionado}")
            st.plotly_chart(fig, user_container_width=True)
        else:
            st.info("Nenhuma compra registrada para mostrar o relatório mensal.")
       
    #Mostra Alertas de limite definidos
    limite = st.number_input("Defina seu orçamento mensal (R$): ", min_value = 0.0, format="%.2f")
    if mes_selecionado == "Todos":
        gasto_total = sum(c['total'] for c in dados)
    else:
        gasto_total = sum(c['total'] for c in dados if c['data'].startswith(mes_selecionado))
    if gasto_total > limite:
        st.error(f"⚠️ Você ultrapassou o limite de R${limite:.2f}!")
    elif gasto_total > limite * 0.8:
        st.warning(f"⚠️ Você já gastou {gasto_total: .2f}, está perto do limite!")

st.markdown(
    """
    <hr style="margin-top:50px; margin-bottom:20px;">
    <div style="text-align:center; color:gray;">
        App de Mercado v1.0 - Desenvolvido por Kamine
    </div>
    """,
    unsafe_allow_html=True
)