import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings

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
    /* Reset e base */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
    }
    /* Header */
    .main-header {
        font-size: 28px;
        font-weight: 700;
        color: #1B3A5C;
        margin-bottom: 0;
        line-height: 1.2;
    }
    .sub-header {
        font-size: 13px;
        color: #6C757D;
        margin-bottom: 20px;
    }
    /* KPI Cards */
    .kpi-card {
        border: 1px solid #DEE2E6;
        border-radius: 6px;
        padding: 16px 18px;
        background-color: #FFFFFF;
        height: 100%;
    }
    .kpi-title {
        font-size: 10px;
        font-weight: 600;
        color: #6C757D;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        margin: 4px 0;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 12px;
        color: #343A40;
        margin-bottom: 2px;
    }
    .kpi-detail {
        font-size: 11px;
        color: #6C757D;
    }
    /* Cores dos KPIs */
    .color-primary { color: #1B3A5C; }
    .color-green { color: #1A7A3A; }
    .color-orange { color: #E8A838; }
    /* Nota metodológica */
    .nota-metodologica {
        background-color: #FFF8E1;
        border: 1px solid #FFE082;
        border-radius: 4px;
        padding: 12px 16px;
        font-size: 11px;
        color: #343A40;
        line-height: 1.6;
        margin: 16px 0;
    }
    /* Seções */
    .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #1B3A5C;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .section-box {
        border: 1px solid #DEE2E6;
        border-radius: 6px;
        padding: 16px;
        background-color: #FFFFFF;
        margin-bottom: 16px;
    }
    /* Tabelas */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }
    .custom-table th {
        background-color: #1B3A5C;
        color: white;
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 11px;
    }
    .custom-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #DEE2E6;
    }
    .custom-table tr:last-child td {
        border-top: 2px solid #1B3A5C;
        font-weight: 700;
    }
    .color-teal { color: #20C997; }
    .color-orange-text { color: #E8A838; }
    /* Progress bar */
    .progress-container {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .progress-bar-bg {
        width: 70px;
        height: 8px;
        background-color: #E8E8E8;
        border-radius: 4px;
        overflow: hidden;
        display: inline-block;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
    }
    /* Status badges */
    .badge-execucao {
        background-color: #FFF3E0;
        color: #E8A838;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 600;
    }
    .badge-destaque {
        background-color: #E8F5E9;
        color: #1A7A3A;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 600;
    }
    /* Classificação cards */
    .class-card {
        border-radius: 4px;
        padding: 14px;
        height: 100%;
    }
    .class-card h4 {
        font-size: 12px;
        margin-bottom: 6px;
    }
    .class-card p {
        font-size: 11px;
        color: #343A40;
        margin: 0;
        line-height: 1.5;
    }
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FUNÇÕES DE FORMATAÇÃO
# =============================================================================
def format_currency(value, decimals=0):
    """Formata valor em moeda brasileira abreviada."""
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
    """Formata valor para tabelas."""
    if pd.isna(value) or value is None or value == 0:
        return "R$ 0"
    value = float(value)
    formatted = f"{value:,.0f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_pct(value):
    """Formata percentual."""
    if pd.isna(value) or value is None:
        return "0.0%"
    return f"{float(value) * 100:.1f}%"


# =============================================================================
# CARREGAMENTO DE DADOS
# =============================================================================
@st.cache_data
def load_data(file_path):
    """Carrega e processa os dados do Excel."""
    data = {}
    data["5_unidades"] = pd.read_excel(file_path, sheet_name="5 Unidades  +", header=None)
    data["pareto"] = pd.read_excel(file_path, sheet_name="Pareto", header=None)
    for planta in ["Diadema", "Jarinu", "Ferraz", "São Leopoldo", "Anchieta"]:
        data[planta] = pd.read_excel(file_path, sheet_name=planta, header=None)
    for area in ["Compras ", "Vendas", "Corporativo"]:
        data[area.strip()] = pd.read_excel(file_path, sheet_name=area, header=None)
    return data


def extract_kpis(data):
    """Extrai os KPIs principais."""
    df = data["5_unidades"]
    return {
        "meta_grupo": df.iloc[6, 3],
        "retorno_previsto": df.iloc[6, 5],
        "previsto_2026": df.iloc[6, 6],
        "validado_custos": df.iloc[6, 7],
        "retorno_real": df.iloc[6, 9],
        "pct_atingimento": df.iloc[6, 11],
        "iniciativas": df.iloc[6, 13],
    }


def extract_plantas_data(data):
    """Extrai dados por planta industrial."""
    df = data["5_unidades"]
    plantas = ["Diadema", "Ferraz", "São Leopoldo", "Jarinu", "Anchieta"]
    cols = [4, 5, 6, 7, 8]
    result = []
    for i, planta in enumerate(plantas):
        col = cols[i]
        meta = df.iloc[21, col]
        retorno_previsto = df.iloc[22, col]
        validado = df.iloc[24, col]
        real = df.iloc[25, col]
        pct = df.iloc[26, col]
        df_p = data.get(planta)
        if df_p is not None:
            if planta == "Jarinu":
                previsto_2026 = df_p.iloc[4, 2]
            else:
                previsto_2026 = df_p.iloc[4, 3]
        else:
            previsto_2026 = 0
        result.append({
            "planta": planta,
            "meta_2026": meta,
            "previsto_total": retorno_previsto,
            "previsto_2026": previsto_2026,
            "validado_custos": validado,
            "real_dre": real,
            "pct_exec_meta": pct,
        })
    return result


def extract_areas_data(data):
    """Extrai dados por área funcional."""
    df = data["5_unidades"]
    areas_info = [
        {"nome": "Compras", "col": 10, "sheet": "Compras"},
        {"nome": "Vendas", "col": 11, "sheet": "Vendas"},
        {"nome": "Corporativo", "col": 9, "sheet": "Corporativo"},
    ]
    result = []
    for area in areas_info:
        col = area["col"]
        meta = df.iloc[21, col]
        retorno_previsto = df.iloc[22, col]
        validado = df.iloc[24, col]
        real = df.iloc[25, col]
        pct = df.iloc[26, col]
        df_a = data.get(area["sheet"])
        if df_a is not None and area["sheet"] != "Corporativo":
            previsto_2026 = df_a.iloc[4, 4]
        else:
            previsto_2026 = 0
        result.append({
            "area": area["nome"],
            "meta_2026": meta,
            "previsto_total": retorno_previsto,
            "previsto_2026": previsto_2026,
            "validado_custos": validado,
            "real_dre": real,
            "pct_exec_meta": pct,
        })
    return result


def extract_pilares(data):
    """Extrai dados por pilar/tipo de iniciativa."""
    df = data["5_unidades"]
    pilares = []
    for i in range(12, 17):
        nome = df.iloc[i, 3]
        qtd = df.iloc[i, 4]
        saving = df.iloc[i, 5]
        validado = df.iloc[i, 6]
        pct = df.iloc[i, 7]
        if pd.notna(nome) and nome != "TOTAL":
            pilares.append({
                "pilar": nome,
                "qtd": qtd,
                "previsto": saving,
                "validado": validado,
                "pct_total": pct,
            })
    return pilares


def extract_projetos_validados(data):
    """Extrai projetos com retorno validado por custos."""
    df = data["5_unidades"]
    projetos = []
    for i in range(53, 137):
        unidade = df.iloc[i, 4]
        nome = df.iloc[i, 5]
        status = df.iloc[i, 7]
        status_custos = df.iloc[i, 8]
        previsto_2026 = df.iloc[i, 9]
        previsto_momento = df.iloc[i, 10]
        real = df.iloc[i, 11]
        if pd.notna(unidade) and pd.notna(nome):
            projetos.append({
                "unidade": unidade,
                "projeto": nome,
                "status": status if pd.notna(status) else "",
                "status_custos": status_custos if pd.notna(status_custos) else "",
                "previsto_2026": float(previsto_2026) if pd.notna(previsto_2026) else 0,
                "previsto_momento": float(previsto_momento) if pd.notna(previsto_momento) else 0,
                "real": float(real) if pd.notna(real) else 0,
            })
    return projetos


def extract_pareto_ranking(data):
    """Extrai ranking de projetos do Pareto (coluna Q em diante)."""
    df = data["pareto"]
    projetos = []
    for i in range(3, 203):
        pos = df.iloc[i, 16]
        valor_previsto = df.iloc[i, 17]
        nome = df.iloc[i, 18]
        unidade = df.iloc[i, 19]
        previsto_2026 = df.iloc[i, 20]
        status = df.iloc[i, 23]
        status_custos = df.iloc[i, 25]
        if pd.notna(pos) and pd.notna(nome):
            projetos.append({
                "posicao": int(pos),
                "valor_previsto": float(valor_previsto) if pd.notna(valor_previsto) else 0,
                "projeto": nome,
                "unidade": unidade if pd.notna(unidade) else "",
                "previsto_2026": float(previsto_2026) if pd.notna(previsto_2026) else 0,
                "status": status if pd.notna(status) else "",
                "status_custos": status_custos if pd.notna(status_custos) else "",
            })
    return projetos


# =============================================================================
# GRÁFICOS
# =============================================================================
def create_donut_plantas(plantas_data):
    """Gráfico de donut - representatividade das plantas."""
    labels = [p["planta"] for p in plantas_data]
    metas = [float(p["meta_2026"]) for p in plantas_data]
    total = sum(metas)
    colors = ["#1B3A5C", "#2C5F8A", "#4A90D9", "#A8C8E8", "#D4E6F1"]
    custom_text = [f"{labels[i]}  {metas[i]/total*100:.1f}%  {format_currency(metas[i])}" for i in range(len(labels))]
    fig = go.Figure(data=[go.Pie(
        labels=custom_text,
        values=metas,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo="none",
        hovertemplate="<b>%{label}</b><extra></extra>",
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.55, font=dict(size=11)),
        margin=dict(l=10, r=10, t=10, b=40),
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        annotations=[dict(text=f"<b>Total: {format_currency(total)}</b>", x=0.22, y=-0.1, font_size=12, showarrow=False)],
    )
    return fig


def create_donut_areas(areas_data):
    """Gráfico de donut - representatividade das áreas funcionais."""
    labels = [a["area"] for a in areas_data]
    metas = [float(a["meta_2026"]) for a in areas_data]
    total = sum(metas)
    colors = ["#1B3A5C", "#28A745", "#20C997"]
    custom_text = [f"{labels[i]}  {metas[i]/total*100:.1f}%  {format_currency(metas[i])}" for i in range(len(labels))]
    fig = go.Figure(data=[go.Pie(
        labels=custom_text,
        values=metas,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo="none",
        hovertemplate="<b>%{label}</b><extra></extra>",
    )])
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.55, font=dict(size=11)),
        margin=dict(l=10, r=10, t=10, b=40),
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        annotations=[dict(text=f"<b>Total: {format_currency(total)}</b>", x=0.22, y=-0.1, font_size=12, showarrow=False)],
    )
    return fig


def create_funnel_chart(kpis):
    """Gráfico de funil horizontal."""
    stages = ["Meta Grupo", "Portfólio Previsto", "Previsto 2026", "Validado Custos", "Real DRE"]
    values = [
        float(kpis["meta_grupo"]),
        float(kpis["retorno_previsto"]),
        float(kpis["previsto_2026"]),
        float(kpis["validado_custos"]),
        float(kpis["retorno_real"]),
    ]
    colors = ["#1B3A5C", "#E8A838", "#DC3545", "#2C5F8A", "#1A7A3A"]
    fig = go.Figure(go.Bar(
        y=stages,
        x=values,
        orientation="h",
        marker=dict(color=colors),
        text=[format_currency(v) for v in values],
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor="#E8E8E8",
            range=[0, max(values) * 1.3],
            tickvals=[0, 10_000_000, 20_000_000, 30_000_000, 40_000_000, 50_000_000, 60_000_000],
            ticktext=["R$ 0.00 Mi", "R$ 10.00 Mi", "R$ 20.00 Mi", "R$ 30.00 Mi", "R$ 40.00 Mi", "R$ 50.00 Mi", "R$ 60.00 Mi"],
        ),
        yaxis=dict(title="", autorange="reversed"),
        margin=dict(l=120, r=100, t=10, b=40),
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        bargap=0.4,
    )
    return fig


def create_bar_tipo_iniciativa(pilares, kpis):
    """Gráfico de barras agrupadas por tipo de iniciativa."""
    nome_map = {
        "Kaizen": "Kaizen",
        "Redução de Custo": "Redução de Custo",
        "BSW": "BSW",
        "Estratégia Comercial": "Outros",
        "Você Resolve": "Você Resolve",
    }
    labels = [nome_map.get(p["pilar"], p["pilar"]) for p in pilares]
    previsto = [float(p["previsto"]) for p in pilares]
    validado = [float(p["validado"]) for p in pilares]
    total_validado = sum(validado)
    total_real = float(kpis["retorno_real"])
    real_estimado = [(v / total_validado * total_real) if total_validado > 0 else 0 for v in validado]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Previsto", x=labels, y=previsto, marker_color="#B8D4E8"))
    fig.add_trace(go.Bar(name="Validado", x=labels, y=validado, marker_color="#2C5F8A"))
    fig.add_trace(go.Bar(name="Real DRE", x=labels, y=real_estimado, marker_color="#1A7A3A"))
    fig.update_layout(
        barmode="group",
        xaxis=dict(title=""),
        yaxis=dict(title="", tickformat=",.0f", showgrid=True, gridcolor="#E8E8E8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=20, t=40, b=40),
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        bargap=0.3,
    )
    return fig


# =============================================================================
# FUNÇÕES DE RENDERIZAÇÃO HTML
# =============================================================================
def render_progress_bar(pct):
    """Renderiza barra de progresso com cor baseada no percentual."""
    width = min(float(pct) * 100, 100)
    if pct >= 0.30:
        color = "#1A7A3A"
    elif pct >= 0.15:
        color = "#E8A838"
    else:
        color = "#DC3545"
    return f"""<div class="progress-container">
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{width}%;background-color:{color};"></div></div>
        <span style="font-size:12px;font-weight:600;">{pct*100:.1f}%</span>
    </div>"""


def render_status_badge(pct):
    """Renderiza badge de status."""
    if pct >= 0.30:
        return '<span class="badge-destaque">DESTAQUE ✓</span>'
    else:
        return '<span class="badge-execucao">EM EXECUÇÃO</span>'


def render_table_plantas(plantas_data):
    """Renderiza tabela HTML de plantas."""
    rows = ""
    total_meta = total_prev = total_prev2026 = total_val = total_real = 0
    for p in plantas_data:
        meta = float(p["meta_2026"]) if pd.notna(p["meta_2026"]) else 0
        prev = float(p["previsto_total"]) if pd.notna(p["previsto_total"]) else 0
        prev2026 = float(p["previsto_2026"]) if pd.notna(p["previsto_2026"]) else 0
        val = float(p["validado_custos"]) if pd.notna(p["validado_custos"]) else 0
        real = float(p["real_dre"]) if pd.notna(p["real_dre"]) else 0
        pct = float(p["pct_exec_meta"]) if pd.notna(p["pct_exec_meta"]) else 0
        total_meta += meta
        total_prev += prev
        total_prev2026 += prev2026
        total_val += val
        total_real += real
        rows += f"""<tr>
            <td><b>{p['planta']}</b></td>
            <td>{format_currency_table(meta)}</td>
            <td>{format_currency_table(prev)}</td>
            <td class="color-orange-text">{format_currency_table(prev2026)}</td>
            <td class="color-teal">{format_currency_table(val)}</td>
            <td>{format_currency_table(real)}</td>
            <td>{render_progress_bar(pct)}</td>
            <td>{render_status_badge(pct)}</td>
        </tr>"""
    total_pct = total_real / total_meta if total_meta > 0 else 0
    rows += f"""<tr>
        <td><b>TOTAL</b></td>
        <td><b>{format_currency_table(total_meta)}</b></td>
        <td><b>{format_currency_table(total_prev)}</b></td>
        <td class="color-orange-text"><b>{format_currency_table(total_prev2026)}</b></td>
        <td class="color-teal"><b>{format_currency_table(total_val)}</b></td>
        <td><b>{format_currency_table(total_real)}</b></td>
        <td><b>{format_pct(total_pct)}</b></td>
        <td></td>
    </tr>"""
    return f"""<table class="custom-table">
        <thead><tr>
            <th>Planta</th><th>Meta 2026</th><th>Previsto Total</th>
            <th style="color:#E8A838;">Previsto 2026</th>
            <th style="color:#20C997;">Validado (Custos)</th>
            <th style="color:#28A745;">Real (DRE)</th>
            <th>% Exec. Meta</th><th>Status</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


def render_table_areas(areas_data):
    """Renderiza tabela HTML de áreas funcionais."""
    rows = ""
    total_meta = total_prev = total_prev2026 = total_val = total_real = 0
    for a in areas_data:
        meta = float(a["meta_2026"]) if pd.notna(a["meta_2026"]) else 0
        prev = float(a["previsto_total"]) if pd.notna(a["previsto_total"]) else 0
        prev2026 = float(a["previsto_2026"]) if pd.notna(a["previsto_2026"]) else 0
        val = float(a["validado_custos"]) if pd.notna(a["validado_custos"]) else 0
        real = float(a["real_dre"]) if pd.notna(a["real_dre"]) else 0
        pct = float(a["pct_exec_meta"]) if pd.notna(a["pct_exec_meta"]) else 0
        total_meta += meta
        total_prev += prev
        total_prev2026 += prev2026
        total_val += val
        total_real += real
        rows += f"""<tr>
            <td><b>{a['area']}</b></td>
            <td>{format_currency_table(meta)}</td>
            <td>{format_currency_table(prev)}</td>
            <td class="color-orange-text">{format_currency_table(prev2026)}</td>
            <td class="color-teal">{format_currency_table(val)}</td>
            <td>{format_currency_table(real)}</td>
            <td>{render_progress_bar(pct)}</td>
            <td>{render_status_badge(pct)}</td>
        </tr>"""
    total_pct = total_real / total_meta if total_meta > 0 else 0
    rows += f"""<tr>
        <td><b>TOTAL</b></td>
        <td><b>{format_currency_table(total_meta)}</b></td>
        <td><b>{format_currency_table(total_prev)}</b></td>
        <td class="color-orange-text"><b>{format_currency_table(total_prev2026)}</b></td>
        <td class="color-teal"><b>{format_currency_table(total_val)}</b></td>
        <td><b>{format_currency_table(total_real)}</b></td>
        <td><b>{format_pct(total_pct)}</b></td>
        <td></td>
    </tr>"""
    return f"""<table class="custom-table">
        <thead><tr>
            <th>Área</th><th>Meta 2026</th><th>Previsto Total</th>
            <th style="color:#E8A838;">Previsto 2026</th>
            <th style="color:#20C997;">Validado (Custos)</th>
            <th style="color:#28A745;">Real (DRE)</th>
            <th>% Exec. Meta</th><th>Status</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


def render_projetos_validados(projetos):
    """Renderiza tabela de projetos validados agrupados por unidade."""
    unidades = {}
    for p in projetos:
        u = p["unidade"]
        if u not in unidades:
            unidades[u] = {"previsto": 0, "validado": 0, "real": 0}
        unidades[u]["previsto"] += p["previsto_2026"]
        unidades[u]["validado"] += p["previsto_momento"]
        unidades[u]["real"] += p["real"]
    sorted_unidades = sorted(unidades.items(), key=lambda x: x[1]["validado"], reverse=True)
    rows = ""
    total_prev = total_val = total_real = 0
    for unidade, dados in sorted_unidades:
        total_prev += dados["previsto"]
        total_val += dados["validado"]
        total_real += dados["real"]
        rows += f"""<tr>
            <td style="font-weight:600;">← {unidade}</td>
            <td>{format_currency_table(dados['previsto'])}</td>
            <td class="color-teal">{format_currency_table(dados['validado'])}</td>
            <td>{format_currency_table(dados['real'])}</td>
            <td></td><td></td>
        </tr>"""
    rows += f"""<tr>
        <td><b>TOTAL GERAL</b></td>
        <td><b>{format_currency_table(total_prev)}</b></td>
        <td class="color-teal"><b>{format_currency_table(total_val)}</b></td>
        <td><b>{format_currency_table(total_real)}</b></td>
        <td></td><td></td>
    </tr>"""
    return f"""<table class="custom-table">
        <thead><tr>
            <th style="width:30%;">Unidade / Projeto</th>
            <th>Previsto (Projeto)</th>
            <th style="color:#20C997;">Validado (Custos)</th>
            <th>Real (DRE)</th>
            <th>Prazo</th><th>Status</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


def render_gap_nao_validado(pareto_ranking):
    """Renderiza tabela de projetos não validados (GAP)."""
    nao_validados = [p for p in pareto_ranking if p["status_custos"] not in ["OK", "Não Ok"]]
    unidades = {}
    for p in nao_validados:
        u = p["unidade"]
        if u and u not in unidades:
            unidades[u] = 0
        if u:
            unidades[u] += p["previsto_2026"]
    sorted_unidades = sorted(unidades.items(), key=lambda x: x[1], reverse=True)
    rows = ""
    total = 0
    for unidade, valor in sorted_unidades:
        total += valor
        rows += f"""<tr>
            <td style="font-weight:600;">← {unidade}</td>
            <td class="color-orange-text">{format_currency_table(valor)}</td>
        </tr>"""
    rows += f"""<tr>
        <td><b>TOTAL GAP NÃO VALIDADO</b></td>
        <td class="color-orange-text"><b>{format_currency_table(total)}</b></td>
    </tr>"""
    return f"""<table class="custom-table">
        <thead><tr>
            <th style="width:60%;">Unidade / Projeto</th>
            <th style="color:#E8A838;">Previsto (Projeto)</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


# =============================================================================
# APLICAÇÃO PRINCIPAL
# =============================================================================

# Header
st.markdown('<p class="main-header">Dashboard Executivo — Grupo Delga 2026</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Gestão Estratégica de Projetos e Redução de Custos | Atualizado: Jun/2026</p>', unsafe_allow_html=True)

# Upload do arquivo Excel
arquivo = st.file_uploader(
    "📁 Carregar Planilha de Indicadores (.xlsx)",
    type=["xlsx"],
    help="Faça upload do arquivo Controle_Indicadores_Delga para atualizar o dashboard."
)

if arquivo is None:
    st.markdown("""<div style="text-align:center;padding:60px 20px;">
        <p style="font-size:48px;margin-bottom:16px;">📊</p>
        <p style="font-size:18px;font-weight:600;color:#1B3A5C;">Faça upload da planilha para visualizar o dashboard</p>
        <p style="font-size:13px;color:#6C757D;margin-top:8px;">Arraste o arquivo Excel ou clique no botão acima.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

try:
    data = load_data(arquivo)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

kpis = extract_kpis(data)
plantas_data = extract_plantas_data(data)
areas_data = extract_areas_data(data)
pilares = extract_pilares(data)
projetos_validados = extract_projetos_validados(data)
pareto_ranking = extract_pareto_ranking(data)

# =============================================================================
# KPI CARDS
# =============================================================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">META ANUAL DO GRUPO</p>
        <p class="kpi-value color-primary">{format_currency(kpis['meta_grupo'])}</p>
        <p class="kpi-sub">{format_currency_table(kpis['meta_grupo'])}</p>
        <p class="kpi-detail">100% do objetivo 2026</p>
    </div>""", unsafe_allow_html=True)

with col2:
    pct_meta = float(kpis['retorno_previsto']) / float(kpis['meta_grupo']) * 100
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">RETORNO PREVISTO (PORTFÓLIO)</p>
        <p class="kpi-value color-green">{format_currency(kpis['retorno_previsto'])}</p>
        <p class="kpi-sub">{format_currency_table(kpis['retorno_previsto'])}</p>
        <p class="kpi-detail">{pct_meta:.1f}% da meta mapeada</p>
    </div>""", unsafe_allow_html=True)

with col3:
    pct_prev = float(kpis['previsto_2026']) / float(kpis['retorno_previsto']) * 100
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">PREVISTO 2026 (PROJETADO)</p>
        <p class="kpi-value color-orange">{format_currency(kpis['previsto_2026'])}</p>
        <p class="kpi-sub">{format_currency_table(kpis['previsto_2026'])}</p>
        <p class="kpi-detail">{pct_prev:.1f}% do previsto total</p>
    </div>""", unsafe_allow_html=True)

with col4:
    pct_val = float(kpis['validado_custos']) / float(kpis['previsto_2026']) * 100
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">VALIDADO POR CUSTOS</p>
        <p class="kpi-value color-primary">{format_currency(kpis['validado_custos'])}</p>
        <p class="kpi-sub">{format_currency_table(kpis['validado_custos'])}</p>
        <p class="kpi-detail">{pct_val:.1f}% do Previsto 2026</p>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""<div class="kpi-card">
        <p class="kpi-title">RETORNO REAL (DRE)</p>
        <p class="kpi-value color-green">{format_currency(kpis['retorno_real'])}</p>
        <p class="kpi-sub">{format_currency_table(kpis['retorno_real'])}</p>
        <p class="kpi-detail">{float(kpis['pct_atingimento'])*100:.1f}% de atingimento da meta</p>
    </div>""", unsafe_allow_html=True)

# =============================================================================
# NOTA METODOLÓGICA
# =============================================================================
st.markdown("""<div class="nota-metodologica">
    <b>Nota metodológica — Tipos de Ganho:</b>
    <b>Redução de Custo</b> (impacto direto e tangível no DRE) |
    <b>Custo Evitado</b> (ganho real, mas não reflete diretamente como redução no DRE) |
    <b>Capital de Giro</b> (redução de estoque, melhora o caixa mas não o DRE de forma tangível).
    Kaizens de Custo Evitado e Capital de Giro geram valor, mas não reduzem GGF de forma tangível.
</div>""", unsafe_allow_html=True)

# =============================================================================
# GRÁFICOS DE DONUT
# =============================================================================
col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title" style="text-align:center;">REPRESENTATIVIDADE DAS PLANTAS — META 2026</p>', unsafe_allow_html=True)
    st.plotly_chart(create_donut_plantas(plantas_data), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_d2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title" style="text-align:center;">REPRESENTATIVIDADE DAS ÁREAS FUNCIONAIS — META 2026</p>', unsafe_allow_html=True)
    st.plotly_chart(create_donut_areas(areas_data), use_container_width=True, config={"displayModeBar": False})
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
# FUNIL E DISTRIBUIÇÃO POR TIPO
# =============================================================================
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">FUNIL DE CONVERSÃO — PORTFÓLIO → DRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;color:#6C757D;margin-bottom:8px;">Quanto do portfólio mapeado efetivamente se converte em resultado no DRE?</p>', unsafe_allow_html=True)
    st.plotly_chart(create_funnel_chart(kpis), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_f2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">DISTRIBUIÇÃO POR TIPO DE INICIATIVA</p>', unsafe_allow_html=True)
    st.plotly_chart(create_bar_tipo_iniciativa(pilares, kpis), use_container_width=True, config={"displayModeBar": False})
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
        <p>Impacto direto e tangível no DRE. Reduz GGF de forma mensurável. <i>Exemplo: redução de MP, troca de fornecedor, eliminação de operação.</i></p>
    </div>""", unsafe_allow_html=True)

with col_c2:
    st.markdown("""<div class="class-card" style="border: 2px solid #E8A838;">
        <h4 style="color:#E8A838;">⚡ CUSTO EVITADO</h4>
        <p>Gera produtividade real, mas a MO é realocada internamente — não reduz o GGF no DRE. <i>Exemplo: Kaizens que eliminam postos mas realocam MO para outro posto.</i></p>
    </div>""", unsafe_allow_html=True)

with col_c3:
    st.markdown("""<div class="class-card" style="border: 2px solid #1A7A3A;">
        <h4 style="color:#1A7A3A;">🏦 CAPITAL DE GIRO</h4>
        <p>Redução de estoque e melhora do fluxo de caixa. Impacto no balanço patrimonial, não no DRE diretamente. <i>Exemplo: redução de estoque de MR.</i></p>
    </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# PROJETOS VALIDADOS POR CUSTOS
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title">PROJETOS COM RETORNO VALIDADO POR CUSTOS — AGRUPADO POR UNIDADE</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:11px;color:#6C757D;margin-bottom:12px;">Clique em cada unidade para expandir e ver os projetos. Ordenados do maior para o menor valor validado dentro de cada grupo.</p>', unsafe_allow_html=True)
st.markdown(render_projetos_validados(projetos_validados), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# GAP NÃO VALIDADO
# =============================================================================
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<p class="section-title" style="color:#E8A838;">PROJETOS COM PREVISTO 2026 AINDA NÃO VALIDADOS POR CUSTOS — GAP A FECHAR</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:11px;color:#6C757D;margin-bottom:12px;">Estes projetos já têm valor projetado pelo dono do projeto mas <b>ainda aguardam validação do depto de Custos.</b> Clique em cada unidade para expandir.</p>', unsafe_allow_html=True)
st.markdown(render_gap_nao_validado(pareto_ranking), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown('<p style="text-align:center;font-size:11px;color:#6C757D;">Dashboard Executivo — Grupo Delga 2026 | Gestão Estratégica de Projetos e Redução de Custos</p>', unsafe_allow_html=True)
