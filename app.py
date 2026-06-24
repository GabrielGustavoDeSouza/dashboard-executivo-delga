import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURAÇÃO
# ==========================================

st.set_page_config(
    page_title="Dashboard Executivo Delga",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Executivo Delga")
st.caption("Gestão Estratégica de Projetos e Retorno Financeiro")

# ==========================================
# UPLOAD
# ==========================================

arquivo = st.sidebar.file_uploader(
    "Carregar Planilha",
    type=["xlsx"]
)

if arquivo is None:
    st.info("Faça upload da planilha para iniciar.")
    st.stop()

# ==========================================
# LER EXCEL
# ==========================================

try:

    excel = pd.ExcelFile(arquivo)

    st.sidebar.success("Arquivo carregado")

    # MOSTRA TODAS AS ABAS
    abas = excel.sheet_names

    # LOCALIZA ABA UNIDADES
    aba_unidades_nome = None

    for aba in abas:

        nome = str(aba).lower().strip()

        if "unidades" in nome:
            aba_unidades_nome = aba
            break

    # LOCALIZA PARETO
    aba_pareto_nome = None

    for aba in abas:

        nome = str(aba).lower().strip()

        if "pareto" in nome:
            aba_pareto_nome = aba
            break

    st.sidebar.write("Aba Unidades:", aba_unidades_nome)
    st.sidebar.write("Aba Pareto:", aba_pareto_nome)

    # LEITURA

    if aba_unidades_nome:
        df_unidades = pd.read_excel(
            arquivo,
            sheet_name=aba_unidades_nome
        )
    else:
        st.error("Não encontrei a aba de Unidades.")
        st.stop()

    if aba_pareto_nome:
        df_pareto = pd.read_excel(
            arquivo,
            sheet_name=aba_pareto_nome
        )
    else:
        st.warning("Aba Pareto não encontrada.")
        df_pareto = pd.DataFrame()

except Exception as e:

    st.error(f"Erro ao ler Excel: {e}")
    st.stop()

# ==========================================
# BIG NUMBERS TEMPORÁRIOS
# ==========================================

c1,c2,c3,c4,c5,c6 = st.columns(6)

with c1:
    st.metric("Meta Grupo", "R$ --")

with c2:
    st.metric("Retorno Previsto", "R$ --")

with c3:
    st.metric("Previsto Ano", "R$ --")

with c4:
    st.metric("Validado", "R$ --")

with c5:
    st.metric("Real DRE", "R$ --")

with c6:
    st.metric("Projetos", len(df_pareto))

# ==========================================
# DIAGNÓSTICO
# ==========================================

st.divider()

st.subheader("Abas Encontradas")

st.write(abas)

st.divider()

st.subheader("Prévia Aba Unidades")

st.dataframe(df_unidades.head(20))

if not df_pareto.empty:

    st.divider()

    st.subheader("Prévia Pareto")

    st.dataframe(df_pareto.head(20))
