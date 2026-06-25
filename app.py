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

DELGA_NAVY   = "#1C2B4A"
DELGA_RED    = "#C8202E"
DELGA_SILVER = "#8A9BB0"
DELGA_LIGHT  = "#F4F6F9"
DELGA_WHITE  = "#FFFFFF"
DELGA_GREEN  = "#1A7A3A"
DELGA_AMBER  = "#E8A838"
DELGA_TEAL   = "#20C997"

VALID_TIPOS = {
    'BSW','Kaizen','Redução de custo','Redução de Custo',
    'Você Resolve','Estratégia Comercial','Meta Executiva',
    'Você resolve','Redução de Custo ','kaizen'
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
.block-container {{ padding-top:0 !important; padding-bottom:1rem; max-width:1440px; }}

/* HEADER */
.delga-header {{
  background:{DELGA_NAVY}; padding:16px 28px;
  border-radius:0 0 8px 8px; display:flex; align-items:center;
  gap:16px; margin-bottom:18px;
}}
.delga-header img {{ height:42px; border-radius:4px; }}
.delga-header-text h1 {{ color:white; font-size:19px; font-weight:700; margin:0; }}
.delga-header-text p  {{ color:{DELGA_SILVER}; font-size:11px; margin:2px 0 0; }}
.delga-badge {{
  margin-left:auto; background:{DELGA_RED}; color:white;
  font-size:11px; font-weight:600; padding:4px 14px;
  border-radius:20px; white-space:nowrap;
}}

/* KPI CARDS */
.kpi-wrap {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:18px; }}
.kpi-card {{
  background:white; border-radius:10px; padding:16px 18px;
  border-left:4px solid {DELGA_NAVY};
  box-shadow:0 1px 5px rgba(28,43,74,.08);
}}
.kpi-card.c-red    {{ border-left-color:{DELGA_RED}; }}
.kpi-card.c-green  {{ border-left-color:{DELGA_GREEN}; }}
.kpi-card.c-amber  {{ border-left-color:{DELGA_AMBER}; }}
.kpi-card.c-silver {{ border-left-color:{DELGA_SILVER}; }}
.kpi-lbl  {{ font-size:9px; font-weight:600; color:{DELGA_SILVER}; text-transform:uppercase; letter-spacing:.8px; margin-bottom:5px; }}
.kpi-val  {{ font-size:23px; font-weight:700; color:{DELGA_NAVY}; line-height:1.1; margin-bottom:3px; }}
.kpi-sub  {{ font-size:11px; color:#555; margin-bottom:2px; }}
.kpi-det  {{ font-size:10px; color:{DELGA_SILVER}; }}

/* SECTION */
.sc {{ background:white; border-radius:10px; padding:18px 20px; box-shadow:0 1px 5px rgba(28,43,74,.07); margin-bottom:14px; }}
.st {{
  font-size:11px; font-weight:700; color:{DELGA_NAVY};
  text-transform:uppercase; letter-spacing:.6px;
  border-bottom:2px solid {DELGA_RED};
  padding-bottom:6px; margin-bottom:12px; display:inline-block;
}}

/* NOTA */
.nota {{ background:#FFF8E1; border-left:3px solid {DELGA_AMBER}; border-radius:4px; padding:10px 14px; font-size:11px; color:#444; line-height:1.6; margin:14px 0; }}

/* TABELA */
.dt {{ width:100%; border-collapse:collapse; font-size:12px; }}
.dt thead tr {{ background:{DELGA_NAVY}; }}
.dt thead th {{ color:white; padding:9px 11px; text-align:left; font-weight:600; font-size:11px; white-space:nowrap; }}
.dt tbody tr:nth-child(even) {{ background:#FAFBFC; }}
.dt tbody tr:hover {{ background:{DELGA_LIGHT}; }}
.dt tbody td {{ padding:7px 11px; border-bottom:1px solid #EEF0F3; vertical-align:middle; }}
.dt tbody tr.tr-total td {{ background:{DELGA_LIGHT}; font-weight:700; border-top:2px solid {DELGA_NAVY}; border-bottom:none; }}

/* MACRO ROW — sempre visível */
.macro-table {{ width:100%; border-collapse:collapse; font-size:12px; }}
.macro-table td {{ padding:9px 11px; border-bottom:1px solid #EEF0F3; vertical-align:middle; }}
.macro-table tr:hover {{ background:{DELGA_LIGHT}; }}
.macro-head {{ background:{DELGA_NAVY}; }}
.macro-head th {{ color:white; padding:9px 11px; font-weight:600; font-size:11px; text-align:left; white-space:nowrap; }}
.macro-total td {{ background:{DELGA_LIGHT}; font-weight:700; border-top:2px solid {DELGA_NAVY}; }}

/* PROGRESS */
.pb-wrap {{ display:flex; align-items:center; gap:7px; }}
.pb-bg {{ height:7px; background:#E2E8F0; border-radius:4px; overflow:hidden; display:inline-block; }}
.pb-fill {{ height:100%; border-radius:4px; }}

/* BADGES */
.bdg {{ display:inline-block; padding:2px 7px; border-radius:10px; font-size:10px; font-weight:600; }}
.bdg-green  {{ background:#E8F5E9; color:{DELGA_GREEN}; }}
.bdg-amber  {{ background:#FFF3E0; color:{DELGA_AMBER}; }}
.bdg-red    {{ background:#FFEBEE; color:{DELGA_RED}; }}
.bdg-gray   {{ background:#F0F0F0; color:#666; }}
.bdg-navy   {{ background:#E8EDF5; color:{DELGA_NAVY}; }}

/* PROJECT DETAIL TABLE (dentro do expander) */
.proj-wrap {{ background:{DELGA_LIGHT}; border-radius:6px; padding:12px 14px; margin-top:6px; }}

/* LOGIN */
.login-wrap {{ max-width:360px; margin:80px auto; padding:40px; background:white; border-radius:12px; box-shadow:0 4px 24px rgba(28,43,74,.12); text-align:center; }}

#MainMenu {{visibility:hidden;}} footer {{visibility:hidden;}}
.stDeployButton {{display:none;}} header[data-testid="stHeader"] {{display:none;}}
div[data-testid="stExpander"] > div:first-child {{
  background:{DELGA_LIGHT} !important;
  border:1px solid #E2E8F0 !important;
  border-radius:8px !important;
  padding:2px 8px !important;
}}
</style>
""", unsafe_allow_html=True)

# ── SENHA ─────────────────────────────────────────────────────────────────────
SENHA = "Delga01"
DADOS_PATH = "/tmp/delga_dados.pkl"

def check_password():
    if st.session_state.get("auth"): return True
    st.markdown("""<div class="login-wrap">
      <div style="font-size:44px;margin-bottom:12px;">📊</div>
      <div style="font-size:20px;font-weight:700;color:#1C2B4A;margin-bottom:4px;">Grupo Delga</div>
      <div style="font-size:12px;color:#8A9BB0;margin-bottom:22px;">Dashboard Executivo 2026 — Acesso Restrito</div>
    </div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        pw = st.text_input("Senha", type="password", placeholder="Senha de acesso", label_visibility="collapsed")
        if st.button("Entrar →", use_container_width=True, type="primary"):
            if pw == SENHA:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    return False

if not check_password():
    st.stop()

# ── FORMATAÇÃO ────────────────────────────────────────────────────────────────
def fmt_mi(v):
    if pd.isna(v) or v is None: return "R$ 0"
    v = float(v)
    if abs(v) >= 1_000_000: return f"R$ {v/1_000_000:.2f} Mi"
    if abs(v) >= 1_000:     return "R$ " + f"{v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
    return f"R$ {v:.0f}"

def fmt_brl(v):
    if pd.isna(v) or v is None or float(v)==0: return "—"
    return "R$ " + f"{float(v):,.0f}".replace(",","X").replace(".",",").replace("X",".")

def fmt_date(v):
    if pd.isna(v) or v is None or str(v)=="nan": return "—"
    try:
        if isinstance(v,(datetime.datetime,datetime.date)): return v.strftime("%m/%Y")
        s = str(v)
        if " " in s: return pd.to_datetime(s).strftime("%m/%Y")
        return s[:7]
    except: return str(v)[:7]

def safe_float(v,d=0.0):
    try: return float(v) if pd.notna(v) else d
    except: return d

def pbar(pct, w=72):
    pc = min(float(pct)*100,100)
    c = DELGA_GREEN if pct>=.30 else (DELGA_AMBER if pct>=.15 else DELGA_RED)
    return (f'<div class="pb-wrap">'
            f'<div class="pb-bg" style="width:{w}px;">'
            f'<div class="pb-fill" style="width:{pc:.0f}%;background:{c};"></div></div>'
            f'<span style="font-size:11px;font-weight:600;">{pc:.1f}%</span></div>')

def bdg_status(pct):
    if pct>=.30: return f'<span class="bdg bdg-green">DESTAQUE ✓</span>'
    return f'<span class="bdg bdg-amber">EM EXECUÇÃO</span>'

def bdg_custos(v):
    v=str(v).strip()
    if v=="OK":                        return '<span class="bdg bdg-green">✓ OK</span>'
    if v in("Não Ok","NOK","Não OK"):  return '<span class="bdg bdg-red">✗ NOK</span>'
    if v in("","nan"):                 return '<span class="bdg bdg-gray">Pendente</span>'
    return f'<span class="bdg bdg-gray">{v}</span>'

def bdg_st(v):
    v=str(v)
    if "Concluído" in v: return '<span class="bdg bdg-green">✓ Concluído</span>'
    if "Execução"  in v: return '<span class="bdg bdg-amber">⏳ Execução</span>'
    if "Não"       in v: return '<span class="bdg bdg-gray">Não iniciado</span>'
    return f'<span class="bdg bdg-gray">{v}</span>'

def bdg_tipo(v):
    v=str(v).strip()
    if "BSW"   in v: return f'<span class="bdg bdg-navy">BSW</span>'
    if "Kaizen" in v or "kaizen" in v: return f'<span class="bdg bdg-amber">Kaizen</span>'
    if "Redução" in v or "Reducao" in v: return f'<span class="bdg bdg-green">Red. Custo</span>'
    if "Você" in v or "voce" in v.lower(): return f'<span class="bdg bdg-gray">Você Resolve</span>'
    return f'<span class="bdg bdg-gray">{v}</span>'

# ── PERSISTÊNCIA ──────────────────────────────────────────────────────────────
def save_bytes(b):
    with open(DADOS_PATH,"wb") as f: pickle.dump(b,f)
def load_bytes():
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH,"rb") as f: return pickle.load(f)
    return None

# ── CARGA ─────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(fb):
    import io
    def xls(sh):
        return pd.read_excel(io.BytesIO(fb), sheet_name=sh, header=None)
    d={}
    d["u5"]  = xls("5 Unidades  +")
    d["par"] = xls("Pareto")
    for s in ["Diadema","Jarinu","Ferraz","São Leopoldo","Anchieta","Compras ","Vendas","Corporativo"]:
        d[s]=xls(s)
    return d

# ── EXTRAÇÃO ──────────────────────────────────────────────────────────────────
def extract_kpis(d):
    df=d["u5"]
    return dict(
        meta     =safe_float(df.iloc[6,3]),
        portfolio=safe_float(df.iloc[6,5]),
        prev2026 =safe_float(df.iloc[6,6]),
        validado =safe_float(df.iloc[6,7]),
        real     =safe_float(df.iloc[6,9]),
        pct_ating=safe_float(df.iloc[6,11]),
        inic     =int(safe_float(df.iloc[6,13])),
    )

def extract_plantas(d):
    df=d["u5"]
    cfg=[("Diadema",4,"Diadema"),("Ferraz",5,"Ferraz"),
         ("São Leopoldo",6,"São Leopoldo"),("Jarinu",7,"Jarinu"),("Anchieta",8,"Anchieta")]
    res=[]
    for nome,col,sh in cfg:
        df_p=d.get(sh,pd.DataFrame())
        p2026=safe_float(df_p.iloc[4,3]) if not df_p.empty else 0
        res.append(dict(nome=nome,sheet=sh,
            meta=safe_float(df.iloc[21,col]),prev=safe_float(df.iloc[22,col]),
            prev2026=p2026,val=safe_float(df.iloc[24,col]),
            real=safe_float(df.iloc[25,col]),pct=safe_float(df.iloc[26,col])))
    return res

def extract_areas(d):
    df=d["u5"]
    cfg=[("Corporativo",9,"Corporativo"),("Compras",10,"Compras "),("Vendas",11,"Vendas")]
    res=[]
    for nome,col,sh in cfg:
        df_a=d.get(sh,pd.DataFrame())
        p2026=safe_float(df_a.iloc[4,4]) if (not df_a.empty and sh!="Corporativo") else 0
        res.append(dict(nome=nome,sheet=sh,
            meta=safe_float(df.iloc[21,col]),prev=safe_float(df.iloc[22,col]),
            prev2026=p2026,val=safe_float(df.iloc[24,col]),
            real=safe_float(df.iloc[25,col]),pct=safe_float(df.iloc[26,col])))
    return res

def extract_pilares(d):
    df=d["u5"]
    return [dict(nome=str(df.iloc[i,3]),qtd=int(safe_float(df.iloc[i,4])),
                 prev=safe_float(df.iloc[i,5]),val=safe_float(df.iloc[i,6]),
                 pct=safe_float(df.iloc[i,7]))
            for i in range(12,17) if pd.notna(df.iloc[i,3]) and str(df.iloc[i,3])!="TOTAL"]

def extract_evolucao(d):
    df=d["u5"]
    meses=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    def row(r): return [safe_float(df.iloc[r,c]) for c in range(22,34)]
    return dict(meses=meses,prev=row(53),real=row(54),
                acum_prev=row(56),acum_real=row(57),proj_meta=row(58))

def extract_proj_planta(d, sheet_key):
    """Extrai projetos de planta — para antes de '3. Adesão SPD' ou padrão inválido."""
    df=d.get(sheet_key)
    if df is None: return []
    res=[]
    # col0=tipo, col2=nome, col5=resp, col7=termino, col8=previsto,
    # col12=valid_custos_str, col13=saving_validado, col14=status
    for i in range(54, min(54+300, df.shape[0])):
        tipo=str(df.iloc[i,0]).strip()
        nome=str(df.iloc[i,2]).strip()
        if tipo in VALID_TIPOS and nome not in ("","nan"):
            res.append(dict(
                tipo=tipo, nome=nome,
                resp=str(df.iloc[i,5]).strip() if pd.notna(df.iloc[i,5]) else "—",
                termino=fmt_date(df.iloc[i,7]),
                previsto=safe_float(df.iloc[i,8]),
                val_custos=str(df.iloc[i,12]).strip() if pd.notna(df.iloc[i,12]) else "",
                val_saving=safe_float(df.iloc[i,13]),
                status=str(df.iloc[i,14]).strip() if pd.notna(df.iloc[i,14]) else "",
            ))
        elif pd.notna(df.iloc[i,0]) and tipo not in ("","nan") and tipo not in VALID_TIPOS:
            break   # parou no padrão diferente
    return res

def extract_proj_compras(d):
    df=d.get("Compras ")
    if df is None: return []
    res=[]
    # col0=tipo, col1=nome_cod, col3=nome_proj, col5=resp, col7=term, col8=prev, col12=val_cus, col13=saving, col14=status
    for i in range(30, min(30+200, df.shape[0])):
        tipo=str(df.iloc[i,0]).strip()
        nome=str(df.iloc[i,3]).strip()   # col3 = DESCRIÇÃO = nome real
        if tipo in VALID_TIPOS and nome not in ("","nan"):
            res.append(dict(
                tipo=tipo, nome=nome,
                resp=str(df.iloc[i,5]).strip() if pd.notna(df.iloc[i,5]) else "—",
                termino=fmt_date(df.iloc[i,7]),
                previsto=safe_float(df.iloc[i,8]),
                val_custos=str(df.iloc[i,12]).strip() if pd.notna(df.iloc[i,12]) else "",
                val_saving=safe_float(df.iloc[i,13]),
                status=str(df.iloc[i,14]).strip() if pd.notna(df.iloc[i,14]) else "",
            ))
        elif pd.notna(df.iloc[i,0]) and tipo not in ("","nan") and tipo not in VALID_TIPOS:
            break
    return res

def extract_proj_vendas(d):
    df=d.get("Vendas")
    if df is None: return []
    res=[]
    # col0=tipo, col1=nome, col4=resp, col7=prev, col13=status
    for i in range(40, min(40+100, df.shape[0])):
        tipo=str(df.iloc[i,0]).strip()
        nome=str(df.iloc[i,1]).strip()
        if tipo in VALID_TIPOS and nome not in ("","nan"):
            res.append(dict(
                tipo=tipo, nome=nome,
                resp=str(df.iloc[i,4]).strip() if pd.notna(df.iloc[i,4]) else "—",
                termino="—",
                previsto=safe_float(df.iloc[i,7]),
                val_custos="",
                val_saving=0,
                status=str(df.iloc[i,13]).strip() if pd.notna(df.iloc[i,13]) else "",
            ))
        elif pd.notna(df.iloc[i,0]) and tipo not in ("","nan") and tipo not in VALID_TIPOS:
            break
    return res

def extract_ranking(d):
    df=d["u5"]
    res=[]
    for i in range(53,137):
        uni=df.iloc[i,4]; nome=df.iloc[i,5]
        if not pd.notna(uni) or not pd.notna(nome): continue
        res.append(dict(
            pos=int(safe_float(df.iloc[i,3],i-52)),
            uni=str(uni), nome=str(nome),
            status=str(df.iloc[i,7]).strip() if pd.notna(df.iloc[i,7]) else "",
            custos=str(df.iloc[i,8]).strip() if pd.notna(df.iloc[i,8]) else "",
            prev26=safe_float(df.iloc[i,9]),
            prev_mo=safe_float(df.iloc[i,10]),
            real=safe_float(df.iloc[i,11]),
        ))
    return res

# ── GRÁFICOS ──────────────────────────────────────────────────────────────────
PAL=[DELGA_NAVY,"#2C4F7C","#4A7AB5",DELGA_SILVER,"#A8C8E8"]

def chart_funnel(kpis):
    stages=["Meta do Grupo","Portfólio Previsto","Previsto 2026","Validado Custos","Real DRE"]
    values=[kpis["meta"],kpis["portfolio"],kpis["prev2026"],kpis["validado"],kpis["real"]]
    colors=[DELGA_NAVY,"#2C5F8A","#4A90D9",DELGA_AMBER,DELGA_GREEN]
    fig=go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo="value+percent initial",
        texttemplate=[f"<b>{fmt_mi(v)}</b>" for v in values],
        marker=dict(color=colors,line=dict(width=1.5,color="white")),
        connector=dict(line=dict(color="#DDD",width=1.5,dash="dot")),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(margin=dict(l=10,r=10,t=10,b=10),height=320,
                      paper_bgcolor="white",plot_bgcolor="white",
                      font=dict(family="Inter",size=11))
    return fig

def chart_gauge(pct):
    clr=DELGA_GREEN if pct>=.30 else (DELGA_AMBER if pct>=.15 else DELGA_RED)
    fig=go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct*100,
        number=dict(suffix="%",font=dict(size=40,color=DELGA_NAVY,family="Inter")),
        gauge=dict(
            axis=dict(range=[0,100],ticksuffix="%",tickfont=dict(size=10)),
            bar=dict(color=clr,thickness=0.28),bgcolor="white",borderwidth=0,
            steps=[dict(range=[0,30],color="#FFEBEE"),
                   dict(range=[30,70],color="#FFF3E0"),
                   dict(range=[70,100],color="#E8F5E9")],
            threshold=dict(line=dict(color=DELGA_RED,width=3),thickness=.75,value=100),
        ),
        title=dict(text="<b>Atingimento da Meta</b>",font=dict(size=12,color=DELGA_SILVER)),
    ))
    fig.update_layout(margin=dict(l=20,r=20,t=50,b=10),height=280,paper_bgcolor="white")
    return fig

def chart_evolucao(ev,series):
    cfg={
        "Acumulado Previsto":dict(data=ev["acum_prev"],color=DELGA_NAVY, dash="solid"),
        "Acumulado Real":    dict(data=ev["acum_real"],color=DELGA_GREEN,dash="solid"),
        "Projeção da Meta":  dict(data=ev["proj_meta"],color=DELGA_RED,  dash="dash"),
        "Previsto Mensal":   dict(data=ev["prev"],     color="#4A90D9",  dash="dot"),
        "Real Mensal":       dict(data=ev["real"],     color="#28A745",  dash="dot"),
    }
    fig=go.Figure()
    for s in series:
        c=cfg[s]
        fig.add_trace(go.Scatter(x=ev["meses"],y=c["data"],mode="lines+markers",name=s,
            line=dict(color=c["color"],width=2.5,dash=c["dash"]),
            marker=dict(size=6,color=c["color"]),
            hovertemplate=f"<b>{s}</b><br>%{{x}}: R$ %{{y:,.0f}}<extra></extra>"))
    fig.update_layout(
        xaxis=dict(showgrid=True,gridcolor="#F0F4F8"),
        yaxis=dict(tickformat=",.0f",showgrid=True,gridcolor="#F0F4F8",title="R$"),
        legend=dict(orientation="h",y=1.05,x=0.5,xanchor="center",font=dict(size=11)),
        margin=dict(l=80,r=20,t=50,b=40),height=400,
        paper_bgcolor="white",plot_bgcolor="white",
        hovermode="x unified",font=dict(family="Inter"))
    return fig

def chart_donut(labels,values,colors):
    total=sum(values)
    txt=[f"  {labels[i]}  {values[i]/total*100:.1f}%  {fmt_mi(values[i])}" for i in range(len(labels))]
    fig=go.Figure(go.Pie(labels=txt,values=values,hole=0.62,marker=dict(colors=colors),
                          textinfo="none",hovertemplate="<b>%{label}</b><extra></extra>"))
    fig.update_layout(showlegend=True,
        legend=dict(orientation="v",y=0.5,x=0.55,yanchor="middle",font=dict(size=11)),
        margin=dict(l=10,r=10,t=10,b=30),height=280,
        paper_bgcolor="white",plot_bgcolor="white",
        annotations=[dict(text=f"<b>{fmt_mi(sum(values))}</b>",x=0.22,y=-0.08,font_size=12,showarrow=False)],
        font=dict(family="Inter"))
    return fig

def chart_pilares(pilares,real_total):
    labels=[p["nome"] for p in pilares]
    previsto=[p["prev"] for p in pilares]
    validado=[p["val"]  for p in pilares]
    tv=sum(validado)
    real_est=[v/tv*real_total if tv>0 else 0 for v in validado]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Previsto",x=labels,y=previsto,marker_color="#B8D4E8"))
    fig.add_trace(go.Bar(name="Validado",x=labels,y=validado,marker_color=DELGA_NAVY))
    fig.add_trace(go.Bar(name="Real DRE",x=labels,y=real_est, marker_color=DELGA_GREEN))
    fig.update_layout(barmode="group",
        yaxis=dict(tickformat=",.0f",showgrid=True,gridcolor="#F0F4F8"),
        legend=dict(orientation="h",y=1.05,x=1,xanchor="right",font=dict(size=11)),
        margin=dict(l=60,r=20,t=40,b=60),height=300,
        paper_bgcolor="white",plot_bgcolor="white",bargap=0.28,font=dict(family="Inter"))
    return fig

# ── HTML HELPERS ──────────────────────────────────────────────────────────────
def th(*cols):
    return "<table class='dt'><thead><tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr></thead><tbody>"

def proj_detail_html(projetos):
    if not projetos:
        return "<p style='color:#999;font-size:12px;padding:6px 0;'>Nenhum projeto encontrado.</p>"
    rows=""
    for p in projetos:
        rows+=f"""<tr>
          <td>{bdg_tipo(p['tipo'])}</td>
          <td style="max-width:260px;font-size:11px;">{p['nome']}</td>
          <td style="font-size:11px;">{p['resp']}</td>
          <td style="font-size:11px;">{p['termino']}</td>
          <td style="text-align:right;font-size:11px;">{fmt_brl(p['previsto'])}</td>
          <td style="text-align:right;font-size:11px;color:{DELGA_TEAL};">{fmt_brl(p['val_saving'])}</td>
          <td style="text-align:right;font-size:11px;color:{DELGA_GREEN};font-weight:600;">—</td>
          <td>{bdg_custos(p['val_custos'])}</td>
          <td>{bdg_st(p['status'])}</td>
        </tr>"""
    return th("Tipo","Projeto","Responsável","Término","V. Previsto","V. Validado","V. Real","Custos","Status")+rows+"</tbody></table>"

# Cabeçalho compartilhado da macro-tabela
MACRO_COLS = ["Unidade / Área","Meta 2026","Previsto Total",
              f'<span style="color:{DELGA_AMBER}">Previsto 2026</span>',
              f'<span style="color:{DELGA_TEAL}">Validado</span>',
              f'<span style="color:{DELGA_GREEN}">Real DRE</span>',
              "% Meta","Status"]

def macro_header_html():
    ths="".join(f'<th style="background:{DELGA_NAVY};color:white;padding:9px 11px;font-size:11px;font-weight:600;">{c}</th>'
                for c in MACRO_COLS)
    return f'<table class="macro-table"><thead><tr class="macro-head">{ths}</tr></thead></table>'

def macro_total_html(items):
    tm=tp=tp26=tv=tr=0
    for it in items:
        tm+=it["meta"]; tp+=it["prev"]; tp26+=it["prev2026"]
        tv+=it["val"];  tr+=it["real"]
    pt=tr/tm if tm>0 else 0
    return f"""<table class="macro-table"><tbody>
      <tr class="macro-total">
        <td><b>TOTAL</b></td>
        <td><b>{fmt_brl(tm)}</b></td>
        <td><b>{fmt_brl(tp)}</b></td>
        <td style="color:{DELGA_AMBER};"><b>{fmt_brl(tp26)}</b></td>
        <td style="color:{DELGA_TEAL};"><b>{fmt_brl(tv)}</b></td>
        <td style="color:{DELGA_GREEN};font-weight:700;"><b>{fmt_brl(tr)}</b></td>
        <td>{pbar(pt)}</td>
        <td></td>
      </tr></tbody></table>"""

def macro_row_html(it, key="nome"):
    return f"""<table class="macro-table"><tbody><tr>
      <td style="font-weight:600;min-width:130px;">{it[key]}</td>
      <td>{fmt_brl(it['meta'])}</td>
      <td>{fmt_brl(it['prev'])}</td>
      <td style="color:{DELGA_AMBER};">{fmt_brl(it['prev2026'])}</td>
      <td style="color:{DELGA_TEAL};">{fmt_brl(it['val'])}</td>
      <td style="color:{DELGA_GREEN};font-weight:600;">{fmt_brl(it['real'])}</td>
      <td>{pbar(it['pct'])}</td>
      <td>{bdg_status(it['pct'])}</td>
    </tr></tbody></table>"""

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

# HEADER
st.markdown(f"""<div class="delga-header">
  <img src="https://grupodelga.com.br/wp-content/uploads/2024/11/logo-fa-e-clientes-grupo-whatsapp-9-300x300.png"
       onerror="this.style.display='none'">
  <div class="delga-header-text">
    <h1>Dashboard Executivo — Grupo Delga 2026</h1>
    <p>Gestão Estratégica de Projetos e Redução de Custos</p>
  </div>
  <div class="delga-badge">Jun / 2026</div>
</div>""", unsafe_allow_html=True)

# ADMIN
with st.expander("🔐 Administrador — Atualizar Planilha"):
    arquivo=st.file_uploader("Nova versão (.xlsx)",type=["xlsx"],key="up")
    if arquivo:
        b=arquivo.read(); save_bytes(b)
        st.cache_data.clear()
        st.success("✅ Planilha atualizada! Todos os usuários verão os novos dados.")

# CARGA
fb=load_bytes()
if fb is None:
    st.warning("⚠️ Nenhuma planilha carregada. Expanda o painel Administrador para fazer o upload.")
    st.stop()
try:
    D=load_data(fb)
except Exception as e:
    st.error(f"Erro ao processar: {e}"); st.stop()

kpis    =extract_kpis(D)
plantas =extract_plantas(D)
areas   =extract_areas(D)
pilares =extract_pilares(D)
ev      =extract_evolucao(D)
ranking =extract_ranking(D)

meta=kpis["meta"]; portfolio=kpis["portfolio"]; prev2026=kpis["prev2026"]
validado=kpis["validado"]; real=kpis["real"]; pct_ating=kpis["pct_ating"]

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
cob=portfolio/meta*100 if meta>0 else 0
pp=prev2026/portfolio*100 if portfolio>0 else 0
pv=validado/prev2026*100 if prev2026>0 else 0

def kpi(cls,lbl,val_big,sub,det):
    return f"""<div class="kpi-card {cls}">
      <div class="kpi-lbl">{lbl}</div>
      <div class="kpi-val">{val_big}</div>
      <div class="kpi-sub">{sub}</div>
      <div class="kpi-det">{det}</div></div>"""

st.markdown(f"""<div class="kpi-wrap">
  {kpi("","Meta Anual do Grupo",fmt_mi(meta),fmt_brl(meta),"Objetivo 2026 — 100%")}
  {kpi("c-silver","Portfólio Previsto",fmt_mi(portfolio),fmt_brl(portfolio),f"{cob:.1f}% da meta · {kpis['inic']} iniciativas")}
  {kpi("c-amber","Previsto 2026",fmt_mi(prev2026),fmt_brl(prev2026),f"{pp:.1f}% do portfólio total")}
  {kpi("","Validado por Custos",fmt_mi(validado),fmt_brl(validado),f"{pv:.1f}% do Previsto 2026")}
  {kpi("c-green","Retorno Real (DRE)",fmt_mi(real),fmt_brl(real),f"{pct_ating*100:.1f}% de atingimento")}
</div>""", unsafe_allow_html=True)

# NOTA
st.markdown(f"""<div class="nota">
  <b>Metodologia — Tipos de Ganho:</b>&nbsp;
  <b>Redução de Custo</b> impacto direto no DRE ·
  <b>Custo Evitado</b> MO realocada internamente, não reduz GGF ·
  <b>Capital de Giro</b> melhora caixa, impacto no balanço e não no DRE.
</div>""", unsafe_allow_html=True)

# ── EVOLUÇÃO ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Evolução Mensal — Acumulado Previsto vs Real vs Meta</span>', unsafe_allow_html=True)
series_all=["Acumulado Previsto","Acumulado Real","Projeção da Meta","Previsto Mensal","Real Mensal"]
sel=st.multiselect("Séries:",series_all,default=series_all[:3],key="ev_sel")
if sel: st.plotly_chart(chart_evolucao(ev,sel),use_container_width=True,config={"displayModeBar":False})
st.markdown('</div>', unsafe_allow_html=True)

# ── FUNIL + GAUGE ──────────────────────────────────────────────────────────────
cfu,cga=st.columns([3,2])
with cfu:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Funil de Conversão — Portfólio → DRE</span>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:11px;color:{DELGA_SILVER};margin-bottom:8px;">Quanto do portfólio mapeado se converte em resultado no DRE?</p>', unsafe_allow_html=True)
    st.plotly_chart(chart_funnel(kpis),use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

with cga:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Atingimento da Meta</span>', unsafe_allow_html=True)
    st.plotly_chart(chart_gauge(pct_ating),use_container_width=True,config={"displayModeBar":False})
    gap_val=meta-real
    st.markdown(f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">
      <div style="background:{DELGA_LIGHT};border-radius:6px;padding:10px;text-align:center;">
        <div style="font-size:9px;font-weight:600;color:{DELGA_SILVER};text-transform:uppercase;letter-spacing:.6px;">GAP para Meta</div>
        <div style="font-size:15px;font-weight:700;color:{DELGA_RED};">{fmt_mi(gap_val)}</div>
      </div>
      <div style="background:{DELGA_LIGHT};border-radius:6px;padding:10px;text-align:center;">
        <div style="font-size:9px;font-weight:600;color:{DELGA_SILVER};text-transform:uppercase;letter-spacing:.6px;">Validado / Meta</div>
        <div style="font-size:15px;font-weight:700;color:{DELGA_NAVY};">{validado/meta*100:.1f}%</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── DONUTS ──────────────────────────────────────────────────────────────────────
cd1,cd2=st.columns(2)
with cd1:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Representatividade — Plantas Industriais</span>', unsafe_allow_html=True)
    st.plotly_chart(chart_donut([p["nome"] for p in plantas],[p["meta"] for p in plantas],PAL),
                    use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)
with cd2:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Representatividade — Áreas Funcionais</span>', unsafe_allow_html=True)
    st.plotly_chart(chart_donut([a["nome"] for a in areas],[a["meta"] for a in areas],
                                [DELGA_NAVY,DELGA_GREEN,"#20C997"]),
                    use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── PILARES ────────────────────────────────────────────────────────────────────
cp1,cp2=st.columns([3,2])
with cp1:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Distribuição por Tipo de Iniciativa</span>', unsafe_allow_html=True)
    st.plotly_chart(chart_pilares(pilares,real),use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)
with cp2:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Resumo por Pilar</span>', unsafe_allow_html=True)
    rows_p="".join(f"""<tr>
      <td style="font-size:11px;">{p['nome']}</td>
      <td style="text-align:center;font-size:11px;">{p['qtd']}</td>
      <td style="text-align:right;font-size:11px;">{fmt_mi(p['prev'])}</td>
      <td style="text-align:right;font-size:11px;color:{DELGA_TEAL};">{fmt_mi(p['val'])}</td>
    </tr>""" for p in pilares)
    st.markdown(th("Pilar","Qtd","Previsto","Validado")+rows_p+"</tbody></table>",
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PLANTAS INDUSTRIAIS — MACRO sempre visível + MICRO no expander
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Plantas Industriais — Performance Consolidada</span>', unsafe_allow_html=True)

# Cabeçalho fixo
st.markdown(macro_header_html(), unsafe_allow_html=True)

for p in plantas:
    # Linha MACRO — sempre visível ANTES do expander
    st.markdown(macro_row_html(p), unsafe_allow_html=True)
    # Expander com projetos MICRO
    with st.expander(f"＋  Ver projetos de {p['nome']}", expanded=False):
        proj = extract_proj_planta(D, p["sheet"])
        n = len(proj)
        st.markdown(f"<p style='font-size:11px;color:{DELGA_SILVER};margin-bottom:8px;'><b>{n} projetos</b> encontrados em {p['nome']}</p>",
                    unsafe_allow_html=True)
        st.markdown(proj_detail_html(proj), unsafe_allow_html=True)

# Linha TOTAL
st.markdown(macro_total_html(plantas), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREAS FUNCIONAIS — mesmo padrão
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Áreas Funcionais — Performance Consolidada</span>', unsafe_allow_html=True)
st.markdown(macro_header_html(), unsafe_allow_html=True)

area_proj_fn = {"Compras": extract_proj_compras, "Vendas": extract_proj_vendas}

for a in areas:
    st.markdown(macro_row_html(a), unsafe_allow_html=True)
    with st.expander(f"＋  Ver projetos de {a['nome']}", expanded=False):
        fn = area_proj_fn.get(a["nome"])
        if fn:
            proj = fn(D)
        else:
            proj = []
        n = len(proj)
        st.markdown(f"<p style='font-size:11px;color:{DELGA_SILVER};margin-bottom:8px;'><b>{n} projetos</b> encontrados em {a['nome']}</p>",
                    unsafe_allow_html=True)
        st.markdown(proj_detail_html(proj), unsafe_allow_html=True)

st.markdown(macro_total_html(areas), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── CLASSIFICAÇÃO ──────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Classificação de Ganhos</span>', unsafe_allow_html=True)
cc1,cc2,cc3=st.columns(3)
for col,cor,icon,titulo,texto in [
    (cc1,DELGA_NAVY, "🔥","Redução de Custo","Impacto direto no DRE. Reduz GGF de forma mensurável.<br><em>Ex: redução de MP, troca de fornecedor.</em>"),
    (cc2,DELGA_AMBER,"⚡","Custo Evitado",   "MO realocada internamente — não reduz GGF no DRE.<br><em>Ex: Kaizens que eliminam postos mas realocam MO.</em>"),
    (cc3,DELGA_GREEN,"🏦","Capital de Giro", "Reduz estoque e melhora fluxo de caixa. Impacto no balanço.<br><em>Ex: redução de estoque de matéria-prima.</em>"),
]:
    with col:
        st.markdown(f"""<div style="border:2px solid {cor};border-radius:8px;padding:14px 16px;">
          <div style="font-weight:700;color:{cor};margin-bottom:6px;font-size:13px;">{icon} {titulo}</div>
          <div style="font-size:11px;color:#444;line-height:1.6;">{texto}</div>
        </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── RANKING ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Ranking de Projetos — Todos os Pilares</span>', unsafe_allow_html=True)

rk1,rk2,rk3=st.columns([2,2,1])
with rk1:
    f_uni=st.multiselect("Unidade:",sorted({r["uni"] for r in ranking}),default=[],placeholder="Todas",key="rk_uni")
with rk2:
    f_st=st.multiselect("Status:", sorted({r["status"] for r in ranking if r["status"]}),default=[],placeholder="Todos",key="rk_st")
with rk3:
    n_lin=st.number_input("Linhas:",5,200,25,5)

pf=ranking
if f_uni: pf=[r for r in pf if r["uni"] in f_uni]
if f_st:  pf=[r for r in pf if r["status"] in f_st]

st.markdown(f"<p style='font-size:11px;color:{DELGA_SILVER};margin-bottom:6px;'>Exibindo {min(int(n_lin),len(pf))} de {len(pf)} projetos</p>",
            unsafe_allow_html=True)
rows_rk="".join(f"""<tr>
  <td style="text-align:center;color:{DELGA_SILVER};font-weight:700;font-size:11px;">{r['pos']}</td>
  <td style="font-weight:600;font-size:11px;">{r['uni']}</td>
  <td style="font-size:11px;">{r['nome']}</td>
  <td>{bdg_st(r['status'])}</td>
  <td>{bdg_custos(r['custos'])}</td>
  <td style="text-align:right;font-size:11px;">{fmt_brl(r['prev26'])}</td>
  <td style="text-align:right;font-size:11px;">{fmt_brl(r['prev_mo'])}</td>
  <td style="text-align:right;font-weight:700;color:{DELGA_GREEN};font-size:11px;">{fmt_brl(r['real'])}</td>
</tr>""" for r in pf[:int(n_lin)])
st.markdown(th("#","Unidade","Projeto","Status","Custos","Previsto 2026","Previsto Momento","Real DRE")+rows_rk+"</tbody></table>",
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── GAP ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown(f'<span class="st" style="border-bottom-color:{DELGA_AMBER};">GAP — Projetos Aguardando Validação de Custos</span>', unsafe_allow_html=True)
st.markdown(f'<p style="font-size:11px;color:{DELGA_SILVER};margin-bottom:10px;">Projetos com valor projetado mas ainda sem validação do depto de Custos.</p>', unsafe_allow_html=True)

gap=[r for r in ranking if r["custos"] not in ("OK","Não Ok","NOK","Não OK") and r["prev26"]>0]
by_uni={}
for r in gap: by_uni[r["uni"]]=by_uni.get(r["uni"],0)+r["prev26"]
tot_gap=sum(by_uni.values())

rows_gap="".join(f"""<tr>
  <td style="font-weight:600;">{u}</td>
  <td style="text-align:right;color:{DELGA_AMBER};font-weight:600;">{fmt_brl(v)}</td>
  <td style="text-align:right;">{v/tot_gap*100:.1f}%</td>
</tr>""" for u,v in sorted(by_uni.items(),key=lambda x:-x[1]))
rows_gap+=f"""<tr class="tr-total">
  <td>TOTAL GAP</td>
  <td style="text-align:right;color:{DELGA_AMBER};">{fmt_brl(tot_gap)}</td>
  <td style="text-align:right;">100%</td>
</tr>"""
st.markdown(f"<p style='font-size:11px;color:{DELGA_SILVER};'>{len(gap)} projetos aguardam validação</p>",
            unsafe_allow_html=True)
st.markdown(th("Unidade",f'<span style="color:{DELGA_AMBER}">Previsto 2026 (não validado)</span>',"% do Gap")+rows_gap+"</tbody></table>",
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="text-align:center;padding:14px 0;border-top:1px solid #EEF0F3;margin-top:4px;">
  <span style="font-size:11px;color:{DELGA_SILVER};">
    Dashboard Executivo · Grupo Delga 2026 · Gestão Estratégica de Projetos e Redução de Custos
  </span>
</div>""", unsafe_allow_html=True)

_,cft=st.columns([5,1])
with cft:
    if st.button("🚪 Sair",key="logout"):
        st.session_state["auth"]=False; st.rerun()
