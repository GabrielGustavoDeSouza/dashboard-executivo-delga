import streamlit as st
import pandas as pd

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================

st.set_page_config(
    page_title="Dashboard Executivo Delga",
    page_icon="📊",
    layout="wide"
)

# ==================================================
# CSS DELGA
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #F4F6F9;
}

.metric-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    text-align:center;
}

.metric-title {
    font-size:14px;
    color:#666;
    font-weight:600;
}

.metric-value {
    font-size:34px;
    font-weight:700;
    color:#0F4C81;
}

.block-container{
    padding-top:2rem;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# CABEÇALHO
# ==================================================

st.title("📊 Dashboard Executivo — Grupo Delga")
st.caption("Gestão Estratégica de Projetos e Retorno Financeiro")

st.divider()

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("⚙ Administração")

arquivo = st.sidebar.file_uploader(
    "Carregar Planilha Atualizada",
    type=["xlsx"]
)

# ==================================================
# SEM ARQUIVO
# ==================================================

if arquivo is None:

    st.info("""
    Faça upload da planilha Excel para visualizar os indicadores.
    
    Arquivo esperado:
    Controle_Indicadores_Delga.xlsx
    """)

    st.stop()

# ==================================================
# LEITURA DAS ABAS
# ==================================================

try:

    aba_unidades = pd.read_excel(
        arquivo,
        sheet_name="5 Unidades +"
    )

    aba_pareto = pd.read_excel(
        arquivo,
        sheet_name="Pareto"
    )

except Exception as e:

    st.error(f"Erro ao ler o arquivo: {e}")
    st.stop()

# ==================================================
# BIG NUMBERS (TEMPORÁRIOS)
# ==================================================
# Vamos substituir pelos cálculos reais depois

meta_grupo = 50320000
retorno_previsto = 48275349
previsto_2026 = 21759477
validado = 16843792
realizado = 4978230
projetos = 204

# ==================================================
# LINHA 1
# ==================================================

c1,c2,c3,c4,c5,c6 = st.columns(6)

with c1:
    st.metric(
        "Meta Grupo",
        f"R$ {meta_grupo/1000000:.2f} Mi"
    )

with c2:
    st.metric(
        "Retorno Previsto",
        f"R$ {retorno_previsto/1000000:.2f} Mi"
    )

with c3:
    st.metric(
        "Previsto 2026",
        f"R$ {previsto_2026/1000000:.2f} Mi"
    )

with c4:
    st.metric(
        "Validado Custos",
        f"R$ {validado/1000000:.2f} Mi"
    )

with c5:
    st.metric(
        "Real DRE",
        f"R$ {realizado/1000000:.2f} Mi"
    )

with c6:
    st.metric(
        "Projetos",
        projetos
    )

st.divider()

# ==================================================
# VISÃO GERAL
# ==================================================

g1,g2 = st.columns(2)

with g1:

    st.subheader("📍 Representatividade das Unidades")

    dados_unidades = pd.DataFrame({
        "Unidade":[
            "Diadema",
            "Jarinu",
            "Ferraz",
            "São Leopoldo",
            "Anchieta"
        ],
        "Valor":[
            6.9,
            5.3,
            13.3,
            2.1,
            3.8
        ]
    })

    st.bar_chart(
        dados_unidades.set_index("Unidade")
    )

with g2:

    st.subheader("🏢 Representatividade das Áreas")

    dados_areas = pd.DataFrame({
        "Área":[
            "Compras",
            "Vendas",
            "Corporativo"
        ],
        "Valor":[
            7,
            10,
            1.7
        ]
    })

    st.bar_chart(
        dados_areas.set_index("Área")
    )

st.divider()

# ==================================================
# FUNIL
# ==================================================

st.subheader("📈 Funil Executivo")

funil = pd.DataFrame({
    "Etapa":[
        "Meta Grupo",
        "Portfólio Previsto",
        "Previsto 2026",
        "Validado",
        "Realizado"
    ],
    "Valor":[
        meta_grupo,
        retorno_previsto,
        previsto_2026,
        validado,
        realizado
    ]
})

st.bar_chart(
    funil.set_index("Etapa")
)

st.divider()

# ==================================================
# PROJETOS
# ==================================================

st.subheader("📋 Base de Projetos")

st.caption(
    "Prévia da aba Pareto"
)

st.dataframe(
    aba_pareto,
    use_container_width=True,
    height=500
)

# ==================================================
# RODAPÉ
# ==================================================

st.divider()

st.caption(
    "Dashboard Executivo Delga • Atualização automática via Excel"
)
