import pandas as pd
import plotly.graph_objects as go

# --- 1. Estruturação dos Dados ---
data = {
    'Modelo': ["GPT Turbo + Mini", "GPT Turbo"],
    'Passaram': [37, 33],
    'Falharam': [5, 10],
    'Erro Crítico': [8, 7],
    'Total': [50, 50],
    'Tempo Médio (s)': [18.28, 23.00]
}
df = pd.DataFrame(data)

# --- 2. Preparação dos Cálculos para os Filtros ---
df['Falha Total (com erro)'] = df['Falharam'] + df['Erro Crítico']
df['Passaram % (com erro)'] = (df['Passaram'] / df['Total']) * 100
df['Falha Total % (com erro)'] = (df['Falha Total (com erro)'] / df['Total']) * 100

df['Total Válido (sem erro)'] = df['Total'] - df['Erro Crítico']
df['Passaram % (sem erro)'] = (df['Passaram'] / df['Total Válido (sem erro)']) * 100
df['Falharam % (sem erro)'] = (df['Falharam'] / df['Total Válido (sem erro)']) * 100

# --- 3. Criação do Gráfico Unificado ---

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['Modelo'], y=df['Passaram'], name='✅ Passaram',
    marker_color='#2E7D32', texttemplate='%{y}', textposition='outside'
))
fig.add_trace(go.Bar(
    x=df['Modelo'], y=df['Falharam'], name='❌ Falharam (Validação)',
    marker_color='#ED6C02', texttemplate='%{y}', textposition='outside'
))
fig.add_trace(go.Bar(
    x=df['Modelo'], y=df['Erro Crítico'], name='💥 Erro Crítico (Execução)',
    marker_color='#D32F2F', texttemplate='%{y}', textposition='outside'
))

# --- 4. Criação dos Botões de Filtro (Menu Dropdown) ---

# MUDANÇA: Definimos o título principal como uma variável para reutilizá-lo
main_title_text = "<b>Dashboard de Performance dos Modelos de Análise de Currículos</b>"

buttons = [
    # MUDANÇA: Cada botão agora inclui a chave 'title_text' para manter o título principal
    dict(label="Resultados: Absoluto (com erros)",
         method="update",
         args=[{"y": [df['Passaram'], df['Falharam'], df['Erro Crítico']],
                "text": [df['Passaram'], df['Falharam'], df['Erro Crítico']],
                "texttemplate": '%{text}', "visible": [True, True, True]},
               {"title_text": f"{main_title_text}<br><sup>Visualização: Resultados Absolutos (com erros)</sup>",
                "yaxis.title": 'Nº de Testes'}]),
    dict(label="Resultados: Porcentagem (com erros)",
         method="update",
         args=[{"y": [df['Passaram % (com erro)'], df['Falha Total % (com erro)']],
                "text": [df['Passaram % (com erro)'].round(1).astype(str) + '%', 
                         df['Falha Total % (com erro)'].round(1).astype(str) + '%'],
                "texttemplate": '%{text}', "visible": [True, True, False]},
               {"title_text": f"{main_title_text}<br><sup>Visualização: Distribuição dos Resultados (% do Total)</sup>",
                "yaxis.title": 'Porcentagem (%)'}]),
    dict(label="Resultados: Absoluto (sem erros)",
         method="update",
         args=[{"y": [df['Passaram'], df['Falharam']],
                "text": [df['Passaram'], df['Falharam']],
                "texttemplate": '%{text}', "visible": [True, True, False]},
               {"title_text": f"{main_title_text}<br><sup>Visualização: Performance da IA (Apenas Testes Válidos)</sup>",
                "yaxis.title": 'Nº de Testes'}]),
    dict(label="Resultados: Porcentagem (sem erros)",
         method="update",
         args=[{"y": [df['Passaram % (sem erro)'], df['Falharam % (sem erro)']],
                "text": [df['Passaram % (sem erro)'].round(1).astype(str) + '%', 
                         df['Falharam % (sem erro)'].round(1).astype(str) + '%'],
                "texttemplate": '%{text}', "visible": [True, True, False]},
               {"title_text": f"{main_title_text}<br><sup>Visualização: Taxa de Sucesso da IA (Apenas Testes Válidos)</sup>",
                "yaxis.title": 'Porcentagem (%)'}]),
    dict(label="Performance: Tempo Médio",
         method="update",
         args=[{"y": [df['Tempo Médio (s)']],
                "text": [df['Tempo Médio (s)'].round(2).astype(str) + 's'],
                "texttemplate": '%{text}', "visible": [True, False, False]},
               {"title_text": f"{main_title_text}<br><sup>Visualização: Performance (Tempo Médio por Análise)</sup>",
                "yaxis.title": 'Tempo Médio (segundos)'}]),
]

# --- 5. Estilização Final do Dashboard ---

fig.update_layout(
    title_text=f"{main_title_text}<br><sup>Use o filtro para explorar diferentes métricas</sup>", # Título inicial
    title_x=0.5,
    height=700,
    template="plotly_white",
    font=dict(family="Arial, Helvetica, sans-serif", size=15, color="#212529"),
    barmode='group',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(t=150, b=80, l=80, r=80),
    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.01,
            xanchor="left",
            y=1.16,
            yanchor="top",
            bgcolor="#f8f9fa",
            bordercolor="#dee2e6"
        )
    ]
)

fig.update_xaxes(title_text="Configuração do Modelo", tickfont=dict(size=14))
fig.update_yaxes(title_text="Nº de Testes", tickfont=dict(size=14), gridcolor='#e9ecef')

# --- 6. Exibição do Dashboard ---
print("Exibindo dashboard interativo... Feche a janela do navegador para encerrar o script.")
fig.show()