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
# FUNÇÃO FORMATAÇÃO
# ==========================================

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0"

def formatar_percentual(valor):
    try:
        return f"{float(valor):.1f}%"
    except:
        return "0%"

# ==========================================
# UP
