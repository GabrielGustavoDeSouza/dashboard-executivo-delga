import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings
import os
import pickle

warnings.filterwarnings("ignore")

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Dashboard Executivo — Grupo Delga 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CSS CUSTOMIZADO
# =============================================================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 1400px; }
    .main-header { font-size: 28px; font-weight: 700; color: #1B3A5C; margin-bottom: 0; line-height: 1.2; }
    .sub-header { font-size: 13px; color: #6C757D; margin-bottom: 20px; }
    .kpi-card { border: 1px solid #DEE2E6; border-radius: 6px; padding: 16px 18px; background-color: #FFFFFF; height: 100%; }
    .kpi-title { font-size: 10px; font-weight: 600; color: #6C757D; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .kpi-value { font-size: 26px; font-weight: 700; margin: 4px 0; line-height: 1.2; }
    .kpi-sub { font-size: 12px; color: #343A40; margin-bottom: 2px; }
    .kpi-detail { font-size: 11px; color: #6C757D; }
    .color-primary { color: #1B3A5C; }
    .color-green { color: #1A7A3A; }
    .color-orange { color: #E8A838; }
    .nota-metodologica { background-color: #FFF8E1; border: 1px solid #FFE082; border-radius: 4px; padding: 12px 16px; font-size: 11px; color: #343A40; line-height: 1.6; margin: 16px 0; }
    .section-title { font-size: 14px; font-weight: 700; color: #1B3A5C; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.3px; }
    .section-box { border: 1px solid #DEE2E6; border-radius: 6px; padding: 16px; background-color: #FFFFFF; margin-bottom: 16px; }
    .custom-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .custom-table th { background-color: #1B3A5C; color: white; padding: 10px 12px; text-align: left; font-weight: 600; font-size: 11px; }
    .custom-table td { padding: 8px 12px; border-bottom: 1px solid #DEE2E6; }
    .custom-table tr:last-child td { border-top: 2px solid #1B3A5C; font-weight: 700; }
    .color-teal { color: #20C997; }
    .color-orange-text { color: #E8A838; }
    .progress-container { display: flex; align-items: center; gap: 8px; }
    .progress-bar-bg { width: 70px; height: 8px; background-color: #E8E8E8; border-radius: 4px; overflow: hidden; display: inline-block; }
    .progress-bar-fill { height: 100%; border-radius: 4px; }
    .badge-execucao { background-color: #FFF3E0; color: #E8A838; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }
    .badge-destaque { background-color: #E8F5E9; color: #1A7A3A; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }
    .class-card { border-radius: 4px; padding: 14px; height: 100%; }
    .class-card h4 { font-size: 12px; margin-bottom: 6px; }
    .class-card p { font-size: 11px; color: #343A40; margin: 0; line-height: 1.5; }
    /* Login */
    .login-box { max-width: 400px; margin: 80px auto; padding: 40px; border: 1px solid #DEE2E6; border-radius: 10px; background: #fff; text-align: center; }
    .login-logo { font-size: 48px; margin-bottom: 16px; }
    .login-title { font-size: 22px; font-weight: 700; color: #1B3A5C; margin-bottom: 4px; }
    .login-sub { font-size: 13px; color: #6C757D; margin-bottom: 24px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} .stDeployButton {display: none;} header[data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# AUTENTICAÇÃO COM SENHA
# =============================================================================
SENHA_CORRETA = "Delga01"
DADOS_PATH = "/tmp/delga_dados.pkl"

def check_password():
    """Verifica senha e retorna True se autenticado."""
    if st.session_state.get("autenticado"):
        return True

    st.markdown("""<div class="login-box">
        <div class="login-logo">📊</div>
        <div class="login-title">Grupo Delga 2026</div>
        <div class="login-sub">Dashboard Executivo — Acesso Restrito</div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha = st.text_input("🔒 Senha de acesso", type="password", placeholder="Digite a senha...")
        if st.button("Entrar", use_container_width=True, type="primary"):
            if senha == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
    return False

if not check_password():
    st.stop()

# =============================================================================
# FUNÇÕES DE FORMATAÇÃO
# =============================================================================
def format_currency(value, decimals=0):
    if pd.isna(value) or value is None:
        return "R$ 0"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f} Mi"
    elif abs(value) >= 1_000:
        formatted = f"{value:,.{decimals}f}"
        return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"R$ {value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_currency_table(value):
    if pd.isna(value) or value is None or value == 0:
        return "R$ 0"
    value = float(value)
    formatted = f"{value:,.0f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")

def format_pct(value):
    if pd.isna(value) or value is None:
        return "0,0%"
    return f"{float(value) * 100:.1f}%".replace(".", ",")

# =============================================================================
# CARREGAMENTO E PERSISTÊNCIA DE DADOS
# =============================================================================
@st.cache_data
def load_data(file_bytes):
    """Carrega e processa os dados do Excel a partir de bytes."""
    import io
    buf = io.BytesIO(file_bytes)
    data = {}
    data["5_unidades"] = pd.read_excel(buf, sheet_name="5 Unidades  +", header=None)
    buf.seek(0)
    data["pareto"] = pd.read_excel(buf, sheet_name="Pareto", header=None)
    for planta in ["Diadema", "Jarinu", "Ferraz", "São Leopoldo", "Anchieta"]:
        buf.seek(0)
        data[planta] = pd.read_excel(buf, sheet_name=planta, header=None)
    for area in ["Compras ", "Vendas", "Corporativo"]:
        buf.seek(0)
        data[area.strip()] = pd.read_excel(buf, sheet_name=area, header=None)
    return data

def save_data_to_disk(file_bytes):
    with open(DADOS_PATH, "wb") as f:
        pickle.dump(file_bytes, f)

def load_data_from_disk():
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH, "rb") as f:
            return pickle.load(f)
    return None

# =============================================================================
# EXTRAÇÃO DE DADOS — 100% VERIFICADO
# =============================================================================
def extract_kpis(data):
    df = data["5_unidades"]
    return {
        "meta_grupo":       df.iloc[6, 3],   # R$ 50.320.000
        "retorno_previsto": df.iloc[6, 5],   # R$ 48.287.138
        "previsto_2026":    df.iloc[6, 6],   # R$ 21.759.476
        "validado_custos":  df.iloc[6, 7],   # R$ 16.843.791
        "retorno_real":     df.iloc[6, 9],   # R$ 4.978.229
        "pct_atingimento":  df.iloc[6, 11],  # 9,89%
        "iniciativas":      df.iloc[6, 13],  # 204
    }

def extract_plantas_data(data):
    """
    Colunas verificadas da row 20:
    col3='-', col4=Diadema, col5=Ferraz, col6=São Leopoldo,
    col7=Jarinu, col8=Anchieta, col9=Corporativo, col10=Compras, col11=Vendas
    """
    df = data["5_unidades"]
    plantas = [
        {"nome": "Diadema",       "col": 4,  "sheet": "Diadema"},
        {"nome": "Ferraz",        "col": 5,  "sheet": "Ferraz"},
        {"nome": "São Leopoldo",  "col": 6,  "sheet": "São Leopoldo"},
        {"nome": "Jarinu",        "col": 7,  "sheet": "Jarinu"},
        {"nome": "Anchieta",      "col": 8,  "sheet": "Anchieta"},
    ]
    result = []
    for p in plantas:
        col = p["col"]
        meta      = df.iloc[21, col]  # META DA UNIDADE
        previsto  = df.iloc[22, col]  # RETORNO PREVISTO
        validado  = df.iloc[24, col]  # RETORNO VALIDADO
        real      = df.iloc[25, col]  # RETORNO REAL
        pct       = df.iloc[26, col]  # % ATINGIMENTO

        # Previsto 2026 — cada planta tem layout próprio
        df_p = data.get(p["sheet"])
        if df_p is not None:
            # Verificado: col3 para todas as plantas industriais (row4 = valores)
            previsto_2026 = df_p.iloc[4, 3]
        else:
            previsto_2026 = 0

        result.append({
            "planta": p["nome"],
            "meta_2026":      float(meta)      if pd.notna(meta)      else 0,
            "previsto_total": float(previsto)  if pd.notna(previsto)  else 0,
            "previsto_2026":  float(previsto_2026) if pd.notna(previsto_2026) else 0,
            "validado_custos":float(validado)  if pd.notna(validado)  else 0,
            "real_dre":       float(real)      if pd.notna(real)      else 0,
            "pct_exec_meta":  float(pct)       if pd.notna(pct)       else 0,
        })
    return result

def extract_areas_data(data):
    """
    Áreas funcionais — cols verificadas:
    col9=Corporativo, col10=Compras, col11=Vendas
    """
    df = data["5_unidades"]
    areas = [
        {"nome": "Corporativo", "col": 9,  "sheet": "Corporativo"},
        {"nome": "Compras",     "col": 10, "sheet": "Compras"},
        {"nome": "Vendas",      "col": 11, "sheet": "Vendas"},
    ]
    result = []
    for a in areas:
        col = a["col"]
        meta      = df.iloc[21, col]
        previsto  = df.iloc[22, col]
        validado  = df.iloc[24, col]
        real      = df.iloc[25, col]
        pct       = df.iloc[26, col]

        df_a = data.get(a["sheet"])
        if df_a is not None and a["sheet"] != "Corporativo":
            previsto_2026 = df_a.iloc[4, 4]
        else:
            previsto_2026 = 0

        result.append({
            "area": a["nome"],
            "meta_2026":      float(meta)      if pd.notna(meta)      else 0,
            "previsto_total": float(previsto)  if pd.notna(previsto)  else 0,
            "previsto_2026":  float(previsto_2026) if pd.notna(previsto_2026) else 0,
            "validado_custos":float(validado)  if pd.notna(validado)  else 0,
            "real_dre":       float(real)      if pd.notna(real)      else 0,
            "pct_exec_meta":  float(pct)       if pd.notna(pct)       else 0,
        })
    return result

def extract_pilares(data):
    """
    Pilares (rows 12-16):
    Kaizen, Redução de Custo, Você Resolve, BSW, Estratégia Comercial
    """
    df = data["5_unidades"]
    pilares = []
    for i in range(12, 17):
        nome     = df.iloc[i, 3]
        qtd      = df.iloc[i, 4]
        saving   = df.iloc[i, 5]
        validado = df.iloc[i, 6]
        pct      = df.iloc[i, 7]
        if pd.notna(nome) and nome != "TOTAL":
            pilares.append({
                "pilar":    nome,
                "qtd":      int(qtd)         if pd.notna(qtd)      else 0,
                "previsto": float(saving)    if pd.notna(saving)   else 0,
                "validado": float(validado)  if pd.notna(validado) else 0,
                "pct_total":float(pct)       if pd.notna(pct)      else 0,
            })
    return pilares

def extract_status_iniciativas(data):
    """Status das iniciativas: rows 12-14, cols 8-10"""
    df = data["5_unidades"]
    status = []
    for i in range(12, 15):
        nome  = df.iloc[i, 8]
        qtd   = df.iloc[i, 9]
        valor = df.iloc[i, 10]
        if pd.notna(nome):
            status.append({
                "status": nome,
                "qtd":    int(qtd)       if pd.notna(qtd)   else 0,
                "valor":  float(valor)   if pd.notna(valor) else 0,
            })
    return status

def extract_projetos_ranking(data):
    """
    Lista de projetos rankiados (rows 53-136, col3=posição, col4=unidade, col5=nome,
    col7=status, col8=status_custos, col9=previsto_2026, col10=previsto_momento, col11=real)
    """
    df = data["5_unidades"]
    projetos = []
    for i in range(53, 137):
        posicao    = df.iloc[i, 3]
        unidade    = df.iloc[i, 4]
        nome       = df.iloc[i, 5]
        status     = df.iloc[i, 7]
        st_custos  = df.iloc[i, 8]
        prev_2026  = df.iloc[i, 9]
        prev_mom   = df.iloc[i, 10]
        real       = df.iloc[i, 11]
        if pd.notna(unidade) and pd.notna(nome):
            projetos.append({
                "posicao":         int(posicao)       if pd.notna(posicao)   else i-52,
                "unidade":         str(unidade),
                "projeto":         str(nome),
                "status":          str(status)        if pd.notna(status)    else "",
                "status_custos":   str(st_custos)     if pd.notna(st_custos) else "",
                "previsto_2026":   float(prev_2026)   if pd.notna(prev_2026) else 0,
                "previsto_momento":float(prev_mom)    if pd.notna(prev_mom)  else 0,
                "real":            float(real)        if pd.notna(real)      else 0,
            })
    return projetos

def extract_evolucao_mensal(data):
    """
    Evolução mensal (rows 53-58, cols 22-33):
    Row 53 = Previsto mensal
    Row 54 = Real mensal
    Row 56 = Acumulado Previsto
    Row 57 = Acumulado Real
    Row 58 = Projeção da Meta
    """
    df = data["5_unidades"]
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    def get_row(row_idx):
        vals = []
        for c in range(22, 34):
            v = df.iloc[row_idx, c]
            vals.append(float(v) if pd.notna(v) else 0)
        return vals

    return {
        "meses":          meses,
        "previsto":       get_row(53),
        "real":           get_row(54),
        "acum_previsto":  get_row(56),
        "acum_real":      get_row(57),
        "projecao_meta":  get_row(58),
    }

def extract_top_projetos(data):
    """Top 3 projetos por retorno real (col15, rows 6-8)."""
    df = data["5_unidades"]
    top = []
    for i in range(6, 9):
        v = df.iloc[i, 15]
        top.append(float(v) if pd.notna(v) else 0)
    return top

# =============================================================================
# GRÁFICOS
# =============================================================================
def create_donut_chart(labels, values, colors, title_total):
    total = sum(values)
    custom_text = [f"{labels[i]}  {values[i]/total*100:.1f}%  {format_currency(values[i])}"
                   for i in range(len(labels))]
    fig = go.Figure(data=[go.Pie(
        labels=custom_text, values=values, hole=0.6,
        marker=dict(colors=colors), textinfo="none",
        hovertemplate="<b>%{label}</b><extra></extra>",
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.55, font=dict(size=11)),
        margin=dict(l=10, r=10, t=10, b=40),
        height=300,
        paper_bgcolor="white", plot_bgcolor="white",
        annotations=[dict(text=f"<b>Total: {format_currency(sum(values))}</b>",
                          x=0.22, y=-0.1, font_size=12, showarrow=False)],
    )
    return fig

def create_funnel_chart(kpis):
    stages = ["Meta Grupo", "Portfólio Previsto", "Previsto 2026", "Validado Custos", "Real DRE"]
    values = [kpis["meta_grupo"], kpis["retorno_previsto"], kpis["previsto_2026"],
              kpis["validado_custos"], kpis["retorno_real"]]
    colors = ["#1B3A5C", "#C87533", "#E8A838", "#2C5F8A", "#1A7A3A"]
    fig = go.Figure(go.Bar(
        x=values, y=stages, orientation="h",
        marker=dict(color=colors),
        text=[format_currency(v) for v in values],
        textposition="outside", textfont=dict(size=11),
    ))
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="#E8E8E8", range=[0, max(values) * 1.25]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=120, r=100, t=10, b=30),
        height=300, paper_bgcolor="white", plot_bgcolor="white",
    )
    return fig

def create_bar_pilares(pilares, kpis):
    labels   = [p["pilar"] for p in pilares]
    previsto = [p["previsto"] for p in pilares]
    validado = [p["validado"] for p in pilares]
    real_total = float(kpis["retorno_real"])
    total_val  = sum(validado)
    real_est   = [v / total_val * real_total if total_val > 0 else 0 for v in validado]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Previsto", x=labels, y=previsto, marker_color="#B8D4E8"))
    fig.add_trace(go.Bar(name="Validado", x=labels, y=validado, marker_color="#2C5F8A"))
    fig.add_trace(go.Bar(name="Real DRE", x=labels, y=real_est,  marker_color="#1A7A3A"))
    fig.update_layout(
        barmode="group",
        yaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#E8E8E8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=20, t=40, b=60),
        height=320, paper_bgcolor="white", plot_bgcolor="white", bargap=0.3,
    )
    return fig

def create_evolucao_chart(evolucao, series_selecionadas):
    meses = evolucao["meses"]
    config = {
        "Acumulado Previsto": {"data": evolucao["acum_previsto"],  "color": "#2C5F8A", "dash": "solid"},
        "Acumulado Real":     {"data": evolucao["acum_real"],      "color": "#1A7A3A", "dash": "solid"},
        "Projeção da Meta":   {"data": evolucao["projecao_meta"],  "color": "#E8A838", "dash": "dash"},
        "Previsto Mensal":    {"data": evolucao["previsto"],       "color": "#4A90D9", "dash": "dot"},
        "Real Mensal":        {"data": evolucao["real"],           "color": "#28A745", "dash": "dot"},
    }
    fig = go.Figure()
    for nome in series_selecionadas:
        cfg = config[nome]
        fig.add_trace(go.Scatter(
            x=meses, y=cfg["data"], mode="lines+markers", name=nome,
            line=dict(color=cfg["color"], width=2.5, dash=cfg["dash"]),
            marker=dict(size=6),
            hovertemplate=f"<b>{nome}</b><br>%{{x}}: R$ %{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(title="R$", tickformat=",.0f", showgrid=True, gridcolor="#E8E8E8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=11)),
        margin=dict(l=80, r=20, t=50, b=40),
        height=420, paper_bgcolor="white", plot_bgcolor="white", hovermode="x unified",
    )
    return fig

def create_gauge_atingimento(pct):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct * 100,
        number={"suffix": "%", "font": {"size": 36, "color": "#1B3A5C"}},
        delta={"reference": 100, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": "#1A7A3A"},
            "steps": [
                {"range": [0, 30],  "color": "#FFEBEE"},
                {"range": [30, 60], "color": "#FFF8E1"},
                {"range": [60, 100],"color": "#E8F5E9"},
            ],
            "threshold": {"line": {"color": "#E8A838", "width": 3}, "thickness": 0.75, "value": 100},
        },
        title={"text": "% Atingimento da Meta", "font": {"size": 14}},
    ))
    fig.update_layout(height=280, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor="white")
    return fig

# =============================================================================
# RENDERIZAÇÃO HTML
# =============================================================================
def render_progress_bar(pct):
    width = min(float(pct) * 100, 100)
    color = "#1A7A3A" if pct >= 0.30 else ("#E8A838" if pct >= 0.15 else "#DC3545")
    return f"""<div class="progress-container">
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{width}%;background-color:{color};"></div></div>
        <span style="font-size:12px;font-weight:600;">{pct*100:.1f}%</span>
    </div>"""

def render_status_badge(pct):
    if pct >= 0.30:
        return '<span class="badge-destaque">DESTAQUE ✓</span>'
    return '<span class="badge-execucao">EM EXECUÇÃO</span>'

def render_table_plantas(plantas_data):
    rows = ""
    totais = {"meta":0, "prev":0, "prev2026":0, "val":0, "real":0}
    for p in plantas_data:
        totais["meta"]    += p["meta_2026"]
        totais["prev"]    += p["previsto_total"]
        totais["prev2026"]+= p["previsto_2026"]
        totais["val"]     += p["validado_custos"]
        totais["real"]    += p["real_dre"]
        rows += f"""<tr>
            <td><b>{p['planta']}</b></td>
            <td>{format_currency_table(p['meta_2026'])}</td>
            <td>{format_currency_table(p['previsto_total'])}</td>
            <td class="color-orange-text">{format_currency_table(p['previsto_2026'])}</td>
            <td class="color-teal">{format_currency_table(p['validado_custos'])}</td>
            <td>{format_currency_table(p['real_dre'])}</td>
            <td>{render_progress_bar(p['pct_exec_meta'])}</td>
            <td>{render_status_badge(p['pct_exec_meta'])}</td>
        </tr>"""
    pct_total = totais["real"] / totais["meta"] if totais["meta"] > 0 else 0
    rows += f"""<tr>
        <td><b>TOTAL</b></td>
        <td><b>{format_currency_table(totais['meta'])}</b></td>
        <td><b>{format_currency_table(totais['prev'])}</b></td>
        <td class="color-orange-text"><b>{format_currency_table(totais['prev2026'])}</b></td>
        <td class="color-teal"><b>{format_currency_table(totais['val'])}</b></td>
        <td><b>{format_currency_table(totais['real'])}</b></td>
        <td><b>{render_progress_bar(pct_total)}</b></td>
        <td></td>
    </tr>"""
    return f"""<table class="custom-table"><thead><tr>
        <th>Planta</th><th>Meta 2026</th><th>Previsto Total</th>
        <th style="color:#E8A838;">Previsto 2026</th>
        <th style="color:#20C997;">Validado (Custos)</th>
        <th style="color:#28A745;">Real (DRE)</th>
        <th>% Exec. Meta</th><th>Status</th>
    </tr></thead><tbody>{rows}</tbody></table>"""

def render_table_areas(areas_data):
    rows = ""
    totais = {"meta":0, "prev":0, "prev2026":0, "val":0, "real":0}
    for a in areas_data:
        totais["meta"]    += a["meta_2026"]
        totais["prev"]    += a["previsto_total"]
        totais["prev2026"]+= a["previsto_2026"]
        totais["val"]     += a["validado_custos"]
        totais["real"]    += a["real_dre"]
        rows += f"""<tr>
            <td><b>{a['area']}</b></td>
            <td>{format_currency_table(a['meta_2026'])}</td>
            <td>{format_currency_table(a['previsto_total'])}</td>
            <td class="color-orange-text">{format_currency_table(a['previsto_2026'])}</td>
            <td class="color-teal">{format_currency_table(a['validado_custos'])}</td>
            <td>{format_currency_table(a['real_dre'])}</td>
            <td>{render_progress_bar(a['pct_exec_meta'])}</td>
            <td>{render_status_badge(a['pct_exec_meta'])}</td>
        </tr>"""
    pct_total = totais["real"] / totais["meta"] if totais["meta"] > 0 else 0
    rows += f"""<tr>
        <td><b>TOTAL</b></td>
        <td><b>{format_currency_table(totais['meta'])}</b></td>
        <td><b>{format_currency_table(totais['prev'])}</b></td>
        <td class="color-orange-text"><b>{format_currency_table(totais['prev2026'])}</b></td>
        <td class="color-teal"><b>{format_currency_table(totais['val'])}</b></td>
        <td><b>{format_currency_table(totais['real'])}</b></td>
        <td><b>{render_progress_bar(pct_total)}</b></td>
        <td></td>
    </tr>"""
    return f"""<table class="custom-table"><thead><tr>
        <th>Área Funcional</th><th>Meta 2026</th><th>Previsto Total</th>
        <th style="color:#E8A838;">Previsto 2026</th>
        <th style="color:#20C997;">Validado (Custos)</th>
        <th style="color:#28A745;">Real (DRE)</th>
        <th>% Exec. Meta</th><th>Status</th>
    </tr></thead><tbody>{rows}</tbody></table>"""

def render_ranking_projetos(projetos, max_rows=20):
    """Renderiza tabela de ranking top N projetos."""
    rows = ""
    for p in projetos[:max_rows]:
        st_color = "#1A7A3A" if "Concluído" in p["status"] else "#E8A838"
        custos_badge = ""
        if p["status_custos"] == "OK":
            custos_badge = '<span style="color:#1A7A3A;font-weight:700;">✓ OK</span>'
        elif p["status_custos"] == "Não Ok":
            custos_badge = '<span style="color:#DC3545;font-weight:700;">✗ Não OK</span>'
        else:
            custos_badge = '<span style="color:#E8A838;">⏳ Pendente</span>'

        rows += f"""<tr>
            <td style="text-align:center;font-weight:700;color:#6C757D;">{p['posicao']}</td>
            <td><b>{p['unidade']}</b></td>
            <td>{p['projeto']}</td>
            <td><span style="color:{st_color};font-size:11px;">{p['status']}</span></td>
            <td>{custos_badge}</td>
            <td style="text-align:right;">{format_currency_table(p['previsto_2026'])}</td>
            <td style="text-align:right;">{format_currency_table(p['previsto_momento'])}</td>
            <td style="text-align:right;font-weight:700;color:#1A7A3A;">{format_currency_table(p['real'])}</td>
        </tr>"""
    return f"""<table class="custom-table"><thead><tr>
        <th style="width:40px;">#</th>
        <th>Unidade</th><th>Projeto</th><th>Status</th><th>Custos</th>
        <th style="text-align:right;">Previsto 2026</th>
        <th style="text-align:right;">Previsto Momento</th>
        <th style="text-align:right;color:#28A745;">Real (DRE)</th>
    </tr></thead><tbody>{rows}</tbody></table>"""

def render_gap_nao_validado(projetos):
    """Projetos sem validação de custos agrupados por unidade."""
    gap = [p for p in projetos if p["status_custos"] not in ["OK", "Não Ok"] and p["previsto_2026"] > 0]
    por_unidade = {}
    for p in gap:
        u = p["unidade"]
        por_unidade[u] = por_unidade.get(u, 0) + p["previsto_2026"]
    sorted_u = sorted(por_unidade.items(), key=lambda x: x[1], reverse=True)
    total = sum(v for _, v in sorted_u)
    rows = ""
    for u, v in sorted_u:
        pct = v / total * 100 if total > 0 else 0
        rows += f"""<tr>
            <td style="font-weight:600;">{u}</td>
            <td class="color-orange-text" style="text-align:right;">{format_currency_table(v)}</td>
            <td style="text-align:right;">{pct:.1f}%</td>
        </tr>"""
    rows += f"""<tr>
        <td><b>TOTAL GAP</b></td>
        <td class="color-orange-text" style="text-align:right;"><b>{format_currency_table(total)}</b></td>
        <td style="text-align:right;"><b>100%</b></td>
    </tr>"""
    n_projetos = len(gap)
    return f"""<p style="font-size:11px;color:#6C757D;margin-bottom:8px;">
        {n_projetos} projetos aguardam validação do depto de Custos</p>
    <table class="custom-table"><thead><tr>
        <th>Unidade</th>
        <th style="text-align:right;color:#E8A838;">Previsto 2026 (não validado)</th>
        <th style="text-align:right;">% do Gap</th>
    </tr></thead><tbody>{rows}</tbody></table>"""

# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================
st.markdown('<p class="main-header">📊 Dashboard Executivo — Grupo Delga 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Gestão Estratégica de Projetos e Redução de Custos | Atualizado: Jun/2026</p>', unsafe_allow_html=True)

# ----- PAINEL DE UPLOAD (somente admin com senha) -----
with st.expander("🔐 Administrador — Atualizar Planilha", expanded=False):
    st.markdown("**Faça upload de uma nova versão da planilha para atualizar o dashboard para todos os usuários.**")
    arquivo = st.file_uploader(
        "📁 Carregar nova versão (.xlsx)",
        type=["xlsx"],
        help="O arquivo substituirá os dados exibidos para todos que acessarem o link.",
        key="admin_upload",
    )
    if arquivo is not None:
        file_bytes = arquivo.read()
        save_data_to_disk(file_bytes)
        st.cache_data.clear()
        st.success("✅ Planilha atualizada com sucesso! Todos os usuários verão os novos dados.")

# ----- CARREGAMENTO DOS DADOS -----
file_bytes = load_data_from_disk()

if file_bytes is None:
    st.markdown("""<div style="text-align:center;padding:80px 20px;background:#FFF8E1;border-radius:8px;border:1px solid #FFE082;margin-top:20px;">
        <p style="font-size:48px;margin-bottom:16px;">⚠️</p>
        <p style="font-size:18px;font-weight:600;color:#1B3A5C;">Nenhuma planilha carregada ainda</p>
        <p style="font-size:13px;color:#6C757D;margin-top:8px;">
            Expanda o painel <b>Administrador</b> acima e faça o upload da planilha para ativar o dashboard.
        </p>
    </div>""", unsafe_allow_html=True)
    st.stop()

try:
    data = load_data(file_bytes)
except Exception as e:
    st.error(f"❌ Erro ao processar a planilha: {e}")
    st.stop()

# Extrair todos os dados
kpis         = extract_kpis(data)
plantas_data = extract_plantas_data(data)
areas_data   = extract_areas_data(data)
pilares      = extract_pilares(data)
status_inic  = extract_status_iniciativas(data)
projetos     = extract_projetos_ranking(data)
evolucao     = extract_evolucao_mensal(data)

# =============================================================================
# KPI CARDS — 5 MÉTRICAS PRINCIPAIS
# =============================================================================
c1, c2, c3, c4, c5 = st.columns(5)
meta        = float(kpis["meta_grupo"])
ret_prev    = float(kpis["retorno_previsto"])
prev_2026   = float(kpis["previsto_2026"])
val_custos  = float(kpis["validado_custos"])
ret_real    = float(kpis["retorno_real"])
pct_ating   = float(kpis["pct_atingimento"])
iniciativas = int(kpis["iniciativas"])

with c1:
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">META ANUAL DO GRUPO</p>
        <p class="kpi-value color-primary">{format_currency(meta)}</p>
        <p class="kpi-sub">{format_currency_table(meta)}</p>
        <p class="kpi-detail">Objetivo 2026 — 100%</p>
    </div>""", unsafe_allow_html=True)

with c2:
    cob = ret_prev / meta * 100
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">PORTFÓLIO PREVISTO</p>
        <p class="kpi-value color-green">{format_currency(ret_prev)}</p>
        <p class="kpi-sub">{format_currency_table(ret_prev)}</p>
        <p class="kpi-detail">{cob:.1f}% da meta coberta · {iniciativas} iniciativas</p>
    </div>""", unsafe_allow_html=True)

with c3:
    pct_prev = prev_2026 / ret_prev * 100 if ret_prev > 0 else 0
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">PREVISTO 2026 (PROJETADO)</p>
        <p class="kpi-value color-orange">{format_currency(prev_2026)}</p>
        <p class="kpi-sub">{format_currency_table(prev_2026)}</p>
        <p class="kpi-detail">{pct_prev:.1f}% do portfólio total</p>
    </div>""", unsafe_allow_html=True)

with c4:
    pct_val = val_custos / prev_2026 * 100 if prev_2026 > 0 else 0
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">VALIDADO POR CUSTOS</p>
        <p class="kpi-value color-primary">{format_currency(val_custos)}</p>
        <p class="kpi-sub">{format_currency_table(val_custos)}</p>
        <p class="kpi-detail">{pct_val:.1f}% do Previsto 2026</p>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">RETORNO REAL (DRE)</p>
        <p class="kpi-value color-green">{format_currency(ret_real)}</p>
        <p class="kpi-sub">{format_currency_table(ret_real)}</p>
        <p class="kpi-detail">{pct_ating*100:.1f}% de atingimento da meta</p>
    </div>""", unsafe_allow_html=True)

# =============================================================================
# NOTA METODOLÓGICA
# =============================================================================
st.markdown("""<div class="nota-metodologica">
    <b>Nota metodológica — Tipos de Ganho:</b>
    <b>Redução de Custo</b> (impacto direto e tangível no DRE) |
    <b>Custo Evitado</b> (ganho real, MO realocada internamente — não reduz GGF no DRE) |
    <b>Capital de Giro</b> (redução de estoque, melhora caixa mas não o DRE diretamente).
    Kaizens de Custo Evitado e Capital de Giro geram valor, mas não reduzem GGF de forma tangível.
</div>""", unsafe_allow_html=True)

# =============================================================================
# EVOLUÇÃO MENSAL
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title">EVOLUÇÃO MENSAL — ACUMULADO PREVISTO vs REAL vs META</p>', unsafe_allow_html=True)
series_opcoes  = ["Acumulado Previsto", "Acumulado Real", "Projeção da Meta", "Previsto Mensal", "Real Mensal"]
series_default = ["Acumulado Previsto", "Acumulado Real", "Projeção da Meta"]
series_sel = st.multiselect("Séries:", options=series_opcoes, default=series_default, key="ev_series")
if series_sel:
    st.plotly_chart(create_evolucao_chart(evolucao, series_sel), use_container_width=True, config={"displayModeBar": False})
else:
    st.info("Selecione ao menos uma série.")
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# GAUGE + FUNIL
# =============================================================================
col_g1, col_g2 = st.columns([1, 2])

with col_g1:
    st.markdown('<div class="section-box" style="height:340px;">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">ATINGIMENTO DA META</p>', unsafe_allow_html=True)
    st.plotly_chart(create_gauge_atingimento(pct_ating), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_g2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">FUNIL DE CONVERSÃO — PORTFÓLIO → DRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;color:#6C757D;margin-bottom:8px;">Quanto do portfólio mapeado efetivamente se converte em resultado no DRE?</p>', unsafe_allow_html=True)
    st.plotly_chart(create_funnel_chart(kpis), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# DONUTS
# =============================================================================
col_d1, col_d2 = st.columns(2)
with col_d1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title" style="text-align:center;">REPRESENTATIVIDADE — PLANTAS INDUSTRIAIS</p>', unsafe_allow_html=True)
    lbls  = [p["planta"] for p in plantas_data]
    vals  = [p["meta_2026"] for p in plantas_data]
    clrs  = ["#1B3A5C", "#2C5F8A", "#4A90D9", "#A8C8E8", "#D4E6F1"]
    st.plotly_chart(create_donut_chart(lbls, vals, clrs, ""), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_d2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title" style="text-align:center;">REPRESENTATIVIDADE — ÁREAS FUNCIONAIS</p>', unsafe_allow_html=True)
    lbls2 = [a["area"] for a in areas_data]
    vals2 = [a["meta_2026"] for a in areas_data]
    clrs2 = ["#1B3A5C", "#28A745", "#20C997"]
    st.plotly_chart(create_donut_chart(lbls2, vals2, clrs2, ""), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TABELA PLANTAS INDUSTRIAIS
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title">PLANTAS INDUSTRIAIS — PERFORMANCE CONSOLIDADA</p>', unsafe_allow_html=True)
st.markdown(render_table_plantas(plantas_data), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TABELA ÁREAS FUNCIONAIS
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title">ÁREAS FUNCIONAIS — PERFORMANCE CONSOLIDADA</p>', unsafe_allow_html=True)
st.markdown(render_table_areas(areas_data), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# DISTRIBUIÇÃO POR TIPO DE INICIATIVA + STATUS
# =============================================================================
col_b1, col_b2 = st.columns([3, 2])

with col_b1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">DISTRIBUIÇÃO POR TIPO DE INICIATIVA</p>', unsafe_allow_html=True)
    st.plotly_chart(create_bar_pilares(pilares, kpis), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_b2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">STATUS DAS INICIATIVAS</p>', unsafe_allow_html=True)
    for s in status_inic:
        pct_s = s["valor"] / ret_prev * 100 if ret_prev > 0 else 0
        st.markdown(f"""<div style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:12px;font-weight:600;">{s['status']}</span>
                <span style="font-size:12px;">{s['qtd']} proj · {format_currency(s['valor'])}</span>
            </div>
            <div class="progress-bar-bg" style="width:100%;height:12px;">
                <div class="progress-bar-fill" style="width:{min(pct_s,100):.1f}%;background-color:#2C5F8A;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Resumo pilares em tabela simples
    st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;font-weight:700;color:#1B3A5C;text-transform:uppercase;">Resumo por Pilar</p>', unsafe_allow_html=True)
    rows_p = ""
    for p in pilares:
        rows_p += f"""<tr>
            <td style="font-size:11px;">{p['pilar']}</td>
            <td style="text-align:center;font-size:11px;">{p['qtd']}</td>
            <td style="text-align:right;font-size:11px;">{format_currency(p['previsto'])}</td>
            <td style="text-align:right;font-size:11px;color:#20C997;">{format_currency(p['validado'])}</td>
        </tr>"""
    st.markdown(f"""<table class="custom-table"><thead><tr>
        <th>Pilar</th><th style="text-align:center;">Qtd</th>
        <th style="text-align:right;">Previsto</th>
        <th style="text-align:right;color:#20C997;">Validado</th>
    </tr></thead><tbody>{rows_p}</tbody></table>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# CLASSIFICAÇÃO DE GANHOS
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title">CLASSIFICAÇÃO DE GANHOS — PROPOSTA DE DIFERENCIAÇÃO</p>', unsafe_allow_html=True)
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    st.markdown("""<div class="class-card" style="border: 2px solid #2C5F8A;">
        <h4 style="color:#2C5F8A;">🔥 REDUÇÃO DE CUSTO</h4>
        <p>Impacto direto e tangível no DRE. Reduz GGF de forma mensurável.<br>
        <i>Ex: redução de MP, troca de fornecedor, eliminação de operação.</i></p>
    </div>""", unsafe_allow_html=True)
with col_c2:
    st.markdown("""<div class="class-card" style="border: 2px solid #E8A838;">
        <h4 style="color:#E8A838;">⚡ CUSTO EVITADO</h4>
        <p>Gera produtividade real, mas MO é realocada internamente — não reduz GGF no DRE.<br>
        <i>Ex: Kaizens que eliminam postos mas realocam MO para outro posto.</i></p>
    </div>""", unsafe_allow_html=True)
with col_c3:
    st.markdown("""<div class="class-card" style="border: 2px solid #1A7A3A;">
        <h4 style="color:#1A7A3A;">🏦 CAPITAL DE GIRO</h4>
        <p>Redução de estoque e melhora do fluxo de caixa. Impacto no balanço, não no DRE.<br>
        <i>Ex: redução de estoque de matéria-prima.</i></p>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# RANKING DE PROJETOS
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title">RANKING DE PROJETOS — TODOS OS PILARES</p>', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
with col_f1:
    filtro_unidade = st.multiselect(
        "Filtrar por Unidade:",
        options=sorted(set(p["unidade"] for p in projetos)),
        default=[],
        key="filtro_unidade",
        placeholder="Todas as unidades",
    )
with col_f2:
    filtro_status = st.multiselect(
        "Filtrar por Status:",
        options=sorted(set(p["status"] for p in projetos if p["status"])),
        default=[],
        key="filtro_status",
        placeholder="Todos os status",
    )
with col_f3:
    max_rows = st.number_input("Linhas exibidas:", min_value=5, max_value=200, value=20, step=5)

proj_filtrados = projetos
if filtro_unidade:
    proj_filtrados = [p for p in proj_filtrados if p["unidade"] in filtro_unidade]
if filtro_status:
    proj_filtrados = [p for p in proj_filtrados if p["status"] in filtro_status]

st.markdown(f'<p style="font-size:11px;color:#6C757D;margin-bottom:8px;">Exibindo {min(max_rows, len(proj_filtrados))} de {len(proj_filtrados)} projetos filtrados</p>', unsafe_allow_html=True)
st.markdown(render_ranking_projetos(proj_filtrados, int(max_rows)), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# GAP NÃO VALIDADO
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title" style="color:#E8A838;">GAP — PROJETOS PREVISTO 2026 AGUARDANDO VALIDAÇÃO DE CUSTOS</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:11px;color:#6C757D;margin-bottom:12px;">Projetos com valor projetado mas ainda sem validação do departamento de Custos. Este é o principal alavancador do pipeline.</p>', unsafe_allow_html=True)
st.markdown(render_gap_nao_validado(projetos), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
col_ft1, col_ft2, col_ft3 = st.columns(3)
with col_ft1:
    st.markdown(f'<p style="font-size:11px;color:#6C757D;">📊 Dashboard Executivo — Grupo Delga 2026</p>', unsafe_allow_html=True)
with col_ft2:
    st.markdown(f'<p style="font-size:11px;color:#6C757D;text-align:center;">Gestão Estratégica de Projetos e Redução de Custos</p>', unsafe_allow_html=True)
with col_ft3:
    if st.button("🚪 Sair", key="logout"):
        st.session_state["autenticado"] = False
        st.rerun()
