import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings
import os
import pickle
import datetime

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Dashboard Executivo — Grupo Delga 2026",
    page_icon="https://grupodelga.com.br/wp-content/uploads/2024/11/logo-fa-e-clientes-grupo-whatsapp-9-300x300.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CORES DELGA ──────────────────────────────────────────────────────────────
# Site: fundo branco, azul escuro #1C2B4A, vermelho/laranja #C8202E, cinza #F5F5F5
DELGA_NAVY   = "#1C2B4A"
DELGA_RED    = "#C8202E"
DELGA_SILVER = "#8A9BB0"
DELGA_LIGHT  = "#F4F6F9"
DELGA_WHITE  = "#FFFFFF"
DELGA_GREEN  = "#1A7A3A"
DELGA_AMBER  = "#E8A838"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

  .block-container {{ padding-top:0 !important; padding-bottom:1rem; max-width:1440px; }}

  /* ── HEADER ── */
  .delga-header {{
    background: {DELGA_NAVY};
    padding: 18px 32px;
    border-radius: 0 0 8px 8px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
  }}
  .delga-header img {{ height: 44px; }}
  .delga-header-text h1 {{
    color: {DELGA_WHITE};
    font-size: 20px;
    font-weight: 700;
    margin: 0;
    letter-spacing: 0.3px;
  }}
  .delga-header-text p {{
    color: {DELGA_SILVER};
    font-size: 12px;
    margin: 2px 0 0;
  }}
  .delga-header-accent {{
    margin-left: auto;
    background: {DELGA_RED};
    color: white;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    white-space: nowrap;
  }}

  /* ── KPI CARDS ── */
  .kpi-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:20px; }}
  .kpi-card {{
    background: {DELGA_WHITE};
    border-radius: 10px;
    padding: 18px 20px;
    border-left: 4px solid {DELGA_NAVY};
    box-shadow: 0 1px 6px rgba(28,43,74,.08);
    position: relative;
    overflow: hidden;
  }}
  .kpi-card::after {{
    content:'';
    position:absolute; right:-10px; top:-10px;
    width:60px; height:60px;
    background: {DELGA_LIGHT};
    border-radius:50%;
  }}
  .kpi-card.red   {{ border-left-color:{DELGA_RED}; }}
  .kpi-card.green {{ border-left-color:{DELGA_GREEN}; }}
  .kpi-card.amber {{ border-left-color:{DELGA_AMBER}; }}
  .kpi-card.silver{{ border-left-color:{DELGA_SILVER}; }}
  .kpi-label {{
    font-size: 9px; font-weight:600; color:{DELGA_SILVER};
    text-transform:uppercase; letter-spacing:.8px; margin-bottom:6px;
  }}
  .kpi-value {{
    font-size: 24px; font-weight:700; color:{DELGA_NAVY}; line-height:1.1; margin-bottom:4px;
  }}
  .kpi-sub {{ font-size:11px; color:#555; margin-bottom:2px; }}
  .kpi-detail {{ font-size:10px; color:{DELGA_SILVER}; }}

  /* ── SECTION CARD ── */
  .section-card {{
    background:{DELGA_WHITE};
    border-radius:10px;
    padding:20px 22px;
    box-shadow:0 1px 6px rgba(28,43,74,.07);
    margin-bottom:16px;
  }}
  .section-title {{
    font-size:11px; font-weight:700; color:{DELGA_NAVY};
    text-transform:uppercase; letter-spacing:.6px;
    border-bottom: 2px solid {DELGA_RED};
    padding-bottom:8px; margin-bottom:14px;
    display:inline-block;
  }}

  /* ── NOTA ── */
  .nota {{
    background:#FFF8E1; border-left:3px solid {DELGA_AMBER};
    border-radius:4px; padding:10px 14px;
    font-size:11px; color:#444; line-height:1.6; margin:16px 0;
  }}

  /* ── TABELA ── */
  .dt {{ width:100%; border-collapse:collapse; font-size:12px; }}
  .dt thead tr {{ background:{DELGA_NAVY}; }}
  .dt thead th {{ color:white; padding:10px 12px; text-align:left; font-weight:600; font-size:11px; white-space:nowrap; }}
  .dt tbody tr:hover {{ background:{DELGA_LIGHT}; }}
  .dt tbody td {{ padding:8px 12px; border-bottom:1px solid #EEF0F3; vertical-align:middle; }}
  .dt tbody tr.total-row td {{ background:{DELGA_LIGHT}; font-weight:700; border-top:2px solid {DELGA_NAVY}; }}

  /* ── PROGRESS ── */
  .pbar-wrap {{ display:flex; align-items:center; gap:8px; }}
  .pbar-bg {{ width:72px; height:7px; background:#E2E8F0; border-radius:4px; overflow:hidden; display:inline-block; }}
  .pbar-fill {{ height:100%; border-radius:4px; transition:width .3s; }}

  /* ── BADGE ── */
  .badge {{ display:inline-block; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:600; }}
  .badge-green {{ background:#E8F5E9; color:{DELGA_GREEN}; }}
  .badge-amber {{ background:#FFF3E0; color:{DELGA_AMBER}; }}
  .badge-red   {{ background:#FFEBEE; color:{DELGA_RED}; }}
  .badge-gray  {{ background:#F0F0F0; color:#666; }}

  /* ── EXPANDER PLANTA ── */
  .plant-row {{
    background:{DELGA_WHITE};
    border:1px solid #E2E8F0;
    border-radius:8px;
    margin-bottom:8px;
    overflow:hidden;
  }}
  .plant-header {{
    padding:12px 16px;
    display:flex; align-items:center; gap:12px;
    cursor:pointer; font-weight:600; font-size:13px; color:{DELGA_NAVY};
  }}
  .plant-plus {{
    width:22px; height:22px;
    background:{DELGA_NAVY}; color:white;
    border-radius:4px; display:inline-flex;
    align-items:center; justify-content:center;
    font-size:14px; font-weight:700; flex-shrink:0;
  }}

  /* ── LOGIN ── */
  .login-wrap {{
    max-width:380px; margin:80px auto; padding:40px 36px;
    background:{DELGA_WHITE}; border-radius:12px;
    box-shadow:0 4px 24px rgba(28,43,74,.12); text-align:center;
  }}
  .login-logo {{ font-size:44px; margin-bottom:16px; }}
  .login-title {{ font-size:22px; font-weight:700; color:{DELGA_NAVY}; margin-bottom:4px; }}
  .login-sub {{ font-size:13px; color:{DELGA_SILVER}; margin-bottom:24px; }}

  #MainMenu {{visibility:hidden;}} footer {{visibility:hidden;}}
  .stDeployButton {{display:none;}} header[data-testid="stHeader"] {{display:none;}}
  div[data-testid="stExpander"] {{ border:none !important; box-shadow:none !important; }}
</style>
""", unsafe_allow_html=True)

# ── SENHA ────────────────────────────────────────────────────────────────────
SENHA = "Delga01"
DADOS_PATH = "/tmp/delga_dados.pkl"

def check_password():
    if st.session_state.get("auth"):
        return True
    st.markdown(f"""<div class="login-wrap">
        <div class="login-logo">📊</div>
        <div class="login-title">Grupo Delga</div>
        <div class="login-sub">Dashboard Executivo 2026 — Acesso Restrito</div>
    </div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        pw = st.text_input("Senha", type="password", placeholder="Digite a senha de acesso", label_visibility="collapsed")
        if st.button("Entrar →", use_container_width=True, type="primary"):
            if pw == SENHA:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    return False

if not check_password():
    st.stop()

# ── FORMATAÇÃO ───────────────────────────────────────────────────────────────
def fmt_mi(v):
    if pd.isna(v) or v is None: return "R$ 0"
    v = float(v)
    if abs(v) >= 1_000_000: return f"R$ {v/1_000_000:.2f} Mi"
    if abs(v) >= 1_000: return "R$ " + f"{v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
    return f"R$ {v:.0f}"

def fmt_brl(v):
    if pd.isna(v) or v is None or v == 0: return "—"
    v = float(v)
    return "R$ " + f"{v:,.0f}".replace(",","X").replace(".",",").replace("X",".")

def fmt_pct(v):
    if pd.isna(v) or v is None: return "0,0%"
    return f"{float(v)*100:.1f}%".replace(".",",")

def fmt_date(v):
    if pd.isna(v) or v is None or str(v) == "nan": return "—"
    try:
        if isinstance(v, (datetime.datetime, datetime.date)):
            return v.strftime("%m/%Y")
        s = str(v)
        if "00:00:00" in s: return pd.to_datetime(s).strftime("%m/%Y")
        return str(v)[:7]
    except:
        return str(v)[:7]

def pbar_html(pct, width=72):
    w = min(float(pct)*100, 100)
    color = DELGA_GREEN if pct >= .30 else (DELGA_AMBER if pct >= .15 else DELGA_RED)
    return (f'<div class="pbar-wrap">'
            f'<div class="pbar-bg" style="width:{width}px;">'
            f'<div class="pbar-fill" style="width:{w:.0f}%;background:{color};"></div></div>'
            f'<span style="font-size:11px;font-weight:600;">{w:.1f}%</span></div>')

def badge_status(pct):
    if pct >= .30: return '<span class="badge badge-green">DESTAQUE ✓</span>'
    return '<span class="badge badge-amber">EM EXECUÇÃO</span>'

def badge_custos(v):
    if v == "OK": return '<span class="badge badge-green">✓ OK</span>'
    if v in ("Não Ok","NOK","Não OK"): return '<span class="badge badge-red">✗ NOK</span>'
    if str(v).strip() == "" or str(v) == "nan": return '<span class="badge badge-gray">Pendente</span>'
    return f'<span class="badge badge-gray">{v}</span>'

def badge_st(v):
    v = str(v)
    if "Concluído" in v: return '<span class="badge badge-green">✓ Concluído</span>'
    if "Execução" in v:  return '<span class="badge badge-amber">⏳ Execução</span>'
    if "Não" in v:       return '<span class="badge badge-gray">Não iniciado</span>'
    return f'<span class="badge badge-gray">{v}</span>'

# ── PERSISTÊNCIA ─────────────────────────────────────────────────────────────
def save_bytes(b):
    with open(DADOS_PATH,"wb") as f: pickle.dump(b,f)

def load_bytes():
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH,"rb") as f: return pickle.load(f)
    return None

# ── CARREGAMENTO ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(file_bytes):
    import io
    def xls(sh): 
        buf = io.BytesIO(file_bytes)
        return pd.read_excel(buf, sheet_name=sh, header=None)
    d = {}
    d["u5"]  = xls("5 Unidades  +")
    d["par"] = xls("Pareto")
    for s in ["Diadema","Jarinu","Ferraz","São Leopoldo","Anchieta","Compras ","Vendas","Corporativo"]:
        d[s] = xls(s)
    return d

# ── EXTRAÇÃO ─────────────────────────────────────────────────────────────────
def safe_float(v, default=0.0):
    try: return float(v) if pd.notna(v) else default
    except: return default

def extract_kpis(d):
    df = d["u5"]
    return {
        "meta":      safe_float(df.iloc[6,3]),
        "portfolio": safe_float(df.iloc[6,5]),
        "prev2026":  safe_float(df.iloc[6,6]),
        "validado":  safe_float(df.iloc[6,7]),
        "real":      safe_float(df.iloc[6,9]),
        "pct_ating": safe_float(df.iloc[6,11]),
        "inic":      int(safe_float(df.iloc[6,13])),
    }

def extract_plantas(d):
    df = d["u5"]
    # cols: 4=Diadema,5=Ferraz,6=SãoLeopoldo,7=Jarinu,8=Anchieta (row20 labels confirmed)
    cfg = [
        ("Diadema",      4, "Diadema"),
        ("Ferraz",       5, "Ferraz"),
        ("São Leopoldo", 6, "São Leopoldo"),
        ("Jarinu",       7, "Jarinu"),
        ("Anchieta",     8, "Anchieta"),
    ]
    res = []
    for nome, col, sh in cfg:
        p2026 = safe_float(d.get(sh, pd.DataFrame()).iloc[4,3]) if sh in d else 0
        res.append({
            "nome": nome, "sheet": sh,
            "meta":     safe_float(df.iloc[21,col]),
            "prev":     safe_float(df.iloc[22,col]),
            "prev2026": p2026,
            "val":      safe_float(df.iloc[24,col]),
            "real":     safe_float(df.iloc[25,col]),
            "pct":      safe_float(df.iloc[26,col]),
        })
    return res

def extract_areas(d):
    df = d["u5"]
    cfg = [
        ("Corporativo", 9,  "Corporativo"),
        ("Compras",     10, "Compras "),
        ("Vendas",      11, "Vendas"),
    ]
    res = []
    for nome, col, sh in cfg:
        p2026 = 0
        if sh in d and sh != "Corporativo":
            p2026 = safe_float(d[sh].iloc[4,4])
        res.append({
            "nome": nome, "sheet": sh,
            "meta":     safe_float(df.iloc[21,col]),
            "prev":     safe_float(df.iloc[22,col]),
            "prev2026": p2026,
            "val":      safe_float(df.iloc[24,col]),
            "real":     safe_float(df.iloc[25,col]),
            "pct":      safe_float(df.iloc[26,col]),
        })
    return res

def extract_pilares(d):
    df = d["u5"]
    res = []
    for i in range(12,17):
        nome = df.iloc[i,3]
        if pd.notna(nome) and str(nome) != "TOTAL":
            res.append({
                "nome": str(nome),
                "qtd":  int(safe_float(df.iloc[i,4])),
                "prev": safe_float(df.iloc[i,5]),
                "val":  safe_float(df.iloc[i,6]),
                "pct":  safe_float(df.iloc[i,7]),
            })
    return res

def extract_evolucao(d):
    df = d["u5"]
    meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    def row(r): return [safe_float(df.iloc[r,c]) for c in range(22,34)]
    return {
        "meses": meses,
        "prev":        row(53),
        "real":        row(54),
        "acum_prev":   row(56),
        "acum_real":   row(57),
        "proj_meta":   row(58),
    }

def extract_proj_planta(d, sheet_key):
    """Extrai projetos de uma aba de planta (header row 53, data from 54)."""
    df = d.get(sheet_key)
    if df is None: return []
    res = []
    # Plants: col0=tipo, col2=nome, col5=resp, col7=termino, col8=previsto, col12=valid_custos, col13=val_saving, col14=status
    for i in range(54, min(54+300, df.shape[0])):
        tipo  = df.iloc[i,0]
        nome  = df.iloc[i,2]
        if not pd.notna(tipo) or not pd.notna(nome): continue
        if str(tipo).strip() == "" or str(nome).strip() == "": continue
        res.append({
            "tipo":       str(tipo).strip(),
            "nome":       str(nome).strip(),
            "resp":       str(df.iloc[i,5]).strip() if pd.notna(df.iloc[i,5]) else "—",
            "termino":    fmt_date(df.iloc[i,7]),
            "previsto":   safe_float(df.iloc[i,8]),
            "val_custos": str(df.iloc[i,12]).strip() if pd.notna(df.iloc[i,12]) else "",
            "val_saving": safe_float(df.iloc[i,13]),
            "status":     str(df.iloc[i,14]).strip() if pd.notna(df.iloc[i,14]) else "",
        })
    return res

def extract_proj_area(d, sheet_key):
    """Extrai projetos de áreas funcionais (Compras header=29, Vendas diferente)."""
    df = d.get(sheet_key)
    if df is None: return []
    res = []
    if "Compras" in sheet_key:
        # col0=tipo,col1=nome,col5=resp,col7=termino,col8=prev,col12=valid,col13=saving,col14=status
        for i in range(30, min(30+200, df.shape[0])):
            tipo = df.iloc[i,0]; nome = df.iloc[i,1]
            if not pd.notna(tipo) or not pd.notna(nome): continue
            if str(tipo).strip() in ("","nan") or str(nome).strip() in ("","nan"): continue
            res.append({
                "tipo":       str(tipo).strip(),
                "nome":       str(nome).strip(),
                "resp":       str(df.iloc[i,5]).strip() if pd.notna(df.iloc[i,5]) else "—",
                "termino":    fmt_date(df.iloc[i,7]),
                "previsto":   safe_float(df.iloc[i,8]),
                "val_custos": str(df.iloc[i,12]).strip() if pd.notna(df.iloc[i,12]) else "",
                "val_saving": safe_float(df.iloc[i,13]),
                "status":     str(df.iloc[i,14]).strip() if pd.notna(df.iloc[i,14]) else "",
            })
    elif sheet_key == "Vendas":
        for i in range(40, min(40+100, df.shape[0])):
            tipo = df.iloc[i,0]; nome = df.iloc[i,1]
            if not pd.notna(tipo) or not pd.notna(nome): continue
            if str(tipo).strip() in ("","nan") or str(nome).strip() in ("","nan"): continue
            res.append({
                "tipo":       str(tipo).strip(),
                "nome":       str(nome).strip(),
                "resp":       str(df.iloc[i,4]).strip() if pd.notna(df.iloc[i,4]) else "—",
                "termino":    "—",
                "previsto":   safe_float(df.iloc[i,7]),
                "val_custos": "",
                "val_saving": 0,
                "status":     str(df.iloc[i,13]).strip() if pd.notna(df.iloc[i,13]) else "",
            })
    return res

def extract_ranking(d):
    df = d["u5"]
    res = []
    for i in range(53,137):
        pos   = df.iloc[i,3]; uni = df.iloc[i,4]; nome = df.iloc[i,5]
        if not pd.notna(uni) or not pd.notna(nome): continue
        res.append({
            "pos":     int(safe_float(pos,i-52)),
            "uni":     str(uni),
            "nome":    str(nome),
            "status":  str(df.iloc[i,7]).strip() if pd.notna(df.iloc[i,7]) else "",
            "custos":  str(df.iloc[i,8]).strip() if pd.notna(df.iloc[i,8]) else "",
            "prev26":  safe_float(df.iloc[i,9]),
            "prev_mo": safe_float(df.iloc[i,10]),
            "real":    safe_float(df.iloc[i,11]),
        })
    return res

# ── GRÁFICOS ─────────────────────────────────────────────────────────────────
PALETTE = [DELGA_NAVY,"#2C4F7C","#4A7AB5",DELGA_SILVER,"#A8C8E8"]

def chart_funnel(kpis):
    stages = ["Meta do Grupo","Portfólio Previsto","Previsto 2026","Validado Custos","Real DRE"]
    values = [kpis["meta"],kpis["portfolio"],kpis["prev2026"],kpis["validado"],kpis["real"]]
    colors = [DELGA_NAVY,"#2C5F8A","#4A90D9",DELGA_AMBER,DELGA_GREEN]
    fig = go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo="value+percent initial",
        texttemplate=[f"<b>{fmt_mi(v)}</b>" for v in values],
        marker=dict(color=colors, line=dict(width=1.5, color="white")),
        connector=dict(line=dict(color="#DDD", width=2, dash="dot")),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(l=10,r=10,t=10,b=10),
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter",size=11),
    )
    return fig

def chart_gauge(pct):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct*100,
        number=dict(suffix="%", font=dict(size=38,color=DELGA_NAVY,family="Inter")),
        gauge=dict(
            axis=dict(range=[0,100], ticksuffix="%", tickfont=dict(size=10)),
            bar=dict(color=DELGA_GREEN if pct>=.30 else (DELGA_AMBER if pct>=.15 else DELGA_RED),
                     thickness=0.28),
            bgcolor="white",
            borderwidth=0,
            steps=[
                dict(range=[0,30],  color="#FFEBEE"),
                dict(range=[30,70], color="#FFF3E0"),
                dict(range=[70,100],color="#E8F5E9"),
            ],
            threshold=dict(line=dict(color=DELGA_RED,width=3), thickness=.75, value=100),
        ),
        title=dict(text="<b>Atingimento da Meta</b>", font=dict(size=12,color=DELGA_SILVER)),
    ))
    fig.update_layout(
        margin=dict(l=20,r=20,t=50,b=10),
        height=280,
        paper_bgcolor="white",
    )
    return fig

def chart_evolucao(ev, series):
    config = {
        "Acumulado Previsto": dict(data=ev["acum_prev"], color=DELGA_NAVY,  dash="solid"),
        "Acumulado Real":     dict(data=ev["acum_real"], color=DELGA_GREEN, dash="solid"),
        "Projeção da Meta":   dict(data=ev["proj_meta"], color=DELGA_RED,   dash="dash"),
        "Previsto Mensal":    dict(data=ev["prev"],      color="#4A90D9",   dash="dot"),
        "Real Mensal":        dict(data=ev["real"],      color="#28A745",   dash="dot"),
    }
    fig = go.Figure()
    for s in series:
        c = config[s]
        fig.add_trace(go.Scatter(
            x=ev["meses"], y=c["data"], mode="lines+markers", name=s,
            line=dict(color=c["color"],width=2.5,dash=c["dash"]),
            marker=dict(size=6,color=c["color"]),
            hovertemplate=f"<b>{s}</b><br>%{{x}}: R$ %{{y:,.0f}}<extra></extra>",
        ))
    fig.update_layout(
        xaxis=dict(showgrid=True,gridcolor="#F0F4F8"),
        yaxis=dict(tickformat=",.0f",showgrid=True,gridcolor="#F0F4F8",title="R$"),
        legend=dict(orientation="h",y=1.05,x=0.5,xanchor="center",font=dict(size=11)),
        margin=dict(l=80,r=20,t=50,b=40),
        height=400,
        paper_bgcolor="white",plot_bgcolor="white",
        hovermode="x unified",
        font=dict(family="Inter"),
    )
    return fig

def chart_donut(labels, values, colors):
    total = sum(values)
    txt = [f"  {labels[i]}  {values[i]/total*100:.1f}%  {fmt_mi(values[i])}" for i in range(len(labels))]
    fig = go.Figure(go.Pie(
        labels=txt, values=values, hole=0.62,
        marker=dict(colors=colors),
        textinfo="none",
        hovertemplate="<b>%{label}</b><extra></extra>",
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v",y=0.5,x=0.55,yanchor="middle",font=dict(size=11)),
        margin=dict(l=10,r=10,t=10,b=30),
        height=280,
        paper_bgcolor="white",plot_bgcolor="white",
        annotations=[dict(text=f"<b>{fmt_mi(total)}</b>",x=0.22,y=-0.08,font_size=12,showarrow=False)],
        font=dict(family="Inter"),
    )
    return fig

def chart_pilares(pilares, real_total):
    labels   = [p["nome"] for p in pilares]
    previsto = [p["prev"] for p in pilares]
    validado = [p["val"]  for p in pilares]
    tot_val  = sum(validado)
    real_est = [v/tot_val*real_total if tot_val>0 else 0 for v in validado]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Previsto", x=labels, y=previsto, marker_color="#B8D4E8"))
    fig.add_trace(go.Bar(name="Validado", x=labels, y=validado, marker_color=DELGA_NAVY))
    fig.add_trace(go.Bar(name="Real DRE", x=labels, y=real_est,  marker_color=DELGA_GREEN))
    fig.update_layout(
        barmode="group",
        yaxis=dict(tickformat=",.0f",showgrid=True,gridcolor="#F0F4F8"),
        legend=dict(orientation="h",y=1.05,x=1,xanchor="right",font=dict(size=11)),
        margin=dict(l=60,r=20,t=40,b=60),
        height=300,paper_bgcolor="white",plot_bgcolor="white",bargap=0.28,
        font=dict(family="Inter"),
    )
    return fig

# ── HTML HELPERS ─────────────────────────────────────────────────────────────
def table_header(*cols):
    ths = "".join(f"<th>{c}</th>" for c in cols)
    return f"<table class='dt'><thead><tr>{ths}</tr></thead><tbody>"

def proj_table_html(projetos):
    if not projetos:
        return "<p style='color:#999;font-size:12px;padding:8px;'>Nenhum projeto encontrado.</p>"
    rows = ""
    for p in projetos:
        rows += f"""<tr>
          <td><span class="badge badge-gray" style="font-size:9px;">{p['tipo']}</span></td>
          <td style="max-width:280px;">{p['nome']}</td>
          <td>{p['resp']}</td>
          <td>{p['termino']}</td>
          <td style="text-align:right;">{fmt_brl(p['previsto'])}</td>
          <td style="text-align:right;color:#20C997;">{fmt_brl(p['val_saving'])}</td>
          <td style="text-align:right;color:{DELGA_GREEN};font-weight:600;">—</td>
          <td>{badge_custos(p['val_custos'])}</td>
          <td>{badge_st(p['status'])}</td>
        </tr>"""
    return (table_header("Tipo","Projeto","Responsável","Término","V. Previsto","V. Validado","V. Real","Custos","Status")
            + rows + "</tbody></table>")

def perf_table_rows(items, key="nome"):
    rows = ""
    totais = dict(meta=0,prev=0,prev2026=0,val=0,real=0)
    for it in items:
        totais["meta"]    += it["meta"]
        totais["prev"]    += it["prev"]
        totais["prev2026"]+= it["prev2026"]
        totais["val"]     += it["val"]
        totais["real"]    += it["real"]
        rows += f"""<tr>
          <td><b>{it[key]}</b></td>
          <td>{fmt_brl(it['meta'])}</td>
          <td>{fmt_brl(it['prev'])}</td>
          <td style="color:{DELGA_AMBER};">{fmt_brl(it['prev2026'])}</td>
          <td style="color:#20C997;">{fmt_brl(it['val'])}</td>
          <td style="color:{DELGA_GREEN};font-weight:600;">{fmt_brl(it['real'])}</td>
          <td>{pbar_html(it['pct'])}</td>
          <td>{badge_status(it['pct'])}</td>
        </tr>"""
    pt = totais["real"]/totais["meta"] if totais["meta"]>0 else 0
    rows += f"""<tr class="total-row">
      <td>TOTAL</td>
      <td>{fmt_brl(totais['meta'])}</td>
      <td>{fmt_brl(totais['prev'])}</td>
      <td style="color:{DELGA_AMBER};">{fmt_brl(totais['prev2026'])}</td>
      <td style="color:#20C997;">{fmt_brl(totais['val'])}</td>
      <td style="color:{DELGA_GREEN};">{fmt_brl(totais['real'])}</td>
      <td>{pbar_html(pt)}</td>
      <td></td>
    </tr>"""
    return rows

# ── HEADER DELGA ─────────────────────────────────────────────────────────────
st.markdown(f"""<div class="delga-header">
  <img src="https://grupodelga.com.br/wp-content/uploads/2024/11/logo-fa-e-clientes-grupo-whatsapp-9-300x300.png"
       onerror="this.style.display='none'">
  <div class="delga-header-text">
    <h1>Dashboard Executivo — Grupo Delga 2026</h1>
    <p>Gestão Estratégica de Projetos e Redução de Custos</p>
  </div>
  <div class="delga-header-accent">Jun / 2026</div>
</div>""", unsafe_allow_html=True)

# ── ADMIN UPLOAD ──────────────────────────────────────────────────────────────
with st.expander("🔐 Administrador — Atualizar Planilha"):
    arquivo = st.file_uploader("Nova versão (.xlsx)", type=["xlsx"], key="up")
    if arquivo:
        b = arquivo.read()
        save_bytes(b)
        st.cache_data.clear()
        st.success("✅ Planilha atualizada! Todos os usuários verão os novos dados.")

# ── CARGA ─────────────────────────────────────────────────────────────────────
fb = load_bytes()
if fb is None:
    st.warning("⚠️ Nenhuma planilha carregada. Expanda o painel Administrador para fazer o upload.")
    st.stop()

try:
    D = load_data(fb)
except Exception as e:
    st.error(f"Erro ao processar planilha: {e}")
    st.stop()

kpis     = extract_kpis(D)
plantas  = extract_plantas(D)
areas    = extract_areas(D)
pilares  = extract_pilares(D)
evolucao = extract_evolucao(D)
ranking  = extract_ranking(D)

meta       = kpis["meta"]
portfolio  = kpis["portfolio"]
prev2026   = kpis["prev2026"]
validado   = kpis["validado"]
real       = kpis["real"]
pct_ating  = kpis["pct_ating"]

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
def kpi_card(cls, label, value_big, sub, detail):
    return f"""<div class="kpi-card {cls}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value_big}</div>
      <div class="kpi-sub">{sub}</div>
      <div class="kpi-detail">{detail}</div>
    </div>"""

cob   = portfolio/meta*100   if meta>0 else 0
pp    = prev2026/portfolio*100 if portfolio>0 else 0
pv    = validado/prev2026*100  if prev2026>0 else 0

kpi_html = f"""<div class="kpi-grid">
  {kpi_card("", "Meta Anual do Grupo", fmt_mi(meta), fmt_brl(meta), "Objetivo 2026 — 100%")}
  {kpi_card("silver", f"Portfólio Previsto", fmt_mi(portfolio), fmt_brl(portfolio), f"{cob:.1f}% da meta · {kpis['inic']} iniciativas")}
  {kpi_card("amber",  "Previsto 2026", fmt_mi(prev2026), fmt_brl(prev2026), f"{pp:.1f}% do portfólio total")}
  {kpi_card("",       "Validado por Custos", fmt_mi(validado), fmt_brl(validado), f"{pv:.1f}% do Previsto 2026")}
  {kpi_card("green",  "Retorno Real (DRE)", fmt_mi(real), fmt_brl(real), f"{pct_ating*100:.1f}% de atingimento")}
</div>"""
st.markdown(kpi_html, unsafe_allow_html=True)

# ── NOTA METODOLÓGICA ────────────────────────────────────────────────────────
st.markdown(f"""<div class="nota">
  <b>Metodologia — Tipos de Ganho:</b>
  <b>Redução de Custo</b> impacto direto no DRE · 
  <b>Custo Evitado</b> MO realocada internamente, não reduz GGF no DRE · 
  <b>Capital de Giro</b> melhora o caixa, mas não o DRE diretamente.
</div>""", unsafe_allow_html=True)

# ── EVOLUÇÃO MENSAL ───────────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<span class="section-title">Evolução Mensal — Acumulado Previsto vs Real vs Meta</span>', unsafe_allow_html=True)
series_all = ["Acumulado Previsto","Acumulado Real","Projeção da Meta","Previsto Mensal","Real Mensal"]
sel = st.multiselect("Séries:", series_all, default=series_all[:3], key="ev")
if sel:
    st.plotly_chart(chart_evolucao(evolucao, sel), use_container_width=True, config={"displayModeBar":False})
st.markdown('</div>', unsafe_allow_html=True)

# ── FUNIL + GAUGE ─────────────────────────────────────────────────────────────
col_fu, col_ga = st.columns([3,2])
with col_fu:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-title">Funil de Conversão — Portfólio → DRE</span>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;color:#8A9BB0;margin-bottom:8px;">Quanto do portfólio mapeado se converte em resultado no DRE?</p>', unsafe_allow_html=True)
    st.plotly_chart(chart_funnel(kpis), use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

with col_ga:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-title">Atingimento da Meta</span>', unsafe_allow_html=True)
    st.plotly_chart(chart_gauge(pct_ating), use_container_width=True, config={"displayModeBar":False})

    # Mini-resumo embaixo do gauge
    gap_val = meta - real
    st.markdown(f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">
      <div style="background:{DELGA_LIGHT};border-radius:6px;padding:10px 12px;text-align:center;">
        <div style="font-size:9px;font-weight:600;color:{DELGA_SILVER};text-transform:uppercase;letter-spacing:.6px;">GAP para Meta</div>
        <div style="font-size:16px;font-weight:700;color:{DELGA_RED};">{fmt_mi(gap_val)}</div>
      </div>
      <div style="background:{DELGA_LIGHT};border-radius:6px;padding:10px 12px;text-align:center;">
        <div style="font-size:9px;font-weight:600;color:{DELGA_SILVER};text-transform:uppercase;letter-spacing:.6px;">Validado / Meta</div>
        <div style="font-size:16px;font-weight:700;color:{DELGA_NAVY};">{validado/meta*100:.1f}%</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── DONUTS ────────────────────────────────────────────────────────────────────
cd1, cd2 = st.columns(2)
with cd1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-title">Representatividade — Plantas Industriais</span>', unsafe_allow_html=True)
    st.plotly_chart(
        chart_donut([p["nome"] for p in plantas],[p["meta"] for p in plantas],PALETTE),
        use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)
with cd2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-title">Representatividade — Áreas Funcionais</span>', unsafe_allow_html=True)
    st.plotly_chart(
        chart_donut([a["nome"] for a in areas],[a["meta"] for a in areas],[DELGA_NAVY,DELGA_GREEN,"#20C997"]),
        use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── PILARES + STATUS ──────────────────────────────────────────────────────────
cp1, cp2 = st.columns([3,2])
with cp1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-title">Distribuição por Tipo de Iniciativa</span>', unsafe_allow_html=True)
    st.plotly_chart(chart_pilares(pilares,real), use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)
with cp2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<span class="section-title">Resumo por Pilar</span>', unsafe_allow_html=True)
    rows_p = "".join(f"""<tr>
      <td style="font-size:11px;">{p['nome']}</td>
      <td style="text-align:center;font-size:11px;">{p['qtd']}</td>
      <td style="text-align:right;font-size:11px;">{fmt_mi(p['prev'])}</td>
      <td style="text-align:right;font-size:11px;color:#20C997;">{fmt_mi(p['val'])}</td>
    </tr>""" for p in pilares)
    st.markdown(table_header("Pilar","Qtd","Previsto","Validado")+rows_p+"</tbody></table>",
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── PLANTAS INDUSTRIAIS — expandable ─────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<span class="section-title">Plantas Industriais — Performance Consolidada</span>', unsafe_allow_html=True)

# Cabeçalho fixo da tabela
header_cols = ["Planta","Meta 2026","Previsto Total",
               f'<span style="color:{DELGA_AMBER}">Previsto 2026</span>',
               '<span style="color:#20C997">Validado</span>',
               f'<span style="color:{DELGA_GREEN}">Real DRE</span>',
               "% Meta","Status"]
st.markdown(f"""<table class='dt'><thead><tr>{"".join(f"<th>{c}</th>" for c in header_cols)}</tr></thead></table>""",
            unsafe_allow_html=True)

# Totais
tot_meta=tot_prev=tot_prev26=tot_val=tot_real=0
for p in plantas:
    tot_meta+=p["meta"]; tot_prev+=p["prev"]; tot_prev26+=p["prev2026"]
    tot_val+=p["val"];   tot_real+=p["real"]

for p in plantas:
    with st.expander(f"＋  {p['nome']}", expanded=False):
        # linha de resumo
        st.markdown(f"""<table class='dt'><tbody><tr>
          <td style="width:130px;"><b>{p['nome']}</b></td>
          <td>{fmt_brl(p['meta'])}</td>
          <td>{fmt_brl(p['prev'])}</td>
          <td style="color:{DELGA_AMBER};">{fmt_brl(p['prev2026'])}</td>
          <td style="color:#20C997;">{fmt_brl(p['val'])}</td>
          <td style="color:{DELGA_GREEN};font-weight:600;">{fmt_brl(p['real'])}</td>
          <td>{pbar_html(p['pct'])}</td>
          <td>{badge_status(p['pct'])}</td>
        </tr></tbody></table>""", unsafe_allow_html=True)
        st.markdown("<hr style='margin:10px 0;border-color:#EEF0F3;'>", unsafe_allow_html=True)
        st.markdown(f"**Projetos — {p['nome']}**")
        proj = extract_proj_planta(D, p["sheet"])
        st.markdown(proj_table_html(proj), unsafe_allow_html=True)

# Linha de total
pt_total = tot_real/tot_meta if tot_meta>0 else 0
st.markdown(f"""<table class='dt'><tbody><tr class="total-row">
  <td><b>TOTAL</b></td>
  <td><b>{fmt_brl(tot_meta)}</b></td>
  <td><b>{fmt_brl(tot_prev)}</b></td>
  <td style="color:{DELGA_AMBER};"><b>{fmt_brl(tot_prev26)}</b></td>
  <td style="color:#20C997;"><b>{fmt_brl(tot_val)}</b></td>
  <td style="color:{DELGA_GREEN};"><b>{fmt_brl(tot_real)}</b></td>
  <td>{pbar_html(pt_total)}</td>
  <td></td>
</tr></tbody></table>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── ÁREAS FUNCIONAIS — expandable ────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<span class="section-title">Áreas Funcionais — Performance Consolidada</span>', unsafe_allow_html=True)
st.markdown(f"""<table class='dt'><thead><tr>{"".join(f"<th>{c}</th>" for c in header_cols)}</tr></thead></table>""",
            unsafe_allow_html=True)

tot_meta=tot_prev=tot_prev26=tot_val=tot_real=0
for a in areas:
    tot_meta+=a["meta"]; tot_prev+=a["prev"]; tot_prev26+=a["prev2026"]
    tot_val+=a["val"];   tot_real+=a["real"]

area_sheets = {"Compras":"Compras ","Vendas":"Vendas","Corporativo":"Corporativo"}
for a in areas:
    with st.expander(f"＋  {a['nome']}", expanded=False):
        st.markdown(f"""<table class='dt'><tbody><tr>
          <td style="width:130px;"><b>{a['nome']}</b></td>
          <td>{fmt_brl(a['meta'])}</td>
          <td>{fmt_brl(a['prev'])}</td>
          <td style="color:{DELGA_AMBER};">{fmt_brl(a['prev2026'])}</td>
          <td style="color:#20C997;">{fmt_brl(a['val'])}</td>
          <td style="color:{DELGA_GREEN};font-weight:600;">{fmt_brl(a['real'])}</td>
          <td>{pbar_html(a['pct'])}</td>
          <td>{badge_status(a['pct'])}</td>
        </tr></tbody></table>""", unsafe_allow_html=True)
        st.markdown("<hr style='margin:10px 0;border-color:#EEF0F3;'>", unsafe_allow_html=True)
        st.markdown(f"**Projetos — {a['nome']}**")
        sh = area_sheets.get(a["nome"], a["nome"])
        proj = extract_proj_area(D, sh)
        st.markdown(proj_table_html(proj), unsafe_allow_html=True)

pt_total = tot_real/tot_meta if tot_meta>0 else 0
st.markdown(f"""<table class='dt'><tbody><tr class="total-row">
  <td><b>TOTAL</b></td>
  <td><b>{fmt_brl(tot_meta)}</b></td>
  <td><b>{fmt_brl(tot_prev)}</b></td>
  <td style="color:{DELGA_AMBER};"><b>{fmt_brl(tot_prev26)}</b></td>
  <td style="color:#20C997;"><b>{fmt_brl(tot_val)}</b></td>
  <td style="color:{DELGA_GREEN};"><b>{fmt_brl(tot_real)}</b></td>
  <td>{pbar_html(pt_total)}</td>
  <td></td>
</tr></tbody></table>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── CLASSIFICAÇÃO DE GANHOS ───────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<span class="section-title">Classificação de Ganhos</span>', unsafe_allow_html=True)
cc1,cc2,cc3 = st.columns(3)
for col, cor, icon, titulo, texto in [
    (cc1, DELGA_NAVY,  "🔥", "Redução de Custo",
     "Impacto direto no DRE. Reduz GGF de forma mensurável.<br><em>Ex: redução de MP, troca de fornecedor.</em>"),
    (cc2, DELGA_AMBER, "⚡", "Custo Evitado",
     "MO realocada internamente — não reduz GGF no DRE.<br><em>Ex: Kaizens que eliminam postos mas realocam MO.</em>"),
    (cc3, DELGA_GREEN, "🏦", "Capital de Giro",
     "Reduz estoque e melhora fluxo de caixa. Impacto no balanço.<br><em>Ex: redução de estoque de matéria-prima.</em>"),
]:
    with col:
        st.markdown(f"""<div style="border:2px solid {cor};border-radius:8px;padding:14px 16px;">
          <div style="font-weight:700;color:{cor};margin-bottom:6px;font-size:13px;">{icon} {titulo}</div>
          <div style="font-size:11px;color:#444;line-height:1.6;">{texto}</div>
        </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── RANKING DE PROJETOS ───────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<span class="section-title">Ranking de Projetos — Todos os Pilares</span>', unsafe_allow_html=True)

rk1,rk2,rk3 = st.columns([2,2,1])
with rk1:
    f_uni = st.multiselect("Unidade:",sorted(set(r["uni"] for r in ranking)),default=[],
                           placeholder="Todas",key="rk_uni")
with rk2:
    f_st  = st.multiselect("Status:", sorted(set(r["status"] for r in ranking if r["status"])),
                           default=[],placeholder="Todos",key="rk_st")
with rk3:
    n_lin = st.number_input("Linhas:",5,200,25,5)

proj_f = ranking
if f_uni: proj_f = [r for r in proj_f if r["uni"] in f_uni]
if f_st:  proj_f = [r for r in proj_f if r["status"] in f_st]

st.markdown(f"<p style='font-size:11px;color:{DELGA_SILVER};margin-bottom:6px;'>"
            f"Exibindo {min(n_lin,len(proj_f))} de {len(proj_f)} projetos</p>", unsafe_allow_html=True)

rows_rk=""
for r in proj_f[:int(n_lin)]:
    rows_rk += f"""<tr>
      <td style="text-align:center;color:{DELGA_SILVER};font-weight:700;">{r['pos']}</td>
      <td><b>{r['uni']}</b></td>
      <td style="max-width:250px;">{r['nome']}</td>
      <td>{badge_st(r['status'])}</td>
      <td>{badge_custos(r['custos'])}</td>
      <td style="text-align:right;">{fmt_brl(r['prev26'])}</td>
      <td style="text-align:right;">{fmt_brl(r['prev_mo'])}</td>
      <td style="text-align:right;font-weight:700;color:{DELGA_GREEN};">{fmt_brl(r['real'])}</td>
    </tr>"""
st.markdown(table_header("#","Unidade","Projeto","Status","Custos",
                         "Previsto 2026","Previsto Momento","Real DRE")+rows_rk+"</tbody></table>",
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── GAP NÃO VALIDADO ─────────────────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown(f'<span class="section-title" style="border-bottom-color:{DELGA_AMBER};">GAP — Projetos Aguardando Validação de Custos</span>', unsafe_allow_html=True)
st.markdown('<p style="font-size:11px;color:#8A9BB0;margin-bottom:12px;">Projetos com valor projetado mas ainda sem validação do depto de Custos. Principal alavancador do pipeline.</p>', unsafe_allow_html=True)

gap = [r for r in ranking if r["custos"] not in ("OK","Não Ok","NOK","Não OK") and r["prev26"]>0]
by_uni = {}
for r in gap:
    by_uni[r["uni"]] = by_uni.get(r["uni"],0)+r["prev26"]
total_gap = sum(by_uni.values())

rows_gap=""
for uni,v in sorted(by_uni.items(),key=lambda x:-x[1]):
    pct = v/total_gap*100 if total_gap>0 else 0
    rows_gap += f"""<tr>
      <td><b>{uni}</b></td>
      <td style="text-align:right;color:{DELGA_AMBER};font-weight:600;">{fmt_brl(v)}</td>
      <td style="text-align:right;">{pct:.1f}%</td>
    </tr>"""
rows_gap += f"""<tr class="total-row">
  <td>TOTAL GAP</td>
  <td style="text-align:right;color:{DELGA_AMBER};">{fmt_brl(total_gap)}</td>
  <td style="text-align:right;">100%</td>
</tr>"""
n_gap = len(gap)
st.markdown(f"<p style='font-size:11px;color:{DELGA_SILVER};'>{n_gap} projetos aguardam validação</p>",
            unsafe_allow_html=True)
st.markdown(table_header("Unidade","Previsto 2026 (não validado)","% do Gap")+rows_gap+"</tbody></table>",
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="text-align:center;padding:16px 0;border-top:1px solid #EEF0F3;margin-top:8px;">
  <span style="font-size:11px;color:{DELGA_SILVER};">
    Dashboard Executivo · Grupo Delga 2026 · Gestão Estratégica de Projetos e Redução de Custos
  </span>
</div>""", unsafe_allow_html=True)

col_ft1,col_ft2 = st.columns([5,1])
with col_ft2:
    if st.button("🚪 Sair",key="logout"):
        st.session_state["auth"]=False
        st.rerun()
