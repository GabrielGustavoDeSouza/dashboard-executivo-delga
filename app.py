import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings, os, pickle, datetime

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Dashboard Executivo — Grupo Delga 2026",
    page_icon="https://grupodelga.com.br/wp-content/uploads/2024/11/logo-fa-e-clientes-grupo-whatsapp-9-300x300.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── PALETA DELGA ──────────────────────────────────────────────────────────────
NAVY   = "#1C2B4A"
RED    = "#C8202E"
SILVER = "#8A9BB0"
LIGHT  = "#F4F6F9"
WHITE  = "#FFFFFF"
GREEN  = "#1A7A3A"
AMBER  = "#E8A838"
TEAL   = "#20C997"

# ── TIPOS VÁLIDOS DE PROJETO ───────────────────────────────────────────────────
# Entram no DRE: BSW, Kaizen, Kaizen - Ganho Recorrente, Redução de Custo, Você Resolve
# NÃO entram no DRE: Kaizen - Custo Evitado, Kaizen - Capital de Giro
DRE_TIPOS = {
    'BSW', 'Kaizen', 'Kaizen - Ganho Recorrente',
    'Redução de custo', 'Redução de Custo', 'Redução de Custo ',
    'Você Resolve', 'Você resolve', 'Meta Executiva',
    'Estratégia Comercial', 'kaizen'
}
NAO_DRE_TIPOS = {
    'Kaizen - Custo Evitado', 'Kaizen - Capital de Giro'
}
VALID_TIPOS = DRE_TIPOS | NAO_DRE_TIPOS

# Agrupamento para o gráfico de pilares (exibe todos os subtipos de Kaizen)
PILARES_EXIBE = {
    'Kaizen': 'Kaizen',
    'kaizen': 'Kaizen',
    'Kaizen - Ganho Recorrente': 'Kaizen - Ganho Recorrente',
    'Kaizen - Custo Evitado':    'Kaizen - Custo Evitado',
    'Kaizen - Capital de Giro':  'Kaizen - Capital de Giro',
    'Redução de custo':          'Redução de Custo',
    'Redução de Custo':          'Redução de Custo',
    'Redução de Custo ':         'Redução de Custo',
    'Você Resolve':              'Você Resolve',
    'Você resolve':              'Você Resolve',
    'BSW':                       'BSW',
    'Meta Executiva':            'Meta Executiva',
    'Estratégia Comercial':      'Estratégia Comercial',
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif;}}
.block-container{{padding-top:0!important;padding-bottom:1rem;max-width:1440px;}}

/* HEADER */
.dh{{background:{NAVY};padding:16px 28px;border-radius:0 0 8px 8px;
     display:flex;align-items:center;gap:16px;margin-bottom:18px;}}
.dh img{{height:42px;border-radius:4px;}}
.dh-t h1{{color:white;font-size:19px;font-weight:700;margin:0;}}
.dh-t p{{color:{SILVER};font-size:11px;margin:2px 0 0;}}
.dh-b{{margin-left:auto;background:{RED};color:white;font-size:11px;
       font-weight:600;padding:4px 14px;border-radius:20px;white-space:nowrap;}}

/* KPI */
.kpi-wrap{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:18px;}}
.kpi-card{{background:white;border-radius:10px;padding:16px 18px;
           border-left:4px solid {NAVY};box-shadow:0 1px 5px rgba(28,43,74,.08);}}
.kpi-card.cr{{border-left-color:{RED};}}
.kpi-card.cg{{border-left-color:{GREEN};}}
.kpi-card.ca{{border-left-color:{AMBER};}}
.kpi-card.cs{{border-left-color:{SILVER};}}
.kpi-l{{font-size:9px;font-weight:600;color:{SILVER};text-transform:uppercase;
        letter-spacing:.8px;margin-bottom:5px;}}
.kpi-v{{font-size:23px;font-weight:700;color:{NAVY};line-height:1.1;margin-bottom:3px;}}
.kpi-s{{font-size:11px;color:#555;margin-bottom:2px;}}
.kpi-d{{font-size:10px;color:{SILVER};}}

/* SECTION */
.sc{{background:white;border-radius:10px;padding:18px 20px;
     box-shadow:0 1px 5px rgba(28,43,74,.07);margin-bottom:14px;}}
.st{{font-size:11px;font-weight:700;color:{NAVY};text-transform:uppercase;
     letter-spacing:.6px;border-bottom:2px solid {RED};
     padding-bottom:6px;margin-bottom:12px;display:inline-block;}}

/* NOTA */
.nota{{background:#FFF8E1;border-left:3px solid {AMBER};border-radius:4px;
       padding:10px 14px;font-size:11px;color:#444;line-height:1.6;margin:14px 0;}}

/* TABELA */
.dt{{width:100%;border-collapse:collapse;font-size:12px;}}
.dt thead tr{{background:{NAVY};}}
.dt thead th{{color:white;padding:9px 11px;text-align:left;font-weight:600;
              font-size:11px;white-space:nowrap;}}
.dt tbody tr:nth-child(even){{background:#FAFBFC;}}
.dt tbody tr:hover{{background:{LIGHT};}}
.dt tbody td{{padding:7px 11px;border-bottom:1px solid #EEF0F3;vertical-align:middle;}}
.dt tbody tr.tr-tot td{{background:{LIGHT};font-weight:700;border-top:2px solid {NAVY};border-bottom:none;}}

/* MACRO ROW */
.mct{{width:100%;border-collapse:collapse;font-size:12px;}}
.mct td{{padding:9px 11px;border-bottom:1px solid #EEF0F3;vertical-align:middle;}}
.mct tr:hover{{background:{LIGHT};}}
.mch{{background:{NAVY};}}
.mch th{{color:white;padding:9px 11px;font-weight:600;font-size:11px;
         text-align:left;white-space:nowrap;}}
.mc-tot td{{background:{LIGHT};font-weight:700;border-top:2px solid {NAVY};}}

/* PROGRESS */
.pb{{display:flex;align-items:center;gap:7px;}}
.pb-bg{{height:7px;background:#E2E8F0;border-radius:4px;overflow:hidden;display:inline-block;}}
.pb-f{{height:100%;border-radius:4px;}}

/* BADGES */
.bdg{{display:inline-block;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:600;}}
.bg{{background:#E8F5E9;color:{GREEN};}}
.ba{{background:#FFF3E0;color:{AMBER};}}
.br{{background:#FFEBEE;color:{RED};}}
.bk{{background:#F0F0F0;color:#666;}}
.bn{{background:#E8EDF5;color:{NAVY};}}

/* IMPEDIMENTO */
.imp{{background:#FFF3E0;border-left:3px solid {AMBER};border-radius:4px;
      padding:4px 8px;font-size:10px;color:#555;margin-top:2px;line-height:1.4;}}

/* LOGIN */
.lw{{max-width:360px;margin:80px auto;padding:40px;background:white;
     border-radius:12px;box-shadow:0 4px 24px rgba(28,43,74,.12);text-align:center;}}

#MainMenu{{visibility:hidden;}}footer{{visibility:hidden;}}
.stDeployButton{{display:none;}}header[data-testid="stHeader"]{{display:none;}}
div[data-testid="stExpander"]>div:first-child{{
  background:{LIGHT}!important;border:1px solid #E2E8F0!important;
  border-radius:8px!important;padding:2px 8px!important;}}
</style>
""", unsafe_allow_html=True)

# ── SENHA ─────────────────────────────────────────────────────────────────────
SENHA = "Delga01"
DADOS_PATH = "/tmp/delga_dados.pkl"

def check_password():
    if st.session_state.get("auth"): return True
    st.markdown("""<div class="lw">
      <div style="font-size:44px;margin-bottom:12px;">📊</div>
      <div style="font-size:20px;font-weight:700;color:#1C2B4A;margin-bottom:4px;">Grupo Delga</div>
      <div style="font-size:12px;color:#8A9BB0;margin-bottom:22px;">Dashboard Executivo 2026 — Acesso Restrito</div>
    </div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        pw = st.text_input("Senha", type="password", placeholder="Senha de acesso",
                           label_visibility="collapsed")
        if st.button("Entrar →", use_container_width=True, type="primary"):
            if pw == SENHA:
                st.session_state["auth"] = True; st.rerun()
            else:
                st.error("Senha incorreta.")
    return False

if not check_password(): st.stop()

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
        s=str(v)
        if " " in s: return pd.to_datetime(s).strftime("%m/%Y")
        return s[:7]
    except: return str(v)[:7]

def safe(v, d=0.0):
    try: return float(v) if pd.notna(v) else d
    except: return d

def pbar_html(pct, w=72):
    pc = min(float(pct)*100, 100)
    c = GREEN if pct>=.30 else (AMBER if pct>=.15 else RED)
    return (f'<div class="pb"><div class="pb-bg" style="width:{w}px;">'
            f'<div class="pb-f" style="width:{pc:.0f}%;background:{c};"></div></div>'
            f'<span style="font-size:11px;font-weight:600;">{pc:.1f}%</span></div>')

def bdg_status(pct):
    return ('<span class="bdg bg">DESTAQUE ✓</span>' if pct>=.30
            else '<span class="bdg ba">EM EXECUÇÃO</span>')

def bdg_custos(v):
    v=str(v).strip()
    if v=="OK":                       return '<span class="bdg bg">✓ OK</span>'
    if v in("Não Ok","NOK","Não OK"): return '<span class="bdg br">✗ NOK</span>'
    if v in("","nan"):                return '<span class="bdg bk">Pendente</span>'
    return f'<span class="bdg bk">{v}</span>'

def bdg_st(v):
    v=str(v)
    if "Concluído" in v: return '<span class="bdg bg">✓ Concluído</span>'
    if "Execução"  in v: return '<span class="bdg ba">⏳ Execução</span>'
    if "Não"       in v: return '<span class="bdg bk">Não iniciado</span>'
    return f'<span class="bdg bk">{v[:20]}</span>'

def bdg_tipo(v):
    v=str(v).strip()
    if "BSW"         in v: return f'<span class="bdg bn">BSW</span>'
    if "Capital"     in v: return f'<span class="bdg" style="background:#EDE7F6;color:#512DA8;">Cap. Giro</span>'
    if "Evitado"     in v: return f'<span class="bdg" style="background:#E3F2FD;color:#0D47A1;">C. Evitado</span>'
    if "Recorrente"  in v: return f'<span class="bdg ba">Kaizen GR</span>'
    if "Kaizen"      in v or "kaizen" in v: return f'<span class="bdg ba">Kaizen</span>'
    if "Redução"     in v: return f'<span class="bdg bg">Red. Custo</span>'
    if "Você"        in v or "Voce" in v: return f'<span class="bdg bk">Você Resolve</span>'
    if "Meta"        in v: return f'<span class="bdg bn">Meta Exec.</span>'
    if "Estratégia"  in v: return f'<span class="bdg bn">Est. Comercial</span>'
    return f'<span class="bdg bk">{v[:15]}</span>'

def is_dre(tipo):
    """True se o tipo de projeto entra no DRE."""
    return str(tipo).strip() in DRE_TIPOS

# ── PERSISTÊNCIA ──────────────────────────────────────────────────────────────
def save_bytes(b):
    with open(DADOS_PATH,"wb") as f: pickle.dump(b,f)
def load_bytes():
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH,"rb") as f: return pickle.load(f)
    return None

# ── CARGA DO EXCEL ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(fb):
    import io
    def xls(sh): return pd.read_excel(io.BytesIO(fb), sheet_name=sh, header=None)
    d = {}
    d["u5"]  = xls("5 Unidades  +")
    d["par"] = xls("Pareto")
    for s in ["Diadema","Jarinu","Ferraz","São Leopoldo","Anchieta",
              "Compras ","Vendas","Corporativo"]:
        d[s] = xls(s)
    return d

# ── EXTRAÇÃO — KPIs GLOBAIS ───────────────────────────────────────────────────
def extract_kpis(d):
    df = d["u5"]
    return dict(
        meta     =safe(df.iloc[6,3]),
        portfolio=safe(df.iloc[6,5]),
        prev2026 =safe(df.iloc[6,6]),
        validado =safe(df.iloc[6,7]),
        real     =safe(df.iloc[6,9]),
        pct_ating=safe(df.iloc[6,11]),
        inic     =int(safe(df.iloc[6,13])),
    )

def extract_plantas(d):
    df = d["u5"]
    cfg = [("Diadema",4,"Diadema"),("Ferraz",5,"Ferraz"),
           ("São Leopoldo",6,"São Leopoldo"),("Jarinu",7,"Jarinu"),("Anchieta",8,"Anchieta")]
    res=[]
    for nome,col,sh in cfg:
        df_p = d.get(sh, pd.DataFrame())
        p2026 = safe(df_p.iloc[4,3]) if not df_p.empty else 0
        res.append(dict(nome=nome,sheet=sh,
            meta=safe(df.iloc[21,col]),prev=safe(df.iloc[22,col]),
            prev2026=p2026,val=safe(df.iloc[24,col]),
            real=safe(df.iloc[25,col]),pct=safe(df.iloc[26,col])))
    return res

def extract_areas(d):
    df = d["u5"]
    cfg = [("Corporativo",9,"Corporativo"),("Compras",10,"Compras "),("Vendas",11,"Vendas")]
    res=[]
    for nome,col,sh in cfg:
        df_a = d.get(sh, pd.DataFrame())
        p2026 = safe(df_a.iloc[4,4]) if (not df_a.empty and sh!="Corporativo") else 0
        res.append(dict(nome=nome,sheet=sh,
            meta=safe(df.iloc[21,col]),prev=safe(df.iloc[22,col]),
            prev2026=p2026,val=safe(df.iloc[24,col]),
            real=safe(df.iloc[25,col]),pct=safe(df.iloc[26,col])))
    return res

def extract_pilares_global(d):
    """Pilares do painel 5 Unidades (rows 12-16)."""
    df = d["u5"]
    res=[]
    for i in range(12,17):
        nome=df.iloc[i,3]
        if pd.notna(nome) and str(nome)!="TOTAL":
            res.append(dict(
                nome=str(nome),qtd=int(safe(df.iloc[i,4])),
                prev=safe(df.iloc[i,5]),val=safe(df.iloc[i,6]),
                pct=safe(df.iloc[i,7])))
    return res

def extract_pilares_local(projetos):
    """
    Gera resumo de pilares a partir da lista de projetos de uma unidade,
    incluindo todos os subtipos de Kaizen. Retorna lista ordenada.
    """
    from collections import defaultdict
    qtd  = defaultdict(int)
    prev = defaultdict(float)
    real = defaultdict(float)
    for p in projetos:
        nome = PILARES_EXIBE.get(p["tipo"], p["tipo"])
        qtd[nome]  += 1
        prev[nome] += p["previsto"]
        real[nome] += p["real_ano"]
    ORDER = ["BSW","Kaizen","Kaizen - Ganho Recorrente",
             "Kaizen - Custo Evitado","Kaizen - Capital de Giro",
             "Redução de Custo","Você Resolve","Meta Executiva","Estratégia Comercial"]
    res=[]
    for k in ORDER:
        if k in qtd:
            entra_dre = k not in ("Kaizen - Custo Evitado","Kaizen - Capital de Giro")
            res.append(dict(nome=k,qtd=qtd[k],prev=prev[k],real=real[k],dre=entra_dre))
    for k in sorted(qtd):
        if k not in ORDER:
            entra_dre = k not in ("Kaizen - Custo Evitado","Kaizen - Capital de Giro")
            res.append(dict(nome=k,qtd=qtd[k],prev=prev[k],real=real[k],dre=entra_dre))
    return res

def extract_evolucao(d):
    df = d["u5"]
    meses=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    def row(r): return [safe(df.iloc[r,c]) for c in range(22,34)]
    return dict(meses=meses,prev=row(53),real=row(54),
                acum_prev=row(56),acum_real=row(57),proj_meta=row(58))

# ── EXTRAÇÃO DE PROJETOS — FUNÇÃO CENTRAL ─────────────────────────────────────
def extract_projetos(df, start_row, col_tipo=0, col_nome=2, col_resp=5,
                     col_termino=7, col_custos=12, col_saving=13,
                     col_status=14, col_impede=15,
                     col_prev_real=17,  # col com 'Previsto'/'Real'
                     col_total_ano=35): # col com Total Ano
    """
    Extrai projetos de uma aba usando a lógica:
      - Linha Previsto: col_tipo in VALID_TIPOS + col_nome preenchido + col_prev_real='Previsto'
      - Linha Real: row+1, col_prev_real='Real', col_total_ano = valor real acumulado
    Para antes de qualquer tipo não reconhecido (seção SPD, etc.)
    """
    res = []
    i = start_row
    max_row = min(start_row + 600, df.shape[0] - 1)
    while i <= max_row:
        tipo = str(df.iloc[i, col_tipo]).strip()
        nome = str(df.iloc[i, col_nome]).strip()
        c_pr = str(df.iloc[i, col_prev_real]).strip() if df.shape[1] > col_prev_real else ""

        if tipo in VALID_TIPOS and nome not in ("", "nan") and c_pr == "Previsto":
            # Linha Previsto — Total Ano
            tot_prev = safe(df.iloc[i, col_total_ano])

            # Linha Real (row+1)
            tot_real = 0.0
            impede = ""
            if i+1 <= max_row:
                c_pr_next = str(df.iloc[i+1, col_prev_real]).strip() if df.shape[1] > col_prev_real else ""
                if c_pr_next == "Real":
                    tot_real = safe(df.iloc[i+1, col_total_ano])

            # O que impede (col15 da linha Previsto)
            if col_impede is not None and df.shape[1] > col_impede:
                v_imp = df.iloc[i, col_impede]
                if pd.notna(v_imp) and str(v_imp).strip() not in ("", "nan"):
                    impede = str(v_imp).strip()

            res.append(dict(
                tipo     = tipo,
                nome     = nome,
                resp     = str(df.iloc[i, col_resp]).strip() if pd.notna(df.iloc[i, col_resp]) else "—",
                termino  = fmt_date(df.iloc[i, col_termino]),
                previsto = tot_prev,
                real_ano = tot_real,
                val_custos = str(df.iloc[i, col_custos]).strip() if pd.notna(df.iloc[i, col_custos]) else "",
                val_saving = safe(df.iloc[i, col_saving]),
                status   = str(df.iloc[i, col_status]).strip() if pd.notna(df.iloc[i, col_status]) else "",
                impede   = impede,
                entra_dre= is_dre(tipo),
            ))
            i += 2  # pula Previsto + Real
        elif tipo not in ("", "nan") and tipo not in VALID_TIPOS:
            break   # seção SPD ou outro bloco diferente — para
        else:
            i += 1
    return res

def get_proj_planta(d, sheet_key):
    df = d.get(sheet_key)
    if df is None: return []
    # Plantas: col0=tipo,col2=nome,col5=resp,col7=term,col12=custos,col13=saving,col14=status,col15=impede,col17=Prev/Real,col35=TotalAno
    return extract_projetos(df, start_row=54,
        col_tipo=0, col_nome=2, col_resp=5, col_termino=7,
        col_custos=12, col_saving=13, col_status=14, col_impede=15,
        col_prev_real=17, col_total_ano=35)

def get_proj_compras(d):
    df = d.get("Compras ")
    if df is None: return []
    # Compras: col0=tipo,col3=nome,col5=resp,col7=term,col12=custos,col13=saving,col14=status,col17=Prev/Real,col35=TotalAno
    # col_impede: verificar se existe col15 ou col16
    return extract_projetos(df, start_row=30,
        col_tipo=0, col_nome=3, col_resp=5, col_termino=7,
        col_custos=12, col_saving=13, col_status=14, col_impede=None,
        col_prev_real=17, col_total_ano=35)

def get_proj_vendas(d):
    df = d.get("Vendas")
    if df is None: return []
    # Vendas: col0=tipo,col1=nome,col4=resp,col6=term,col11=custos,col12=saving,col13=status,col15=Prev/Real,col33=TotalAno
    return extract_projetos(df, start_row=36,
        col_tipo=0, col_nome=1, col_resp=4, col_termino=6,
        col_custos=11, col_saving=12, col_status=13, col_impede=None,
        col_prev_real=15, col_total_ano=33)

def extract_ranking(d):
    df = d["u5"]
    res=[]
    for i in range(53,137):
        uni=df.iloc[i,4]; nome=df.iloc[i,5]
        if not pd.notna(uni) or not pd.notna(nome): continue
        res.append(dict(
            pos=int(safe(df.iloc[i,3],i-52)),
            uni=str(uni),nome=str(nome),
            status=str(df.iloc[i,7]).strip() if pd.notna(df.iloc[i,7]) else "",
            custos=str(df.iloc[i,8]).strip() if pd.notna(df.iloc[i,8]) else "",
            prev26=safe(df.iloc[i,9]),prev_mo=safe(df.iloc[i,10]),real=safe(df.iloc[i,11]),
        ))
    return res

# ── GRÁFICOS ──────────────────────────────────────────────────────────────────
PAL = [NAVY,"#2C4F7C","#4A7AB5",SILVER,"#A8C8E8"]

def chart_funnel(kpis):
    stages = ["Meta do Grupo","Portfólio Previsto","Previsto 2026","Validado Custos","Real DRE"]
    values = [kpis["meta"],kpis["portfolio"],kpis["prev2026"],kpis["validado"],kpis["real"]]
    pcts   = [f"{v/kpis['meta']*100:.1f}%" for v in values]
    colors = [NAVY,"#2C5F8A","#4A90D9",AMBER,GREEN]

    fig = go.Figure()
    # Barras horizontais simulando funil (comprimento proporcional)
    for idx,(stage,val,pct,color) in enumerate(zip(stages,values,pcts,colors)):
        w = val/kpis["meta"]
        fig.add_trace(go.Bar(
            x=[val], y=[stage],
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=f"  <b>{fmt_mi(val)}</b>  <span style='opacity:.7'>({pct})</span>",
            textposition="outside",
            textfont=dict(size=12,color="#333"),
            hovertemplate=f"<b>{stage}</b><br>{fmt_mi(val)}<br>{pct} da meta<extra></extra>",
            showlegend=False,
            base=[(kpis["meta"]-val)/2],  # centraliza para efeito funil
        ))

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(visible=False, range=[0, kpis["meta"]*1.3]),
        yaxis=dict(autorange="reversed",tickfont=dict(size=12,color="#444")),
        margin=dict(l=130,r=150,t=10,b=10),
        height=310,
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter"),
    )
    return fig

def chart_gauge(pct):
    clr = GREEN if pct>=.30 else (AMBER if pct>=.15 else RED)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct*100,
        number=dict(suffix="%",font=dict(size=40,color=NAVY,family="Inter")),
        gauge=dict(
            axis=dict(range=[0,100],ticksuffix="%",tickfont=dict(size=10)),
            bar=dict(color=clr,thickness=0.28),
            bgcolor="white",borderwidth=0,
            steps=[dict(range=[0,30],color="#FFEBEE"),
                   dict(range=[30,70],color="#FFF3E0"),
                   dict(range=[70,100],color="#E8F5E9")],
            threshold=dict(line=dict(color=RED,width=3),thickness=.75,value=100),
        ),
        title=dict(text="<b>Atingimento da Meta</b>",font=dict(size=12,color=SILVER)),
    ))
    fig.update_layout(margin=dict(l=20,r=20,t=50,b=10),height=280,paper_bgcolor="white")
    return fig

def chart_evolucao(ev, series):
    cfg = {
        "Acumulado Previsto":dict(data=ev["acum_prev"],color=NAVY, dash="solid"),
        "Acumulado Real":    dict(data=ev["acum_real"],color=GREEN,dash="solid"),
        "Projeção da Meta":  dict(data=ev["proj_meta"],color=RED,  dash="dash"),
        "Previsto Mensal":   dict(data=ev["prev"],     color="#4A90D9",dash="dot"),
        "Real Mensal":       dict(data=ev["real"],     color="#28A745",dash="dot"),
    }
    fig = go.Figure()
    for s in series:
        c = cfg[s]
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
    total = sum(values)
    txt = [f"  {labels[i]}  {values[i]/total*100:.1f}%  {fmt_mi(values[i])}"
           for i in range(len(labels))]
    fig = go.Figure(go.Pie(labels=txt,values=values,hole=0.62,
        marker=dict(colors=colors),textinfo="none",
        hovertemplate="<b>%{label}</b><extra></extra>"))
    fig.update_layout(showlegend=True,
        legend=dict(orientation="v",y=0.5,x=0.55,yanchor="middle",font=dict(size=11)),
        margin=dict(l=10,r=10,t=10,b=30),height=280,
        paper_bgcolor="white",plot_bgcolor="white",
        annotations=[dict(text=f"<b>{fmt_mi(sum(values))}</b>",x=0.22,y=-0.08,
                          font_size=12,showarrow=False)],
        font=dict(family="Inter"))
    return fig

def chart_pilares(pilares_global, real_total):
    """Gráfico de pilares do painel global (5 Unidades)."""
    labels=[p["nome"] for p in pilares_global]
    previsto=[p["prev"] for p in pilares_global]
    validado=[p["val"]  for p in pilares_global]
    tv=sum(validado)
    real_est=[v/tv*real_total if tv>0 else 0 for v in validado]
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Previsto",x=labels,y=previsto,marker_color="#B8D4E8"))
    fig.add_trace(go.Bar(name="Validado",x=labels,y=validado,marker_color=NAVY))
    fig.add_trace(go.Bar(name="Real DRE",x=labels,y=real_est, marker_color=GREEN))
    fig.update_layout(barmode="group",
        yaxis=dict(tickformat=",.0f",showgrid=True,gridcolor="#F0F4F8"),
        legend=dict(orientation="h",y=1.05,x=1,xanchor="right",font=dict(size=11)),
        margin=dict(l=60,r=20,t=40,b=60),height=300,
        paper_bgcolor="white",plot_bgcolor="white",
        bargap=0.28,font=dict(family="Inter"))
    return fig

# ── HTML HELPERS ──────────────────────────────────────────────────────────────
def th(*cols):
    ths = "".join(f"<th>{c}</th>" for c in cols)
    return f"<table class='dt'><thead><tr>{ths}</tr></thead><tbody>"

def proj_table_html(projetos):
    """Tabela de projetos com coluna 'O que impede'."""
    if not projetos:
        return "<p style='color:#999;font-size:12px;padding:6px 0;'>Nenhum projeto encontrado.</p>"
    rows = ""
    for p in projetos:
        real_v = p["real_ano"]
        real_s = fmt_brl(real_v) if real_v and real_v != 0 else "—"
        real_c = GREEN if real_v and real_v > 0 else "#999"

        impede_html = ""
        if p.get("impede"):
            impede_html = f'<div class="imp">⚠️ {p["impede"]}</div>'

        # Indicador de DRE
        dre_icon = (f'<span title="Entra no DRE" style="color:{GREEN};font-size:10px;">✓ DRE</span>'
                    if p["entra_dre"] else
                    f'<span title="Não entra no DRE" style="color:{SILVER};font-size:10px;">↷ N/DRE</span>')

        rows += f"""<tr>
          <td>{bdg_tipo(p['tipo'])}<br>{dre_icon}</td>
          <td style="max-width:240px;font-size:11px;">{p['nome']}{impede_html}</td>
          <td style="font-size:11px;">{p['resp']}</td>
          <td style="font-size:11px;white-space:nowrap;">{p['termino']}</td>
          <td style="text-align:right;font-size:11px;">{fmt_brl(p['previsto'])}</td>
          <td style="text-align:right;font-size:11px;color:{TEAL};">{fmt_brl(p['val_saving'])}</td>
          <td style="text-align:right;font-size:11px;color:{real_c};font-weight:600;">{real_s}</td>
          <td>{bdg_custos(p['val_custos'])}</td>
          <td>{bdg_st(p['status'])}</td>
        </tr>"""
    return (th("Tipo","Projeto / Impedimento","Responsável","Término",
               "V.Previsto (Ano)","V.Validado","V.Real (Acum.)","Custos","Status")
            + rows + "</tbody></table>")

def pilar_resumo_html(projetos):
    """Tabela de resumo de pilares local — compacta, sem quebra de palavra."""
    pilares = extract_pilares_local(projetos)
    if not pilares: return ""
    ABREV = {
        "Kaizen - Ganho Recorrente": "Kaizen GR",
        "Kaizen - Custo Evitado":    "K. C. Evitado",
        "Kaizen - Capital de Giro":  "K. Cap. Giro",
        "Redução de Custo":          "Red. Custo",
        "Estratégia Comercial":      "Est. Comercial",
        "Meta Executiva":            "Meta Exec.",
    }
    rows = ""
    for p in pilares:
        nome_abrev = ABREV.get(p["nome"], p["nome"])
        dot_color = GREEN if p["dre"] else SILVER
        dot = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{dot_color};margin-right:4px;vertical-align:middle;"></span>'
        real_c = GREEN if p["real"] > 0 else SILVER
        rows += f"""<tr>
          <td style="font-size:10px;white-space:nowrap;">{dot}<b>{nome_abrev}</b></td>
          <td style="text-align:center;font-size:11px;font-weight:700;color:{NAVY};">{p['qtd']}</td>
          <td style="text-align:right;font-size:10px;">{fmt_mi(p['prev'])}</td>
          <td style="text-align:right;font-size:10px;color:{real_c};font-weight:600;">{fmt_mi(p['real'])}</td>
        </tr>"""
    tot_qtd  = sum(p["qtd"]  for p in pilares)
    tot_prev = sum(p["prev"] for p in pilares)
    tot_real = sum(p["real"] for p in pilares)
    rows += f"""<tr class="tr-tot">
      <td style="font-size:10px;">TOTAL</td>
      <td style="text-align:center;font-size:11px;">{tot_qtd}</td>
      <td style="text-align:right;font-size:10px;">{fmt_mi(tot_prev)}</td>
      <td style="text-align:right;font-size:10px;color:{GREEN};">{fmt_mi(tot_real)}</td>
    </tr>"""
    legend = (f'<p style="font-size:9px;color:{SILVER};margin-top:5px;">'
              f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{GREEN};margin-right:3px;vertical-align:middle;"></span>DRE&nbsp;&nbsp;'
              f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{SILVER};margin-right:3px;vertical-align:middle;"></span>Não DRE</p>')
    return (th("Pilar","Qtd","Previsto","Real Acum.") + rows + "</tbody></table>" + legend)

# Cabeçalho macro-tabela
MC_COLS = ["Unidade / Área","Meta 2026","Previsto Total",
           f'<span style="color:{AMBER}">Previsto 2026</span>',
           f'<span style="color:{TEAL}">Validado</span>',
           f'<span style="color:{GREEN}">Real DRE</span>',
           "% Meta","Status"]

def mc_header():
    ths = "".join(f'<th style="background:{NAVY};color:white;padding:9px 11px;'
                  f'font-size:11px;font-weight:600;">{c}</th>' for c in MC_COLS)
    return f'<table class="mct"><thead><tr>{ths}</tr></thead></table>'

def mc_row(it):
    return f"""<table class="mct"><tbody><tr>
      <td style="font-weight:600;min-width:130px;">{it['nome']}</td>
      <td>{fmt_brl(it['meta'])}</td>
      <td>{fmt_brl(it['prev'])}</td>
      <td style="color:{AMBER};">{fmt_brl(it['prev2026'])}</td>
      <td style="color:{TEAL};">{fmt_brl(it['val'])}</td>
      <td style="color:{GREEN};font-weight:600;">{fmt_brl(it['real'])}</td>
      <td>{pbar_html(it['pct'])}</td>
      <td>{bdg_status(it['pct'])}</td>
    </tr></tbody></table>"""

def mc_total(items):
    tm=tp=tp26=tv=tr=0
    for it in items:
        tm+=it["meta"];tp+=it["prev"];tp26+=it["prev2026"];tv+=it["val"];tr+=it["real"]
    pt = tr/tm if tm>0 else 0
    return f"""<table class="mct"><tbody><tr class="mc-tot">
      <td><b>TOTAL</b></td>
      <td><b>{fmt_brl(tm)}</b></td><td><b>{fmt_brl(tp)}</b></td>
      <td style="color:{AMBER};"><b>{fmt_brl(tp26)}</b></td>
      <td style="color:{TEAL};"><b>{fmt_brl(tv)}</b></td>
      <td style="color:{GREEN};font-weight:700;"><b>{fmt_brl(tr)}</b></td>
      <td>{pbar_html(pt)}</td><td></td>
    </tr></tbody></table>"""

# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

# HEADER
st.markdown(f"""<div class="dh">
  <img src="https://grupodelga.com.br/wp-content/uploads/2024/11/logo-fa-e-clientes-grupo-whatsapp-9-300x300.png"
       onerror="this.style.display='none'">
  <div class="dh-t">
    <h1>Dashboard Executivo — Grupo Delga 2026</h1>
    <p>Gestão Estratégica de Projetos e Redução de Custos</p>
  </div>
  <div class="dh-b">Jun / 2026</div>
</div>""", unsafe_allow_html=True)

# ADMIN UPLOAD
with st.expander("🔐 Administrador — Atualizar Planilha"):
    arquivo = st.file_uploader("Nova versão (.xlsx)", type=["xlsx"], key="up")
    if arquivo:
        b = arquivo.read(); save_bytes(b)
        st.cache_data.clear()
        st.success("✅ Planilha atualizada! Todos os usuários verão os novos dados.")

# CARGA
fb = load_bytes()
if fb is None:
    st.warning("⚠️ Nenhuma planilha carregada. Expanda o painel Administrador para fazer o upload.")
    st.stop()
try:
    D = load_data(fb)
except Exception as e:
    st.error(f"Erro ao processar planilha: {e}"); st.stop()

# EXTRAÇÃO
kpis    = extract_kpis(D)
plantas = extract_plantas(D)
areas   = extract_areas(D)
p_glob  = extract_pilares_global(D)
ev      = extract_evolucao(D)
ranking = extract_ranking(D)

meta=kpis["meta"]; portfolio=kpis["portfolio"]; prev2026=kpis["prev2026"]
validado=kpis["validado"]; real=kpis["real"]; pct_ating=kpis["pct_ating"]

# ── KPI CARDS ──────────────────────────────────────────────────────────────────
cob = portfolio/meta*100 if meta>0 else 0
pp  = prev2026/portfolio*100 if portfolio>0 else 0
pv  = validado/prev2026*100 if prev2026>0 else 0

def kpi(cls,lbl,vb,sub,det):
    return (f'<div class="kpi-card {cls}"><div class="kpi-l">{lbl}</div>'
            f'<div class="kpi-v">{vb}</div><div class="kpi-s">{sub}</div>'
            f'<div class="kpi-d">{det}</div></div>')

st.markdown(f"""<div class="kpi-wrap">
  {kpi("","Meta Anual do Grupo",fmt_mi(meta),fmt_brl(meta),"Objetivo 2026 — 100%")}
  {kpi("cs","Portfólio Previsto",fmt_mi(portfolio),fmt_brl(portfolio),f"{cob:.1f}% da meta · {kpis['inic']} iniciativas")}
  {kpi("ca","Previsto 2026",fmt_mi(prev2026),fmt_brl(prev2026),f"{pp:.1f}% do portfólio total")}
  {kpi("","Validado por Custos",fmt_mi(validado),fmt_brl(validado),f"{pv:.1f}% do Previsto 2026")}
  {kpi("cg","Retorno Real (DRE)",fmt_mi(real),fmt_brl(real),f"{pct_ating*100:.1f}% de atingimento")}
</div>""", unsafe_allow_html=True)

# NOTA
st.markdown(f"""<div class="nota">
  <b>Metodologia — Tipos de Ganho:</b>&nbsp;
  <b style="color:{GREEN};">✓ DRE</b>: BSW, Kaizen, Kaizen Ganho Recorrente, Redução de Custo, Você Resolve —
  impacto direto e mensurável no DRE.&nbsp;
  <b style="color:{SILVER};">↷ Não DRE</b>: Kaizen Custo Evitado, Kaizen Capital de Giro —
  geram valor (MO realocada / melhora de caixa) mas não reduzem GGF de forma tangível no DRE.
</div>""", unsafe_allow_html=True)

# ── EVOLUÇÃO ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Evolução Mensal — Acumulado Previsto vs Real vs Meta</span>', unsafe_allow_html=True)
series_all = ["Acumulado Previsto","Acumulado Real","Projeção da Meta","Previsto Mensal","Real Mensal"]
sel = st.multiselect("Séries:", series_all, default=series_all[:3], key="ev_sel")
if sel: st.plotly_chart(chart_evolucao(ev,sel), use_container_width=True, config={"displayModeBar":False})
st.markdown('</div>', unsafe_allow_html=True)

# ── FUNIL + GAUGE ──────────────────────────────────────────────────────────────
cfu, cga = st.columns([3,2])
with cfu:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Funil de Conversão — Portfólio → DRE</span>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:11px;color:{SILVER};margin-bottom:8px;">Quanto do portfólio mapeado converte em resultado no DRE?</p>', unsafe_allow_html=True)
    st.plotly_chart(chart_funnel(kpis), use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

with cga:
    st.markdown('<div class="sc">', unsafe_allow_html=True)
    st.markdown('<span class="st">Atingimento da Meta</span>', unsafe_allow_html=True)
    st.plotly_chart(chart_gauge(pct_ating), use_container_width=True, config={"displayModeBar":False})
    gap_val = meta-real
    st.markdown(f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">
      <div style="background:{LIGHT};border-radius:6px;padding:10px;text-align:center;">
        <div style="font-size:9px;font-weight:600;color:{SILVER};text-transform:uppercase;letter-spacing:.6px;">GAP para Meta</div>
        <div style="font-size:15px;font-weight:700;color:{RED};">{fmt_mi(gap_val)}</div>
      </div>
      <div style="background:{LIGHT};border-radius:6px;padding:10px;text-align:center;">
        <div style="font-size:9px;font-weight:600;color:{SILVER};text-transform:uppercase;letter-spacing:.6px;">Validado / Meta</div>
        <div style="font-size:15px;font-weight:700;color:{NAVY};">{validado/meta*100:.1f}%</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── DONUTS ──────────────────────────────────────────────────────────────────────
cd1,cd2 = st.columns(2)
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
                                [NAVY,GREEN,"#20C997"]),
                    use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── PILARES ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Distribuição por Tipo de Iniciativa — Grupo</span>', unsafe_allow_html=True)

# --- Gráfico gerencial de barras horizontais por pilar ---
def chart_pilares_gerencial(pilares_global, real_total):
    """Barras horizontais — Previsto / Validado / Real por pilar. Mais leitura gerencial."""
    labels   = [p["nome"] for p in pilares_global]
    previsto = [p["prev"] for p in pilares_global]
    validado = [p["val"]  for p in pilares_global]
    tv = sum(validado)
    real_est = [v / tv * real_total if tv > 0 else 0 for v in validado]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Previsto", y=labels, x=previsto,
        orientation="h", marker_color="#C8D8EE",
        text=[fmt_mi(v) for v in previsto],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Previsto: R$ %{x:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Validado", y=labels, x=validado,
        orientation="h", marker_color=NAVY,
        text=[fmt_mi(v) for v in validado],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Validado: R$ %{x:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Real DRE", y=labels, x=real_est,
        orientation="h", marker_color=GREEN,
        text=[fmt_mi(v) for v in real_est],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Real est.: R$ %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        barmode="group",
        xaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#F0F4F8",
                   title="R$", tickprefix="R$ "),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center",
                    font=dict(size=11)),
        margin=dict(l=130, r=120, t=40, b=30),
        height=max(220, len(labels) * 55),
        paper_bgcolor="white", plot_bgcolor="white",
        bargap=0.25, bargroupgap=0.08,
        font=dict(family="Inter"),
    )
    return fig

cp1, cp2 = st.columns([3, 2])
with cp1:
    st.plotly_chart(chart_pilares_gerencial(p_glob, real),
                    use_container_width=True, config={"displayModeBar": False})

with cp2:
    st.markdown('<span class="st">Resumo por Pilar — Grupo</span>', unsafe_allow_html=True)

    # Totais globais
    tot_qtd_g  = sum(p["qtd"]  for p in p_glob)
    tot_prev_g = sum(p["prev"] for p in p_glob)
    tot_val_g  = sum(p["val"]  for p in p_glob)
    tv_g = tot_val_g
    real_total_g = real
    real_est_g = {p["nome"]: p["val"] / tv_g * real_total_g if tv_g > 0 else 0 for p in p_glob}

    rows_p = ""
    for p in p_glob:
        re = real_est_g.get(p["nome"], 0)
        pct_val = p["val"] / p["prev"] * 100 if p["prev"] > 0 else 0
        # mini progress bar validado vs previsto
        bar_w = min(pct_val, 100)
        bar_color = GREEN if pct_val >= 60 else (AMBER if pct_val >= 30 else RED)
        bar_html = (f'<div style="display:flex;align-items:center;gap:5px;">'
                    f'<div style="width:50px;height:6px;background:#E2E8F0;border-radius:3px;overflow:hidden;">'
                    f'<div style="width:{bar_w:.0f}%;height:100%;background:{bar_color};border-radius:3px;"></div></div>'
                    f'<span style="font-size:10px;color:{SILVER};">{pct_val:.0f}%</span></div>')
        rows_p += f"""<tr>
          <td style="font-size:11px;font-weight:600;">{p['nome']}</td>
          <td style="text-align:center;font-size:11px;font-weight:700;">{p['qtd']}</td>
          <td style="text-align:right;font-size:11px;">{fmt_mi(p['prev'])}</td>
          <td style="text-align:right;font-size:11px;color:{TEAL};font-weight:600;">{fmt_mi(p['val'])}</td>
          <td style="text-align:right;font-size:11px;color:{GREEN};font-weight:600;">{fmt_mi(re)}</td>
          <td>{bar_html}</td>
        </tr>"""
    # linha total
    tot_real_est = sum(real_est_g.values())
    pct_tot = tot_val_g / tot_prev_g * 100 if tot_prev_g > 0 else 0
    bar_w_t = min(pct_tot, 100)
    bar_t = (f'<div style="display:flex;align-items:center;gap:5px;">'
             f'<div style="width:50px;height:6px;background:#E2E8F0;border-radius:3px;overflow:hidden;">'
             f'<div style="width:{bar_w_t:.0f}%;height:100%;background:{NAVY};border-radius:3px;"></div></div>'
             f'<span style="font-size:10px;color:{SILVER};">{pct_tot:.0f}%</span></div>')
    rows_p += f"""<tr class="tr-tot">
      <td style="font-size:11px;">TOTAL</td>
      <td style="text-align:center;font-size:11px;">{tot_qtd_g}</td>
      <td style="text-align:right;font-size:11px;">{fmt_mi(tot_prev_g)}</td>
      <td style="text-align:right;font-size:11px;color:{TEAL};">{fmt_mi(tot_val_g)}</td>
      <td style="text-align:right;font-size:11px;color:{GREEN};">{fmt_mi(tot_real_est)}</td>
      <td>{bar_t}</td>
    </tr>"""
    st.markdown(th("Pilar","Qtd","Previsto","Validado","Real DRE (est.)","Val/Prev") +
                rows_p + "</tbody></table>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PLANTAS INDUSTRIAIS — macro sempre visível + micro expandível
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Plantas Industriais — Performance Consolidada</span>', unsafe_allow_html=True)
st.markdown(mc_header(), unsafe_allow_html=True)

for p in plantas:
    st.markdown(mc_row(p), unsafe_allow_html=True)
    with st.expander(f"＋  Ver projetos de {p['nome']}", expanded=False):
        with st.spinner(f"Carregando projetos de {p['nome']}..."):
            proj = get_proj_planta(D, p["sheet"])
        n = len(proj)
        # Resumo por pilar LOCAL
        if proj:
            col_tab, col_pil = st.columns([3,1])
            with col_tab:
                st.markdown(f"<p style='font-size:11px;color:{SILVER};margin-bottom:6px;'>"
                            f"<b>{n} projetos</b> em {p['nome']}</p>", unsafe_allow_html=True)
                st.markdown(proj_table_html(proj), unsafe_allow_html=True)
            with col_pil:
                st.markdown(f"<p style='font-size:10px;font-weight:700;color:{NAVY};'>"
                            f"Pilares — {p['nome']}</p>", unsafe_allow_html=True)
                st.markdown(pilar_resumo_html(proj), unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#999;font-size:12px;'>Sem projetos encontrados.</p>",
                        unsafe_allow_html=True)

st.markdown(mc_total(plantas), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ÁREAS FUNCIONAIS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Áreas Funcionais — Performance Consolidada</span>', unsafe_allow_html=True)
st.markdown(mc_header(), unsafe_allow_html=True)

area_fn = {"Compras": get_proj_compras, "Vendas": get_proj_vendas}

for a in areas:
    st.markdown(mc_row(a), unsafe_allow_html=True)
    with st.expander(f"＋  Ver projetos de {a['nome']}", expanded=False):
        fn = area_fn.get(a["nome"])
        proj = fn(D) if fn else []
        n = len(proj)
        if proj:
            col_tab, col_pil = st.columns([3,1])
            with col_tab:
                st.markdown(f"<p style='font-size:11px;color:{SILVER};margin-bottom:6px;'>"
                            f"<b>{n} projetos</b> em {a['nome']}</p>", unsafe_allow_html=True)
                st.markdown(proj_table_html(proj), unsafe_allow_html=True)
            with col_pil:
                st.markdown(f"<p style='font-size:10px;font-weight:700;color:{NAVY};'>"
                            f"Pilares — {a['nome']}</p>", unsafe_allow_html=True)
                st.markdown(pilar_resumo_html(proj), unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#999;font-size:12px;'>Sem projetos encontrados.</p>",
                        unsafe_allow_html=True)

st.markdown(mc_total(areas), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── CLASSIFICAÇÃO DE GANHOS ────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Classificação de Ganhos — Impacto no DRE</span>', unsafe_allow_html=True)
cc1,cc2,cc3,cc4,cc5 = st.columns(5)
ganhos = [
    (cc1,NAVY,   "🔵","BSW","Benchmark de peso bruto. Redução de MP — impacto direto e mensurável no DRE.","✓ DRE",GREEN),
    (cc2,GREEN,  "🔥","Redução de Custo","Elimina custo direto na operação. Reduz GGF no DRE de forma tangível.","✓ DRE",GREEN),
    (cc3,AMBER,  "⚡","Kaizen / Ganho Recorrente","Produtividade recorrente apurada. Entra no DRE quando validado por Custos.","✓ DRE",GREEN),
    (cc4,"#512DA8","↷","Kaizen – Custo Evitado","MO realocada internamente — não reduz GGF no DRE. Gera valor operacional.","↷ Não DRE",SILVER),
    (cc5,"#0D47A1","🏦","Kaizen – Capital de Giro","Reduz estoque / melhora fluxo de caixa. Impacto no balanço, não no DRE.","↷ Não DRE",SILVER),
]
for col,cor,icon,titulo,texto,dre,dcor in ganhos:
    with col:
        st.markdown(f"""<div style="border:2px solid {cor};border-radius:8px;padding:12px 14px;height:100%;">
          <div style="font-weight:700;color:{cor};margin-bottom:4px;font-size:12px;">{icon} {titulo}</div>
          <div style="font-size:10px;color:#444;line-height:1.5;margin-bottom:6px;">{texto}</div>
          <div style="font-size:10px;font-weight:700;color:{dcor};">{dre}</div>
        </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── RANKING ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown('<span class="st">Ranking de Projetos — Todos os Pilares</span>', unsafe_allow_html=True)

rk1,rk2,rk3 = st.columns([2,2,1])
with rk1:
    f_uni = st.multiselect("Unidade:", sorted({r["uni"] for r in ranking}),
                           default=[], placeholder="Todas", key="rk_uni")
with rk2:
    f_st  = st.multiselect("Status:", sorted({r["status"] for r in ranking if r["status"]}),
                           default=[], placeholder="Todos", key="rk_st")
with rk3:
    n_lin = st.number_input("Linhas:", 5, 200, 25, 5)

pf = ranking
if f_uni: pf = [r for r in pf if r["uni"] in f_uni]
if f_st:  pf = [r for r in pf if r["status"] in f_st]

st.markdown(f"<p style='font-size:11px;color:{SILVER};margin-bottom:6px;'>"
            f"Exibindo {min(int(n_lin),len(pf))} de {len(pf)} projetos</p>",
            unsafe_allow_html=True)
rows_rk = "".join(f"""<tr>
  <td style="text-align:center;color:{SILVER};font-weight:700;font-size:11px;">{r['pos']}</td>
  <td style="font-weight:600;font-size:11px;">{r['uni']}</td>
  <td style="font-size:11px;">{r['nome']}</td>
  <td>{bdg_st(r['status'])}</td>
  <td>{bdg_custos(r['custos'])}</td>
  <td style="text-align:right;font-size:11px;">{fmt_brl(r['prev26'])}</td>
  <td style="text-align:right;font-size:11px;">{fmt_brl(r['prev_mo'])}</td>
  <td style="text-align:right;font-weight:700;color:{GREEN};font-size:11px;">{fmt_brl(r['real'])}</td>
</tr>""" for r in pf[:int(n_lin)])
st.markdown(th("#","Unidade","Projeto","Status","Custos",
               "Previsto 2026","Previsto Momento","Real DRE")+rows_rk+"</tbody></table>",
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── GAP ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sc">', unsafe_allow_html=True)
st.markdown(f'<span class="st" style="border-bottom-color:{AMBER};">GAP — Projetos Aguardando Validação de Custos</span>',
            unsafe_allow_html=True)
st.markdown(f'<p style="font-size:11px;color:{SILVER};margin-bottom:10px;">Projetos com valor projetado mas ainda sem validação do depto de Custos. Principal alavancador do pipeline.</p>',
            unsafe_allow_html=True)

gap = [r for r in ranking if r["custos"] not in ("OK","Não Ok","NOK","Não OK") and r["prev26"]>0]
by_uni = {}
for r in gap: by_uni[r["uni"]] = by_uni.get(r["uni"],0)+r["prev26"]
tot_gap = sum(by_uni.values())

rows_gap = "".join(f"""<tr>
  <td style="font-weight:600;">{u}</td>
  <td style="text-align:right;color:{AMBER};font-weight:600;">{fmt_brl(v)}</td>
  <td style="text-align:right;">{v/tot_gap*100:.1f}%</td>
</tr>""" for u,v in sorted(by_uni.items(),key=lambda x:-x[1]))
rows_gap += f"""<tr class="tr-tot">
  <td>TOTAL GAP</td>
  <td style="text-align:right;color:{AMBER};">{fmt_brl(tot_gap)}</td>
  <td style="text-align:right;">100%</td>
</tr>"""
st.markdown(f"<p style='font-size:11px;color:{SILVER};'>{len(gap)} projetos aguardam validação</p>",
            unsafe_allow_html=True)
st.markdown(th("Unidade",f'<span style="color:{AMBER}">Previsto 2026 (não validado)</span>',
               "% do Gap")+rows_gap+"</tbody></table>",
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="text-align:center;padding:14px 0;border-top:1px solid #EEF0F3;margin-top:4px;">
  <span style="font-size:11px;color:{SILVER};">
    Dashboard Executivo · Grupo Delga 2026 · Gestão Estratégica de Projetos e Redução de Custos
  </span>
</div>""", unsafe_allow_html=True)
_,cft = st.columns([5,1])
with cft:
    if st.button("🚪 Sair", key="logout"):
        st.session_state["auth"]=False; st.rerun()
