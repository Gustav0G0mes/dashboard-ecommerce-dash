import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px
import plotly.figure_factory as ff


# 1. Leitura do arquivo
df = pd.read_csv("ecommerce_estatistica.csv")


# 2. Ajustes automáticos
possiveis_precos = ["Preco", "Preço", "preco", "preço"]
possiveis_descontos = ["Desconto", "desconto"]
possiveis_notas = ["Nota", "nota"]
possiveis_avaliacoes = ["N_Avaliacoes", "Avaliacoes", "Avaliações", "n_avaliacoes"]
possiveis_categoria = ["Temporada", "Categoria", "Marca", "Material", "temporada", "categoria"]

def encontrar_coluna(lista_possiveis, colunas_df):
    for col in lista_possiveis:
        if col in colunas_df:
            return col
    return None

col_preco = encontrar_coluna(possiveis_precos, df.columns)
col_desconto = encontrar_coluna(possiveis_descontos, df.columns)
col_nota = encontrar_coluna(possiveis_notas, df.columns)
col_avaliacoes = encontrar_coluna(possiveis_avaliacoes, df.columns)
col_categoria = encontrar_coluna(possiveis_categoria, df.columns)


# 3. Tratamento básico
if col_desconto and df[col_desconto].dtype == object:
    df[col_desconto] = df[col_desconto].astype(str).str.extract(r"(\d+)")[0]
    df[col_desconto] = pd.to_numeric(df[col_desconto], errors="coerce")

for col in [col_preco, col_desconto, col_nota, col_avaliacoes]:
    if col is not None:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# 4. Criação dos gráficos
graficos = []

# Histograma
if col_preco:
    fig_hist = px.histogram(
        df,
        x=col_preco,
        nbins=20,
        title="Histograma dos Preços dos Produtos"
    )
    fig_hist.update_layout(xaxis_title="Preço", yaxis_title="Frequência")
    graficos.append(dcc.Graph(figure=fig_hist))

# Dispersão
if col_desconto and col_preco:
    fig_disp = px.scatter(
        df,
        x=col_desconto,
        y=col_preco,
        title="Relação entre Desconto e Preço",
        opacity=0.7
    )
    fig_disp.update_layout(xaxis_title="Desconto", yaxis_title="Preço")
    graficos.append(dcc.Graph(figure=fig_disp))

# Mapa de calor
colunas_numericas = [col for col in [col_preco, col_desconto, col_nota, col_avaliacoes] if col is not None]

if len(colunas_numericas) >= 2:
    correlacao = df[colunas_numericas].corr().round(2)
    fig_heat = ff.create_annotated_heatmap(
        z=correlacao.values,
        x=list(correlacao.columns),
        y=list(correlacao.index),
        annotation_text=correlacao.values.astype(str),
        colorscale="RdBu",
        showscale=True
    )
    fig_heat.update_layout(title="Mapa de Calor das Correlações")
    graficos.append(dcc.Graph(figure=fig_heat))

# Gráfico de barras
if col_categoria and col_preco:
    media_por_categoria = df.groupby(col_categoria)[col_preco].mean().sort_values().reset_index()
    media_por_categoria.columns = ["Categoria", "Preço Médio"]

    fig_bar = px.bar(
        media_por_categoria,
        x="Categoria",
        y="Preço Médio",
        title="Preço Médio por Categoria"
    )
    fig_bar.update_layout(xaxis_title="Categoria", yaxis_title="Preço Médio")
    graficos.append(dcc.Graph(figure=fig_bar))

# Gráfico de pizza
if col_categoria:
    contagem_categoria = df[col_categoria].value_counts().head(8).reset_index()
    contagem_categoria.columns = ["Categoria", "Quantidade"]

    fig_pizza = px.pie(
        contagem_categoria,
        names="Categoria",
        values="Quantidade",
        title="Distribuição por Categoria"
    )
    graficos.append(dcc.Graph(figure=fig_pizza))

# Gráfico de densidade
if col_preco:
    serie_preco = df[col_preco].dropna()
    if not serie_preco.empty:
        fig_dens = ff.create_distplot(
            [serie_preco],
            [col_preco],
            show_hist=False,
            show_rug=False
        )
        fig_dens.update_layout(
            title="Densidade dos Preços",
            xaxis_title="Preço",
            yaxis_title="Densidade"
        )
        graficos.append(dcc.Graph(figure=fig_dens))

# Gráfico de regressão
if col_desconto and col_preco:
    df_reg = df[[col_desconto, col_preco]].dropna()

    if not df_reg.empty:
        fig_reg = px.scatter(
            df_reg,
            x=col_desconto,
            y=col_preco,
            trendline="ols",
            title="Regressão entre Desconto e Preço",
            opacity=0.6
        )
        fig_reg.update_layout(xaxis_title="Desconto", yaxis_title="Preço")
        graficos.append(dcc.Graph(figure=fig_reg))


# 5. Aplicação Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de E-commerce", style={"textAlign": "center"}),
    html.P(
        "Visualização interativa dos gráficos gerados a partir do arquivo ecommerce_estatistica.csv",
        style={"textAlign": "center"}
    ),
    html.Div(graficos, style={"width": "90%", "margin": "0 auto"})
])

# 6. Executar servidor
if __name__ == "__main__":
    app.run(debug=True)